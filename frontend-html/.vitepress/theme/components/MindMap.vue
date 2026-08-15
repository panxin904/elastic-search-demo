<template>
  <div class="mindmap-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="mm-toolbar">
      <button class="mm-toolbar__btn" @click="expandAll">📖 全部展开</button>
      <button class="mm-toolbar__btn" @click="collapseAll">📕 全部收起</button>
      <button class="mm-toolbar__btn" @click="resetView">🎯 重置视图</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { TreeChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([TreeChart, TooltipComponent, CanvasRenderer])

const props = defineProps({
  height: { type: Number, default: 920 }
})

const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: '前端 + Node 全栈',
  symbolSize: 30,
  itemStyle: { color: '#1f2937' },
  children: [
    {
      name: '🌐 基础层',
      itemStyle: { color: '#d97706' },
      children: [
        { name: 'HTML 语义化', link: '/01-foundation/html' },
        { name: 'CSS 基础与盒模型', link: '/01-foundation/css' },
        { name: '浏览器渲染原理', link: '/01-foundation/browser' },
        { name: 'DOM / Event Loop', link: '/01-foundation/event-loop' },
        { name: 'Web 协议与安全', link: '/01-foundation/protocol' }
      ]
    },
    {
      name: '📜 语言层',
      itemStyle: { color: '#2563eb' },
      children: [
        { name: 'JavaScript 核心', link: '/02-language/javascript' },
        { name: 'TypeScript 类型系统', link: '/02-language/typescript' },
        { name: 'ES2024 新特性', link: '/02-language/esnext' },
        { name: 'WebAssembly 入门', link: '/02-language/wasm' }
      ]
    },
    {
      name: '⚛️ UI 框架',
      itemStyle: { color: '#06b6d4' },
      children: [
        { name: '框架总览与选型', link: '/03-framework/overview' },
        { name: 'React 核心与 Hooks', link: '/03-framework/react' },
        { name: 'Vue 3 组合式 API', link: '/03-framework/vue' },
        { name: 'Angular 体系', link: '/03-framework/angular' },
        { name: 'Svelte / Solid', link: '/03-framework/svelte' }
      ]
    },
    {
      name: '🚀 元框架',
      itemStyle: { color: '#8b5cf6' },
      children: [
        { name: 'Next.js (React)', link: '/04-meta/nextjs' },
        { name: 'Nuxt (Vue)', link: '/04-meta/nuxt' },
        { name: 'Remix / React Router 7', link: '/04-meta/remix' },
        { name: 'SvelteKit', link: '/04-meta/sveltekit' },
        { name: 'Astro / Qwik', link: '/04-meta/astro' }
      ]
    },
    {
      name: '🛠️ 构建工具',
      itemStyle: { color: '#ea580c' },
      children: [
        { name: 'Vite 原理', link: '/05-build/vite' },
        { name: 'Webpack / Rspack', link: '/05-build/webpack' },
        { name: 'Turbopack / esbuild', link: '/05-build/esbuild' },
        { name: '包管理器 (pnpm/yarn)', link: '/05-build/package-manager' },
        { name: 'Monorepo (Turbo/Nx)', link: '/05-build/monorepo' }
      ]
    },
    {
      name: '🎨 样式方案',
      itemStyle: { color: '#ec4899' },
      children: [
        { name: 'CSS 预处理器', link: '/06-style/preprocessor' },
        { name: 'Tailwind / UnoCSS', link: '/06-style/tailwind' },
        { name: 'CSS-in-JS', link: '/06-style/css-in-js' },
        { name: 'CSS Modules', link: '/06-style/css-modules' },
        { name: '设计系统 / 组件库', link: '/06-style/design-system' }
      ]
    },
    {
      name: '🗃️ 状态管理',
      itemStyle: { color: '#0891b2' },
      children: [
        { name: 'Redux Toolkit', link: '/07-state/redux' },
        { name: 'Zustand / Jotai', link: '/07-state/zustand' },
        { name: 'Pinia (Vue)', link: '/07-state/pinia' },
        { name: 'React Query / SWR', link: '/07-state/data-fetching' }
      ]
    },
    {
      name: '🛣️ 路由',
      itemStyle: { color: '#4f46e5' },
      children: [
        { name: 'React Router v6/v7', link: '/08-routing/react-router' },
        { name: 'Vue Router 4', link: '/08-routing/vue-router' },
        { name: 'TanStack Router', link: '/08-routing/tanstack-router' },
        { name: 'File-system Routing', link: '/08-routing/file-routing' }
      ]
    },
    {
      name: '📡 数据层',
      itemStyle: { color: '#10b981' },
      children: [
        { name: 'GraphQL / Apollo', link: '/09-data/graphql' },
        { name: 'tRPC', link: '/09-data/trpc' },
        { name: 'REST 规范 / OpenAPI', link: '/09-data/rest' },
        { name: 'WebSocket / SSE', link: '/09-data/realtime' }
      ]
    },
    {
      name: '🧪 测试',
      itemStyle: { color: '#eab308' },
      children: [
        { name: 'Jest / Vitest 单元测试', link: '/10-testing/unit' },
        { name: 'React Testing Library', link: '/10-testing/rtl' },
        { name: 'Cypress / Playwright', link: '/10-testing/e2e' },
        { name: 'Storybook 组件测试', link: '/10-testing/storybook' }
      ]
    },
    {
      name: '🟢 Node 后端',
      itemStyle: { color: '#16a34a' },
      children: [
        { name: 'Node 运行时与事件循环', link: '/11-node/runtime' },
        { name: 'Express / Koa', link: '/11-node/express' },
        { name: 'NestJS 体系化框架', link: '/11-node/nestjs' },
        { name: 'Fastify / Hono', link: '/11-node/fastify' },
        { name: 'Serverless / Edge', link: '/11-node/serverless' }
      ]
    },
    {
      name: '⚡ 性能优化',
      itemStyle: { color: '#be123c' },
      children: [
        { name: 'Core Web Vitals', link: '/12-perf/cwv' },
        { name: '加载性能 (CDN/SSR)', link: '/12-perf/loading' },
        { name: '运行时性能', link: '/12-perf/runtime' },
        { name: '可访问性 (a11y)', link: '/12-perf/a11y' }
      ]
    },
    {
      name: '🎯 面试',
      itemStyle: { color: '#7c3aed' },
      children: [
        { name: '高频面试题', link: '/13-interview/basic' },
        { name: '手写代码题', link: '/13-interview/coding' },
        { name: '系统设计题', link: '/13-interview/system' }
      ]
    },
    {
      name: '🧰 工程化',
      itemStyle: { color: '#475569' },
      children: [
        { name: '代码规范 (ESLint/Prettier)', link: '/14-tools/lint' },
        { name: 'Git Hooks 与 CI/CD', link: '/14-tools/cicd' },
        { name: '前端监控 / Sentry', link: '/14-tools/monitor' },
        { name: '微前端 (qiankun/Module-Federation)', link: '/14-tools/micro-frontend' }
      ]
    }
  ]
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  chart.setOption({
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      formatter: (p) => {
        if (p.data?.link) return `<b>${p.name}</b><br/>点击跳转`
        return p.name
      }
    },
    series: [{
      type: 'tree',
      data: [mindMapData],
      top: '5%',
      left: '8%',
      bottom: '5%',
      right: '20%',
      symbolSize: 14,
      orient: 'LR',
      expandAndCollapse: true,
      initialTreeDepth: 2,
      label: {
        position: 'left',
        verticalAlign: 'middle',
        align: 'right',
        fontSize: 13,
        color: 'var(--vp-c-text-1, #333)'
      },
      leaves: {
        label: {
          position: 'right',
          verticalAlign: 'middle',
          align: 'left'
        }
      },
      emphasis: { focus: 'descendant' },
      animationDuration: 550,
      animationDurationUpdate: 750,
      lineStyle: { color: '#aaa', width: 1, curveness: 0.05 }
    }]
  })
  chart.on('click', (params) => {
    if (params.data?.link) {
      window.location.href = params.data.link
    }
  })
}

function expandAll() {
  if (!chart) return
  const traverse = (node, depth) => {
    if (depth > 0 && node.children) {
      chart.dispatchAction({ type: 'treeExpandAndCollapse', data: node, seriesIndex: 0 })
    }
    if (node.children) node.children.forEach(c => traverse(c, depth + 1))
  }
  traverse(mindMapData, 0)
}

function collapseAll() {
  if (!chart) return
  const traverse = (node) => {
    if (node.children) {
      node.children.forEach(c => {
        chart.dispatchAction({ type: 'treeExpandAndCollapse', data: c, seriesIndex: 0 })
        traverse(c)
      })
    }
  }
  traverse(mindMapData)
}

function resetView() {
  if (!chart) return
  chart.dispatchAction({ type: 'restore' })
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', () => chart?.resize())
})

onBeforeUnmount(() => {
  chart?.dispose()
  chart = null
})
</script>
