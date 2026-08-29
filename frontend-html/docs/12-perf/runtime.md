---
title: 运行时性能
date: 2026-08-15  # date-auto-injected
---

# 运行时性能

> 用户开始操作后，UI 是否快速响应。

## ⚡ React 性能模式

### 1. 不要做没必要的渲染

- 把"输入 → state"放到受控组件自身
- 用 stable key（避免 index 当 key）
- **派生状态用 useMemo**：处理昂贵计算

```ts
const visible = useMemo(() => items.filter(match), [items, query])
```

### 2. 拆分组件 / 降级 Context

Context 全部消费者都会重渲染。最佳实践：

- 拆小组件，**用 selector**
- 大数据放 `useRef` 或外部 store

```tsx
function ProfileHeader() {
  const name = useStore(s => s.user.name)   // 仅 name 变化触发
  return <h1>{name}</h1>
}
```

### 3. 虚拟化长列表

```tsx
import { useVirtualizer } from '@tanstack/react-virtual'

function List({ rows }) {
  const parent = useRef(null)
  const virtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => parent.current,
    estimateSize: () => 50
  })

  return (
    <div ref={parent} style={{ height: 400, overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map(v => (
          <div key={v.key} style={{ transform: `translateY(${v.start}px)` }}>
            {rows[v.index].name}
          </div>
        ))}
      </div>
    </div>
  )
}
```

1 万行列表也只渲染可见的几十条。

### 4. StartTransition / useDeferredValue

React 18+ 的并发特性：

```tsx
import { useTransition, useDeferredValue, useState } from 'react'

function Search() {
  const [text, setText] = useState('')
  const deferred = useDeferredValue(text)   // 延迟渲染昂贵列表
  const [isPending, startTransition] = useTransition()

  return (
    <>
      <input value={text} onChange={e => startTransition(() => setText(e.target.value))} />
      {isPending && <Spinner />}
      <List query={deferred} />
    </>
  )
}
```

### 5. 动画只用 transform / opacity

```
Layout < Paint < Composite
transform / opacity 只触发 composite，GPU 加速
```

```css
.card {
  transition: transform 200ms;
}
.card:hover { transform: translateY(-4px); }
```

## 🗃️ 数据请求

- **TanStack Query**：缓存 + 失效 + refetch
- **GraphQL**：合并请求，避免 N+1
- **预取**：`router.prefetchRoute()` / `queryClient.prefetchQuery()`

## 🎬 防抖 / 节流

```ts
function debounce<T extends (...args: any[]) => void>(fn: T, ms: number) {
  let timer: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), ms)
  }
}
```

- **debounce**：连续输入完才触发（搜索）
- **throttle**：固定间隔内最多 1 次（scroll）

## 🧵 Worker（重计算）

```ts
const worker = new Worker(new URL('./heavy.ts', import.meta.url))
worker.postMessage(data)
worker.onmessage = (e) => setResult(e.data)
```

复杂计算 / 大数据集解析放 Worker，主线程保持响应。

## 🧭 Profiling

- React DevTools Profiler
- Chrome Performance tab
- `why-did-you-render`：找出多余渲染
- Vue DevTools / Svelte DevTools

## 📊 检查清单

```
□ 长列表用虚拟化
□ 重复渲染用 memo + selector
□ 滑动 / 滚动用 passive listener
□ 动画只用 transform / opacity
□ 输入 / scroll 防抖 / 节流
□ 大请求用 Query 缓存
□ 重计算放 Worker
□ setState 不在循环内调
□ Profile 然后再优化（不要过早）
```

## 🔗 下一步

- [Core Web Vitals](/12-perf/cwv)
- [加载性能](/12-perf/loading)

<!-- svg-injected:do-not-edit -->

## 图示：浏览器渲染流水线

![浏览器渲染流水线](/browser-render.svg)
