#!/usr/bin/env bash
# sites-hub/scripts/render-sites-hub-conf.sh
#
# 渲染 VPS 端 sites-hub.conf（**单一真相源**）。
# deploy-vps.sh（首次部署）和 deploy-release.sh（每次 deploy）共用，
# 保证 VPS 配置永远与 git 仓库一致，消除手动 SSH 修 nginx 复现路径。
#
# 设计：
# - source sites.sh 取 SITES 数组（驱动子站 location）
# - 包含所有 P3 / T18 公开元数据 location（sitemap / llms / feed / stats.html 等）
# - nginx 不支持 ${VAR} 语法，写完用 sed 把占位符替换为实际路径
# - 幂等：每次跑产出相同结果
#
# 用法：
#   source render-sites-hub-conf.sh
#   render_sites_hub_conf [--mode=http-only|https]
#
# 前置：root 权限（写 /etc/nginx/sites-available/）

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/sites.sh
source "$SCRIPT_DIR/sites.sh"

: "${SERVER_NAME:=java-px.bot.cd}"
: "${WEB_ROOT:=/var/www/sites-hub}"
: "${ACME_ROOT:=/var/www/certbot}"
: "${AUTH_FILE:=/etc/nginx/.sites-hub.htpasswd}"
: "${CURRENT_LINK:=$WEB_ROOT/current}"
: "${CONFIG_PATH:=/etc/nginx/sites-available/sites-hub.conf}"
: "${MODE:=https}"

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
    gzip_static on;
    gzip_proxied any;
    gzip_vary on;
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

    # P0: GoAccess stats — public（无需 auth，让匿名访问看流量统计）
    location = /stats.html {
        auth_basic off;
        access_log off;
        add_header Cache-Control "no-cache, must-revalidate";
        alias /var/www/sites-hub/www/stats.html;
    }

    # C3: 内容质量趋势 Dashboard — public
    location = /audit-dashboard.html {
        auth_basic off;
        access_log off;
        alias ${WEB_ROOT}/current/www/audit-dashboard.html;
    }

    # T15：CSP violation report（写日志，可接 ELK）
    location = /csp-report {
        auth_basic off;
        access_log /var/log/nginx/csp-report.log combined buffer=32k flush=5s;
        return 204;
    }

    # P3: 公开元数据（sitemap + llms + feed + manifest）— SEO 友好，无 auth
    location = /sitemap.xml       { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/sitemap.xml; }
    location = /sitemap.xml.gz   { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/sitemap.xml.gz; default_type application/gzip; }
    location = /llms.txt         { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/llms.txt; }
    location = /llms.txt.gz      { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/llms.txt.gz; default_type application/gzip; }
    location = /llms-full.txt    { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/llms-full.txt; }
    location = /llms-full.txt.gz { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/llms-full.txt.gz; default_type application/gzip; }
    location = /feed.xml         { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/feed.xml; }
    location = /feed.xml.gz      { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/feed.xml.gz; default_type application/gzip; }
    # P19: robots.txt 直接由 nginx 返回（不依赖 release 产物，避免 missing file 导致 401）
    location = /robots.txt {
        auth_basic off;
        access_log off;
        default_type text/plain;
        return 200 "User-agent: *\nAllow: /\nSitemap: https://${SERVER_NAME}/sitemap.xml\n";
    }
    location = /manifest.webmanifest { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/manifest.webmanifest; }
    location = /ld.json          { auth_basic off; access_log off; alias ${WEB_ROOT}/current/www/ld.json; }

    # T6：自定义错误页
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;

    # T6：长缓存 VitePress 哈希资源（assets/ 下的 js/css/woff2/svg/...）
    # P0 fix: assets 必须公开（auth_basic off）
    # 原因：VitePress 客户端 hydrate 用 ES module dynamic import，
    # 浏览器对子模块 fetch 在某些场景不传 Authorization header，
    # 导致 assets 401 → JS 不执行 → 用户看到纯 SSR 裸文字
    # 主体内容（HTML）仍需 auth，公开 assets 不泄露内容（只是样式/JS）
    location ~* "^/[^/]+/assets/.*\.(js|css|woff2|woff|ttf|otf|svg|png|webp|avif|ico)$" {
        auth_basic off;
        access_log off;
        add_header Cache-Control "public, max-age=31536000, immutable";
        try_files \$uri =404;
    }
    location ~* "^/[^/]+/assets/chunks/.*$" {
        auth_basic off;
        access_log off;
        add_header Cache-Control "public, max-age=31536000, immutable";
        try_files \$uri =404;
    }

    # ===== 子站 location（由 sites.sh 驱动，勿手动改）=====
${location_blocks}

    # 门户 www/fonts 自托管字体（公开，避免 CSP font-src 限制）
    location ^~ /www/fonts/ {
        auth_basic off;
        access_log off;
        alias /var/www/sites-hub/www/fonts/;
        add_header Cache-Control "public, max-age=31536000, immutable";
        expires 365d;
    }

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

render_sites_hub_conf() {
  case "${MODE}" in
    http-only)
      write_http_only_config
      ;;
    https|*)
      write_https_config
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  if [[ "${EUID:-$(id -u)}" -ne 0 ]]; then
    echo "Run with sudo or as root." >&2
    exit 1
  fi
  render_sites_hub_conf
  echo "Rendered $CONFIG_PATH (mode=$MODE, sites=${#SITES[@]})"
fi
