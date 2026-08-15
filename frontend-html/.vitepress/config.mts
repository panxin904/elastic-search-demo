import { defineConfig } from 'vitepress'

export default defineConfig({
  base: '/frontend/',
  title: '前端 & Node 全栈 知识图谱',
  description: '系统化学习前端 & Node 全栈 - 框架 / 构建 / 状态 / Node 后端 / 性能',
  lang: 'zh-CN',
  lastUpdated: true,
  srcDir: 'docs',
  cleanUrls: true,
  head: [
    ['link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png', sizes: '180x180' }],
    ['link', { rel: 'icon', href: '/favicon.svg', type: 'image/svg+xml' }],
    ['link', { rel: 'icon', href: '/favicon.ico', type: 'image/x-icon' }],
    ['meta', { name: 'theme-color', content: '#06b6d4' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'zh_CN' }]  ],
  themeConfig: {
    siteTitle: '前端 & Node 全栈',
    nav: [

      { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' },
{ text: '首页', link: '/' },
      { text: '知识图谱', link: '/graph' },
      { text: '思维导图', link: '/mindmap' },
      { text: '学习路径', link: '/path' },
      {
        text: '更多站点',
        items: [
        { text: 'AI 工具 / 大模型', link: 'https://java-px.bot.cd/ai/' },
        { text: '企业级架构', link: 'https://java-px.bot.cd/architecture/' },
        { text: '大数据', link: 'https://java-px.bot.cd/bigdata/' },
        { text: '云原生 / Docker / K8s', link: 'https://java-px.bot.cd/cloud-native/' },
        { text: 'ElasticSearch', link: 'https://java-px.bot.cd/es/' },
        { text: 'Java 语言', link: 'https://java-px.bot.cd/java-language/' },
        { text: 'Java Web 开发', link: 'https://java-px.bot.cd/java/' },
        { text: 'Kafka', link: 'https://java-px.bot.cd/kafka/' },
        { text: 'Linux 服务器', link: 'https://java-px.bot.cd/linux/' },
        { text: 'MySQL', link: 'https://java-px.bot.cd/mysql/' },
        { text: 'Python', link: 'https://java-px.bot.cd/python/' },
        { text: 'Redis', link: 'https://java-px.bot.cd/redis/' },
        { text: '微服务 / Spring Cloud', link: 'https://java-px.bot.cd/cloud/' },
        { text: '计算机网络', link: 'https://java-px.bot.cd/network/' },
        { text: '文件系统与存储', link: 'https://java-px.bot.cd/filesystem/' },
        { text: '在线工具', link: 'https://java-px.bot.cd/tools/' },
        { text: '视频处理', link: 'https://java-px.bot.cd/video/' }
      ]
      }
    ],
    sidebar: {
      '/': [
        { text: '🎯 开始', items: [{ text: '📖 学习路径', link: '/path' }] },
        {
          text: '🌐 基础层',
          items: [
            { text: 'HTML 语义化', link: '/01-foundation/html' },
            { text: 'CSS 基础', link: '/01-foundation/css' },
            { text: '浏览器渲染原理', link: '/01-foundation/browser' },
            { text: 'Event Loop', link: '/01-foundation/event-loop' },
            { text: 'Web 协议与安全', link: '/01-foundation/protocol' }
          ]
        },
        {
          text: '📜 语言层',
          items: [
            { text: 'JavaScript 核心', link: '/02-language/javascript' },
            { text: 'TypeScript 类型系统', link: '/02-language/typescript' },
            { text: 'ESNext 新特性', link: '/02-language/esnext' },
            { text: 'WebAssembly 入门', link: '/02-language/wasm' }
          ]
        },
        {
          text: '⚛️ UI 框架',
          items: [
            { text: '框架总览与选型', link: '/03-framework/overview' },
            { text: 'React 核心与 Hooks', link: '/03-framework/react' },
            { text: 'Vue 3 组合式 API', link: '/03-framework/vue' },
            { text: 'Angular 体系', link: '/03-framework/angular' },
            { text: 'Svelte / Solid', link: '/03-framework/svelte' }
          ]
        },
        {
          text: '🚀 元框架',
          items: [
            { text: 'Next.js (React)', link: '/04-meta/nextjs' },
            { text: 'Nuxt (Vue)', link: '/04-meta/nuxt' },
            { text: 'Remix / RR v7', link: '/04-meta/remix' },
            { text: 'SvelteKit', link: '/04-meta/sveltekit' },
            { text: 'Astro / Qwik', link: '/04-meta/astro' }
          ]
        },
        {
          text: '🛠️ 构建工具',
          items: [
            { text: 'Vite 原理', link: '/05-build/vite' },
            { text: 'Webpack / Rspack', link: '/05-build/webpack' },
            { text: 'esbuild / Turbopack', link: '/05-build/esbuild' },
            { text: '包管理器 (pnpm/yarn)', link: '/05-build/package-manager' },
            { text: 'Monorepo (Turbo/Nx)', link: '/05-build/monorepo' }
          ]
        },
        {
          text: '🎨 样式方案',
          items: [
            { text: 'CSS 预处理器', link: '/06-style/preprocessor' },
            { text: 'Tailwind / UnoCSS', link: '/06-style/tailwind' },
            { text: 'CSS-in-JS', link: '/06-style/css-in-js' },
            { text: 'CSS Modules', link: '/06-style/css-modules' },
            { text: '设计系统 / 组件库', link: '/06-style/design-system' }
          ]
        },
        {
          text: '🗃️ 状态管理',
          items: [
            { text: 'Redux Toolkit', link: '/07-state/redux' },
            { text: 'Zustand / Jotai', link: '/07-state/zustand' },
            { text: 'Pinia (Vue)', link: '/07-state/pinia' },
            { text: 'React Query / SWR', link: '/07-state/data-fetching' }
          ]
        },
        {
          text: '🛣️ 路由',
          items: [
            { text: 'React Router v6/v7', link: '/08-routing/react-router' },
            { text: 'Vue Router 4', link: '/08-routing/vue-router' },
            { text: 'TanStack Router', link: '/08-routing/tanstack-router' },
            { text: 'File-system Routing', link: '/08-routing/file-routing' }
          ]
        },
        {
          text: '📡 数据层',
          items: [
            { text: 'GraphQL / Apollo', link: '/09-data/graphql' },
            { text: 'tRPC', link: '/09-data/trpc' },
            { text: 'REST 规范 / OpenAPI', link: '/09-data/rest' },
            { text: 'WebSocket / SSE', link: '/09-data/realtime' }
          ]
        },
        {
          text: '🧪 测试',
          items: [
            { text: 'Jest / Vitest 单元测试', link: '/10-testing/unit' },
            { text: 'React Testing Library', link: '/10-testing/rtl' },
            { text: 'Cypress / Playwright', link: '/10-testing/e2e' },
            { text: 'Storybook 组件测试', link: '/10-testing/storybook' }
          ]
        },
        {
          text: '🟢 Node 后端',
          items: [
            { text: 'Node 运行时与事件循环', link: '/11-node/runtime' },
            { text: 'Express / Koa', link: '/11-node/express' },
            { text: 'NestJS 体系化框架', link: '/11-node/nestjs' },
            { text: 'Fastify / Hono', link: '/11-node/fastify' },
            { text: 'Serverless / Edge', link: '/11-node/serverless' }
          ]
        },
        {
          text: '⚡ 性能优化',
          items: [
            { text: 'Core Web Vitals', link: '/12-perf/cwv' },
            { text: '加载性能 (CDN/SSR)', link: '/12-perf/loading' },
            { text: '运行时性能', link: '/12-perf/runtime' },
            { text: '可访问性 (a11y)', link: '/12-perf/a11y' }
          ]
        },
        {
          text: '🎯 面试',
          items: [
            { text: '高频面试题', link: '/13-interview/basic' },
            { text: '手写代码题', link: '/13-interview/coding' },
            { text: '系统设计题', link: '/13-interview/system' }
          ]
        },
        {
          text: '🧰 工程化',
          items: [
            { text: 'Lint / Format', link: '/14-tools/lint' },
            { text: 'CI / CD', link: '/14-tools/cicd' },
            { text: '前端监控 / Sentry', link: '/14-tools/monitor' },
            { text: '微前端', link: '/14-tools/micro-frontend' }
          ]
        }
      ],
      '/graph': [{ text: '🌐 知识图谱', items: [{ text: '全局知识图谱', link: '/graph' }] }],
      '/mindmap': [{ text: '🧭 思维导图', items: [{ text: '全栈思维导图', link: '/mindmap' }] }],
      '/path': [{ text: '🎯 学习路径', items: [{ text: '前端 + Node 学习路径', link: '/path' }] }]
    },
    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ],
    footer: {
      message: '前端 & Node 全栈 - 系统化学习现代 Web · 🏠 <a href="https://java-px.bot.cd/" target="_blank">门户首页</a>',
      copyright: 'MIT License'
    },
    outline: {
      level: [2, 3],
      label: '页面大纲'
    },
    docFooter: { prev: '上一篇', next: '下一篇' },

    search: { provider: 'local' },
  }
})
