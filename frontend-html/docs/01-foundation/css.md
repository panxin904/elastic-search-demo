---
title: CSS 基础
date: 2026-08-15  # date-auto-injected
---

# CSS 基础与盒模型

## 📦 盒模型

每个元素都是一个盒子：

```
┌────────────────────────────────────┐
│ margin                              │
│  ┌──────────────────────────────┐   │
│  │  border                       │   │
│  │  ┌────────────────────────┐  │   │
│  │  │  padding               │  │   │
│  │  │  ┌──────────────────┐  │  │   │
│  │  │  │  content         │  │  │   │
│  │  │  └──────────────────┘  │  │   │
│  │  └────────────────────────┘  │   │
│  └──────────────────────────────┘   │
└────────────────────────────────────┘
```

两种盒模型：

| | content-box | border-box |
|--|--|--|
| 宽 = | content | content + padding + border |
| 默认 | 旧浏览器 | 现代默认 |

```css
:root {
  box-sizing: border-box; /* 全局推荐 */
}
*, *::before, *::after { box-sizing: inherit; }
```

## 📐 布局：现代三件套

### Flexbox — 一维布局

```css
.row {
  display: flex;
  justify-content: space-between; /* 主轴 */
  align-items: center;            /* 交叉轴 */
  gap: 16px;                      /* 子项间距 */
}
.item { flex: 1; }                 /* 等分剩余空间 */
```

### Grid — 二维布局

```css
.grid {
  display: grid;
  grid-template-columns: 200px 1fr 200px; /* 三列：左固定 中间自适应 右固定 */
  grid-template-rows: auto 1fr auto;     /* 行：header / main / footer */
  gap: 16px;
  min-height: 100vh;
}
```

### 容器查询 — 组件级响应式

```css
.card-container { container-type: inline-size; }

@container (min-width: 500px) {
  .card { display: grid; grid-template-columns: 1fr 2fr; }
}
```

## 🎨 优先级与继承

```css
/* 优先级（从高到低，相同则后者覆盖）：*/
/* !important > 内联 style > #id > .class > tag > * > 继承 */
.btn.danger { color: red; }  /* class×2 比 id×1 略高 */
```

## 🧬 自定义属性（CSS 变量）

```css
:root {
  --color-brand: #06b6d4;
  --space-1: 4px;
  --radius-md: 8px;
}
.card {
  color: var(--color-brand);
  padding: var(--space-1) calc(var(--space-1) * 4);
  border-radius: var(--radius-md);
}

@media (prefers-color-scheme: dark) {
  :root { --color-brand: #22d3ee; }
}
```

## 🔧 常用工具

- **CSS Reset**：消除浏览器默认样式
- **PostCSS + Autoprefixer**：自动加厂商前缀
- **CSS Modules / CSS-in-JS**：作用域隔离

## 🔗 下一步

- [Tailwind / UnoCSS](/06-style/tailwind)
- [CSS-in-JS](/06-style/css-in-js)
- [CSS Modules](/06-style/css-modules)
