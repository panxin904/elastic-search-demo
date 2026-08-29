---
title: Svelte / Solid
date: 2026-08-15  # date-auto-injected
---

# Svelte / Solid

> 两个"非主流但很香"的现代前端方案。

## 🦋 Svelte

**Slogan**: *"Write less code"* — 编译时框架，无运行时虚拟 DOM。

### 心智模型

```svelte
<script>
  let count = 0
  $: doubled = count * 2
  function inc() { count++ }
</script>

<button on:click={inc}>
  Clicked {count} (×2 = {doubled})
</button>
```

### 特点

- **真小**：运行时 0（编译为原生 DOM 操作 + 响应式指令）
- **`$:` 响应式声明块** 类似 Svelte 的杀手锏
- **CSS 作用域默认隔离**：不需要 CSS Modules
- **SvelteKit**：类 Next.js 的元框架，支持 SSR/SSG/Edge

```svelte
<style>
  /* 默认 scoped，无需 .module / BEM */
  button { background: tomato; }
</style>
```

### 适用

- 关注性能（移动端、低功耗）
- 想要最少样板代码
- 单页 / 独立产品（个人博客、落地页）

## ⚡ Solid

**类 React 心智 + 类 SolidJS 细粒度响应式**。

### 心智模型

```jsx
import { createSignal, createMemo, For } from 'solid-js'

const [count, setCount] = createSignal(0)
const double = createMemo(() => count() * 2)

function App() {
  return (
    <button onClick={() => setCount(c => c + 1)}>
      {count()} × 2 = {double()}
    </button>
  )
}

function List(props) {
  return (
    <For each={props.items}>
      {item => <li>{item}</li>}
    </For>
  )
}
```

### 特点

- **无虚拟 DOM**：直接订阅 + 精准更新
- **JSX 语法**但底层完全不同（不像 React）
- **SolidStart**：类 Next.js 的元框架
- **Bundle 极小**：~7KB

### 为什么不用 hooks

```jsx
// ❌ Solid 没有 hooks（不需要）
// ✅ 相反：createSignal + 自动订阅
```

## 🆚 三者对比

| | Svelte | Solid | React |
|--|-------|-------|-------|
| 体积 | ~0 (compiled) | ~7KB | ~45KB |
| 虚拟 DOM | ❌ | ❌ | ✅ |
| JSX | 自有模板 | ✅ JSX | ✅ JSX |
| 状态语法 | `$:` 声明 | `createSignal()` | `useState()` |
| 学习曲线 | 平缓 | 中（要懂响应式） | 中 |
| 生态 | 中 | 小 | 巨大 |

## 🎯 我的建议

| 场景 | 选择 |
|------|------|
| 性能至上（移动 H5 / Web 应用） | Svelte / Solid |
| 团队最大池子（招聘容易） | React |
| 中文社区 / 中台 | Vue |
| 企业大型 / 严谨 | Angular |

## 🔗 下一步

- [框架总览](/03-framework/overview)
- [Vite 原理](/05-build/vite)
