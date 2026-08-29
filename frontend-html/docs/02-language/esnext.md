---
title: ESNext 新特性
date: 2026-08-15  # date-auto-injected
---

# ESNext 新特性

> 用到 ES2024 的关键语法、TC39 已进入 stage 4 的提案。

## 📅 时间线

- **ES2015 (ES6)** — class, arrow, Promise, let/const, 解构, 模板字符串…
- **ES2016** — `**` 幂、 `Array.includes`
- **ES2017** — async/await, Object.values/entries
- **ES2018** — 异步迭代、对象 spread、Promise.finally
- **ES2019** — `Array.flat / flatMap`, optional catch binding
- **ES2020** — `??`, `?.`, `Promise.allSettled`, BigInt, dynamic import
- **ES2021** — `||=`, `&&=`, `??=`, 数字分隔符, `String.replaceAll`
- **ES2022** — top-level await, `Array.at`, `Object.hasOwn`, class fields
- **ES2023** — `Array.findLast`, `Array.toSorted/Reversed/Spliced`, hashbang `#!`
- **ES2024** — `Array.group`, `Object.groupBy`, `Well-Formed Unicode`, `Atomics.waitAsync`

## 🌟 常用新语法

### 可选链 `?.`

```js
const name = user?.profile?.name ?? 'anonymous'
```

### 空值合并 `??`

仅在 `null` / `undefined` 时使用右侧值（区别于 `||`）。

### 逻辑赋值 `??=` / `||=` / `&&=`

```js
config.timeout ??= 3000     // 仅 null/undefined 时赋值
```

### 类字段 + 私有字段

```ts
class Counter {
  static #count = 0
  #value = 0

  static inc() { Counter.#count++ }
  get value() { return this.#value }
}
```

### Top-level await

```js
// ESM
const data = await fetch('/api/data')
export { data }
```

### Object.groupBy / Map.groupBy

```js
const fruits = [
  { name: 'apple', color: 'red' },
  { name: 'banana', color: 'yellow' }
]
const byColor = Object.groupBy(fruits, f => f.color)
// { red: [...], yellow: [...] }
```

### Array.findLast / findLastIndex

```js
arr.findLast(x => x % 2 === 0)
```

### Promise.withResolvers

```js
const { promise, resolve, reject } = Promise.withResolvers()
// 在事件回调中 resolve/reject
```

## 🧰 可迭代协议 + 迭代器

```js
const range = {
  [Symbol.iterator]() {
    let i = 0
    return {
      next: () => ({ value: i++, done: i > 5 })
    }
  }
}

for (const n of range) console.log(n)
```

## 📦 动态 import

```js
const { default: marked } = await import('marked')
```

## 🧪 实战偏好

- **`async/await`**：99% 的场景替代 Promise 链
- **`??`**：避免 `||` 把 `0` 当成空
- **`?.`**：替代 `&&` 链（更明确）
- **`Object.groupBy`**：替代第三方 groupBy 库（如果你的 target 支持）

## ⚠️ 注意版本

Vite / TypeScript 默认目标 ES2020 + ESNext 转换（视场景）。生产记得在构建时设置 `target` 与 `browserslist`。

## 🔗 下一步

- [JavaScript 核心](/02-language/javascript)
- [TypeScript 类型系统](/02-language/typescript)
- [WebAssembly](/02-language/wasm)


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
