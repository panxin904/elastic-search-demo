---
title: 速查表
date: 2026-08-29  # date-auto-injected
---

# 📋 前端速查表

> 80+ 高频前端命令/工具速查，支持分类过滤和关键词搜索（Cmd+F 即可）。

## 📦 包管理

| 场景 | 命令 |
|------|------|
| 初始化项目 | `npm init` / `pnpm init` / `yarn init` |
| 安装依赖 | `npm install <pkg>` / `pnpm add <pkg>` |
| 全局安装 | `npm install -g <pkg>` |
| 卸载依赖 | `npm uninstall <pkg>` |
| 运行脚本 | `npm run dev` / `pnpm dev` |
| 锁定依赖 | `npm ci`（仅按 lock 文件安装） |
| 查看过期依赖 | `npm outdated` |
| 更新到最新 | `npm update <pkg>` |
| pnpm 节省磁盘 | `pnpm store prune` |

## 🚀 构建工具

| 场景 | 命令 |
|------|------|
| Vite 启动 | `npm run dev`（默认 5173 端口） |
| Vite 构建 | `npm run build`（输出到 `dist/`） |
| Vite 预览 | `npm run preview` |
| Webpack 构建 | `npx webpack --mode production` |
| Webpack 分析 | `webpack-bundle-analyzer` |
| Turborepo 构建 | `turbo run build` |
| Nx 工作区 | `nx run <app>:build` |
| esbuild 编译 | `esbuild src/index.ts --bundle --outfile=dist/bundle.js` |

## ⚛️ 框架 CLI

| 框架 | 创建命令 |
|------|----------|
| React (Vite) | `npm create vite@latest my-app -- --template react-ts` |
| Vue (Vite) | `npm create vue@latest` |
| Svelte (Vite) | `npm create vite@latest my-app -- --template svelte-ts` |
| Next.js | `npx create-next-app@latest my-app` |
| Nuxt | `npx nuxi@latest init my-app` |
| SvelteKit | `npx sv create my-app` |
| Astro | `npm create astro@latest` |
| Remix | `npx create-remix@latest` |
| Angular | `npx -p @angular/cli ng new my-app` |
| React Native | `npx react-native init MyApp` |

## 🎨 样式方案

| 方案 | 核心 API |
|------|----------|
| Tailwind | `<div class="flex gap-4 p-2">` |
| CSS Modules | `import styles from './x.module.css'` |
| styled-components | `const Btn = styled.button\`color: red\`` |
| Emotion | `const S = css\`color: red\`` |
| Sass/Less | `@use './vars'; color: $primary;` |
| CSS-in-JS (Vue) | `<style scoped>` |
| UnoCSS | 同 Tailwind 语法 |

## 🗄️ 状态管理

| 库 | 核心 API |
|----|----------|
| Zustand | `const useStore = create((set) => ({...}))` |
| Redux Toolkit | `createSlice({name, reducers})` |
| Pinia (Vue) | `defineStore('id', () => ({...}))` |
| Jotai | `const xAtom = atom(0)` |
| Recoil | `const xAtom = atom({key, default})` |
| MobX | `makeAutoObservable(this)` |
| Context API | `<Context.Provider value={...}>` |

## 🌐 路由

| 库 | 路由配置 |
|----|----------|
| React Router v6 | `<Route path="/" element={<Home/>}>` |
| Vue Router 4 | `createRouter({routes})` |
| Next.js | 文件系统路由 (`pages/` 或 `app/`) |
| Nuxt | 文件系统路由 (`pages/`) |
| TanStack Router | `createRouter({routeTree})` |
| 文件路由 (Vite) | `vite-plugin-pages` |

## 🔄 数据获取

| 方案 | 核心 API |
|------|----------|
| Fetch API | `fetch(url).then(r => r.json())` |
| Axios | `axios.get(url).then(r => r.data)` |
| SWR | `const {data} = useSWR(key, fetcher)` |
| React Query | `const {data} = useQuery({queryKey, queryFn})` |
| tRPC | `trpc.user.list.useQuery()` |
| GraphQL | `useQuery(QUERY, {variables})` |
| WebSocket | `new WebSocket('wss://...')` |

## 🧪 测试

| 工具 | 命令/用法 |
|------|----------|
| Vitest | `npx vitest` |
| Jest | `npx jest` |
| RTL | `render(<X />)` |
| Playwright | `npx playwright test` |
| Cypress | `npx cypress open` |
| Storybook | `npx storybook dev -p 6006` |
| Coverage | `vitest --coverage` |

## 🛠️ 调试工具

| 工具 | 用途 |
|------|------|
| Chrome DevTools | F12 打开 |
| React DevTools | 浏览器扩展 |
| Vue DevTools | 浏览器扩展 |
| Lighthouse | `npx lighthouse <url>` |
| Bundle 分析 | `npx source-map-explorer dist/*.js` |
| 性能追踪 | `performance.mark('start')` |
| 内存泄漏 | Chrome DevTools → Memory tab |

## 📝 代码规范

| 工具 | 命令 |
|------|------|
| ESLint 检查 | `npx eslint .` |
| ESLint 修复 | `npx eslint . --fix` |
| Prettier 格式化 | `npx prettier --write .` |
| TypeScript 检查 | `npx tsc --noEmit` |
| Husky hooks | `.husky/pre-commit` |
| lint-staged | 自动暂存文件 lint |

## 🚀 部署

| 平台 | 命令 |
|------|------|
| Vercel | `vercel --prod` |
| Netlify | `netlify deploy --prod` |
| Cloudflare Pages | `wrangler pages deploy dist/` |
| GitHub Pages | `npm run deploy`（gh-pages） |
| Docker | `docker build -t myapp . && docker run -p 80:80` |
| Nginx | `nginx -s reload` |


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
