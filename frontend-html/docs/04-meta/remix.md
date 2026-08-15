---
title: Remix / RR v7
---

# Remix / React Router 7

## 🎯 Remix

Remix 已被合并回 **React Router v7**。两者现在共享代码库。

**Remix 的核心思想**：
- Load in loader, mutate in action（数据流跟 URL 绑死）
- 内置 form、`<Link>`、`<Meta>` 等组件
- 服务端渲染优先，无 RSC（v7 之前）

## 📦 React Router v7 三种模式

```ts
import { createBrowserRouter, RouterProvider } from 'react-router'
const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/blog/:id', element: <Post /> }
])
```

```ts
// 声明式（v6）
<BrowserRouter>
  <Routes>
    <Route path="/" element={<Home />} />
  </Routes>
</BrowserRouter>
```

```ts
// 文件路由（v6.4+，Remix 兼容）
app/routes/blog.$id.tsx
```

## 🔄 Loader / Action

```ts
// app/routes/blog.$id.tsx
import { json, useLoaderData, Form } from 'react-router'

export async function loader({ params }) {
  const post = await db.posts.find(params.id)
  return json(post)
}

export async function action({ request }) {
  const fd = await request.formData()
  await db.posts.update(fd)
  return redirect('/blog')
}

export default function Post() {
  const post = useLoaderData<typeof loader>()
  return <article>{post.title}</article>
}
```

## 📡 ErrorBoundary

```ts
export function ErrorBoundary({ error }: { error: Error }) {
  return <div>Error: {error.message}</div>
}
```

## 🆚 Remix v7 vs Next.js

| | Remix (v7) | Next.js |
|--|------------|---------|
| 数据加载 | loader 函数 | async page |
| 写入 | action 函数 | server action |
| RSC | v7 不再支持 RSC | ✅ 原生 |
| 部署 | 任意 Node / Edge | Vercel 最佳 |
| 心智 | 路由 = 数据 + UI | 路由 = URL |

## 🚀 React Router v7

```ts
// 通过 Remix 的 builder 也可以产出 vite + RR7 应用
npx create-react-router@latest
```

## 🔗 下一步

- [React Router v6/v7](/08-routing/react-router)
- [Next.js](/04-meta/nextjs)
