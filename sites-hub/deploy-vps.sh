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
    apt-get install -y nginx apache2-utils certbot
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

write_http_only_config() {
  cat > "$CONFIG_PATH" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${SERVER_NAME};

    location ^~ /.well-known/acme-challenge/ {
        root ${ACME_ROOT};
        auth_basic off;
        try_files \$uri =404;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOF
}

write_https_config() {
  # 把 location 块先渲染到临时变量，再 cat 进来
  local location_blocks
  location_blocks="$(render_location_blocks)"

  cat > "$CONFIG_PATH" <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name ${SERVER_NAME};

    location ^~ /.well-known/acme-challenge/ {
        root ${ACME_ROOT};
        auth_basic off;
        try_files \$uri =404;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    server_name ${SERVER_NAME};
    charset utf-8;

    ssl_certificate /etc/letsencrypt/live/${SERVER_NAME}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${SERVER_NAME}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # T2：HSTS（含子域 + preload 候选）
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # T13：gzip 补全
    gzip on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/javascript text/xml
               application/javascript application/json application/xml
               application/xhtml+xml application/rss+xml application/atom+xml
               application/ld+json application/manifest+json application/wasm
               image/svg+xml image/x-icon image/bmp image/vnd.microsoft.icon
               font/woff2 font/ttf font/otf;

    # T13：Brotli 压缩（可选，需要 nginx --with-http_brotli_module 或加载 nginx-module-brotli.so）
    # 启用：apt install libnginx-mod-http-brotli  (Debian/Ubuntu) 或从源编译
    # 然后取消下面注释并 reload：
    # brotli on;
    # brotli_comp_level 6;
    # brotli_types application/atom+xml application/grpc application/javascript application/json application/ld+json application/manifest+json application/rss+xml application/wasm application/xhtml+xml application/xml font/otf font/ttf image/svg+xml text/css text/javascript text/plain text/xml;

    # T2：安全响应头（always 即使 4xx/5xx 也带上）
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options        "DENY" always;
    add_header Referrer-Policy        "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy     "geolocation=(), camera=(), microphone=(), interest-cohort=()" always;
    add_header Content-Security-Policy "default-src 'self'; \
        img-src 'self' data: blob:; \
        style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; \
        font-src 'self' https://fonts.gstatic.com; \
        script-src 'self' 'unsafe-inline'; \
        frame-ancestors 'none'; base-uri 'self'; form-action 'self'; report-uri /csp-report;" always;

    # T3：basic auth 限流（防爆破；trusted IP 旁路）
    limit_req zone=auth burst=20 nodelay;

    # T3：basic auth 本身（强制全部受保护）
    auth_basic "Restricted";
    auth_basic_user_file ${AUTH_FILE};

    # T3：auth 失败单独日志（供 fail2ban 读取）
    error_log /var/log/nginx/auth.log;

    # T11：健康检查（auth 前）
    location = /healthz {
        auth_basic off;
        access_log off;
        return 200 "ok\\n";
        add_header Content-Type text/plain;
    }

    # T11：Prometheus exporter 取数（仅 localhost 防外泄 + auth 前）
    location = /metrics {
        auth_basic off;
        access_log off;
        allow 127.0.0.1;
        allow ::1;
        deny  all;
        stub_status;
    }

    # T11：basic auth 探测（确认密码文件可读）
    location = /auth-check {
        auth_basic off;
        access_log off;
        return 200 "auth-ok\\n";
        add_header Content-Type text/plain;
    }

    # T15：CSP violation report（写日志，可接 ELK）
    location = /csp-report {
        auth_basic off;
        access_log /var/log/nginx/csp-report.log combined buffer=32k flush=5s;
        return 204;
    }

    # T6：自定义错误页
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;

    # T6：长缓存 VitePress 哈希资源（assets/ 下的 js/css/woff2/svg/...）
    location ~* "^/[^/]+/assets/.*\.(js|css|woff2|svg|png|webp|avif|ico)$" {
        add_header Cache-Control "public, max-age=31536000, immutable";
        access_log off;
        try_files \$uri =404;
    }

    # ===== 子站 location（由 sites.sh 驱动，勿手动改）=====
${location_blocks}

    # ===== 门户首页 =====
    location / {
        root \${CURRENT_LINK}/www;
        try_files \$uri \$uri/ =404;
        autoindex off;
    }
}
EOF
  # P0 fix: nginx 不支持 ${VAR} 语法（只支持 $VAR），把占位符展开为实际路径
  sed -i "s|\${CURRENT_LINK}|${CURRENT_LINK}|g" "$CONFIG_PATH"
}

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

# Serve only the ACME challenge on HTTP while requesting the first certificate.
write_http_only_config
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

write_https_config
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
