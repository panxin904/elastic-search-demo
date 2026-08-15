---
title: Event Loop
---

# JavaScript Event Loop

## 🎯 为什么需要 Event Loop

JS 是单线程语言，但有大量异步操作（I/O、setTimeout、Promise）。Event Loop 用任务调度让单线程也能并发。

## 📚 相关术语

| 术语 | 含义 |
|------|------|
| Call Stack | 函数调用栈（LIFO） |
| Microtask Queue | 微任务队列（Promise、queueMicrotask） |
| Macrotask Queue | 宏任务队列（setTimeout / setInterval / I/O / UI 事件） |
| Render | 浏览器渲染步骤（requestAnimationFrame 所在） |

## 🔁 循环顺序

```
1. 执行同步代码（压栈 / 出栈）
2. Call Stack 为空 → 优先清空 Microtask Queue（微任务）
3. 必要时 UI render（task 结束时浏览器判断）
4. 从 Macrotask Queue 取一个任务执行
5. 回到第 2 步
```

注意：**Microtask 在每个宏任务之后都会清空**，渲染可能在两次任务之间发生。

## 🧪 经典例子

```js
console.log('1')                          // 同步

setTimeout(() => console.log('2'), 0)    // 宏任务

Promise.resolve().then(() => console.log('3')) // 微任务

queueMicrotask(() => console.log('4'))   // 微任务

console.log('5')                          // 同步

// 输出：1 5 3 4 2
```

## 🎬 Node 中的 Event Loop

Node 12+ 同样使用微任务优先，且有多个阶段：

```
┌─ Timers (setTimeout / setInterval)
├─ Pending Callbacks (I/O)
├─ Idle / Prepare
├─ Poll (新 I/O)
├─ Check (setImmediate)
├─ Close Callbacks (close)
```

`process.nextTick` 的回调比 Promise 微任务更优先（在每个阶段切分时执行）。

## 🧰 API 的任务类型

| API | 类型 |
|-----|------|
| `setTimeout / setInterval` | 宏任务 |
| `Promise.then / catch / finally` | 微任务 |
| `queueMicrotask` | 微任务 |
| `MutationObserver` | 微任务 |
| `requestAnimationFrame` | 渲染前回调 |
| `requestIdleCallback` | 浏览器空闲时 |
| `MessageChannel / postMessage` | 宏任务 |
| `fetch` 回调 | 微任务（在 fetch 后） |

## ⚠️ 实战陷阱

1. **大量微任务会阻塞渲染**：浏览器在所有微任务清空前不会渲染页面。
2. **`setTimeout(fn, 0)` 不是 0ms**：最小延迟 4ms（嵌套会拉到 16ms+）。
3. **回调地狱**用 `async/await` 或 Promise 链。
4. **长任务 > 50ms** 会触发 TBT / INP 警告，拆成 `setTimeout(fn, 0)` 或 `scheduler.yield()`。

## 🔗 下一步

- [JavaScript 核心](/02-language/javascript)
- [Node 运行时](/11-node/runtime)
