---
title: DeepSeek Harness Agent 高级实战
date: 2026-09-14  # date-auto-injected
---

# 🧠 DeepSeek Harness Agent 高级实战

> 本章聚焦 Harness 上的 **Agent 构建高级模式**：自定义工具、Skill 系统、MCP 接入、意图识别、RAG、单 Agent / 多 Agent 协作。全部基于 Harness 0.1.2-rc.1 API。

## 🧩 第 1 章：自定义工具定义

### 1.1 最简单的工具（Hello 级别）

```typescript
// ~/.config/dsh/plugins/my-greeter/index.ts
import { Service, Context } from 'cordis'
import { z } from 'zod'

export default class GreeterService extends Service {
  static Config = {
    name: { type: 'string', default: 'World' },
  }

  constructor(ctx: Context, private config: { name: string }) {
    super(ctx, 'greeter', true)
  }

  async start() {
    this.ctx.tool('greet', {
      description: '向某人打招呼',
      parameters: z.object({
        target: z.string().describe('打招呼对象'),
      }),
      handler: async ({ target }) => {
        return `你好，${target}！来自 ${this.config.name} 的问候。`
      },
    })
  }
}

declare module 'cordis' {
  interface Context {
    greeter: GreeterService
  }
}
```

### 1.2 工具返回结构化数据

```typescript
import { z } from 'zod'

async start() {
  this.ctx.tool('search_users', {
    description: '在用户表中搜索用户',
    parameters: z.object({
      query: z.string().describe('搜索关键字'),
      limit: z.number().min(1).max(100).default(10),
    }),
    handler: async ({ query, limit }) => {
      // 返回 JSON 数组，Harness 自动展示给 LLM
      const users = await db.query(
        'SELECT id, name, email FROM users WHERE name ILIKE ? LIMIT ?',
        [`%${query}%`, limit]
      )
      return JSON.stringify(users)
    },
  })
}
```

### 1.3 工具带副作用（写文件）

```typescript
import { writeFile, mkdir } from 'node:fs/promises'

this.ctx.tool('write_note', {
  description: '把笔记写到指定路径',
  parameters: z.object({
    path: z.string().describe('文件路径，相对工作目录'),
    content: z.string().describe('笔记内容'),
  }),
  handler: async ({ path, content }, ctx) => {
    // 安全检查：必须经过沙箱验证
    if (!ctx.sandbox.allowPath(path)) {
      throw new Error(`Path not allowed: ${path}`)
    }

    await mkdir(dirname(path), { recursive: true })
    await writeFile(path, content, 'utf-8')

    return `✓ Wrote ${content.length} bytes to ${path}`
  },
})
```

### 1.4 工具组合（高级工具调用其他工具）

```typescript
this.ctx.tool('code_review_and_fix', {
  description: '审查并自动修复代码',
  parameters: z.object({
    file: z.string(),
  }),
  handler: async ({ file }, ctx) => {
    // 1. 调用 Harness 内置工具
    const src = await ctx.tool.file_edit.read({ file })

    // 2. 用 LLM 分析
    const prompt = `审查这段代码:\n${src}\n\n只输出修复建议:`
    const review = await ctx.model.complete({
      prompt,
      model: 'sonnet',    // 用便宜模型
      temperature: 0.2,
    })

    // 3. 应用修复
    if (review.includes('FIX:')) {
      const fix = review.split('FIX:')[1].trim()
      await ctx.tool.file_edit.write({ file, content: fix })
      return '✓ Fixed: ' + fix
    }
    return 'No issues found'
  },
})
```

### 1.5 流式工具（长任务实时反馈）

```typescript
this.ctx.tool('long_running_task', {
  description: '长时间运行的任务，流式返回进度',
  parameters: z.object({ task_id: z.string() }),
  stream: true,                              // ← 标记为流式
  handler: async function* ({ task_id }, ctx) {
    yield { type: 'progress', percent: 0, msg: 'Starting...' }

    for (let i = 1; i <= 10; i++) {
      await sleep(1000)
      yield { type: 'progress', percent: i * 10, msg: `Step ${i}/10` }
    }

    const result = await fetchResult(task_id)
    yield { type: 'done', result }
  },
})
```

## 🎯 第 2 章：意图识别（Intent Recognition）

### 2.1 基于 LLM 的分类器

```typescript
// IntentService：识别用户消息属于哪个意图
export default class IntentService extends Service {
  static inject = ['model']

  async start() {
    this.ctx.tool('classify_intent', {
      description: '识别用户意图',
      parameters: z.object({
        message: z.string(),
        candidates: z.array(z.object({
          name: z.string(),
          description: z.string(),
          examples: z.array(z.string()),
        })),
      }),
      handler: async ({ message, candidates }) => {
        const prompt = `你是意图分类器。用户消息属于以下哪个意图？

${candidates.map((c, i) =>
  `${i+1}. ${c.name}\n   描述: ${c.description}\n   示例:\n${c.examples.map(e => `   - ${e}`).join('\n')}`
).join('\n\n')}

用户消息: "${message}"

只输出意图名称（${candidates.map(c => c.name).join(' | ')}），不要解释:`

        const intent = await this.ctx.model.complete({
          prompt,
          model: 'gpt5m',           // 用便宜模型
          max_tokens: 50,
          temperature: 0,
        })

        return intent.trim()
      },
    })
  }
}
```

### 2.2 注册意图

```typescript
// ~/.config/dsh/config.yaml
intents:
  - name: code_question
    description: 用户询问代码相关
    examples:
      - "这段代码是什么意思？"
      - "为什么这里用 useEffect？"
      - "帮我看看这个 bug"
    handler: code_assistant_agent

  - name: git_operation
    description: 用户要做 git 操作
    examples:
      - "提交代码"
      - "创建分支"
      - "push 一下"
    handler: git_skill

  - name: web_search
    description: 用户要查资料
    examples:
      - "搜一下 React 19 新特性"
      - "查文档"
    handler: web_search_skill

  - name: file_edit
    description: 用户要改文件
    examples:
      - "把 README.md 改一下"
      - "删除 test.js"
    handler: file_edit_skill

  - name: chitchat
    description: 闲聊
    examples:
      - "你好"
      - "今天天气"
    handler: small_talk_response
```

### 2.3 路由到不同 Agent

```typescript
// IntentRouterService
this.ctx.tool('route_user_message', {
  description: '路由用户消息到对应 Agent',
  parameters: z.object({ message: z.string() }),
  handler: async ({ message }, ctx) => {
    // 1. 识别意图
    const intent = await ctx.tool.intent.classify_intent({
      message,
      candidates: ctx.config.intents,
    })

    // 2. 路由
    const handler = ctx.config.intents.find(i => i.name === intent)?.handler

    switch (handler) {
      case 'code_assistant_agent':
        return ctx.subagent.spawn({
          model: 'sonnet',
          systemPrompt: '你是资深 code assistant',
          task: message,
        })
      case 'git_skill':
        return ctx.skill.run('commit', { message })
      case 'web_search_skill':
        return ctx.skill.run('web-search', { query: message })
      default:
        return ctx.model.complete({ prompt: message })
    }
  },
})
```

### 2.4 基于 Embedding 的相似度意图识别

```typescript
// 用向量相似度判断（适合候选意图多的场景）
export default class EmbeddingIntentService extends Service {
  static inject = ['model']

  async start() {
    this.ctx.tool('classify_intent_embed', {
      description: '基于 embedding 相似度的意图识别',
      parameters: z.object({
        message: z.string(),
      }),
      handler: async ({ message }, ctx) => {
        // 1. Embedding 用户消息
        const msgVec = await ctx.model.embed({ input: message })

        // 2. 与候选意图的示例做相似度
        const candidates = ctx.config.intents
        const exampleVecs = await ctx.model.embed({
          input: candidates.flatMap(c => c.examples),
        })

        // 3. 计算相似度 + 选最大
        const scores = candidates.map((c, ci) => ({
          name: c.name,
          score: maxSimilarity(msgVec, exampleVecs.slice(ci * c.examples.length, (ci+1) * c.examples.length)),
        }))

        const top = scores.sort((a, b) => b.score - a.score)[0]
        return top.score > 0.7 ? top.name : 'unknown'
      },
    })
  }
}
```

## 🤖 第 3 章：单 Agent 智能体构建

### 3.1 通用 Agent 模板

```typescript
// agents/general-assistant/index.ts
import { Service, Context } from 'cordis'
import { z } from 'zod'

export default class GeneralAssistantAgent extends Service {
  static inject = ['model', 'memory', 'tool']

  constructor(ctx: Context, private config) {
    super(ctx, 'agent.assistant', true)
  }

  async start() {
    this.ctx.tool('chat', {
      description: '通用对话（带工具调用 + 长期记忆）',
      parameters: z.object({
        message: z.string(),
        session_id: z.string().optional(),
      }),
      handler: async ({ message, session_id }, ctx) => {
        // 1. 加载历史记忆
        const history = await ctx.memory.load(session_id || 'default', {
          limit: 20,
        })

        // 2. 拼 messages
        const messages = [
          { role: 'system', content: this.systemPrompt() },
          ...history,
          { role: 'user', content: message },
        ]

        // 3. LLM 调用 + 工具循环
        let response = await ctx.model.chat({
          model: this.config.model,
          messages,
          tools: ctx.tool.listAvailable(),         // 所有可用工具
          tool_choice: 'auto',
        })

        // 4. 工具调用循环
        let maxIter = 10
        while (response.tool_calls && maxIter-- > 0) {
          const toolResults = []
          for (const call of response.tool_calls) {
            try {
              const r = await ctx.tool.execute(call.function.name, JSON.parse(call.function.arguments))
              toolResults.push({ tool_call_id: call.id, role: 'tool', content: r })
            } catch (e) {
              toolResults.push({ tool_call_id: call.id, role: 'tool', content: `Error: ${e.message}` })
            }
          }
          messages.push(response.choices[0].message)
          messages.push(...toolResults)

          response = await ctx.model.chat({ model: this.config.model, messages, tools: ctx.tool.listAvailable() })
        }

        // 5. 保存记忆
        const answer = response.choices[0].message.content
        await ctx.memory.save(session_id || 'default', {
          messages: [
            { role: 'user', content: message },
            { role: 'assistant', content: answer },
          ],
        })

        return answer
      },
    })
  }

  private systemPrompt() {
    return `你是通用 AI 助手，具备工具调用能力。

工具使用规则：
1. 优先使用工具获取实时数据，不要猜测
2. 工具调用失败时，向用户说明
3. 完成任务后用自然语言总结

当前时间: ${new Date().toISOString()}
`
  }
}
```

### 3.2 编程 Agent（带代码执行）

```typescript
// agents/coding-assistant/index.ts
export default class CodingAgent extends Service {
  static inject = ['model', 'tool.shell', 'tool.file_edit', 'tool.search']

  async start() {
    this.ctx.tool('code_task', {
      description: '执行编程任务（读文件、编辑、跑命令）',
      parameters: z.object({
        task: z.string(),
        cwd: z.string().default('.'),
      }),
      handler: async ({ task, cwd }, ctx) => {
        const systemPrompt = `你是编程助手。

工作目录: ${cwd}
可用工具: read_file, write_file, edit_file, run_cmd, search_code

工作流程：
1. 先搜索相关代码了解项目结构
2. 阅读相关文件
3. 制定修改方案（必要时跟用户确认）
4. 实施修改
5. 跑测试验证
6. 总结改动

输出风格：简洁、技术、可执行`

        return ctx.subagent.run({
          model: 'sonnet',
          systemPrompt,
          task,
          tools: ['read_file', 'write_file', 'edit_file', 'run_cmd', 'search_code'],
          cwd,
          max_iterations: 30,
        })
      },
    })
  }
}
```

### 3.3 研究 Agent（带 RAG）

```typescript
// agents/research-assistant/index.ts
export default class ResearchAgent extends Service {
  static inject = ['model', 'rag']

  async start() {
    this.ctx.tool('research', {
      description: '深度研究某个主题（基于知识库 + 联网搜索）',
      parameters: z.object({
        topic: z.string(),
        depth: z.enum(['shallow', 'medium', 'deep']).default('medium'),
      }),
      handler: async ({ topic, depth }, ctx) => {
        // 1. 查本地知识库
        const localResults = await ctx.rag.search({
          query: topic,
          top_k: depth === 'shallow' ? 3 : depth === 'medium' ? 8 : 15,
        })

        // 2. 联网补充
        const webResults = await ctx.tool.web_search({
          query: topic,
          limit: depth === 'shallow' ? 3 : 8,
        })

        // 3. 合并 + 总结
        const prompt = `主题: ${topic}

本地知识:
${localResults.map((r, i) => `[L${i+1}] ${r.content}`).join('\n')}

网络资料:
${webResults.map((r, i) => `[W${i+1}] ${r.title} - ${r.snippet}`).join('\n')}

请综合以上资料，写一份 ${depth === 'shallow' ? '简要' : depth === 'medium' ? '详细' : '深度'}的研究报告。
引用处用 [L1][W2] 标记。`

        const report = await ctx.model.complete({
          prompt,
          model: 'r1',         // 复杂任务用 R1
          max_tokens: 8000,
        })

        return report
      },
    })
  }
}
```

## 👥 第 4 章：多 Agent 协作

### 4.1 协作模式总览

```
┌────────────────────────────────────────────────────────┐
│  4 种主流模式                                          │
├────────────────────────────────────────────────────────┤
│  1. Supervisor：1 主 N 从（主代理调度）                │
│  2. Hierarchical：树形（多层管理）                    │
│  3. Sequential：流水线（上一个输出是下一个输入）      │
│  4. Peer：平等协作（互相消息 + 投票）                 │
└────────────────────────────────────────────────────────┘
```

### 4.2 Supervisor 模式（最常见）

```typescript
// agents/supervisor/index.ts
export default class SupervisorAgent extends Service {
  static inject = ['model', 'subagent']

  async start() {
    this.ctx.tool('orchestrate', {
      description: '主代理调度多个子任务',
      parameters: z.object({
        goal: z.string(),
      }),
      handler: async ({ goal }, ctx) => {
        // 1. 主代理拆解任务
        const planPrompt = `目标: ${goal}

请拆解为 3-7 个独立子任务，每个任务输出：
{
  "id": "task-1",
  "type": "code|research|review|test|docs",
  "agent": "coding-assistant|research-assistant|...",
  "task": "具体任务描述",
  "depends_on": []   // 依赖的其他任务 ID
}

只输出 JSON 数组:`

        const planJson = await ctx.model.complete({
          prompt: planPrompt,
          model: 'sonnet',
        })

        const tasks = JSON.parse(planJson)

        // 2. 拓扑排序（按依赖）
        const sorted = topoSort(tasks, t => t.depends_on)

        // 3. 并行执行独立任务
        const results = {}
        for (const wave of sorted) {           // wave = 一层无依赖任务
          const waveResults = await Promise.all(
            wave.map(async task => {
              const r = await ctx.subagent.spawn({
                agent: task.agent,
                task: task.task,
                model: task.type === 'code' ? 'sonnet' : 'gpt5m',
              })
              return [task.id, r]
            })
          )
          Object.assign(results, Object.fromEntries(waveResults))
        }

        // 4. 汇总
        const summary = await ctx.model.complete({
          prompt: `汇总以下子任务结果:\n${JSON.stringify(results, null, 2)}\n\n用一段话总结完成情况。`,
          model: 'sonnet',
        })

        return summary
      },
    })
  }
}
```

### 4.3 Hierarchical 模式（多层）

```
                  CEO Agent
                   │
        ┌──────────┼──────────┐
        │          │          │
   Manager A   Manager B   Manager C
        │          │          │
   Workers   Workers   Workers

   CEO：定战略
   Manager：分解 + 验收
   Worker：执行
```

```typescript
// 启动分层 Agent
const workflow = ctx.subagent.hierarchical({
  root: {
    agent: 'ceo-agent',
    task: '开发一个新功能',
  },
  levels: [
    {
      role: 'manager',
      children: [
        { role: 'worker', task: '设计 API' },
        { role: 'worker', task: '实现核心逻辑' },
        { role: 'worker', task: '写测试' },
      ],
    },
  ],
})
```

### 4.4 Sequential 流水线模式

```typescript
// 流水线：research → design → code → review
this.ctx.tool('pipeline', {
  description: '按顺序执行的流水线',
  parameters: z.object({ initial_input: z.string() }),
  handler: async ({ initial_input }, ctx) => {
    const stages = [
      { agent: 'research-agent', task_in: 'topic', task_out: 'findings' },
      { agent: 'design-agent',   task_in: 'findings', task_out: 'design_doc' },
      { agent: 'coding-agent',   task_in: 'design_doc', task_out: 'code_diff' },
      { agent: 'review-agent',   task_in: 'code_diff', task_out: 'review_notes' },
    ]

    let current = initial_input
    const trace = []

    for (const stage of stages) {
      const output = await ctx.subagent.run({
        agent: stage.agent,
        task: `输入: ${current}\n\n请完成 ${stage.task_in} → ${stage.task_out} 的转换`,
      })
      trace.push({ stage: stage.agent, input: current, output })
      current = output
    }

    return trace
  },
})
```

### 4.5 Peer 协作（Code Review 多 Agent 投票）

```typescript
// 3 个 reviewer 独立审查，少数服从多数
this.ctx.tool('multi_reviewer_review', {
  description: '多 reviewer 并行审查',
  parameters: z.object({ diff: z.string() }),
  handler: async ({ diff }, ctx) => {
    const reviewers = [
      { agent: 'security-reviewer', focus: '安全漏洞' },
      { agent: 'perf-reviewer',     focus: '性能问题' },
      { agent: 'style-reviewer',    focus: '代码风格' },
    ]

    // 并行跑
    const reviews = await Promise.all(
      reviewers.map(async r => ({
        ...r,
        comments: await ctx.subagent.run({
          agent: r.agent,
          task: `审查 diff，重点关注 ${r.focus}:\n\n${diff}`,
        }),
      }))
    )

    // 投票汇总
    const severityCounts = reviews.reduce((acc, r) => {
      const matches = r.comments.match(/🔴|🟡|🟢/g) || []
      matches.forEach(s => acc[s] = (acc[s] || 0) + 1)
      return acc
    }, {})

    return {
      reviews,
      summary: severityCounts,
      consensus: severityCounts['🔴'] > 0 ? 'HAS_ISSUES' : 'PASS',
    }
  },
})
```

## 🔌 第 5 章：MCP 接入

### 5.1 MCP 基础概念

```
MCP（Model Context Protocol）= 模型上下文协议
让 Agent 能连接外部工具/数据源。
Harness 通过 MCP Server 子进程连接。
```

### 5.2 配置文件

```json
// ~/.config/dsh/mcp-servers.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxx"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/mydb"
      }
    },
    "puppeteer": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-xxx",
        "SLACK_TEAM_ID": "T1234567"
      }
    }
  }
}
```

### 5.3 列出可用 MCP 工具

```bash
dsh mcp list

# Output:
# SERVER       TOOLS                          STATUS
# github       24 tools (PR/Issue/Repo)       connected
# filesystem   8 tools                        connected
# postgres     6 tools (query/explain)        connected
# puppeteer    4 tools (screenshot/nav)       connected
# slack        12 tools                       disconnected (auth failed)
```

### 5.4 在 Skill 中使用 MCP

```yaml
# ~/.config/dsh/skills/code-search-github.md
---
name: code-search-github
description: 在 GitHub 上搜索公司内部代码
mode: standard
---

# /code-search-github Skill

工具：mcp.github.search_code

参数：
- query: 搜索字符串
- org: GitHub org（默认当前用户的所有 org）

示例对话：
  用户: "/code-search-github auth login"
  Harness:
    1. 调 mcp.github.search_code(query="auth login org:my-company")
    2. 返回 top 10 个匹配文件
    3. 用户点开看完整内容
```

### 5.5 自定义 MCP Server

```typescript
// mcp-servers/my-internal-tools/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js'

const server = new Server({
  name: 'my-internal-tools',
  version: '0.1.0',
}, {
  capabilities: { tools: {} },
})

// 注册工具
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'internal_search',
      description: '搜索公司内部 wiki',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string' },
          limit: { type: 'number', default: 10 },
        },
      },
    },
    {
      name: 'jira_create_ticket',
      description: '创建 Jira 工单',
      inputSchema: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          description: { type: 'string' },
          priority: { type: 'string', enum: ['Low', 'Medium', 'High'] },
        },
        required: ['title'],
      },
    },
  ],
}))

// 处理工具调用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  switch (request.params.name) {
    case 'internal_search':
      const results = await callInternalSearch(request.params.arguments)
      return { content: [{ type: 'text', text: JSON.stringify(results) }] }
    case 'jira_create_ticket':
      const issue = await createJiraIssue(request.params.arguments)
      return { content: [{ type: 'text', text: JSON.stringify(issue) }] }
  }
})

// 启动
const transport = new StdioServerTransport()
server.connect(transport)
```

```json
// 加到 mcp-servers.json
{
  "mcpServers": {
    "internal": {
      "command": "node",
      "args": ["./mcp-servers/my-internal-tools/dist/index.js"],
      "env": {
        "INTERNAL_API_KEY": "xxx"
      }
    }
  }
}
```

## 🎓 第 6 章：Skill 系统深度使用

### 6.1 Skill 结构

```yaml
# ~/.config/dsh/skills/my-skill/SKILL.md
---
name: deploy-staging
description: 一键部署到 staging 环境
mode: standard
tools:
  - shell
  - file_edit
inputs:
  - name: service
    type: string
    required: true
    description: 服务名
  - name: version
    type: string
    required: false
    default: latest
outputs:
  - type: url
    description: 部署后的访问 URL
---

# /deploy-staging Skill

## 步骤

1. 检查 git status
   ```bash
   git status
   ```
   如果不干净，提示用户先 commit。

2. 跑测试
   ```bash
   npm test
   ```
   失败则中止。

3. 部署
   ```bash
   ./scripts/deploy.sh {{service}} {{version}}
   ```

4. 健康检查
   ```bash
   curl https://{{service}}-staging.example.com/health
   ```

## 输出

部署 URL: https://{{service}}-staging.example.com
```

### 6.2 Skill 注册为命令

```bash
# 自动注册到 dsh 命令
dsh /deploy-staging my-service v1.2.3

# 带交互输入
dsh /deploy-staging
> Service: my-service
> Version (default: latest): v1.2.3
```

### 6.3 多 Skill 组合（Workflow）

```yaml
# ~/.config/dsh/skills/release-workflow.md
---
name: release
description: 完整发布流程（测试 → 部署 → 通知）
mode: standard
---

# /release Skill

组合调用：
1. /test                          # 跑测试
2. /build                         # 打包
3. /deploy-staging                # 部署 staging
4. /smoke-test                    # 烟测
5. /deploy-prod                   # 部署生产
6. /changelog                     # 更新日志
7. /notify-slack                  # 通知 Slack

任一步失败，中止流程并回滚。
```

### 6.4 Skill 上下文管理

```typescript
// Skill 之间的状态共享
this.ctx.tool('run_skill_with_context', {
  description: '运行 Skill 并保留上下文',
  parameters: z.object({
    skill_name: z.string(),
    inputs: z.record(z.any()),
  }),
  handler: async ({ skill_name, inputs }, ctx) => {
    const sessionId = `skill-${Date.now()}`

    // 1. 写输入到上下文
    await ctx.memory.save(sessionId, {
      role: 'user',
      content: `Run with inputs: ${JSON.stringify(inputs)}`,
    })

    // 2. 执行 Skill
    const result = await ctx.skill.run(skill_name, {
      ...inputs,
      session_id: sessionId,           // 复用会话
    })

    // 3. 记录到 Skill 历史
    await ctx.memory.tag(sessionId, `skill:${skill_name}`)

    return result
  },
})
```

### 6.5 Skill 自动选择（基于描述）

```typescript
// Harness 自动根据用户消息匹配最合适的 Skill
this.ctx.tool('auto_skill_router', {
  description: '根据消息自动路由 Skill',
  parameters: z.object({ message: z.string() }),
  handler: async ({ message }, ctx) => {
    const skills = await ctx.skill.list()
    const prompt = `用户消息: "${message}"

可用 Skills:
${skills.map((s, i) => `${i+1}. ${s.name} - ${s.description}`).join('\n')}

最匹配的 Skill 编号（只输出数字）:`

    const skillIdx = parseInt(await ctx.model.complete({
      prompt, model: 'gpt5m', temperature: 0,
    }))

    const selectedSkill = skills[skillIdx - 1]
    return ctx.skill.run(selectedSkill.name, { message })
  },
})
```

## 📚 第 7 章：RAG 接入

### 7.1 Harness RAG 插件架构

```
┌────────────────────────────────────────┐
│         User Query                     │
└────────────┬───────────────────────────┘
             ▼
┌────────────────────────────────────────┐
│  Embedding（@harness/model）           │
│  - bge-m3 / text-embedding-3 / cohere  │
└────────────┬───────────────────────────┘
             ▼
┌────────────────────────────────────────┐
│  Vector DB                             │
│  - chromadb / milvus / pgvector / faiss│
└────────────┬───────────────────────────┘
             ▼
┌────────────────────────────────────────┐
│  Re-rank（可选）                       │
│  - bge-reranker / cohere-rerank        │
└────────────┬───────────────────────────┘
             ▼
┌────────────────────────────────────────┐
│  LLM Generation（@harness/model）      │
└────────────────────────────────────────┘
```

### 7.2 配置文件

```yaml
# ~/.config/dsh/config.yaml
rag:
  enabled: true
  default_provider: chromadb

  providers:
    chromadb:
      type: chromadb
      path: ~/.local/share/dsh/rag/chroma
      collection: default

    milvus:
      type: milvus
      host: localhost
      port: 19530
      collection: default

    pgvector:
      type: pgvector
      url: postgresql://user:pass@localhost:5432/ragdb

  embedding:
    default: bge-m3
    providers:
      bge-m3:
        type: ollama
        model: bge-m3
      text-embedding-3:
        type: openai
        model: text-embedding-3-small
      cohere:
        type: cohere
        api_key: xxx

  rerank:
    enabled: true
    model: bge-reranker-v2-m3

  ingestion:
    chunk_size: 512
    chunk_overlap: 64
    splitters: [markdown, code, html]
```

### 7.3 索引文档

```bash
# 命令行索引
dsh rag index ~/projects/my-app/docs

# 增量更新
dsh rag index --watch ~/projects/my-app/docs

# 看索引状态
dsh rag status
# Documents: 1247
# Chunks: 5832
# Last indexed: 2026-09-14 12:34:56
```

### 7.4 自定义 RAG 工具

```typescript
// 业务专用 RAG
export default class DocsRAGService extends Service {
  static inject = ['rag', 'model']

  async start() {
    this.ctx.tool('ask_docs', {
      description: '基于公司文档库问答',
      parameters: z.object({
        question: z.string(),
        top_k: z.number().default(5),
      }),
      handler: async ({ question, top_k }, ctx) => {
        // 1. 检索
        const chunks = await ctx.rag.search({
          query: question,
          top_k,
        })

        // 2. 拼 prompt（缓存友好）
        const systemPrompt = `你是公司内部知识库助手。

参考资料:
${chunks.map((c, i) => `[${i+1}] (来源: ${c.source})\n${c.content}`).join('\n\n')}

规则：
1. 仅基于参考资料回答
2. 不确定时回答"未在文档中找到"
3. 引用用 [1][2] 标记`

        // 3. 生成
        const answer = await ctx.model.complete({
          prompt: `问题: ${question}`,
          system: systemPrompt,
          model: 'sonnet',
          max_tokens: 2000,
        })

        return {
          answer,
          citations: chunks.map(c => ({ source: c.source, score: c.score })),
        }
      },
    })
  }
}
```

### 7.5 高级 RAG 模式

#### 7.5.1 Hybrid Search（向量 + BM25）

```typescript
async hybridSearch(query: string, top_k: number) {
  const [vectorResults, bm25Results] = await Promise.all([
    this.ctx.rag.vector_search({ query, top_k: top_k * 2 }),
    this.ctx.rag.bm25_search({ query, top_k: top_k * 2 }),
  ])

  // RRF 融合
  const rrf = (results, k = 60) =>
    results.reduce((acc, r, i) => {
      acc[r.id] = (acc[r.id] || 0) + 1 / (k + i + 1)
      return acc
    }, {})

  const scores = {
    ...rrf(vectorResults),
    ...rrf(bm25Results),
  }

  return Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, top_k)
    .map(([id]) => [...vectorResults, ...bm25Results].find(r => r.id === id))
}
```

#### 7.5.2 Multi-hop RAG（多跳推理）

```typescript
async multiHop(question: string, max_hops = 3) {
  let context = ''
  let currentQ = question

  for (let hop = 1; hop <= max_hops; hop++) {
    const results = await this.ctx.rag.search({ query: currentQ, top_k: 5 })
    context += `\n\n=== Hop ${hop} ===\n${results.map(r => r.content).join('\n')}`

    // 让 LLM 判断是否还需要继续
    const needMore = await this.ctx.model.complete({
      prompt: `问题: ${question}\n当前上下文: ${context}\n\n还需要更多信息吗？(yes/no)`,
      model: 'gpt5m',
    })

    if (!needMore.toLowerCase().includes('yes')) break

    currentQ = await this.ctx.model.complete({
      prompt: `基于已有上下文，下一步应该查什么？\n${context}`,
      model: 'gpt5m',
    })
  }

  return this.ctx.model.complete({
    prompt: `问题: ${question}\n上下文: ${context}\n\n回答:`,
    model: 'sonnet',
  })
}
```

#### 7.5.3 GraphRAG（图增强 RAG）

```typescript
// 索引时提取实体关系
async indexWithGraph(docs: Document[]) {
  for (const doc of docs) {
    const triples = await this.ctx.model.complete({
      prompt: `从这段文本提取实体关系三元组 (subject, predicate, object):\n${doc.content}\n\n输出 JSON 数组:`,
      model: 'gpt5m',
    })

    const parsed = JSON.parse(triples)
    await this.ctx.graph.addTriples(parsed, { source: doc.path })
  }
}

// 查询时用图遍历
async graphRAG(question: string) {
  // 1. 提取问题中的实体
  const entities = await this.extractEntities(question)

  // 2. 图遍历
  const subgraph = await this.ctx.graph.expand(entities, depth: 2)

  // 3. 子图 → 文本
  const context = subgraphToText(subgraph)

  return this.ctx.model.complete({
    prompt: `问题: ${question}\n图谱信息: ${context}\n\n回答:`,
    model: 'sonnet',
  })
}
```

## 🛠️ 第 8 章：工具定义最佳实践

### 8.1 工具描述规范

```typescript
// ✅ 好的工具定义
this.ctx.tool('search_repos', {
  description: `在 GitHub 上搜索仓库。

适用场景：用户想找开源项目、了解某技术生态。
返回：仓库名、描述、star 数、最后更新时间。

示例：
- "搜一下 React 状态管理库" → 找高 star 仓库
- "找下 Kafka 客户端" → 匹配 Java/Python/Go`,

  parameters: z.object({
    query: z.string().min(2).describe('搜索关键字（必填，至少 2 字符）'),
    language: z.enum(['JavaScript', 'Python', 'Go', 'Rust', 'Java']).optional(),
    min_stars: z.number().min(0).default(100).describe('最少 star 数（默认 100）'),
    sort: z.enum(['stars', 'updated', 'forks']).default('stars'),
  }),

  handler: async ({ query, language, min_stars, sort }) => {
    // 实现
  },
})

// ❌ 不好的工具定义
this.ctx.tool('search', {
  description: '搜索',                          // 太模糊
  parameters: z.object({ q: z.string() }),     // q 不清晰
})
```

### 8.2 工具错误处理

```typescript
this.ctx.tool('robust_api_call', {
  description: '调用外部 API（带重试 + 错误分类）',
  parameters: z.object({ endpoint: z.string() }),
  handler: async ({ endpoint }, ctx) => {
    try {
      const resp = await fetch(endpoint, {
        signal: AbortSignal.timeout(10000),    // 10s 超时
      })

      if (resp.status === 429) {
        const retryAfter = parseInt(resp.headers.get('Retry-After') || '60')
        return JSON.stringify({
          error: 'rate_limited',
          message: `API 限流，${retryAfter}s 后重试`,
          retry_after: retryAfter,
        })
      }

      if (!resp.ok) {
        return JSON.stringify({
          error: 'http_error',
          status: resp.status,
          message: await resp.text(),
        })
      }

      return await resp.text()

    } catch (e) {
      if (e.name === 'AbortError') {
        return JSON.stringify({ error: 'timeout', message: '请求超时（10s）' })
      }
      return JSON.stringify({ error: 'network', message: e.message })
    }
  },
})
```

### 8.3 工具权限分级

```typescript
// 工具分级：只读 / 写 / 危险
this.ctx.tool('file_read', {
  description: '读文件（只读，无须确认）',
  risk_level: 'read_only',
  handler: readFileImpl,
})

this.ctx.tool('file_write', {
  description: '写文件（需用户确认）',
  risk_level: 'write',
  handler: writeFileImpl,
})

this.ctx.tool('shell_run', {
  description: '执行 shell 命令（危险，需显式确认 + 命令白名单）',
  risk_level: 'dangerous',
  handler: shellImpl,
})

this.ctx.tool('git_push', {
  description: 'git push（危险，必须显式确认）',
  risk_level: 'dangerous',
  required_permission: 'git:push',
  handler: gitPushImpl,
})
```

### 8.4 工具复用与组合

```typescript
// 工具 = 单一职责
// 复杂任务 = 多个工具组合

// ✅ 推荐：每个工具做一件事
ctx.tool('read_file', { ... })        // 只读
ctx.tool('write_file', { ... })       // 只写
ctx.tool('search_code', { ... })      // 只搜

// 业务复杂工具 = 组合原子工具
ctx.tool('refactor_function', {
  description: '重构函数（组合 read + write + run）',
  handler: async ({ function_name }, ctx) => {
    const usages = await ctx.tool.search_code({ query: function_name })
    const source = await ctx.tool.read_file({ path: usages[0].file })

    const refactored = await ctx.model.complete({
      prompt: `重构函数 ${function_name}:\n${source}`,
    })

    await ctx.tool.write_file({ path: usages[0].file, content: refactored })
    return 'Done'
  },
})
```

### 8.5 工具调试技巧

```typescript
// 启用调试日志
this.ctx.tool('my_tool', {
  description: '...',
  parameters: ...,
  handler: async (params, ctx) => {
    ctx.logger.debug('my_tool called', { params })

    const t0 = Date.now()
    try {
      const result = await doWork(params)
      ctx.logger.debug('my_tool success', { duration_ms: Date.now() - t0 })
      return result
    } catch (e) {
      ctx.logger.error('my_tool failed', { error: e.message, stack: e.stack })
      throw e
    }
  },
})

// 查看日志
// dsh web --log-level debug
// 或 ~/.local/share/dsh/logs/dsh.log
```

## 🧪 第 9 章：测试 Agent / Skill / Tool

### 9.1 单元测试工具

```typescript
// plugins/my-plugin/__tests__/tool.test.ts
import { describe, it, expect } from 'vitest'
import { createTestContext } from '@harness/test-utils'
import MyService from '../src/index'

describe('my_tool', () => {
  it('returns greeting', async () => {
    const ctx = await createTestContext({ plugins: [MyService] })
    const result = await ctx.tool.execute('my_tool', { target: 'Alice' })
    expect(result).toBe('Hello, Alice!')
  })

  it('handles invalid input', async () => {
    const ctx = await createTestContext({ plugins: [MyService] })
    await expect(
      ctx.tool.execute('my_tool', { target: '' })
    ).rejects.toThrow('target cannot be empty')
  })
})
```

### 9.2 Agent E2E 测试

```typescript
// e2e/agent.test.ts
import { test, expect } from '@playwright/test'

test('research agent answers correctly', async ({ page }) => {
  await page.goto('http://localhost:3080')

  await page.fill('[data-testid="message-input"]', 'DeepSeek-V3 用了什么注意力机制？')
  await page.click('[data-testid="send"]')

  await page.waitForSelector('[data-testid="agent-reply"]')

  const reply = await page.textContent('[data-testid="agent-reply"]')
  expect(reply).toContain('MLA')
  expect(reply).toContain('Multi-head Latent Attention')
})
```

### 9.3 跑测试

```bash
# 单元测试
dsh test plugins/my-plugin

# E2E
dsh test:e2e

# 覆盖率
dsh test --coverage
```

## 🎁 第 10 章：完整实战项目（融合所有）

### 项目：内部知识库 + 工单自动化系统

**目标**：员工能用 Harness 自动查文档 + 创建/查 Jira ticket + 通知 Slack

**架构**：

```
┌────────────┐
│ 员工对话   │ 用户："上次那个支付失败的 bug 怎么修的？"
└─────┬──────┘
      ▼
┌────────────────────────────────────────────┐
│  Intent Router                              │
│  - classify_intent: research | ticket | ... │
└─────┬───────────────────────────────────────┘
      │
      ├─ intent=research ──────────► DocsRAG Agent ──► RAG 工具
      │
      ├─ intent=ticket ────────────► Ticket Agent ──► Jira MCP
      │
      └─ intent=code_question ────► Coding Agent ──► 文件工具

      ▼
┌────────────────────────────────────────────┐
│  Skill: /search-and-ticket                  │
│  - search_docs + jira_create + slack_notify │
└────────────────────────────────────────────┘
```

**实现步骤**：

1. 装插件
```bash
dsh plugin install dsh-plugin-jira dsh-plugin-slack dsh-plugin-rag
```

2. 配 RAG
```yaml
# ~/.config/dsh/config.yaml
rag:
  default_provider: chromadb
  embedding:
    default: text-embedding-3-small
```

3. 索引文档
```bash
dsh rag index ~/company/wiki
dsh rag index ~/company/runbooks
```

4. 配 MCP
```json
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-jira"],
      "env": {
        "JIRA_HOST": "https://company.atlassian.net",
        "JIRA_TOKEN": "xxx"
      }
    },
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": { "SLACK_BOT_TOKEN": "xxx" }
    }
  }
}
```

5. 注册 Skill
```yaml
# ~/.config/dsh/skills/search-and-ticket.md
---
name: search-and-ticket
description: 搜文档 + 自动建 Jira ticket + 通知 Slack
mode: standard
---

# /search-and-ticket Skill

输入: 问题描述

流程:
1. ask_docs(question) → 找相关 runbook
2. （用户确认后）jira_create_issue(title=runbook, ...)
4. slack_notify(channel=dev, text=新 ticket)
5. 输出: 文档链接 + ticket URL
```

6. 启动
```bash
dsh web --profile=work --cwd ~/company-workspace
```

7. 对话测试
```
用户: "上次生产数据库连不上是怎么排查的？"
Harness:
  1. classify_intent → research
  2. ask_docs("数据库连不上 排查") → 找到 runbook
  3. 输出: "在 wiki/db-runbook.md 第 3 节..."

用户: "顺便帮我建个 ticket 跟踪"
Harness:
  1. jira_create_issue(title="数据库连接问题排查", ...)
  2. slack_notify(#dev, "新 ticket ENG-1234")
  3. 输出: "✓ Ticket ENG-1234 已创建，已通知 #dev"
```
