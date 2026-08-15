---
title: Jest / Vitest 单元测试
---

# Jest / Vitest 单元测试

## 🆚 Jest vs Vitest

| | Jest | Vitest |
|--|------|--------|
| 引擎 | Node | Vite + esbuild |
| 速度 | 慢 | 快 10x+ |
| ESM | 配置复杂 | 原生 |
| TS | ts-jest | 内置 |
| 生态系统 | 极大 | 增长中 |
| API | 类似 | 类似（基本可互改） |

**新项目建议 Vitest**（Vue / Vite / Next.js 都适合）；**Jest** 适合 React 长期项目。

## 🧪 基本模式 (AAA)

```ts
// counter.ts
export function add(a: number, b: number) {
  return a + b
}

// counter.test.ts
import { describe, it, expect } from 'vitest'
import { add } from './counter'

describe('add', () => {
  it('正数相加', () => {
    expect(add(1, 2)).toBe(3)
  })

  it('负数相加', () => {
    expect(add(-1, -2)).toBe(-3)
  })
})
```

## 🎯 常用 matcher

```ts
expect(x).toBe(3)               // 严格相等
expect(x).toEqual({ a: 1 })     // 深度相等
expect(x).toBeTruthy()
expect(x).toContain('abc')
expect(arr).toHaveLength(3)
expect(fn).toThrow()
expect(mock).toHaveBeenCalledWith(...)
expect(0.1 + 0.2).toBeCloseTo(0.3)  // 浮点数
```

## 🧰 Mock

```ts
import { vi } from 'vitest'

const sendEmail = vi.fn()
vi.mock('./email', () => ({ sendEmail: vi.fn() }))

it('调用一次', () => {
  sendEmail('a@b.com')
  expect(sendEmail).toHaveBeenCalledTimes(1)
})
```

## ⏱ 异步

```ts
it('async', async () => {
  const user = await fetchUser(1)
  expect(user.name).toBe('alice')
})

// 拒绝 Promise
await expect(failingFn()).rejects.toThrow('oops')
```

## ⏳ fake timers

```ts
beforeEach(() => vi.useFakeTimers())

it('setTimeout', () => {
  const fn = vi.fn()
  setTimeout(fn, 1000)
  vi.advanceTimersByTime(1000)
  expect(fn).toHaveBeenCalled()
})
```

## 🧪 覆盖度

```bash
vitest run --coverage
```

`vitest.config.ts`：
```ts
export default {
  test: {
    coverage: {
      provider: 'v8',
      include: ['src/**'],
      thresholds: { lines: 80, functions: 80, branches: 75 }
    }
  }
}
```

## 🧰 实用模式

### 1. 模拟 fetch

```ts
global.fetch = vi.fn(() =>
  Promise.resolve({ json: () => Promise.resolve({ id: 1, name: 'a' }) })
)
```

### 2. 测试 React Hook

```tsx
import { renderHook, act } from '@testing-library/react'
import { useCounter } from './useCounter'

it('increment', () => {
  const { result } = renderHook(() => useCounter())
  act(() => result.current.inc())
  expect(result.current.value).toBe(1)
})
```

### 3. Mock 模块

```ts
vi.mock('./db', () => ({
  insert: vi.fn().mockResolvedValue({ id: 1 })
}))
```

## ⚖️ 测什么

```
✅ 业务纯函数
✅ 自定义 hook（renderHook）
✅ 工具库
⚠ 组件：基本渲染 / 关键交互（详交给 RTL/E2E）
❌ 实现细节（不要测试 useState 是否被调用）
❌ 第三方库
```

## 🔗 下一步

- [React Testing Library](/10-testing/rtl)
- [Cypress / Playwright](/10-testing/e2e)
- [Storybook 组件测试](/10-testing/storybook)
