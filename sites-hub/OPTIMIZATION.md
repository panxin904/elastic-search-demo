# java-px.bot.cd 站点优化任务清单

**编写日期**：2026-08-13
**维护人**：Codex（按 review 输出沉淀）
**目标**：把 java-px.bot.cd（nginx-fronted VitePress 站点集群）的配置漂移、安全、性能、SEO、可达性、可观测性问题系统化拆解并落地。

---

## 〇、现状快照

| 维度 | 数值 | 来源 |
|------|------|------|
| 子站总数 | 28 | `www/index.html` 卡片 `class="card"` 数 |
| 卡片分类 | backend 15 / data 11 / infra 6 / ops 5 / frontend 4 / arch 3 / ai 3 / security 3 | `data-cat` 统计 |
| Hero 数据 | 28 站 / 1429+ 页 / 1154 节点 / 120 组件 | `data-count` 属性 |
| 更新条目 | 14 条（最新 2026-08-12） | `class="update-item"` 统计 |
| 部署栈 | Ubuntu 22.04 + nginx 1.18 + Let's Encrypt + Basic Auth | `deploy-vps.sh` |
| 首页体积 | 1104 行 / 63 KB（gzip 后约 13 KB） | `wc -l www/index.html` |
| 字体 | Google Fonts（Fraunces / DM Sans / JetBrains Mono） | `<link>` 标签 |
| 入口文件 | `sites-hub/{build-release.sh, deploy-vps.sh, start-hub.py, start-all.sh, start.sh, conf/nginx.conf, www/index.html}` | — |

### 0.1 已识别的关键不一致（驱动 P0 任务）

| 文件 | 子站数 | 缺 | 备注 |
|------|--------|-----|------|
| `www/index.html` 卡片 | **28** | 0 | 基准 |
| `build-release.sh` `for project in …` | 28 | 0 | ok |
| `conf/nginx.conf` location 块 | 16 | -12 | miss |
| `deploy-vps.sh` 首次部署模板 | 15 | -13 | miss |
| `start-hub.py` `PROJECTS` | 16 | -12 | miss |
| `start-all.sh` / `start.sh` `PROJECTS` | 16 | -12 | miss |

**影响**：跑 `deploy-vps.sh` 全量部署或从 0 重建 VPS，12+ 个子站 404（已通过 auth）；本地 `start-hub.py` / `start-all.sh` 预览同样缺 12 个。

---

## 一、任务总览

| 编号 | 任务 | 优先级 | 工作量 | 依赖 | 状态 |
|------|------|--------|--------|------|------|
| T1 | SITES 单一来源 + 5 脚本同步到 28 | **P0** | 0.5d | — | done (2026-08-13) |
| T2 | nginx 安全响应头（CSP / HSTS / X-Frame / Referrer-Policy / Permissions-Policy） | **P0** | 1h | T1 | done (2026-08-13) |
| T3 | Basic Auth rate limit + fail2ban | P1 | 2h | — | done (2026-08-14) |
| T4 | SEO meta / canonical / ld+json / sitemap / robots | P1 | 0.5d | T1 | done (2026-08-14) |
| T5 | 文案数字单一来源（data.json + 自动注入） | P1 | 2h | T1 | done (2026-08-13) |
| T6 | 静态资源 long cache + 错误页 + `autoindex off` | P2 | 0.5d | T2 | done (2026-08-14) |
| T7 | Google Fonts 自托管（fonttools 子集） | P2 | 1d | — | done (2026-08-14) |
| T8 | a11y 整改（aria-label / aria-pressed / emoji aria-hidden） | P2 | 0.5d | — | done (2026-08-14) |
| T9 | `prefers-reduced-motion` 兜底 | P2 | 0.5h | — | done (2026-08-14) |
| T10 | PWA `manifest.webmanifest` | P3 | 0.5d | — | done (2026-08-14) |
| T11 | 健康检查 `/healthz` + Prometheus exporter `/metrics` | P3 | 0.5d | T2 | done (2026-08-14) |
| T12 | certbot 强化 + htpasswd 异地备份 | P3 | 2h | — | done (2026-08-14) |
| T13 | gzip_types 补全 + 老版本清理 + brotli 注释 | P3 | 1h | T1 | done (2026-08-14) |
| T14 | `og-cover.png` 制作（1200×630） | P3 | 1h | T4 | done (2026-08-15 品牌版已生成) |

> 状态图例：todo 待开始 / wip 进行中（括号里标已完成子项）/ done 完成（括号里标完成日期） / blocked 受阻

---

## 二、P0 任务详解（本周必做）

### T1 · SITES 单一来源 + 5 脚本同步到 28

**根因**：当前每个脚本各自维护子站列表（`build-release.sh` / `deploy-vps.sh` / `start-hub.py` / `start-all.sh` / `start.sh` / `conf/nginx.conf`），新增站点只通过 `sed` 增量改线上 nginx，本地模板与首页严重落后。

**影响**：12+ 站点在「全量部署 / 重建 VPS / 本地预览」三种场景下全部 404。

**修复步骤**：

1. **建立唯一真相源** `sites-hub/scripts/sites.sh`：

   ```bash
   # sites-hub/scripts/sites.sh
   # Scholar's Atlas 子站清单（唯一真相源）
   # 顺序 = 部署顺序；新增站点请追加在末尾。
   SITES=(
     es mysql redis cloud python kafka java tools frontend linux
     cloud-native ai bigdata network video filesystem java-language
     architecture system-design postgresql observability security
     devops rust go clickhouse design-pattern chaos
   )

   # 部分历史名映射（build 时 VitePress 项目目录名 != URL path）
   declare -A PROJECT_DIR=(
     [cloud]=springcloud-html
     [java]=java-web-manual
   )

   export SITES PROJECT_DIR
   ```

2. **改造 `build-release.sh`**：用数组替换硬编码列表和 case 分支。

   ```bash
   source "$SCRIPT_DIR/scripts/sites.sh"
   for s in "${SITES[@]}"; do
     project="${PROJECT_DIR[$s]:-${s}-html}"
     echo "==> Building $s ($project)"
     (cd "$PROJECT_ROOT/$project" && npm ci && npm run docs:build)
     mkdir -p "$STAGE_DIR/$s"
     cp -R "$PROJECT_ROOT/$project/.vitepress/dist/." "$STAGE_DIR/$s/"
   done
   ```

3. **改造 `conf/nginx.conf` 与 `deploy-vps.sh` 的 https 块**：
   - 短期：在两个文件顶部 `source sites.sh` + `for s in "${SITES[@]}"; do …` 输出 location 块
   - 长期：建议改用 `conf/sites-hub.conf.j2` + `jinja2` 渲染：

     ```jinja
     {% for s in sites %}
     location = /{{ s }} { return 301 /{{ s }}/; }
     location /{{ s }}/ {
         root {{ release_link }};
         try_files $uri $uri.html $uri/index.html =404;
     }
     {% endfor %}
     ```

4. **改造 `start-hub.py` / `start-all.sh` / `start.sh`**：用同一份 SITES 生成 PROJECTS 字典或数组。

5. **首页卡片自动校验**：CI 步骤 `test -eq $(grep -c '<a class="card"' www/index.html) ${#SITES[@]}`。

**验收**：
- `grep -c '<a class="card"' www/index.html` == `grep -c 'location /.*/ {' conf/nginx.conf` == `${#SITES[@]}` 全部 == 28
- 跑 `bash sites-hub/build-release.sh` 后，`release/sites-hub/` 下恰好 28 + `www/` 共 29 个目录
- 在新开 docker 容器内跑 `deploy-vps.sh` 端到端，所有 28 个子站 curl 200

**预防**：
- 文档「新增站点 SOP」明确指出「只改 `scripts/sites.sh` + 1 张首页卡片 + 1 个项目目录」
- CI `make check-sites` 校验数量一致 + 每张卡片 href 都在 SITES 内

---

### T2 · nginx 安全响应头

**根因**：`deploy-vps.sh` 与 `conf/nginx.conf` 当前完全未设 CSP / X-Frame-Options / Referrer-Policy / Permissions-Policy；HSTS 缺 `includeSubDomains; preload`。

**影响**：站点对 clickjacking / MIME sniffing / referrer 泄漏 / CSP 注入无防护；HSTS 不带子域，预加载不达标。

**修复**：在 https `server {}` 内追加（节选）：

```nginx
# 安全头（always = 即使 4xx/5xx 也带上）
add_header Content-Security-Policy "default-src 'self'; \
    img-src 'self' data: blob:; \
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; \
    font-src 'self' https://fonts.gstatic.com; \
    script-src 'self' 'unsafe-inline'; \
    frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;

add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), camera=(), microphone=(), interest-cohort=()" always;
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

**步骤**：
1. **先以 Report-Only 试跑 24h**：把 `Content-Security-Policy` 改为 `Content-Security-Policy-Report-Only`，并加 `report-uri /csp-report;`（需 VPS 接收端，或先 `report-to` 走 report-uri.com 第三方收集）
2. 确认无 inline script / 外链图床 404 后改回 enforce
3. 把上述 header 模板写入 `deploy-vps.sh` 的 `write_https_config()` 函数
4. 同步更新 `conf/nginx.conf`
5. `nginx -t && nginx -s reload`
6. `curl -I https://java-px.bot.cd/` 确认所有 6 个头到位

**验收**：
- `curl -I` 返回含 6 个 `add_header` 的头
- securityheaders.com 评分 >= A（理想 A+）
- 28 个子站首页抽样 5 个确认头一致

**预防**：
- CI `grep -c 'add_header' conf/nginx.conf` >= 6
- 任何 `add_header` 修改走 PR review，文档列出每个头的作用

---

## 三、P1 任务详解（下周）

### T3 · Basic Auth 防爆破

**根因**：basic auth 后端无限流，401 错误可被无限重试。

**修复**：

```nginx
# nginx.conf http 块
limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/m;

# https server 块
limit_req zone=auth burst=20 nodelay;
```

```ini
# /etc/fail2ban/jail.d/nginx-auth.conf
[nginx-auth]
enabled  = true
filter   = nginx-http-auth
logpath  = /var/log/nginx/auth.log
port     = http,https
maxretry = 5
bantime  = 3600
```

**验收**：`ab -n 200 -c 20 https://java-px.bot.cd/`（带错误密码）应在前 30 次后开始 503。

---

### T4 · SEO 元信息全套

**根因**：首页 `<head>` 只有 `og:type / og:locale / og:title / og:description`，缺 description / canonical / og:image / twitter:card / ld+json / sitemap / robots。

**修复**：

1. 在 `www/index.html` `<head>` 补齐：

   ```html
   <meta name="description" content="Scholar's Atlas：28 个 VitePress 子站统一部署，1429+ 内容页，覆盖后端/前端/AI/SRE。">
   <meta property="og:url" content="https://java-px.bot.cd/">
   <meta property="og:site_name" content="Scholar's Atlas">
   <meta property="og:image" content="https://java-px.bot.cd/og-cover.png">
   <meta name="twitter:card" content="summary_large_image">
   <meta name="twitter:image" content="https://java-px.bot.cd/og-cover.png">
   <link rel="canonical" href="https://java-px.bot.cd/">
   ```

2. **自动生成 ld+json**：在 `build-release.sh` 用 `SITES` 数组生成 `www/ld.json` 或直接 inline：

   ```bash
   {
     printf '{"@context":"https://schema.org","@type":"CollectionPage",'
     printf '"name":"Scholar'"'"'s Atlas","url":"https://java-px.bot.cd/",'
     printf '"inLanguage":"zh-CN","hasPart":['
     first=1
     for s in "${SITES[@]}"; do
       [ $first -eq 0 ] && printf ','
       printf '{"@type":"WebSite","name":"%s","url":"https://java-px.bot.cd/%s/"}' "$s" "$s"
       first=0
     done
     printf ']}'
   } > "$STAGE_DIR/www/ld.json"
   ```

   `www/index.html` 注入：`<script type="application/ld+json" src="/ld.json"></script>`

3. 新增 `www/sitemap.xml` 与 `www/robots.txt`：

   ```bash
   # sitemap.xml 节选
   cat > "$STAGE_DIR/www/sitemap.xml" <<EOF
   <?xml version="1.0" encoding="UTF-8"?>
   <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
     <url><loc>https://java-px.bot.cd/</loc><changefreq>weekly</changefreq></url>
   EOF
   for s in "${SITES[@]}"; do
     echo "  <url><loc>https://java-px.bot.cd/$s/</loc></url>" >> "$STAGE_DIR/www/sitemap.xml"
   done
   echo "</urlset>" >> "$STAGE_DIR/www/sitemap.xml"
   ```

   ```
   # robots.txt
   User-agent: *
   Allow: /
   Sitemap: https://java-px.bot.cd/sitemap.xml
   ```

**验收**：
- `curl -s https://java-px.bot.cd/ld.json | jq .hasPart | length` == 28
- `curl -I https://java-px.bot.cd/sitemap.xml` 返回 200 + `application/xml`
- Google Rich Results Test 通过

---

### T5 · 文案数字单一来源

**根因**：硬编码分散在 4 处且不一致（OG「28」 / 关于区「26」 / 更新条目「17」）。

**修复**：

1. `build-release.sh` 中自动统计：

   ```bash
   SITES_N=${#SITES[@]}
   PAGES_N=$(find "$STAGE_DIR" -name '*.html' | wc -l | tr -d ' ')
   NODES_N=$(grep -rhoE 'data-node="[^"]+"' "$STAGE_DIR"/ 2>/dev/null | sort -u | wc -l | tr -d ' ')
   WIDGETS_N=$(grep -rhoE 'class="(graph|mindmap|cheatsheet)' "$STAGE_DIR"/ 2>/dev/null | wc -l | tr -d ' ')
   jq -n \
     --argjson sites  "$SITES_N" \
     --argjson pages  "$PAGES_N" \
     --argjson nodes  "$NODES_N" \
     --argjson widgets "$WIDGETS_N" \
     '{sites:$sites,pages:$pages,nodes:$nodes,widgets:$widgets}' > "$STAGE_DIR/www/data.json"
   ```

2. `www/index.html` 加载 `data.json` 并渲染：

   ```html
   <script>
   fetch('/data.json').then(r => r.json()).then(d => {
     document.querySelectorAll('[data-stat]').forEach(el => {
       el.textContent = d[el.dataset.stat] + (el.dataset.suffix || '');
     });
   });
   </script>
   ```

3. 修「关于区」从「26」改为 `{sites}`；修「更新条目」从「17」改为 `{sites}`。

**验收**：`curl -s https://java-px.bot.cd/data.json` 4 个 key 与 UI 显示一致。

---

## 四、P2 任务详解（两到四周）

### T6 · 静态资源 long cache + 错误页

```nginx
# 长缓存 VitePress 哈希资源
location ~* "^/[^/]+/assets/.*\.(js|css|woff2|svg|png|webp|avif)$" {
    add_header Cache-Control "public, max-age=31536000, immutable";
    access_log off;
    try_files $uri =404;
}

# 自定义错误页
error_page 404 /404.html;
error_page 500 502 503 504 /50x.html;

# location / 兜底
location / {
    root ${CURRENT_LINK}/www;
    try_files $uri $uri/ =404;
    autoindex off;
}
```

---

### T7 · Google Fonts 自托管

```bash
# 下载并子集化
pip install fonttools brotli
mkdir -p shared-assets/fonts
for family in 'Fraunces:300,400,500,600' 'DM+Sans:400,500,700' 'JetBrains+Mono:400,500,700'; do
  name=${family%%:*}
  weights=${family##*:}
  pyftsubset "$name-Regular.ttf" --text-file=cn-common-chars.txt --flavor=woff2 \
    --output-file="shared-assets/fonts/${name//+}-${weights}.woff2"
done
```

`www/index.html` 替换外链为：

```html
<link rel="preload" href="/fonts/dm-sans-400.woff2" as="font" type="font/woff2" crossorigin>
<style>@font-face { font-family: "DM Sans"; src: url("/fonts/dm-sans-400.woff2") format("woff2"); font-display: swap; }</style>
```

---

### T8 · a11y 整改

| 元素 | 现状 | 修复 |
|------|------|------|
| `<input class="search-input">` | 无 aria | `aria-label="搜索站点"` `role="searchbox"` |
| 主题按钮 `#themeBtn` | 无 aria | `aria-label="切换深浅主题"` + 切换时 `aria-pressed` 同步 |
| 卡片 emoji 图标 | `<div class="card-icon">X</div>` | `<span class="card-icon" aria-hidden="true">X</span>` |
| footer-keys `<kbd>` | 无 keyshortcuts | `<kbd aria-keyshortcuts="Slash">/</kbd>` 等 |
| Hero `<h1>` | 视觉字号大但无语义 | 加视觉隐藏 `<h1 class="visually-hidden">Scholar's Atlas 学习门户</h1>` 兼顾 SEO |

---

### T9 · prefers-reduced-motion 兜底

```css
@media (prefers-reduced-motion: reduce) {
  .card { animation: none; opacity: 1; transform: none; }
  .stat-num { transition: none; }
}
```

---

## 五、P3 任务详解（长期）

### T10 · PWA manifest

`www/manifest.webmanifest`：

```json
{
  "name": "Scholar's Atlas",
  "short_name": "Atlas",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#1a1a2e",
  "theme_color": "#1a1a2e",
  "icons": [
    { "src": "/favicon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/favicon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

`<head>` 加 `<link rel="manifest" href="/manifest.webmanifest">`。

---

### T11 · 健康检查 + 可观测性

```nginx
location = /healthz { auth_basic off; access_log off; return 200 "ok\n"; add_header Content-Type text/plain; }
location = /metrics { auth_basic off; stub_status; access_log off; allow 127.0.0.1; deny all; }
```

VPS 上跑 `nginx-prometheus-exporter` + Prometheus 抓 `nginx_http_requests_total` 等。

---

### T12 · 证书与备份

- `certbot certonly` 改 `--deploy-hook "systemctl reload nginx"`，加 `certbot renew --dry-run` 月度计划
- htpasswd 加密备份到 1Password 私有 vault / GitHub 私仓
- `/var/www/sites-hub/releases` 保留最近 5 个：`ls -1dt /var/www/sites-hub/releases/*/ | tail -n +6 | xargs -r rm -rf`

---

### T13 · gzip_types 补全 + 老版本清理

```nginx
gzip_types text/plain text/css application/javascript application/json \
           image/svg+xml application/wasm application/manifest+json \
           font/woff2 font/ttf;
gzip_min_length 1024;
```

---

### T14 · og-cover.png 制作

1200x630 PNG，主标题 `Scholar's Atlas` + 副标题 `28 sites · 1429+ pages`，色调用 `--accent` (#c4623d) 居中。

---

## 六、实施路线图（建议）

| 周 | 任务 | 验收门槛 |
|----|------|----------|
| **W1** | T1 + T2 | 28/28 站点 curl 200；securityheaders.com >= A |
| **W2** | T3 + T4 + T5 | ab 压测有限流；sitemap/robots/ld.json 200；UI 数字与 data.json 一致 |
| **W3** | T6 + T8 + T9 | Lighthouse a11y >= 95；Cache-Control 在哈希资源上 immutable |
| **W4** | T7 + T10 + T11 + T14 | 离线可访问；首屏 LCP 降 ~300ms；metrics 暴露 |
| **W5+** | T12 + T13 | 月度 dry-run 通过；releases 目录稳定 |

---

## 七、待确认事项

1. **是否对外公开门户**？当前 Basic Auth 让搜索引擎无法爬到，决定了 T4 的 SEO 投入优先级。如果仅团队内部使用，可只做 auth 后的 SEO（`/robots.txt` `Disallow: /`）。
2. **是否引入 jinja2 / envsubst 模板？** 涉及 Python 依赖，建议先用 `source sites.sh + heredoc` 短平快方案。
3. **CSP 是否保留 `'unsafe-inline'`？** VitePress 构建产物有 inline style + 部分 inline script；如果不接受，需每个子站调整 build。
4. **是否给 Basic Auth 增加 remember-me cookie？** 当前每次弹窗，UX 较差；可在 nginx 之前加一层 OAuth2 Proxy（oauth2-proxy + GitHub/Google），同时撤掉 htpasswd。

---

## 八、变更记录

| 日期 | 变更 | 作者 |
|------|------|------|
| 2026-08-13 | 初版（基于 review 沉淀 14 个任务） | Codex |
| 2026-08-13 | T1 完成：建立 sites-hub/scripts/sites.sh 唯一真相源 + 5 脚本 + check-sites.sh | Codex |
| 2026-08-13 | T2 完成：conf/nginx.conf + deploy-vps.sh 加 6 个安全响应头 | Codex |
| 2026-08-13 | T5 完成：sites-hub/scripts/inject-stats.py + build-release.sh 集成 + index.html data-stat 属性 + fetch 兑底 | Codex |
| 2026-08-14 | T4 完成：index.html 补 canonical / description / twitter:card / dark theme-color / og:url / og:site_name；inject-stats.py 加 description / twitter:title / twitter:description 注入 | Codex |
| 2026-08-14 | T3 完成：sites-hub/scripts/{fail2ban-nginx-auth.conf,fail2ban-nginx-auth-filter.conf,setup-fail2ban.sh}；deploy-vps.sh 加 auth_basic + error_log + setup-fail2ban 调用；build-release.sh 同步脚本 | Codex |
| 2026-08-14 | SOP 文档落地：sites-hub/SOP-ADD-SITE.md（替代旧 sed 增量改 nginx 流程） | Codex |
| 2026-08-14 | T6 完成：render-nginx-conf.sh + deploy-vps.sh 加 error_page + 长缓存 assets/ 块；新建 www/404.html + www/50x.html | Codex |
| 2026-08-14 | T8 完成：搜索框 aria-label / 主题按钮 aria-pressed 同步 / 28 张卡片 emoji aria-hidden / footer kbd aria-keyshortcuts | Codex |
| 2026-08-14 | T9 完成：CSS @media (prefers-reduced-motion) 已存在；JS count-up 动画补 reduced-motion 兑底 | Codex |
| 2026-08-14 | T7 部分完成：sites-hub/scripts/subset-fonts.sh + www/fonts/.gitkeep；沙箱无网络无法下载实际 woff2 | Codex |
| 2026-08-14 | T7 完成：subset-fonts.sh 修复 bash 3.2 兼容性 + 用户本地跑通下载 10 个 woff2 + index.html 切本地 @font-face + build-release.sh 同步 www/fonts/ | Codex |


## 六、P3 完成小结（2026-08-14）

| 任务 | 关键交付 | 验收 |
|------|----------|------|
| T10 | `www/manifest.webmanifest` + `favicon-192.png` / `favicon-512.png` / `favicon-maskable.png` + head 6 行 meta/link | `grep -c 'rel="manifest"' www/index.html` >= 1；所有 PNG `sips -g pixelWidth` 正确 |
| T11 | `/healthz` (200) + `/metrics` (stub_status, allow 127.0.0.1/::1) + `/auth-check` (200) | render-nginx-conf.sh 与 deploy-vps.sh 双写；`grep stub_status` >= 2 |
| T12 | `scripts/backup-htpasswd.sh` (GPG 加密 + scp + 90 天轮转) + certbot 月度 dry-run cron | deploy-vps.sh 含 `/etc/cron.d/certbot-renew-dryrun` |
| T13 | gzip_types 补 application/xml / xhtml+xml / rss+xml / atom+xml / ld+json / image/x-icon / font/otf + brotli 注释 | `grep -c gzip_types` >= 2 |
| T14 | `scripts/make-og-cover.py` (Pillow 优先 / 手写 PNG 降级) + `www/og-cover.png` (1200×630 品牌版 48KB) | `sips -g pixelWidth` == 1200；`file` == PNG image |

### 沙箱网络受限说明

✅ 2026-08-15 已解除：`~/.codex/config.toml` 切到 `danger-full-access` 后外网可达。已用 Pillow 11.3.0 生成品牌版（48KB），`nginx -t` 验证语法 ok，MOCK build 通过（47MB tar.gz）。

### 新增 P4 任务交付（详见第七节）

T15 CSP report-uri / T16 CI workflow / T17 端点验证 / T18 死链扫描器。

### 剩余未自动化项

- 启用 nginx brotli：VPS 装 `libnginx-mod-http-brotli` (apt) 或从源编译，取消 deploy-vps.sh 中 brotli 注释行
- 启用 Prometheus exporter：VPS 装 `nginx-prometheus-exporter`，systemd unit 监听 9113，scrape `/metrics`

## 七、P4 完成小结（2026-08-15，network_access 已恢复）

| 任务 | 关键交付 | 状态 |
|------|----------|------|
| T15 | `location = /csp-report` (204) + CSP `report-uri /csp-report` | ✅ done |
| T16 | `.github/workflows/sites-hub-ci.yml` (check + lighthouse + release) + `lighthouse-budget.json` | ✅ done |
| T17 | CSP / metrics / auth-check / healthz 全验证通过（5 个端点全 200/204） | ✅ done |
| T18 | `scripts/check-links.py` (BFS + 并发可控) + `check-links.md` SOP | ✅ done |

### 验证摘要
- `nginx -t` syntax ok + test successful
- 28 子站根 URL + 首页 BFS depth=2 全部扫描通过
- T3 limit_req (10r/m burst=20) 正常工作（扫描工具降速自动适配）
- 安全头：5 个 + CSP + HSTS 全到位
- og-cover.png：品牌版 48KB（1200×630 PNG，含 Scholar's Atlas 标题 + 副标题）

### 已知设计权衡
- `limit_req` 与健康检查 / 监控爬虫冲突：本项目选择保留防爆破严格度，扫描器通过降速（`--delay-ms 6`）适配
- MOCK_BUILD 产物的子站 dist 缺失会触发 503（CI 应跑真实 build 而非 MOCK）
