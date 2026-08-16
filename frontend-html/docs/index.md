---
layout: home

hero:
  name: 前端 & Node 全栈 知识图谱
  text: 系统化学习
  tagline: 用知识图谱串联前端框架 / 构建工具 / 状态管理 / Node 后端
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 🧠 思维导图
      link: /mindmap
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "HTML / CSS 基础不扎实，遇到复杂布局就懵？",
      "React / Vue / Angular / Svelte 选哪个？",
      "浏览器渲染原理、Event Loop 讲不清？",
      "TypeScript 类型系统、泛型、条件类型卡壳？",
      "Node 后端怎么写、怎么部署、怎么调优？"
    ]
const goals = [
      "HTML / CSS / 浏览器渲染 / Event Loop 全链路打通",
      "JS 核心 + TypeScript 类型系统深入",
      "React Hooks + Vue 3 组合式 API + 选型矩阵",
      "构建工具链（Vite / Webpack / Turbopack）",
      "Node 后端（Express / Koa / NestJS / Fastify）"
    ]
const relatedSites = [
      { site: "tools", path: "/json", label: "JSON 工具" },
      { site: "network", path: "/01-fundamentals/tcp-ip", label: "TCP/IP 协议" },
      { site: "system-design", path: "/01-theory/cap-theorem", label: "CAP 定理" },
      { site: "ai", path: "/06-mcp/core", label: "MCP 协议" },
      { site: "go", path: "/04-cloud-native/overview", label: "Go 云原生" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>

features:
  - icon: 🌐
    title: 基础层
    details: HTML / CSS / 浏览器渲染 / Event Loop / Web 协议 — 前端最底层
    link: /01-foundation/html
    linkText: 开始学习 →
  - icon: 📜
    title: 语言层
    details: JavaScript 核心 / TypeScript 类型系统 / ESNext / WebAssembly
    link: /02-language/javascript
    linkText: 深入语言 →
  - icon: ⚛️
    title: UI 框架
    details: React Hooks / Vue 3 组合式 API / Angular / Svelte / Solid
    link: /03-framework/overview
    linkText: 看框架 →
  - icon: 🚀
    title: 元框架
    details: Next.js / Nuxt / Remix / SvelteKit / Astro / Qwik
    link: /04-meta/nextjs
    linkText: 看元框架 →
  - icon: 🛠️
    title: 构建工具
    details: Vite 原理 / Webpack Rspack / esbuild / Monorepo / 包管理器
    link: /05-build/vite
    linkText: 看构建 →
  - icon: 🎨
    title: 样式方案
    details: Tailwind / UnoCSS / CSS-in-JS / CSS Modules / 设计系统
    link: /06-style/tailwind
    linkText: 看样式 →
  - icon: 🗃️
    title: 状态管理
    details: Redux Toolkit / Zustand / Pinia / React Query / SWR
    link: /07-state/redux
    linkText: 看状态 →
  - icon: 🛣️
    title: 路由
    details: React Router / Vue Router / TanStack Router / File-system Routing
    link: /08-routing/react-router
    linkText: 看路由 →
  - icon: 📡
    title: 数据层
    details: GraphQL / tRPC / REST OpenAPI / WebSocket / SSE
    link: /09-data/graphql
    linkText: 看数据层 →
  - icon: 🧪
    title: 测试
    details: Jest / Vitest / RTL / Cypress / Playwright / Storybook
    link: /10-testing/unit
    linkText: 看测试 →
  - icon: 🟢
    title: Node 后端
    details: Node 运行时 / Express / NestJS / Fastify / Hono / Serverless
    link: /11-node/runtime
    linkText: 看 Node →
  - icon: ⚡
    title: 性能优化
    details: Core Web Vitals / 加载性能 / 运行时性能 / 可访问性 a11y
    link: /12-perf/cwv
    linkText: 看性能 →
  - icon: 🎯
    title: 面试
    details: 高频面试题 / 手写代码题 / 系统设计题
    link: /13-interview/basic
    linkText: 看面试 →
  - icon: 🧰
    title: 工程化
    details: Lint / CI CD / 监控 Sentry / 微前端
    link: /14-tools/lint
    linkText: 看工程化 →

---

## 🎯 为什么写这个知识图谱？

```
现代前端早已不是"切图仔"。从浏览器到 Node 后端，从 UI 到构建工具，从状态管理到部署监控，
随便一个方向挖下去都有几十个工具、框架和最佳实践。

本图谱的目标：
  ✅ 系统覆盖浏览器前端：HTML / CSS / JavaScript / TypeScript
  ✅ UI 框架：React / Vue / Angular / Svelte
  ✅ 元框架：Next.js / Nuxt / Remix / SvelteKit / Astro
  ✅ 工程化：Vite / Webpack / Tailwind / 设计系统 / 状态管理 / 路由 / 数据层
  ✅ 测试：单元测试 / RTL / Cypress / Playwright / Storybook
  ✅ Node 后端：运行时 / Express / NestJS / Fastify / Serverless
  ✅ 性能与可访问性：Core Web Vitals / SSR / 加载 / 运行时 / a11y
  ✅ 工程化与面试：监控 / CI/CD / 微前端 / 高频面试题 / 手写代码 / 系统设计
```

## 🎯 学习路径

```
🆕 入门     →  🌐 基础层 →  📜 语言层
⚛️ 核心     →  ⚛️ UI 框架 →  🚀 元框架
🛠️ 工程    →  🛠️ 构建工具 →  🎨 样式方案 →  🗃️ 状态管理 →  🛣️ 路由 →  📡 数据层
🧪 质量     →  🧪 测试
🟢 后端     →  🟢 Node 后端
⚡ 性能     →  ⚡ 性能优化
🎯 求职     →  🎯 面试 +  🧰 工程化
```

完整路径请看 [📖 学习路径](/path)。


## 💡 知识图谱 + 思维导图

- [🌐 知识图谱](/graph) — 全局节点关系图，鼠标拖拽，点击节点跳转
- [🧭 思维导图](/mindmap) — 树形结构概览，可展开/收起

## 🎁 学习建议

```
1. 初学者  →  从"基础层 / 语言层 / UI 框架"开始
2. 进阶者  →  把"构建 / 状态 / 路由 / 数据层"补齐
3. 全栈    →  加入"Node 后端"
4. 求职    →  "面试"模块 +  高频手写代码
```
