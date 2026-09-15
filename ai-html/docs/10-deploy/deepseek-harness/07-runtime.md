---
title: dsh 运行时与 Agent 运行原理
date: 2026-09-15  # date-auto-injected
---

# ⚙️ dsh 运行时与 Agent 运行原理

> `dsh`（DeepSeek Harness 的命令行）**不是一个 chatbot，也不是 LLM API 包装器**。它是一个**本地 AI Agent 运行时环境**——为 Agent 提供完整的执行基础设施。本章从架构、启动、Agent Loop、工具调度、子代理、消息流、沙箱、状态管理、错误恢复等维度深入讲解 dsh 进程内部。

## 🎯 核心定位

```
┌──────────────────────────────────────────┐
│  传统 LLM 调用：用户 → LLM API → 文本       │
│                                          │
│  dsh 模式：                               │
│  用户 → dsh 进程                          │
│       └→ [消息循环 + 工具调度 + 记忆 + 沙箱] │
│       └→ Agent 输出                       │
│                                          │
│  dsh = Agent 的"操作系统"                 │
│  提供：进程管理 / 文件系统 / 工具集 /       │
│        权限 / 记忆 / 子进程 / 网络          │
└──────────────────────────────────────────┘
```

## 🏛️ 运行时架构总览

```
┌────────────────────────────────────────────────────────┐
│ dsh Process (单 Node.js 进程)                          │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Cordis Context（容器）                            │  │
│  │  ├ Plugin Loader    按依赖拓扑加载插件           │  │
│  │  ├ DI Registry      依赖注入                     │  │
│  │  ├ Event Bus        进程内事件总线               │  │
│  │  └ Lifecycle        start / stop 钩子            │  │
│  └─────────────────────────────────────────────────┘  │
│                          ↓                             │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Agent Runtime（核心运行时）                       │  │
│  │  ├ Message Loop      接收用户消息循环            │  │
│  │  ├ Tool Dispatcher   工具调度                     │  │
│  │  ├ Model Adapter     LLM 协议适配                 │  │
│  │  ├ Memory Manager    长期记忆                     │  │
│  │  ├ Sandbox           沙箱 + 权限检查              │  │
│  │  ├ Subagent Pool     子代理池                     │  │
│  │  └ Session / Checkpoint  会话 + 检查点            │  │
│  └─────────────────────────────────────────────────┘  │
│                          ↓                             │
│  ┌─────────────────────────────────────────────────┐  │
│  │ Plugins（插件层）                                 │  │
│  │  ├ @harness/model-*   OpenAI / Anthropic 适配     │  │
│  │  ├ @harness/tool-*    文件 / 搜索 / Shell / Web   │  │
│  │  ├ @harness/skill-*   /review / commit / test     │  │
│  │  └ 社区插件 (npm: dsh-plugin-*)                  │  │
│  └─────────────────────────────────────────────────┘  │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### 源码位置

```
packages/
├─ core/      @harness/core      Cordis 容器 + 插件加载
├─ cli/       @harness/cli      dsh 命令（bin/dsh）
├─ server/    @harness/server   Fastify HTTP + WebSocket
├─ web/       @harness/web      Vite + Vue 前端
├─ config/    @harness/config   配置文件 schema
├─ utils/     @harness/utils    工具函数
├─ tools/     @harness/tool-*   内置工具
├─ skills/    @harness/skill-*  内置技能
└─ models/    @harness/model-*  模型适配器
```

## 🚀 启动流程（从 `npx dsh web` 到可用）

```
1. npm / npx 解析入口
   → 找到 @deepseek-ai/dsh 包 → packages/cli/bin/dsh
2. Node.js 启动 main.ts
3. 加载配置文件
   ├ ~/.config/dsh/config.yaml          （全局）
   ├ ~/.config/dsh/profiles/<name>.yaml （profile，可选）
   └ .dsh/config.yaml                  （项目级，覆盖全局）
4. 实例化 Cordis Context
5. 按 plugin 依赖图拓扑排序
6. 依次加载插件：
   ├ @harness/core       基础容器
   ├ @harness/utils      工具函数
   ├ @harness/config     配置 schema 校验
   ├ @harness/model-*    模型适配（按 provider）
   ├ @harness/tool-*     工具集（file / shell / search / web）
   ├ @harness/skill-*    技能集（init / review / commit / test）
   ├ @harness/server     Fastify HTTP / WebSocket 服务
   ├ @harness/web        Vite + Vue 前端
   └ 第三方插件
7. 调用每个 plugin.start()
   ├ Model Adapter 建立连接（懒加载 API Key）
   ├ Tool Registry 注册到 ctx.tool
   ├ Skill Registry 注册到 ctx.skill
   ├ Server 启动 Fastify
   └ Web 启动 Vite dev server
8. Fastify 监听 3080
9. 浏览器访问 http://localhost:3080
```

### 关键代码片段（简化版）

```typescript
// packages/cli/src/main.ts
import { Context } from '@harness/core'
import { loadConfig } from '@harness/config'
import { ServerPlugin } from '@harness/server'
import { WebPlugin } from '@harness/web'

async function main() {
  // 1. 加载配置
  const config = await loadConfig()

  // 2. 创建 Cordis Context
  const ctx = new Context()

  // 3. 注册插件（按依赖顺序）
  ctx.plugin(ServerPlugin, config.server)
  ctx.plugin(WebPlugin, config.web)

  for (const pluginSpec of config.plugins) {
    ctx.plugin(await loadPlugin(pluginSpec))
  }

  // 4. 启动所有插件
  await ctx.start()

  // 5. 监听信号优雅关闭
  process.on('SIGTERM', () => ctx.stop())
}
```

## 🔄 Agent Loop 执行模型（核心中的核心）

一个用户消息会经历**循环**：

```
用户输入 "修复 src/auth/login.ts 第 42 行的 bug"
   │
   ▼
① 构建消息上下文
   ├ system prompt
   ├ 历史 messages（从 memory 加载）
   ├ 当前用户消息
   └ 可用工具列表（ctx.tool.listAvailable()）
   │
   ▼
② 调用 LLM
   POST {base_url}/v1/chat/completions
   { model, messages, tools, stream: true }
   │
   ▼
③ 解析 LLM 响应
   ├ 文本内容 → 输出给用户
   └ tool_calls → 进入工具调度
   │
   ▼ (如果有 tool_calls)
④ 工具调度（每个 tool_call 一次）
   ├ 沙箱权限检查
   ├ ctx.tool.execute(name, args)
   ├ 收集结果（成功 / 失败）
   └ 错误处理 + 重试
   │
   ▼
⑤ 工具结果回传给 LLM
   messages.push(tool_result)
   │
   └──────────────┐
                  ▼ （回到 ②，循环）
 直到 LLM 不再返回 tool_calls
   或 max_iterations 达到上限（默认 10-50）
   │
   ▼
⑥ 保存状态
   ├ 本轮 messages 写入 memory
   ├ 文件修改写入 checkpoint
   └ 写日志 + 审计
   │
   ▼
最终答案返回给用户
```

### 简化代码

```typescript
// packages/core/src/agent-loop.ts（简化版）
async function* agentLoop(ctx: Context, userMessage: string) {
  // ① 构建消息
  const messages = [
    { role: 'system', content: ctx.config.systemPrompt },
    ...(await ctx.memory.load(ctx.sessionId)),
    { role: 'user', content: userMessage },
  ]

  let iteration = 0
  const maxIter = ctx.config.maxIterations || 30

  while (iteration++ < maxIter) {
    // ② 调用 LLM
    const response = await ctx.model.chat({
      model: ctx.config.model,
      messages,
      tools: ctx.tool.listAvailable(),
      stream: true,
    })

    // 流式输出文本
    let fullContent = ''
    for await (const delta of response.contentStream) {
      fullContent += delta.text
      yield { type: 'content_delta', text: delta.text }
    }

    // ③ 解析 tool_calls
    const toolCalls = response.toolCalls || []

    if (toolCalls.length === 0) {
      // 没工具调用，结束
      yield { type: 'done', content: fullContent }
      return
    }

    // 把 assistant 消息加入历史
    messages.push({
      role: 'assistant',
      content: fullContent,
      tool_calls: toolCalls,
    })

    // ④ 并行执行所有 tool_calls
    const toolResults = await Promise.all(
      toolCalls.map(async call => {
        try {
          const result = await ctx.tool.execute(
            call.function.name,
            JSON.parse(call.function.arguments),
            { signal: ctx.abortController.signal }
          )
          return { tool_call_id: call.id, role: 'tool', content: result }
        } catch (e) {
          return { tool_call_id: call.id, role: 'tool', content: `Error: ${e.message}` }
        }
      })
    )

    // ⑤ 工具结果加入 messages
    messages.push(...toolResults)

    // ⑥ 检查点
    await ctx.checkpoint.save(ctx.sessionId, { messages, iteration })

    // 回到 ②
  }

  throw new Error(`Max iterations (${maxIter}) reached`)
}
```

## 🧰 工具调度机制

每个 `tool_call` 都经过这个流程：

```
LLM 返回 tool_use(name="read_file", args={"path": "..."})
   │
   ▼
Tool Dispatcher
   │
   ├ 1. 查找工具
   │ ctx.tool.registry.get("read_file")
   │
   ├ 2. 沙箱权限检查
   │     ├ 路径在 allow 列表？
   │     ├ 用户已确认（危险操作）？
   │     ├ 风险级别（read / write / dangerous）？
   │     └ 频率限制？
   │
   ├ 3. 包装为 Promise
   │     ├ timeout（可配置，默认 30s）
   │     └ AbortController（可取消）
   │
   ├ 4. 执行 handler(args, ctx)
   │     └ 异步执行
   │
   ├ 5. 收集结果
   │     ├ 成功 → JSON.stringify(result)
   │     └ 失败 → 抛 Error（带 stack）
   │
   └ 6. 结果回流 └ 作为 tool 角色消息回到 messages
```

### 工具调度简化代码

```typescript
// packages/core/src/tool-dispatcher.ts（简化版）
async function dispatchTool(
  ctx: Context,
  name: string,
  args: any,
  signal: AbortSignal
): Promise<string> {
  // 1. 查找
  const tool = ctx.tool.registry.get(name)
  if (!tool) {
    throw new Error(`Tool not found: ${name}`)
  }

  // 2. 沙箱检查
  const decision = await ctx.sandbox.check(name, args, tool.riskLevel)
  if (decision === 'deny') {
    throw new Error(`Permission denied: ${name}`)
  }
  if (decision === 'ask') {
    const userApproved = await ctx.ui.confirmRisk(name, args)
    if (!userApproved) {
      throw new Error(`User denied: ${name}`)
    }
  }

  // 3. 超时包装
  const timeoutMs = tool.timeout || ctx.config.toolTimeout || 30000
  const timeoutSignal = AbortSignal.timeout(timeoutMs)
  const combinedSignal = AbortSignal.any([signal, timeoutSignal])

  // 4. 执行
  try {
    const result = await tool.handler(args, { ctx, signal: combinedSignal })
    return typeof result === 'string' ? result : JSON.stringify(result)
  } catch (e) {
    // 5. 错误处理
    ctx.logger.error('Tool failed', { name, args, error: e.message })
    throw e
  }
}
```

## 👥 子代理（Subagent）机制

主 Agent 可以派生子 Agent 完成并行任务：

```
主 Agent
   │
   ├ subagent.spawn({
   │     agent: 'coding-assistant',
   │     task: '修复 login bug',
   │     model: 'sonnet',
   │     isolated_session: true   ← 独立会话
   │ })
   │
   ▼
子 Agent 实例（独立 Agent 实例，共享 dsh 进程）
   ├ 独立 messages
   ├ 独立 tool 调用历史
   ├ 共享 Cordis Context（plugin 单例）
   └ 完成后结果返回主 Agent
```

### 与多进程的关键区别

```
传统多进程（fork / spawn）：
  ❌ 资源开销大（每个子代理 ~100MB 内存）
  ❌ IPC 复杂（需序列化 / 协议）
  ❌ 插件无法共享

dsh 单进程多 Agent 实例：
  ✅ 共享 Cordis Context（plugin 单例）
  ✅ 子代理 = 独立的 Agent Runtime 实例
  ✅ 共享缓存（LLM 响应 / 工具结果）
  ✅ 父子通信走 Event Bus（零序列化）
```

### 子代理代码（简化）

```typescript
// packages/core/src/subagent.ts
export async function spawnSubagent(
  parent: Context,
  config: SubagentConfig
): Promise<string> {
  // 创建子 Context（共享 plugin 但独立 session）
  const childCtx = parent.fork({
    sessionId: `sub-${Date.now()}`,
    model: config.model,
    systemPrompt: config.systemPrompt,
    tools: config.tools,
  })

  // 在子 Context 上跑 Agent Loop
  let result = ''
  for await (const event of agentLoop(childCtx, config.task)) {
    // 转发事件到主 Context
    parent.emit('subagent:event', { subId: config.id, event })
    if (event.type === 'content_delta') result += event.text
    if (event.type === 'done') break
  }

  // 清理
  await childCtx.stop()

  return result
}
```

## 📡 消息流（Web UI 实时推送）

dsh 进程通过 SSE / WebSocket 推送事件给前端：

```
dsh 内部事件流：
   { type: 'message_start', role: 'assistant' }
   { type: 'content_delta', text: '我来分析...' }
   { type: 'tool_call', name: 'read_file', args: {...} }
   { type: 'tool_result', content: 'function foo()...' }
   { type: 'content_delta', text: '问题是 line 42...' }
   { type: 'message_end', usage: { tokens: 1234 } }
   │
   ▼
Fastify SSE / WSocket 推送
   │
   ▼
Web UI（Vite + Vue）渲染
   ├ 流式文字（打字机效果）
   ├ 工具调用卡片（折叠展开）
   └ Token 计数 + 计时器
```

### 推送实现（简化）

```typescript
// packages/server/src/routes/chat.ts
fastify.post('/chat', async (req, reply) => {
  const { message, sessionId } = req.body

  // 设置 SSE 头
  reply.raw.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
  })

  // 把 Agent Loop 的事件流转发给前端
  for await (const event of agentLoop(ctx, message)) {
    reply.raw.write(`event: ${event.type}\n`)
    reply.raw.write(`data: ${JSON.stringify(event)}\n\n`)
  }

  reply.raw.end()
})
```

## 🔒 沙箱与权限检查

每个危险操作都过沙箱：

```yaml
# config.yaml
permissions:
  filesystem:
    write: ["src/**", "*.md", "*.json"]
    deny:  [".env", "secrets/**", ".git/**"]
  shell:
    allow: ["npm test", "git status", "git diff"]
    deny:  ["rm -rf", "sudo", "curl | sh"]
```

### 三层检查

```
① 静态检查
   ├ 路径在 allow 列表？
   ├ 命令在 deny 列表？（黑名单）
   └ 风险级别（read / write / dangerous）？

② 动态检查
   ├ 用户已确认（危险操作弹确认框）？
   ├ 频率限制（防止滥用）？
   └ 配额检查（API 调用上限）？

③ 运行时检查
   ├ 执行后结果是否符合预期？
   ├ 输出是否包含敏感信息？
   └ 是否触发额外审计？
```

### 沙箱代码（简化）

```typescript
// packages/core/src/sandbox.ts
export class Sandbox {
  async check(
    toolName: string,
    args: any,
    riskLevel: 'read' | 'write' | 'dangerous'
  ): Promise<'allow' | 'deny' | 'ask'> {

    // 1. 黑名单
    if (this.config.deny.includes(toolName)) return 'deny'

    // 2. 白名单
    if (this.config.allow.includes(toolName)) return 'allow'

    // 3. 按风险级别
    if (riskLevel === 'read') return 'allow'
    if (riskLevel === 'write') return 'ask'
    if (riskLevel === 'dangerous') {
      // 危险操作必须显式确认
      const approved = await this.ui.confirm(
        `危险操作: ${toolName}`,
        JSON.stringify(args, null, 2)
      )
      return approved ? 'allow' : 'deny'
    }

    return 'ask'
  }
}
```

## 💾 状态管理

```
~/.local/share/dsh/
├─ sessions/
│  └─ <session-id>/
│     ├─ messages.json       # 完整对话（可重放）
│     ├─ edits.jsonl         # 文件修改日志（可回滚）
│     ├─ commands.jsonl      # shell 命令历史
│     └─ metadata.json       # 元数据（model, profile, time）
├─ checkpoints/              # 关键节点快照
└─ cache/
   └─ llm-cache/             # LLM 响应缓存（按 hash）
```

### 持久化时机

```
每轮 Agent Loop 完成后：
├ 检查点保存
│ ├ messages（追加）
│ ├ edits（追加）
│ └ commands（追加）
│
├ 后台异步写磁盘（不阻塞主循环）
│
└ 异常退出时：
   ├ 自动 flush
   └ 下次启动 dsh session resume 可恢复
```

### Checkpoint 回放

```typescript
// 恢复会话（dsh session resume <id>）
async function resumeSession(sessionId: string) {
  const session = await loadSession(sessionId)

  // 重放到上次中断的位置
  const messages = session.messages

  // 从下一个用户输入恢复 Agent Loop
  for await (const event of agentLoop(ctx, messages)) {
    yield event
  }
}
```

## 🧬 进程模型

dsh 是**单进程多插件**架构：

```
1 个 Node.js 进程
├ 1 个 Cordis Context          ← 单例
├ N 个 Plugin 实例             ← 按 config 加载
├ M 个 Agent 实例              ← 多会话时并发
└ K 个 Tool Handler            ← 异步执行

不是多进程：
❌ 不用 spawn() 子进程跑工具
❌ 不用 fork() 跑子代理

是单进程：
✅ 全部进程内异步执行
✅ 子代理是独立的 Agent 实例
✅ 共享同一个 dsh 进程（节省资源 + 共享缓存）
```

### 进程内并发模型

```
Node.js 单线程 + 事件循环
├ 主 Event Loop
│   ├ Agent Loop（用户消息处理）
│   ├ Fastify HTTP 服务器（IO 多路复用）
│   └ WebSocket 连接
│
├ Worker Threads（可选）
│   ├ 大文件读取（CPU 密集）
│   ├ 嵌入计算
│   └ 图像处理
```

## 🛟 错误恢复

### 错误分类

```
┌─────────────────────────────────────────────────┐
│ 可重试错误                                       │
│  ├ 网络超时                                       │
│  ├ API 限流 (429)                                │
│  ├ 临时服务不可用 (503)                           │
│  └ 处理：exponential backoff + 最多 3 次           │
├─────────────────────────────────────────────────┤
│ 不可重试错误                                      │
│  ├ 参数错误                                       │
│  ├ 权限拒绝                                       │
│  ├ 文件不存在                                     │
│  └ 处理：错误信息回传给 LLM，让 LLM 决策            │
├─────────────────────────────────────────────────┤
│ 严重错误                                          │
│  ├ OOM                                            │
│  ├ Unhandled Exception                            │
│  └ 处理：保存 checkpoint + 优雅退出 + 提示用户     │
└─────────────────────────────────────────────────┘
```

### 错误恢复代码（简化）

```typescript
// packages/core/src/error-recovery.ts
async function withRetry<T>(
  fn: () => Promise<T>,
  opts: { maxRetries: number; baseDelay: number }
): Promise<T> {
  for (let attempt = 1; attempt <= opts.maxRetries; attempt++) {
    try {
      return await fn()
    } catch (e) {
      if (!isRetryable(e) || attempt === opts.maxRetries) throw e

      const delay = opts.baseDelay * Math.pow(2, attempt - 1) +
                    Math.random() * 1000  // jitter
      ctx.logger.warn(`Retry ${attempt}/${opts.maxRetries} after ${delay}ms`)
      await sleep(delay)
    }
  }
  throw new Error('unreachable')
}
```

### Session 崩溃恢复

```
整个 session 崩溃？
├ 自动保存 checkpoint              ← 每次循环结束
├ 下次启动可恢复                  ← dsh session resume
└ 用户的文件修改已落盘             ← 不丢数据（每个 tool 立即写）
```

## 🆚 与 Claude Code 的本质区别

| 维度 | Claude Code | dsh (Harness) |
|---|---|---|
| 开源 | ❌ 闭源 | ✅ MIT |
| 插件架构 | ❌ 无 | ✅ Cordis |
| 多种 Agent 模式 | ❌ 单模式 | ✅ standard / ptc / minimal / creative |
| 模型选择 | ❌ 仅 Claude | ✅ 任意 OpenAI / Anthropic |
| 子代理 | ✅ 有限 | ✅ 完整派生机制 |
| 自定义 Skill | ❌ 无 | ✅ 可写 .md + 调用 |
| 源码可读 | ❌ | ✅ TS 99.8% 可读 |
| 进程模型 | 单进程 | 单进程（共享 Cordis） |
| 本地优先 | ✅ | ✅ + 完全离线能力 |
| Web UI | ❌ | ✅ 内置（端口 3080） |

## 🧪 调试与诊断技巧

### 启用调试日志

```bash
# 启动时
dsh web --log-level debug

# 或环境变量
DSH_LOG_LEVEL=debug dsh web

# 输出位置
~/.local/share/dsh/logs/dsh.log
```

### 追踪单次工具调用

```typescript
// packages/core/src/agent-loop.ts（注入调试钩子）
async function dispatchTool(ctx, name, args) {
  const t0 = Date.now()

  ctx.logger.debug('tool:start', { name, args })

  try {
    const result = await tool.handler(args, ctx)
    ctx.logger.debug('tool:end', {
      name,
      duration_ms: Date.now() - t0,
      result_length: result.length,
    })
    return result
  } catch (e) {
    ctx.logger.error('tool:error', {
      name,
      duration_ms: Date.now() - t0,
      error: e.message,
      stack: e.stack,
    })
    throw e
  }
}
```

### 性能分析

```bash
# 启用 v8 profiler
dsh web --prof

# 生成的 isolate-*.log 可用 chrome://inspect 分析
```

### 内存监控

```typescript
// 定时打印内存使用
setInterval(() => {
  const usage = process.memoryUsage()
  ctx.logger.info('memory', {
    rss_mb: Math.round(usage.rss / 1024 / 1024),
    heap_used_mb: Math.round(usage.heapUsed / 1024 / 1024),
    external_mb: Math.round(usage.external / 1024 / 1024),
  })
}, 30000)
```

## 🎯 性能基准（参考值）

| 场景 | 延迟 | 吞吐量 |
|---|---|---|
| 单轮 LLM 调用（V3.2） | ~800ms TTFT | ~50 tokens/s |
| 工具调用（read_file） | <10ms | 1000+ calls/s |
| 工具调用（shell） | 50-500ms | 受命令本身限制 |
| 子代理派生 | <5ms | 100+ agents/s |
| Checkpoint 写入 | <50ms | 异步不阻塞 |

## 📚 深入阅读

| 主题 | 源码位置 |
|---|---|
| Cordis 容器 | packages/core/src/context.ts |
| 插件加载 | packages/core/src/plugin-loader.ts |
| Agent Loop | packages/core/src/agent-loop.ts |
| Tool Dispatcher | packages/core/src/tool-dispatcher.ts |
| Sandbox | packages/core/src/sandbox.ts |
| Subagent | packages/core/src/subagent.ts |
| Memory | packages/core/src/memory/ |
| Checkpoint | packages/core/src/checkpoint.ts |
| Server (Fastify) | packages/server/src/ |
| CLI | packages/cli/src/main.ts |

## 🎓 一句话总结

> **dsh = 给 AI Agent 一个完整的"操作系统"**：进程管理、文件系统、工具集、权限系统、记忆系统、子进程能力、网络，让 Agent 能像人一样在本地环境里完成真实任务。

Agent 在这个运行时里通过 **"Message Loop + Tool Dispatch + Memory + Sandbox"** 的循环完成复杂任务，每一步都经过 Cordis 容器的事件总线 + 沙箱检查 + 持久化 checkpoint，保证可恢复、可调试、可观测。
