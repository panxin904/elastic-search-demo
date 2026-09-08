---
title: §8.81 全局响应式工具类演示
date: 2026-09-08
---

# §8.81 全局响应式工具类演示

> 全站只需 `import './style.css'` 或通过 `@shared` 引用，所有工具类自动生效。
> 拖动浏览器窗口宽度即可看到响应式效果。

## 📦 1. 网格布局

<div class="at-grid-cards">
  <div class="at-card"><strong>卡片 1</strong><p>移动端单列，平板 2 列，桌面 3 列，大屏 4 列。</p></div>
  <div class="at-card"><strong>卡片 2</strong><p><code>auto-fit + minmax</code> 自动填充，无需写媒体查询。</p></div>
  <div class="at-card"><strong>卡片 3</strong><p><code>clamp()</code> 流式间距，移动紧凑 / 桌面宽松。</p></div>
  <div class="at-card"><strong>卡片 4</strong><p>无需 JavaScript，纯 CSS 自适应。</p></div>
  <div class="at-card"><strong>卡片 5</strong><p>新增第 5 张卡片，仍保持完整布局。</p></div>
  <div class="at-card"><strong>卡片 6</strong><p>当窗口过窄时，自动回流为 1 列。</p></div>
</div>

## 🎨 2. 流式字号（h1/h2/h3 + clamp）

<div class="at-stack at-container">
  <h1 class="at-h1">流式 H1（标题）</h1>
  <h2 class="at-h2">流式 H2（副标题）</h2>
  <h3 class="at-h3">流式 H3（小节）</h3>
  <p class="at-text-lg">流式正文（大字号）</p>
  <p class="at-text-sm">流式辅助文字（小字号）</p>
</div>

## 🧱 3. 弹性容器（stack/row）

<div class="at-stack at-container">
  <div class="at-card at-link-card">📌 <strong>提示 1</strong>：移动端纵向堆叠</div>
  <div class="at-card at-link-card">📌 <strong>提示 2</strong>：窗口 ≥ 600px 时（容器查询）自动横向排列</div>
  <div class="at-card at-link-card">📌 <strong>提示 3</strong>：使用 <code>.at-container</code> 包裹即可启用容器查询</div>
</div>

## 📐 4. 内容宽度限制

<div class="at-prose at-content-text">
<p>这是受控宽度的正文（<code>max-width: 75ch</code>），在大屏上有更好的可读性。
段落用 <code>clamp(0.95rem, 0.5vw + 0.9rem, 1.05rem)</code> 流式字号，
行高 <code>1.8</code> 适合长篇阅读。</p>
</div>

<div class="at-prose-wide at-content-text">
<p>这是宽版正文（<code>max-width: 90ch</code>），用于需要展示更宽内容的场景。
两边距通过 <code>margin-inline: auto</code> 自动居中。</p>
</div>

## 🚦 5. 信息密度工具

<div class="at-row">
  <span class="at-meta">2026-09-08</span>
  <span class="at-meta">难度: ⭐⭐</span>
  <span class="at-meta">阅读: 5 min</span>
  <span class="at-meta">标签: responsive · css · utils</span>
</div>

## 📋 6. 显式断点类（mobile-first）

<div class="at-grid-cards">
  <div class="at-card">xs (移动) 单列 · sm:at-grid-2 (≥640px) 2 列</div>
  <div class="at-card">md (≥768px) 3 列 · lg (≥1024px) 4 列</div>
  <div class="at-card">配合 at-grid-cards 自适应基础布局</div>
</div>

## 🧩 7. 完整工具清单

| 类别 | 类名 | 用途 |
|---|---|---|
| 网格 | `at-grid-cards` / `at-grid-2` / `at-grid-3` | 自适应卡片布局 |
| 弹性 | `at-stack` / `at-row` | flex 容器 |
| 字号 | `at-h1` / `at-h2` / `at-h3` / `at-text-{sm,lg}` | 流式排版 |
| 间距 | `at-p-{1,2,3}` / `at-mt-{1,2,3}` | 响应式 padding/margin |
| 卡片 | `at-card` / `at-link-card` | 标准 / 链接卡片 |
| 容器 | `at-container` | 启用容器查询 |
| 内容 | `at-prose` / `at-prose-wide` | 宽度限制 |
| 文本 | `at-content-text` / `at-meta` | 排版预设 |
| 提示 | `at-banner` | 信息条 |
| 断点 | `sm:/md:/lg:/xs:` 前缀 | 显式断点 |

## 🔍 8. 容器查询 vs 媒体查询

容器查询根据**父容器尺寸**变化，媒体查询根据**视口尺寸**变化：

<div class="at-container" style="background: var(--vp-c-bg-soft); padding: 1rem; border-radius: 8px; resize: horizontal; overflow: auto; min-width: 300px;">
  <p>👉 <strong>拖动右下角</strong>查看 <code>.at-stack</code> 在容器内的响应式效果</p>
  <div class="at-stack">
    <span class="at-card">块 1（移动时纵向）</span>
    <span class="at-card">块 2（≥600px 容器宽时横向）</span>
    <span class="at-card">块 3</span>
  </div>
</div>

## 📚 9. 引入方式

**VitePress 自动加载**（共享 theme 已通过 `@shared` 别名引用）：

```ts
// shared-assets/vitepress-template/theme/style.css
// 内容已追加到末尾，本文件无需手动 import
```

**站点本地 style.css 引用**：

```css
/* ai-html/.vitepress/theme/style.css */
@import '@shared/vitepress-template/theme/style.css';
```

**HTML 直接使用**：

```html
<div class="at-grid-cards">
  <div class="at-card">内容</div>
  <div class="at-card">内容</div>
</div>
```
