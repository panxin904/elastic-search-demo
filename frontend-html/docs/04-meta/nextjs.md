---
title: Next.js (React 元框架)
date: 2026-08-15  # date-auto-injected
---

# Next.js (React 元框架)

## 🎯 Next.js 是什么

Vercel 维护的 React 元框架，开箱即用 SSR / SSG / ISR / RSC / Edge / Middleware。

```
Next.js 13+ App Router (推荐)  vs  Pages Router (旧)
```

## 📁 App Router 文件结构

```
app/
├── layout.tsx          ← 必须：根布局
├── page.tsx            ← 路由 / 对应 UI
├── loading.tsx         ← 加载 UI（Suspense 自动 fallback）
├── error.tsx           ← 错误边界
├── not-found.tsx       ← 404
├── blog/
│   ├── page.tsx
│   └── [slug]/page.tsx ← 动态路由
├── api/
│   └── hello/route.ts  ← 后端路由
```

## 🆚 Server vs Client Components

```tsx
// 默认是 Server Component（在服务端执行、不进 bundle）
export default async function Page() {
  const data = await fetch('https://api.example.com/data')
  return <div>{data.title}</div>
}

// 含交互 / 状态 必须 'use client'
'use client'
import { useState } from 'react'
export default function Counter() {
  const [n, setN] = useState(0)
  return <button onClick={() => setN(n + 1)}>{n}</button>
}
```

## 🧬 数据请求

```tsx
// Server Component 中直接 await fetch（自动 dedupe + 缓存）
export default async function Page({ params }) {
  const post = await fetch(`https://api/posts/${params.id}`, {
    next: { revalidate: 60 }  // ISR：60s 内缓存
  }).then(r => r.json())
  return <article>{post.body}</article>
}
```

## 📡 Server Actions

```tsx
'use server'

export async function createPost(formData: FormData) {
  const title = formData.get('title')
  await db.insert({ title })
  revalidatePath('/posts')  // 重新验证路由
}
```

```tsx
'use client'
import { createPost } from './actions'
export function Form() {
  return <form action={createPost}>
    <input name="title" />
    <button>Save</button>
  </form>
}
```

## 🎨 渲染策略

| 策略 | 用途 | 何时 |
|------|------|------|
| SSR | 每次请求渲染 | 内容实时、SEO |
| SSG | 构建时静态化 | 内容稳定（博客） |
| ISR | 增量静态化 | 大型站点、阶段性更新 |
| RSC | 服务端组件 | 默认 |
| CSR | 客户端渲染 | 内部应用 / 后台 |

## 🛡️ Middleware

```ts
// middleware.ts
export function middleware(request: NextRequest) {
  if (request.nextUrl.pathname.startsWith('/admin')) {
    const token = request.cookies.get('token')
    if (!token) return NextResponse.redirect('/login')
  }
  return NextResponse.next()
}
```

## 📦 路由

| 类型 | 语法 |
|------|------|
| 静态 | `app/about/page.tsx` |
| 动态 | `app/blog/[slug]/page.tsx` |
| Catch-all | `app/docs/[[...slug]]/page.tsx` |
| 路由组 | `app/(marketing)/page.tsx` (不参与路径) |
| 平行路由 | `app/@modal/page.tsx` |

## 🚀 部署

- **Vercel**：首选，0 配置
- **自托管**：Node.js / Docker / Edge runtime
- **静态导出**：`output: 'export'`（有限制）

## ⚠️ 常见坑

1. **Client Component 嵌套 Server Component**：Server 不能在 Client 中用 import，要靠 children 传
2. **Server Action 中不能直接读取 Cookies**：用 `cookies()` 函数
3. **Hydration mismatch**：服务端与客户端渲染结果不一致（检查时区 / `Date.now()`）

## 🔗 下一步

- [Remix / RR v7](/04-meta/remix)
- [React Router v6/v7](/08-routing/react-router)
- [Vercel / Serverless](/11-node/serverless)
