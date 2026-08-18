# HTTPS 部署技术文档

> 本文档专题讲解 `java-px.bot.cd` 站点的 HTTPS 部署技术细节：证书 / nginx 配置生成 / 部署同步机制。
>
> 适用版本：commit `ad2b61e` 及之后（render-sites-hub-conf.sh 已抽离 + deploy-release.sh idempotent 同步）。

---

## 1. 概述

`java-px.bot.cd` 是一个**多子站聚合门户**（28 个 VitePress 子站），部署在单 VPS（38.207.171.83 / Ubuntu 22.04 / nginx-full）上，全站强制 HTTPS + basic auth（除 11 个公开元数据 location）。

**核心约束**
- **单一真相源**：`sites-hub/scripts/sites.sh` 的 SITES 数组驱动 28 个子站
- **零停机部署**：软链 atomic switch + `nginx -s reload`
- **配置同步**：每次 deploy 自动重写 VPS `/etc/nginx/sites-available/sites-hub.conf`（无手动 SSH）

---

## 2. 三层架构（single source of truth）

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 1: 配置文件生成（仓库内，source of truth）                         │
│                                                                         │
│   sites-hub/scripts/sites.sh                  # 28 站 SITES 数组        │
│   sites-hub/scripts/render-nginx-conf.sh      # 本地 dev（listen 8081） │
│   sites-hub/scripts/render-sites-hub-conf.sh  # VPS（listen 80/443）★  │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 2: 构建（CI build-all job）                                        │
│                                                                         │
│   sites-hub/build-release.sh                                              │
│     1. bash scripts/check-sites.sh              # SITES 一致性检查       │
│     2. bash scripts/render-nginx-conf.sh        # 本地 dev conf         │
│     3. bash scripts/render-sites-hub-conf.sh    # VPS conf ★            │
│     4. for s in "${SITES[@]}"; do              # 28 站串行构建           │
│          (cd "$s-html"; npm ci; npm run docs:build)                     │
│        done                                                            │
│     5. tar czf sites-hub-static.tar.gz         # 打包 stage             │
└─────────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 3: 部署（VPS 端，atomic + idempotent）                              │
│                                                                         │
│   sites-hub/scripts/deploy-release.sh                                    │
│     1. flock 防并发（/var/lock/sites-hub-deploy.lock）                   │
│     2. mkdir $RELEASES_DIR/$ID/ && tar xzf tarball                       │
│     3. nginx -t -c $RELEASE/conf/nginx.conf -p $RELEASE/                │
│     4. ln -sfn + mv -Tf：atomic symlink switch current → $RELEASE       │
│     5. ★ bash scripts/render-sites-hub-conf.sh                            │
│        → 重新生成 /etc/nginx/sites-available/sites-hub.conf              │
│        → sed -i 's|${CURRENT_LINK}|/var/www/sites-hub/current|g'        │
│     6. nginx -s reload                              # 零停机            │
│     7. 清理 5 个之前 release                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**★ = 单点真相**（ad2b61e 引入）
- `render-sites-hub-conf.sh` 同时被 deploy-vps.sh（首次）和 deploy-release.sh（每次）调用
- 任何 P3 location 增删**只需改这一个文件**，下次 deploy 自动生效

---

## 3. HTTPS 关键技术决策

### 3.1 证书申请

**首次部署**（deploy-vps.sh）走 HTTP-01 challenge 两阶段：

```
阶段 1: MODE=http-only render_sites_hub_conf
        → 写入仅含 ACME challenge location 的 HTTP-only sites-hub.conf
        → nginx -t && systemctl reload nginx
        → certbot certonly --webroot -w /var/www/certbot --non-interactive ...

阶段 2: MODE=https render_sites_hub_conf
        → 写入完整 HTTPS sites-hub.conf（含 ssl_certificate 引用）
        → nginx -t && systemctl reload nginx
```

**续期**：
- `certbot.timer`（systemd）自动续期（30 天前）
- `--deploy-hook "systemctl reload nginx || nginx -s reload"` 续期后 reload
- cron 月度 dry-run（`/etc/cron.d/certbot-renew-dryrun`，每月 1 日 04:30）提前 30 天检测

### 3.2 TLS 协议与 HSTS

```nginx
ssl_protocols TLSv1.2 TLSv1.3;     # 禁用 TLS 1.0/1.1（已 deprecate）
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
                                    # 2 年 + 子域 + preload 候选
```

### 3.3 HTTP → HTTPS 重定向

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name java-px.bot.cd;

    location ^~ /.well-known/acme-challenge/ {
        root /var/www/certbot;       # certbot webroot challenge
        auth_basic off;
        try_files $uri =404;
    }

    location / {
        return 301 https://$host$request_uri;  # 永久重定向
    }
}
```

### 3.4 资源压缩

```nginx
gzip on;
gzip_static on;             # 服务预压缩 .gz（sitemap.xml.gz / llms-full.txt.gz 等）
gzip_proxied any;           # CDN/proxy 也压缩
gzip_vary on;               # Vary: Accept-Encoding
gzip_min_length 1024;
gzip_types text/plain text/css text/javascript text/xml
           application/javascript application/json application/xml
           application/xhtml+xml application/rss+xml application/atom+xml
           application/ld+json application/manifest+json application/wasm
           image/svg+xml image/x-icon image/bmp image/vnd.microsoft.icon
           font/woff2 font/ttf font/otf;

# Brotli（可选）：apt install libnginx-mod-http-brotli + 取消注释下面段
# brotli on; brotli_comp_level 6;
```

### 3.5 认证与限流

```nginx
# T3：basic auth + 限流（防爆破）
auth_basic "Restricted";
auth_basic_user_file /etc/nginx/.sites-hub.htpasswd;
limit_req zone=auth burst=20 nodelay;

# 限流区域定义（在 http {} 块）
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;
```

**T12 htpasswd 权限修正**（必须，否则 500）：
```bash
chown root:www-data /etc/nginx/.sites-hub.htpasswd
chmod 640 /etc/nginx/.sites-hub.htpasswd
```

### 3.6 安全响应头

```nginx
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options        "DENY" always;
add_header Referrer-Policy        "strict-origin-when-cross-origin" always;
add_header Permissions-Policy     "geolocation=0, camera=0, microphone=0, interest-cohort=0" always;
add_header Content-Security-Policy "default-src 'self'; \
    img-src 'self' data: blob:; \
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; \
    font-src 'self' https://fonts.gstatic.com; \
    script-src 'self' 'unsafe-inline'; \
    frame-ancestors 'none'; base-uri 'self'; form-action 'self'; report-uri /csp-report;" always;
```

**HSTS 注释**：HTTPS-only 上才加 HSTS（本地开发不加）

### 3.7 子站 location（SITES 驱动）

```nginx
# 由 render_sites_hub_conf → render_location_blocks 生成
location = /es { return 301 /es/; }
location /es/ {
    root /var/www/sites-hub/current;  # 跟随 atomic 切换的 current 软链
    try_files $uri $uri.html $uri/index.html =404;
}
```

**28 个子站全部由 `sites.sh` 的 SITES 数组驱动**——新增站点只需改 SITES + 一首页卡片 + 一项目目录。

### 3.8 资源长缓存

```nginx
location ~* "^/[^/]+/assets/.*\.(js|css|woff2|svg|png|webp|avif|ico)$" {
    add_header Cache-Control "public, max-age=31536000, immutable";
    access_log off;
    try_files $uri =404;
}
```

VitePress 1.6+ 输出文件名带 hash（`assets/chunks/framework-abc123.js`），所以 immutable 安全。

---

## 4. P3 公开元数据（**11 个 location，无 auth**）

SEO / LLM / 流量监控类公开资源，免 auth（auth_basic off）：

| URL | 类型 | 用途 |
|---|---|---|
| `/sitemap.xml` | XML | 搜索引擎索引 |
| `/sitemap.xml.gz` | gzip | sitemap 压缩版（172K → 12K，-93%） |
| `/llms.txt` | text | LLM 摘要（Markdown） |
| `/llms.txt.gz` | gzip | LLM 摘要压缩 |
| `/llms-full.txt` | text | LLM 全量内容 |
| `/llms-full.txt.gz` | gzip | LLM 全量压缩 |
| `/feed.xml` | RSS | RSS 订阅 |
| `/feed.xml.gz` | gzip | RSS 压缩 |
| `/robots.txt` | text | 爬虫规则 |
| `/manifest.webmanifest` | JSON | PWA manifest |
| `/ld.json` | JSON-LD | 结构化数据 |
| `/stats.html` | HTML | **GoAccess 流量报告** |

**nginx 配置模式**：
```nginx
location = /sitemap.xml {
    auth_basic off;
    access_log off;
    alias /var/www/sites-hub/current/www/sitemap.xml;
}
location = /sitemap.xml.gz {
    auth_basic off;
    access_log off;
    alias /var/www/sites-hub/current/www/sitemap.xml.gz;
    default_type application/gzip;
}
```

**生成端**：`sites-hub/scripts/build-sitemap-and-llms.py` 生成 4 个 metadata + .gz 副本，由 build-release.sh 在 stage 阶段自动跑。

---

## 5. 配置同步机制（single source of truth）

### 5.1 渲染脚本接口

`render-sites-hub-conf.sh` 接受 env vars：

| 变量 | 默认值 | 说明 |
|---|---|---|
| `SERVER_NAME` | `java-px.bot.cd` | VPS 域名 |
| `WEB_ROOT` | `/var/www/sites-hub` | 解压根目录 |
| `CURRENT_LINK` | `$WEB_ROOT/current` | atomic switch 软链 |
| `ACME_ROOT` | `/var/www/certbot` | certbot webroot |
| `AUTH_FILE` | `/etc/nginx/.sites-hub.htpasswd` | htpasswd 路径 |
| `CONFIG_PATH` | `/etc/nginx/sites-available/sites-hub.conf` | 写入目标 |
| `MODE` | `https` | `http-only` / `https` |

### 5.2 三方调用点

```
首次部署：deploy-vps.sh
  MODE=http-only render_sites_hub_conf    # 证书申请阶段
  MODE=https render_sites_hub_conf        # 完整 HTTPS 配置

每次部署：deploy-release.sh
  export MODE=https
  bash scripts/render-sites-hub-conf.sh   # 子 shell 隔离 env vars
  nginx -s reload
```

### 5.3 占位符替换

`render-sites-hub-conf.sh` 内 `write_https_config()` 用 `${CURRENT_LINK}` 占位符（nginx 不支持 `${VAR}` 语法），函数末尾 sed 替换：

```bash
sed -i "s|\${CURRENT_LINK}|${CURRENT_LINK}|g" "$CONFIG_PATH"
```

确保生成的 sites-hub.conf 是 nginx 能直接加载的（无 `${...}` 字面量）。

### 5.4 验证

```bash
# nginx 语法
nginx -t -c /etc/nginx/sites-available/sites-hub.conf

# 公开 URL 全部 200（无 auth_basic）
for u in /sitemap.xml /sitemap.xml.gz /llms.txt /llms-full.txt \
         /feed.xml /robots.txt /manifest.webmanifest /ld.json /stats.html; do
  curl -sI "https://java-px.bot.cd$u" | head -1
done
```

---

## 6. 部署故障排查

### 6.1 部署失败但 release 目录保留

deploy-release.sh 用 `set -e`，任何步骤失败会 exit 非零并清理当前 release。检查：

```bash
ls /var/www/sites-hub/releases/        # 历史 release
cat /var/log/nginx/error.log | tail -20
```

回滚：软链 `current` 仍指向旧 release，无需操作。

### 6.2 nginx -t 失败

```bash
nginx -t -c /etc/nginx/sites-available/sites-hub.conf
```

常见原因：
- `${CURRENT_LINK}` 没替换（render-sites-hub-conf.sh 出错）
- 路径占位符变量未导出
- cert 路径不存在（首次部署前 nginx -t 会失败，先 certbot 再 https 配置）

### 6.3 401 Unauthorized（除 P3 外所有路径）

```bash
# 1. 检查 htpasswd 文件
ls -la /etc/nginx/.sites-hub.htpasswd
# 必须 root:www-data + 640

# 2. 检查 nginx 配置 auth 行
grep -A1 "auth_basic_user_file" /etc/nginx/sites-available/sites-hub.conf
```

### 6.4 P3 公开 URL 401

`/sitemap.xml` 等 11 个公开 URL 出现 401 → 站点配置里漏了 `auth_basic off; alias ...`。修复：

```bash
# 重新跑 render-sites-hub-conf.sh（应 idempotent 修复）
sudo bash /var/www/sites-hub/scripts/render-sites-hub-conf.sh
sudo nginx -t && sudo nginx -s reload
```

### 6.5 GitHub Actions 0-step failure（私有 repo）

症状：所有 workflow 2 秒内 0 step failure。**不是 workflow 本身问题**，是 GitHub 私有 repo Actions 配额 / 临时故障。

绕过：commit message 加 `[skip ci]` 跳过 push trigger，workflow_dispatch 仍可用（但也会 0-step）。

---

## 7. 相关脚本清单

| 脚本 | 路径 | 职责 |
|---|---|---|
| `sites.sh` | `sites-hub/scripts/sites.sh` | SITES 数组（28 站） + `site_to_project` / `project_to_site` 映射 |
| `render-nginx-conf.sh` | `sites-hub/scripts/render-nginx-conf.sh` | 本地 dev conf 生成（listen 8081） |
| `render-sites-hub-conf.sh` | `sites-hub/scripts/render-sites-hub-conf.sh` | **VPS conf 生成**（listen 80/443，含 11 个 P3 location） |
| `build-release.sh` | `sites-hub/build-release.sh` | 28 站构建 + 打包 tarball |
| `deploy-vps.sh` | `sites-hub/deploy-vps.sh` | 首次部署（install + certbot + config + fail2ban + goaccess） |
| `deploy-release.sh` | `sites-hub/scripts/deploy-release.sh` | 每次部署（解压 + atomic switch + render sites-hub.conf + reload） |
| `setup-fail2ban.sh` | `sites-hub/scripts/setup-fail2ban.sh` | auth 失败监控 |
| `setup-goaccess.sh` | `sites-hub/scripts/setup-goaccess.sh` | GoAccess 流量统计 |
| `build-sitemap-and-llms.py` | `sites-hub/scripts/build-sitemap-and-llms.py` | 4 个 metadata + .gz 生成 |

---

## 8. 参考

- [ARCHITECTURE.md §8 VPS 部署](../ARCHITECTURE.md#8-vps-部署) — 高层概览
- [ARCHITECTURE.md §8.x GoAccess](../ARCHITECTURE.md#8x-goaccess-流量监控轻量零依赖) — 流量监控
- [PR-REVIEW-CHECKLIST.md](./PR-REVIEW-CHECKLIST.md) — PR 审查清单（含 nginx 变更检查项）
- [CONTRIBUTING.md](../CONTRIBUTING.md) — 贡献指南
