---
title: WebSocket / SSE
---

# WebSocket / SSE

## 🌐 三种实时方案

| | 轮询 (Polling) | SSE (Server-Sent Events) | WebSocket |
|--|--------|--------|-------------|
| 协议 | HTTP 循环 | HTTP（单向长连接） | WS 升级 |
| 方向 | 客户端 → 服务端 | 服务端 → 客户端 | 双工 |
| 复杂度 | 低 | 低 | 中 |
| 重连 | 应用层处理 | 浏览器自动 | 自己实现 |
| 二进制 | ✅ | ❌ 仅文本 | ✅ |
| 兼容 | 全 | 全 | 全 |
| 适合 | 状态更新不频繁 | 通知、进度、行情 | 聊天、协作 |

## 📡 WebSocket

### 浏览器 API

```ts
const ws = new WebSocket('wss://example.com/socket')

ws.onopen = () => {
  ws.send(JSON.stringify({ type: 'hello', name: 'alice' }))
}

ws.onmessage = (e) => {
  console.log('got:', JSON.parse(e.data))
}

ws.onclose = () => { /* reconnect */ }
```

### Node 服务端（ws 库）

```ts
import { WebSocketServer } from 'ws'

const wss = new WebSocketServer({ port: 8080 })

wss.on('connection', (ws) => {
  ws.on('message', (data) => {
    const msg = JSON.parse(data.toString())
    console.log('recv:', msg)

    // 广播
    wss.clients.forEach(client => {
      if (client.readyState === ws.OPEN) client.send(JSON.stringify({ echo: msg }))
    })
  })
})
```

### 高级库

- **Socket.IO**：自动重连、rooms、broadcast、轮询 fallback
- **µWebSockets.js**：超快（V8-native）
- **@fastify/websocket**：Fastify 插件

## 🌊 SSE (Server-Sent Events)

**服务端单向流**，适合"只读"通知。

```ts
// Node 服务端
app.get('/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream')
  res.setHeader('Cache-Control', 'no-cache')
  res.setHeader('Connection', 'keep-alive')

  const interval = setInterval(() => {
    res.write(`data: ${JSON.stringify({ ts: Date.now() })}\n\n`)
  }, 1000)

  req.on('close', () => clearInterval(interval))
})
```

```js
// 浏览器
const es = new EventSource('/events')
es.onmessage = (e) => console.log(e.data)
es.onerror = (e) => console.warn('SSE error', e)
```

**优势**：
- HTTP/1.1 兼容
- 浏览器自动重连（`retry` 字段）
- 单向时省心

**限制**：
- 文本 only
- 单向（服务端 → 客户端）
- 浏览器最多 6 个并发连接 / origin

## 🎯 选型

| 场景 | 选择 |
|------|------|
| 行情、进度、通知 | SSE |
| 聊天、协作、白板 | WebSocket |
| WebRTC 信令 | WebSocket |
| 服务端单向日志 | SSE |
| IoT 控制 | MQTT / WebSocket |

## 📚 框架集成

### Next.js + SSE

```ts
// app/api/events/route.ts
export async function GET() {
  const stream = new ReadableStream({
    start(controller) {
      const interval = setInterval(() => {
        controller.enqueue(`data: ${Date.now()}\n\n`)
      }, 1000)
      return () => clearInterval(interval)
    }
  })

  return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' } })
}
```

### Express + ws

见上方 Node 示例。

## 🔗 下一步

- [GraphQL](/09-data/graphql)
- [REST 规范 / OpenAPI](/09-data/rest)
- [运行时性能](/12-perf/runtime)
