---
title: Vite 原理
---

# Vite 原理

## 🎯 Vite 是什么

Vite 是基于**浏览器原生 ESM + esbuild + Rollup** 的下一代前端构建工具。由 Vue 作者尤雨溪团队开发。

```
卖点：
  ⚡ 启动毫秒级（不需要打包）
  ⚡ HMR 几十毫秒（基于 ESM）
  ⚡ 生产构建用 Rollup，产物体积小
```

## ⚙️ 工作原理

### Dev 阶段（核心）

```
浏览器请求 main.js
    │
    ▼
Vite 中间件拦截 .js 请求
    │
    ▼
把 import 'vue' 重写为 /node_modules/.vite/deps/vue.js?v=xxx
    │
    ▼
浏览器收到 ESM，模块级按需请求（HMR 立即生效）
```

- **预构建依赖**：用 esbuild 把 CommonJS 依赖（如 `react`、`lodash`）转换为 ESM，缓存到 `.vite/deps/`
- **源码 on-demand**：每个文件就是个 ESM 模块，浏览器直接 import
- **HMR**：基于 ESM 模块边界，只接受修改的模块 + Propagation API

### Prod 阶段

```
源码 → Rollup 打包 → 代码分割 + 压缩 → 输出 dist/
```

未来 Vite 6 可能切到 Rolldown（Rust 版 Rollup）。

## 🚀 快速上手

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8080', changeOrigin: true }
    }
  },
  build: {
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks: { react: ['react', 'react-dom'] }
      }
    }
  }
})
```

## 🔌 常用插件

| 插件 | 作用 |
|------|------|
| `@vitejs/plugin-react` | React Fast Refresh |
| `@vitejs/plugin-vue` | Vue SFC |
| `vite-plugin-svgr` | SVG 当组件 |
| `unplugin-auto-import` | 自动 import |
| `vite-plugin-pwa` | Service Worker |

## 📦 静态资源处理

```ts
import imgUrl from './foo.png'           // 返回 URL
import svgUrl from './icon.svg?url'        // 字符串 URL
import shader from './shader.glsl?raw'     // 字符串源码

new URL('./foo.png', import.meta.url)     // 推荐写法
```

```css
.bg { background: url('./bg.png') }       /* 直接用 */
```

## ⚡ 性能优化

- **按需加载**：`import()` 动态导入，Vite 自动 code-split
- **依赖预构建**：第一次启动慢一点，之后秒级
- **开发代理**：用 `server.proxy`，绕开 CORS

## ⚠️ 常见坑

1. **CommonJS 插件不能用**：用 vite-plugin-commonjs 包一层
2. **`process.env` 替换**：在源码中只用 `import.meta.env`
3. **大依赖卡顿**：如 monaco-editor，需要 `optimizeDeps.exclude`
4. **多页面应用**：在 `rollupOptions.input` 配置多入口

## 🔗 下一步

- [Webpack / Rspack](/05-build/webpack)
- [包管理器](/05-build/package-manager)
- [Monorepo](/05-build/monorepo)
