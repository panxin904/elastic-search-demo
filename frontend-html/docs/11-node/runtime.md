---
title: Node 运行时
date: 2026-08-15  # date-auto-injected
---

# Node 运行时

## 🎯 Node.js 是什么

Ryan Dahl 2009 年发布：用 **Chrome V8 引擎 + libuv 异步 I/O** 让 JS 跑在服务端。

```
应用层（JS） — V8 编译执行
↓
Node Core（C++） — File System / Net / Crypto / …
↓
libuv — 事件循环 + 线程池 + 异步 I/O
↓
系统调用（OS）
```

## 🧠 关键概念

### 单线程 ≠ 真"单线程"

- **JS 主线程**：单线程（一个调用栈）
- **底层 I/O**：libuv 维护**线程池**（默认 4 个）+ OS 异步 syscall
- CPU-heavy 会阻塞主线程 → 用 `worker_threads` / `child_process`

### Event Loop 阶段

```
   ┌───────────────────────────┐
┌─→│           timers          │ setTimeout / setInterval
│  ├───────────────────────────┤
│  │     pending callbacks     │ 部分 I/O 回调
│  ├───────────────────────────┤
│  │       idle, prepare       │ 内部
│  ├───────────────────────────┤
│  │          poll             │ 获取新的 I/O 事件
│  ├───────────────────────────┤
│  │          check            │ setImmediate
│  └───────────────────────────┘
```

`process.nextTick()` 不在阶段中，会在每个阶段切换前清空。

## 🚀 模块系统

```js
// CommonJS（传统）
const fs = require('fs')
module.exports = {}

// ESM（新）
import fs from 'node:fs'
export default {}
```

Node 22+ 默认 ESM。

## ⚙️ 内置命令

```bash
node app.js                    # 启动
node --watch                   # 文件变化重启（Node 18+）
node --env-file=.env app.js    # 加载 .env 文件
node --inspect app.js          # DevTools 调试
node --loader tsx app.ts        # TS loader
```

## 📦 现代框架：使用现成的 Fastify / Hono / NestJS

不要裸写 HTTP handler，但**业务 / 工具型小服务**裸写依然 ok：

```ts
import { createServer } from 'node:http'

createServer((req, res) => {
  res.end('hello')
}).listen(3000)
```

## 📊 内置工具

| 工具 | 作用 |
|------|------|
| `--prof` | V8 性能分析 |
| `clinic.js` | 火焰图、性能瓶颈定位 |
| `node --inspect` + Chrome DevTools | 断点调试 |
| `process.memoryUsage()` | 内存监控 |
| `perf_hooks` | 性能埋点 |

## ⚡ 性能调优基础

```
1. 用最新 LTS（Node 20/22）：V8 / V8-Turbofan 每年变快
2. 启用 ESM + Native Modules：减少解析开销
3. fast-json-stringify / fast-querystring 替换标准库
4. ioredis 而非 redis
5. undici 替代 fetch（必要时）
6. 监控事件循环 lag（monitor-event-loop-delay）
```

## 🛡️ 安全

```bash
npm audit --production
```

- 不用 `--inspect-prod` 在生产开调试端口
- 避免 `eval` / `Function()`
- env 不要落到代码里：用 `process.env`
- 严格使用 zod / valibot 校验 request

## 🔗 下一步

- [Express / Koa](/11-node/express)
- [NestJS](/11-node/nestjs)
- [Fastify / Hono](/11-node/fastify)
- [Serverless](/11-node/serverless)
