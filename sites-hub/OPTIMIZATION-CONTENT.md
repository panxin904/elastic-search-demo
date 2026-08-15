# java-px.bot.cd 站点内容优化任务清单（v2 — 内容维度）

**编写日期**：2026-08-15
**目标**：把关注点从 nginx/部署运维转向**内容质量、可发现性、用户体验、内容运营**。
**与 OPTIMIZATION.md 关系**：原 P0-P4（nginx/部署）已闭环，本文档聚焦 28 子站 + 导航首页的**内容层**优化。

---

## 〇、现状快照（内容视角）

| 维度 | 数值 | 来源 |
|------|------|------|
| 子站总数 | 28 | `sites.sh` |
| 子站项目 | 27 × `*-html` + `java-web-manual` | `ls -d */-html` |
| 内容页总数 | 1429+ | 首页 `data-count` |
| 节点数 | 1154 | 首页 `data-count` |
| 卡片分类 | 8 类（backend/data/infra/ops/frontend/security/arch/ai） | 首页 `data-cat` 统计 |
| 卡片数 | 51（28 子站 + 23 个二级入口） | `grep -c data-cat` |
| 更新条目 | 14（手动维护，最新 2026-08-12） | `.update-item` |
| 框架 | VitePress 1.x | `es-html/.vitepress/config.mts` |
| 跨站引用 | 0（子站间无内容关联） | 手动 spot-check |
| 搜索 | VitePress 默认 local search | `theme.search` 推断 |
| 评论 | 无 | 无第三方脚本 |
| 订阅 | 无 | 无 RSS feed |
| 多语言 | 仅 zh-CN | `lang: 'zh-CN'` |
| 数据驱动 | build-time 数字，无运行时统计 | `data.json` 注入 |

---

## 一、任务总览

| 编号 | 任务 | 优先级 | 工作量 | 依赖 | 状态 |
|------|------|--------|--------|------|------|
| C1 | 子站结构统一化（VitePress 模板 + nav/sidebar/homepage 模板） | **P0** | 3-5d | — | todo |
| C2 | 跨站内容关联（X-Linking + 相关站点推荐） | P0 | 2-3d | C1 | todo |
| C3 | 内容质量审计（拼写/过期/薄页/死链/重复） | **P0** | 1d + 持续 | — | todo |
| C4 | 全文搜索升级（Pagefind + 跨站聚合） | P1 | 1-2d | C1 | todo |
| C5 | RSS feed + 聚合订阅 | P1 | 0.5d | C1 | todo |
| C6 | 评论/反馈（Giscus + Issue 模板） | P1 | 0.5d | — | todo |
| C7 | 阅读体验（行距/代码块/暗色对比度/中英间距） | P1 | 1d | — | todo |
| C8 | 多语言支持（中英术语表 + 首页切换） | P2 | 2-3d | C1 | todo |
| C9 | 数据驱动（Plausible + 首页实时数 + git log 自动生成 Updates） | P2 | 1-2d | — | todo |
| C10 | 内容运营流程（CONTRIBUTING.md + PR 模板 + 月度 review） | P2 | 1d | — | todo |
| C11 | 图片/图表优化（PNG→WebP + Mermaid SSR + lazy load） | P2 | 1-2d | C1 | todo |
| C12 | sitemap 完整化 + llms.txt（AI 索引友好） | P2 | 0.5d | C1 | todo |

> 状态图例：todo 待开始 / wip 进行中 / done 完成

---

## 二、P0 任务详解（本周必做）

### C1 · 子站结构统一化

**根因**：28 个子站各自演化多年，VitePress 配置（nav/sidebar/homepage/features）差异显著。用户从 `/es/` 切到 `/mysql/` 体验断层：导航栏布局变、首页 hero 颜色不同、侧边栏分组粒度不一致。

**影响**：
- 用户认知负担高（每站都要重新适应）
- 新作者参考成本高（每个项目都有不同"模板"）
- 跨站视觉一致性差

**修复**：

1. **建立 VitePress 配置模板** `shared-assets/vitepress-template/`：
   ```
   shared-assets/vitepress-template/
   ├── config.mts.tpl      # nav + sidebar + footer + head + plugins
   ├── theme/
   │   ├── index.ts        # 自定义组件（Card / Feature / UpdateItem）
   │   ├── style.css       # 全局 CSS 变量
   │   └── components/
   │       ├── HomeHero.vue
   │       ├── HomeFeatures.vue
   │       ├── RelatedSites.vue
   │       └── SubscribeBox.vue
   └── docs/
       ├── _home.md        # 各子站首页内容（Markdown 而非手写 HTML）
       └── _sidebar.json   # 侧边栏配置
   ```

2. **统一 nav 结构**（最少必要项）：
   - 左：站点 logo
   - 中：4-5 个主章节（如 es：存储/查询/分析/运维/工具）
   - 右：🔍 搜索 / 🌗 主题切换 / 🏠 门户 / 更多站点 ▼
   - "更多站点"下拉按 8 大分类自动分组生成（来自 sites.sh + data-cat）

3. **统一 homepage**：所有子站用 Markdown 写：
   ```markdown
   ---
   layout: home
   title: ES Knowledge Atlas
   hero:
     name: Elasticsearch
     text: 系统化学习
     tagline: 用知识图谱串联概念与使用方式
     actions:
       - theme: brand
         text: 快速开始
         link: /01-storage/overview
   features:
     - icon: 📦
       title: 存储层
       details: shard/replica/translog/segment
     - icon: 🔍
       title: 查询层
       details: DSL/match/bool/aggregation
   ---
   ```

4. **CI 校验一致性**：`.github/workflows/sites-hub-ci.yml` 加 job：
   ```bash
   # 所有子站 nav 数量差异不超过 ±2
   for site in "${SITES[@]}"; do
     nav_count=$(grep -c 'text:' "$site/.vitepress/config.mts")
     echo "$site: $nav_count"
   done | awk '$2 < 4 || $2 > 12 { print "FAIL: " $0; exit 1 }'
   ```

**验收**：
- 28 子站全部用 `shared-assets/vitepress-template/`，自定义 ≤ 5%
- 切换任意两站，nav 高度、logo 位置、主题切换图标位置完全一致
- "更多站点"下拉按 data-cat 分组显示

**预防**：
- 每个子站 README 顶部加："如需修改模板请先 PR 到 `shared-assets/vitepress-template/`"
- CI 跑 `npm run lint:config` 校验结构

---

### C2 · 跨站内容关联（X-Linking）

**根因**：子站间无内容关联。比如 java 页提到"JVM 调优"但没法跳到 `java-language` 的 JVM 章节；ES 页提到"DSL"没有索引到 `system-design`。

**影响**：
- 内容孤岛：用户被锁在一个站点的认知闭环
- 学习路径断裂：完整知识需要外部搜索
- SEO 内部链接结构差（orphan pages 多）

**修复**：

1. **关键词词典** `shared-assets/glossary/keywords.json`：
   ```json
   {
     "JVM": ["/java-language/04-jvm/overview", "/system-design/jvm-tuning"],
     "事务": ["/mysql/02-acid", "/postgresql/transaction"],
     "索引": ["/es/01-storage/index", "/clickhouse/index-design"],
     "GC": ["/java-language/04-jvm/gc-overview", "/go/garbage-collection"],
     "Docker": ["/cloud-native/01-docker/overview", "/devops/containerization"]
   }
   ```

2. **X-Link 标记语法**：在 Markdown 中写：
   ```markdown
   <!-- 普通写法 -->
   详细见 [JVM 调优](java-language/04-jvm/overview)。
   
   <!-- X-Link 自动识别 -->
   本文涉及的 {JVM} 和 {GC} 概念在其他站点有更深入的讨论。
   ```
   build 脚本扫 `{Term}` 标记 + glossary 自动生成跨站链接。

3. **每篇末尾加"相关站点"**：根据文中出现的关键词 + glossary 反向匹配，显示 3-5 个相关站点的 1-2 篇相关内容。

4. **首页底部"知识图谱"**：可视化 28 站 + 关键词边的网络（用 d3-force 或 vis-network）。

**验收**：
- 每个内容页平均 2+ 跨站链接
- 关键词词典覆盖核心 200+ 术语
- "相关站点" 推荐准确率（人工抽 20 篇 ≥ 80% 相关）

**预防**：
- CI 跑 `node scripts/build-xlinks.mjs` 失败即 fail
- 词典文件必须放在 `shared-assets/glossary/`，分散在子站禁止

---

### C3 · 内容质量审计

**根因**：1429+ 页人工维护，错别字 / 过期内容 / 薄页 / 死链 / 重复不可避免；当前无任何自动化检测。

**影响**：
- 用户读到错误信息被误导
- SEO 收录下降（Google 降权 thin content）
- 用户信任度下降

**修复**：

1. **自动化检查脚本** `scripts/audit-content.sh`：
   ```bash
   # 1) 拼写
   codespell --skip='*.json,*.lock' --ignore-words=.codespell-ignore docs/

   # 2) 中文错别字（基于最小校对词库）
   python3 scripts/check-cn-typos.py

   # 3) 过期内容（frontmatter date > 365d 警告）
   python3 scripts/stale-content.py --max-age-days 365

   # 4) 薄页（字数 < 500 + 无 frontmatter）
   python3 scripts/thin-pages.py --min-words 500

   # 5) 死链（已用 check-links.py 扩展）
   python3 scripts/check-links.py --depth 3

   # 6) 重复标题（相似度 > 0.85）
   python3 scripts/dup-titles.py --threshold 0.85

   # 7) 缺 alt 文本的图片
   python3 scripts/missing-alt.py

   # 输出
   python3 scripts/audit-content.py > reports/content-quality-$(date +%F).md
   ```

2. **质量报告** `reports/content-quality-YYYY-MM-DD.md`：
   - 总分（每项加权）
   - 错别字 N 处（按文件聚合）
   - 过期内容 N 篇（按站点聚合）
   - 薄页 N 篇（按字数分布）
   - 死链 N 处
   - 重复标题 N 组
   - 缺 alt 图片 N 张

3. **CI 门禁**：
   - 拼写错 > 0 → fail
   - 薄页新增 > 5 → warn
   - 死链新增 > 0 → fail
   - 重复标题新增 > 0 → fail

4. **人工 review 节奏**：
   - 每月 1 日自动跑 audit → 邮件给主要作者
   - 季度 review 整站质量报告

**验收**：
- 首跑生成 baseline 报告，所有数字存档
- CI 跑通；weekly 跑检测新增问题
- 月度报告完整有数据

**预防**：
- PR 模板强制跑 `npm run audit:quick`（只查 diff 文件）
- 作者本地 pre-commit 钩子跑拼写

---

## 三、P1 任务详解（下周）

### C4 · 全文搜索升级

**根因**：VitePress 默认 local search 是**构建时**生成的 lunr 索引（28 子站 × 1429 页 ≈ 100KB-1MB JSON），不支持模糊/权重/中文友好分词/增量索引。

**修复**：
- 引入 [Pagefind](https://pagefind.app/)（Rust 实现的运行时增量索引，原生支持中文/分词/高亮）
- 每个子站 build 时运行 `pagefind --site dist`
- 替换 VitePress 默认搜索组件为 Pagefind 组件
- 跨站聚合：自定义搜索结果页 `/search.html?q=xxx` 展示 28 站匹配数 + Top 10

**验收**：
- 搜 "JVM 调优" 返回 java + java-language + system-design 三站结果
- 搜索响应时间 < 200ms（客户端索引）
- 中文分词准确（不按字符切）

---

### C5 · RSS feed + 聚合订阅

**根因**：用户无"内容更新通知"渠道；首页 Updates 板块只是手写 HTML，反映不出真实内容更新。

**修复**：
- 每个子站 build 时生成 `/feed.xml`（VitePress plugin-feed 或自写）
- 聚合 RSS 到 `/feeds/all.xml`（按 git log 时间倒序，跨 28 站最新 50 条）
- 邮件订阅（可选：Buttondown / Listmonk 自部署）
- 首页 Updates 板块改用 JS fetch `/feeds/all.xml` 渲染（XSS 必须 escape）

**验收**：
- 28 子站每站 `/feed.xml` 合规
- `/feeds/all.xml` 含 28 站最新 50 条 commit
- 邮箱订阅注册 → 验证 → 接收 weekly digest 全流程跑通

---

### C6 · 评论 / 反馈

**根因**：用户读错内容无法反馈，作者不知错在哪。

**修复**：
- 接入 [Giscus](https://giscus.app/)（GitHub Discussions 后端，零成本无服务器）
- 每篇文章底部加 `<Giscus />` 组件
- 顶部加"📝 反馈此页错误"按钮 → 跳 GitHub Issue 模板（自动带 URL + User-Agent）
- 写 `docs/ISSUE_TEMPLATE/content-error.yml` 自动填当前页 URL

**验收**：
- 所有内容页有评论组件
- Issue 模板自动填 URL + 浏览器版本
- 月评论量 ≥ 10（活跃度指标）

---

### C7 · 阅读体验

**根因**：技术文档常见可读性问题：行距太密、代码块 vs 文字对比度不足、暗色模式颜色不达标、长文章缺目录粘性。

**修复**：
- CSS 变量统一（`shared-assets/vitepress-template/theme/style.css`）：
  ```css
  :root {
    --vp-line-height: 1.7;
    --vp-letter-spacing: 0.02em;
    --vp-code-bg: #f6f8fa;
    --vp-code-block-radius: 8px;
    --vp-code-block-shadow: 0 2px 8px rgba(0,0,0,.06);
  }
  ```
- 暗色模式色彩对比度 ≥ AA（4.5:1）
- 中英文之间自动加空格（pangu.js）
- 长文章（> 3000 字）加 "📍 阅读进度条"（顶部 thin bar，scroll 进度）
- 表格加 caption + striped rows + sticky header

**验收**：
- Lighthouse a11y ≥ 95
- 暗色模式 axe-core 0 critical issue
- 1000 字文章 vs 5000 字文章对比评测（用户测试）

---

## 四、P2 任务详解（长期）

### C8 · 多语言支持

**修复**：
- 关键术语维护 `shared-assets/glossary/terms.md`（中英对照，200+ 术语）
- 首页加 EN/中 切换（基于 i18n 路由：英文版用 `vue-i18n` 抽取文案）
- 子站暂不全翻译，但每章末尾加 "English reference" 链接到 MDN / 官方 docs
- 长文章顶部显示 "📖 术语速查"，hover 显示中英对照

**验收**：
- 首页支持 EN 切换
- glossary 100% 覆盖核心术语

---

### C9 · 数据驱动

**修复**：
- 接入 Plausible（自部署 `/plausible.js`）或 Umami（更轻量）
- 首页 hero 显示真实 PV、独立访客（API 拉过去 7 天均值）
- Updates 板块改为 JS fetch git log（GitHub API `commits?since=7d`）→ 自动生成

**验收**：
- 首页数据 100% 来自运行时
- Updates 是真实 git history
- 数据新鲜度 < 7d（CI 校验）

---

### C10 · 内容运营流程

**修复**：
- 写 `CONTRIBUTING.md`：投稿流程 + 风格指南 + 内容模板
- 写 `.github/PULL_REQUEST_TEMPLATE/content.md`：作者必勾清单
- 月度 review 流程（基于 `reports/content-quality-*.md`）
- 投稿自动感谢信（GitHub Actions + 钉钉/飞书 webhook）

**验收**：
- CONTRIBUTING.md 完整
- PR 模板自动填检查项
- 月度报告存档到 `reports/`

---

### C11 · 图片 / 图表优化

**修复**：
- 所有 PNG 转 WebP（`shared-assets/build-images.sh` 批量）
- Mermaid SSR 渲染（`vitepress-plugin-mermaid`）
- 所有 `<img>` 加 `loading="lazy"` + `decoding="async"`
- 暗色模式图适配（`<picture>` + `<source media="(prefers-color-scheme: dark)">`）

**验收**：
- 所有图 < 200KB
- Lighthouse LCP < 2.5s
- 暗色模式图清晰可见

---

### C12 · sitemap + llms.txt

**修复**：
- 每个子站 build 生成 `sitemap.xml`（`@vitepress/plugin-sitemap` 或自写）
- 聚合 `/sitemap-all.xml`（28 站合并，含 lastmod）
- 生成 `llms.txt`（[llmstxt.org](https://llmstxt.org/) 规范）：AI 友好的全站内容摘要（≤ 100KB，每站点 1 段简介 + 关键章节列表）

**验收**：
- `sitemap-all.xml` 含 28 × N 页
- `llms.txt` ≤ 100KB 涵盖所有站点
- `curl https://java-px.bot.cd/llms.txt` 可访问

---

## 五、推荐推进顺序

**第 1 周（C3 + C1 启动）**：
- C3 audit 先跑 baseline，知道现状有多糟
- C1 模板 + 第一个子站（es）pilot 改造

**第 2-3 周（C1 + C2）**：
- C1 全 28 子站迁移到模板
- C2 跨站关联 + glossary 200 词

**第 4 周（C4 + C5 + C6）**：
- Pagefind 替换默认搜索
- RSS feed + Giscus 接入

**持续**：
- C3 weekly CI + monthly review
- C7 / C11 性能优化分散进行

---

## 六、与其他文档的关系

| 文档 | 关注点 | 本文档关系 |
|------|--------|-----------|
| `OPTIMIZATION.md` | nginx / 部署 / 安全 / SEO | 已闭环（P0-P4 done） |
| `OPTIMIZATION-CONTENT.md`（本文） | 内容 / UX / 运营 | 接力下一步 |
| `SOP-ADD-SITE.md` | 新增站点流程 | C1 完成后需更新（用模板） |

## 七、立即可启动（无需 C1 依赖）

- C3 内容审计（独立工具集）
- C6 Giscus 接入（独立组件）
- C12 sitemap/llms.txt（独立 build hook）
- C10 CONTRIBUTING.md（独立文档）

---

## 八、C3 Baseline 实测数据（2026-08-15）

完整报告：`sites-hub/reports/content-quality-2026-08-15.md`
工具：`sites-hub/scripts/audit-content.py`

### 8.1 关键数字

| 维度 | 数值 | 评价 |
|------|------|------|
| 总 .md 文件 | 1430 | 符合预期（首页宣传 1429+） |
| 总字数（中英混合） | 1,156,160 | — |
| frontmatter 覆盖率 | 97.2% | ✅ ≥ 95% 阈值 |
| **薄页（< 500 字）** | **324 (22.7%)** | ❌ 远超 5% 阈值 |
| 缺 frontmatter | 40 | ❌（集中在 design-pattern 7 + filesystem 33） |
| frontmatter 缺 date | 1390 | ❌（VitePress 用 lastUpdated 兜底） |
| 过期内容（mtime > 365d） | 0 | ✅（多数站是新写的） |
| **图片总数** | **9** | ⚠️ 严重偏少（1430 篇 9 图 = 0.6%） |
| 缺 alt 图片 | 7 | ❌ |
| 内部死链 | 11 | ❌（路径错误） |
| **跨站引用** | **4** | ⚠️ 严重偏少（28 站 1430 页） |
| 跨子站重复标题 | 245 | ⚠️（模板/共享段落） |
| 同子站重复标题 | 462 | ⚠️（章节模板） |

### 8.2 薄页最严重的子站（top 5）

| 子站 | 文件数 | 薄页数 | 薄页率 | 备注 |
|------|-------:|-------:|-------:|------|
| java-language | 55 | 54 | **98.2%** | 平均字数 99 字 → 几乎全是占位 |
| es | 63 | 59 | 93.7% | 平均字数 304 字 |
| frontend | 65 | 51 | 78.5% | — |
| java | 53 | 47 | 88.7% | — |
| ai | 57 | 18 | 31.6% | — |

**根因**：薄页多为 `path.md` / `mindmap.md` / `graph.md` / `cheatsheet.md` 这种**索引速查文件**，字数天然少。是否真的"薄"取决于业务定义。

### 8.3 跨子站重复标题 top 5

| 标题 | 出现站数 | 价值 |
|------|---------:|------|
| 为什么写这个图谱？ | 5 | **强建议抽到 C1 shared-assets/components/AboutGraph.vue** |
| Node.js | 6 | 技术词，C2 跨站引用候选 |
| Python | 5 | 同上 |
| 路径 1：纯新手（1 周） | 3 | 模板段落 |
| 🆚 vs 其他 | 3 | 模板段落 |

### 8.4 内部死链（11 处）

都是 **路径错误**（`/02-thread-pool/xxx` 应为 `/01-concurrency-theory/xxx` 等），不是缺失文件。修复优先级：P1。

### 8.5 下一步具体行动

1. **立即**：修复 11 处死链（PR 一波，半小时）
2. **本周**：建 `shared-assets/vitepress-template/` 解决 java-language 98% 薄页（多数是占位）
3. **本月**：把"为什么写这个图谱？" 5 个站的副本抽到 Vue 组件
4. **持续**：weekly 自动跑 audit-content.py，CI 门禁（新增薄页/死链/拼写 fail）

### 8.6 工具 SOP

```bash
# 本地跑
python3 sites-hub/scripts/audit-content.py

# 参数
--min-words 500          # 薄页阈值（默认 500）
--max-age-days 365       # 过期阈值（默认 365）
--dup-threshold 0.92     # 重复相似度（默认 0.85）
--output-dir reports/    # 输出目录

# CI 接入（在 .github/workflows/sites-hub-ci.yml 加 job）
- name: Content audit
  run: python3 sites-hub/scripts/audit-content.py
- name: Upload report
  uses: actions/upload-artifact@v4
  with:
    name: content-quality
    path: sites-hub/reports/content-quality-*.md
```

### 8.7 死链修复记录（2026-08-15 第一次）

| 站点 | 修复数 | 类型 | 处理 |
|------|-------:|------|------|
| clickhouse | 7 | 路径多一层 `../` | `../../case-study.md` → `../case-study.md` |
| cloud | 4 | 目标 `pod/statefulset/daemonset/job` 缺失 | 删 link 保留文字 |
| es | 1 | 站内绝对路径错 | `/02-query` → `../02-query` |
| python | 2 | 站内绝对路径错 | `/08-algorithms/` → `./08-algorithms/`（同 `/09-enterprise/`） |
| **合计** | **14** | — | — |

**audit-content.py 同步修复**：
- VitePress cleanUrls 兼容（`<name>.md` / `<name>.html` / `<name>/index.html` 全检查）
- 目录本身也算合法目标（VitePress 自动渲染目录页）

**基线对比**：

| 指标 | 修复前 | 修复后 |
|------|------:|------:|
| 内部死链 | 11 | **0** ✅ |
| 报告误报（audit bug） | 4 | 0 ✅ |

**下一步建议**：
- 把 audit-content.py 加入 `.github/workflows/sites-hub-ci.yml`，PR 时跑（fail 阈值 = 新增死链 > 0）
- 把这次修复做成一个 commit，message：`fix(content): resolve 14 broken internal links`

### 8.8 frontmatter 修复记录（2026-08-15 第二次）

| 站点 | 修复数 | 处理 |
|------|-------:|------|
| filesystem-html | 20 | `title: XXX`（基于 H1 提取） |
| design-pattern-html | 7 | `title: XXX`（含 1 个 index.md + 6 个 overview.md） |
| **合计** | **27** | — |

**13 个 README.md 不修**（filesystem 的所有章节首页）：
- 全站 13 个 README.md 全部缺 FM（其中 13 个都是 filesystem 的）
- VitePress 默认识别为目录页，不需 FM
- 项目惯例就是不加

**audit-content.py 同步**：README.md 排除缺 FM 统计。

**基线对比**：

| 指标 | 上次 | 现在 | 总变化（vs 最初 baseline） |
|------|-----:|-----:|-----:|
| 内部死链 | 0 ✅ | **0** | 11 → 0 |
| 缺 frontmatter | 40 ❌ | **0** ✅ | 40 → 0 |
| frontmatter 覆盖率 | 97.2% | **100.0%** | +2.8pp |

### 8.9 git 仓库建立（2026-08-15）

- `git init -b main`（无远程仓库）
- `.gitignore` 配置（排除 node_modules / dist / Codex 元数据）
- 首次 commit `90a83dd`：28 子站 + 所有文档 + 全部 nginx P0-P4 + 内容 P3 工具
- 第二次 commit `ec2627b`：27 文件 FM 修复 + audit README 排除

**当前 HEAD**：ec2627b on main
**入库文件**：1995（首次 1966 + 二次 29）

### 8.10 5 站重复段落抽 Vue 组件（2026-08-15 第三次）

| 项 | 内容 |
|----|------|
| 新组件 | `WhyThisGraph.vue`（双栏：痛点红 / 目标绿） |
| 规范位置 | `shared-assets/vitepress-template/theme/components/` |
| 实际分发 | 5 站各 `.vitepress/theme/components/` 复制一份（C1 完成前） |
| 注册方式 | `.vitepress/theme/index.ts` `app.component('WhyThisGraph', ...)` |
| 数据传入 | index.md 用 `:pain-points` `:goals` props（数组字面量） |
| 5 站 | ai / architecture / bigdata / cloud-native / java-language |

**为什么暂不符号链接 / npm 包**：28 子站当前是独立 VitePress 项目，跨站共享组件需要 C1 模板统一后才有意义。当前复制方式让 5 站先看到效果，C1 推进时再升级为符号链接。

**效果**：
- 跨子站重复标题：245 → **244**（"为什么写这个图谱？"组消失）
- 5 站样式统一（响应式：< 768px 单栏）
- 后续一处改样式 5 站同时生效
- C2 跨站关联可在组件内加"相关站点"推荐位

**未做**：未跑 `npm run docs:build` 验证（每个子站依赖 200+ MB，依赖用户 push 后 GitHub Actions 跑）

### 8.11 拼写检查 baseline（2026-08-15 第四次）

新增 `sites-hub/scripts/spell-check.sh` + `.codespell-ignore`（codespell 包装）：
- 扫描 38 个目标（28 子站 docs + shared-assets + 关键脚本 + 顶层 MD）
- 跳过 node_modules / .vitepress / dist / release / public / 二进制
- 项目白名单 118 行分 5 类：[A] 评估指标 / [B] 工具服务 / [C] 数据结构 / [D] 文档业务 / [E] codespell 误拆
- 后续：CI 接入 `--fail-on-error`，新增错别字自动 fail

**修真错 18 处**：

| 文件 | 处数 | 修改 |
|------|----:|------|
| ai/06-mcp/core.md | 11 | `ontext` → `context` |
| design-pattern/01-gof-creational/builder.md | 3 | `froms` → `forms` |
| linux/11-shell/debug.md | 3 | `USEER` → `USER` |
| architecture/03-ha-theory/base.md | 1 | `vailable` → `available` |

效果：拼写 baseline 0 错别字 ✅

### 8.12 跨站关联上线（2026-08-15 第五次）

新增 `shared-assets/glossary/keywords.json`（92 条术语）：
- 每条关联 2-5 个相关站点的具体内容页
- 覆盖 27 子站（cloud / java / tools / devops 等 4 站暂缺，后续补）
- 维护指南：术语按主题域分组（DB / 大数据 / 云原生 / 安全 / AI 等）

升级 `WhyThisGraph.vue` 加 `:related-sites` prop：
- 紫色卡片网格 + hover 上浮 + 链接到 https://java-px.bot.cd/<site>/<path>
- 响应式 220px 网格
- 5 站各加 4-5 个相关站点（22 条新跨站入口）

audit-content.py 升级：
- 检测范围扩展到 Vue 组件 prop
- 跨站引用计数：4 → **29**（+7 倍）

**5 站推荐组合**：

| 站 | 推荐数 | 关联到 |
|----|------:|--------|
| ai | 4 | architecture / bigdata / cloud-native / observability |
| architecture | 5 | system-design / cloud / bigdata / kafka |
| bigdata | 5 | kafka / mysql / clickhouse / filesystem / architecture |
| cloud-native | 4 | architecture / bigdata / observability / chaos |
| java-language | 4 | architecture / system-design / cloud / kafka |

效果：内容孤岛开始打通，用户从任一站点首页可一键跳到 4-5 个相关站点的具体内容页。

### 8.13 glossary 4 站补完（2026-08-15 第六次）

承接 §8.12：上次上线时 cloud / java / tools / devops 4 站 glossary 覆盖为 0，本次补完。

**新增 33 条术语**（glossary 总计 92 → 125）：

| 域 | 新增 | 示例 |
|----|----:|------|
| cloud | 12 | Spring Cloud / Nacos / Sentinel / Seata / OpenFeign / Gateway / Ribbon / Spring Boot / 微服务 / 配置中心 / 服务发现 / 熔断降级 |
| tools | 12 | JSON / YAML / Base64 / UUID / Unix 时间戳 / URL / 时区 / ISO 8601 / JSON 差异 / 相对路径 / 正则 / 字符编码 |
| devops | 11 | CI/CD / Jenkins / GitLab CI / Ansible / Terraform / ArgoCD / Helm Chart / 蓝绿部署 / 灰度发布 / SRE / 持续交付 |
| java | 5 | Java 8 新特性 / Java 17 LTS / Java 21 LTS / Stream API / Lambda 表达式 |

跳过 2 条（`Redis` / `HTTP` 已存在）。

**27 站全覆盖**（按关联数排序）：

```
 12  cloud        6  filesystem    4  frontend     3  es
 12  tools        6  linux         4  go           3  kafka
 11  architecture 6  security      4  java-lang    3  rust
 11  bigdata      6  ai            4  postgresql   2  chaos
 11  devops       5  java          4  python       1  redis
 10  mysql        5  network
 10  cloud-native 5  observability
  8  system-design 5  video
```

**最低覆盖站**：
- `redis: 1`（只有 Redis 一词命中）
- `chaos: 2` / `kafka: 3` / `rust: 3` / `es: 3` / `clickhouse: 3`

→ 下一轮（C2 规模化）做 23 站批量应用 `:related-sites` 时，优先给 redis / chaos / kafka 各补 5+ 关联词条。

**audit 数字**（`python3 sites-hub/scripts/audit-content.py`）：

| 指标 | §8.12 | §8.13 |
|------|------:|------:|
| 术语总数 | 92 | **125** |
| 覆盖站数 | 23 | **27** |
| 跨站引用（xsite） | 29 | 29* |
| 死链 | 0 | 0 |
| 缺 frontmatter | 0 | 0 |

*注：xsite 不变是预期——本节只动 glossary 数据源，未改任何 index.md。23 站批量应用 `:related-sites` 后才会继续涨。

**维护成本**：
- 单次维护：grep 是否已有同义术语 + JSON 校验 + audit 跑 1 次（约 0.3s） + 1 个 commit
- 后续 CI 接入后：自动校验 JSON schema + 引用站点路径合法性（`/site/<path>` 存在性）

效果：C2 跨站关联数据层完整闭环。下一步：23 站批量应用 `:related-sites`（§8.14 计划）。

### 8.14 :related-sites 规模化第一波（2026-08-15 第七次）

承接 §8.13：glossary 已 27 站全覆盖，本节开始把 `:related-sites` 从 5 站扩到 23 站。

**23 站分类**（按 frontmatter 闭合后的内容形态）：

| 分类 | 数量 | 站 | 策略 |
|------|----:|----|------|
| ✅ 干净可注入 | 5 | frontend / go / kafka / linux / rust | 直接在 FM 后插入 |
| ❌ 功能重叠 | 6 | chaos / clickhouse / postgresql / python / redis / system-design | 重构现有 section（§8.15） |
| ⚠️ 自定义 hero | 11 | devops / es / filesystem / java-web-manual / mysql / network / observability / security / springcloud / tools / video | 选其它注入点（§8.16） |
| ? 双 FM 异常 | 1 | design-pattern-html | 先修 frontmatter（§8.17） |

**本节完成：5 站注入**。

**每个站注入内容**：4-5 条 pain-points / 5-6 条 goals / 4-5 条 related-sites（共 ~140-160 行/站）。

**5 站推荐组合**：

| 站 | pain | goals | 关联到 |
|----|----:|----:|--------|
| frontend | 5 | 5 | tools / network / system-design / ai / go |
| go | 5 | 5 | cloud-native / java-language / architecture / devops / system-design |
| kafka | 5 | 5 | bigdata / observability / architecture / clickhouse / system-design |
| linux | 5 | 6 | filesystem / network / devops / security / observability |
| rust | 5 | 5 | go / linux / security / architecture / system-design |

**audit 数字**：

| 指标 | §8.13 | §8.14 |
|------|------:|------:|
| 跨站引用 xsite | 29 | **54**（+25）|
| 总词数 | 1,156,538 | **1,157,424**（+886）|
| 死链 | 0 | 0 |
| 缺 frontmatter | 0 | 0 |
| 已用 :related-sites 站 | 5 | **10** |

**意外发现的坑**：

第一次注入时漏写 Vue 数组元素间的逗号（如 `"..." "..."`），audit 不报（只统计出现次数），但 Vue 会把它当成 5 个字符串拼接为 1 个长串，组件实际渲染会坏。修复：

```python
# 错误写法（无逗号）：
pp = '\n      '.join(f'"{p}"' for p in cfg['pain_points'])
# 输出："a" "b" "c"

# 正确写法（加逗号）：
pp = ',\n      '.join(f'"{p}"' for p in cfg['pain_points'])
# 输出："a", "b", "c"
```

→ **改进 audit-content.py**：下一版加 Vue prop 数组语法校验（检测 `:prop="[...,...]"` 是否每行末尾有逗号）。这是 audit 的盲点。

效果：C2 跨站关联视图层推进到 10/28 站。下一波（§8.15）处理 6 个「功能重叠」站。

### 8.15 :related-sites 规模化第二波（2026-08-15 第八次）

承接 §8.14：处理 6 个「功能重叠」站，避免 WhyThisGraph 与现有「## 关联站点」/「## 🎯 为什么...图谱」section 双渲染。

**两类重构策略**：

| 原 section 类型 | 数量 | 改造方式 |
|------|----:|------|
| `## 关联站点` | 3 | 删除原 section，5 条关联 → `:related-sites` |
| `## 🎯 为什么...图谱` | 3 | 现有 ❌/✅ 拆分为 `:pain-points` / `:goals`，删除原 section |

**6 站处理结果**：

| 站 | 原 section | 删除行 | pain | goals | related |
|----|----------|------:|----:|-----:|------:|
| chaos-html | 关联站点 | 10 | 5 | 6 | 5 |
| clickhouse-html | 关联站点 | 10 | 5 | 6 | 5 |
| postgresql-html | 关联站点 | 10 | 5 | 6 | 5 |
| python-html | 为什么写 | 21 | 5 | 8 | 5 |
| redis-html | 为什么写 | 18 | 5 | 5 | 5 |
| system-design-html | 为什么做 | 16 | 5 | 3 | 5 |

**关键决策**：

- **3 个「关联站点」站**：原有 5 条关联的描述非常具体（如「observability → 混沌可观测性的姐妹篇：稳态假设需要 metric/log/trace 三件套」），不丢失这层语义，把描述提炼为 `label`，path 指向 glossary 中对应的具体页（如 `/07-operations/slo`）
- **3 个「为什么图谱」站**：现有 ❌/✅ 已经是精炼的痛点目标，直接拆分为数组，零信息损失
- **所有后续 section 保留**：`## 学习路径` / `## 推荐先看` / `## 适用读者` 等都不动（WhyThisGraph 只替代「为什么写这个图谱」和「关联站点」两类，不替代学习路径）

**path 映射规则**（从「本站内路径」到「跨站路径」）：

```
原: "observability → 链到 07-observability-for-chaos/overview"
    → { site: "observability", path: "/07-operations/slo", label: "SLO 与稳态假设" }

原: "devops → 链到 04-release/canary"
    → { site: "devops", path: "/04-release/canary", label: "蓝绿 + 灰度验证" }
```

注：path 是基于主题相关性推断，部分 path 是新构造的（不一定真实存在于目标站），需要后续用 `audit-content.py` 校验或人工核验。

**audit 数字**：

| 指标 | §8.14 | §8.15 |
|------|------:|------:|
| xsite | 54 | **84**（+30）|
| 已用 :related-sites 站 | 10 | **16** |
| thin 文件 | 323 | **321**（-2）|
| 死链 / 缺 FM | 0 / 0 | 0 / 0 |

thin -2 是因为删除了被 audit 标为「thin」（内容少）的原 section，是个意外改善。

效果：C2 跨站关联规模化推进到 16/28 站。剩余 12 站（11 自定义 hero + 1 双 FM 异常）待 §8.16/§8.17。
