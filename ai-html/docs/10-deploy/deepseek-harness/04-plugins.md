---
title: DeepSeek Harness 常用插件
date: 2026-09-14  # date-auto-injected
---

# 🧩 DeepSeek Harness 常用插件

> Harness 生态汇总：官方插件、社区插件、Skills、桌面壳、CI 集成。插件标记 `npm tag: dsh-plugin`。

## 📦 官方插件（deepseek-ai 组织）

| 插件名 | 说明 |
|---|---|
| `@harness/core` | Cordis 容器 + 插件加载 |
| `@harness/cli` | `dsh` 命令行 |
| `@harness/server` | Web UI 后端（Fastify） |
| `@harness/web` | Web UI 前端（Vite + Vue） |
| `@harness/config` | 配置文件 schema |
| `@harness/utils` | 通用工具函数 |
| `@harness/model-openai` | OpenAI 兼容适配（DeepSeek / Qwen / Moonshot） |
| `@harness/model-anthropic` | Anthropic Claude 适配 |
| `@harness/model-gemini` | Google Gemini 适配 |
| `@harness/model-ollama` | Ollama 本地模型适配 |
| `@harness/tool-file` | 文件读写（read/write/edit/multi_edit） |
| `@harness/tool-shell` | Shell 命令（受权限控制） |
| `@harness/tool-search` | 文件/代码搜索 |
| `@harness/tool-web` | 联网检索（web_search + web_fetch） |
| `@harness/tool-todo` | 任务清单 |
| `@harness/skill-init` | /init 项目初始化 |
| `@harness/skill-review` | /review Code Review |
| `@harness/skill-refactor` | /refactor 智能重构 |
| `@harness/skill-test` | /test 自动测试 |
| `@harness/skill-docs` | /docs 文档生成 |
| `@harness/skill-commit` | /commit Conventional Commits |
| `@harness/skill-fix` | /fix 自动修复 |
| `@harness/skill-clean` | /clean 死代码清理 |
| `@harness/skill-changelog` | /changelog 更新日志 |

## 🌟 社区精选插件（按 star 数）

### 效率类

| 插件 | 说明 | 用途 |
|---|---|---|
| `dsh-plugin-github` | GitHub CLI 集成 | 创建/管理 PR、issue、Actions |
| `dsh-plugin-gitlab` | GitLab API 集成 | MR、CI/CD、Container Registry |
| `dsh-plugin-jira` | Jira 双向同步 | 创建/查询/评论 ticket |
| `dsh-plugin-linear` | Linear 集成 | 创建/查询 issue、project |
| `dsh-plugin-notion` | Notion 集成 | 读写页面、数据库 |
| `dsh-plugin-confluence` | Confluence 集成 | 搜索/更新文档 |
| `dsh-plugin-slack` | Slack 消息 | 发消息、查 thread |
| `dsh-plugin-discord` | Discord 集成 | 发消息、管理频道 |
| `dsh-plugin-figma` | Figma 集成 | 读取设计稿、导出资源 |
| `dsh-plugin-trello` | Trello 看板 | 移动卡片、查清单 |

### 数据库 / 后端类

| 插件 | 说明 |
|---|---|
| `dsh-plugin-postgres` | PostgreSQL 查询（带 RLS 安全过滤） |
| `dsh-plugin-mysql` | MySQL 查询 |
| `dsh-plugin-mongodb` | MongoDB 文档查询 |
| `dsh-plugin-redis` | Redis 命令行操作 |
| `dsh-plugin-elasticsearch` | ES 查询 |
| `dsh-plugin-supabase` | Supabase 集成（含 Auth + RLS） |
| `dsh-plugin-prisma` | Prisma schema 迁移辅助 |
| `dsh-plugin-kafka` | Kafka topic 浏览 + 生产消费 |
| `dsh-plugin-s3` | S3 / OSS 文件读写 |
| `dsh-plugin-cloudflare` | Cloudflare Workers + KV + D1 |

### DevOps / 监控类

| 插件 | 说明 |
|---|---|
| `dsh-plugin-docker` | Docker 镜像 / 容器管理 |
| `dsh-plugin-k8s` | kubectl 包装 + Helm 操作 |
| `dsh-plugin-terraform` | Terraform plan/apply 辅助 |
| `dsh-plugin-aws` | AWS CLI 集成（EC2/S3/Lambda） |
| `dsh-plugin-gcp` | GCP CLI 集成 |
| `dsh-plugin-azure` | Azure CLI 集成 |
| `dsh-plugin-prometheus` | Prometheus PromQL 查询 |
| `dsh-plugin-grafana` | Grafana Dashboard 操作 |
| `dsh-plugin-datadog` | Datadog 指标 + 日志 |
| `dsh-plugin-sentry` | Sentry 错误查询 |

### 测试 / 质量类

| 插件 | 说明 |
|---|---|
| `dsh-plugin-jest` | Jest 跑测 + 生成用例 |
| `dsh-plugin-vitest` | Vitest 集成 |
| `dsh-plugin-playwright` | Playwright E2E 测试生成 |
| `dsh-plugin-cypress` | Cypress 测试辅助 |
| `dsh-plugin-sonarqube` | SonarQube 集成 |
| `dsh-plugin-eslint` | ESLint 自动修复 |
| `dsh-plugin-prettier` | Prettier 自动格式化 |
| `dsh-plugin-perf` | Lighthouse 性能审计 |

### AI / ML 类

| 插件 | 说明 |
|---|---|
| `dsh-plugin-rag` | 本地 RAG（基于向量库） |
| `dsh-plugin-embedding` | 多模型 Embedding 适配 |
| `dsh-plugin-image` | 多模态图像理解 |
| `dsh-plugin-tts` | 文本转语音 |
| `dsh-plugin-stt` | 语音转文本 |
| `dsh-plugin-translate` | 多语种翻译 |
| `dsh-plugin-ocr` | OCR 文本提取 |

### 安全 / 凭据类

| 插件 | 说明 |
|---|---|
| `dsh-plugin-1password` | 1Password 密钥管理 |
| `dsh-plugin-vault` | HashiCorp Vault 集成 |
| `dsh-plugin-bitwarden` | Bitwarden 密码读取 |
| `dsh-plugin-snyk` | Snyk 漏洞扫描 |
| `dsh-plugin-trivy` | 容器镜像扫描 |

## 🎯 Skills 库（精选）

### 官方 Skills

```
/init          项目初始化（生成 .dsh/ + README）
/review        Code Review（基于 git diff）
/refactor      智能重构（保持行为）
/test          自动补单元测试
/docs          文档生成/同步
/commit        Conventional Commits
/fix           自动修复 lint/test
/clean         死代码清理
/changelog     CHANGELOG 更新
/migration        数据库 schema 迁移辅助
/plan          任务规划（多步骤）
/explain       复杂代码解释
/optimize      性能优化建议
/security      安全审查
/i18n          国际化文案生成
```

### 社区 Skills

```
/pr-review     PR 自动审查（集成 GitHub）
/pr-fix        PR 评论自动修复建议
/issue-triage  Issue 自动分类
/release-notes 发布说明生成
/api-doc       OpenAPI 文档生成
/db-diagram    ER 图生成
/test-coverage 测试覆盖率补齐
/load-test     k6 压测脚本生成
/migration     跨语言代码迁移（如 JS → Go）
/regex-explain 正则表达式解释
/sql-explain   SQL 执行计划分析
/git-blame-stats  blame 统计
/deps-audit    依赖审计
/license-check License 合规检查
```

## 🖥️ 桌面壳 / 客户端

### 第三方 GUI 封装

| 应用 | 平台 | 说明 |
|---|---|---|
| **Harness Desktop** | macOS / Win / Linux | Electron 封装版，含托盘 + 全局快捷键 |
| **Harness Tray** | macOS | 菜单栏常驻，最快启动 |
| **Harness Tray (Windows)** | Windows | 系统托盘 |
| **Harness Web Tray** | Chrome | Chrome 扩展（侧边栏） |
| **Harness Raycast** | macOS | Raycast 扩展 |
| **Harness Alfred** | macOS | Alfred Workflow |
| **Harness Spotlight** | macOS | Spotlight 替代 |

### TUI 替代

| 应用 | 说明 |
|---|---|
| **Harness TUI** | Rust 写的 Terminal UI（更流畅） |
| **Harness Bubbletea** | Go 写的 Terminal UI |
| **hsmux** | tmux 集成，多 pane 显示 Harness |

## 🔌 IDE 集成

| IDE | 扩展名 | 功能 |
|---|---|---|
| VS Code | `harness-vscode` | 官方侧边栏 + 内联 diff |
| JetBrains | `harness-jetbrains` | IntelliJ 插件（IDEA / WebStorm / PyCharm） |
| Sublime | `Harness-Sublime` | 命令面板 + 内联 |
| Vim | `harness.vim` | 命令 + 异步流 |
| Neovim | `harness.nvim` | Telescope + inline diff |
| Emacs | `harness.el` | magit 集成 |

## 📱 移动端

| 应用 | 平台 |
|---|---|
| **Harness Mobile (iOS)** | iOS / iPadOS |
| **Harness Mobile (Android)** | Android |
| **Harness Web (PWA)** | 任意浏览器（响应式） |

## 🤖 CI 集成

| CI | 集成方式 |
|---|---|
| GitHub Actions | `deepseek-ai/harness-action` Marketplace Action |
| GitLab CI | `dsh-gitlab-runner` 镜像 |
| Jenkins | `harness-jenkins-plugin` |
| CircleCI | `harness-orb` |
| Buildkite | `harness-buildkite-plugin` |
| Drone | `harness-drone-plugin` |

### 示例：GitHub Actions 中用 Harness

```yaml
# .github/workflows/harness-review.yml
name: AI Code Review
on: [pull_request]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: deepseek-ai/harness-action@v1
        with:
          profile: ci
          skill: /review
          args: ${{ github.event.pull_request.base.sha }} ${{ github.event.pull_request.head.sha }}
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
      - uses: marocchino/sticky-pull-request-comment@v2
        with:
          message: ${{ steps.review.outputs.comment }}
```

## 📚 模板库（Preset）

Harness 内置 4 个 preset，可扩展：

```
presets/
├─ standard/    # 默认
├─ ptc/         # Programmatic Tool Calling
├─ minimal/     # 极简
├─ creative/    # 创造
├─ security/    # 安全审查专家
├─ data/        # 数据分析专家
├─ devops/      # DevOps 专家
└─ doc-writer/  # 文档写作专家
```

### 用 preset

```bash
dsh --preset security
# 或写 config.yaml:
preset: security
```

## 🔍 插件搜索与安装

### 官方插件索引

```bash
# 列出所有官方插件
dsh plugin list --official

# 搜索关键字
dsh plugin search "github"
# 输出：
# dsh-plugin-github        1.2k ⭐  GitHub CLI 集成
# dsh-plugin-github-pr     234 ⭐    PR 评论自动审查
# dsh-plugin-github-issue  156 ⭐    Issue 自动管理
```

### 安装

```bash
# 装最新
dsh plugin install dsh-plugin-github

# 装指定版本
dsh plugin install dsh-plugin-github@2.1.0

# 装多个
dsh plugin install dsh-plugin-github dsh-plugin-jira dsh-plugin-figma

# 列出已装
dsh plugin list

# 更新
dsh plugin update

# 卸载
dsh plugin uninstall dsh-plugin-github
```

### 配置文件位置

```
~/.config/dsh/plugins/        # 全局插件
.dsh/plugins/                 # 项目级插件
```

## 💡 选型建议

```
🎯 个人开发者：
   必备：dsh-plugin-github / dsh-plugin-docker
   推荐：dsh-plugin-1password

🎯 前端工程师：
   必备：dsh-plugin-figma / dsh-plugin-postgres
   推荐：dsh-plugin-playwright / dsh-plugin-image

🎯 后端工程师：
   必备：dsh-plugin-postgres / dsh-plugin-redis / dsh-plugin-k8s
   推荐：dsh-plugin-datadog / dsh-plugin-prometheus

🎯 数据工程师：
   必备：dsh-plugin-postgres / dsh-plugin-elasticsearch
   推荐：dsh-plugin-embedding / dsh-plugin-rag

🎯 DevOps / SRE：
   必备：dsh-plugin-k8s / dsh-plugin-aws / dsh-plugin-prometheus
   推荐：dsh-plugin-terraform / dsh-plugin-snyk

🎯 团队协作：
   必备：dsh-plugin-jira / dsh-plugin-slack / dsh-plugin-notion
   推荐：dsh-plugin-github / dsh-plugin-figma
```
