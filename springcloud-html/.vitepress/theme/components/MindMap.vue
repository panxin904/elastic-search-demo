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
  height: { type: Number, default: 720 }
})

const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: 'Spring Cloud',
  symbolSize: 24,
  itemStyle: { color: '#6DB33F' },
  children: [
    {
      name: '🍃 Spring Boot',
      itemStyle: { color: '#1e40af' },
      children: [
        { name: '快速开始', link: '/01-springboot/quickstart' },
        { name: '自动配置', link: '/01-springboot/auto-config' },
        { name: 'Web 开发', link: '/01-springboot/web' },
        { name: '数据访问', link: '/01-springboot/data' },
        { name: '事务管理', link: '/01-springboot/transaction' }
      ]
    },
    {
      name: '☁️ Spring Cloud Alibaba',
      itemStyle: { color: '#166534' },
      children: [
        { name: '总览', link: '/02-overview/intro' },
        { name: 'Nacos 服务发现', link: '/02-overview/nacos-discovery' },
        { name: 'Nacos 配置中心', link: '/02-overview/nacos-config' }
      ]
    },
    {
      name: '🚪 Gateway 网关',
      itemStyle: { color: '#9d174d' },
      children: [
        { name: 'Gateway 基础', link: '/03-gateway/basic' },
        { name: '路由与断言', link: '/03-gateway/route' },
        { name: '过滤器', link: '/03-gateway/filter' }
      ]
    },
    {
      name: '⚖️ 负载均衡',
      itemStyle: { color: '#3730a3' },
      children: [
        { name: 'LoadBalancer', link: '/04-loadbalancer/basic' },
        { name: '负载均衡策略', link: '/04-loadbalancer/strategy' }
      ]
    },
    {
      name: '🔐 认证授权',
      itemStyle: { color: '#9f1239' },
      children: [
        { name: 'Spring Security', link: '/05-security/basic' },
        { name: 'OAuth2 + JWT', link: '/05-security/oauth2' },
        { name: '统一认证中心', link: '/05-security/auth-center' }
      ]
    },
    {
      name: '🛠️ 实战与面试',
      itemStyle: { color: '#854d0e' },
      children: [
        { name: '综合实战项目', link: '/06-practice/comprehensive' },
        { name: '常见坑与最佳实践', link: '/06-practice/pitfalls' },
        { name: '高频面试题', link: '/06-practice/interview' }
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
      left: '12%',
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
      expandAndCollapse: true,
      animationDuration: 550,
      animationDurationUpdate: 750,
      lineStyle: { color: '#aaa', width: 1, curveness: 0.1 }
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

<style scoped>
.mindmap-container { position: relative; }
.mm-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background: var(--vp-c-bg-soft);
  border-top: 1px solid var(--vp-c-divider);
}
.mm-toolbar__btn {
  padding: 4px 12px;
  background: var(--sc-green, #6DB33F);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.mm-toolbar__btn:hover { opacity: 0.85; }
</style>