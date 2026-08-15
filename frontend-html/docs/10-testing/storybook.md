---
title: Storybook 组件测试
---

# Storybook

## 🎯 Storybook 是什么

**组件驱动的开发 + 文档平台**：把组件单独拿出来"展示"，独立开发、测试、视觉回归。

```
优点：
  ✅ 不依赖业务路由，快速调样式
  ✅ 设计 / 前端协作平台
  ✅ 自动生成 props 文档
  ✅ 内置 a11y / 视觉 / 交互测试插件
```

## 📦 启动

```bash
npx storybook@latest init
```

自动生成 `.storybook/` 目录和示例 story。

## 🧱 写第一个 Story

```tsx
// Button.tsx
export function Button({ variant = 'primary', children, onClick }) {
  return <button className={`btn btn-${variant}`} onClick={onClick}>{children}</button>
}
```

```tsx
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react'
import { Button } from './Button'

const meta: Meta<typeof Button> = {
  component: Button,
  title: 'UI/Button',
  argTypes: {
    variant: { control: 'select', options: ['primary', 'ghost'] }
  }
}
export default meta

type Story = StoryObj<typeof Button>

export const Primary: Story = {
  args: { variant: 'primary', children: 'Click me' }
}

export const Ghost: Story = {
  args: { variant: 'ghost', children: 'Cancel' }
}
```

打开 `http://localhost:6006` 即可看到。

## 🧩 高级特性

### 装饰器（Context 模拟）

```ts
const meta = {
  decorators: [
    (Story) => (
      <ThemeProvider>
        <MemoryRouter>
          <Story />
        </MemoryRouter>
      </ThemeProvider>
    )
  ]
}
```

### 组件测试（Story 本身做测试）

```tsx
export const EmptyCart: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement)
    expect(canvas.getByText(/购物车为空/)).toBeInTheDocument()
  }
}
```

可以启用 **@storybook/test-runner** 把所有 story 自动跑一遍。

## 🧪 测试插件

| 插件 | 作用 |
|------|------|
| `@storybook/addon-a11y` | 自动 a11y 审计（axe-core） |
| `@storybook/addon-essentials` | Controls / Actions / Viewport |
| `storybook-addon-vitest` | 在 Storybook 中跑 Vitest |
| `chromatic` | 视觉回归（云服务） |

```ts
// .storybook/main.ts
export default {
  addons: ['@storybook/addon-a11y', '@storybook/addon-essentials']
}
```

## 🎨 写文档

Storybook 自动从 story 生成 props 表 + 示例。

```md
# 设计系统中加入 Storybook 链接
- 每个组件含至少 3 个 story
- 至少一个 "Empty / Loading / Error / Filled" 状态
- 视觉回归基线（Chromatic / Loki）
```

## 📦 发布 Storybook

```bash
npx storybook build
# 输出到 storybook-static/
```

可以部署到 Vercel / GitHub Pages / 公司内网。

## 🆚 Storybook vs Styleguidist

| | Storybook | Styleguidist |
|--|-----------|--------------|
| 框架 | 任意（React/Vue/Angular） | 主要 React |
| 测试 | 内置 | 仅样式文档 |
| 视觉回归 | 插件 | 否 |
| 状态 | 当前事实标准 | 旧项目偏好 |

## 🔗 下一步

- [设计系统](/06-style/design-system)
- [CI/CD](/14-tools/cicd)
- [Jest / Vitest](/10-testing/unit)
