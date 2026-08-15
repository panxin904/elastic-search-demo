---
title: Fastify / Hono
---

# Fastify / Hono

## ⚡ Fastify

**性能极强**的 Node web 框架（比 Express 快 2-3x）。插件生态类似 Express。

```bash
npm install fastify
```

```ts
import Fastify from 'fastify'

const app = Fastify({ logger: true })

app.get('/api/users', async () => {
  return [{ id: 1, name: 'alice' }]
})

app.post('/api/users', async (req, reply) => {
  const user = await db.users.create(req.body)
  reply.code(201).send(user)
})

app.listen({ port: 3000 })
```

### 插件

```ts
// fastify-cors
app.register(import('@fastify/cors'), {
  origin: 'https://app.example.com'
})

// fastify-jwt
app.register(import('@fastify/jwt'))
app.decorate('auth', async (req, reply) => {
  try { await req.jwtVerify() } catch { reply.code(401).send() }
})
```

### Schema + JSON Schema 校验

```ts
app.post('/api/users', {
  schema: {
    body: {
      type: 'object',
      required: ['name', 'email'],
      properties: {
        name: { type: 'string' },
        email: { type: 'string', format: 'email' }
      }
    }
  }
}, async (req) => {
  // req.body 已被校验
  return await createUser(req.body)
})
```

### 优势

- **快**：路由用 radix tree，序列化比 Express 快 ~2x
- **Schema 优先**：JSON Schema 自动校验 + 序列化
- **日志**集成 pino（最快 Node logger）
- **Type Provider**：配合 zod / TypeBox 自动推断类型

```ts
import { validatorCompiler, serializerCompiler, ZodTypeProvider } from 'fastify-type-provider-zod'
import { z } from 'zod'

app.setValidatorCompiler(validatorCompiler)
app.setSerializerCompiler(serializerCompiler)
app.withTypeProvider<ZodTypeProvider>().post('/users', {
  schema: { body: z.object({ name: z.string() }) }
}, async (req) => { req.body.name })  // 全类型推断
```

## ⚡ Hono

**Web Standards**（Fetch API）为基础、极快、跨运行时（Deno / Bun / Cloudflare）。

```bash
npm install hono
```

```ts
import { Hono } from 'hono'

const app = new Hono()

app.get('/api/users', (c) => c.json([{ id: 1, name: 'alice' }]))

app.post('/api/users', async (c) => {
  const body = await c.req.json()
  return c.json({ id: 2, ...body }, 201)
})

export default app
```

### 特色

| | Hono |
|--|------|
| 运行时 | Node / Deno / Bun / Workers / Lagon |
| 心智 | 类 hono-router / Express，但用 Web 标准 |
| 性能 | 比 Express / Fastify 都快 |
| Validator | zod / valibot 内置支持 |

```ts
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'

app.post('/users',
  zValidator('json', z.object({ name: z.string() })),
  (c) => c.json({ ok: true })
)
```

### 路由分组 / RPC

```ts
// 客户端直接调用类型安全的 RPC
import { hc } from 'hono/client'
const client = hc<typeof app>('http://localhost')
const res = await client.api.users.$get()
```

## 🆚 Hono vs Fastify

| | Fastify | Hono |
|--|---------|------|
| 目标平台 | Node 优先 | 多运行时 |
| 生态 | Express-like 庞大 | 较新但增长 |
| 验证 | 多种 type provider | zod / valibot 一等 |
| 部署 | Node / Docker | 边缘 / Workers / Bun |

## 🎯 选型

| 场景 | 选择 |
|------|------|
| 极致 Node 性能 + JSON Schema | Fastify |
| 跨运行时 / Edge / Cloudflare | Hono |
| 老项目维护 | Fastify 兼容 Express |
| 想要类型 RPC | Hono |

## 🔗 下一步

- [Express / Koa](/11-node/express)
- [NestJS](/11-node/nestjs)
- [Serverless](/11-node/serverless)
