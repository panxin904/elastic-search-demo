---
title: React Testing Library
date: 2026-08-15  # date-auto-injected
---

# React Testing Library

## 🎯 哲学

**RTL 测试用户行为，而非实现细节**。

- 找元素：screen.getByRole / getByText / getByLabelText
- 触发事件：userEvent.click / type
- 断言：可见文本 / 属性 / 值

✅ 测试组件，❌ 测 hooks / state。

## 📦 安装

```bash
npm install --save-dev @testing-library/react @testing-library/user-event @testing-library/jest-dom
```

```ts
// vitest.config.ts
import '@testing-library/jest-dom/vitest'
```

## 🧱 第一个测试

```tsx
// Counter.tsx
export function Counter() {
  return (
    <div>
      <h1>0</h1>
      <button>+1</button>
    </div>
  )
}
```

```tsx
// Counter.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Counter } from './Counter'

it('点击 +1 数值增 1', async () => {
  render(<Counter />)

  await userEvent.click(screen.getByText('+1'))

  expect(screen.getByText('1')).toBeInTheDocument()
})
```

## 🔍 查询方法

| 方法 | 行为 |
|------|------|
| `getByRole('button', { name: '提交' })` | 通过 ARIA role + name |
| `getByLabelText('邮箱')` | 通过关联 label |
| `getByPlaceholderText('搜索')` | 通过 placeholder |
| `getByText('hello')` | 通过文本 |
| `getByTestId('cart')` | 通过 data-testid（最后手段） |

带 `getBy` 表示找不到就 throw；`findBy` 是异步；`queryBy` 找不到返回 null。

## 🎭 userEvent vs fireEvent

- **userEvent** 模拟真实用户：触发完整事件链
- **fireEvent** 只触发一个事件

```tsx
await userEvent.type(input, 'hello')
await userEvent.click(button)
await userEvent.tab()
```

## 🪟 Provider / Router 包裹

```tsx
import { render } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ThemeProvider } from './Theme'

function renderWithProviders(ui) {
  return render(
    <BrowserRouter>
      <ThemeProvider>{ui}</ThemeProvider>
    </BrowserRouter>
  )
}

renderWithProviders(<Page />)
```

## 🪝 测试 hook

```tsx
import { renderHook, act } from '@testing-library/react'

it('useCounter', () => {
  const { result } = renderHook(() => useCounter())
  act(() => result.current.inc())
  expect(result.current.value).toBe(1)
})
```

## ⏳ 异步断言

```tsx
await waitFor(() => {
  expect(screen.getByText('loaded')).toBeInTheDocument()
})

// 或 findBy，自动重试
expect(await screen.findByText('loaded')).toBeInTheDocument()
```

## 🐛 常用 debugging

```tsx
screen.debug()              // 打印当前 DOM
screen.logTestingPlaygroundURL()
```

## ⚠️ 反模式

1. **不要测试 state 是否被 set**：测输出
2. **不要用 container.querySelector**：用 screen.getBy*
3. **不要 snapshot 整个组件**：snapshot 易碎且不验证行为
4. **用 `act()` 包裹状态更新**：避免 warning

## 🔗 下一步

- [Jest / Vitest](/10-testing/unit)
- [Cypress / Playwright](/10-testing/e2e)
- [Storybook](/10-testing/storybook)
