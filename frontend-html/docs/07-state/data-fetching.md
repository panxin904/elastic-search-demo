---
title: React Query / SWR
date: 2026-08-15  # date-auto-injected
---

# React Query / SWR

## 🎯 为什么需要"服务端数据"库

服务端数据与"本地状态"不同：
- **远程**：需要 fetch + loading / error 状态
- **缓存**：避免重复请求
- **失效**：需要 invalidate / 重新拉取
- **乐观更新**：UI 先变，请求失败再回滚

自己写 hook 处理这堆很痛苦，**TanStack Query (React Query) / SWR** 帮你封装好。

## 🟦 TanStack Query

```bash
npm install @tanstack/react-query
```

```tsx
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <UserList />
    </QueryClientProvider>
  )
}

function UserList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json())
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  return <ul>{data.map(u => <li key={u.id}>{u.name}</li>)}</ul>
}
```

### 变更

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'

function CreateUser() {
  const qc = useQueryClient()
  const create = useMutation({
    mutationFn: (newUser) => fetch('/api/users', { method: 'POST', body: JSON.stringify(newUser) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['users'] })
  })

  return <button onClick={() => create.mutate({ name: 'bob' })}>Add</button>
}
```

### 高级特性

| 特性 | 描述 |
|------|------|
| 自动 refetch | 窗口聚焦 / 网络恢复时重新拉取 |
| 缓存时间 | `staleTime` / `gcTime` |
| 分页 | `useInfiniteQuery` |
| 预取 | `queryClient.prefetchQuery` |
| 并行查询 | `useQueries` |
| SSR | `dehydrate` / `hydrate` |

## 🟧 SWR（更轻）

```tsx
import useSWR from 'swr'

function UserList() {
  const { data, error, isLoading } = useSWR('/api/users', fetcher)
  // ...
}
```

- 用 **stale-while-revalidate** 策略：先返回缓存，再后台刷新
- 体积更小，DX 简单
- 同样支持 mutate / pagination / WebSocket

```tsx
const { data, mutate } = useSWR('/api/me')

mutate({ ...data, name: 'new' }, false)  // 乐观更新
```

## ⚖️ Query / SWR 对比

| | TanStack Query | SWR |
|--|----------------|-----|
| 体积 | ~12KB | ~5KB |
| 功能 | 全 | 简化 |
| Devtools | ✅ | 简易 |
| 突变 | ✅ 完整 | ✅ |
| 缓存策略 | 多种 | SWR-fixed |
| 中间件 | 社区丰富 | 较少 |
| SSR | ✅ 完善 | ✅ |

## 🛠️ 与 Zustand / Redux 协作

- **服务端数据**（列表、详情）→ Query / SWR
- **本地 UI 状态**（弹窗、主题）→ Zustand / useState
- **业务核心状态**（购物车、用户认证）→ Zustand + Query

避免把"服务端状态"放到 Redux / Zustand：你将需要重新发明 Query 的全部功能。

## 🔗 下一步

- [GraphQL / Apollo](/09-data/graphql)
- [tRPC](/09-data/trpc)
- [Zustand / Jotai](/07-state/zustand)
