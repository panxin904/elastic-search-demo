---
title: Agent 优化路线图
date: 2026-09-17  # date-auto-injected
---

# 🚀 Agent 优化路线图

> 本章系统梳理 **dsh Agent 的 5 大优化目标 × 12 个具体方向 × 4 级优先级**，给出可量化的 KPI 指标、完整代码示例、实战优化案例。  
> 适用于所有用 dsh 构建的 Agent（PR Reviewer、Data Analyst、SRE、Onboarding 等）。

## 🎯 5 大优化目标

```
┌───────────────────────────────────────────────────────┐
│                                                        │
│  ⏱️ 1. 性能（快）    用户/系统角度                  │
│  💰 2. 成本（省）    商业角度                          │
│  🎯 3. 质量（准）    业务角度                          │
│  🛡️ 4. 可靠（稳）    工程角度                          │
│  🧠 5. 智能（智）    AI 角度                          │
│                                                        │
└───────────────────────────────────────────────────────┘
```

## ⏱️ 1. 性能优化

### 1.1 LLM 调用延迟

| 指标 | 当前基线 | 目标 | 优化手段 |
|---|---|---|---|
| **TTFT** | 800ms | ≤ 500ms | Streaming + Prefix Cache + 早期 dispatch |
| **吞吐** | 50 tok/s | 80 tok/s | 批量请求 + 模型选型 |
| **P95 延迟** | 5s | 2s | 工具并行 + 缓存 |

**核心优化**：边生成边工具调用

```typescript
// packages/core/src/agent-loop.ts（优化版）
async function* agentLoop(ctx, message) {
  // ... 初始化 ...

  while (iteration++ < maxIter) {
    // ===== 关键优化 1：边生成边工具调用 =====
    const stream = ctx.model.chatStream({ messages, tools })
    let pendingToolCall: any = null

    for await (const chunk of stream) {
      if (chunk.type === 'content') yield { type: 'content_delta', text: chunk.text }

      if (chunk.type === 'tool_call_start') {
        // 不等流结束就开始执行工具
        pendingToolCall = chunk
      }

      if (chunk.type === 'tool_call_complete') {
        // ===== 关键优化 2：直接 fire 并行执行 =====
        const result = await toolDispatcher.dispatch(chunk.name, chunk.args, {
          signal: ctx.abortController.signal,
        })
        // 工具结果已经准备好，下一轮 LLM 调用立即可用
      }
    }

    // ... 继续循环
  }
}
```

### 1.2 工具调度优化

```yaml
# preset.yaml
performance:
  tool_dispatch:
    # 结果缓存（相同参数不重复执行）
    result_cache:
      enabled: true
      max_size: 1000
      ttl: 3600

    # 并发控制
    concurrency:
      max_parallel: 8                # 最多 8 个工具并行
      per_tool_limit:
        npm_install: 1              # 装包串行
        npm_test: 1
        read_file: 100              # 读文件可大量并发
        shell: 5                    # shell 命令适度并发

    # 超时分级
    timeouts:
      read_file: 10s
      write_file: 10s
      shell: 60s
      web_fetch: 30s
      web_search: 30s

    # 预加载（启动时 import）
    preload:
      - read_file
      - write_file
      - search_code
```

### 1.3 上下文窗口优化

```typescript
// packages/core/src/context-manager.ts
export class ContextManager {
  private historyLimit = 30          // 保留最近 30 轮
  private compressThreshold = 20      // 超过 20 轮触发压缩

  async compress(messages: Message[]): Promise<Message[]> {
    if (messages.length < this.compressThreshold) return messages

    // 保留 system + 最近 N 轮
    const system = messages.filter(m => m.role === 'system')
    const recent = messages.slice(-this.historyLimit)

    // 中间部分压缩成 summary
    const middleToCompress = messages.slice(system.length, -this.historyLimit)
    const summary = await this.llm.complete({
      prompt: `压缩以下对话历史为 200 字内的摘要，保留关键决策和工具调用结果：\n\n${this.formatMessages(middleToCompress)}`,
      model: 'gpt-5-mini',
    })

    return [
      ...system,
      { role: 'system', content: `## 历史摘要\n${summary}` },
      ...recent,
    ]
  }

  async smartTrim(messages: Message[]): Promise<Message[]> {
    // 工具结果 >2KB 自动摘要
    return messages.map(m => {
      if (m.role === 'tool' && m.content.length > 2000) {
        return {
          ...m,
          content: m.content.slice(0, 1000) + '\n...[省略]...\n' + m.content.slice(-500),
        }
      }
      return m
    })
  }
}
```

### 1.4 启动优化

```typescript
// packages/core/src/lazy-loader.ts
export class LazyPluginLoader {
  private loaded = new Set<string>()

  async load(plugins: PluginSpec[]): Promise<void> {
    // 1. 先加载核心（必须）
    const core = plugins.filter(p => p.priority === 'core')
    await Promise.all(core.map(p => this.instantiate(p)))

    // 2. 其他插件延后到第一次使用时
    const others = plugins.filter(p => p.priority !== 'core')
    for (const spec of others) {
      // 只注册代理，实际加载延后
      this.registry.register(spec.name, new LazyProxy(spec))
    }

    // 3. 预热 LLM 连接
    this.warmupLLMConnection()
  }

  private async warmupLLMConnection() {
    // 后台异步建立连接
    setTimeout(async () => {
      await this.ctx.model.chat({
        messages: [{ role: 'user', content: 'ping' }],
        max_tokens: 1,
      })
    }, 100)
  }
}
```

## 💰 2. 成本优化

### 2.1 模型路由（按难度分级）

```typescript
// packages/core/src/model-router.ts
type ModelTier = 'mini' | 'chat' | 'reasoner' | 'sonnet' | 'opus'

interface TaskMeta {
  type: string
  complexity: number     // 0-10
  estimatedTokens: number
  userPreference?: ModelTier
}

const MODEL_CONFIG = {
  mini:     { id: 'gpt-5-mini',         cost: { in: 0.10, out: 0.40 }, latency: 200 },
  chat:     { id: 'deepseek-chat',       cost: { in: 0.27, out: 1.10 }, latency: 800 },
  reasoner: { id: 'deepseek-reasoner',  cost: { in: 0.55, out: 2.19 }, latency: 3000 },
  sonnet:   { id: 'claude-sonnet-4.5',   cost: { in: 3, out: 15 }, latency: 1000 },
  opus:     { id: 'claude-opus-4',      cost: { in: 15, out: 75 }, latency: 1500 },
}

export function routeModel(meta: TaskMeta, ctx: Context): ModelTier {
  // 用户显式偏好优先
  if (meta.userPreference) return meta.userPreference

  // 简单任务规则
  if (meta.type === 'simple_qa' || meta.complexity < 3) return 'mini'

  // 推理任务必须用 reasoner
  if (meta.type === 'reasoning' || meta.type === 'math') return 'sonnet'

  // 复杂代码/架构任务用 sonnet
  if (meta.type === 'code_architecture' && meta.complexity > 7) return 'opus'

  // 默认 chat
  return 'chat'
}

// 在 Agent Loop 中使用
const tier = routeModel(taskMeta, ctx)
const model = MODEL_CONFIG[tier]
ctx.logger.info('model routed', { tier, complexity: taskMeta.complexity })
```

### 2.2 多级缓存策略

```yaml
# preset.yaml
cache:
  strategy: multi_level

  # L1 内存缓存（响应 < 1ms）
  l1_memory:
    enabled: true
    max_entries: 500
    hash: "prompt_hash + model_id"

  # L2 磁盘缓存（embedding 索引）
  l2_disk:
    enabled: true
    path: "~/.local/share/dsh/cache/llm"
    backend: sqlite-vec
    ttl: 7d

  # L3 Provider 缓存（DeepSeek prompt cache）
  l3_provider:
    enabled: true
    cache_breakpoints:
      - system_prompt
      - tool_definitions

# 预期效果
# 整体缓存命中率：40%+，节省 30%+ 成本
```

**实现**：

```typescript
// packages/core/src/cache.ts
export class MultiLevelCache {
  private l1 = new LRUCache<string, any>({ max: 500 })

  async get(prompt: string, model: string): Promise<any | null> {
    const key = this.hash(prompt + model)

    // L1：内存
    if (this.l1.has(key)) return this.l1.get(key)

    // L2：磁盘
    const diskResult = await this.l2.get(key)
    if (diskResult) {
      this.l1.set(key, diskResult)  // 提升到 L1
      return diskResult
    }

    return null
  }

  async set(prompt: string, model: string, response: any): Promise<void> {
    const key = this.hash(prompt + model)

    // L1 + L2 都存
    this.l1.set(key, response)
    await this.l2.set(key, response, { ttl: 7 * 24 * 3600 })
  }
}
```

### 2.3 折扣时段调度

```typescript
// packages/core/src/discount-scheduler.ts
export class DiscountScheduler {
  // DeepSeek 折扣时段：UTC 16:30 - 00:30
  isDiscountPeriod(): boolean {
    const now = new Date()
    const utcHour = now.getUTCHours()
    const utcMin = now.getUTCMinutes()
    const currentMinutes = utcHour * 60 + utcMin

    return currentMinutes >= 16 * 60 + 30 || currentMinutes < 30
  }

  // 任务队列：非紧急任务排到折扣时段
  async schedule(task: Task): Promise<void> {
    if (task.priority === 'urgent' || !this.isDiscountPeriod()) {
      return this.executeNow(task)
    }

    // 排到下一个折扣时段
    const delay = this.nextDiscountStart() - Date.now()
    ctx.logger.info('scheduling to discount window', { delay_ms: delay })

    setTimeout(() => this.executeNow(task), delay)
  }

  private nextDiscountStart(): number {
    // 计算下一个 UTC 16:30
    const now = new Date()
    const target = new Date(now)
    target.setUTCHours(16, 30, 0, 0)
    if (now.getTime() > target.getTime()) target.setUTCDate(target.getUTCDate() + 1)
    return target.getTime()
  }
}
```

## 🎯 3. 质量优化

### 3.1 多层评估体系

```typescript
// packages/core/src/evaluator.ts
export class Evaluator {
  async evaluate(output: AgentOutput, task: Task): Promise<EvaluationResult> {
    const results: EvaluationResult = {
      passed: true,
      scores: {},
    }

    // L1 语法层
    if (task.type === 'code') {
      const syntaxCheck = await this.checkSyntax(output.code)
      results.scores.syntax = syntaxCheck.score
      if (syntaxCheck.score < 0.9) results.passed = false
    }

    // L2 语义层（执行测试）
    if (task.testCommand) {
      const testResult = await this.executeTest(task.testCommand)
      results.scores.test = testResult.success ? 1 : 0
      if (!testResult.success) results.passed = false
    }

    // L3 任务层（用户采纳率）
    const userAcceptRate = await this.getUserAcceptRate(task.id)
    results.scores.acceptance = userAcceptRate

    return results
  }

  private async executeTest(cmd: string): Promise<{ success: boolean; output: string }> {
    try {
      const { stdout } = await exec(cmd, { timeout: 60_000 })
      return { success: true, output: stdout }
    } catch (e: any) {
      return { success: false, output: e.stderr || e.message }
    }
  }
}
```

### 3.2 自动重试与降级

```typescript
// packages/core/src/executor.ts
export async function executeWithRetry(task: Task): Promise<AgentOutput> {
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const result = await executeAgentLoop(task)

      // 验证
      const eval_result = await evaluator.evaluate(result, task)
      if (eval_result.passed) return result

      // 不通过：换 prompt 重试
      task.feedback = this.extractFeedback(eval_result)
      ctx.logger.warn(`attempt ${attempt} failed validation, retrying`, eval_result.scores)
    } catch (e) {
      if (attempt === 3) {
        // 最终降级
        return await executeFallback(task)
      }
      await sleep(1000 * 2 ** attempt)
    }
  }
}

async function executeFallback(task: Task): Promise<AgentOutput> {
  ctx.logger.error('all attempts failed, executing fallback', { task })

  // 降级策略：
  // 1. 切到更小但更稳的模型
  // 2. 用最简 prompt
  // 3. 限制工具集
  // 4. 告知用户无法完成

  return {
    content: '抱歉，经过3 次尝试仍无法完成任务。请提供更详细的指令。',
    is_fallback: true,
  }
}
```

### 3.3 多模型投票

```typescript
// packages/core/src/multi-model-vote.ts
export async function multiModelVote(prompt: string, models: ModelTier[]): Promise<string> {
  // 并行跑多个模型
  const results = await Promise.all(
    models.map(async (model) => {
      const response = await ctx.model.chat({
        model: MODEL_CONFIG[model].id,
        messages: [{ role: 'user', content: prompt }],
      })
      return { model, output: response.content }
    })
  )

  // 一致性检查
  const uniqueOutputs = [...new Set(results.map(r => r.output))]

  if (uniqueOutputs.length === 1) {
    // 完全一致 → 采纳
    return uniqueOutputs[0]
  }

  if (uniqueOutputs.length === 2) {
    // 2:1 多数票
    const counts = new Map<string, number>()
    for (const r of results) {
      counts.set(r.output, (counts.get(r.output) || 0) + 1)
    }
    const winner = [...counts.entries()].sort((a, b) => b[1] - a[1])[0]
    if (winner[1] >= 2) return winner[0]
  }

  // 都不同 → 用最强模型裁决
  const arbitrate = await ctx.model.chat({
    model: MODEL_CONFIG.opus.id,
    prompt: `以下是多个模型对同一问题的回答，请选出最优：\n\n${results.map((r, i) => `回答 ${i + 1} (${r.model}):\n${r.output}\n`).join('\n')}`,
  })
  return arbitrate.content
}
```

## 🛡️ 4. 可靠性优化

### 4.1 Failover 配置

```yaml
# preset.yaml
reliability:
  failover_strategy:
    # 模型失败 → 降级到备用模型
    model_failure:
      primary: sonnet
      fallbacks: [chat, mini]

    # 工具失败 → 重试 + 跳过
    tool_failure:
      retry_count: 3
      retry_backoff: exponential
      skip_on_failure: false        # 失败不跳过，让 LLM 知道

    # API 限流 → 自动等待
    rate_limit:
      strategy: wait_and_retry
      max_wait_seconds: 60

    # 网络断开 → 缓存到本地，恢复后重发
    network_failure:
      queue_locally: true
      queue_path: ~/.local/share/dsh/queue/

# 心跳监控
health_check:
  interval: 30s
  timeout: 10s
  actions_on_failure: [restart, alert]
```

### 4.2 优雅降级

```typescript
// packages/core/src/graceful-degradation.ts
export class GracefulDegradation {
  async execute(task: Task): Promise<AgentOutput> {
    const strategy = this.chooseStrategy(task)

    switch (strategy) {
      case 'full':
        return this.fullExecution(task)

      case 'reduced':
        // 降级 1：禁用昂贵工具
        return this.executeWithoutExpensiveTools(task)

      case 'minimal':
        // 降级 2：只保留最核心功能
        return this.executeMinimal(task)

      case 'cached':
        // 降级 3：用缓存结果
        return this.executeFromCache(task)

      case 'failure':
        return this.failureResponse(task)
    }
  }

  private chooseStrategy(task: Task): ExecutionStrategy {
    // 系统压力高 → 降级
    if (this.cpuUsage() > 80) return 'reduced'
    if (this.memoryPressure() > 0.9) return 'minimal'

    // API 限流 → 降级
    if (this.isRateLimited()) return 'cached'

    // 任务关键度高 → 全功能
    if (task.priority === 'critical') return 'full'

    return 'full'
  }
}
```

### 4.3 监控告警

```yaml
# prometheus.yml 配置
scrape_configs:
  - job_name: 'dsh-agents'
    static_configs:
      - targets: ['dsh.local:9090']
    metrics_path: /metrics
```

```typescript
// packages/core/src/metrics.ts
import { Counter, Histogram, Gauge, register } from 'prom-client'

export const metrics = {
  // 请求量
  requestsTotal: new Counter({
    name: 'dsh_requests_total',
    help: 'Total requests',
    labelNames: ['agent', 'task_type', 'status'],
  }),

  // 延迟
  requestDuration: new Histogram({
    name: 'dsh_request_duration_seconds',
    help: 'Request duration',
    buckets: [0.1, 0.5, 1, 2, 5, 10, 30],
    labelNames: ['agent'],
  }),

  // Token 用量
  tokensUsed: new Counter({
    name: 'dsh_tokens_total',
    help: 'Total tokens used',
    labelNames: ['agent', 'model', 'direction'],  // direction: prompt/completion
  }),

  // 任务成功率
  taskSuccess: new Counter({
    name: 'dsh_task_success_total',
    help: 'Task success',
    labelNames: ['agent', 'task_type'],
  }),

  // 工具调用延迟
  toolDuration: new Histogram({
    name: 'dsh_tool_duration_seconds',
    help: 'Tool call duration',
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 5],
    labelNames: ['agent', 'tool'],
  }),

  // 当前活跃任务
  activeTasks: new Gauge({
    name: 'dsh_active_tasks',
    help: 'Currently active tasks',
    labelNames: ['agent'],
  }),

  // 错误率（用于告警）
  errorsTotal: new Counter({
    name: 'dsh_errors_total',
    help: 'Total errors',
    labelNames: ['agent', 'error_type'],
  }),
}

// 在 tool handler 中：
metrics.toolDuration.observe({ agent, tool: name }, duration)
metrics.errorsTotal.inc({ agent, error_type: e.constructor.name })
```

### 4.4 自动恢复（checkpoint + resume）

```typescript
// packages/server/src/routes/session.ts
fastify.post('/api/session/resume', async (req, reply) => {
  const { session_id } = req.body

  // 1. 加载 checkpoint
  const checkpoint = await checkpointManager.load(session_id)
  if (!checkpoint) {
    return reply.code(404).send({ error: 'Session not found' })
  }

  // 2. 检查 checkpoint 完整性
  if (Date.now() - checkpoint.metadata.lastUpdate > 7 * 24 * 3600 * 1000) {
    return reply.code(410).send({ error: 'Session too old, expired' })
  }

  // 3. 恢复 Context
  const ctx = await restoreContext(checkpoint)

  // 4. 继续 Agent Loop
  return reply.send({
    session_id,
    status: 'resumed',
    from_iteration: checkpoint.iteration,
    remaining: checkpoint.metadata.maxIterations - checkpoint.iteration,
  })
})
```

## 🧠 5. 智能化优化

### 5.1 记忆系统（被动反馈 + 自动进化）

```typescript
// plugins/agent-memory/src/passive-feedback.ts
export class PassiveFeedbackCollector {
  static inject = ['agent_memory', 'file_watcher', 'git_watcher']

  async start() {
    // 1. 监听文件修改（最强信号）
    this.ctx.fileWatcher.on('change', async (event) => {
      await this.handleFileChange(event)
    })

    // 2. 监听 git commit
    this.ctx.gitWatcher.on('commit', async (commit) => {
      await this.handleCommit(commit)
    })

    // 3. 监听任务完成 → 自动验证
    this.ctx.on('task:completed', async (task) => {
      await this.verifyAndLearn(task)
    })

    // 4. 每周统计模式
    setInterval(() => this.detectPatterns(), 7 * 24 * 3600 * 1000)
  }

  private async handleFileChange(event: FileChangeEvent) {
    const recentOutputs = await this.getRecentAgentOutputs({
      windowMs: 5 * 60 * 1000,
      affectedFile: event.path,
    })

    for (const output of recentOutputs) {
      const agentEdit = output.fileEdits[event.path]
      if (!agentEdit) continue

      const diff = computeDiff(agentEdit.after, event.newContent)

      if (diff.similarity > 0.95) {
        // 完全接受
        await this.ctx.agent_memory.reinforce(output.memoryId, +0.15, 'accepted')
      } else if (diff.similarity > 0.5) {
        // 部分接受 → 学习用户的修改
        const mods = extractModifications(agentEdit.after, event.newContent)
        await this.ctx.agent_memory.record({
          type: 'preference',
          content: `用户修改风格: ${mods.description}`,
        })
        await this.ctx.agent_memory.reinforce(output.memoryId, +0.05, 'partial_accepted')
      } else {
        // 拒绝
        await this.ctx.agent_memory.reinforce(output.memoryId, -0.20, 'rejected')
      }
    }
  }

  private async handleCommit(commit: GitCommit) {
    const recent = await this.getRecentAgentOutputs({ windowMs: 30 * 60 * 1000 })
    for (const output of recent) {
      if (commit.message.toLowerCase().includes(output.taskSummary.toLowerCase())) {
        await this.ctx.agent_memory.reinforce(output.memoryId, +0.25, 'committed')
      }
    }
  }

  private async verifyAndLearn(task: CompletedTask) {
    if (!task.verifyCommand) return

    const result = await exec(task.verifyCommand, { timeout: 60_000 })

    if (result.exitCode === 0) {
      await this.ctx.agent_memory.reinforce(task.sourceMemoryId, +0.20, 'auto_verified')
    } else {
      await this.ctx.agent_memory.reinforce(task.sourceMemoryId, -0.30, 'auto_failed')
      await this.ctx.agent_memory.record({
        type: 'learning',
        content: `失败案例: ${task.description}\n错误: ${result.stderr.slice(0, 500)}`,
        confidence: 0.85,
      })
    }
  }

  private async detectPatterns() {
    // 每周：聚类相似经验，提炼用户偏好
    const recentMemories = await this.ctx.agent_memory.listRecent({ days: 30, min_confidence: 0.6 })

    // 调用 LLM 提炼模式
    const patterns = await this.ctx.model.complete({
      prompt: `从以下 ${recentMemories.length} 条历史记忆中提取 5-10 个共同模式：\n\n${this.formatMemories(recentMemories)}`,
      model: 'gpt-5-mini',
    })

    await this.ctx.agent_memory.record({
      type: 'pattern',
      content: patterns,
      confidence: 0.8,
      scope: 'user',
    })
  }
}
```

### 5.2 工具选择优化

```typescript
// packages/core/src/tool-selector.ts
export class ToolSelector {
  // 基于任务描述，自动选 top-3 工具
  async selectRelevantTools(
    taskDescription: string,
    allTools: Tool[],
    topK = 10
  ): Promise<Tool[]> {
    // 1. embedding 任务描述
    const taskEmbedding = await this.embed(taskDescription)

    // 2. 计算每个工具的相关性
    const scored = await Promise.all(
      allTools.map(async (tool) => {
        const toolEmbedding = await this.embed(tool.description)
        const similarity = cosineSimilarity(taskEmbedding, toolEmbedding)
        return { tool, similarity }
      })
    )

    // 3. 加上使用统计权重
    const usageStats = await this.getToolUsageStats()
    return scored
      .sort((a, b) => {
        const scoreA = a.similarity * 0.7 + (usageStats[a.tool.name] || 0) * 0.3
        const scoreB = b.similarity * 0.7 + (usageStats[b.tool.name] || 0) * 0.3
        return scoreB - scoreA
      })
      .slice(0, topK)
      .map(s => s.tool)
  }
}
```

### 5.3 自我反思

```typescript
// packages/core/src/self-reflection.ts
export async function* agentLoopWithReflection(ctx, message) {
  let iteration = 0
  while (iteration++ < maxIter) {
    const response = await ctx.model.chatStream({ messages, tools })

    // ... 处理响应和工具调用 ...

    // 每 5 轮触发一次反思
    if (iteration % 5 === 0 && needsReflection(currentTask)) {
      const reflection = await ctx.model.complete({
        prompt: `反思：我们是否走在正确道路上？

任务: ${currentTask.description}
当前进度: ${summarizeProgress(messages)}
已用轮次: ${iteration}

问题：
1. 我们是否还在解决正确的问题？
2. 是否有更高效的方法？
3. 是否应该尝试不同的工具？

输出 100 字内的反思：`,
        model: 'sonnet',
      })

      messages.push({
        role: 'system',
        content: `## 自我反思\n${reflection}`,
      })

      yield { type: 'reflection', content: reflection }
    }
  }
}

function needsReflection(task: Task): boolean {
  return task.complexity >= 6 || task.attemptCount > 1
}
```

## 📊 6. 可量化的 KPI 指标

### 6.1 性能指标

| 指标 | 当前基线 | 3 月目标 | 6 月目标 | 测量方式 |
|---|---|---|---|---|
| **响应延迟 P50** | 1.5s | 1.0s | 800ms | Prometheus histogram |
| **响应延迟 P95** | 5s | 3s | 2s | Prometheus histogram |
| **TTFT** | 800ms | 500ms | 300ms | Custom timer |
| **吞吐（tokens/s）** | 50 | 70 | 100 | LLM 响应时间 |
| **启动时间** | 3s | 2s | 1s | 自定义计时 |

### 6.2 成本指标

| 指标 | 当前基线 | 3 月目标 | 6 月目标 | 测量方式 |
|---|---|---|---|---|
| **单任务成本** | $0.10 | $0.05 | $0.03 | Token 累加 |
| **月成本** | $500 | $250 | $150 | LLM Provider 账单 |
| **缓存命中率** | 10% | 40% | 60% | Cache 命中统计 |
| **模型路由节省** | 0% | 40% | 60% | Mini 模型占比 |

### 6.3 质量指标

| 指标 | 当前基线 | 3 月目标 | 6 月目标 | 测量方式 |
|---|---|---|---|---|
| **任务成功率** | 70% | 85% | 92% | 任务完成统计 |
| **用户采纳率** | 60% | 80% | 90% | 隐式反馈 |
| **输出准确率** | 75% | 90% | 95% | 评估器 |
| **错误率** | 5% | 2% | 1% | 异常日志 |

### 6.4 可靠性指标

| 指标 | 当前基线 | 3 月目标 | 6 月目标 | 测量方式 |
|---|---|---|---|---|
| **可用性 SLA** | 95% | 99% | 99.5% | Uptime 监控 |
| **MTTR** | 30min | 10min | 5min | 故障日志 |
| **恢复成功率** | 80% | 95% | 99% | Resume 成功数 |

## 🔥 7. 优先级清单（4 级）

### P0（立即做，立竿见影）

```
□ 模型路由（按难度分级）
  └ 预期收益：成本 -50%
  └ 实现成本：1 天

□ 启用 prefix cache
  └ 预期收益：速度 +30%，成本 -20%
  └ 实现成本：0.5 天（仅配置）

□ 任务结果自动验证（npm test / lint）
  └ 预期收益：质量 +15%
  └ 实现成本：1 天

□ Failover fallback model
  └ 预期收益：可用性 +10%
  └ 实现成本：0.5 天
```

### P1（1 个月内）

```
□ 工具结果截断
□ 并发控制
□ Prometheus 监控 + 告警
□ 上下文压缩
□ 智能询问 UI
□ 被动反馈采集（file/git watcher）
```

### P2（3 个月内）

```
□ 记忆系统完善（被动反馈 + 自动进化）
□ 多模型投票
□ 自我反思能力
□ 工具智能选择
□ 跨会话模式检测
```

### P3（6 个月内）

```
□ 主动学习（新插件建议）
□ 工具自动发现
□ OpenTelemetry 集成
□ 自动故障转移（多区域）
□ 自适应模型选择（基于任务表现）
```

## 🎯 8. 实战优化案例：PR Reviewer Agent

### 初始状态（Day 1）

```
指标：
├ 任务成功率：65%
├ 单任务成本：$0.15（用 sonnet）
├ 平均响应时间：4s
├ 用户满意度：50%
└ 失败原因：30% 安全问题漏检 / 25% 风格不符 / 45% 其他
```

### 3 个月优化（按优先级）

**Month 1：P0 优化**
```yaml
# 1. 模型路由
- 简单 lint 检查 → gpt-5-mini
- 一般 review → deepseek-chat
- 安全/性能深度审查 → sonnet

# 2. prefix cache + 任务验证
- 启用 prefix cache
- 改完后跑 npm test / lint 自动验证

# 3. 失败降级
- 主模型失败 → 自动切 chat
```

**Month 2：P1 优化**
```yaml
# 4. 被动反馈
- 监听 commit：用户采纳的 commit 强化记忆
- 监听文件修改：分析被修改的部分学习

# 5. 监控告警
- Prometheus 接入
- 告警：错误率 > 5% / 延迟 > 10s
```

**Month 3：P2 优化**
```yaml
# 6. 记忆系统
- 团队规范沉淀（review-style-guide）
- 历史 PR 模式识别

# 7. 多模型投票
- 关键 PR 用 sonnet + chat 投票
```

### 3 个月后效果

```
指标对比：
├ 任务成功率：65% → 88%
├ 单任务成本：$0.15 → $0.06（路由后 -60%）
├ 平均响应时间：4s → 2s
├ 用户满意度：50% → 85%
├ 团队规范一致性：40% → 90%
└ 新成员上手时间：2 周 → 3 天

ROI 估算：
├ 节省成本：$0.09 × 1000 PR/月 = $90/月
├ 节省时间：每 PR 节省 20 分钟 × 100 = $50/月人力成本
└ 总收益：~$140/月（投入 1 人 3 周 = 60 小时）
```

## 🎓 一句话总结

> **5 大目标（性能/成本/质量/可靠/智能）× 12 个优化方向 × 4 级优先级 × 可量化 KPI**。
>
> **立即做 P0**（模型路由 + prefix cache + 自动验证 + failover）→ 1 周内立竿见影  
> **1 月做 P1**（监控 + 被动反馈）→ 稳定运行基础  
> **3 月做 P2**（记忆 + 多模型投票 + 反思）→ 智能化跃迁  
> **6 月做 P3**（主动学习 + 全链路追踪）→ 行业领先

---

## 📚 实践资源

- Prometheus Grafana: 监控 Agent 全链路
- OpenLLMetry: LLM 调用追踪
- DeepSeek 文档: https://api-docs.deepseek.com
- Anthropic Prompt Cache: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
