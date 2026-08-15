---
title: TanStack Router
---

# TanStack Router

## 🌟 卖点

TanStack Router = **类型安全的 React 路由器**。

- **路由即类型**：`Link to=...` 推导参数
- **Search Params 类型化**：`?` 后参数自动推断
- **内置缓存** + loader

## 📦 安装

```bash
npm install @tanstack/react-router
```

## 🧱 路由定义

```ts
import { createRootRoute, createRoute, createRouter } from '@tanstack/react-router'

const rootRoute = createRootRoute()

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: () => <div>Home</div>
})

const userRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/users/$userId',
  component: UserPage,
  loader: ({ params }) => fetchUser(params.userId)
})

const routeTree = rootRoute.addChildren([indexRoute, userRoute])

export const router = createRouter({ routeTree })
```

## 🔗 类型安全链接

```tsx
import { Link } from '@tanstack/react-router'

<Link to="/users/$userId" params={{ userId: 123 }}>
  Go
</Link>
```

⚡ 编译期校验：写错路径或漏参数会报错。

## 🔍 Search Params 类型化

```ts
const searchRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/search',
  validateSearch: (search) => ({
    q: (search.q as string) ?? '',
    page: Number(search.page) || 1
  }),
  component: SearchPage
})
```

```tsx
import { useNavigate } from '@tanstack/react-router'

function Page() {
  const navigate = useNavigate({ from: '/search' })
  return (
    <input
      onChange={e => navigate({ search: { q: e.target.value } })}
    />
  )
}
```

## ⚡ 内置数据缓存

```ts
const userRoute = createRoute({
  path: '/users/$id',
  // 同 TanStack Query 的 staleTime / cacheTime
  staleTime: 10_000,
  loader: ({ params }) => fetch(`/api/users/${params.id}`)
})

const data = useLoaderData({ from: userRoute })
```

## 🧩 文件路由约定

```
src/routes/
  __root.tsx
  index.tsx
  users.$userId.tsx
  posts.route.tsx
  posts.index.tsx
```

类似 Next.js 的约定，可以用 `@tanstack/router-cli` / `@tanstack/router-plugin/vite` 自动生成路由树。

## ⚖️ TanStack Router vs React Router v7

| | TanStack | RR v7 |
|--|----------|-------|
| 类型安全 | ✅ 极致 | ⚠ 半自动 |
| 内置缓存 | ✅ | ❌ |
| 体积 | ~12KB | ~8KB |
| 学习曲线 | 中 | 平缓 |
| 生态 | 增长中 | 主流 |

## 🎯 我的建议

| 场景 | 选择 |
|------|------|
| 新项目重视类型 | TanStack Router |
| 大型项目、SEO、SSR | Next.js（无需选 RR） |
| 维护快速迭代 / 中小项目 | React Router |

## 🔗 下一步

- [React Router v6/v7](/08-routing/react-router)
- [File-system Routing](/08-routing/file-routing)
- [Next.js](/04-meta/nextjs)
