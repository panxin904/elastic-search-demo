---
title: Zustand / Jotai
date: 2026-08-15  # date-auto-injected
---

# Zustand / Jotai

## 🌿 Zustand

**极简的全局状态库**，样板代码极少。

```bash
npm install zustand
```

### 单文件 store

```ts
import { create } from 'zustand'

type Counter = {
  value: number
  inc: () => void
  reset: () => void
}

export const useCounter = create<Counter>((set) => ({
  value: 0,
  inc: () => set((s) => ({ value: s.value + 1 })),
  reset: () => set({ value: 0 })
}))
```

```tsx
import { useCounter } from './store'

function Counter() {
  const value = useCounter((s) => s.value)
  const inc = useCounter((s) => s.inc)
  return <button onClick={inc}>{value}</button>
}
```

**selector 的好处**：只订阅 `value`，避免整个 store 重渲染。

### 多 store

```ts
export const useCartStore = create(...)
export const useAuthStore = create(...)
```

按业务领域拆，每个组件树按需 import。

### 中间件

```ts
import { persist, devtools } from 'zustand/middleware'

export const useAuth = create(persist(
  (set) => ({
    user: null,
    login: (u) => set({ user: u }),
    logout: () => set({ user: null })
  }),
  { name: 'auth-storage' }
))
```

`persist` 自动同步到 localStorage。

## ⚛️ Jotai

**原子化**状态管理（类 Recoil）。适合细粒度订阅。

```bash
npm install jotai
```

```ts
import { atom, useAtom } from 'jotai'

const countAtom = atom(0)
const doubleAtom = atom(get => get(countAtom) * 2)

function Counter() {
  const [count, setCount] = useAtom(countAtom)
  const double = useAtom(doubleAtom)
  return <button onClick={() => setCount(c => c + 1)}>
    {count} (×2 = {double})
  </button>
}
```

- **细粒度订阅**：仅更新用到该原子的组件
- **派生原子**：`atom(get => ...)` 类似 computed
- 异步原子：`atom(async get => await fetch(...))`

## 🆚 Zustand vs Jotai vs Context

| | Zustand | Jotai | Context |
|--|---------|-------|--------|
| 体积 | ~1KB | ~3KB | 0 |
| 心智 | 标准 store | 原子 + 派生 | Provider/Consumer |
| 选择性订阅 | 自动 | 自动 | ❌ 全量更新 |
| 派生 | selector | derived atom | 自实现 useMemo |
| 持久化 | 内置 | 第三方 | 自实现 |
| SSR | ✅ | ✅ | ✅ |

## ⚠️ 常见陷阱

1. **大对象当 selector**：默认浅比较，导致多余重渲染
2. **派生计算应该用 selector / derived atom**，而非在渲染时算
3. **Zustand 不要在 store 内调用 React Hooks**

## 🛠️ 选型

| 场景 | 推荐 |
|------|------|
| 5-15 个 store，标准结构 | Zustand |
| 派生 / 局部原子 / 异步流 | Jotai |
| 服务端数据为主 | TanStack Query（不是状态库） |
| Vue 项目 | Pinia（不是 Zustand）|

## 🔗 下一步

- [Pinia](/07-state/pinia)
- [Redux Toolkit](/07-state/redux)
- [React Query](/07-state/data-fetching)
