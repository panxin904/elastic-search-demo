# Contributing to Scholar's Atlas sites-hub

> 28 个 VitePress 子站的知识图谱集群（`java-px.bot.cd`）。

## 🚀 快速开始

### 提 Issue

- **内容错误** → [📝 内容反馈](https://github.com/Scholar-s-Atlas/sites-hub/issues/new?template=content_feedback.md)
- **Bug 报告** → [🐛 Bug 报告](https://github.com/Scholar-s-Atlas/sites-hub/issues/new?template=bug_report.md)
- **新功能请求** → [✨ 功能请求](https://github.com/Scholar-s-Atlas/sites-hub/issues/new?template=feature_request.md)
- **页面底部评论** → 直接用 GitHub 账号在任意文档页底部评论（需配置 Giscus，见下文）

### 改内容

```bash
git clone <repo>
cd <子站目录，如 ai-html>
# 编辑 docs/<topic>/<file>.md
npm install
npm run docs:dev  # http://localhost:5173
# 验证后提交 PR
```

---

## 📋 仓库结构

```
<root>/
├── ai-html/             # 28 个子站，每个独立 VitePress 项目
├── architecture-html/
├── ...
├── shared-assets/       # 共享模板（C1 + C7 成果）
│   └── vitepress-template/
│       ├── theme/
│       │   ├── style.css                       # 全局样式
│       │   ├── composables/readingProgress.ts  # 阅读进度条
│       │   └── components/
│       │       ├── WhyThisGraph.vue           # C2 跨站关联组件
│       │       ├── GiscusComment.vue          # C6 评论组件
│       │       └── ...
│       └── scripts/render-config.py           # config.mts 渲染
├── sites-hub/
│   ├── scripts/
│   │   ├── audit-content.py   # 内容质量审计
│   │   ├── spell-check.sh     # 拼写检查
│   │   └── check-links.py     # 死链扫描
│   ├── OPTIMIZATION.md        # nginx / 部署优化（P0-P4）
│   ├── OPTIMIZATION-CONTENT.md # 内容优化（C1-C12）
│   └── conf/nginx.conf        # nginx 配置
└── .github/
    ├── ISSUE_TEMPLATE/        # 4 个模板（bug / content / feature / config）
    └── workflows/sites-hub-ci.yml
```

---

## 🔧 配置 Giscus 评论（C6）

> 28 站共享一个 `Scholar-s-Atlas/comments` repo，所有评论统一管理。

### 一次性配置（仓库管理员）

1. 创建仓库 `Scholar-s-Atlas/comments`，启用 Discussions
2. 创建分类 `Comments`（或自定义名）
3. 访问 https://giscus.app/zh-CN
4. 填入：
   - 仓库：`Scholar-s-Atlas/comments`
   - Discussions 分类：`Comments`
   - 映射：`pathname`
   - 主题：`preferred_color_scheme`（自动跟随暗色）
5. giscus.app 生成 4 个 ID：
   - `data-repo-id`（`R_xxx`）
   - `data-category-id`（`DIC_xxx`）
6. 把这 2 个 ID 填到 `shared-assets/vitepress-template/theme/components/GiscusComment.vue` 的 props 默认值

### 在文档页启用评论

在任意 `.md` 文件末尾加：

```markdown
<ClientOnly>
  <GiscusComment />
</ClientOnly>
```

不需要每页都加，只在「需要讨论的长文」底部加。

---

## 📐 内容规范

### frontmatter 必填

```yaml
---
title: 页面标题
description: 简短描述（≤ 120 字）
date: 2026-08-16
---
```

### 跨站关联（自动）

通过 `shared-assets/glossary/keywords.json` 维护：

- 每个术语关联 2-5 个其它站的具体内容页
- WhyThisGraph 组件自动读取 glossary 生成「相关站点」推荐卡
- 加新术语前 grep 是否已有同义词

### 拼写检查

```bash
bash sites-hub/scripts/spell-check.sh
# 新增错别字会被列出
```

### 内容质量审计

```bash
python3 sites-hub/scripts/audit-content.py
# 检查 9 维度：死链 / 缺 FM / 错别字 / Vue prop bug / 组件缺失 / ...
```

报告：`sites-hub/reports/content-quality-{date}.md`

---

## 🚫 不要做

- ❌ 直接 push 到 `main` —— 用 PR + review
- ❌ 删除其它站点的内容（除非有共识）
- ❌ 在 docs/ 内嵌大图（用 WebP + lazy load）
- ❌ 硬编码颜色（用 CSS 变量）
- ❌ 跳过 frontmatter（VitePress OG/SEO 依赖）

---

## 📞 联系

- Issue: GitHub Issues
- 评论: 站点底部 Giscus
- 紧急: @maintainers
