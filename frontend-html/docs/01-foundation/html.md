---
title: HTML 语义化
date: 2026-08-15  # date-auto-injected
---

# HTML 语义化

> 用对的标签表达对的含义，是前端工程师的基本功。

## 🎯 什么是语义化

语义化 HTML = 用最合适的标签表达内容，让机器（搜索引擎、屏幕阅读器、爬虫）能"读懂"页面。

```html
<!-- ❌ 一坨 div -->
<div class="header">
  <div class="nav">
    <div><a href="/">首页</a></div>
  </div>
</div>

<!-- ✅ 用对的标签 -->
<header>
  <nav>
    <ul><li><a href="/">首页</a></li></ul>
  </nav>
</header>
```

## 🧱 常用语义标签

| 标签 | 用途 |
|------|------|
| `<header>` | 页面或区块的头部 |
| `<nav>` | 导航 |
| `<main>` | 页面主内容（一个页面只能有一个） |
| `<article>` | 独立的内容块（博客、新闻、商品） |
| `<section>` | 主题性分组（带标题） |
| `<aside>` | 侧边栏 / 与主内容相关但非核心 |
| `<footer>` | 页脚 |
| `<figure>` / `<figcaption>` | 图 + 说明 |
| `<time datetime="...">` | 时间 |
| `<mark>` | 高亮 |

## 🆘 ARIA 无障碍扩展

当 HTML 语义不够时，用 ARIA 补充：

```html
<!-- 弹出层 -->
<div role="dialog" aria-modal="true" aria-labelledby="title">
  <h2 id="title">确认删除？</h2>
</div>

<!-- 实时通知 -->
<div role="status" aria-live="polite">已保存</div>

<!-- 装饰性图标 -->
<button>
  <span aria-hidden="true">×</span>
  <span class="sr-only">关闭</span>
</button>
```

## ✅ 语义化最佳实践

1. **能用 `<button>` 就不写 `<div onClick>`**：天然支持键盘 / a11y。
2. **能用 `<a href>` 就不写 `<div onClick>`**：可右键打开、可被爬虫看到。
3. **标题用 `<h1>-<h6>`，不要跳级**：对屏幕阅读器至关重要。
4. **`alt`** 描述图片作用（不是"图片"，是"一只金毛在公园追球"）。
5. 表单用 `<label for>` 关联 input，或用 `aria-label` 兜底。
6. **`<table>` 只用于表格数据**，布局用 CSS Grid/Flex。

## 🚫 反模式

```html
<!-- ❌ 用 div 做按钮 -->
<div class="btn" onclick="submit()">提交</div>

<!-- ✅ 用 button -->
<button type="submit" class="btn">提交</button>

<!-- ❌ 跳级标题 -->
<h1>标题</h1>
<h3>子标题</h3>

<!-- ✅ -->
<h1>标题</h1>
<h2>子标题</h2>
```

## 🔗 下一步

- [CSS 基础与盒模型](/01-foundation/css)
- [可访问性 a11y](/12-perf/a11y)
