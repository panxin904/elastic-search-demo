---
title: File-system Routing
---

# File-system Routing

## 🎯 概念

**用文件路径映射 URL 路由**，不用手写路由配置。

```
pages/users/[id].vue     →  /users/:id
app/blog/[slug]/page.tsx  →  /blog/:slug
```

## 🧰 主流元框架都支持

| 框架 | 风格 |
|------|------|
| Next.js (App Router) | `app/*/page.tsx` |
| Nuxt | `pages/*.vue` |
| SvelteKit | `src/routes/*/+page.svelte` |
| Remix | `app/routes/*.tsx`（约定） |
| Astro | `src/pages/*.astro` |
| TanStack Router | `src/routes/*`（通过 plugin） |

## 🧱 Next.js App Router 示例

```
app/
├── layout.tsx           ← 所有路由共用
├── page.tsx             ← /
├── about/page.tsx       ← /about
├── blog/
│   ├── page.tsx         ← /blog
│   └── [slug]/page.tsx  ← /blog/foo
└── api/hello/route.ts   ← /api/hello
```

## 🔄 动态参数

| 框架 | 语法 |
|------|------|
| Next.js | `[slug]/page.tsx` |
| Nuxt | `[slug].vue` |
| SvelteKit | `[slug]/+page.svelte` |
| Remix | `routes/blog.$slug.tsx` |

```tsx
// app/blog/[slug]/page.tsx
export default async function Post({ params }: { params: { slug: string } }) {
  const post = await fetchPost(params.slug)
  return <article>{post.body}</article>
}
```

## 🛣️ Catch-all & Optional

```
[...slug]/page.tsx          ←  /a/b/c → params.slug = 'a/b/c'
[[...slug]]/page.tsx        ←  /a/b/c OR /（slug 可选）
```

## 🧭 路由组 (Route Groups)

```
app/
├── (marketing)/
│   ├── page.tsx           ← /
│   └── about/page.tsx     ← /about
└── (app)/
    ├── layout.tsx         ← 仅 app 路由共用
    └── dashboard/page.tsx ← /dashboard
```

`(marketing)` 圆括号不参与 URL，但用于组织文件 / 共享布局。

## 🆚 手写路由 vs File-system

| | 手写（React Router） | 文件路由（Next/Nuxt） |
|--|--------------------|----------------------|
| 心智 | 显式 | 约定 |
| 重构 | 多文件改动 | 移动文件即可 |
| 嵌套布局 | 嵌套 `<Outlet>` | 嵌套 layout 组件 |
| 动态新增页面 | 需注册 | 新建文件即生效 |
| 缺点 | 入口集中 | 找不到文件在哪就懵 |

## 🛠️ 选型

| 场景 | 推荐 |
|------|------|
| 新项目 + SEO 重要 | Next.js / Nuxt |
| 已有应用 + 加些页面 | TanStack Router 文件式 |
| 团队习惯了 React Router | 保持手写也行 |

## 🔗 下一步

- [Next.js](/04-meta/nextjs)
- [Nuxt](/04-meta/nuxt)
- [SvelteKit](/04-meta/sveltekit)
