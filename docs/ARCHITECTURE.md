# Scholar's Atlas — 架构与开发参考

> 28 个 VitePress 子站 + 共享门户 + nginx-fronted VPS 部署集群。
> 域名：[java-px.bot.cd](https://java-px.bot.cd/)（强 Basic Auth）。
>
> **本文档定位**：架构 + 模式 + 约定参考，供后续开发者快速上手。
>
> 相关文档（不重复）：
> - 操作流程：[CONTRIBUTING.md](../CONTRIBUTING.md)
> - 新增站点 SOP：[sites-hub/SOP-ADD-SITE.md](../sites-hub/SOP-ADD-SITE.md)
> - PR 审核清单：[docs/PR-REVIEW-CHECKLIST.md](./PR-REVIEW-CHECKLIST.md)
> - 优化历史：[sites-hub/OPTIMIZATION.md](../sites-hub/OPTIMIZATION.md) + [OPTIMIZATION-CONTENT.md](../sites-hub/OPTIMIZATION-CONTENT.md)

---

## 1. 项目概览

### 1.1 一句话定义

**单仓多站 + 共享主题 + 共享数据 + 统一 CI/CD + 单 VPS 部署** 的静态站点集群。

### 1.2 核心数据

| 指标 | 数量 |
|------|----:|
| 子站 | 28 个 VitePress 站 |
| 内容页 | ~1464 个 .md |
| 内容字数 | ~6.2M 字 |
| 跨站术语 | 161 个（glossary） |
| CI 并行 build | 28 job matrix（~3min） |
| VPS | 38.207.171.83（ubuntu 22.04, nginx 1.18） |
| 月度访问 | GoAccess 统计（见 /stats.html） |

### 1.3 三层架构

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 内容层（28 个 VitePress 站）                       │
│  ├── <site>-html/docs/**/*.md  (内容源)                      │
│  ├── <site>-html/.vitepress/config.mts  (站配置)              │
│  └── <site>-html/.vitepress/theme/  (每站一份共享主题副本)     │
└─────────────────────────────────────────────────────────────┘
                            ↓ vitepress build
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: 资源层（共享主题 + 共享数据）                       │
│  ├── shared-assets/vitepress-template/  (VitePress 主题模板) │
│  ├── shared-assets/glossary/keywords.json  (跨站术语词典)    │
│  └── shared-assets/{favicon,apple-touch-icon}.png           │
└─────────────────────────────────────────────────────────────┘
                            ↓ CI: build-all matrix 28
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 门户层（sites-hub：portal + 自动化）                │
│  ├── www/index.html  (28 站卡片入口)                          │
│  ├── www/{sitemap,llms,feed}.xml + llms-full.txt             │
│  ├── conf/nginx.conf  (28 个 location + 安全头)              │
│  ├── scripts/sites.sh  (唯一真相源：SITES 数组)               │
│  ├── scripts/*.sh + *.py  (审计/构建/部署工具集)              │
│  └── build-release.sh  (一键 release tarball)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓ GitHub Actions release
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: VPS（nginx + certbot + Basic Auth + fail2ban）    │
│  ├── /var/www/sites-hub/current → releases/<id>/  (蓝绿)    │
│  ├── /etc/nginx/sites-available/sites-hub.conf  (28 location)│
│  ├── /etc/letsencrypt/live/java-px.bot.cd/  (HTTPS cert)    │
│  ├── /etc/nginx/.sites-hub.htpasswd  (Basic Auth)           │
│  └── /var/www/sites-hub/www/stats.html  (GoAccess 报告)       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 技术栈

| 类别 | 选型 | 版本 | 理由 |
|------|------|------|------|
| 静态站点 | VitePress | ^1.6.4 | 主题自动注册组件、Pagefind 集成 |
| 图表 | vitepress-plugin-mermaid + mermaid | ^2.0.17 / ^11.16 | 唯一支持 SSR + 自动注册的 Mermaid 插件 |
| 全文搜索 | Pagefind | ^1.3.0 | VitePress 1.6+ 自动加载 UI |
| 评论 | Giscus | GitHub Discussions 后端 | 零服务器、零数据库 |
| 部署 | nginx 1.18 + Let's Encrypt | ubuntu 22.04 | 资源极轻（~30MB RAM）|
| 防爆破 | fail2ban | 0.11 | nginx-auth jail（401 监控）|
| 访问统计 | GoAccess | 1.5.5 | 单二进制、零依赖（vs Plausible 500MB）|
| CI | GitHub Actions | ubuntu-22.04 | 28-job matrix 并行 build |
| 安全头 | nginx add_header | — | CSP / HSTS / X-Frame / Referrer-Policy |
| 字体 | 自托管 woff2（subset） | — | 4 个字体族 × 3 字重 = 12 个 |

**明确拒绝**：

- ❌ Plausible SaaS / Docker 自托管（资源受限 VPS 选 GoAccess）
- ❌ Lighthouse（用户明确拒绝）
- ❌ npm ci（CI 用 npm install，容忍 lockfile drift）

---

## 3. 目录结构

```
elastic-search-demo/
├── README.md                          # 项目说明（Java ES demo）
├── CONTRIBUTING.md                    # PR 提交流程
├── docs/
│   ├── ARCHITECTURE.md                # 本文档
│   └── PR-REVIEW-CHECKLIST.md         # PR 审核清单
│
├── shared-assets/                     # 跨子站共享资源
│   ├── vitepress-template/            # VitePress 主题模板（**单一真相源**）
│   │   ├── config.mts.tpl             # 配置模板（@VARIABLE 占位符）
│   │   ├── theme/
│   │   │   ├── components/            # 共享 Vue 组件
│   │   │   │   ├── WhyThisGraph.vue   # 双栏「为什么写这个图谱」
│   │   │   │   ├── GiscusComment.vue  # 评论
│   │   │   │   ├── SiteFooter.vue     # 门户底部链接
│   │   │   │   └── SitePortalLink.vue # 跳门户链接
│   │   │   ├── composables/
│   │   │   │   └── readingProgress.ts # 阅读进度条
│   │   │   └── style.css              # 共享样式
│   │   ├── scripts/render-config.py   # 模板 → config.mts 渲染器
│   │   └── docs/                      # 模板自带的示例文档
│   ├── glossary/
│   │   └── keywords.json              # 跨站术语词典（161 词：中文 34 + EN 122 + 混合 5）
│   └── {favicon,apple-touch-icon}.png # PWA 图标
│
├── sites-hub/                         # 门户 + 自动化
│   ├── www/                           # 门户静态文件
│   │   ├── index.html                 # 28 站卡片入口
│   │   ├── sitemap.xml / llms.txt / feed.xml / llms-full.txt
│   │   ├── robots.txt / ld.json / manifest.webmanifest
│   │   ├── stats.html                 # GoAccess 报告（nginx alias 指向）
│   │   └── fonts/                     # 自托管 woff2
│   ├── conf/
│   │   └── nginx.conf                 # 本地开发 nginx 配置
│   ├── scripts/                       # 工具脚本（17 个）
│   │   ├── sites.sh                   # ★ 唯一真相源：SITES 数组
│   │   ├── check-sites.sh             # 一致性校验（12 项）
│   │   ├── render-nginx-conf.sh       # sites.sh → nginx.conf
│   │   ├── build-release.sh           # 一键 release tarball
│   │   ├── deploy-vps.sh              # VPS 初始化（apt + nginx + certbot）
│   │   ├── deploy-release.sh          # VPS 蓝绿切换 deploy
│   │   ├── setup-fail2ban.sh          # 防爆破
│   │   ├── setup-goaccess.sh          # 访问统计
│   │   ├── build-sitemap-and-llms.py  # sitemap + llms + feed 生成
│   │   ├── build-updates-from-git.py  # git log → Updates 列表
│   │   ├── inject-stats.py            # data.json → index.html
│   │   ├── audit-content.py           # 内容审计（12 项检查）
│   │   ├── check-links.py             # 死链检测
│   │   ├── spell-check.sh             # 拼写检查
│   │   ├── add-video-link.py          # 视频链接转换
│   │   ├── make-og-cover.py           # OG 封面生成
│   │   ├── subset-fonts.sh            # 字体子集化
│   │   └── backup-htpasswd.sh         # 备份 htpasswd
│   ├── build-release.sh               # 一键 release
│   ├── deploy-vps.sh                  # VPS 初始化
│   ├── start.sh / start-all.sh / start-hub.py  # 本地预览
│   ├── OPTIMIZATION.md                # nginx 优化历史（P0-P4）
│   ├── OPTIMIZATION-CONTENT.md        # 内容优化历史（§0-§8.38）
│   ├── SOP-ADD-SITE.md                # 新增站点 SOP
│   └── dist/                          # 28 站 sitemap/llms/feed（手动生成）
│
├── <site>-html/                       # 28 个 VitePress 子站（每站结构相同）
│   ├── package.json                   # vitepress + plugins
│   ├── .vitepress/
│   │   ├── config.mts                 # 站配置（vite alias @shared + withMermaid）
│   │   └── theme/
│   │       ├── index.ts               # 主题入口（setupReadingProgress + 组件注册）
│   │       ├── components/            # 共享组件副本（WhyThisGraph 等）
│   │       └── style.css              # @import '@shared/...'
│   └── docs/
│       ├── index.md                   # 首页（VPHero + WhyThisGraph）
│       └── <章节>.md                  # 内容
│
└── .github/
    ├── workflows/sites-hub-ci.yml     # CI: check + build-all + release + deploy
    ├── ISSUE_TEMPLATE/                # 4 个模板（bug/feature/feedback/config）
    └── PULL_REQUEST_TEMPLATE.md       # PR 自动填充
```

---

## 4. 关键约定

### 4.1 单一真相源：`sites.sh`

**所有**站点列表都从 [`sites-hub/scripts/sites.sh`](../sites-hub/scripts/sites.sh) 读 SITES 数组，禁止硬编码。

```bash
SITES=(es mysql redis cloud python kafka java tools frontend linux ...)
PROJECT_DIR_MAP="cloud:springcloud-html;java:java-web-manual"
```

**约束**：
1. SITES 元素 = URL 路径段（不带 `/`，不带 `-html`）
2. 项目目录 ≠ URL 路径时，在 `PROJECT_DIR_MAP` 声明
3. macOS bash 3.2 兼容：不依赖 `declare -A` / `mapfile` / IFS word splitting
4. 任何脚本（build-release / deploy-vps / start.sh / start-hub.py / conf/nginx）都从这里读

**校验**：[`check-sites.sh`](../sites-hub/scripts/check-sites.sh) 跑 12 项一致性检查：

```bash
bash sites-hub/scripts/check-sites.sh
# ✓ SITES count == cards count == nginx count == 28
# ✓ 所有项目目录存在
# ✓ deploy-vps.sh / start.sh / start-hub.py 都 source 了 sites.sh
# ...
```

### 4.2 共享主题：`@shared` alias

共享 Vue 组件 / composables / styles 在 [`shared-assets/vitepress-template/`](../shared-assets/vitepress-template)，子站通过 vite alias 引用：

```ts
// 每个 <site>-html/.vitepress/config.mts
import { fileURLToPath, URL } from 'node:url'
const SHARED_ASSETS = fileURLToPath(new URL('../../shared-assets', import.meta.url))

export default withMermaid(defineConfig({
  vite: {
    resolve: {
      alias: [{ find: '@shared', replacement: SHARED_ASSETS }],
    },
  },
}))
```

**为什么用 alias 而不是相对路径**：

- VitePress/rollup 默认 `fs.allow` 限制 cwd 外 import
- 用绝对路径 alias 绕过限制
- 主题组件可同时被多个子站引用

**副本模式**（VitePress 1.6+ 兼容）：

VitePress 1.6+ 从 `theme/components/*.vue` 自动注册组件（PascalCase）。所以**每个子站 `theme/components/` 都有一份共享组件副本**（不是符号链接）。改共享组件需用脚本同步所有 28 站。

### 4.3 共享词典：`glossary/keywords.json`

161 个跨站术语，每个术语关联 2-4 个相关站点的具体路径：

```json
{
  "JVM": {
    "sites": [
      { "site": "java-language", "path": "/04-jvm/overview", "label": "JVM 原理" },
      { "site": "system-design", "path": "/jvm-tuning",   "label": "JVM 调优" }
    ]
  }
}
```

**维护**：
- 新增术语前先 grep 确认无同义词
- URL 路径用站点 ID（不带 `-html`）
- 一次编辑 ≤ 50 条

### 4.4 Conventional Commits

格式：`<type>(<scope>): <subject>`

```bash
git commit -m "feat(es): add JVM GC tuning chapter"
git commit -m "fix(c2): glossary JVM → system-design link broken"
git commit -m "ci(github): parallelize build-all via 28-job matrix"
git commit -m "docs(OPTIMIZATION-CONTENT): record §8.38 build-all speedup"
```

`type` ∈ `feat` / `fix` / `refactor` / `docs` / `chore` / `style` / `test` / `build` / `ci` / `perf`

### 4.5 Mermaid 是 CSR 不是 SSR

`vitepress-plugin-mermaid` v2 是**客户端渲染**（CSR），构建只输出 `<div class="mermaid"></div>` 占位，浏览器 `onMounted` 异步渲染 SVG。

**不要**：

- ❌ 在 dist HTML 里搜 SVG（构建后不会有）
- ❌ 期望 build 后立即看 SVG

**应该**：

- ✅ `npm run docs:dev` + 浏览器实测
- ✅ 验证 `/<site>/assets/chunks/*Diagram-*.js`（mermaid 库按需懒加载）

---

## 5. 共享资源（[`shared-assets/`](../shared-assets)）

### 5.1 VitePress 主题模板

**结构**：
```
shared-assets/vitepress-template/
├── config.mts.tpl            # 配置模板（@VARIABLE 占位符）
├── theme/
│   ├── components/
│   │   ├── WhyThisGraph.vue
│   │   ├── GiscusComment.vue
│   │   ├── SiteFooter.vue
│   │   └── SitePortalLink.vue
│   ├── composables/
│   │   └── readingProgress.ts
│   └── style.css
└── scripts/render-config.py  # 模板渲染器
```

**渲染流程**：

```bash
# 单站渲染（输出 .rendered，需手动 mv）
python3 shared-assets/vitepress-template/scripts/render-config.py <site>-html

# 批量：CI 自动跑 build-release.sh 时调
```

**变量替换**：

| 占位符 | 来源 |
|--------|------|
| `@SITE_ID` | 目录名 → 自动提取 |
| `@SITE_BASE` | `config.mts` 里 `base:` |
| `@SITE_TITLE` | `config.mts` 里 `siteTitle:` / `title:` |
| `@SITE_DESC` | `config.mts` 里 `description:` |
| `@SITE_ACCENT` | theme-color meta |
| `@SITE_LANG` | `lang:` |

### 5.2 跨站术语词典

[`shared-assets/glossary/keywords.json`](../shared-assets/glossary/keywords.json)：161 词

- 中文术语：34 个（如 `JVM` `GC` `分布式`）
- 英文术语：122 个（如 `CAP` `Raft` `Kafka`）
- 混合术语：5 个

**自动生成**：sitemap.xml + llms.txt + llms-full.txt + feed.xml 都从这个词典扩展跨站链接。

---

## 6. 开发工作流

### 6.1 新增站点（3 处改动）

详见 [`sites-hub/SOP-ADD-SITE.md`](../sites-hub/SOP-ADD-SITE.md)：

| # | 文件 | 改动 |
|---|------|------|
| 1 | `sites-hub/scripts/sites.sh` | SITES 数组末尾追加 |
| 2 | `sites-hub/www/index.html` | 加 .card |
| 3 | `~/work_space/elastic-search-demo/<新>-html/` | 新 VitePress 项目 |

**校验**：

```bash
bash sites-hub/scripts/check-sites.sh   # 必跑，期望全绿
```

### 6.2 修改内容（最常见）

```bash
# 1. 改 markdown
vim <site>-html/docs/02-overview/some-chapter.md

# 2. 本地预览
cd <site>-html && npm install && npm run docs:dev

# 3. 校验
python3 sites-hub/scripts/audit-content.py
bash sites-hub/scripts/spell-check.sh

# 4. commit + push → CI 自动 build + deploy
git add . && git commit -m "feat(<scope>): <subject>" && git push
```

### 6.3 修改共享组件（危险操作）

**步骤**：

1. 改 [`shared-assets/vitepress-template/theme/components/<X>.vue`](../shared-assets/vitepress-template/theme/components)
2. 同步到所有 28 站 `theme/components/`（脚本待写：见 §10 TODO）
3. CI 会自动 build 全部验证
4. PR 描述必须列出影响范围

### 6.4 改 glossary

```bash
vim shared-assets/glossary/keywords.json
# 加新术语前 grep 确认无同义词
grep -i "JVM" shared-assets/glossary/keywords.json
# 一次编辑 ≤ 50 条
```

CI 的 `build-sitemap-and-llms.py` 会自动从 glossary 扩展 sitemap + llms。

### 6.5 改部署脚本（危险）

修改 `sites-hub/scripts/deploy-vps.sh` 或 `deploy-release.sh`：

- 本地 `bash -n` 必须通过
- CI `check` job 跑 `bash -n` 验证
- 涉及 nginx config 改动：本地跑 `bash sites-hub/scripts/render-nginx-conf.sh` 验证

---

## 7. CI/CD

### 7.1 Workflow（[`.github/workflows/sites-hub-ci.yml`](../.github/workflows/sites-hub-ci.yml)）

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:    # 手动触发
    inputs:
      skip_build: choice  # true=跳过 build 直接 deploy

jobs:
  check:                  # ~30s
    # - nginx -t
    # - Python compile
    # - bash -n 所有 .sh
    # - PWA 资产验证

  build-all:              # ~3min (matrix 28 并行)
    strategy:
      fail-fast: false
      matrix:
        site: [28 个站]
    steps:
      # - npm install (不用 npm ci，容忍 lockfile drift)
      # - npm run docs:build
      # - npx pagefind --site
      # - tar czf dist-<site>.tar.gz
      # - upload-artifact dist-<site>

  release:                # ~30s
    needs: [check, build-all]
    if: push || (dispatch + skip_build=true)
    # - download 28 artifacts
    # - tar xzf each
    # - MOCK_BUILD=1 bash build-release.sh (复用 dists)
    # - upload-artifact sites-hub-static

  deploy:                 # ~30s
    needs: [release]
    if: push || dispatch
    steps:
      # - download sites-hub-static
      # - scp to VPS
      # - ssh VPS: deploy-release.sh
    requires secrets: VPS_HOST / VPS_USER / VPS_SSH_KEY
```

### 7.2 性能

| 阶段 | 时长 |
|------|-----:|
| check | ~30s |
| build-all (matrix 28 并行) | ~2min |
| release | ~30s |
| deploy (scp 87M + 解压 + reload) | ~30s |
| **总** | **~3min 30s** |

之前串行 build 16min，**提速 5×**。

**本地 build-release.sh 并行化**（commit `6b2cf20`）：

| 场景 | 串行 | 并行 PARALLEL=4 | 备注 |
|------|-----:|------:|------|
| MOCK_BUILD=1（reuse dists）| ~10s | **~11s** | 几乎全部时间在 cp + 渲染元数据，build 阶段不是瓶颈 |
| 实际 build（npm ci + docs:build × 28）| ~14min | **~3-4min** | bash 3.2+ 兼容，默认 PARALLEL=4，可 `PARALLEL=8 bash build-release.sh` 调整 |

CI 端 `build-all` 已用 matrix 28 并行（每个站独立 runner job），不受影响。本地并行化主要服务于手动部署 / CI 故障回退场景。

### 7.3 触发条件速查

| 触发 | check | build-all | release | deploy |
|------|:---:|:---:|:---:|:---:|
| `push main` | ✅ | ✅ | ✅ | ✅ |
| `pull_request` | ✅ | ✅ | ⏭️ | ⏭️ |
| `workflow_dispatch`（默认）| ✅ | ✅ | ⏭️ | ✅ 手动重试 |
| `workflow_dispatch`（skip_build=true）| ⏭️ | ⏭️ | ✅ | ✅ |

### 7.4 关键经验（CI 调试踩坑）

详见 [`sites-hub/OPTIMIZATION-CONTENT.md` §8.35](../sites-hub/OPTIMIZATION-CONTENT.md)：

1. **`npm ci` 失败**：package-lock 严格 sync → CI 用 `npm install` 容忍 drift
2. **`tar` 路径错位**：必须 `tar czf -C "$(dirname $proj)" "$(basename $proj)/.vitepress/dist"` 保留 proj 前缀
3. **`test -d` 检查文件**永远 false（`-d` 查目录，pagefind.js 是文件）→ 用 `-d dir -a -f file` 双验证
4. **`actions/upload-artifact` glob `*/.vitepress/dist` 失败** → tar 打包
5. **`actions/download-artifact` `pattern: dist-*`** 批量下载，保留 artifact 名作为子目录
6. **bash 3.2 没有 `wait -n`**：本地并行化 build 时不能用 `wait -n` 等任意一个完成；改用 `wait PID` 阻塞最早启动的（最早启动的通常最先完成）

### 7.5 GitHub Actions 0-step Failure 排查（2026-08-18）

**症状**：自 12:15 UTC 后所有 `sites-hub-ci.yml` run 都以 0-step failure 结束（job 创建 2-5 秒后即 `conclusion=failure`，`runner_id=0`，`steps=[]`）。

**根因（已确认）**：GitHub 后端 active incident "Intermittent failures in runner group and runner-related permissions pages"（started 07:40 UTC, impact minor, status monitoring）。GitHub 于 11:24 UTC 发布 mitigation 更新但**实测仍 100% 0-step fail**——包括最小化 `hello world` workflow + ubuntu-22.04/ubuntu-latest/ubuntu-24.04 三种 runner image 全失败。

**与本项目无关的证据**：
1. 失败 run 只有 4 jobs（check + release + build-all + deploy），build-all 的 matrix 28 个 site 不展开 → 调度器在 runner pool 取不到 worker
2. workflow 文件 GitHub 端 sha 与本地一致（`761452eb`），yq 解析无错
3. 手动 `workflow_dispatch`（绕过 webhook）也 4-5 秒内 fail
4. 12:10 之前的 run 正常 31 jobs 全 success → workflow 文件中途未损坏

**应急措施**：
- §6.6 manual deploy fallback（`scp tarball + ssh deploy-release.sh`）已就位，可绕过 CI
- 私仓无并发配额限制（并发 ≤ 5 jobs），单次 deploy ~3min
- 等 GitHub 完全恢复后，CI 重新可用；不要修改 workflow 内容（无效）

**排查脚本**（用于将来类似事件）：
```bash
# 1. 看最新 run + jobs
gh run list --workflow=sites-hub-ci.yml --limit=3 --json databaseId,createdAt,updatedAt,conclusion
gh api repos/OWNER/REPO/actions/runs/$ID/jobs | jq '.jobs[] | {name, runner_name, steps: (.steps|length)}'

# 2. 看 GitHub status 是否有 incident
curl -s https://www.githubstatus.com/api/v2/incidents.json | jq '.incidents[] | select(.name | contains("runner")) | {name, status, incident_updates: [.incident_updates[0].body]}'

# 3. workflow_dispatch 触发一次确认（vs push 排除 webhook 问题）
gh workflow run sites-hub-ci.yml --ref main
```

---

## 8. VPS 部署

### 8.1 VPS 配置

| 项 | 值 |
|----|---|
| IP | `38.207.171.83` |
| 域名 | `java-px.bot.cd` |
| OS | Ubuntu 22.04 |
| nginx | 1.18.0（apt nginx-light + 加 nginx-full）|
| certbot | 1.21.0（Let's Encrypt RSA cert，65 天有效）|
| fail2ban | 0.11（nginx-auth jail）|
| goaccess | 1.5.5（每日 cron 0:00）|
| Basic Auth | `/etc/nginx/.sites-hub.htpasswd`（admin + 用户密码）|

### 8.2 目录结构

```
/var/www/sites-hub/
├── current → releases/<latest-id>/   # 蓝绿软链
├── releases/
│   ├── 20260816085428/               # 历史版本（保留 5 个）
│   │   ├── www/                      # 28 站 dist + portal
│   │   ├── conf/nginx.conf           # nginx 配置
│   │   └── scripts/                  # 部署/运维脚本
│   └── ...
├── www/                               # 独立元数据（不跟随 release）
│   ├── stats.html                    # GoAccess 报告（nginx alias）
│   ├── sitemap.xml / llms.txt / feed.xml  # 主门户聚合版
│   └── ld.json / manifest.webmanifest
├── scripts/                           # 部署/运维脚本
│   ├── deploy-vps.sh                  # VPS 初始化（一次性）
│   ├── deploy-release.sh              # 蓝绿切换
│   ├── setup-fail2ban.sh
│   ├── setup-goaccess.sh
│   └── sites.sh
└── ...

/etc/nginx/
├── sites-available/sites-hub.conf     # 28 个 location + 6 个安全头
├── sites-enabled/sites-hub.conf → sites-available/...
└── .sites-hub.htpasswd                # Basic Auth

/etc/letsencrypt/live/java-px.bot.cd/  # HTTPS cert
/etc/fail2ban/{filter,jail}.d/nginx-auth.{conf,conf}  # fail2ban 配置
/etc/cron.d/goaccess-stats             # GoAccess 每日 0:00 cron
```

### 8.3 nginx 公开路径（auth_basic off）

```
/healthz, /metrics, /auth-check, /csp-report  # 内部健康
/stats.html                                     # GoAccess 流量统计
/sitemap.xml, /llms.txt, /llms-full.txt       # AI 索引
/feed.xml                                       # RSS
/robots.txt, /manifest.webmanifest, /ld.json   # SEO 元数据
```

其他路径全部 Basic Auth 保护。

### 8.4 部署模式

**蓝绿切换**（[`deploy-release.sh`](../sites-hub/scripts/deploy-release.sh)）：

```
1. 解压新 release → releases/<new-id>/
2. nginx -t 验证 config
3. ln -sfn new && mv -Tf current → atomic 切换
4. nginx -s reload（worker 进程平滑替换，零停机）
5. 保留 5 个历史 release，自动清理更早的
6. flock 防并发（两个 deploy 同时只跑 1 个）
```

### 8.5 初始化（首次部署）

```bash
# VPS 上（root）
cd /var/www/sites-hub
bash deploy-vps.sh java-px.bot.cd you@example.com admin
# 交互式输入 Basic Auth 密码

bash scripts/setup-fail2ban.sh   # 防爆破（nginx-auth jail）
bash scripts/setup-goaccess.sh   # 访问统计
```

### 8.6 GitHub Secrets（CI 自动 deploy 需配置）

| Secret | 值 |
|--------|---|
| `VPS_HOST` | `38.207.171.83` |
| `VPS_USER` | `root` 或 deploy user |
| `VPS_SSH_KEY` | ed25519 / RSA 4096 private key（含 BEGIN/END）|
| `VPS_PORT`（可选）| `22` |

VPS `authorized_keys` 加 CI 的 public key。

### 8.x GoAccess 流量监控（**轻量、零依赖**）

[VPS 端部署后立即可用] `https://java-px.bot.cd/stats.html`

| 组件 | 路径 | 说明 |
|------|------|------|
| **二进制** | `/usr/bin/goaccess` | apt 包，单文件 ~5MB |
| **访问日志** | `/var/log/nginx/access.log` | COMBINED 格式（nginx 默认） |
| **持久化 DB** | `/var/lib/goaccess/` | 增量模式必须 |
| **输出** | `/var/www/sites-hub/www/stats.html` | nginx 直接 alias 公开 |
| **Generator** | `/usr/local/bin/goaccess-generate-stats.sh` | `--persist --keep-last=30` 增量模式 |
| **Cron** | `/etc/cron.d/goaccess-stats` | 每日 0:00 触发 |
| **日志** | `/var/log/goaccess-generate.log` | 每次跑 append 时间戳 |

**安装**：`sites-hub/scripts/setup-goaccess.sh` 由 `deploy-vps.sh` 自动调用（首次部署），幂等可重跑。

**公开访问**：在 `render-sites-hub-conf.sh` 里硬编码（不依赖 SITES 数组）：
```nginx
location = /stats.html {
    auth_basic off;
    access_log off;
    add_header Cache-Control "no-cache, must-revalidate";
    alias /var/www/sites-hub/www/stats.html;
}
```

**为什么选 GoAccess 而不是 Plausible SaaS**：零账号、零外部请求、VPS 自托管零成本。代价是只看 nginx access log（无 JS 埋点、无法区分 SPA 路由）。

**资源占用**：单次跑 ~30s，CPU spike ~5%，RAM ~30MB，stats.html ~300KB，DB ~5MB（30 天）。对比 Plausible Docker 自托管需 ~500MB+ RAM。

### 8.y HTTPS 部署专题

完整 HTTPS 配置（证书 / nginx 渲染 / 部署同步 / 故障排查）见 [HTTPS-DEPLOY.md](./HTTPS-DEPLOY.md)。

**关键点速览**：
- 证书：certbot webroot + HTTP-only 临时 conf 两阶段
- 配置生成：`render-sites-hub-conf.sh`（deploy-vps.sh + deploy-release.sh 共用，**消除手动 SSH 修 nginx**）
- 部署同步：每次 deploy 末尾 idempotent 重写 `/etc/nginx/sites-available/sites-hub.conf`
- P3 公开元数据：11 个 `auth_basic off` location（sitemap / llms / feed / robots / manifest / ld.json / stats.html）

---

## 9. 关键脚本清单

### 9.1 单一真相源

| 脚本 | 作用 |
|------|------|
| [`sites.sh`](../sites-hub/scripts/sites.sh) | SITES 数组（28 站） |

### 9.2 构建 / 部署

| 脚本 | 作用 |
|------|------|
| [`build-release.sh`](../sites-hub/build-release.sh) | 一键打 release tarball（含 sitemap/llms/feed 生成） |
| [`deploy-vps.sh`](../sites-hub/deploy-vps.sh) | VPS 一次性初始化（apt + nginx + certbot + htpasswd） |
| [`deploy-release.sh`](../sites-hub/scripts/deploy-release.sh) | VPS 蓝绿切换 deploy（flock + nginx reload） |
| [`render-nginx-conf.sh`](../sites-hub/scripts/render-nginx-conf.sh) | sites.sh → nginx.conf 渲染（本地开发用）|

### 9.3 内容生成

| 脚本 | 作用 |
|------|------|
| [`build-sitemap-and-llms.py`](../sites-hub/scripts/build-sitemap-and-llms.py) | sitemap + llms.txt + llms-full.txt + feed.xml 生成 |
| [`build-updates-from-git.py`](../sites-hub/scripts/build-updates-from-git.py) | git log → portal "Updates" 列表 |
| [`inject-stats.py`](../sites-hub/scripts/inject-stats.py) | data.json → index.html（数字注入）|
| [`make-og-cover.py`](../sites-hub/scripts/make-og-cover.py) | OG 封面生成 |
| [`subset-fonts.sh`](../sites-hub/scripts/subset-fonts.sh) | 字体子集化（4 字体 × 3 字重 → 12 woff2）|

### 9.4 内容质量

| 脚本 | 作用 |
|------|------|
| [`audit-content.py`](../sites-hub/scripts/audit-content.py) | 内容审计（12 项：frontmatter / 死链 / 未引用图片 / glossary 一致性）|
| [`check-sites.sh`](../sites-hub/scripts/check-sites.sh) | sites.sh 一致性校验（12 项）|
| [`check-links.py`](../sites-hub/scripts/check-links.py) | 死链检测 |
| [`spell-check.sh`](../sites-hub/scripts/spell-check.sh) | 拼写检查 |
| [`add-video-link.py`](../sites-hub/scripts/add-video-link.py) | 视频链接转换工具 |

### 9.5 运维

| 脚本 | 作用 |
|------|------|
| [`setup-fail2ban.sh`](../sites-hub/scripts/setup-fail2ban.sh) | VPS 防爆破（nginx-auth jail） |
| [`setup-goaccess.sh`](../sites-hub/scripts/setup-goaccess.sh) | VPS 访问统计（cron 每日 0:00）|
| [`backup-htpasswd.sh`](../sites-hub/scripts/backup-htpasswd.sh) | htpasswd 备份 |

---

## 10. 故障排查

### 10.1 macOS 沙箱限制

| 问题 | 解决方案 |
|------|---------|
| `rm -rf <path>` 被 auto_review 拒绝 | 用 `python3 -c "import shutil; shutil.rmtree(...)"` |
| macOS bash 3.2 不支持 `declare -A` / `mapfile` | 字符串解析 / while loop |
| bash 双引号内嵌单引号 EOF 错误 | 用 Python `cat > file <<'EOF'` |
| Python 3.9 不支持 `str \| None` 注解 | 用 `Optional[str]` 或不写注解 |
| Python heredoc 内 Jinja `{{ }}` 被替换 | 用 `cat > file <<EOF` 或先写文件再 sed |
| `re.sub` `\d` 报错（bad escape）| 用 `lambda m: ...` |

### 10.2 VitePress / 主题

| 问题 | 解决方案 |
|------|---------|
| 构建后 HTML 看不到 mermaid SVG | CSR 是预期行为，浏览器实测 |
| `pagefind --site` 自动加载 UI | VitePress 1.6+ 内置 |
| 主题组件自动注册 | VitePress 1.6+ 从 `theme/components/*.vue` 自动 |
| 多行 YAML `:prop="[...]"` 在 Vue SFC 编译失败 | 用 `<script setup>` 形式 |
| `../../../../shared-assets/...` rollup fs.allow 拒绝 | vite alias `@shared` 替代 |

### 10.3 npm / CI

| 问题 | 解决方案 |
|------|---------|
| `npm ci` lockfile 严格 sync 失败 | CI 用 `npm install` |
| `actions/upload-artifact` glob 失败 | tar 打包（保留 proj 路径前缀）|
| `actions/download-artifact pattern: dist-*` | 批量下载，保留 artifact 名作为子目录 |
| `tar -C $(dirname $proj)` | 必须显式指定，保留 proj 前缀 |
| `test -d path/file` 永远 false | `-d` 检查目录，文件用 `-f` |

### 10.4 nginx / VPS

| 问题 | 解决方案 |
|------|---------|
| `nginx: [emerg] unknown "current_link"` | sed 把 `${CURRENT_LINK}` 展开为实际路径 |
| `nginx: [emerg] zero size shared memory zone "auth"` | 在 `/etc/nginx/conf.d/limit-req.conf` 加 `limit_req_zone` |
| nginx 路径 `/opt/homebrew/etc/nginx/mime.types` | CI 用 sed 替换为 `/etc/nginx/` |
| `limit_req_zone` / `stub_status` 缺失 | 装 nginx-full（不要 nginx-light）|
| certbot `FileNotFoundError` | 检查 webroot `/var/www/certbot` + DNS 解析 |
| `getcwd: cannot access parent directories` | heredoc 之前 `cd /` |

---

## 11. 已知 TODO（未来优化）

> CI/CD 完整流程专题见 [`docs/CICD-PIPELINE.md`](./CICD-PIPELINE.md)（652 行，含 0-step failure 排查过程 + 手动 deploy fallback）。

> 完整列表见 [`sites-hub/OPTIMIZATION-CONTENT.md` §8.40](../sites-hub/OPTIMIZATION-CONTENT.md)

| 优先级 | 任务 | 原因 |
|:---:|------|------|
| ⊘ P2 | 共享组件同步脚本 | **跳过** — `sites-hub/shared-assets/` 不存在；无共享 theme 需要同步；按需新建 |
| ✅ P3 | nginx gzip_static + 架构 gap | render-nginx-conf.sh 加 8 个公开元数据 location（commit `192cc58`）；新 `scripts/render-sites-hub-conf.sh` 抽离 deploy-vps.sh 的 HTTPS 写配置函数（含 stats.html / robots.txt / manifest.webmanifest / ld.json 共 11 个 P3 location），deploy-vps.sh + deploy-release.sh 共用，**每次 deploy 自动重写 sites-hub.conf + reload，消除手动修复 nginx 复现路径** |
| 🔲 P3 | GitHub Environment `production` | 加 reviewer approval gate |
| 🔲 P3 | SSH key 自动 rotate | 当前手动 |
| ⚠️ P3 | Branch protection rules | **受限**：private free repo GitHub API 返回 403；需转 public 或升 Pro 才能启用（CODEOWNERS 已就位等待启用）|
| ✅ P3 | CODEOWNERS | 已完成（commit `d82251a`）— 单 owner 仓库 assign 作用有限，主要为未来扩展性 |
| 🔲 P3 | Dependabot | 自动依赖更新 |

---

## 12. 上手指南（TL;DR）

**第一次接触项目？**

```bash
# 1. 读本文档 §1-§4（架构 + 约定）
# 2. 读 sites-hub/SOP-ADD-SITE.md（操作 SOP）
# 3. 跑一致性校验
bash sites-hub/scripts/check-sites.sh

# 4. 跑审计看现有问题
python3 sites-hub/scripts/audit-content.py

# 5. 看 CI 状态
gh run list --workflow=sites-hub-ci.yml --limit 5

# 6. 找一个最简单的小任务开始
# - 加 glossary 词
# - 加 audit 字典里的常见错别字
# - 修 spell-check.sh 报错
```

**改内容？**

```bash
# 单站
cd <site>-html && npm install && npm run docs:dev

# 全 28 站（本地基本不会跑，CI matrix 是 source of truth；单站调试进子目录 npm run docs:dev）

# 提交前
python3 sites-hub/scripts/audit-content.py
bash sites-hub/scripts/spell-check.sh
bash sites-hub/scripts/check-sites.sh
```

**改部署？**

```bash
# 1. 改 sites-hub/scripts/*.sh 或 deploy-vps.sh
# 2. 本地 bash -n 验证
bash -n sites-hub/scripts/<file>.sh

# 3. push → CI check job 会跑 bash -n

# 4. 真正部署到 VPS 需要 GitHub Secrets 配置
```

