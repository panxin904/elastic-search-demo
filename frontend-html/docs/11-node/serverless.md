---
title: Serverless / Edge
---

# Serverless / Edge

## ☁️ Serverless 概念

按调用计费、无服务器管理、自动扩缩容。

```
传统 VM：
  - 运维 OS
  - 配置 autoscale
  - 长连接
  - 闲置成本高

Serverless：
  - 平台管理 OS
  - 自动扩缩容（毫秒级）
  - 请求级冷启动 / 短生命周期
  - 按调用 / CPU·ms 计费
```

## 🧩 主流平台

| 平台 | 函数 | Edge |
|------|------|------|
| AWS | Lambda | Lambda@Edge / CloudFront Functions |
| Vercel | Functions | Edge Functions (V8 isolates) |
| Cloudflare | Workers | Workers KV / Durable Objects |
| Deno Deploy | Deno | ✅ |
| Netlify | Functions | Deno-based Edge |
| Aliyun | FC | EdgeRoutine |

## ⚡ Edge vs Origin

```
Edge 函数：
  - 部署在全球 CDN 节点
  - V8 isolates / WASM（启动 <5ms）
  - 受限 API（无 Node fs / 部分 npm 包）
  - 适合：SSR、auth、redirect、A/B

Origin 函数：
  - 部署在单区域
  - 完整 Node 兼容
  - 适合：长时任务、复杂计算
```

## 🚀 Vercel Edge Functions

```ts
// app/api/hello/route.ts (Next.js App Router)
export const runtime = 'edge'

export async function GET(req: Request) {
  const geo = req.geo  // Vercel 注入
  return Response.json({
    msg: `Hello from ${geo.city}, ${geo.country}`
  })
}
```

## ⚡ Cloudflare Workers

```ts
export default {
  async fetch(request: Request, env: Env) {
    const url = new URL(request.url)
    if (url.pathname === '/api/users') {
      return Response.json([{ id: 1 }])
    }
    return new Response('Not Found', { status: 404 })
  }
}
```

支持 KV、R2、D1、Durable Objects、Cron Triggers。

## 🌐 Hono 跨运行时

Hono 的 API 是 Web 标准，可以在多种 Serverless 平台运行：

```ts
import { Hono } from 'hono'
const app = new Hono()
app.get('/api/users', (c) => c.json([]))

// Cloudflare Workers
export default app

// Vercel Edge
export const GET = app.fetch
export const POST = app.fetch

// AWS Lambda (Node 20+)
export const handler = app.fetch
```

## 📊 冷启动 / 内存限制

| 平台 | 冷启动 | 内存上限 | 单次时长 |
|------|--------|---------|---------|
| Cloudflare Workers | <5ms | 128MB | 30s（CPU） |
| Vercel Edge | <50ms | 128MB | 25s (pro) |
| AWS Lambda | ~200ms | 10GB | 15min |
| Deno Deploy | <10ms | 256MB | 1min |

**优化冷启动**：
- Bundle 小（不要 tree-shake 反向）
- 避免冷启动慢的库（aws-sdk）
- 用 edge adapter

## 🧰 适合场景

| 场景 | 选择 |
|------|------|
| SaaS API | Lambda / Workers |
| 静态站 / SSR 边缘 | Vercel / Cloudflare |
| 实时数据 / 流 | Durable Objects |
| 短任务（webhook / 图像 resize） | Lambda / Workers |
| 长时任务（>15min） | ECS / Cloud Run |

## ⚠️ 限制

- 冷启动可能引发第一次请求延迟
- 不适合长时间连接（WebSocket 推荐 Durable Objects 或专门方案）
- 受限 API（无 fs）
- 厂商锁定（不同平台 API 略有差异）

## 🔗 下一步

- [Fastify / Hono](/11-node/fastify)
- [Node 运行时](/11-node/runtime)
