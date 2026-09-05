---
title: React 核心与 Hooks
date: 2026-08-15  # date-auto-injected
---

# React 核心与 Hooks

![React Fiber Tree](/react-fiber-tree.svg)

## 🧬 心智模型

React = **声明式 UI + 单向数据流 + 不可变状态**

```jsx
function App() {
  const [count, setCount] = useState(0)
  return (
    <button onClick={() => setCount(c => c + 1)}>
      Clicked {count} times
    </button>
  )
}
```

## ⚙️ Hooks 列表

| Hook | 作用 |
|------|------|
| `useState` | 本地状态 |
| `useReducer` | 复杂状态 / reducer 模式 |
| `useEffect` | 副作用（数据请求、订阅） |
| `useLayoutEffect` | 同步执行，在 DOM 变更后绘制前 |
| `useMemo` | 缓存计算值 |
| `useCallback` | 缓存函数引用 |
| `useRef` | 跨渲染持久引用 |
| `useContext` | 跨组件共享 |
| `useId` | 稳定的 SSR 唯一 id |
| `useTransition` | 把更新标记为低优先级 |
| `useDeferredValue` | 延迟值，常用于搜索框 |
| `useSyncExternalStore` | 订阅外部 store |

## 🔄 useState 闭环

```jsx
const [count, setCount] = useState(0)

// 替换 vs 函数式更新
setCount(1)            // 直接赋值
setCount(c => c + 1)   // 函数式（拿到最新值）

// 对象 / 数组更新（不可变）
setUser({ ...user, name: 'bob' })
setList([...list, item])
```

## ⚡ useEffect 三件事

```jsx
useEffect(() => {
  // 1. 设置（每次依赖变更后）
  const sub = api.subscribe(id, handler)

  // 2. 副作用（数据请求、订阅）
  fetchData()

  // 3. 清理（卸载或下次 effect 前）
  return () => sub.unsubscribe()
}, [id])   // 依赖数组
```

**常见陷阱**：
- 忘加依赖 → lint 警告
- 在 effect 里直接调 setState 触发循环 → 改用回调或 reducer
- 异步 fetch 没清理 → 在 unmount 后 setState 会警告（用 AbortController 或 ignore flag）

## 🎯 useRef 妙用

```jsx
const ref = useRef<HTMLDivElement>(null)
useEffect(() => ref.current?.focus(), [])

const prev = useRef(count)  // 跨渲染读取上一次的值
useEffect(() => { prev.current = count }, [count])

const idRef = useRef<NodeJS.Timeout>()  // 可变容器，不参与渲染
```

## 🎬 性能优化三件套

```jsx
const memoComp = React.memo(Comp)            // 浅比较 props
const stableFn = useCallback(fn, deps)      // 稳定函数引用
const cachedVal = useMemo(() => compute(), deps) // 缓存计算
```

**什么时候用**：经过 profiling（React DevTools Profiler）确认是性能瓶颈再用。

## 🎭 React Server Components（RSC）

Next.js App Router 引入：

- **Server Component**：在服务端渲染，不进 bundle
- **Client Component**（`'use client'`）：含交互、进 bundle

```jsx
// 纯展示，作为 Server Component（默认）
function ProductList({ products }) {
  return <ul>{products.map(p => <li>{p.name}</li>)}</ul>
}

// 含交互，必须作为 Client Component
'use client'
function AddToCart({ id }) {
  const [loading, setLoading] = useState(false)
  // ...
}
```

## 🧰 Context

```jsx
const ThemeCtx = createContext('light')

function App() {
  return (
    <ThemeCtx.Provider value="dark">
      <Page />
    </ThemeCtx.Provider>
  )
}

const theme = useContext(ThemeCtx)
```

Context 适合"低频更新 + 跨组件共享"，高频更新用 Redux / Zustand。

## 🧪 常用社区库

- **React Hook Form**：表单
- **TanStack Query**：数据请求缓存
- **Framer Motion**：动画
- **Radix UI / Headless UI**：无样式可访问性组件
- **react-i18next**：国际化

## ⚠️ 常见反模式

1. **不要在 render 里发请求** → 用 effect 或事件回调
2. **避免 prop drilling** → context 或 Zustand
3. **index 作为 key** 影响列表性能
4. **直接修改 state** → 永远创建新引用
5. **大对象放进 Context** → 会让所有消费者重渲染

## 🔗 下一步

- [Next.js](/04-meta/nextjs)
- [Redux Toolkit](/07-state/redux)
- [Zustand / Jotai](/07-state/zustand)
- [React Query](/07-state/data-fetching)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 后端 API
- [android](https://java-px.bot.cd/android/):Android 移动
- [java-language](https://java-px.bot.cd/java-language/):Java 基础
