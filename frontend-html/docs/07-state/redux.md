---
title: Redux Toolkit
date: 2026-08-15  # date-auto-injected
---

# Redux Toolkit

## 🎯 Redux 现状

Redux 是 React 全家桶里的"老资格"，但**过去**写法繁琐（action / reducer / connect）。Redux Toolkit (RTK) 是官方推荐的现代写法，2023+ 的事实标准。

## 📦 安装

```bash
npm install @reduxjs/toolkit react-redux
```

## 🧱 Store 切片

```ts
// store/counter.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    inc: (state) => { state.value++ },
    add: (state, action: PayloadAction<number>) => { state.value += action.payload }
  }
})

export const { inc, add } = counterSlice.actions
export default counterSlice.reducer
```

```ts
// store/index.ts
import { configureStore } from '@reduxjs/toolkit'
import { counterSlice } from './counter'

export const store = configureStore({
  reducer: {
    counter: counterSlice.reducer
  }
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

## ⚛️ React 中使用

```tsx
// App.tsx
import { Provider } from 'react-redux'
import { store } from './store'

<Provider store={store}>
  <App />
</Provider>
```

```tsx
// Counter.tsx
import { useSelector, useDispatch } from 'react-redux'
import { inc, add } from './store/counter'

function Counter() {
  const value = useSelector((s: RootState) => s.counter.value)
  const dispatch = useDispatch()
  return (
    <>
      <div>{value}</div>
      <button onClick={() => dispatch(inc())}>+1</button>
      <button onClick={() => dispatch(add(10))}>+10</button>
    </>
  )
}
```

## 🌐 RTK Query（远程数据）

```ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export const api = createApi({
  baseQuery: fetchBaseQuery({ baseUrl: '/api/' }),
  endpoints: (build) => ({
    getUsers: build.query<User[], void>({ query: () => 'users' }),
    addUser: build.mutation<User, NewUser>({ query: b => ({ url: 'users', method: 'POST', body: b }) })
  })
})

export const { useGetUsersQuery, useAddUserMutation } = api
```

## ⚖️ Pros / Cons

| ✅ | ❌ |
|----|---|
| 时间旅行调试友好 | 样板代码仍较多 |
| 生态强（中间件、devtools） | 相比 Zustand 更繁琐 |
| 大型项目结构清晰 | 小项目过度设计 |
| RTK Query 强大 | 学习曲线 |

## ⚖️ 该选 Redux 还是 Zustand？

| 场景 | 选 |
|------|----|
| 中大型 / 多人 / 严格结构 / 时间旅行 | Redux Toolkit |
| 中小型 / 想要最少样板 | Zustand |
| 服务端数据为主 | RTK Query / TanStack Query |

## 🔗 下一步

- [Zustand / Jotai](/07-state/zustand)
- [Pinia](/07-state/pinia)
- [React Query / SWR](/07-state/data-fetching)
