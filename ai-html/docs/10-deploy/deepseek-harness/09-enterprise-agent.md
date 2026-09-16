---
title: 企业级 Agent 构建完整实战
date: 2026-09-16  # date-auto-injected
---

# 🏢 企业级 Agent 构建完整实战

> 本章是 [03-recipes.md](./03-recipes) + [06-advanced.md](./06-advanced) 的企业级实战版。用一个完整的 **PR Reviewer Agent** 为例，展示如何用 dsh 整合 **preset + skills + plugins + MCP + 子代理** 五件套，构建可上线的企业级 AI Agent。
>
> 同样适用于其他 Agent 场景：Data Analyst、Security Audit、SRE Incident、Onboarding 等——只需替换配置和业务代码。

## 🎯 企业级 Agent 的核心特征

```
✅ 可复用        preset 一次定义，全团队使用
✅ 可观测        所有 tool_call / shell / file_edit 可审计
✅ 可扩展        新场景只需加 Skill，不用改核心
✅ 安全隔离       sandbox + permissions + 沙箱检查
✅ 多系统集成     MCP 连接 GitHub / Jira / Slack
✅ 多 Agent 协作  Supervisor + 子代理 + 流水线
✅ 可分发        Git / npm / Docker 多种方式
```

## 🏛️ 完整架构（五件套）

```
PR Reviewer Agent
│
├── 📋 preset.yaml       ← 场景配置（系统 prompt + 工具集 + 权限）
├── 📚 skills/            ← Skill 命令（/review-pr / /review-batch）
│   ├── review-pr.md
│   ├── review-batch.md
│   └── review-stale.md
├── 🔌 plugins/           ← 自定义业务插件（持久化 / 内部 API）
│   ├── review-store/     ← 审查历史存储
│   ├── pr-analyzer/      ← PR 复杂度分析
│   └── team-policy/      ← 团队规范检查
├── 🤖 agents/            ← 子代理（多 Agent 协作）
│   ├── security-agent    ← 专门安全审查
│   ├── perf-agent        ← 专门性能分析
│   └── style-agent       ← 专门代码风格
├── 🌐 mcp-servers.json   ← 外部系统（MCP 连接）
│   ├── github            ← GitHub API
│   ├── jira              ← Jira API
│   └── slack             ← Slack 通知
└── 📖 README.md          ← 团队使用文档
```

## 📁 完整目录结构

```
my-pr-reviewer-agent/
├─ preset.yaml                          # 主配置
├─ README.md                            # 使用文档
├─ package.json                         # 依赖（plugins/ 子包）
├─ pnpm-workspace.yaml                  # monorepo 配置
├─ tsconfig.json                        # TS 配置
│
├─ skills/                              # Skill 命令定义
│  ├─ review-pr.md                       # /review-pr
│  ├─ review-batch.md                   # /review-batch
│  ├─ review-stale.md                   # /review-stale
│  └─ review-summary.md                  # /review-summary
│
├─ plugins/                             # 自定义 Cordis 插件
│  ├─ review-store/                     # SQLite 持久化
│  │  ├─ src/index.ts
│  │  ├─ package.json
│  │  └─ tsconfig.json
│  ├─ pr-analyzer/                      # PR 复杂度分析
│  │  ├─ src/index.ts
│  │  └─ package.json
│  └─ team-policy/                      # 团队规范
│     ├─ src/index.ts
│     ├─ policies/
│     │  ├─ naming.md
│     │  ├─ testing.md
│     │  └─ security.md
│     └─ package.json
│
├─ agents/                              # 子代理定义
│  ├─ security-agent/
│  │  ├─ system-prompt.md
│  │  ├─ tools.json
│  │  └─ config.yaml
│  ├─ perf-agent/
│  │  └─ ...
│  └─ style-agent/
│     └─ ...
│
├─ mcp-servers.json                     # MCP 配置
├─ .env.example                         # 环境变量示例
└─ docker-compose.yml                   # Docker 部署
```

## 📋 1. preset.yaml（主配置）

```yaml
# my-pr-reviewer-agent/preset.yaml
name: pr-reviewer
version: 1.2.0
description: 企业级自动化 PR Review Agent
mode: standard

# ========== Agent 人格 + 系统 prompt ==========
system_prompt: |
  你是 PR Review Agent v1.2，团队代码质量守门人。

  ## 核心职责
  1. 审查 PR 变更（安全 / 性能 / 风格 / 测试 / 文档）
  2. 维护审查历史（SQLite 持久化）
  3. 执行团队规范（team-policy 插件）
  4. 并行调度3 个子代理深度审查
  5. 生成可发布的审查报告

  ## 工作流（PR Review 全流程）
  1. 获取 PR 元数据（mcp.github.get_pull_request）
  2. 获取 diff（gh pr diff）
  3. 计算复杂度（pr-analyzer 工具）
  4. 并行启动3 个子代理：
     ├ security-agent：OWASP Top 10 + 依赖漏洞
     ├ perf-agent：N+1 查询 / 内存泄漏 / 阻塞 IO
     └ style-agent：lint / type / 命名规范
  5. 汇总子代理结果
  6. 调用 team-policy 检查规范
  7. 生成 Markdown 报告
  8. 保存到 SQLite（review-store 工具）
  9. 询问用户是否发布到 GitHub 评论
  10. 通知 Slack（mcp.slack.post_message）

  ## 输出格式（强制）
  ```
  ## 📋 PR 概览
  - 编号：#`<number>`
  - 标题：`<title>`
  - 作者：`<author>`
  - 变更：+`<additions>` -`<deletions>` (`<changed_files>` files)
  - 复杂度：`<score>`/100

  ## 🔴 严重问题（必须修复）
  - [文件名:行号] 问题描述
    修复建议：...

  ## 🟡 改进建议
  - ...

  ## 🟢 亮点
  - ...

  ## 📊 团队规范检查
  - ✅ 命名规范
  - ⚠️ 测试覆盖率 < 80%
  - ...

  ## 🎯 总结
  - 总体评价
  - 是否可合并（YES / NO / WITH FIXES）
  ```

# ========== 启用的插件 ==========
plugins:
  enabled:
    # 核心运行时
    - model-anthropic
    - model-openai              # fallback

    # 工具
    - tool-git
    - tool-shell
    - tool-file-edit
    - tool-search
    - tool-web                  # 联网查文档

    # 自定义业务插件
    - ./plugins/review-store     # SQLite 持久化
    - ./plugins/pr-analyzer     # PR 复杂度
    - ./plugins/team-policy     # 团队规范

    # 子代理
    - ./agents/security-agent
    - ./agents/perf-agent
    - ./agents/style-agent

    # MCP 外部系统
    - mcp-github
    - mcp-jira
    - mcp-slack

  disabled:
    - tool-deploy
    - tool-db
    - tool-email

# ========== 默认工具集（暴露给 LLM） ==========
tools:
  default:
    # 内置工具
    - git_diff
    - git_log
    - git_show
    - read_file
    - search_code
    - run_shell
    - web_search

    # 自定义工具
    - pr_analyzer.complexity_score
    - pr_analyzer.file_hotspots
    - review_store.save_review
    - review_store.list_recent
    - review_store.search_similar
    - team_policy.check

    # MCP 工具
    - mcp.github.get_pull_request
    - mcp.github.list_pull_request_files
    - mcp.github.get_file_content
    - mcp.github.create_issue_comment
    - mcp.jira.get_issue
    - mcp.jira.create_issue
    - mcp.slack.post_message

  require_approval:
    - run_shell
    - mcp.github.create_issue_comment    # 发评论前确认
    - mcp.slack.post_message

# ========== 权限（沙箱） ==========
permissions:
  filesystem:
    read: ["**"]
    deny: [".env", "secrets/**", "**/prod/**", ".aws/**"]
  shell:
    allow:
      - "git status"
      - "git diff"
      - "git log"
      - "git show"
      - "gh pr view"
      - "gh pr diff"
      - "gh pr list"
      - "npm test"
      - "npm run lint"
      - "npm run typecheck"
      - "pnpm test"
      - "pnpm lint"
      - "cat"
      - "ls"
    deny:
      - "rm -rf"
      - "sudo"
      - "git push --force"
      - "git reset --hard"
      - "curl * | sh"

sandbox:
  level: strict

# ========== 模型配置 ==========
model_overrides:
  default: sonnet
  fallback: gpt-5-mini
  temperature: 0.2                  # 审查任务低随机性
  max_tokens: 8000

# ========== UI 定制 ==========
ui:
  show_diff: side-by-side
  auto_apply: false
  show_cost: true
  show_token_usage: true
  shortcuts:
    submit_comment: "cmd+enter"
    skip_question: "cmd+shift+s"

# ========== 审计 ==========
audit:
  log_path: ~/.local/share/dsh/audit/pr-reviewer.jsonl
  retention_days: 365
  redact_secrets: true

# ========== 性能优化 ==========
performance:
  parallel_tool_calls: true
  max_concurrent_tools: 5
  llm_cache:
    enabled: true
    ttl: 3600
```

## 📚 2. Skills（任务命令）

### 2.1 /review-pr — 审查单个 PR

```yaml
# skills/review-pr.md
---
name: review-pr
description: 审查单个 PR（含完整流程）
mode: standard
inputs:
  - name: pr_number
    type: number
    required: false
    description: PR 编号（省略时用当前分支）
  - name: focus
    type: enum
    options: [all, security, performance, style]
    default: all
    description: 审查焦点
  - name: post_comment
    type: boolean
    default: false
    description: 审查后是否发 PR 评论
---

# /review-pr Skill

## 输入
- `pr_number`（可选）：PR 编号
- `focus`（默认 all）：审查焦点
- `post_comment`（默认 false）：是否发 PR 评论

## 完整流程

### Step 1：获取 PR 信息
```bash
# 如有 pr_number
gh pr view `<pr_number>` --json number,title,author,additions,deletions,changedFiles,baseRefName,headRefName

# 否则用当前分支
gh pr view --json number,title,author,additions,deletions,changedFiles
```

### Step 2：获取 diff
```bash
# 完整 diff
gh pr diff `<pr_number>`

# 或本地 diff（对比 base 分支）
git diff origin/`<base_branch>`...HEAD
```

### Step 3：分析变更
```bash
# 用 pr_analyzer 工具
pr_analyzer.complexity_score({
  pr_number: `<number>`,
  diff: `<diff_content>`
})

pr_analyzer.file_hotspots({
  files: `<changed_files>`,
  metric: "churn+complexity"
})
```

### Step 4：并行启动3 个子代理
```
并行派发：
- security-agent：审查安全风险
- perf-agent：审查性能瓶颈
- style-agent：审查代码风格

每个子代理返回结构化报告：
{
  findings: [
    { severity, file, line, message, suggestion }
  ],
  summary: "..."
}
```

### Step 5：执行团队规范
```yaml
team_policy.check({
  policies: ["naming", "testing", "security"],
  files: `<changed_files>`,
  pr_author: `<author>`
})
```

### Step 6：生成报告
按 system_prompt 中的输出格式整理。

### Step 7：保存历史
```yaml
review_store.save_review({
  pr_number: `<number>`,
  pr_title: `<title>`,
  author: `<author>`,
  review: `<markdown_report>`,
  severity: { critical, warning, good }
})
```

### Step 8：发布（可选）
```
如果 post_comment=true：
  询问用户 → mcp.github.create_issue_comment({
    owner, repo, issue_number: `<number>`,
    body: `<markdown_report>`
  })

通知 Slack：
  mcp.slack.post_message({
    channel: "#code-review",
    text: "PR #`<number>` 审查完成：`<summary>`"
  })
```

## 错误处理

- PR 不存在 → 提示用 gh pr list 查看
- diff 为空 → 提示可能是 merge commit
- 子代理失败 → 重试 1 次后回退到主代理单独审查
- API 限流 → 自动 fallback model
```

### 2.2 /review-batch — 批量审查

```yaml
# skills/review-batch.md
---
name: review-batch
description: 批量审查多个 PR（按 label 过滤）
mode: ptc   # PTC 模式适合批量编排
inputs:
  - name: label
    type: string
    default: "needs-review"
  - name: limit
    type: number
    default: 10
---

# /review-batch Skill

## 流程

1. 列出所有带 `<label>` 的 PR
   ```bash
   gh pr list --label `<label>` --json number,title --limit `<limit>`
   ```

2. 对每个 PR 并行派发 /review-pr（子代理）

3. 汇总结果：
   - 各 PR 审查摘要
   - 高风险 PR 列表
   - 团队成员贡献统计

4. 输出 Markdown 报告 + 发送 Slack
```

### 2.3 /review-stale — 审查过期 PR

```yaml
# skills/review-stale.md
---
name: review-stale
description: 找出超过 N 天未合并的 PR
---

# /review-stale Skill

## 流程

1. 列出创建超过 14 天的 open PR
   ```bash
   gh pr list --state open --json number,title,createdAt
   ```

2. 按创建时间排序

3. 输出表格 + 建议操作（close / 跟进 / 合并）
```

## 🔌 3. 自定义 Plugins

### 3.1 review-store（SQLite 持久化）

```typescript
// plugins/review-store/src/index.ts
import { Service, Context } from 'cordis'
import { z } from 'zod'
import Database from 'better-sqlite3'
import { promises as fs } from 'node:fs'
import { dirname } from 'node:path'

export default class ReviewStoreService extends Service {
  static Config = {
    dbPath: { type: 'string', default: '~/.local/share/dsh/reviews.db' },
  }

  static inject = ['logger']

  private db!: Database.Database

  constructor(ctx: Context, private config: { dbPath: string }) {
    super(ctx, 'review_store', true)
  }

  async start() {
    // 初始化数据库
    const dbPath = this.config.dbPath.replace('~', process.env.HOME!)
    await fs.mkdir(dirname(dbPath), { recursive: true })

    this.db = new Database(dbPath)
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS reviews (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          pr_number INTEGER NOT NULL,
          pr_title TEXT NOT NULL,
          author TEXT,
          review_text TEXT NOT NULL,
          severity TEXT NOT NULL,
          focus TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          INDEX idx_pr (pr_number),
          INDEX idx_created (created_at)
        );

      CREATE TABLE IF NOT EXISTS findings (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          review_id INTEGER REFERENCES reviews(id) ON DELETE CASCADE,
          severity TEXT NOT NULL,
          file TEXT,
          line INTEGER,
          message TEXT NOT NULL,
          suggestion TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    `)

    // 注册工具
    this.registerTools()
  }

  private registerTools() {
    // 1. 保存审查
    this.ctx.tool('save_review', {
      description: '保存 PR 审查结果（含 findings）到 SQLite',
      parameters: z.object({
        pr_number: z.number(),
        pr_title: z.string(),
        author: z.string().optional(),
        review: z.string().describe('完整 Markdown 报告'),
        severity: z.object({
          critical: z.number().default(0),
          warning: z.number().default(0),
          good: z.number().default(0),
        }),
        focus: z.string().optional(),
        findings: z.array(z.object({
          severity: z.enum(['critical', 'warning', 'good']),
          file: z.string().optional(),
          line: z.number().optional(),
          message: z.string(),
          suggestion: z.string().optional(),
        })).optional(),
      }),
      riskLevel: 'write',
      handler: async (params, ctx) => {
        const tx = this.db.transaction(() => {
          const result = this.db.prepare(`
            INSERT INTO reviews (pr_number, pr_title, author, review_text, severity, focus)
            VALUES (?, ?, ?, ?, ?, ?)
          `).run(
            params.pr_number,
            params.pr_title,
            params.author ?? null,
            params.review,
            JSON.stringify(params.severity),
            params.focus ?? null
          )

          const reviewId = result.lastInsertRowid as number

          if (params.findings?.length) {
            const stmt = this.db.prepare(`
              INSERT INTO findings (review_id, severity, file, line, message, suggestion)
              VALUES (?, ?, ?, ?, ?, ?)
            `)
            for (const f of params.findings) {
              stmt.run(
                reviewId,
                f.severity,
                f.file ?? null,
                f.line ?? null,
                f.message,
                f.suggestion ?? null
              )
            }
          }

          return reviewId
        })

        const reviewId = tx()
        this.ctx.logger.info('review saved', { review_id: reviewId })
        return `✓ Review #${reviewId} saved (${params.findings?.length ?? 0} findings)`
      },
    })

    // 2. 列历史
    this.ctx.tool('list_recent_reviews', {
      description: '列出最近的 PR 审查记录',
      parameters: z.object({
        limit: z.number().min(1).max(100).default(10),
        author: z.string().optional(),
      }),
      riskLevel: 'read',
      handler: async ({ limit, author }, ctx) => {
        const sql = author
          ? 'SELECT * FROM reviews WHERE author = ? ORDER BY created_at DESC LIMIT ?'
          : 'SELECT * FROM reviews ORDER BY created_at DESC LIMIT ?'
        const rows = this.db.prepare(sql).all(...(author ? [author, limit] : [limit]))
        return JSON.stringify(rows, null, 2)
      },
    })

    // 3. 搜索相似审查
    this.ctx.tool('search_similar_reviews', {
      description: '基于关键词搜索历史审查',
      parameters: z.object({
        query: z.string().describe('搜索词（如 SQL injection）'),
        limit: z.number().default(5),
      }),
      riskLevel: 'read',
      handler: async ({ query, limit }, ctx) => {
        const rows = this.db.prepare(`
          SELECT r.*, GROUP_CONCAT(f.message, ' | ') AS finding_messages
          FROM reviews r
          LEFT JOIN findings f ON f.review_id = r.id
          WHERE r.review_text LIKE ? OR f.message LIKE ?
          GROUP BY r.id
          ORDER BY r.created_at DESC
          LIMIT ?
        `).all(`%${query}%`, `%${query}%`, limit)

        return JSON.stringify(rows, null, 2)
      },
    })

    // 4. 统计
    this.ctx.tool('review_statistics', {
      description: '生成审查统计报告（按作者 / 时间 / 严重级别）',
      parameters: z.object({
        days: z.number().default(30),
      }),
      riskLevel: 'read',
      handler: async ({ days }, ctx) => {
        const since = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString()

        const totalReviews = this.db.prepare(
          'SELECT COUNT(*) AS count FROM reviews WHERE created_at >= ?'
        ).get(since) as any

        const byAuthor = this.db.prepare(`
          SELECT author, COUNT(*) AS count,
                 AVG(json_extract(severity, '$.critical')) AS avg_critical
          FROM reviews
          WHERE created_at >= ?
          GROUP BY author
          ORDER BY count DESC
          LIMIT 10
        `).all(since)

        const topIssues = this.db.prepare(`
          SELECT message, COUNT(*) AS occurrences
          FROM findings
          WHERE severity = 'critical' AND created_at >= ?
          GROUP BY message
          ORDER BY occurrences DESC
          LIMIT 10
        `).all(since)

        return JSON.stringify({
          period_days: days,
          total_reviews: totalReviews.count,
          by_author: byAuthor,
          top_critical_issues: topIssues,
        }, null, 2)
      },
    })
  }

  async stop() {
    this.db?.close()
  }
}

declare module 'cordis' {
  interface Context {
    review_store: ReviewStoreService
  }
}
```

```json
// plugins/review-store/package.json
{
  "name": "@my-org/dsh-plugin-review-store",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "keywords": ["dsh-plugin", "cordis", "pr-reviewer"],
  "dependencies": {
    "better-sqlite3": "^11.3.0",
    "cordis": "^2.0.0",
    "zod": "^3.23.0"
  },
  "peerDependencies": {
    "@harness/core": "^0.1.2"
  }
}
```

### 3.2 pr-analyzer（PR 复杂度分析）

```typescript
// plugins/pr-analyzer/src/index.ts
import { Service, Context } from 'cordis'
import { z } from 'zod'

export default class PrAnalyzerService extends Service {
  static Config = {
    complexity_threshold: { type: 'number', default: 70 },
  }

  async start() {
    // 1. 复杂度评分
    this.ctx.tool('complexity_score', {
      description: '评估 PR 复杂度（0-100）',
      parameters: z.object({
        diff: z.string().describe('完整 diff 内容'),
        changed_files: z.array(z.string()),
        additions: z.number(),
        deletions: z.number(),
      }),
      riskLevel: 'read',
      handler: async ({ diff, changed_files, additions, deletions }, ctx) => {
        let score = 0
        const factors: Record<string, number> = {}

        // 变更行数（40 分）
        const totalLines = additions + deletions
        const lineScore = Math.min(40, totalLines / 25)
        factors.lines = lineScore
        score += lineScore

        // 文件数（20 分）
        const fileScore = Math.min(20, changed_files.length * 2)
        factors.files = fileScore
        score += fileScore

        // 嵌套复杂度（25 分）
        const nestedDepth = (diff.match(/\n {4,}/g) || []).length
        const nestedScore = Math.min(25, nestedDepth * 0.5)
        factors.nesting = nestedScore
        score += nestedScore

        // 测试覆盖（15 分）—— 启发式：是否有测试文件改动
        const hasTestChanges = changed_files.some(f =>
          f.includes('test') || f.includes('spec') || f.includes('__tests__')
        )
        factors.test_coverage = hasTestChanges ? 15 : 0
        score += factors.test_coverage

        const level = score < 30 ? 'low' : score < 60 ? 'medium' : 'high'

        return JSON.stringify({
          score: Math.round(score),
          level,
          factors,
          recommendation: score > 70
            ? '建议拆分为多个小 PR'
            : score > 40
              ? '可合并，但需仔细 review'
              : '复杂度低，快速 review',
        }, null, 2)
      },
    })

    // 2. 热点文件
    this.ctx.tool('file_hotspots', {
      description: '识别 PR 中的热点文件（高改动频率 + 高复杂度）',
      parameters: z.object({
        files: z.array(z.string()),
      }),
      riskLevel: 'read',
      handler: async ({ files }, ctx) => {
        // 用 git log 统计每个文件的改动频率
        const hotspots = await Promise.all(
          files.map(async file => {
            const { exec } = await import('node:child_process')
            const util = await import('node:util')
            const execp = util.promisify(exec)

            try {
              const { stdout } = await execp(
                `git log --oneline --follow -50 -- "${file}" | wc -l`
              )
              const churn = parseInt(stdout.trim())

              return {
                file,
                churn,
                risk: churn > 20 ? 'high' : churn > 10 ? 'medium' : 'low',
                reason: churn > 20 ? '改动频繁，需特别关注' : '常规文件',
              }
            } catch {
              return { file, churn: 0, risk: 'unknown', reason: '无法读取 git 历史' }
            }
          })
        )

        return JSON.stringify(hotspots.sort((a, b) => b.churn - a.churn), null, 2)
      },
    })
  }
}

declare module 'cordis' {
  interface Context {
    pr_analyzer: PrAnalyzerService
  }
}
```

### 3.3 team-policy（团队规范）

```typescript
// plugins/team-policy/src/index.ts
import { Service, Context } from 'cordis'
import { z } from 'zod'
import { promises as fs } from 'node:fs'
import { join } from 'node:path'

export default class TeamPolicyService extends Service {
  static Config = {
    policies_dir: { type: 'string', default: './policies' },
  }

  constructor(ctx, private config: { policies_dir: string }) {
    super(ctx, 'team_policy', true)
  }

  async start() {
    this.ctx.tool('check', {
      description: '检查代码是否符合团队规范',
      parameters: z.object({
        policies: z.array(z.string()).describe('要检查的规范列表'),
        files: z.array(z.string()).describe('要检查的文件'),
        pr_author: z.string().optional(),
      }),
      riskLevel: 'read',
      handler: async ({ policies, files, pr_author }, ctx) => {
        const violations: any[] = []

        for (const policyName of policies) {
          const policy = await this.loadPolicy(policyName)
          if (!policy) continue

          for (const file of files) {
            const fileViolations = await this.checkFile(file, policy, pr_author)
            violations.push(...fileViolations)
        }

        return JSON.stringify({
          passed: violations.length === 0,
          violations,
          summary: `${violations.filter(v => v.severity === 'error').length} errors, ${violations.filter(v => v.severity === 'warning').length} warnings`,
        }, null, 2)
      },
    })

    this.ctx.tool('list_policies', {
      description: '列出所有可用的团队规范',
      parameters: z.object({}),
      riskLevel: 'read',
      handler: async (_, ctx) => {
        const files = await fs.readdir(this.config.policies_dir)
        return files.filter(f => f.endsWith('.md')).join('\n')
      },
    })
  }

  private async loadPolicy(name: string): Promise<any> {
    try {
      const content = await fs.readFile(
        join(this.config.policies_dir, `${name}.md`),
        'utf-8'
      )
      // 解析 Markdown frontmatter + 检查规则
      const match = content.match(/^---\n([\s\S]+?)\n---\n([\s\S]+)$/)
      if (!match) return null

      const [, frontmatter, body] = match
      // 简化：用 YAML 解析 frontmatter + 正则提取规则
      return {
        name,
        rules: this.extractRules(body),
      }
    } catch {
      return null
    }
  }

  private extractRules(text: string): RegExp[] {
    // 提取形如 `- pattern: \`regex\`` 的规则
    const rules: RegExp[] = []
    const matches = text.matchAll(/pattern: `(.+?)`/g)
    for (const m of matches) {
      try {
        rules.push(new RegExp(m[1], 'gm'))
      } catch {}
    }
    return rules
  }

  private async checkFile(file: string, policy: any, _author?: string): Promise<any[]> {
    try {
      const content = await fs.readFile(file, 'utf-8')
      const violations: any[] = []

      for (const rule of policy.rules) {
        const lines = content.split('\n')
        lines.forEach((line, idx) => {
          if (rule.test(line)) {
            violations.push({
              policy: policy.name,
              severity: 'warning',
              file,
              line: idx + 1,
              message: `匹配规则: ${rule.source}`,
            })
          }
        })
      }

      return violations
    } catch {
      return []
    }
  }
}

declare module 'cordis' {
  interface Context {
    team_policy: TeamPolicyService
  }
}
```

```markdown
<!-- plugins/team-policy/policies/naming.md -->
---
description: 命名规范
---

# 命名规范

## 必须遵循
- 文件名：kebab-case（`user-profile.ts`）
- 类名：PascalCase（`UserProfile`）
- 变量/函数：camelCase（`getUserName`）
- 常量：UPPER_SNAKE（`MAX_RETRIES`）

## 禁止模式
- 单字母变量：`pattern: `[a-z]\s*=\s*[^=]``
- 拼音命名：`pattern: `(?i)(mingzi|nianling|dizhi)``
- 下划线开头：`pattern: `^_\w+\s*=``
```

## 🤖 4. 子代理（多 Agent 协作）

### 4.1 security-agent

```yaml
# agents/security-agent/config.yaml
name: security-agent
description: 专门做安全审查的子代理
model: sonnet

system_prompt: |
  你是 Security Agent，专精应用安全。
  ## 审查范围
  - OWASP Top 10（2026 版）
  - 依赖漏洞（npm audit / pip-audit）
  - 密钥泄漏（API Key / Token / Password）
  - 注入风险（SQL / NoSQL / LDAP / OS Command）
  - 身份认证与授权失效
  - 敏感数据暴露
  - XXE / XSS / CSRF
  - 不安全反序列化
  - 已知漏洞组件
  - 日志与监控不足

  ## 工具集
  - semgrep_scan：静态分析
  - snyk_check：依赖漏洞
  - search_secrets：密钥扫描（gitleaks）
  - run_shell：受限 shell
  - read_file：读源码

  ## 输出格式
  返回 JSON 数组：
  [
    {
      "severity": "critical|warning|info",
      "category": "owasp_category",
      "file": "...",
      "line": 123,
      "message": "...",
      "suggestion": "..."
    }
  ]

tools:
  - semgrep_scan
  - snyk_check
  - search_secrets
  - run_shell
  - read_file
  - search_code

permissions:
  shell:
    allow:
      - "semgrep"
      - "snyk test"
      - "gitleaks detect"
      - "npm audit"
      - "pip-audit"
    deny: ["*"]

isolated_session: true
max_iterations: 20
```

```typescript
// agents/security-agent/index.ts（自动加载）
import { Service } from 'cordis'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import yaml from 'yaml'

export default class SecurityAgentService extends Service {
  async start() {
    // 读取 agent config
    const configPath = join(__dirname, 'config.yaml')
    const config = yaml.parse(await readFile(configPath, 'utf-8'))

    this.ctx.tool('security_audit', {
      description: '派生子代理做安全审查',
      parameters: z.object({
        diff: z.string(),
      }),
      handler: async ({ diff }, ctx) => {
        // 启动子代理
        const result = await ctx.subagent.spawn({
          agent: 'security-agent',
          task: `审查以下 diff 的安全风险:\n\n${diff}\n\n按系统 prompt 格式返回 findings 数组`,
          systemPrompt: config.system_prompt,
          model: config.model,
          tools: config.tools,
          permissions: config.permissions,
          isolatedSession: config.isolated_session,
          maxIterations: config.max_iterations,
        })

        return result
      },
    })
  }
}
```

### 4.2 perf-agent & style-agent（类似结构）

```yaml
# agents/perf-agent/config.yaml
name: perf-agent
description: 性能分析子代理
model: sonnet

system_prompt: |
  你是 Performance Agent，专精性能瓶颈识别。

  ## 审查范围
  - N+1 查询问题
  - 同步阻塞调用
  - 大循环 / 大对象
  - 内存泄漏（未清理的监听器、定时器、引用）
  - 频繁 GC（短期大对象）
  - 网络请求未并发
  - 缺少缓存
  - 数据库索引缺失
  - 不必要的 deep clone

  ## 工具集
  - read_file / search_code
  - run_shell（受限于性能分析命令）

  ## 输出格式
  JSON 数组 + 每个 finding 包含：
  - severity: critical / warning / info
  - type: n_plus_one / blocking_io / memory_leak / ...
  - estimated_impact: 高/中/低
  - file, line, message, suggestion

tools:
  - read_file
  - search_code
  - run_shell
  - complexity_score       # 来自 pr-analyzer
```

```yaml
# agents/style-agent/config.yaml
name: style-agent
description: 代码风格子代理
model: gpt-5-mini  # 风格检查用便宜模型

system_prompt: |
  你是 Style Agent，专精代码风格与可读性。

  ## 审查范围
  - ESLint 规则
  - Prettier 格式
  - TypeScript 类型完整性（no-any / explicit-return）
  - 命名规范
  - 注释完整性（JSDoc / 内联）
  - 函数长度（< 50 行）
  - 文件长度（< 500 行）
  - 圈复杂度（< 10）
  - 重复代码

  ## 工具集
  - run_shell（lint 命令）
  - read_file
  - search_code

  ## 输出
  JSON 数组 + 每个 finding 是风格问题
```

## 🌐 5. MCP 配置

```json
// mcp-servers.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "jira": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-jira"],
      "env": {
        "JIRA_HOST": "https://my-org.atlassian.net",
        "JIRA_EMAIL": "${JIRA_EMAIL}",
        "JIRA_TOKEN": "${JIRA_TOKEN}"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}",
        "SLACK_TEAM_ID": "${SLACK_TEAM_ID}"
      }
    }
  }
}
```

## 🚀 6. 启动

```bash
# 单行启动（所有组件自动加载）
dsh --preset pr-reviewer --profile work --cwd ~/projects/my-app

# Web UI: http://localhost:3080
# 对话框输入：
# /review-pr 1234
# 或 /review-batch
```

## 🐳 7. Docker 部署

```dockerfile
# Dockerfile
FROM node:22.19-alpine

# 安装 dsh
RUN npm install -g @deepseek-ai/dsh pnpm

# 复制 Agent 包
WORKDIR /app
COPY . .

# 安装 plugins
RUN pnpm install --frozen-lockfile
RUN pnpm --filter "./plugins/*" run build

# 复制 preset
RUN mkdir -p /root/.config/dsh/presets
COPY preset.yaml /root/.config/dsh/presets/pr-reviewer/
COPY skills /root/.config/dsh/presets/pr-reviewer/skills
COPY mcp-servers.json /root/.config/dsh/

ENV DSH_PRESET=pr-reviewer
ENV NODE_ENV=production

EXPOSE 3080

CMD ["dsh", "web", "--host", "0.0.0.0", "--port", "3080"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  pr-reviewer:
    build: .
    ports:
      - "3080:3080"
    environment:
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - JIRA_EMAIL=${JIRA_EMAIL}
      - JIRA_TOKEN=${JIRA_TOKEN}
      - SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
    volumes:
      - pr-reviewer-data:/root/.local/share/dsh
    restart: unless-stopped

volumes:
  pr-reviewer-data:
```

```bash
# 一键启动
docker-compose up -d
open http://localhost:3080
```

## 📦 8. 分发给团队

### 8.1 Git 仓库（最简）

```bash
# 项目仓库
my-org/pr-reviewer-agent/
├─ preset.yaml
├─ skills/
├─ plugins/
├─ agents/
└─ README.md
```

```bash
# 团队成员安装
git clone git@github.com:my-org/pr-reviewer-agent.git
cd pr-reviewer-agent
./install.sh   # 自动 ln 到 ~/.config/dsh/presets/

# 启动
dsh --preset pr-reviewer --profile work
```

### 8.2 npm monorepo（专业）

```json
// package.json（monorepo 根）
{
  "name": "@my-org/pr-reviewer-agent",
  "private": true,
  "workspaces": [
    "plugins/*",
    "agents/*"
  ],
  "scripts": {
    "build": "pnpm -r run build",
    "publish": "pnpm -r publish --access public"
  }
}
```

```yaml
# pnpm-workspace.yaml
packages:
  - 'plugins/*'
  - 'agents/*'
```

```bash
# 发布
pnpm build
pnpm publish -r --access public

# 团队安装
dsh plugin install @my-org/dsh-plugin-review-store
dsh plugin install @my-org/dsh-plugin-pr-analyzer
dsh plugin install @my-org/dsh-plugin-team-policy
dsh plugin install @my-org/dsh-agent-security
dsh plugin install @my-org/dsh-agent-perf
dsh plugin install @my-org/dsh-agent-style

# preset 仍从 Git 仓库拉
git clone git@github.com:my-org/pr-reviewer-preset ~/.config/dsh/presets/pr-reviewer
```

### 8.3 完整 Docker 镜像（最强隔离）

```bash
# 构建镜像
docker build -t my-org/pr-reviewer:v1.2.0 .

# 推送到内部 registry
docker push registry.my-org.com/pr-reviewer:v1.2.0

# 团队成员
docker run -d -p 3080:3080 \
  -e DEEPSEEK_API_KEY=$KEY \
  -e GITHUB_TOKEN=$TOKEN \
  registry.my-org.com/pr-reviewer:v1.2.0
```

## 📊 9. 监控与运维

### 9.1 启用审计日志

```yaml
# preset.yaml
audit:
  log_path: ~/.local/share/dsh/audit/pr-reviewer.jsonl
  retention_days: 365
  redact_secrets: true
  events:
    - tool_call
    - shell_command
    - file_edit
    - api_call
    - subagent_spawn
    - mcp_call
```

### 9.2 Prometheus 暴露

```typescript
// plugins/review-store/src/metrics.ts
import { Counter, Histogram, register } from 'prom-client'

export const reviewsTotal = new Counter({
  name: 'pr_reviewer_reviews_total',
  help: 'Total reviews performed',
  labelNames: ['severity'],
})

export const reviewDuration = new Histogram({
  name: 'pr_reviewer_duration_seconds',
  help: 'Review duration',
  buckets: [1, 5, 10, 30, 60, 120],
})

// 在 tool handler 里：
reviewsTotal.inc({ severity: params.severity.critical > 0 ? 'has_critical' : 'clean' })
reviewDuration.observe(duration)
```

```typescript
// packages/server/src/routes/metrics.ts
fastify.get('/metrics', async (req, reply) => {
  reply.type('text/plain')
  return register.metrics()
})
```

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'pr-reviewer'
    static_configs:
      - targets: ['pr-reviewer.local:3080']
    metrics_path: /metrics
```

### 9.3 告警规则

```yaml
# alerts.yml
groups:
- name: pr-reviewer
  rules:
  - alert: HighCriticalFindings
    expr: rate(pr_reviewer_reviews_total{severity="has_critical"}[1h]) > 5
    annotations:
      summary: "PR Reviewer 发现大量严重问题"
  
  - alert: SlowReviews
    expr: histogram_quantile(0.95, pr_reviewer_duration_seconds_bucket) > 120
    annotations:
      summary: "95% 审查超过 2 分钟"
  
  - alert: TokenCostHigh
    expr: increase(pr_reviewer_token_cost_total[1d]) > 100
    annotations:
      summary: "单日 token 成本 > $100"
```

## 🧪 10. 测试

### 10.1 单元测试 Plugin

```typescript
// plugins/review-store/__tests__/store.test.ts
import { describe, it, expect, beforeEach } from 'vitest'
import { createTestContext } from '@harness/test-utils'
import ReviewStore from '../src/index'

describe('ReviewStore', () => {
  let ctx
  
  beforeEach(async () => {
    ctx = await createTestContext({
      plugins: [ReviewStore],
      config: { dbPath: ':memory:' },
    })
  })

  it('saves a review', async () => {
    const result = await ctx.tool.execute('save_review', {
      pr_number: 1234,
      pr_title: 'Test PR',
      author: 'alice',
      review: '## 🔴 Critical\n- issue 1',
      severity: { critical: 1, warning: 0, good: 0 },
    })

    expect(result).toContain('Review #1 saved')
  })

  it('lists recent reviews', async () => {
    await ctx.tool.execute('save_review', {
      pr_number: 1234,
      pr_title: 'Test',
      review: 'test',
      severity: { critical: 0, warning: 1, good: 0 },
    })

    const reviews = await ctx.tool.execute('list_recent_reviews', { limit: 10 })
    const parsed = JSON.parse(reviews as string)
    expect(parsed).toHaveLength(1)
  })
})
```

### 10.2 E2E 测试 Skill

```typescript
// tests/e2e/review-pr.test.ts
import { test, expect } from '@playwright/test'

test('review-pr skill works end-to-end', async ({ page }) => {
  await page.goto('http://localhost:3080')
  
  // 输入 /review-pr 命令
  await page.fill('[data-testid="message-input"]', '/review-pr 1234')
  await page.click('[data-testid="send"]')

  // 等到审查完成（最多 2 分钟）
  await page.waitForSelector('[data-testid="agent-done"]', { timeout: 120000 })

  // 验证输出包含预期 section
  const output = await page.textContent('[data-testid="agent-reply"]')
  expect(output).toContain('📋 PR 概览')
  expect(output).toContain('🎯 总结')
})
```

## 📖 11. 团队 README 模板

```markdown
<!-- README.md -->
# PR Reviewer Agent

> 自动化 PR Review Agent，集成 GitHub / Jira / Slack

## 快速开始

\`\`\`bash
# 一键安装
curl -fsSL https://raw.githubusercontent.com/my-org/pr-reviewer-agent/main/install.sh | bash

# 启动
dsh --preset pr-reviewer --profile work

# 打开 Web UI
open http://localhost:3080
\`\`\`

## 使用

### 审查单个 PR
\`\`\`
/review-pr 1234
\`\`\`

### 批量审查
\`\`\`
/review-batch label=needs-review
\`\`\`

## 配置

复制 `.env.example` 到 `.env` 并填入：
- `DEEPSEEK_API_KEY`
- `GITHUB_TOKEN`
- `JIRA_TOKEN`
- `SLACK_BOT_TOKEN`

## 故障排查

| 症状 | 解决方案 |
|---|---|
| GitHub MCP 401 | 检查 `GITHUB_TOKEN` 是否过期 |
| Slack 发送失败 | 检查 `SLACK_BOT_TOKEN` 权限 |
| SQLite 错误 | `rm ~/.local/share/dsh/reviews.db` 重置 |

## 贡献指南

修改 plugin / skill 后：
\`\`\`bash
pnpm test
pnpm build
git commit -m "feat: ..."
\`\`\`
```

## 🎯 12. 其他场景模板（速查）

修改 `preset.yaml` + `skills/` + `plugins/` 即可适配其他场景：

| 场景 | preset name | 主要插件 | Skills |
|---|---|---|---|
| **Data Analyst** | `data-analyst` | postgres / jupyter / plot | `/eda` `/hypothesis` `/viz` |
| **Security Audit** | `security-audit` | semgrep / snyk / gitleaks | `/audit` `/deps-check` |
| **SRE Incident** | `sre-incident` | prometheus / datadog / pagerduty | `/triage` `/mitigate` |
| **Onboarding** | `onboarding` | docs / explore | `/tour` `/setup` |
| **Code Review** | `pr-reviewer` | ← 本章 | ← 本章 |
| **Release Manager** | `release-manager` | github / npm / docker | `/release` `/rollback` |
| **Content Writer** | `content-writer` | web_search / image_gen | `/blog` `/seo` |

## 🎓 一句话总结

> **企业级 Agent = preset（场景）+ skills（命令）+ plugins（业务）+ MCP（外部）+ 子代理（协作）**。
>
> 五件套按需组合，从单个 PR Reviewer 到完整 DevOps Agent 平台，复杂度可控、可观测、可分发。

---

## 📚 完整示例代码

所有完整代码已展示在本章。如需 GitHub 仓库模板，可参考：
- 官方示例：github.com/deepseek-ai/deepseek-harness/tree/main/examples/agents
- 社区模板：github.com/topics/dsh-agent
