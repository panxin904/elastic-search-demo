#!/usr/bin/env bash
# sites-hub/scripts/deploy-release.sh
# VPS 端部署脚本：解压 sites-hub-static.tar.gz → 切换软链 → reload nginx
# 由 GitHub Actions 通过 SSH 调用（不需交互），也可手动跑。
#
# 用法（手动）：
#   sudo ./deploy-release.sh /path/to/sites-hub-static.tar.gz
#
# 用法（CI 推送后 SSH 调用）：
#   ssh user@host 'sudo /var/www/sites-hub/scripts/deploy-release.sh /tmp/sites-hub-static.tar.gz'
#
# 前置：
#   - deploy-vps.sh 已跑过（/var/www/sites-hub 目录结构 + nginx 配置已就绪）
#   - 当前用户有 sudo 权限（或用 root 跑）
#
# 设计要点：
#   - 蓝绿切换：解压到新目录 → 软链 atomic 切换 → nginx reload
#   - 自动回滚：解压失败 / 验证失败 → 旧软链不动
#   - flock 防并发：同时 2 次推送只跑 1 次
#   - 保留 5 个历史 release（超过自动清理）
#   - 零停机：nginx reload 是平滑重载，不丢连接

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TARBALL="${1:-}"
if [[ -z "$TARBALL" ]]; then
  echo "Usage: sudo $0 <path-to-sites-hub-static.tar.gz>" >&2
  echo "Example: sudo $0 /tmp/sites-hub-static.tar.gz" >&2
  exit 2
fi
if [[ ! -f "$TARBALL" ]]; then
  echo "Tarball not found: $TARBALL" >&2
  exit 3
fi

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run with sudo or as root." >&2
  exit 1
fi

WEB_ROOT="/var/www/sites-hub"
RELEASES_DIR="$WEB_ROOT/releases"
CURRENT_LINK="$WEB_ROOT/current"
LOCK_FILE="/var/lock/sites-hub-deploy.lock"
KEEP_RELEASES=5

# flock 防并发
exec 9>"$LOCK_FILE"
if ! flock -n 9; then
  echo "Another deployment is already running (lock held: $LOCK_FILE)" >&2
  exit 4
fi

echo "==> Checking prerequisites..."
if [[ ! -d "$WEB_ROOT" ]]; then
  echo "Web root not found: $WEB_ROOT (run deploy-vps.sh first)" >&2
  exit 5
fi
mkdir -p "$RELEASES_DIR"

RELEASE_ID="$(date +%Y%m%d%H%M%S)"
RELEASE_DIR="$RELEASES_DIR/$RELEASE_ID"

echo "==> Extracting $TARBALL → $RELEASE_DIR ..."
mkdir -p "$RELEASE_DIR"
# 解压失败自动 exit（非交互模式）
if ! tar xzf "$TARBALL" -C "$RELEASE_DIR" 2>&1 | tail -5; then
  echo "ERROR: tar extraction failed" >&2
  rm -rf "$RELEASE_DIR"
  exit 6
fi

# 验证产物结构（必须有 www/ 和 conf/）
if [[ ! -d "$RELEASE_DIR/www" ]] || [[ ! -f "$RELEASE_DIR/conf/nginx.conf" ]]; then
  echo "ERROR: extracted release missing www/ or conf/nginx.conf" >&2
  echo "Extracted contents:" >&2
  ls -la "$RELEASE_DIR" >&2
  rm -rf "$RELEASE_DIR"
  exit 7
fi

echo "==> Release structure:"
ls -la "$RELEASE_DIR" | head -10
echo "    www/: $(du -sh "$RELEASE_DIR/www" | cut -f1)"
echo "    conf/: $(du -sh "$RELEASE_DIR/conf" | cut -f1)"

echo "==> Verifying nginx config..."
# conf/nginx.conf 引用 ${CURRENT_LINK}/www，临时 symlink 让 nginx -t 找到路径
TMP_CURRENT="$RELEASE_DIR/_current_for_validation"
ln -sfn "$RELEASE_DIR" "$TMP_CURRENT"
# nginx -p 需要 prefix/logs/nginx.pid 存在（即使空文件也行）
mkdir -p "$TMP_CURRENT/logs"
touch "$TMP_CURRENT/logs/nginx.pid"
if ! nginx -t -c "$RELEASE_DIR/conf/nginx.conf" -p "$TMP_CURRENT/" 2>&1 | tail -5; then
  echo "ERROR: nginx config validation failed" >&2
  rm -rf "$RELEASE_DIR"
  rm -f "$TMP_CURRENT"
  exit 8
fi
rm -f "$TMP_CURRENT"

echo "==> Atomic symlink switch: $CURRENT_LINK → $RELEASE_DIR"
ln -sfn "$RELEASE_DIR" "$CURRENT_LINK.new"
mv -Tf "$CURRENT_LINK.new" "$CURRENT_LINK"

echo "==> Re-rendering /etc/nginx/sites-enabled/sites-hub.conf (idempotent)..."
# 渲染 VPS nginx 配置（含 P3 公开元数据 + stats.html + GoAccess），消除手动 SSH 修 nginx 复现路径
SITES_HUB_CONF_PATH="$SCRIPT_DIR/scripts/render-sites-hub-conf.sh"
if [[ ! -f "$SITES_HUB_CONF_PATH" ]]; then
  echo "WARN: render-sites-hub-conf.sh not found at $SITES_HUB_CONF_PATH; skipping re-render" >&2
else
  (
    # 子 shell：临时设置 env vars（不污染当前 shell）
    export SERVER_NAME
    SERVER_NAME="$(grep -m1 server_name "$RELEASE_DIR/conf/nginx.conf" 2>/dev/null | awk '{print $2}' | tr -d ';')"
    export WEB_ROOT="$WEB_ROOT"
    export CURRENT_LINK="$CURRENT_LINK"
    export ACME_ROOT="$ACME_ROOT"
    export AUTH_FILE="$AUTH_FILE"
    if [[ -d /etc/nginx/sites-available ]]; then
      export CONFIG_PATH="/etc/nginx/sites-available/sites-hub.conf"
    else
      export CONFIG_PATH="/etc/nginx/conf.d/sites-hub.conf"
    fi
    export MODE=https
    bash "$SITES_HUB_CONF_PATH"
  )
  echo "    Rendered: $CONFIG_PATH"
fi

echo "==> Reloading nginx..."
if ! nginx -s reload 2>&1; then
  echo "ERROR: nginx reload failed (release is now active but nginx uses old workers)" >&2
  exit 9
fi

echo "==> Cleaning old releases (keep last $KEEP_RELEASES)..."
if [[ -d "$RELEASES_DIR" ]]; then
  ls -1dt "$RELEASES_DIR"/*/ 2>/dev/null | tail -n +$((KEEP_RELEASES + 1)) | while read -r old; do
    echo "    removing: $old"
    rm -rf "$old"
  done
fi

echo ""
echo "==> Deploy complete"
echo "    Release: $RELEASE_ID"
echo "    Path:    $RELEASE_DIR"
echo "    Active:  $CURRENT_LINK → $RELEASE_DIR"
echo "    Test:    curl -fsSL https://$(grep server_name "$RELEASE_DIR/conf/nginx.conf" | head -1 | awk '{print $2}' | tr -d ';')/healthz"
