---
title: tRPC
date: 2026-08-15  # date-auto-injected
---

# tRPC

## 🎯 tRPC 是什么

**TypeScript 优先**的 RPC 方案：服务端定义函数，**前端直接调用，类型自动同步**——零 schema、零 codegen。

```bash
# Monorepo 或单仓
npm install @trpc/server @trpc/client
```

## 🧱 服务端定义 router

```ts
// server/trpc.ts
import { initTRPC } from '@trpc/server'
const t = initTRPC.create()
export const router = t.router
export const publicProcedure = t.procedure
```

```ts
// server/index.ts
import { z } from 'zod'
import { router, publicProcedure } from './trpc'

const appRouter = router({
  getUser: publicProcedure
    .input(z.object({ id: z.string() }))
    .query(({ input }) => db.users.find(input.id)),

  createUser: publicProcedure
    .input(z.object({ name: z.string() }))
    .mutation(({ input }) => db.users.create(input))
})

export type AppRouter = typeof appRouter
```

## 🌐 客户端使用

```ts
// client/index.ts
import { createTRPCProxyClient } from '@trpc/client'
import type { AppRouter } from '../server'

const client = createTRPCProxyClient<AppRouter>({
  url: 'http://localhost:3000/trpc'
})

const user = await client.getUser.query({ id: '1' })  // 类型安全！
```

## ⚛️ React Hooks（推荐）

```tsx
import { createTRPCReact } from '@trpc/react-query'

const trpc = createTRPCReact<AppRouter>()

function UserCard({ id }: { id: string }) {
  const { data, isLoading } = trpc.getUser.useQuery({ id })
  if (isLoading) return 'Loading'
  return <div>{data.name}</div>
}
```

底层基于 **TanStack Query**，自动拿到缓存 / refetch / invalidate。

## ✅ 优势

| | tRPC | REST | GraphQL |
|--|------|------|---------|
| 类型安全 | ✅ 编译期 | ❌ | ⚠ codegen |
| 学习成本 | 平 | 平 | 中 |
| Schema 维护 | 0 | 0 | 1 |
| 缓存集成 | TanStack Query | 自实现 | Apollo 内置 |
| 多端（移动） | ✅ | ✅ | ✅ |
| 跨语言 | ❌ 仅 TS | ✅ | ✅ |

## ⚠️ 局限

- **服务端 / 客户端必须共享类型**：必须是 TS 项目
- **跨语言不能直接用**：需要额外适配
- **不适合公共 API**（给外部团队调用）

## 🛠️ 适合场景

- 全栈 TS 项目（Next.js + tRPC）
- 中小团队内部 BFF
- 一人多角色（无需分工）

## 🚫 不适合场景

- 服务端是 Java / Go（其他团队）
- 需要公共 OpenAPI 文档
- 大量公共消费方

## 🔗 下一步

- [GraphQL](/09-data/graphql)
- [REST 规范 / OpenAPI](/09-data/rest)
- [React Query](/07-state/data-fetching)
