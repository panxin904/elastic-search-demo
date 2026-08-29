---
title: 手写代码题
date: 2026-08-15  # date-auto-injected
---

# 手写代码题

> 30 个手写代码题，按主题分类。

## 🔧 JS 基础

### 1. 防抖 (debounce)

```ts
function debounce<T extends (...args: any[]) => void>(fn: T, ms: number) {
  let timer: ReturnType<typeof setTimeout>
  return (...args: Parameters<T>) => {
    clearTimeout(timer)
    timer = setTimeout(() => fn(...args), ms)
  }
}
```

### 2. 节流 (throttle)

```ts
function throttle<T extends (...args: any[]) => void>(fn: T, ms: number) {
  let last = 0
  return (...args: Parameters<T>) => {
    const now = Date.now()
    if (now - last >= ms) {
      last = now
      fn(...args)
    }
  }
}
```

### 3. 深拷贝

```ts
function deepClone<T>(obj: T, map = new WeakMap()): T {
  if (obj === null || typeof obj !== 'object') return obj
  if (map.has(obj as object)) return map.get(obj as object)
  if (obj instanceof Date) return new Date(obj.getTime()) as any
  if (obj instanceof RegExp) return new RegExp(obj) as any

  const out: any = Array.isArray(obj) ? [] : {}
  map.set(obj as object, out)
  for (const key in obj) {
    out[key] = deepClone((obj as any)[key], map)
  }
  return out
}
```

### 4. Promise.all / Promise.allSettled

```ts
Promise.myAll = (promises: Promise<any>[]) =>
  new Promise((resolve, reject) => {
    const out: any[] = []
    let done = 0
    promises.forEach((p, i) =>
      Promise.resolve(p).then(v => {
        out[i] = v
        if (++done === promises.length) resolve(out)
      }, reject)
    )
  })

Promise.myAllSettled = (promises: Promise<any>[]) =>
  Promise.all(promises.map(p => Promise.resolve(p).then(
    v => ({ status: 'fulfilled', value: v }),
    e => ({ status: 'rejected', reason: e })
  )))
```

### 5. 手写 call / apply / bind

```ts
Function.prototype.myCall = function (ctx: any, ...args: any[]) {
  const fn = Symbol('fn')
  ctx[fn] = this
  const result = ctx[fn](...args)
  delete ctx[fn]
  return result
}

Function.prototype.myBind = function (ctx: any, ...args: any[]) {
  const fn = this
  return (...more: any[]) => fn.apply(ctx, [...args, ...more])
}
```

### 6. 柯里化

```ts
function curry(fn: Function) {
  return function curried(...args: any[]) {
    if (args.length >= fn.length) return fn.apply(this, args)
    return curried.bind(this, ...args)
  }
}
```

## 📚 数据结构

### 7. LRU 缓存

```ts
class LRUCache {
  private map = new Map<string, any>()
  constructor(private capacity: number) {}

  get(key: string) {
    if (!this.map.has(key)) return -1
    const v = this.map.get(key)
    this.map.delete(key)
    this.map.set(key, v)
    return v
  }

  put(key: string, val: any) {
    if (this.map.has(key)) this.map.delete(key)
    else if (this.map.size >= this.capacity) {
      const firstKey = this.map.keys().next().value
      this.map.delete(firstKey!)
    }
    this.map.set(key, val)
  }
}
```

### 8. 大数相加（字符串）

```ts
function addStrings(a: string, b: string) {
  let i = a.length - 1, j = b.length - 1, carry = 0, res = ''
  while (i >= 0 || j >= 0 || carry) {
    const sum = (i >= 0 ? +a[i--] : 0) + (j >= 0 ? +b[j--] : 0) + carry
    res = (sum % 10) + res
    carry = Math.floor(sum / 10)
  }
  return res
}
```

### 9. 千分位分隔

```ts
function toThousands(n: number) {
  return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}
```

### 10. 数组拍平（指定深度）

```ts
function flat(arr: any[], depth = 1): any[] {
  return depth <= 0
    ? arr
    : arr.reduce((a, v) => a.concat(Array.isArray(v) ? flat(v, depth - 1) : v), [])
}
```

## ⚛️ React Hooks 手写

### 11. useState

```ts
function useState(initial: any) {
  const hook = mountWorkInProgressHook()
  hook.memoizedState = initial
  return [
    () => hook.memoizedState,
    (next: any) => {
      hook.memoizedState = typeof next === 'function' ? next(hook.memoizedState) : next
      scheduleUpdate()
    }
  ]
}
```

### 12. useEffect（伪码）

```ts
function useEffect(fn: () => void, deps: any[]) {
  const hook = mountWorkInProgressHook()
  if (hook.deps === undefined || !shallowEqual(deps, hook.deps)) {
    hook.deps = deps
    effectsToRun.push(() => fn())
  }
}
```

## 🎨 CSS / DOM

### 13. 深拷贝（DOM 序列化）

```ts
function cloneDOM(node: Node): Node {
  return node.cloneNode(true)
}
```

### 14. 解析 URL 查询字符串

```ts
function parseQuery(qs: string) {
  return qs.replace(/^\?/, '').split('&').reduce((acc, pair) => {
    const [k, v = ''] = pair.split('=')
    const key = decodeURIComponent(k)
    const value = decodeURIComponent(v)
    if (acc[key]) {
      acc[key] = [].concat(acc[key], value)
    } else {
      acc[key] = value
    }
    return acc
  }, {} as Record<string, string | string[]>)
}
```

### 15. 手写 instanceof

```ts
function myInstanceof(obj: any, Ctor: any) {
  let proto = Object.getPrototypeOf(obj)
  while (proto) {
    if (proto === Ctor.prototype) return true
    proto = Object.getPrototypeOf(proto)
  }
  return false
}
```

## 📊 实现工具

### 16. 数组去重

```ts
const unique = (arr: number[]) => [...new Set(arr)]
const uniqueBy = (arr: any[], key: string) => [...new Map(arr.map(x => [x[key], x])).values()]
```

### 17. instanceof & typeof

```ts
const myType = (v: any) =>
  Object.prototype.toString.call(v).slice(8, -1).toLowerCase()
```

### 18. Function.prototype.compose

```ts
const compose = (...fns: Function[]) => (x: any) =>
  fns.reduceRight((v, f) => f(v), x)
```

## 🧠 算法题

### 19. 括号匹配

```ts
function isValid(s: string) {
  const stack: string[] = []
  const map: Record<string, string> = { ')': '(', ']': '[', '}': '{' }
  for (const c of s) {
    if ('([{'.includes(c)) stack.push(c)
    else if (stack.pop() !== map[c]) return false
  }
  return stack.length === 0
}
```

### 20. 千分位数字格式化（含小数）

```ts
function format(n: number) {
  const [int, dec] = n.toString().split('.')
  return int.replace(/\B(?=(\d{3})+(?!\d))/g, ',') + (dec ? `.${dec}` : '')
}
```

## 📦 实战题

### 21. 手写 EventEmitter

```ts
class EventEmitter {
  private listeners = new Map<string, Set<Function>>()
  on(event: string, fn: Function) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set())
    this.listeners.get(event)!.add(fn)
    return () => this.off(event, fn)
  }
  emit(event: string, ...args: any[]) {
    this.listeners.get(event)?.forEach(fn => fn(...args))
  }
  off(event: string, fn: Function) {
    this.listeners.get(event)?.delete(fn)
  }
}
```

### 22. 浅比较

```ts
function shallowEqual(a: any, b: any) {
  if (Object.is(a, b)) return true
  if (typeof a !== 'object' || typeof b !== 'object' || !a || !b) return false
  const ka = Object.keys(a), kb = Object.keys(b)
  if (ka.length !== kb.length) return false
  return ka.every(k => Object.hasOwn(b, k) && Object.is(a[k], b[k]))
}
```

### 23. JSON.parse 实现（带安全字符）

```ts
function parseJson(s: string) {
  return eval('(' + s + ')')
  // 注意：实际应用不安全！真实场景用 new Function + sandbox
}
```

### 24. setTimeout 模拟 setInterval

```ts
function myInterval(fn: () => void, ms: number) {
  let timer: any
  const wrap = () => { fn(); timer = setTimeout(wrap, ms) }
  timer = setTimeout(wrap, ms)
  return () => clearTimeout(timer)
}
```

### 25. fetch 重试 N 次

```ts
async function fetchWithRetry(url: string, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const res = await fetch(url)
      if (res.ok) return await res.json()
      throw new Error(res.statusText)
    } catch (e) {
      if (i === retries - 1) throw e
      await new Promise(r => setTimeout(r, 1000 * (i + 1)))
    }
  }
}
```

### 26. JSONP

```ts
function jsonp(url: string, callbackName = '_cb_' + Date.now()) {
  return new Promise((resolve, reject) => {
    (window as any)[callbackName] = (data: any) => {
      resolve(data)
      delete (window as any)[callbackName]
      document.body.removeChild(script)
    }
    const script = document.createElement('script')
    script.src = `${url}?callback=${callbackName}`
    script.onerror = reject
    document.body.appendChild(script)
  })
}
```

### 27. 模板字符串解析（迷你）

```ts
function template(str: string, data: Record<string, any>) {
  return str.replace(/\{\{(\w+)\}\}/g, (_, k) => data[k] ?? '')
}
```

### 28. 数组转树

```ts
type Item = { id: number; parentId: number; name: string; children?: Item[] }
function arrToTree(arr: Item[]): Item[] {
  const map = new Map(arr.map(i => [i.id, { ...i, children: [] }]))
  const tree: Item[] = []
  for (const item of map.values()) {
    if (item.parentId === 0) tree.push(item)
    else map.get(item.parentId)?.children!.push(item)
  }
  return tree
}
```

### 29. 树转数组（扁平化）

```ts
function flattenTree(root: Item): Item[] {
  const out: Item[] = []
  const dfs = (n: Item) => {
    out.push(n)
    n.children?.forEach(dfs)
  }
  dfs(root)
  return out
}
```

### 30. 实现 Promise.race

```ts
Promise.myRace = (promises: Promise<any>[]) =>
  new Promise((resolve, reject) => {
    promises.forEach(p => Promise.resolve(p).then(resolve, reject))
  })
```

## 🔗 下一步

- [高频面试题](/13-interview/basic)
- [系统设计题](/13-interview/system)


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java](https://java-px.bot.cd/java-web-manual/):Java 后端 API
- [android](https://java-px.bot.cd/android/):Android 移动
- [java-language](https://java-px.bot.cd/java-language/):Java 基础
