---
title: 加载性能
date: 2026-08-15  # date-auto-injected
---

# 加载性能

> 减少首屏到达时间（TTI / LCP）。

## 📦 减小 Bundle

1. **代码分割（懒加载）**

```tsx
import { lazy, Suspense } from 'react'

const Chart = lazy(() => import('./Chart'))

<Suspense fallback={<Spinner />}>
  <Chart />
</Suspense>
```

Next.js App Router / Nuxt 自动做基于路由的代码分割。

2. **Tree Shaking**：默认生产模式开启，但别忘了写 side-effect-free

```jsonc
// package.json
{
  "sideEffects": false
}
```

3. **压缩**：开启 gzip / brotli

```nginx
gzip_types application/javascript text/css;
# 或 brotli（需要模块编译）
```

4. **移除未用依赖**

```bash
npx knip   # 扫描未引用
```

## 🖼 资源优化

### 图片

```html
<img src="hero.avif"  type="image/avif" />  <!-- AVIF 体积更小 -->
<img src="hero.webp"  type="image/webp" />  <!-- 兼容回退 -->
<img src="hero.jpg" />
```

- 用 `<picture>` 或 `<source>` 让浏览器选择格式
- Vite plugin `vite-imagetools` 转格式
- Next.js `<Image>` 组件自动响应式 + 格式选择

### 字体

```css
@font-face {
  font-family: 'Inter';
  src: url('/inter.woff2') format('woff2');
  font-display: swap;       /* 先显示回退字形 */
  unicode-range: U+4E00-9FFF;  /* 中文字符子集 */
}
```

### 视频

```html
<video preload="metadata" poster="preview.jpg">
  <source src="clip.mp4" type="video/mp4" />
</video>
```

不用 `autoplay + preload=auto`，会拖慢首屏。

## 🚚 CDN 与缓存

```
资源          缓存策略
HTML          短（no-cache）— 内容可能更新
JS / CSS      hash 命名 + 1 年（immutable）
图片          hash 命名 + 1 年
字体          hash 命名 + 1 年
API 响应      ETag + 短缓存
```

```nginx
location ~* \.(js|css|woff2|woff)$ {
  add_header Cache-Control "public, max-age=31536000, immutable";
}
```

## ⏱ Preload / Prefetch / Preconnect

```html
<!-- 关键资源 -->
<link rel="preload" href="/hero.avif" as="image" />

<!-- 下一页 -->
<link rel="prefetch" href="/about.html" />

<!-- 第三方域 -->
<link rel="preconnect" href="https://api.example.com" />
```

## 🖥 SSR / SSG / Streaming

| 模式 | 首屏速度 | 服务器压力 | 适合 |
|------|---------|----------|------|
| CSR | 慢 | 低 | 后台 |
| SSR | 快（首字） | 高 | 内容型站点 |
| SSG | 最快（CDN） | 极低 | 博客、文档 |
| ISR | 介于 SSG 和 SSR | 中 | 大型内容站 |
| Streaming SSR | 更快 | 中 | Next.js 14+ |

## 📦 第三方依赖

- `partytown`：把 GTM / FB Pixel 跑在 Worker
- `<script async defer>` 让分析脚本非阻塞

```html
<script async src="https://www.googletagmanager.com/gtag/js?id=..." />
```

## 🪶 关键 CSS 内联

```tsx
// Next.js
<Head>
  <style dangerouslySetInnerHTML={{ __html: criticalCss }} />
</Head>
```

框架如 Vite / Next 默认支持 `critical-css` 插件。

## 🗜 HTML 极致小

- 用 `gzip` / `brotli` 压缩
- 移除空白 / 注释（生产构建）
- 把 `<link rel="modulepreload">` 显式声明

## 🛠 持续监控

```ts
// 上报 Web Vitals
import { onLCP, onINP, onCLS } from 'web-vitals'

onLCP(metric => {
  navigator.sendBeacon('/api/telemetry', JSON.stringify({
    name: 'lcp', value: metric.value
  }))
})
```

## 🔗 下一步

- [Core Web Vitals](/12-perf/cwv)
- [运行时性能](/12-perf/runtime)
- [Vite 原理](/05-build/vite)
