---
title: DeepSeek Harness 实战教程
date: 2026-09-14  # date-auto-injected
---

# 🎯 DeepSeek Harness 实战教程

> 9 个生产级实战场景：每个都附可复制的 Harness 对话 / Skill / 插件配置。

## 🍜 实战 1：让 Harness 给开源项目提 PR

### 场景

```
给 github.com/facebook/react 提一个文档修正的 PR。
```

### 完整流程

```bash
# 1. 克隆项目到本地
git clone https://github.com/facebook/react.git
cd react

# 2. 启动 Harness（带 work profile）
dsh web --profile work --cwd .

# 3. 在 Web UI 输入：
#   "README.md 中第 42 行说 React 19 已经发布，
#    实际最新稳定版是 19.0.1，请帮我提一个 PR 修正版本号。
#    先 fork 到我的账号（panxin904），再创建分支 fix/readme-version，
#    修改后发 PR。"
```

### Harness 自动执行的步骤

```
✓ fork react → panxin904/react
✓ git remote add fork https://github.com/panxin904/react.git
✓ git checkout -b fix/readme-version
✓ file_edit README.md (修正版本号)
✓ /commit (生成 Conventional Commits message)
✓ git push fork fix/readme-version
✓ gh pr create (用 gh CLI 创建 PR)
✓ 输出 PR URL 给用户
```

### 复盘与定制

```yaml
# 复用此流程：保存为 ~/.config/dsh/skills/contribute-pr.md
---
name: contribute-pr
description: 给开源项目提 PR 的标准流程
mode: standard
---

# /contribute-pr Skill

输入参数：
- upstream: 原仓库（user/repo）
- description: PR 描述

流程：
1. 检查是否已 fork（没有则 fork）
2. 创建分支 fix/<description>
4. 让用户输入修改内容
5. /commit + push
6. 创建 PR
```

## 🐛 实战 2：Debug 一个 CI 失败

### 场景

```
GitHub Actions 跑 npm test 失败，Harness 帮分析日志。
```

### 操作

```bash
# 在 CI 失败的项目根目录
dsh web --cwd /Users/me/my-project

# 对话框输入：
#   "我刚 push 的 commit 触发了 GitHub Actions 失败。
#    帮我：1) 拉最新日志 2) 找出失败原因 3) 给出修复建议"
```

### Harness 自动步骤

```
1. shell: gh run list --limit 1 (找最新 run)
2. shell: gh run view <run-id> --log-failed (拉失败日志)
3. file_search: 找失败相关的源码
4. 分析 + 给出修复方案
5. （可选）直接修复 + commit
```

### 复用为 Skill

```yaml
# ~/.config/dsh/skills/debug-ci.md
---
name: debug-ci
description: 诊断 GitHub Actions 失败
mode: standard
---

# /debug-ci Skill

1. gh run list --limit 1 --json databaseId,status,conclusion
2. 取最新失败的 run ID
3. gh run view <id> --log-failed
4. 分析 + 输出
   - 失败 job 名
   - 失败步骤
   - 错误信息
   - 推测根因
   - 修复建议
5. （用户确认后）file_edit 修复 + commit
```

## 🔄 实战 3：批量迁移 50 个文件的 import 路径

### 场景

```
src/ 下有 50 个文件 import "old-lib"，
要批量改成 "new-lib"，同时加 type hint。
```

### 用 PTC 模式一键搞定

```bash
dsh --mode ptc

# 对话框：
#   "src/ 下所有 *.ts 文件 import "old-lib" 改成 import { X } from "new-lib"，
#    其中 X 对应 old-lib 的默认导出。完成后跑 npm run build 验证。"
```

### Harness 生成的 PTC 代码

```typescript
import { glob } from '@harness/tools/file'
import { readFile, writeFile } from '@harness/tools/file'

const files = await glob('src/**/*.ts')
let changed = 0

for (const file of files) {
  const src = await readFile(file)
  const updated = src
    .replace(/import\s+(\w+)\s+from\s+["']old-lib["']/g,
             'import { $1 } from "new-lib"')

  if (updated !== src) {
    await writeFile(file, updated)
    changed++
  }
}

console.log(`✓ Modified ${changed} files`)

// 验证
const { exec } = await import('node:child_process')
await exec('npm run build')
```

### 相比标准模式的优势

```
标准模式：50 次 file_edit 调用，可能漏、可能错
PTC 模式：一次性代码 + 验证，零遗漏
```

## 🌐 实战 4：用 Harness + MCP 连接 Jira

### 场景

```
开发流程：Harness 改完代码 → 自动创建 Jira ticket 关联
```

### 配置 MCP Server

```json
// ~/.config/dsh/mcp-servers.json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-jira"],
      "env": {
        "JIRA_HOST": "https://company.atlassian.net",
        "JIRA_EMAIL": "you@company.com",
        "JIRA_TOKEN": "ATATT3xFfGF0..."
      }
    }
  }
}
```

### 在 Harness 中使用

```
用户："把刚才改的 auth/login.ts 关联到 Jira ticket ENG-1234，
       并评论 'fixed in PR #456'"
```

### Harness 自动调用

```
MCP tool: jira.add_comment
{
  "ticket": "ENG-1234",
  "comment": "fixed in PR #456"
}
```

## 📝 实战 5：用 Skill 自动生成 commit message

### 场景

```
改完代码，commit message 要符合 Conventional Commits。
Harness 自动分析 diff → 生成规范 message。
```

### 启用 /commit Skill

```bash
# 改完代码后：
dsh /commit

# Harness 自动：
# 1. git diff --staged
# 2. 分析改动类型（feat/fix/refactor/docs/test/chore）
# 3. 分析 scope（影响哪个模块）
# 4. 生成 message（首行 ≤72 字）
# 5. 显示给用户确认 → git commit
```

### 输出示例

```
✓ Analyzing staged changes...
✓ Files: src/auth/login.ts, src/auth/login.test.ts
✓ Type: feat (new feature)
✓ Scope: auth
✓ Description: "add remember-me checkbox to login form"

Proposed:
────────────────────────────────────
feat(auth): add remember-me checkbox to login form

- Persist login for 30 days via httpOnly + secure cookie
- Add unit test for remember-me flow
- Update login form UI with checkbox

Refs: ENG-1234
────────────────────────────────────
[y/n/edit]: y

✓ Committed: feat(auth): add remember-me checkbox to login form
```

## 🧪 实战 6：用 Skill 补单元测试

### 场景

```
src/utils/string.ts 有 10 个函数，只有 5 个有测试。
跑 /test 让 Harness 自动补齐。
```

### 启用

```bash
dsh /test
```

### Harness 自动流程

```
1. file_search: src/utils/string.ts
2. file_search: src/utils/string.test.ts (5 个 test)
3. 分析未覆盖的 5 个函数
4. 为每个函数：
   - read 函数源代码
   - 生成 3-5 个 test case（正常/边界/异常）
   - 写入 test 文件
5. npm test 验证全绿
6. （如失败）自动迭代修复
```

### 输出

```
✓ Found 10 functions, 5 untested
✓ Generated tests for:
  - truncate(text, maxLen): 4 cases
  - slugify(text): 5 cases
  - camelToSnake(str): 3 cases
  - isValidEmail(email): 6 cases
  - formatCurrency(amount, currency): 4 cases
✓ All 22 tests passing (5 existing + 17 new)
```

## 📚 实战 7：用 Skill 自动写 CHANGELOG

### 场景

```
从 git log 提取最近 7 天 commits，自动写 CHANGELOG.md。
```

### Skill 定义

```yaml
# ~/.config/dsh/skills/changelog.md
---
name: changelog
description: 从 git log 自动生成 CHANGELOG
mode: standard
---

# /changelog Skill

输入（可选）：--since=7.days / --version=1.2.0

流程：
1. git log --since=<since> --no-merges
2. 按 Conventional Commits 分类（Features / Fixes / Breaking）
3. 合并到 CHANGELOG.md（顶部插入）
4. 提交
```

### 启用

```bash
dsh /changelog --since=7.days

# 输出：
# ✓ 17 commits analyzed
# ✓ CHANGELOG.md updated
#
# ## [Unreleased]
#
# ### Features
# - feat(auth): add remember-me checkbox (#456)
# - feat(api): add batch user lookup endpoint (#458)
#
# ### Bug Fixes
# - fix(ui): tooltip no longer hides on scroll (#455)
#
# ### BREAKING CHANGES
# - refactor(api)!: rename /v1/users to /v1/accounts (#457)
```

## 🏗️ 实战 8：搭建 Harness 自定义插件

### 场景

```
公司内部用 Linear 管 ticket，想让 Harness 能查/创建 Linear issue。
```

### 初始化插件

```bash
mkdir my-harness-plugin-linear
cd my-harness-plugin-linear
pnpm init

# 装依赖
pnpm add @harness/core cordis zod
pnpm add -D @harness/config typescript vitest
```

### 编写插件

```typescript
// src/index.ts
import { Context, Service, Schema } from 'cordis'
import { z } from 'zod'

const ConfigSchema = z.object({
  apiKey: z.string(),
  teamId: z.string(),
})

export class LinearService extends Service {
  static inject = ['model']      // 依赖 model 插件

  constructor(ctx: Context, private config: z.infer<typeof ConfigSchema>) {
    super(ctx, 'linear', true)
  }

  // 注册为 Harness 可调用的工具
  async start() {
    this.ctx.tool('linear_search_issues', {
      description: 'Search Linear issues by query',
      parameters: z.object({
        query: z.string().describe('Search query, e.g. "ENG-1234" or "bug"'),
        limit: z.number().default(10),
      }),
      handler: async ({ query, limit }) => {
        const res = await fetch('https://api.linear.app/graphql', {
          method: 'POST',
          headers: {
            'Authorization': this.config.apiKey,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: `
              query SearchIssues($q: String!) {
                issueSearch(query: $q, first: 10) {
                  nodes { id identifier title url state { name } }
                }
              }
            `,
            variables: { q: query },
          }),
        })
        const data = await res.json()
        return JSON.stringify(data.data.issueSearch.nodes)
      },
    })

    this.ctx.tool('linear_create_issue', {
      description: 'Create a new Linear issue',
      parameters: z.object({
        title: z.string(),
        description: z.string().optional(),
        priority: z.number().min(0).max(4).optional(),
      }),
      handler: async ({ title, description, priority }) => {
        // ... 类似实现
        return JSON.stringify({ id: '...', url: '...' })
      },
    })
  }
}

declare module 'cordis' {
  interface Context {
    linear: LinearService
  }
}

export default LinearService
```

### 配置文件

```typescript
// src/config.ts
import { defineConfig } from '@harness/config'
import LinearService from './index'

export default defineConfig({
  name: 'linear',
  schema: {
    apiKey: { type: 'string', required: true },
    teamId: { type: 'string', required: true },
  },
  service: LinearService,
})
```

### 发布到 npm

```bash
# package.json
{
  "name": "@my-org/dsh-plugin-linear",
  "version": "0.1.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "keywords": ["dsh-plugin", "deepseek-harness", "linear"],
  "peerDependencies": {
    "@harness/core": "^0.1.2",
    "cordis": "^2.0.0"
  }
}

# 发布
pnpm build
npm publish --access public
```

### 在 Harness 中安装

```bash
dsh plugin install @my-org/dsh-plugin-linear

# 配置 ~/.config/dsh/config.yaml
plugins:
  linear:
    apiKey: lin_api_xxxxxxxxxxxxx
    teamId: ENG

# 重启
dsh web
```

### 使用

```
用户："查 Linear 上所有 ENG-1234 相关的 issue"
Harness 调用 linear_search_issues { query: "ENG-1234" }
返回 JSON 列表给用户
```

## 🖥️ 实战 9：Harness 集成 IDE（VS Code 扩展）

### 概念

```
虽然 Harness 有 Web UI，但开发者更想直接在编辑器里用。
DeepSeek 官方提供了 VS Code 扩展 "Harness IDE"。
```

### 安装扩展

```
VS Code Marketplace 搜索 "DeepSeek Harness"
安装 → 自动检测 ~/.config/dsh/ 配置 → 启用
```

### 功能

```
- 侧边栏面板：直接在编辑器里开对话
- 内联 diff：编辑预览 + 应用/拒绝按钮
- 终端集成：在 VS Code 终端跑 dsh 命令
- 多文件编辑：跨文件同时改（用 subagent）
```

### 快捷键

```
Cmd + Shift + H     打开 Harness 面板
Cmd + Shift + I     当前文件提问
Cmd + Shift + R     接受当前 diff
Cmd + Shift + X     拒绝当前 diff
```

### 配置

```json
// VS Code settings.json
{
  "harness.path": "dsh",
  "harness.profile": "work",
  "harness.model": "claude-sonnet-4.5",
  "harness.autoApply": false,
  "harness.diffStyle": "side-by-side"
}
```
