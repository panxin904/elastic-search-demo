<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #0ea5e9"></span>Docker</span>
        <span><span class="kg-legend-dot" style="background: #326ce5"></span>k8s 架构</span>
        <span><span class="kg-legend-dot" style="background: #9333ea"></span>工作负载</span>
        <span><span class="kg-legend-dot" style="background: #ea580c"></span>Service</span>
        <span><span class="kg-legend-dot" style="background: #16a34a"></span>存储</span>
        <span><span class="kg-legend-dot" style="background: #0f766e"></span>Helm</span>
        <span><span class="kg-legend-dot" style="background: #f59e0b"></span>可观测</span>
        <span><span class="kg-legend-dot" style="background: #7c3aed"></span>Service Mesh</span>
        <span><span class="kg-legend-dot" style="background: #0891b2"></span>CI/CD</span>
        <span><span class="kg-legend-dot" style="background: #84cc16"></span>IaC</span>
        <span><span class="kg-legend-dot" style="background: #ef4444"></span>安全</span>
        <span><span class="kg-legend-dot" style="background: #6366f1"></span>Serverless</span>
        <span><span class="kg-legend-dot" style="background: #f97316"></span>排错</span>
        <span><span class="kg-legend-dot" style="background: #14b8a6"></span>面试</span>
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
  height: { type: Number, default: 820 }
})

const chartRef = ref(null)
let chart = null
const graphData = ref(defaultGraphData)

const categoryColors = {
  docker: '#0ea5e9',
  k8sarch: '#326ce5',
  workload: '#9333ea',
  service: '#ea580c',
  storage: '#16a34a',
  helm: '#0f766e',
  observability: '#f59e0b',
  mesh: '#7c3aed',
  cicd: '#0891b2',
  iac: '#84cc16',
  security: '#ef4444',
  serverless: '#6366f1',
  trouble: '#f97316',
  interview: '#14b8a6'
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  const nodes = graphData.value.nodes.map(n => ({
    ...n,
    itemStyle: { color: categoryColors[n.category] || '#1f2937' },
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