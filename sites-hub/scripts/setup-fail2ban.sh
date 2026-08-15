#!/usr/bin/env bash
# sites-hub/scripts/setup-fail2ban.sh
# VPS 一键安装 fail2ban + Basic Auth 防爆破（运行于 root）
#
# 用法：
#   1. 在 deploy-vps.sh 末尾自动调用
#   2. 或手动 sudo bash setup-fail2ban.sh
#
# 前置：
#   - nginx 1.18+ 已运行
#   - sites-hub/scripts/fail2ban-nginx-auth.conf 与 fail2ban-nginx-auth-filter.conf 已上传

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo or as root." >&2
  exit 1
fi

if ! command -v apt-get >/dev/null; then
  echo "This script assumes apt (Ubuntu/Debian)." >&2
  exit 1
fi

# 1. 安装 fail2ban
if ! command -v fail2ban-client >/dev/null; then
  echo "==> Installing fail2ban..."
  apt-get update
  apt-get install -y fail2ban
fi

# 2. 配置 fail2ban：复制 filter + jail
echo "==> Installing nginx-auth filter + jail..."
cp "$SCRIPT_DIR/fail2ban-nginx-auth-filter.conf" /etc/fail2ban/filter.d/nginx-auth.conf
cp "$SCRIPT_DIR/fail2ban-nginx-auth.conf" /etc/fail2ban/jail.d/nginx-auth.conf
chmod 644 /etc/fail2ban/filter.d/nginx-auth.conf /etc/fail2ban/jail.d/nginx-auth.conf

# 3. 验证 nginx 配置：auth 失败时是否打 auth.log
NGINX_CONF=/etc/nginx/sites-available/sites-hub.conf
if ! grep -q 'auth.log' "$NGINX_CONF" 2>/dev/null; then
  echo "WARN: nginx config does not have auth_basic_log to /var/log/nginx/auth.log" >&2
  echo "      Add this inside the https server { } block (between auth_basic and the location blocks):" >&2
  echo '        error_log /var/log/nginx/auth.log;'
  echo
fi

# 4. 创建 /var/log/nginx/auth.log（如果不存在）
touch /var/log/nginx/auth.log
chown www-data:adm /var/log/nginx/auth.log 2>/dev/null || chown www-data:root /var/log/nginx/auth.log
chmod 640 /var/log/nginx/auth.log

# 5. 启动 fail2ban
echo "==> Starting fail2ban..."
systemctl enable --now fail2ban
systemctl restart fail2ban

# 6. 验证
sleep 2
fail2ban-client status nginx-auth || {
  echo "WARN: nginx-auth jail not yet active (no failed login to trigger yet)" >&2
}

echo
echo "==> fail2ban installed. Manual check:"
echo "    sudo fail2ban-client status nginx-auth"
echo "    sudo tail -f /var/log/fail2ban.log"
