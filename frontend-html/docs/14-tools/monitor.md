---
title: 前端监控 / Sentry
date: 2026-08-15  # date-auto-injected
---

# 前端监控 / Sentry

## 🎯 监控三大块

```
错误监控      - 崩溃、报错
性能监控      - Web Vitals / API 耗时
行为回放      - Session Replay（鼠标 / 视频）
```

## 🚨 Sentry（事实标准）

```bash
npm install @sentry/react @sentry/vue
```

```tsx
// React
import * as Sentry from '@sentry/react'

Sentry.init({
  dsn: 'https://xxx@sentry.io/123',
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration()
  ],
  tracesSampleRate: 0.2,        // 20% 性能采样
  replaysSessionSampleRate: 0.1, // 10% session 录制
  replaysOnErrorSampleRate: 1.0, // 出错时 100% 录制
  environment: import.meta.env.MODE
})

// 错误边界
<Sentry.ErrorBoundary fallback={<ErrorPage />}>
  <App />
</Sentry.ErrorBoundary>
```

### Source Map 上传

```bash
npm i -D @sentry/vite-plugin
```

```ts
// vite.config.ts
import { sentryVitePlugin } from '@sentry/vite-plugin'

export default defineConfig({
  build: { sourcemap: true },
  plugins: [sentryVitePlugin({ org: 'org', project: 'web' })]
})
```

Sentry 才能把压缩后的行号还原为源码行号。

### 上下文

```ts
Sentry.setUser({ id: '123', email: 'alice@example.com' })
Sentry.setTag('page_locale', 'zh-CN')
Sentry.setContext('order', { id: 'abc', items: 3 })

// 自定义
Sentry.captureException(new Error('oops'))
Sentry.captureMessage('user reached limit', 'warning')
```

## 🛠 自建监控（最小集）

### 错误

```js
window.addEventListener('error', (e) => report({ kind: 'js', msg: e.message, stack: e.error?.stack }))
window.addEventListener('unhandledrejection', (e) =>
  report({ kind: 'promise', msg: e.reason?.message })
)
```

### 性能

```js
// 利用 PerformanceObserver
new PerformanceObserver(list => {
  list.getEntries().forEach(entry => report({ kind: 'perf', name: entry.name, dur: entry.duration }))
}).observe({ type: 'navigation', buffered: true })
```

### 上报

```js
function report(payload) {
  navigator.sendBeacon('/api/telemetry', JSON.stringify(payload))
}
```

`sendBeacon` 在 unload 时仍能发出；用 `fetch` 在 unload 时会被丢弃。

## 🔍 常见信号

| 信号 | 含义 |
|------|------|
| **JS error rate ↑** | 某次发布有问题（搜 release） |
| **特定页面 error ↑** | 某功能退化 |
| **API P95 ↑** | 后端慢 / 网络差 |
| **CLS ↑** | 某次改动 layout 抖动 |
| **LCP 上涨** | 资源变大 |
| **Error fingerprint** | 通过栈 + 文件归类 |

## 🪛 自建前端 RUM（最小实现）

```js
// 性能
const t = { fcp: 0, lcp: 0 }
new PerformanceObserver((list) => {
  list.getEntries().forEach(e => {
    if (e.name === 'first-contentful-paint') t.fcp = e.startTime
    if (e.entryType === 'largest-contentful-paint') t.lcp = e.startTime
  })
}).observe({ type: 'paint', buffered: true })

// 接口耗时
const origFetch = window.fetch
window.fetch = async (...args) => {
  const t0 = performance.now()
  const res = await origFetch(...args)
  report({ kind: 'api', url: args[0], dur: performance.now() - t0, status: res.status })
  return res
}
```

## 📊 Sentry 仪表盘

预置：
- Issues（按 tag / release 过滤）
- Performance（按 trace / transaction）
- Releases（每次部署对比）
- Alerts（异常 → Slack / Email）

## 🛡️ Source Map 安全

不要把 source map 公开！上传到 Sentry / Bugsnag backend 即可。

## 🔗 下一步

- [CI/CD](/14-tools/cicd)
- [Core Web Vitals](/12-perf/cwv)
