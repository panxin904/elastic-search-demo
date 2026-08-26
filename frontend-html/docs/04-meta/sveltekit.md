---
title: SvelteKit
---

# SvelteKit

Svelte 团队出品的元框架。

## 🌟 特性

- 文件路由（pages 目录）
- 服务端钩子（hooks.server.ts）
- `+page.server.ts` / `+page.ts` / `+page.svelte`
- Forms 内置：`<form method="POST">`
- 适配器：`adapter-auto` / `adapter-vercel` / `adapter-node` / `adapter-cloudflare`

## 📁 项目结构

```
my-app/
├── src/
│   ├── routes/
│   │   ├── +page.svelte          ← /
│   │   ├── blog/
│   │   │   ├── +page.svelte      ← /blog
│   │   │   └── [slug]/+page.svelte ← /blog/:slug
│   │   └── api/foo/+server.ts    ← /api/foo
│   ├── lib/
│   └── hooks.server.ts
├── svelte.config.js
└── vite.config.ts
```

## 🔄 数据加载

```ts
// src/routes/blog/[slug]/+page.ts
export async function load({ params, fetch }) {
  const post = await fetch(`/api/posts/${params.slug}`).then(r => r.json())
  return { post }
}
```

```svelte
<script>
  export let data
  $: ({ post } = data)
</script>
<h1>{post.title}</h1>
```

## 📝 表单动作

```ts
// src/routes/blog/+page.server.ts
import { fail, redirect } from '@sveltejs/kit'

export const actions = {
  create: async ({ request }) => {
    const fd = await request.formData()
    const title = fd.get('title')
    if (!title) return fail(400, { error: 'title required' })
    await db.posts.insert({ title })
    return redirect('/blog')
  }
}
```

```svelte
<!-- src/routes/blog/+page.svelte -->
<form method="POST" action="?/create">
  <input name="title" />
  <button>Create</button>
</form>
```

## 🚀 部署适配器

```ts
// svelte.config.js
import adapter from '@sveltejs/adapter-vercel'
export default {
  kit: { adapter: adapter() }
}
```

无需配置：直接 `adapter-auto`，根据部署平台自动选择。

## 🧰 与 Svelte 5 runes

SvelteKit 已支持 Svelte 5 的 runes（响应式原语）：

```svelte
<script>
  let count = $state(0)
  let double = $derived(count * 2)
</script>
<button onclick={() => count++}>{count} × 2 = {double}</button>
```

## 🔗 下一步

- [Svelte / Solid](/03-framework/svelte)
- [Vite 原理](/05-build/vite)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
