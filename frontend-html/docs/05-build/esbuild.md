---
title: esbuild / Turbopack
date: 2026-08-15  # date-auto-injected
---

# esbuild / Turbopack / SWC

## ⚡ esbuild

**用 Go 写的极快 bundler / transpiler**。Vite 的预构建 + minify 都靠它。

```bash
esbuild app.jsx --bundle --minify --target=es2020 --outfile=out.js
```

性能对比（同等任务）：
- Webpack：~40s
- esbuild：~0.4s（**100x**）

esbuild 适合：
- 库打包（`tsup`、`unbuild`）
- Vite 的依赖预构建
- monorepo 单文件构建

不适合（暂时）：
- 复杂 chunk 拆分（项目级）
- HMR（dev 主要靠 dev server）

## 🦀 Turbopack

**Vercel / Next.js 团队出品的 Rust bundler**，定位是 Webpack 替代品（Next.js 13+ 默认 dev 启用）。

```
Turbopack vs Vite：
  Turbopack：内存型，类 Webpack 心智，incremental computation
  Vite：基于浏览器 ESM + esbuild/Rollup
```

## 🦀 SWC

**Rust 实现的 Babel 替代品**（transpiler，不是 bundler）。

优势：
- TypeScript / JSX 转译 **20x** 快于 Babel
- 被 Next.js、Rspack、Vite 插件内置

```ts
// .swcrc
{
  "jsc": {
    "parser": { "syntax": "typescript", "tsx": true },
    "target": "es2020"
  },
  "module": { "type": "es6" }
}
```

## 📦 工具一览

| 工具 | 类型 | 速度 | 用途 |
|------|------|------|------|
| esbuild | bundler + transpiler | ~100x | 库打包、prebuild |
| SWC | transpiler | ~20x | ts/jsx 编译 |
| Turbopack | bundler (类 Webpack) | 5-10x | Next.js dev/build |
| Rspack | bundler (类 Webpack) | 5-10x | Webpack 兼容场景 |
| Rolldown | bundler (类 Rollup) | TBD | Vite 6+ 可能采用 |
| Lightning CSS | CSS bundler | 100x | CSS 解析 / 压缩 |

## 🧩 库的现代构建：tsup

```bash
tsup src/index.ts --format esm,cjs --dts --clean
```

一键生成 ESM + CJS + d.ts，常用于发布 npm 库。

## 🔗 下一步

- [Vite 原理](/05-build/vite)
- [Webpack / Rspack](/05-build/webpack)
- [Monorepo](/05-build/monorepo)
