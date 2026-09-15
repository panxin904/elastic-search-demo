---
title: dsh 源码级深度讲解
date: 2026-09-15  # date-auto-injected
---

# 🔬 dsh 源码级深度讲解

> 本章是 [07-runtime.md](./07-runtime) 的进阶版。逐行分析 dsh 进程内部的关键源码模块（路径基于 `packages/core/src/`、`packages/server/src/` 等），帮助开发者：
> - 理解 dsh 的实现细节
> - 自定义插件时知道扩展点
> - 排查生产环境的疑难问题
>
> 源码引用基于 DeepSeek Harness v0.1.2-rc.1。

## 📑 目录

1. [Agent Loop 主循环](#1-agent-loop-主循环源码逐行分析)
2. [Cordis 容器原理](#2-cordis-容器原理)
3. [Tool Dispatcher 调度机制](#3-tool-dispatcher-调度机制)
4. [MCP 桥接实现](#4-mcp-桥接实现)
5. [流式响应实现](#5-流式响应实现-sse--websocket)
6. [会话持久化原理](#6-会话持久化原理)
7. [性能基准](#7-性能基准)
8. [故障排查](#8-故障排查指南)

---

## 1. Agent Loop 主循环（源码逐行分析）

### 文件位置

```
packages/core/src/agent-loop.ts
```

### 完整源码（v0.1.2-rc.1 简化版，~150 行）

```typescript
// packages/core/src/agent-loop.ts
import { Context } from '@harness/core'
import { ToolDispatcher } from './tool-dispatcher'
import { EventBus } from './event-bus'
import { CheckpointManager } from './checkpoint'
import { Logger } from '@harness/utils'

export interface AgentLoopConfig {
  maxIterations: number           // 默认 30
  timeoutMs?: number             // 单轮 LLM 超时
  toolTimeoutMs?: number         // 单个工具超时
  parallelToolCalls: boolean      // 是否并行执行 tool_calls
  checkpointOnIteration: boolean // 是否每轮做 checkpoint
}

export type AgentEvent =
  | { type: 'iteration_start'; iteration: number }
  | { type: 'content_delta'; text: string }
  | { type: 'tool_call_start'; name: string; args: any; callId: string }
  | { type: 'tool_call_end'; name: string; result: string; durationMs: number; callId: string }
  | { type: 'done'; content: string; usage: TokenUsage }
  | { type: 'error'; error: Error; recoverable: boolean }

export async function* agentLoop(
  ctx: Context,
  userMessage: string,
  config: AgentLoopConfig
): AsyncIterable<AgentEvent> {
  // ============ 阶段 1: 初始化 ============
  const logger = ctx.get(Logger)
  const toolDispatcher = ctx.get(ToolDispatcher)
  const eventBus = ctx.get(EventBus)
  const checkpointMgr = ctx.get(CheckpointManager)
  const abortController = new AbortController()

  // 监听外部取消信号（用户按 Ctrl+C / 关闭 Web UI）
  ctx.on('abort', () => abortController.abort())

  // ============ 阶段 2: 构建消息上下文 ============
  const sessionId = ctx.sessionId
  const messages = await ctx.memory.load(sessionId, { limit: 50 })
  messages.push({ role: 'user', content: userMessage })

  const systemPrompt = buildSystemPrompt(ctx)
  messages.unshift({ role: 'system', content: systemPrompt })

  // ============ 阶段 3: 主循环 ============
  let iteration = 0
  let totalUsage: TokenUsage = { prompt: 0, completion: 0, total: 0 }

  while (iteration++ < config.maxIterations) {
    if (abortController.signal.aborted) {
      throw new Error('Agent loop aborted')
    }

    yield { type: 'iteration_start', iteration }

    try {
      // -------- 3.1: 调用 LLM（流式） --------
      const stream = ctx.model.chatStream({
        model: ctx.config.model,
        messages,
        tools: toolDispatcher.listAvailable(),
        temperature:,
        max_tokens: ctx.config.maxTokens,
        signal: abortController.signal,
        timeoutMs: config.timeoutMs,
      })

      let assistantMessage = ''
      const toolCalls: ToolCall[] = []

      // 流式解析响应
      for await (const chunk of stream) {
        if (abortController.signal.aborted) break

        // 文本增量
        if (chunk.type === 'content') {
          assistantMessage += chunk.text
          yield { type: 'content_delta', text: chunk.text }
        }

        // 工具调用增量（OpenAI delta 格式）
        if (chunk.type === 'tool_call_delta') {
          const existing = toolCalls.find(c => c.id === chunk.id)
          if (existing) {
            existing.function.arguments += chunk.function.arguments
          } else {
            toolCalls.push({
              id: chunk.id,
              type: 'function',
              function: {
                name: chunk.function.name,
                arguments: chunk.function.arguments,
              },
            })
          }
        }

        // Token 计数
        if (chunk.usage) {
          totalUsage = {
            prompt: chunk.usage.prompt_tokens,
            completion: chunk.usage.completion_tokens,
            total: chunk.usage.total_tokens,
          }
        }
      }

      // -------- 3.2: 把 assistant 消息加入历史 --------
      messages.push({
        role: 'assistant',
        content: assistantMessage,
        tool_calls: toolCalls.length > 0 ? toolCalls : undefined,
      })

      // -------- 3.3: 没有工具调用，结束 --------
      if (toolCalls.length === 0) {
        yield { type: 'done', content: assistantMessage, usage: totalUsage }
        await checkpointMgr.save(ctx.sessionId, { messages, done: true })
        return
      }

      // -------- 3.4: 并行执行所有工具调用 --------
      const toolResults = await Promise.all(
        toolCalls.map(async (call) => {
          const t0 = Date.now()
          yield {
            type: 'tool_call_start',
            name: call.function.name,
            args: JSON.parse(call.function.arguments || '{}'),
            callId: call.id,
          }

          try {
            const result = await toolDispatcher.dispatch(
              call.function.name,
              JSON.parse(call.function.arguments || '{}'),
              { signal: abortController.signal, timeoutMs: config.toolTimeoutMs }
            )

            yield {
              type: 'tool_call_end',
              name: call.function.name,
              result,
              durationMs: Date.now() - t0,
              callId: call.id,
            }

            return { tool_call_id: call.id, role: 'tool', content: result }
          } catch (e) {
            // 错误回传 LLM（让它决定怎么应对）
            const errorMsg = `Error: ${e.message}\n\nStack:\n${e.stack}`
            yield {
              type: 'tool_call_end',
              name: call.function.name,
              result: errorMsg,
              durationMs: Date.now() - t0,
              callId: call.id,
            }
            return { tool_call_id: call.id, role: 'tool', content: errorMsg }
          }
        })
      )

      // -------- 3.5: 工具结果加入 messages --------
      messages.push(...toolResults)

      // -------- 3.6: Checkpoint（异步，不阻塞） --------
      if (config.checkpointOnIteration) {
        checkpointMgr.save(ctx.sessionId, { messages, iteration }).catch(err => {
          logger.error('Checkpoint save failed', { error: err.message })
        })
      }

      // 回到 3.1，继续循环
    } catch (e) {
      // -------- 3.7: 错误处理 --------
      if (isRetryable(e) && iteration < config.maxIterations) {
        logger.warn(`Retry iteration ${iteration} due to: ${e.message}`)
        await sleep(Math.min(1000 * 2 ** iteration, 10000))
        continue
      }

      yield { type: 'error', error: e, recoverable: false }
      throw e
    }
  }

  // max iterations 达到
  throw new Error(`Agent loop exceeded max iterations (${config.maxIterations})`)
}
```

### 关键设计点逐行解析

#### 1. 异步生成器（Async Iterable）模式

```typescript
export async function* agentLoop(...): AsyncIterable<AgentEvent>
```

**为什么用 generator？**
- ✅ 流式推送事件给 UI（每收到一个 chunk 立刻 yield）
- ✅ UI 可以中途取消（generator 支持 break）
- ✅ 测试友好（可以用 `for await` 模拟单步）

#### 2. AbortSignal 多源合并

```typescript
const abortController = new AbortController()
ctx.on('abort', () => abortController.abort())  // 外部取消

// 传给 LLM 和工具
ctx.model.chatStream({ signal: abortController.signal, ... })
toolDispatcher.dispatch(..., { signal: abortController.signal })
```

**好处**：
- 用户按 Ctrl+C → 立即取消所有 LLM 调用和工具执行
- Web UI 关闭 → 同上
- 工具超时 → 单独 AbortSignal，但合并到主信号

#### 3. 工具调用增量解析

```typescript
if (chunk.type === 'tool_call_delta') {
  const existing = toolCalls.find(c => c.id === chunk.id)
  if (existing) {
    existing.function.arguments += chunk.function.arguments
  } else {
    toolCalls.push({ id: chunk.id, ... })
  }
}
```

**关键**：OpenAI / Anthropic 都用流式输出工具调用参数，每个 chunk 只来一段 JSON 片段，必须拼接。

#### 4. 工具并行执行

```typescript
const toolResults = await Promise.all(
  toolCalls.map(async (call) => { ... })
)
```

**如果 LLM 一次返回 3 个独立 tool_calls**（如 `read_file` + `read_file` + `search_code`），并行执行可节省 60%+ 时间。

#### 5. Checkpoint 异步写入

```typescript
checkpointMgr.save(ctx.sessionId, { messages, iteration })
  .catch(err => logger.error('Checkpoint save failed', ...))
```

**不 await**：避免阻塞主循环。失败仅记日志，不影响用户体验。

---

## 2. Cordis 容器原理

### 文件位置

```
packages/core/src/context.ts
packages/core/src/plugin.ts
packages/core/src/registry.ts
```

### 核心数据结构

```typescript
// packages/core/src/context.ts（简化版）
export class Context {
  // 服务注册表（DI 容器）
  public registry = new Map<string, Service>()

  // 事件总线
  public emitter = new EventEmitter()

  // 父子 Context 关系
  public parent?: Context
  public children: Context[] = []

  // 当前会话 ID
  public sessionId: string

  constructor(options: ContextOptions = {}) {
    this.sessionId = options.sessionId || `session-${Date.now()}`
  }

  // ===== DI 核心方法 =====

  // 注册插件
  plugin<T extends Service>(
    ServiceClass: new (...args: any[]) => T,
    ...configArgs: any[]
  ): this {
    // 1. 解析依赖（static inject 声明）
    const deps = (ServiceClass as any).inject || []

    // 2. 注入依赖实例
    const depInstances = deps.map(d => this.get(d))

    // 3. 实例化
    const instance = new ServiceClass(this, ...configArgs, ...depInstances)

    // 4. 注册到 registry
    const name = (ServiceClass as any).name || ServiceClass.constructor.name
    this.registry.set(name, instance)

    // 5. 加入生命周期
    this.lifecycleQueue.push(instance)

    return this
  }

  // 获取服务
  get<T extends Service>(name: string | typeof Service): T {
    const key = typeof name === 'string' ? name : name.name
    const service = this.registry.get(key)

    if (!service) {
      throw new Error(`Service not found: ${key}`)
    }
    return service as T
  }

  // ===== 生命周期 =====

  private lifecycleQueue: Service[] = []

  async start() {
    // 拓扑排序所有插件（按依赖关系）
    const sorted = topoSort(this.lifecycleQueue, s => s.constructor.inject || [])

    // 依次启动
    for (const service of sorted) {
      await service.start?.()
    }
  }

  async stop() {
    // 逆序关闭
    const reversed = [...this.lifecycleQueue].reverse()
    for (const service of reversed) {
      await service.stop?.()
    }
  }

  // ===== 事件总线 =====

  emit(event: string, ...args: any[]) {
    this.emitter.emit(event, ...args)
  }

  on(event: string, handler: (...args: any[]) => void) {
    this.emitter.on(event, handler)
  }
}
```

### 依赖注入（DI）工作流

```
1. Service 声明依赖：
   ┌──────────────────────────────────────────────┐
   │ class CodingAgent extends Service {          │
   │   static inject = ['model', 'tool.file_edit'] │
   │ }                                              │
   └──────────────────────────────────────────────┘

2. 注册插件时：
   ├ Cordis 读取 static inject = ['model', 'tool.file_edit']
   ├ 从 registry 查 model 和 tool.file_edit
   ├ 注入到构造函数
   └ new CodingAgent(ctx, model, fileEdit)

3. 使用：
   ctx.get('model').chat({ ... })   ← 简单 API
   this.model.chat({ ... })        ← 在 Service 内部直接用
```

### 事件总线使用模式

```typescript
// 发送事件
ctx.emit('tool:called', { name, args, duration })
ctx.emit('session:end', { usage, duration })

// 订阅事件
ctx.on('tool:called', (event) => {
  metrics.record('tool_calls_total', { name })
})

ctx.on('session:end', (event) => {
  logger.info('Session ended', { tokens: event.usage.total })
})

// 一次性订阅
ctx.once('session:end', cleanup)

// 取消订阅
const handler = (e) => { ... }
ctx.on('event', handler)
ctx.off('event', handler)
```

### 子 Context 派生

```typescript
// 创建子 Context（共享 plugin，独立 session）
const subCtx = ctx.fork({
  sessionId: `sub-${Date.now()}`,
  model: 'gpt5m',           // 覆盖父的 model
})

// 注册额外插件
subCtx.plugin(SomeExtraPlugin)

// 子 Context 继承父的所有 plugin
subCtx.get('model')   // ← 拿到的是父的 model（除非覆盖）

// 子 Context 独立的事件
subCtx.emit('sub:event')
parentCtx.emit('sub:event')   // 父收不到子的事件
```

### 源码引用

| 模块 | 路径 | 行数 |
|---|---|---|
| Context | `packages/core/src/context.ts` | ~250 |
| Service 基类 | `packages/core/src/service.ts` | ~80 |
| 插件加载器 | `packages/core/src/plugin-loader.ts` | ~120 |
| 依赖解析 | `packages/core/src/inject.ts` | ~60 |
| 生命周期 | `packages/core/src/lifecycle.ts` | ~90 |
| EventBus | `packages/core/src/event-bus.ts` | ~40 |

---

## 3. Tool Dispatcher 调度机制

### 文件位置

```
packages/core/src/tool-dispatcher.ts
```

### 完整源码

```typescript
// packages/core/src/tool-dispatcher.ts（简化版）
export class ToolDispatcher {
  static inject = ['sandbox', 'logger', 'ui']

  private registry = new Map<string, Tool>()

  // 注册工具
  register(name: string, tool: Tool) {
    this.registry.set(name, tool)
  }

  // 列出可用工具（传给 LLM）
  listAvailable(): ToolSchema[] {
    return Array.from(this.registry.values()).map(t => ({
      type: 'function',
      function: {
        name: t.name,
        description: t.description,
        parameters: zodToJsonSchema(t.parameters),  // zod → JSON Schema
      },
    }))
  }

  // 分发调用（核心方法）
  async dispatch(
    name: string,
    args: any,
    options: DispatchOptions = {}
  ): Promise<string> {
    const startTime = Date.now()
    const signal = options.signal || new AbortController().signal

    // 1. 查找工具
    const tool = this.registry.get(name)
    if (!tool) {
      throw new Error(`Tool not found: ${name}`)
    }

    // 2. 参数校验（zod schema）
    try {
      args = tool.parameters.parse(args)
    } catch (e) {
      throw new Error(`Invalid args for ${name}: ${e.message}`)
    }

    // 3. 沙箱权限检查（关键注入点）
    const decision = await this.sandbox.check(name, args, tool.riskLevel)

    if (decision === 'deny') {
      throw new Error(`Permission denied by sandbox: ${name}`)
    }

    if (decision === 'ask') {
      const userApproved = await this.ui.confirmRisk(
        `执行工具: ${name}`,
        JSON.stringify(args, null, 2),
        tool.riskLevel
      )
      if (!userApproved) {
        throw new Error(`User denied execution: ${name}`)
      }
    }

    // 4. 超时控制（关键注入点）
    const timeoutMs = options.timeoutMs || tool.timeout || 30000
    const timeoutController = new AbortController()
    setTimeout(() => timeoutController.abort(`Tool ${name} timed out`), timeoutMs)

    const combinedSignal = AbortSignal.any([
      signal,
      timeoutController.signal,
    ])

    // 5. 执行（带错误处理 + 重试）
    const result = await this.executeWithRetry(tool, args, combinedSignal)

    // 6. 输出限流（防止大对象爆内存）
    const resultStr = typeof result === 'string' ? result : JSON.stringify(result)
    const truncated = resultStr.length > 100000
      ? resultStr.slice(0, 100000) + '\n\n[TRUNCATED - 100KB limit]'
      : resultStr

    // 7. 审计日志
    this.logger.info('tool:dispatched', {
      name,
      duration_ms: Date.now() - startTime,
      args_size: JSON.stringify(args).length,
      result_size: truncated.length,
    })

    return truncated
  }

  // 内部：带重试的执行
  private async executeWithRetry(
    tool: Tool,
    args: any,
    signal: AbortSignal
  ): Promise<any> {
    const maxRetries = tool.retryable ? 3 : 1
    let lastError: Error | undefined

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await tool.handler(args, { signal })
      } catch (e) {
        lastError = e

        if (!isRetryable(e) || attempt === maxRetries) break

        // 指数退避 + jitter
        const delay = Math.min(1000 * 2 ** attempt, 10000) + Math.random() * 500
        await sleep(delay)
      }
    }

    throw lastError
  }
}
```

### 关键设计点

#### 1. 沙箱注入点

```typescript
// 第 3 步：沙箱检查
const decision = await this.sandbox.check(name, args, tool.riskLevel)
```

**`riskLevel` 决定默认策略**：

| riskLevel | 默认决策 | 适用 |
|---|---|---|
| `read` | allow | 读文件、搜索 |
| `write` | ask | 写文件、改配置 |
| `dangerous` | ask + 用户确认 | shell、git push |

#### 2. 超时机制

```typescript
const timeoutController = new AbortController()
setTimeout(() => timeoutController.abort(`Tool ${name} timed out`), timeoutMs)

const combinedSignal = AbortSignal.any([signal, timeoutController.signal])
```

**多源 AbortSignal 合并**：
- 外部信号（用户取消）
- 超时信号（30s 默认）
- 任意一个 abort → 工具 handler 收到 abort

#### 3. 并发控制

```typescript
// 工具级别并发限制
private semaphores = new Map<string, Semaphore>()

async dispatch(name: string, args: any, options: DispatchOptions) {
  const max = this.config.maxConcurrent?.[name] || Infinity
  const sem = this.semaphores.get(name) || new Semaphore(max)
  this.semaphores.set(name, sem)

  return sem.acquire(() => this.execute(name, args))
}
```

**避免资源耗尽**：比如同时跑 10 个 `npm install` 会撑爆磁盘 IO。

#### 4. 结果截断

```typescript
const truncated = resultStr.length > 100000
  ? resultStr.slice(0, 100000) + '\n\n[TRUNCATED - 100KB limit]'
  : resultStr
```

**为什么**：LLM 上下文窗口有限，单个工具结果 > 100KB 会撑爆。

---

## 4. MCP 桥接实现

### 文件位置

```
packages/core/src/mcp/manager.ts
packages/core/src/mcp/transport/stdio.ts
packages/core/src/mcp/protocol.ts
```

### MCP 协议简介

```
MCP (Model Context Protocol) = JSON-RPC 2.0 over stdio
├ dsh 进程 spawn 一个 MCP Server 子进程
├ 通过 stdin/stdout 通信
├ JSON-RPC 消息格式
└ MCP Server 注册工具列表 → dsh 转发给 LLM
```

### 完整源码

```typescript
// packages/core/src/mcp/manager.ts（简化版）
import { spawn, ChildProcess } from 'node:child_process'
import { JSONRPCClient } from './protocol/json-rpc'

export class MCPManager {
  static inject = ['logger', 'toolDispatcher']

  private servers = new Map<string, MCPConnection>()

  async connectServer(name: string, config: MCPServerConfig) {
    // 1. spawn 子进程
    const child = spawn(config.command, config.args, {
      env: { ...process.env, ...config.env },
      stdio: ['pipe', 'pipe', 'pipe'],
    })

    // 2. JSON-RPC 客户端
    const rpc = new JSONRPCClient({
      write: (msg) => child.stdin.write(msg + '\n'),
      read: (cb) => {
        let buffer = ''
        child.stdout.on('data', (data) => {
          buffer += data.toString()
          // 按换行分割（JSON-RPC 帧）
          let idx
          while ((idx = buffer.indexOf('\n')) >= 0) {
            const line = buffer.slice(0, idx)
            buffer = buffer.slice(idx + 1)
            if (line.trim()) cb(JSON.parse(line))
          }
        })
      },
    })

    // 3. 握手：initialize
    const serverInfo = await rpc.request('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: { sampling: {}, roots: {} },
      clientInfo: { name: 'dsh', version: '0.1.2' },
    })

    // 4. 列出工具
    const { tools } = await rpc.request('tools/list', {})

    // 5. 注册到 ToolDispatcher
    for (const tool of tools) {
      this.toolDispatcher.register(`mcp.${name}.${tool.name}`, {
        name: `mcp.${name}.${tool.name}`,
        description: tool.description,
        parameters: zodFromJsonSchema(tool.inputSchema),
        riskLevel: 'read',  // 默认只读，特殊工具可覆盖
        handler: async (args, { signal }) => {
          const result = await rpc.request('tools/call', {
            name: tool.name,
            arguments: args,
          })

          return result.content
            .filter(c => c.type === 'text')
            .map(c => c.text)
            .join('\n')
        },
      })
    }

    this.servers.set(name, { child, rpc, config, serverInfo })
  }
}
```

### JSON-RPC 通信示例

```
dsh → Server (stdin):
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{...}}

Server → dsh (stdout):
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05",...}}

dsh → Server (stdin):
{"jsonrpc":"2.0","id":2,"method":"tools/list"}

Server → dsh (stdout):
{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"search",...}]}}

dsh → Server (stdin):
{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"search","arguments":{"q":"hello"}}}

Server → dsh (stdout):
{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"..."}]}}
```

### 关键技术点

| 维度 | 实现 |
|---|---|
| **进程隔离** | 每个 MCP Server 一个子进程，崩溃不影响 dsh |
| **stdio 通信** | stdin/stdout + JSON-RPC 2.0 |
| **协议版本** | MCP 协议 2024-11-05 |
| **生命周期** | initialize → tools/list → ready → tools/call |
| **超时** | 每个 RPC 请求 30s 超时 |
| **错误** | JSON-RPC error 字段透传 |
| **并发** | 单连接串行（按 JSON-RPC id 匹配响应） |

### 与多进程 agent 对比

| 维度 | MCP Server（外部进程） | 子 Agent（内部） |
|---|---|---|
| 进程 | 独立子进程 | 同进程 |
| 通信 | stdio + JSON-RPC | Event Bus（零开销） |
| 隔离 | 完全隔离 | 共享 Context |
| 性能 | IPC 序列化开销 ~1ms | 直接函数调用 ~0.01ms |
| 适用 | 外部工具（Jira/GitHub） | 内部子任务 |

---

## 5. 流式响应实现（SSE + WebSocket）

### 文件位置

```
packages/server/src/routes/chat.ts
packages/server/src/ws/agent-events.ts
```

### SSE 实现

```typescript
// packages/server/src/routes/chat.ts（简化版）
fastify.post('/api/chat', async (req, reply) => {
  const { message, sessionId } = req.body

  // 1. 设置 SSE 响应头
  reply.raw.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache, no-transform',
    'Connection': 'keep-alive',
    'X-Accel-Buffering': 'no',  // 禁用 Nginx 缓冲
  })

  // 2. 创建 session（如果不存在）
  const ctx = await getOrCreateSession(sessionId, req.user)

  // 3. 监听 abort（客户端断开）
  const abortController = new AbortController()
  reply.raw.on('close', () => abortController.abort('client disconnected'))

  // 4. 把 agentLoop 的事件转发为 SSE
  try {
    for await (const event of agentLoop(ctx, message, config)) {
      if (abortController.signal.aborted) break

      // SSE 格式：event + data + 双换行
      reply.raw.write(`event: ${event.type}\n`)
      reply.raw.write(`data: ${JSON.stringify(event)}\n\n`)
    }
  } catch (e) {
    reply.raw.write(`event: error\ndata: ${JSON.stringify({ message: e.message })}\n\n`)
  } finally {
    reply.raw.end()
  }
})
```

### WebSocket 实现

```typescript
// packages/server/src/ws/agent-events.ts（简化版）
fastify.register(async (fastify) => {
  fastify.get('/ws/agent', { websocket: true }, (connection, req) => {
    const sessionId = req.query.sessionId
    const ctx = getSessionContext(sessionId)

    connection.on('message', async (raw) => {
      const msg = JSON.parse(raw.toString())

      switch (msg.type) {
        case 'chat':
          // 客户端发消息
          for await (const event of agentLoop(ctx, msg.content, config)) {
            connection.send(JSON.stringify({
              type: event.type,
              payload: event,
              sessionId,
            }))

            // 用户中断
            if (event.type === 'user_interrupted') break
          }
          break

        case 'abort':
          ctx.abort('user interrupted')
          break
      }
    })

    connection.on('close', () => {
      ctx.abort('websocket closed')
    })
  })
})
```

### 协议格式对比

| 维度 | SSE | WebSocket |
|---|---|---|
| **方向** | 单向（服务端→客户端） | 双向 |
| **协议** | HTTP/1.1 + chunked transfer | 独立 WS 协议 |
| **断线重连** | 浏览器自动重连 | 需手动实现 |
| **代理穿透** | 友好（HTTP） | 可能被代理拦截 |
| **适用场景** | 简单的流式输出 | 需要双向通信（abort/correction） |

### 客户端示例

```typescript
// packages/web/src/composables/useChatStream.ts（Vue）
export function useChatStream() {
  const events = ref<AgentEvent[]>([])

  async function sendMessage(message: string) {
    const sessionId = getCurrentSessionId()

    // 用 EventSource 接收 SSE
    const source = new EventSource(
      `/api/chat?message=${encodeURIComponent(message)}&sessionId=${sessionId}`
    )

    source.addEventListener('content_delta', (e) => {
      const event = JSON.parse(e.data)
      events.value.push(event)
      // 更新 UI 流式渲染
      appendToLastMessage(event.text)
    })

    source.addEventListener('done', (e) => {
      source.close()
    })

    source.addEventListener('error', (e) => {
      console.error('Stream error', e)
      source.close()
    })
  }

  return { events, sendMessage }
}
```

---

## 6. 会话持久化原理

### 文件位置

```
packages/core/src/checkpoint.ts
packages/core/src/memory/json-store.ts
```

### 数据结构

```typescript
// packages/core/src/checkpoint.ts
export interface Checkpoint {
  sessionId: string
  iteration: number
  messages: Message[]          // 完整对话历史
  toolCalls: ToolCallRecord[]  // 工具调用记录
  fileEdits: FileEdit[]        // 文件修改日志
  shellCommands: ShellCmd[]    // shell 命令历史
  metadata: {
    model: string
    profile: string
    startedAt: number
    lastUpdate: number
    totalTokens: number
    totalCost: number
}
```

### 持久化算法

```typescript
// packages/core/src/checkpoint.ts（简化版）
export class CheckpointManager {
  static inject = ['logger']
  private path: string

  constructor() {
    this.path = path.join(
      os.homedir(),
      '.local/share/dsh/sessions'
    )
  }

  // 异步保存（不阻塞主循环）
  async save(sessionId: string, data: Partial<Checkpoint>): Promise<void> {
    const sessionPath = path.join(this.path, sessionId)
    await fs.mkdir(sessionPath, { recursive: true })

    const checkpoint: Checkpoint = {
      sessionId,
      iteration: data.iteration || 0,
      messages: data.messages || [],
      toolCalls: data.toolCalls || [],
      fileEdits: data.fileEdits || [],
      shellCommands: data.shellCommands || [],
      metadata: {
        model: data.metadata?.model || 'unknown',
        profile: data.metadata?.profile || 'default',
        startedAt: data.metadata?.startedAt || Date.now(),
        lastUpdate: Date.now(),
        totalTokens: data.metadata?.totalTokens || 0,
        totalCost: data.metadata?.totalCost || 0,
      },
    }

    // 写入文件（原子替换）
    const tmpPath = `${sessionPath}/checkpoint.json.tmp`
    const finalPath = `${sessionPath}/checkpoint.json`

    await fs.writeFile(tmpPath, JSON.stringify(checkpoint, null, 2), 'utf-8')
    await fs.rename(tmpPath, finalPath)  // 原子操作

    // 编辑日志（追加模式）
    if (data.fileEdits?.length) {
      await this.appendEdits(sessionId, data.fileEdits)
    }

    if (data.shellCommands?.length) {
      await this.appendCommands(sessionId, data.shellCommands)
    }
  }

  // 加载恢复
  async load(sessionId: string): Promise<Checkpoint> {
    const sessionPath = path.join(this.path, sessionId)
    const data = await fs.readFile(`${sessionPath}/checkpoint.json`, 'utf-8')
    return JSON.parse(data)
  }

  // 列出会话
  async list(): Promise<SessionInfo[]> {
    const dirs = await fs.readdir(this.path, { withFileTypes: true })
    const sessions: SessionInfo[] = []

    for (const dir of dirs) {
      if (!dir.isDirectory()) continue
      try {
        const ckpt = await this.load(dir.name)
        sessions.push({
          id: dir.name,
          ...ckpt.metadata,
          messageCount: ckpt.messages.length,
        })
      } catch (e) {
        // 损坏的会话跳过
      }
    }

    return sessions.sort((a, b) => b.lastUpdate - a.lastUpdate)
  }
}
```

### 文件布局

```
~/.local/share/dsh/sessions/
└─ <session-id>/
   ├─ checkpoint.json              # 主检查点
   ├─ checkpoint.json.tmp          # 写入中（短暂存在）
   ├─ edits.jsonl                  # 文件修改日志（可回滚）
   ├─ commands.jsonl               # shell 命令历史
   └─ messages/
      └─ <msg-idx>.json            # 大消息单独存（避免 checkpoint 过大）
```

### 会话回放

```bash
# 命令
dsh session resume <session-id>

# 内部流程
1. 加载 checkpoint.json
2. 重建 Context（用保存的 model / profile）
3. 从 messages 末尾找到 user 最后一条消息
4. 从该位置继续跑 Agent Loop
```

### 编辑回滚（高级）

```typescript
// 基于 edits.jsonl 的回滚
async function rollback(sessionId: string, toIndex: number) {
  const edits = await loadEdits(sessionId)  // 读 jsonl

  // 反向应用编辑
  for (let i = edits.length - 1; i >= toIndex; i--) {
    const edit = edits[i]
    if (edit.type === 'create') {
      await fs.unlink(edit.path)
    } else if (edit.type === 'modify') {
      await fs.writeFile(edit.path, edit.beforeContent)
    } else if (edit.type === 'delete') {
      await fs.writeFile(edit.path, edit.beforeContent)
    }
  }
}
```

---

## 7. 性能基准

### 测试环境

```
CPU:     Apple M2 Pro (12-core)
RAM:     32 GB
Disk:    SSD
Node:    v22.19.0
Model:   deepseek-chat (V3.2)
网络:    Cloudflare R2 + api.deepseek.com (东亚)
```

### 关键指标

| 指标 | 实测值 | 备注 |
|---|---|---|
| **TTFT（首 token 时间）** | 800-1500ms | 含网络 + LLM 推理启动 |
| **流式吞吐** | 45-65 tokens/s | V3.2（非推理） |
| **R1 推理速度** | 30-50 tokens/s | 推理模型 |
| **工具调度延迟** | 5-50ms | 不含工具自身耗时 |
| **文件读（<1MB）** | <10ms | 内存读取 |
| **shell 执行** | 50-500ms | 受命令本身限制 |
| **MCP 桥接** | 10-30ms | 含 JSON-RPC 序列化 |
| **Checkpoint 写入** | <50ms | 异步不阻塞 |
| **子代理派生** | <5ms | 单进程实例化 |
| **SSE 首事件延迟** | <20ms | 含事件循环 |
| **WebSocket RTT** | <5ms | localhost |

### 瓶颈分析

```
Agent Loop 单轮耗时分布（典型场景）：

LLM 调用          ████████████████████  800ms   80%
工具调度 × 3      ██  50ms              50ms   5%
Checkpoint 写入   █  30ms               30ms   3%（异步）
上下文构建        █  20ms               20ms   2%
事件 yield × N    █  20ms               20ms   2%
其他              █  80ms               80ms   8%
                               ──────────
                               1000ms（典型）
```

**结论**：LLM 调用占 80%+ 时间。优化 dsh 本身收益小，应聚焦：
1. 用更小模型（如 gpt-5-mini）
2. 减少 tool_call 次数（批处理）
3. 用 prefix caching（DeepSeek 自动）

### 压力测试

```bash
# 并发 10 个 Agent Loop
dsh bench --concurrent 10 --iterations 50

# 输出：
# Iteration   Duration   Tokens   Throughput
# 1           1023ms     450      440 t/s
# 2           987ms      512      519 t/s
# ...
# 50          1056ms     498      472 t/s
# 
# Total: 51.2s, avg 1024ms/iter, 487 t/s
# Memory: peak 412MB RSS
```

### 优化建议

```yaml
# config.yaml 性能优化
performance:
  # LLM 缓存（同一 prompt 不重复调用）
  llm_cache:
    enabled: true
    max_size: 1000
    ttl: 3600

  # 并发控制
  concurrency:
    tool_dispatch: 10       # 最多 10 个工具并行
    subagent: 4             # 最多 4 个子代理

  # 流式优化
  stream:
    batch_size: 5           # 每 5 个 token 触发一次 yield（减少事件循环压力）
    flush_interval_ms: 50   # 最多 50ms flush 一次
```

---

## 8. 故障排查指南

### 8.1 卡死（hang）排查

**症状**：dsh 无响应，UI 不刷新，但进程没崩。

**排查步骤**：

```bash
# 1. 看进程状态
ps aux | grep dsh

# 2. 看 CPU / 内存
top -pid <pid>

# 3. 看 Node.js 内部状态（需要 inspector）
kill -USR1 <pid>    # 触发 heap dump
# 或
node --inspect dsh web  # 启动时打开 inspector

# 4. 用 Chrome DevTools 连接 chrome://inspect
# 看 Call Stack / Heap / Event Loop
```

**常见卡死原因**：

| 症状 | 根因 | 解决方案 |
|---|---|---|
| 100% CPU，rss 不变 | LLM 死循环（max_iterations 没设） | 加 max_iterations |
| 100% CPU，rss 暴涨 | 内存泄漏（messages 累积） | 限制 history 长度 |
| CPU 低，IO 高 | 大量文件读 / 慢 shell | 加 timeout |
| 看起来正常但无响应 | Event Loop 卡死（同步 big task） | 用 worker_threads |

### 8.2 内存泄漏排查

**症状**：RSS 持续增长，GC 不回收。

```bash
# 1. 启用 heap snapshot
dsh web --inspect

# 2. Chrome DevTools → Memory → Take Heap Snapshot
# 3. 对比多次 snapshot 找增长源
```

**代码级排查**：

```typescript
// packages/core/src/agent-loop.ts
// ❌ 常见泄漏 1：闭包捕获大对象
const oldMessages = messages  // 整个 messages 数组被闭包捕获

// ✅ 解决：传弱引用或及时清理
const oldMessagesRef = WeakRef(messages)
setTimeout(() => {
  const stillAlive = oldMessagesRef.deref()
  if (!stillAlive) console.log('GC\'d OK')
}, 60000)

// ❌ 常见泄漏 2：EventEmitter listener 不清理
ctx.on('event', handler)
// 长期跑下来 listener 累积
// ✅ 解决：每次创建新 Context 或显式 off
ctx.off('event', handler)

// ❌ 常见泄漏 3：AbortController 不取消
const ac = new AbortController()
// 工具 handler 已完成，但 ac 没 abort()
// ✅ 解决：
ac.abort()
```

### 8.3 CPU 飙高排查

**症状**：dsh 占 CPU 80%+。

```bash
# 1. 采样（v8 profiler）
dsh web --prof
# 生成 isolate-*.log

# 2. 分析
node --prof-process isolate-*.log > profile.txt
# 看 [Bottom up (heavy)] 找热点函数

# 3. Chrome DevTools → Performance → Record
```

**常见热点**：

| 函数 | 原因 | 优化 |
|---|---|---|
| `JSON.stringify` | 大对象序列化 | 流式或增量序列化 |
| `zod.parse` | schema 校验 | 缓存解析后的 schema |
| `llm chat` | 长上下文 | 限制 history 长度 |
| `tool dispatch` | 同步阻塞 | async + 超时 |

### 8.4 工具调用失败排查

```bash
# 启用 debug 日志
DSH_LOG_LEVEL=debug dsh web 2>&1 | tee /tmp/dsh.log

# 看工具失败详情
grep "tool:dispatched" /tmp/dsh.log | jq

# 输出：
# {
#   "name": "shell",
#   "duration_ms": 30104,
#   "args_size": 23,
#   "result_size": 0,
#   "error": "Tool shell timed out"
# }
```

### 8.5 LLM 调用慢/失败

```bash
# 测试连通性
dsh doctor

# 检查 API 响应时间
dsh bench --model deepseek-chat --iterations 3

# 切换 provider / model
dsh --model sonnet "test message"

# 启用 fallback
# config.yaml
fallback_models:
  - gpt-5-mini
  - claude-haiku-4
```

### 8.6 会话无法恢复

```bash
# 检查 checkpoint 文件
ls ~/.local/share/dsh/sessions/<id>/
cat ~/.local/share/dsh/sessions/<id>/checkpoint.json | jq .metadata

# 手动修复（JSON 损坏）
# 1. 备份
cp checkpoint.json checkpoint.json.bak
# 2. 尝试修复（移除多余字段）
jq 'del(.extraFields)' checkpoint.json > fixed.json
mv fixed.json checkpoint.json
# 3. 尝试恢复
dsh session resume <id>
```

### 8.7 性能突然下降

**诊断清单**：

```yaml
# 检查清单（按优先级）
1. LLM API 是否限流？
   curl -X POST https://api.deepseek.com/v1/chat/completions \
     -H "Authorization: Bearer $KEY" \
     -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}'

2. 网络延迟？
   ping api.deepseek.com
   mtr api.deepseek.com

3. 模型切换到更小的？
   dsh --model gpt-5-mini

4. 减少 history 长度？
   config.yaml → memory.history_limit: 20

5. 启用 prefix caching？
   config.yaml → llm_cache.enabled: true
```

### 8.8 常用诊断命令

```bash
# 健康检查
dsh doctor

# 看 plugin 加载情况
dsh plugin list --verbose

# 看活跃 tool 调用
dsh tool list

# 看会话列表
dsh session list --limit 20

# 跑性能基准
dsh bench --concurrent 5 --iterations 30

# 看日志（debug 级别）
DSH_LOG_LEVEL=debug dsh web 2>&1 | less

# heap dump
kill -USR1 <pid>  # 生成 heap-*.heapsnapshot

# CPU profile（v8）
dsh web --prof --prof-process
```

### 8.9 错误码速查

| 错误码 | 含义 | 解决方案 |
|---|---|---|
| `EADDRINUSE` | 端口占用 | 换端口：`dsh web --port 9090` |
| `401` | API Key 无效 | 更新 `~/.config/dsh/config.yaml` |
| `429` | 限流 | 等待 / 加 fallback / 申请提额 |
| `ECONNREFUSED` | 网络问题 | 检查代理 / VPN |
| `ERR_REQUIRE_ESM` | ESM 兼容问题 | 升级 Node 到 22+ |
| `CHECKPOINT_CORRUPTED` | 检查点损坏 | 删除会话或手动修复 JSON |

---

## 📚 附录：源码导航

```
packages/
├─ core/
│  ├─ src/
││   ├─ agent-loop.ts          ← 第 1 章
││   ├─ context.ts             ← 第 2 章
││   ├─ plugin-loader.ts       ← 第 2 章
││   ├─ service.ts             ← 第 2 章
││   ├─ event-bus.ts           ← 第 2 章
││   ├─ tool-dispatcher.ts     ← 第 3 章
││   ├─ checkpoint.ts          ← 第 6 章
││   ├─ memory/                ← 第 6 章
││   └─ mcp/                   ← 第 4 章
│  │     ├─ manager.ts
│  │     ├─ transport/stdio.ts
│  │     └─ protocol/json-rpc.ts
├─ server/
│  └─ src/
│     ├─ routes/chat.ts        ← 第 5 章（SSE）
│     └─ ws/agent-events.ts    ← 第 5 章（WebSocket）
├─ cli/
│  └─ src/main.ts              ← 启动入口
├─ models/
│  └─ src/openai.ts            ← OpenAI 兼容适配
├─ tools/
│  └─ src/file-edit.ts         ← 文件编辑工具
├─ skills/
│  └─ src/review.ts            ← /review Skill
└─ web/
   └─ src/composables/useChatStream.ts  ← 客户端
```

## 🎯 推荐阅读顺序

1. **第 1 章 Agent Loop**：最核心，所有功能的基础
2. **第 2 章 Cordis 容器**：理解扩展点
3. **第 3 章 Tool Dispatcher**：理解工具调用
4. **第 4 章 MCP 桥接**：理解外部工具集成
5. **第 5 章 流式响应**：理解 UI 实时性
6. **第 6 章 会话持久化**：理解恢复机制
7. **第 7 章 性能基准**：理解优化方向
8. **第 8 章 故障排查**：解决生产问题
