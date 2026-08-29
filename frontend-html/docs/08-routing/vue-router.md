---
title: Vue Router 4
date: 2026-08-15  # date-auto-injected
---

# Vue Router 4

## 🎯 Vue Router 4 vs 3

- 适配 Vue 3 Composition API
- `createRouter`、`createWebHistory` 替代类导出
- `<router-link>` / `<router-view>` 接口基本不变

```bash
npm install vue-router@4
```

## 🚀 基本配置

```ts
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('./Home.vue') },
    { path: '/about', component: () => import('./About.vue') },
    {
      path: '/users/:id',
      component: () => import('./User.vue'),
      props: true
    }
  ]
})
```

```ts
// main.ts
app.use(router)
```

## 🧩 `<router-link>`

```vue
<router-link to="/">Home</router-link>
<router-link :to="{ name: 'user', params: { id: 1 }}">User</router-link>
```

## 🛡️ 导航守卫

```ts
router.beforeEach((to, from) => {
  if (to.path.startsWith('/admin') && !isLogin()) {
    return { path: '/login', query: { redirect: to.fullPath }}
  }
})
```

也可以在路由表里：

```ts
{
  path: 'admin',
  component: AdminPage,
  beforeEnter: (to) => {
    if (!isLogin()) return '/login'
  }
}
```

## 🆕 组合式 API

```vue
<script setup>
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

watch(() => route.params.id, (id) => {
  // 路由变化时拉数据
})
</script>
```

## 🧠 数据加载

```ts
{
  path: 'user/:id',
  component: () => import('./User.vue'),
  // 路由进入前预取
  async beforeRouteEnter(to) {
    const user = await fetchUser(to.params.id)
    to.meta.user = user
  }
}
```

或用 **defineAsyncComponent + Suspense** 思路（Nuxt 更自动化）。

## 🏗 嵌套路由

```ts
{
  path: '/admin',
  component: AdminLayout,  // 含 <router-view>
  children: [
    { path: 'dashboard', component: Dashboard },
    { path: 'users', component: Users }
  ]
}
```

## 🆚 与 File-system Routing

实际项目通常用 **Nuxt** 自动生成路由，避免手写 `routes` 数组。

## 🔗 下一步

- [Vue 3 组合式 API](/03-framework/vue)
- [Nuxt](/04-meta/nuxt)
- [React Router v6/v7](/08-routing/react-router)
- [File-system Routing](/08-routing/file-routing)


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
