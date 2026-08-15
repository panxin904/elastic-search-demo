<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #d97706"></span>基础</span>
        <span><span class="kg-legend-dot" style="background: #2563eb"></span>语言</span>
        <span><span class="kg-legend-dot" style="background: #06b6d4"></span>框架</span>
        <span><span class="kg-legend-dot" style="background: #8b5cf6"></span>元框架</span>
        <span><span class="kg-legend-dot" style="background: #ea580c"></span>构建</span>
        <span><span class="kg-legend-dot" style="background: #ec4899"></span>样式</span>
        <span><span class="kg-legend-dot" style="background: #0891b2"></span>状态</span>
        <span><span class="kg-legend-dot" style="background: #4f46e5"></span>路由</span>
        <span><span class="kg-legend-dot" style="background: #10b981"></span>数据</span>
        <span><span class="kg-legend-dot" style="background: #eab308"></span>测试</span>
        <span><span class="kg-legend-dot" style="background: #16a34a"></span>Node</span>
        <span><span class="kg-legend-dot" style="background: #be123c"></span>性能</span>
        <span><span class="kg-legend-dot" style="background: #7c3aed"></span>面试</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { GraphChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { graphData as defaultGraphData } from '../composables/graphData'

echarts.use([GraphChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const props = defineProps({
  height: { type: Number, default: 780 }
})

const chartRef = ref(null)
let chart = null
const graphData = ref(defaultGraphData)

const categoryColors = {
  foundation: '#d97706',
  language: '#2563eb',
  framework: '#06b6d4',
  meta: '#8b5cf6',
  build: '#ea580c',
  style: '#ec4899',
  state: '#0891b2',
  routing: '#4f46e5',
  data: '#10b981',
  testing: '#eab308',
  node: '#16a34a',
  perf: '#be123c',
  interview: '#7c3aed'
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  const nodes = graphData.value.nodes.map(n => ({
    ...n,
    itemStyle: { color: categoryColors[n.category] || '#231F20' },
    symbolSize: n.symbolSize || (n.value ? Math.min(60, 22 + n.value * 3) : 28),
    label: { show: true, position: 'right', fontSize: 11 }
  }))
  const links = graphData.value.links.map(l => ({
    ...l,
    lineStyle: { color: '#aaa', width: 1, curveness: 0.05 }
  }))
  chart.setOption({
    tooltip: {
      formatter: (p) => {
        if (p.dataType === 'node') return `<b>${p.name}</b>`
        return `${p.source} → ${p.target}`
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      roam: true,
      draggable: true,
      animation: true,
      data: nodes,
      links: links,
      force: { repulsion: 280, edgeLength: 110, gravity: 0.05 },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3, color: '#06b6d4' }
      }
    }]
  })
  chart.on('click', (params) => {
    if (params.dataType === 'node' && params.data.link) {
      window.location.href = params.data.link
    }
  })
}

function resetLayout() {
  if (chart) chart.dispatchAction({ type: 'restore' })
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
