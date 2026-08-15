---
title: Astro / Qwik
---

# Astro / Qwik

## 🌌 Astro

**MPA 优先 + 岛架构（Islands）** —— 默认零 JS，按需注入。

### 哲学

```astro
---
import Layout from '../layouts/Layout.astro'
const posts = await fetch('/api/posts').then(r => r.json())
---
<Layout title="Blog">
  <h1>Articles</h1>
  {posts.map(p => (
    <article>
      <h2>{p.title}</h2>
      <p>{p.excerpt}</p>
    </article>
  ))}

  <!-- Island: 唯一会被水合的交互组件 -->
  <LikeButton client:load postId="123" />
</Layout>
```

### 指令

| 指令 | 行为 |
|------|------|
| `client:load` | 立即水合 |
| `client:idle` | 浏览器空闲时水合 |
| `client:visible` | 进入视口水合 |
| `client:media="..."` | 媒体查询匹配时水合 |
| `client:only="react"` | 不在服务端渲染 |

### 适配

- **UI 框架**：React / Vue / Svelte / Solid 都可以用
- **`astro:assets`**：图片优化
- **`content collections`**：类型安全的 Markdown / MDX

### 适合

- 内容站（博客、文档、营销页）
- SEO 敏感
- 想要最少 JS

## ⚡ Qwik

**Resumability（可恢复）** —— 不水合，直接序列化为 HTML，恢复时按需 lazy 加载 JS。

```tsx
import { component$ } from '@builder.io/qwik'

export default component$(() => {
  const count = useSignal(0)
  return <button onClick$={() => count.value++}>{count.value}</button>
})
```

`$` 后缀表示"懒边界"。

### 优势

- **首屏几乎 0 JS**
- **TTI 极低**
- 适合电商、内容站、登录后 dashboard

### 缺点

- 心智不同（`$` 边界、Provider 用 `useContextProvider`，需要适应）
- 生态相比 React / Vue 小

### Qwik City

Qwik 的元框架，类 Next.js 的能力。

```tsx
// src/routes/product/[id]/index.tsx
import { routeLoader$ } from '@builder.io/qwik-city'

export const useProduct = routeLoader$(async ({ params }) => {
  return fetch(`/api/products/${params.id}`).then(r => r.json())
})
```

## 🎯 选型

| 场景 | Astro | Qwik | Next.js |
|------|-------|------|--------|
| 内容/营销 | ✅ | ✅ | OK |
| 大型 SPA / SaaS | ⚠ | ⚠ | ✅ |
| 首屏 + SEO | ✅ | ✅ | ✅ |
| React 生态 | 兼容 | 不直接（需 adapter） | ✅ 原生 |

## 🔗 下一步

- [Vite 原理](/05-build/vite)
- [加载性能](/12-perf/loading)
