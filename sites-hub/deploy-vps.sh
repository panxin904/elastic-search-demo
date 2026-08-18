#!/usr/bin/env bash
# Run this script on the VPS after extracting sites-hub-static.tar.gz.
# Usage: sudo ./deploy-vps.sh example.com admin@example.com [basic_auth_username]
#
# **本脚本现在由 sites-hub/scripts/sites.sh 驱动**：
# 子站 location / 重定向 / for site in ... 循环 都从 SITES 数组生成。
# 任何新增站点都只改 sites.sh + 一张首页卡片 + 1 个项目目录。

set -euo pipefail

# shellcheck source=scripts/sites.sh
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/scripts/sites.sh"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this deployment script with sudo or as root." >&2
  exit 1
fi

SERVER_NAME="${1:-}"
CERTBOT_EMAIL="${2:-}"
AUTH_USER="${3:-}"
if [[ -z "$SERVER_NAME" || -z "$CERTBOT_EMAIL" ]]; then
  echo "Usage: sudo $0 example.com admin@example.com [basic_auth_username]" >&2
  exit 1
fi
if ! [[ "$SERVER_NAME" =~ ^[A-Za-z0-9.-]+$ ]] || [[ "$SERVER_NAME" != *.* ]]; then
  echo "Use a valid domain name (for example: docs.example.com), not an IP address." >&2
  exit 1
fi

if [[ -z "$AUTH_USER" ]]; then
  read -r -p "Basic Auth username: " AUTH_USER
fi
if [[ -z "$AUTH_USER" ]]; then
  echo "Basic Auth username cannot be empty." >&2
  exit 1
fi

# P0 fix: 支持非交互模式（CI 自动部署）
# 优先级：AUTH_PASSWORD env var > 交互 read
if [[ -z "${AUTH_PASSWORD:-}" ]]; then
  while true; do
    read -r -s -p "Password for ${AUTH_USER}: " AUTH_PASSWORD
    echo
    read -r -s -p "Confirm password: " AUTH_PASSWORD_CONFIRM
    echo
    if [[ -n "$AUTH_PASSWORD" && "$AUTH_PASSWORD" == "$AUTH_PASSWORD_CONFIRM" ]]; then
      break
    fi
    echo "Passwords are empty or do not match; try again." >&2
  done
  unset AUTH_PASSWORD_CONFIRM
else
  echo "==> Using AUTH_PASSWORD from environment (non-interactive mode)"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_ROOT="/var/www/sites-hub"
RELEASES_DIR="$WEB_ROOT/releases"
RELEASE_ID="$(date +%Y%m%d%H%M%S)"
RELEASE_DIR="$RELEASES_DIR/$RELEASE_ID"
CURRENT_LINK="$WEB_ROOT/current"
ACME_ROOT="/var/www/certbot"
AUTH_FILE="/etc/nginx/.sites-hub.htpasswd"

install_dependencies() {
  if command -v apt-get >/dev/null; then
    apt-get update
    # P3: 用 nginx-full 替换默认 nginx-core，提供 gzip_static / limit_req / stub_status 等模块
apt-get install -y nginx-full apache2-utils certbot
  elif command -v dnf >/dev/null; then
    dnf install -y nginx httpd-tools certbot
  elif command -v yum >/dev/null; then
    yum install -y nginx httpd-tools certbot
  else
    echo "Could not find apt-get, dnf, or yum to install dependencies." >&2
    exit 1
  fi
}

configure_path() {
  if [[ -d /etc/nginx/sites-available ]]; then
    CONFIG_PATH="/etc/nginx/sites-available/sites-hub.conf"
    # P18 加固：idempotent symlink 修复（防止历史部署残留独立文件导致 nginx -t 报 duplicate directive）
    if [[ -e /etc/nginx/sites-enabled/sites-hub.conf ]] && [[ ! -L /etc/nginx/sites-enabled/sites-hub.conf ]]; then
      echo "WARN: /etc/nginx/sites-enabled/sites-hub.conf 是独立文件（非 symlink），自动替换为 symlink"
      cp -p /etc/nginx/sites-enabled/sites-hub.conf "$CONFIG_PATH.bak.orphan.$(date +%Y%m%d%H%M%S)" 2>/dev/null || true
      rm -f /etc/nginx/sites-enabled/sites-hub.conf
    fi
    ln -sfn "$CONFIG_PATH" /etc/nginx/sites-enabled/sites-hub.conf
    # This VPS is dedicated to the sites hub; otherwise the distribution's
    # default server can answer IP requests instead of this virtual host.
    rm -f /etc/nginx/sites-enabled/default
  else
    CONFIG_PATH="/etc/nginx/conf.d/sites-hub.conf"
  fi
}

# 渲染 nginx location 块：完全由 SITES 数组驱动
render_location_blocks() {
  for s in "${SITES[@]}"; do
    cat <<SUB
    location = /$s { return 301 /$s/; }
    location /$s/ {
        root \${CURRENT_LINK};
        try_files \$uri \$uri.html \$uri/index.html =404;
    }
SUB
  done
}

# nginx 配置渲染已抽到 scripts/render-sites-hub-conf.sh（deploy-vps.sh + deploy-release.sh 共用）。
# 见文件顶部 source 调用。
install_dependencies
configure_path

mkdir -p "$RELEASE_DIR" "$ACME_ROOT"
cp -R "$SCRIPT_DIR/www" "$RELEASE_DIR/www"
# 由 SITES 驱动的拷贝循环（替代硬编码 for site in ...）
for s in "${SITES[@]}"; do
  src="$SCRIPT_DIR/$s"
  if [[ -d "$src" ]]; then
    cp -R "$src" "$RELEASE_DIR/$s"
  else
    echo "WARN: staged site directory missing for '$s' ($src)" >&2
  fi
done
ln -sfn "$RELEASE_DIR" "$CURRENT_LINK"

printf '%s\n' "$AUTH_PASSWORD" | htpasswd -c -i "$AUTH_FILE" "$AUTH_USER"
# T12：htpasswd 权限修正（必须 chown 到 www-data，否则 500）
chown root:www-data "$AUTH_FILE"
chmod 640 "$AUTH_FILE"
unset AUTH_PASSWORD

# 阶段 1：渲染 HTTP-only 配置（仅用于 certbot 申请证书）
MODE=http-only render_sites_hub_conf
nginx -t
if command -v systemctl >/dev/null; then
  systemctl enable --now nginx
  systemctl reload nginx
else
  nginx -s reload || nginx
fi

# T12：强制短续期，避免到期前 30 天才续的窗口风险
certbot certonly --webroot -w "$ACME_ROOT" \
  --non-interactive --agree-tos --keep-until-expiring \
  --deploy-hook "systemctl reload nginx || nginx -s reload" \
  --email "$CERTBOT_EMAIL" -d "$SERVER_NAME"

# 阶段 2：渲染 HTTPS 完整配置（含所有 P3 location + stats.html + GoAccess）
MODE=https render_sites_hub_conf
nginx -t
if command -v systemctl >/dev/null; then
  systemctl reload nginx
  systemctl enable --now certbot.timer 2>/dev/null || true
  # T12：月度 certbot renew dry-run 计划（提前 30 天检测续期问题）
  cat > /etc/cron.d/certbot-renew-dryrun <<CRON
# 每月 1 日 04:30 做 certbot renew dry-run，结果发到 root 邮箱
30 4 1 * * root /usr/bin/certbot renew --dry-run --quiet >> /var/log/certbot-dryrun.log 2>&1 || echo "certbot dry-run FAILED $(date -I)" | /usr/bin/mail -s "certbot dry-run failed on $(hostname)" root 2>/dev/null || true
CRON
  chmod 644 /etc/cron.d/certbot-renew-dryrun
else
  nginx -s reload
fi

# T3：安装 fail2ban 防爆破（只在首次部署时跑，fail2ban-client status 可查）
if [[ -f "$SCRIPT_DIR/scripts/setup-fail2ban.sh" ]]; then
  echo "==> Setting up fail2ban..."
  bash "$SCRIPT_DIR/scripts/setup-fail2ban.sh" || echo "WARN: fail2ban setup failed; continuing"
else
  echo "WARN: scripts/setup-fail2ban.sh not found; skipping fail2ban install" >&2
fi

# C9：轻量访问统计（GoAccess，单二进制 + cron，零外部依赖）
if [[ -f "$SCRIPT_DIR/scripts/setup-goaccess.sh" ]]; then
  echo "==> Setting up GoAccess stats..."
  bash "$SCRIPT_DIR/scripts/setup-goaccess.sh" || echo "WARN: goaccess setup failed; continuing"
else
  echo "WARN: scripts/setup-goaccess.sh not found; skipping GoAccess install" >&2
fi

# T13：保留最近 5 个 release，避免 /var/www/sites-hub/releases 无限堆积
if [[ -d "$RELEASES_DIR" ]]; then
  ls -1dt "$RELEASES_DIR"/*/ 2>/dev/null | tail -n +6 | while read -r old; do
    rm -rf "$old" && echo "Pruned old release: $old"
  done
fi

echo "Deployment complete. Visit: https://${SERVER_NAME}/"
