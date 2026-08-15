---
title: CSS-in-JS
---

# CSS-in-JS

## 🎯 概念

把 CSS 写在 JS / TS 中，通过运行时或编译时生成类名。

## 📚 主流方案

### styled-components（运行时）

```jsx
import styled from 'styled-components'

const Button = styled.button`
  background: ${({ primary }) => primary ? '#06b6d4' : '#fff'};
  color: ${({ primary }) => primary ? 'white' : '#333'};
  padding: 0.5rem 1rem;
  border-radius: 4px;
`

<Button primary>Click</Button>
```

### Emotion（运行时）

```jsx
import { css } from '@emotion/react'

const buttonStyle = css`
  padding: 8px 16px;
  &:hover { opacity: 0.8; }
`

<button css={buttonStyle}>Click</button>
```

### vanilla-extract（**编译时**）

```ts
// styles.css.ts
import { style, styleVariants } from '@vanilla-extract/css'

export const button = style({
  padding: '8px 16px',
  background: '#06b6d4',
  color: 'white'
})

export const buttonVariant = styleVariants({
  primary: { background: '#06b6d4', color: 'white' },
  ghost: { background: 'transparent', color: '#06b6d4' }
})
```

```tsx
import * as s from './styles.css'

<button className={s.buttonVariant.primary}>Click</button>
```

### Tailwind（**编译时 utility**）

虽然不算 CSS-in-JS，但语法上类似——已在 [Tailwind 章节](/06-style/tailwind) 详述。

## 🆚 运行时 vs 编译时

| | 运行时（styled / Emotion） | 编译时（vanilla-extract / Linaria） |
|--|----------------|------------------|
| Bundle 体积 | +10-30KB | 0 |
| 类型 | 一般 | 完整 TS |
| 动态主题 | 易（props） | 需 token 文件 |
| SSR | 需 stylesheet extractor | 自动 |
| 心智 | 易上手 | 要写 .css.ts |

## ⚠️ 运行时方案的痛点

1. **RSC（React Server Components）兼容性差**：动态注入样式不能用
2. **Bundle 大**：~10KB 起步
3. **调试体验**：dev tools 中出现不友好类名
4. **包大小依赖**：很多项目不再推荐

> 趋势：**Tailwind / vanilla-extract / Linaria / CSS Modules** 等"编译时"方案正取代 styled-components。

## 🛠️ 选型

| 场景 | 选择 |
|------|------|
| 老项目维护 | styled-components |
| 新 SaaS / 想要严格类型 + 编译时 | vanilla-extract |
| 想要 SSR / RSC 友好 | Tailwind / Linaria |
| 想要 0 工具 | CSS Modules + CSS Variables |

## 🔗 下一步

- [Tailwind / UnoCSS](/06-style/tailwind)
- [CSS Modules](/06-style/css-modules)
- [设计系统 / 组件库](/06-style/design-system)
