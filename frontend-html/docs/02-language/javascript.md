---
title: JavaScript 核心
---

# JavaScript 核心

> 把 JS 基础打扎实 — ES2024 已经进化很多，但核心机制没变。

## 🧩 类型系统

```
7 种原始类型（Primitive）：
  string, number, bigint, boolean, undefined, symbol, null
引用类型：Object (含 Array, Function, Date, Map, Set 等)

typeof null === 'object'      // 语言历史遗留 bug
typeof [] === 'object'        // 数组也是对象
Array.isArray([]) === true    // 区分数组
```

## 🌀 类型转换

```js
// 转 Boolean：falsy 值只有 6 个
Boolean('')         // false
Boolean(0)          // false
Boolean(NaN)        // false
Boolean(null)       // false
Boolean(undefined)  // false
Boolean(false)      // false

// 转 Number
Number('')          // 0
Number('  10  ')    // 10
Number('abc')       // NaN
parseInt('10abc')   // 10（读到非数字停止）
parseInt('abc10')   // NaN
+'10'               // 10
+true               // 1
```

## 🔒 闭包（Closure）

```js
function makeCounter() {
  let n = 0
  return {
    inc: () => ++n,
    get: () => n
  }
}

const c = makeCounter()
c.inc()
c.inc()
c.get() // 2
```

每个函数被创建时都会绑定自己的"作用域对象"，即使外层函数已经返回。

## 🎯 this

| 调用方式 | this 指向 |
|----------|----------|
| `obj.fn()` | obj |
| `fn()` | undefined（严格模式）/ window（sloppy） |
| `new Fn()` | 新对象 |
| `fn.call(ctx)` | ctx |
| `arrow` | 外层作用域（无 this） |

```js
const obj = {
  name: 'alice',
  greet() { return this.name },
  // 箭头函数：在创建时就锁定了 this
  delayed: () => setTimeout(() => console.log(this.name), 100)
}
```

## 🧬 原型链

```js
function Person(name) { this.name = name }
Person.prototype.say = function () { return `I'm ${this.name}` }

const p = new Person('alice')
p.__proto__ === Person.prototype
Person.prototype.__proto__ === Object.prototype
Object.prototype.__proto__ === null   // 链的终点
```

## 🌀 Promise

```js
const p = new Promise((resolve, reject) => {
  setTimeout(() => resolve('done'), 1000)
})

await p  // 'done'

Promise.all([p1, p2]).then(([r1, r2]) => {})  // 全部成功
Promise.allSettled([p1, p2])                  // 全部完成（不论成功失败）
Promise.race([p1, p2])                         // 最快的
Promise.any([p1, p2])                         // 第一个成功的
```

## ⛓️ async/await

```js
async function loadUser(id) {
  try {
    const user = await fetchUser(id)
    const orders = await fetchOrders(user.id)
    return { user, orders }
  } catch (e) {
    console.error(e)
    throw e  // 重新抛出
  }
}
```

## 🗃️ Map / Set / WeakMap / WeakSet

| 结构 | 特点 |
|------|------|
| `Map` | 任意类型键、有序、可迭代 |
| `Set` | 去重、有序 |
| `WeakMap` | 键必须对象、不阻止 GC |
| `WeakSet` | 同上 |

## 🔢 数组常用方法

```js
arr.map(fn)              // 转换
arr.filter(fn)           // 过滤
arr.reduce((acc, x) => acc + x, 0)  // 累加
arr.find(fn)             // 找到第一个匹配
arr.some(fn) / every(fn) // 至少 / 全部
arr.includes(value)      // 包含
arr.flat(2)              // 展平
arr.flatMap(fn)          // map + flat
arr.from(set)            // Set → Array
arr.at(-1)               // 最后一项
```

## 📦 解构 + 剩余/展开

```js
const { a, b, ...rest } = obj
const [first, , third] = arr
const merged = { ...defaults, ...options }
const all = [...setA, ...setB]
```

## 🔍 严格相等 vs 宽松

`===` 不做类型转换；`==` 会。**永远用 `===`**。

例外：`x == null` 同时排除 `null` 和 `undefined` 是常见技巧。

## 🛡️ 常用工具

- `Object.freeze` 深度冻结（深度需手写）
- `??` 空值合并（`null` / `undefined` 才走右侧）
- `?.` 可选链
- `[...'abc']` 字符串转字符数组

## 🔗 下一步

- [TypeScript 类型系统](/02-language/typescript)
- [React 核心与 Hooks](/03-framework/react)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 后端 API
- [android](https://java-px.bot.cd/android/):Android 移动
- [java-language](https://java-px.bot.cd/java-language/):Java 基础
