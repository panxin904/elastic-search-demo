---
title: Nuxt (Vue 元框架)
date: 2026-08-15  # date-auto-injected
---

# Nuxt (Vue 元框架)

## 🎯 Nuxt 是什么

Vue 生态最主流的元框架，类 Next.js 的能力 + Vue DX。

```
Nuxt 3+ 默认：Vite + TypeScript + ESM + SSR
Nuxt 2 默认：Webpack（已弃用）
```

## 📁 项目结构

```
nuxt-app/
├── app.vue                  ← 根组件
├── nuxt.config.ts           ← 配置
├── pages/                   ← 自动生成路由
├── components/              ← 自动导入
├── composables/             ← 自动导入
├── layouts/                 ← 多布局
├── server/                  ← 服务端 API（Nitro）
│   └── api/hello.ts
├── middleware/              ← 全局中间件
└── public/
```

## 🛣️ 路由

```vue
<!-- pages/index.vue -->
<template><div>Home</div></template>

<!-- pages/blog/[slug].vue -->
<template>
  <div>{{ slug }}</div>
</template>
<script setup>
const route = useRoute()
const { slug } = route.params
</script>
```

文件路由约定类似 Next.js + 自动按需加载。

## 📡 Server API（Nitro）

```ts
// server/api/hello.ts
export default defineEventHandler((event) => {
  return { hello: 'world' }
})
```

Nitro 让 Nuxt 可以脱离 Node 部署（Cloudflare Workers / Vercel Edge）。

## 🔄 数据获取

### `useFetch` (Setup)

```vue
<script setup>
const { data, pending, error, refresh } = await useFetch('/api/users')
</script>

<template>
  <div v-if="pending">Loading...</div>
  <div v-else-if="error">Error: {{ error.message }}</div>
  <ul v-else>
    <li v-for="u in data" :key="u.id">{{ u.name }}</li>
  </ul>
</template>
```

### `useAsyncData` + 自定义 fetcher

```ts
const { data } = await useAsyncData('cache-key', () => $fetch('/api/posts'))
```

## 🎨 自动导入

Nuxt 会自动导入 `components/`、`composables/`、`utils/` 下的导出：

```vue
<script setup>
// 无需 import
const { data } = await useFetch('/api/users')
const double = computed(() => count.value * 2)
</script>
```

## 🧩 Server Middleware

```ts
// server/middleware/log.ts
export default defineEventHandler((event) => {
  console.log('[req]', event.method, event.path)
})
```

## 🛡️ Route Middleware

```ts
// middleware/auth.global.ts
export default defineNuxtRouteMiddleware((to) => {
  if (to.path.startsWith('/admin') && !useAuth().isLogin) {
    return navigateTo('/login')
  }
})
```

## 🚀 渲染模式

```ts
// nuxt.config.ts
{
  ssr: true,        // 默认
  // ssr: false     // SPA 模式
  // nitro: { preset: 'static' }  // 全静态
}
```

## 📦 状态管理：useState

Nuxt 内置跨组件跨 SSR 的 `useState`：

```ts
const counter = useState('counter', () => 0)
counter.value++  // 全局共享
```

需要更复杂用 [Pinia](/07-state/pinia)（Nuxt 模块自动连接）。

## 🔗 下一步

- [Vue 3 组合式 API](/03-framework/vue)
- [Pinia](/07-state/pinia)
- [Vue Router](/08-routing/vue-router)


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
