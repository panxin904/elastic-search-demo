---
title: Core Web Vitals
date: 2026-08-15  # date-auto-injected
---

![浏览器关键渲染路径](/frontend-browser-pipeline.svg)

# Core Web Vitals

## 📊 CWV 三大指标

Google 2020 年推出，作为搜索排名因子之一。

| 指标 | 含义 | 阈值（好） |
|------|------|----------|
| **LCP** (Largest Contentful Paint) | 最大内容渲染时间 | < 2.5s |
| **INP** (Interaction to Next Paint) | 交互到下一次绘制 | < 200ms |
| **CLS** (Cumulative Layout Shift) | 累计布局偏移 | < 0.1 |

过去 FID 已被 INP 取代。

## 🔍 各指标怎么测

```js
import { onLCP, onINP, onCLS } from 'web-vitals'

onLCP(console.log)
onINP(console.log)
onCLS(console.log)
```

或在 Chrome DevTools → Performance / Lighthouse / Web Vitals 扩展。

## 🧱 LCP 优化

LCP 候选元素一般是：
- 大图（hero）
- 视频 / 海报
- 大段文本
- 大背景图

策略：
- 减小体积（WebP / AVIF）
- 优先级提示：`<link rel="preload" as="image">`
- SSR / 预渲染
- CDN + 边缘缓存
- 内联关键 CSS

## ⚡ INP 优化

INP 比 FID 更严格，要求每个交互延迟都 < 200ms。

**长任务拆分**：

```ts
// ❌ 长任务
function handleClick() {
  for (let i = 0; i < 1_000_000; i++) heavyCompute()
}

// ✅ 拆分：用 scheduler.yield / setTimeout
import { scheduler } from 'https://...'

async function handleClick() {
  let i = 0
  while (i < 1_000_000) {
    heavyChunk(i)
    i++
    if (i % 100 === 0) await scheduler.yield()  // 让出主线程
  }
}
```

**避免同步重计算**：
- 输入防抖 / 节流
- `startTransition` 包裹非紧急更新
- 大量列表虚拟化

## 📐 CLS 优化

CLS = 影响分数 × 距离分数

```html
<!-- ❌ 没有尺寸，图片加载时撑开容器 -->
<img src="hero.png" />

<!-- ✅ 预设尺寸 -->
<img src="hero.png" width="1200" height="600" />
```

```css
.ad-slot {
  min-height: 250px;  /* 防止动态注入时撑动 */
}
```

策略：
- 所有 `<img>` / `<video>` / `<iframe>` 显式 `width` / `height` 属性
- 字体 `font-display: swap` + 备用度量匹配（`size-adjust`）
- 动态注入容器给最小高度
- **不使用** `document.write`

## 🛠 监测 & 上报

```ts
import { onLCP, onINP, onCLS } from 'web-vitals'

function sendToAnalytics(metric: any) {
  navigator.sendBeacon('/api/perf', JSON.stringify(metric))
}

onLCP(sendToAnalytics)
onINP(sendToAnalytics)
onCLS(sendToAnalytics)
```

## 🧰 测量工具

- **Lighthouse**：单页审计
- **PageSpeed Insights**：在线版
- **Chrome User Experience Report (CrUX)**：真实用户数据
- **Vercel Analytics**：自动接 web-vitals
- **Sentry Performance**：含 RUM

## 🎯 阈值

```
LCP  good ≤ 2.5s    poor > 4.0s
INP  good ≤ 200ms   poor > 500ms
CLS  good ≤ 0.1     poor > 0.25
```

CI 中接入 Lighthouse CI：

```yaml
- name: Lighthouse
  uses: treosh/lighthouse-ci-action@v10
  with:
    urls: |
      https://example.com/
      https://example.com/blog
    budgetPath: ./lighthouse-budget.json
```

## 🔗 下一步

- [加载性能](/12-perf/loading)
- [运行时性能](/12-perf/runtime)
- [可访问性](/12-perf/a11y)
