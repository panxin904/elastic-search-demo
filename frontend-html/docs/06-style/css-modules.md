---
title: CSS Modules
---

# CSS Modules

## 🎯 CSS Modules 是什么

把 CSS 文件 `import` 进 JS 中，并且**类名自动 scope** 的方案。由构建工具（Vite / webpack）支持。

```css
/* Button.module.css */
.button {
  padding: 8px 16px;
  background: cyan;
}
.button.primary {
  background: #06b6d4;
  color: white;
}
```

```jsx
import s from './Button.module.css'

<button className={s.button}>Default</button>
<button className={`${s.button} ${s.primary}`}>Primary</button>
```

构建后输出：
```html
<button class="_button_abc123">Default</button>
<button class="_button_abc123 _primary_def456">Primary</button>
```

## ✅ 优点

- **作用域隔离**：不会出现全局污染
- **复用纯 CSS**：不依赖任何运行时
- **零运行时开销**：构建期 class 名 hash
- **CSS 文件可读**：保持传统 CSS 心智

## ⚠️ 缺点

- 不易跨组件共享样式（除非配合 :global()）
- 动态化不如 CSS-in-JS

## 🌐 :global 抛出全局

```css
.title :global(.highlight) {
  /* 这里的 .highlight 不被 scope */
}
```

## 🧩 与 Tailwind、CSS 变量搭配

```css
/* Button.module.css */
.button {
  padding: var(--btn-padding, 8px 16px);
  background: var(--btn-bg, cyan);
  border-radius: var(--btn-radius, 4px);
}
```

```css
/* globals.css */
:root {
  --btn-padding: 0.5rem 1rem;
  --btn-bg: #06b6d4;
}
```

CSS Variables 实现**主题 / 动态切换**。

## 🛠️ Vite / Next.js 自带支持

```
Button.tsx
Button.module.css
```

无需安装任何依赖。

## 🔗 下一步

- [Tailwind / UnoCSS](/06-style/tailwind)
- [CSS-in-JS](/06-style/css-in-js)
