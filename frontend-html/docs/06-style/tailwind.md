---
title: Tailwind / UnoCSS
---

# Tailwind / UnoCSS

## 🌊 Tailwind CSS

**Utility-first CSS 框架**：在 HTML / JSX 中拼出 class。

```html
<button class="px-4 py-2 bg-cyan-500 text-white rounded-md hover:bg-cyan-600">
  Click me
</button>
```

### 优点

- **不用离开 HTML**：无需切换文件
- **约束体积**：自动 purge 未用到的 class
- **一致性**：design token 内置（间距、颜色、字号）
- **dark mode**：内置 `dark:` 前缀

### 配置文件

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,vue}'],
  theme: {
    extend: {
      colors: { brand: '#06b6d4' },
      spacing: { '18': '4.5rem' }
    }
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/typography')]
}
```

### 与 React / Vue 集成

```tsx
// React + tailwind-variants / clsx 组合
import { clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

function Button({ variant = 'primary', children }) {
  return (
    <button className={twMerge(
      'px-4 py-2 rounded-md transition',
      variant === 'primary' && 'bg-cyan-500 text-white hover:bg-cyan-600',
      variant === 'ghost' && 'text-cyan-500 hover:bg-cyan-50'
    )}>
      {children}
    </button>
  )
}
```

### 变体

```jsx
<button className="
  px-4 py-2
  bg-cyan-500 hover:bg-cyan-600 active:bg-cyan-700
  text-white font-medium
  rounded-md
  disabled:opacity-50
  md:px-6 md:py-3
  dark:bg-cyan-400 dark:text-gray-900
">
```

### Tailwind v4

2024+ 新版本：
- **CSS-first 配置**（在 CSS 里写 `@theme`）
- 零配置 / 更快的构建
- 兼容现有 v3 项目（迁移工具齐全）

## ⚡ UnoCSS

**更激进**的 atomic CSS：

- **按需生成**：原子化 class 任意组合（`p-4` 等同 `padding: 1rem`）
- **preset-tailwind**：与 Tailwind v3 兼容
- **预设**：UnoCSS 有几十个 preset（wind / mini / icons / typography）

```ts
// uno.config.ts
import { defineConfig, presetWind } from 'unocss'

export default defineConfig({
  presets: [
    presetWind(),
    presetIcons({ scale: 1.2 }),
    presetAttributify()
  ]
})
```

```html
<!-- attributify 写法 -->
<button
  bg="cyan-500 hover:cyan-600"
  text="white"
  p="x-4 y-2"
  rounded="md"
>Click</button>
```

## 🆚 Tailwind vs UnoCSS vs vanilla-extract

| | Tailwind | UnoCSS | vanilla-extract |
|--|---------|--------|-----------------|
| 运行时 | 编译期 | 编译期 | 编译期 |
| 学习曲线 | 平缓 | 平缓 | 中（要写 TS） |
| 配置 | tailwind.config.js | uno.config.ts | CSS.ts |
| Bundle | 极小（按需） | 极小 | 0 |
| 生态 | 极大 | 中 | 小但稳 |

## 🛠️ 选型

| 场景 | 选择 |
|------|------|
| 想要快 / 团队接受 utility-first | Tailwind |
| 想要最快构建 + 与 Tailwind 兼容 | UnoCSS |
| 想 strict TS types + zero runtime | vanilla-extract |
| 公司项目历史遗留 CSS / 复杂组件库 | CSS Modules / CSS-in-JS |

## 🔗 下一步

- [CSS Modules](/06-style/css-modules)
- [CSS-in-JS](/06-style/css-in-js)
- [设计系统 / 组件库](/06-style/design-system)
