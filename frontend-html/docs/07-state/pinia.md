---
title: Pinia (Vue)
---

# Pinia

## 🌟 Pinia 是什么

Vue 官方推荐的**现代状态库**（替代 Vuex）。Composition API 风格，类型友好。

```bash
npm install pinia
```

```ts
// main.ts
import { createPinia } from 'pinia'
app.use(createPinia())
```

## 🧱 定义 store

```ts
// stores/counter.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useCounter = defineStore('counter', () => {
  const value = ref(0)
  const double = computed(() => value.value * 2)
  function inc() { value.value++ }
  function reset() { value.value = 0 }
  return { value, double, inc, reset }
})
```

**Setup 风格**：直接用 Vue 的 `ref`/`computed`，更易测试。

## ⚙️ Options 风格（更结构化）

```ts
export const useUser = defineStore('user', {
  state: () => ({ profile: null as User | null }),
  getters: {
    isLogin: (s) => !!s.profile
  },
  actions: {
    async fetchProfile() {
      this.profile = await api.getProfile()
    }
  }
})
```

## 🧩 在组件中使用

```vue
<script setup>
import { useCounter } from '@/stores/counter'

const counter = useCounter()

counter.inc()           // 直接调 action

// 解构保持响应性（用 storeToRefs）
import { storeToRefs } from 'pinia'
const { value, double } = storeToRefs(counter)

// 或全部订阅
const state = counter.$state
</script>

<template>
  <div>{{ counter.value }}</div>
  <button @click="counter.inc()">+1</button>
</template>
```

## 🔁 跨 store 通讯

```ts
export const useCart = defineStore('cart', () => {
  const user = useUserStore()
  const items = ref<Item[]>([])

  function checkout() {
    if (!user.isLogin) throw new Error('请先登录')
    return api.checkout(items.value)
  }

  return { items, checkout }
})
```

## 💾 持久化

```ts
import { defineStore } from 'pinia'
import { piniaPersist } from 'pinia-plugin-persistedstate'

export const useAuth = defineStore('auth', () => {
  const token = ref<string | null>(null)
  return { token }
}, {
  persist: {
    key: 'auth',
    storage: localStorage,
    paths: ['token']
  }
})

app.use(piniaPersist)
```

## 🆚 Pinia vs Vuex

| | Pinia | Vuex 4 |
|--|-------|--------|
| 体积 | ~1KB | ~10KB |
| 类型 | ✅ TS 优先 | 一般 |
| Composition API | ✅ | 不原生 |
| 模块化 | 自动分割 | 显式 modules |
| DevTools | ✅ | ✅ |

Vue 团队推荐 **Pinia 替代 Vuex**。

## 🔗 下一步

- [Vue 3 组合式 API](/03-framework/vue)
- [Zustand / Jotai](/07-state/zustand)
- [Vue Router](/08-routing/vue-router)
