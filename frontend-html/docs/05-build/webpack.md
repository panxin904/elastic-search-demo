---
title: Webpack / Rspack
date: 2026-08-15  # date-auto-injected
---

# Webpack / Rspack

![Webpack Build Pipeline](/webpack-build-pipeline.svg)

## ⚙️ Webpack 是什么

老牌模块打包器（2012）。所有项目在生产构建时（曾经）都会经过 Webpack：
- 多文件合并 → bundle
- 加载器链（loader）翻译非 JS
- 插件链（plugin）优化产物体积

```
entry → loader chain → 依赖图（graph） → chunk 拆分 → 优化 → 产物
```

## 🔧 核心概念

| 概念 | 作用 |
|------|------|
| **entry** | 起点文件（如 `./src/index.tsx`） |
| **output** | 输出（如 `dist/main.[contenthash].js`） |
| **loader** | 翻译非 JS（ts-loader, css-loader, file-loader） |
| **plugin** | 扩展行为（HtmlWebpackPlugin, MiniCssExtractPlugin） |
| **chunk** | 拆分出的代码块 |
| **asset** | 静态资源（图、字体） |
| **mode** | `production` / `development` |

## 🚀 webpack.config.js

```js
const path = require('path')
const HtmlWebpackPlugin = require('html-webpack-plugin')

module.exports = {
  mode: 'production',
  entry: './src/index.tsx',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'main.[contenthash].js',
    clean: true,
    publicPath: '/'
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js']
  },
  module: {
    rules: [
      { test: /\.tsx?$/, use: 'ts-loader', exclude: /node_modules/ },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] },
      { test: /\.(png|jpg)$/, type: 'asset/resource' }
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({ template: './public/index.html' })
  ],
  optimization: {
    splitChunks: { chunks: 'all' },
    runtimeChunk: 'single'
  }
}
```

## ⚡ 性能优化

### 1. 构建加速

- **cache**：`cache: { type: 'filesystem' }`
- **thread-loader**：多进程
- **exclude / include**：减少处理范围
- **swc-loader / esbuild-loader**：替代 ts-loader（~10x 速度）
- **持久化缓存**：webpack 5 内置

### 2. 产物优化

- **代码分割**：`splitChunks`、动态 `import()`
- **Tree Shaking**（默认 production 开启）
- **压缩**：`TerserPlugin`
- **CSS 拆分**：`MiniCssExtractPlugin`
- **gzip / brotli**：`CompressionPlugin`

### 3. 分析

```bash
webpack --profile --json > stats.json
# 上传到 https://webpack.github.io/analyse/
```

或 `webpack-bundle-analyzer` 插件。

## 🆚 Rspack（字节跳动）

**Rust 实现的 Webpack 兼容打包器**，主打**超快冷启动 + 兼容 Webpack 生态**。

```js
// rspack.config.js
const { defineConfig } = require('@rspack/cli')
module.exports = defineConfig({
  entry: './src/index.tsx',
  module: {
    rules: [
      { test: /\.tsx?$/, loader: 'builtin:swc-loader' }
    ]
  }
})
```

- 启动 5-10x 快于 Webpack 5
- 100% 兼容 Webpack 5 loader / plugin API
- 内置 SWC（比 Babel 快 20x）

## 🎯 选型

| | Webpack | Rspack | Vite |
|--|---------|--------|------|
| 启动（dev） | 慢 | 较快 | 极快 |
| 构建（prod） | 慢 | 较快 | 快 |
| 生态兼容 | ✅ | ✅ 兼容 webpack | ❌ vite 插件 |
| 配置心智 | 复杂 | 复杂 → 简单 | 简洁 |
| 大型项目 | ✅ 久经考验 | ✅ 字节大规模验证 | ⚠ 起步稍晚 |

## 🔗 下一步

- [Vite 原理](/05-build/vite)
- [esbuild / Turbopack](/05-build/esbuild)
