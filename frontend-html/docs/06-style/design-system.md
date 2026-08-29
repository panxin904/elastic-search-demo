---
title: 设计系统 / 组件库
date: 2026-08-15  # date-auto-injected
---

# 设计系统 / 组件库

## 🎯 两种"系统"

| 术语 | 含义 |
|------|------|
| **设计系统** (Design System) | 设计 token + 组件 + 文档 + 规范一整套（设计 + 工程） |
| **UI 组件库** (Component Library) | 一套可复用 React/Vue 组件 |

## 🧱 主流 UI 库

### React

| 库 | 特点 | 适合 |
|----|------|------|
| **Ant Design** | 中文企业风、组件全 | 中后台 |
| **Material UI (MUI)** | Google Material | 通用 |
| **Chakra UI** | 简洁、props 风格 | 通用 |
| **shadcn/ui** | 复制粘贴源码 + Tailwind | 想要可控 |
| **Radix UI** | 无样式可访问性 primitives | 高度定制 |
| **HeroUI / NextUI** | 现代、Tailwind | 现代中后台 |
| **Arco Design** | 字节跳动 | 中后台 |

### Vue

| 库 | 适合 |
|----|------|
| **Element Plus** | 中后台首选 |
| **Vuetify** | Material 风 |
| **Naive UI** | 简洁现代 |
| **Arco Vue** | 字节跳动 |

## 🎨 Design Token 三层

```ts
// 1. primitive（原子）
export const color = {
  blue500: '#06b6d4',
  red500:   '#ef4444'
}

// 2. semantic（语义）
export const theme = {
  brand:    color.blue500,
  danger:   color.red500,
  text:     '#0f172a',
  bg:       '#ffffff'
}

// 3. component（组件）
export const button = {
  primary:    { bg: theme.brand, fg: '#fff' },
  destructive:{ bg: theme.danger, fg: '#fff' }
}
```

下游可以**跨主题切换**（比如白天 / 暗色 / 品牌白标）。

## 🏗 自建设计系统

```ts
// packages/ui/src/index.ts
export { Button } from './Button'
export { Card } from './Card'
export { tokens } from './tokens'

// packages/ui/package.json
{
  "name": "@org/ui",
  "main": "./dist/index.js",
  "types": "./dist/index.d.ts"
}
```

```tsx
// apps/web
import { Button } from '@org/ui'

<Button variant="primary">OK</Button>
```

monorepo 方式：直接源码 import，无需发布。

## 🛠️ 关键工具

| 工具 | 作用 |
|------|------|
| **Storybook** | 组件文档 / 可视化测试 |
| **Style Dictionary** | 跨平台 token（Web/iOS/Android） |
| **Figma Tokens** | Figma → 代码 token |
| **Changesets / Lerna** | 版本发布 + changelog |

```ts
// storybook 配置文件
export default {
  stories: ['../src/**/*.stories.@(ts|tsx)']
}
```

## 📐 文档规范

- 每个组件必须有 **Props Type**
- **用法示例**（基础 / 进阶 / 禁用状态 / 错误状态）
- **a11y 说明**
- **设计稿链接 / Figma**

## 🔗 下一步

- [Tailwind / UnoCSS](/06-style/tailwind)
- [CSS Modules](/06-style/css-modules)
- [Storybook 组件测试](/10-testing/storybook)
