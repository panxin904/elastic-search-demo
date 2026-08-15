---
title: 学习路径
---

# 📖 前端 + Node 学习路径

> 根据你的角色选择对应路径，每条路径推荐了核心阅读顺序。

## 🛤️ 路径 1：纯前端入门（1-2 周）

适合**刚接触前端**的开发者，或转岗的全栈工程师。

1. [🌐 HTML 语义化](/01-foundation/html) — 标签语义与 a11y
2. [🎨 CSS 基础](/01-foundation/css) — 盒模型 / 布局 / 变量
3. [🌐 浏览器渲染原理](/01-foundation/browser) — DOM / CSSOM / Reflow
4. [⚡ Event Loop](/01-foundation/event-loop) — 微任务 / 宏任务
5. [📜 JavaScript 核心](/02-language/javascript) — 闭包 / this / 原型 / Promise
6. [📦 TypeScript 类型系统](/02-language/typescript) — 必备

**目标**：理解浏览器原理、写出可维护的 JS/TS 代码。

## 🛤️ 路径 2：React 工程师（3-4 周）

适合**想做 React 工程师**的开发者。

- 完成"入门"路径
- [⚛️ 框架总览与选型](/03-framework/overview)
- [⚛️ React 核心与 Hooks](/03-framework/react)
- [🛠️ Vite](/05-build/vite)
- [🎨 Tailwind](/06-style/tailwind)
- [🗃️ Zustand](/07-state/zustand)
- [🛣️ React Router v6/v7](/08-routing/react-router)
- [📡 REST 规范 / OpenAPI](/09-data/rest)
- [🧪 Jest / Vitest 单元测试](/10-testing/unit)
- [🧪 React Testing Library](/10-testing/rtl)
- [🚀 Next.js](/04-meta/nextjs)

**目标**：能独立用 React + Vite + Tailwind + Zustand 完成项目。

## 🛤️ 路径 3：Vue 工程师（3-4 周）

适合**想做 Vue 工程师**的开发者。

- 完成"入门"路径
- [⚛️ 框架总览与选型](/03-framework/overview)
- [🟢 Vue 3 组合式 API](/03-framework/vue)
- [🛠️ Vite](/05-build/vite)
- [🎨 Tailwind](/06-style/tailwind)
- [🗃️ Pinia](/07-state/pinia)
- [🛣️ Vue Router 4](/08-routing/vue-router)
- [🚀 Nuxt](/04-meta/nuxt)

**目标**：能独立用 Vue 3 + Vite + Pinia + Vue Router 完成项目。

## 🛤️ 路径 4：全栈工程师（6-8 周）

适合**做 Node 全栈**或**独立 SaaS**的开发者。

- 完成"前端工程师"路径任意一条
- [🟢 Node 运行时与事件循环](/11-node/runtime)
- [🟢 Express / Koa](/11-node/express)
- [🟢 NestJS 体系化框架](/11-node/nestjs)
- [🟢 Fastify / Hono](/11-node/fastify)
- [📡 tRPC](/09-data/trpc)
- [📡 REST 规范 / OpenAPI](/09-data/rest)
- [🧪 E2E（Cypress / Playwright）](/10-testing/e2e)
- [⚡ 加载性能 (CDN/SSR)](/12-perf/loading)

**目标**：能用 Node 全栈做出完整可上线的应用。

## 🛤️ 路径 5：前端架构师（8-12 周）

适合**想成为前端架构师 / Tech Lead**的开发者。

- 完成所有前置路径
- [🚀 Next.js](/04-meta/nextjs)
- [🚀 Nuxt](/04-meta/nuxt)
- [🛠️ Webpack / Rspack](/05-build/webpack)
- [🛠️ Monorepo（Turbo/Nx）](/05-build/monorepo)
- [🎨 设计系统 / 组件库](/06-style/design-system)
- [🗃️ Redux Toolkit](/07-state/redux)
- [🛣️ TanStack Router](/08-routing/tanstack-router)
- [📡 GraphQL](/09-data/graphql)
- [📡 WebSocket / SSE](/09-data/realtime)
- [🟢 Serverless / Edge](/11-node/serverless)
- [⚡ Core Web Vitals](/12-perf/cwv)
- [⚡ 运行时性能](/12-perf/runtime)
- [🧰 Lint / Format](/14-tools/lint)
- [🧰 CI / CD](/14-tools/cicd)
- [🧰 前端监控 / Sentry](/14-tools/monitor)
- [🧰 微前端](/14-tools/micro-frontend)

**目标**：能设计大型前端工程方案，主导微前端 / Monorepo / 设计系统等基础设施。

## 🛤️ 路径 6：求职冲刺（4 周）

适合**1-3 个月内要面试**的开发者。

- 复习 [📜 JavaScript 核心](/02-language/javascript)
- 复习 [📦 TypeScript 类型系统](/02-language/typescript)
- 复习 [⚛️ React 核心与 Hooks](/03-framework/react)（或 [🟢 Vue 3](/03-framework/vue)）
- [🎯 高频面试题](/13-interview/basic)
- [🎯 手写代码题](/13-interview/coding)
- [🎯 系统设计题](/13-interview/system)

## 🎯 速查卡片

| 我想 | 推荐先看 |
|------|---------|
| 学基础 | [📜 JavaScript 核心](/02-language/javascript) → [📦 TypeScript](/02-language/typescript) |
| 做 React 项目 | [⚛️ React 核心](/03-framework/react) → [🚀 Next.js](/04-meta/nextjs) |
| 做 Vue 项目 | [🟢 Vue 3](/03-framework/vue) → [🚀 Nuxt](/04-meta/nuxt) |
| 学构建 | [🛠️ Vite](/05-build/vite) → [🛠️ Webpack / Rspack](/05-build/webpack) |
| 做样式 | [🎨 Tailwind](/06-style/tailwind) → [🎨 设计系统](/06-style/design-system) |
| 做 Node 后端 | [🟢 Node 运行时](/11-node/runtime) → [🟢 NestJS](/11-node/nestjs) |
| 优化性能 | [⚡ Core Web Vitals](/12-perf/cwv) → [⚡ 加载性能](/12-perf/loading) |
| 找工作 | [🎯 高频面试题](/13-interview/basic) → [🎯 手写代码](/13-interview/coding) |
