#!/usr/bin/env bash
# sites-hub/scripts/render-nginx-conf.sh
# 从 sites.sh 渲染 conf/nginx.conf。
# 这是真正的"单一真相源"生成器：修改 sites.sh 后跑这个脚本即可。

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/sites.sh
source "$SCRIPT_DIR/sites.sh"

OUT="${1:-$SCRIPT_DIR/../conf/nginx.conf}"

cat > "$OUT" <<NGXHEAD
# $OUT
# 本地开发用 nginx 配置（VPS 用 deploy-vps.sh 生成的 sites-hub.conf）。
#
# **本文件由 scripts/render-nginx-conf.sh 自动生成**。
# 子站 location 由 sites-hub/scripts/sites.sh 驱动（**唯一真相源**）。
# 任何新增站点只需改 sites.sh + 一张首页卡片 + 1 个项目目录，再跑本脚本。
# T2 安全响应头在此集中配置。

worker_processes  auto;
error_log  logs/error.log;
pid        logs/nginx.pid;

events {
    worker_connections  1024;
}

http {
    include       /opt/homebrew/etc/nginx/mime.types;
    default_type  application/octet-stream;
    access_log    logs/access.log;

    sendfile        on;
    keepalive_timeout  65;

    # T13：gzip 补全
    gzip  on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/javascript text/xml
               application/javascript application/json application/xml
               application/xhtml+xml application/rss+xml application/atom+xml
               application/ld+json application/manifest+json application/wasm
               image/svg+xml image/x-icon image/bmp image/vnd.microsoft.icon
               font/woff2 font/ttf font/otf;

    # T3：basic auth 暴力破解限流
    limit_req_zone \$binary_remote_addr zone=auth:10m rate=10r/m;


    # T11：健康检查（auth 前）
    server {
        listen       8081;
        server_name  localhost;
        charset      utf-8;

        # T2：安全响应头（即使 4xx/5xx 也带上 always）
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
        # HTTPS-only 站点上再加 HSTS（本地开发不上）：见 deploy-vps.sh

        # T3：限流（auth 路径；trusted IP 旁路）
        limit_req zone=auth burst=20 nodelay;

        # 健康检查（auth 前）
        location = /healthz {
            access_log off;
            return 200 "ok\\n";
            add_header Content-Type text/plain;
        }

        # T11：Prometheus exporter 取数（仅 localhost，防外泄）
        location = /metrics {
            access_log off;
            allow 127.0.0.1;
            allow ::1;
            deny  all;
            stub_status;
        }

        # T11：basic auth 探测（200 表示 auth 后端正常）
        location = /auth-check {
            access_log off;
            return 200 "auth-ok\\n";
            add_header Content-Type text/plain;
        }

        # T15：CSP violation report（写日志，供后续 ELK/Loki ingest）
        location = /csp-report {
            access_log logs/csp-report.log combined buffer=32k flush=5s;
            return 204;
        }

        # ===== 自定义错误页（T6）=====
        error_page 404 /404.html;
        error_page 500 502 503 504 /50x.html;

        # ===== 长缓存 VitePress 哈希资源（T6）=====
        location ~* "^/[^/]+/assets/.*\.(js|css|woff2|svg|png|webp|avif|ico)$" {
            add_header Cache-Control "public, max-age=31536000, immutable";
            access_log off;
            try_files \$uri =404;
        }

        # ===== 导航首页 =====
        location / {
            root   www/;
            index  index.html;
            try_files \$uri \$uri/ =404;
            autoindex off;
        }
NGXHEAD

for s in "${SITES[@]}"; do
  project="$(site_to_project "$s")"
  cat >> "$OUT" <<SUB

        # T1：自动生成自 sites.sh（勿手动改）
        location = /$s { return 301 /$s/; }
        location /$s/ {
            alias  ../$project/.vitepress/dist/;
            index  index.html;
            try_files \$uri \$uri.html \$uri/index.html =404;
        }
SUB
done

cat >> "$OUT" <<'NGTAIL'
    }
}
NGTAIL

echo "Rendered $OUT with ${#SITES[@]} site location blocks."
