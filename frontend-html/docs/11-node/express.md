---
title: Express / Koa
date: 2026-08-15  # date-auto-injected
---

# Express / Koa

## 🚂 Express

**Node 生态的事实标准 web 框架**（2010 年发布）。极简、稳定、生态最大。

```bash
npm install express
```

```ts
import express from 'express'

const app = express()

app.use(express.json())      // 解析 JSON body

app.get('/api/users', (req, res) => {
  res.json([{ id: 1, name: 'alice' }])
})

app.post('/api/users', (req, res) => {
  const user = req.body
  res.status(201).json({ id: 2, ...user })
})

app.listen(3000, () => console.log('http://localhost:3000'))
```

### 中间件链

```ts
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`)
  next()
})

app.use(authMiddleware)   // 检查 token
app.use('/api', router)
```

### 路由

```ts
const router = express.Router()
router.get('/users', listUsers)
router.post('/users', createUser)
app.use('/api/v1', router)
```

### 错误处理

```ts
app.use((err, req, res, next) => {  // 4 个参数
  console.error(err)
  res.status(500).json({ error: 'Internal Server Error' })
})
```

## 🦊 Koa

**Express 同一团队打造**。更现代（基于 async/await + 更小内核）。

```ts
import Koa from 'koa'
import Router from '@koa/router'
import bodyParser from 'koa-bodyparser'

const app = new Koa()
const router = new Router()

router.get('/api/users', (ctx) => {
  ctx.body = [{ id: 1 }]
})

app.use(bodyParser())
app.use(router.routes())
app.listen(3000)
```

### Koa 洋葱模型

```
     ┌───────────────────
     │   middleware 1    │
     │   ┌─────────────  │
     │   │  middleware 2 │
     │   │  ┌──────────  │
     │   │  │  handler  │
     │   │  └──────────  │
     │   │  next 之后回 │
     │   └─────────────  │
     │   next 之后回     │
     └───────────────────
```

`await next()` 可以让中间件在内部"暂停"，等下游执行完再继续。

## 🆚 Express vs Koa

| | Express | Koa |
|--|---------|-----|
| 体积 | ~200KB | ~10KB（核心） |
| 中间件 | callback 或 async | async/await only |
| 错误处理 | 错误中间件 | `try / catch` / `ctx.throw` |
| 内置 | static / router | 几乎 0（需 koa-router 等） |
| 生态 | 极大 | 中 |
| 学习曲线 | 平 | 略陡（洋葱模型） |

## ⚠️ Express 的问题

1. **callback 兼容旧写法**：新的 async function 与 callback 容易出错
2. **错误流不直观**：没 `await next()` 这种洋葱
3. **生态**虽大但**普遍老旧**

**新项目建议**：
- 小服务 / 工具：**Express / Koa** 仍可
- 现代中型项目：**Fastify / Hono / NestJS**

## 🛠️ 实用中间件

```ts
// 日志
app.use(morgan('combined'))

// CORS
app.use(cors({ origin: 'https://app.example.com' }))

// 文件上传
app.use(multer({ storage }).single('avatar'))
```

## 🔗 下一步

- [Node 运行时](/11-node/runtime)
- [NestJS](/11-node/nestjs)
- [Fastify / Hono](/11-node/fastify)
- [REST 规范 / OpenAPI](/09-data/rest)
