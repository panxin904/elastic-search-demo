<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #991b1b"></span>基础</span>
        <span><span class="kg-legend-dot" style="background: #92400e"></span>数据结构</span>
        <span><span class="kg-legend-dot" style="background: #166534"></span>持久化</span>
        <span><span class="kg-legend-dot" style="background: #1e40af"></span>集群</span>
        <span><span class="kg-legend-dot" style="background: #3730a3"></span>Java SDK</span>
        <span><span class="kg-legend-dot" style="background: #9d174d"></span>企业实战</span>
        <span><span class="kg-legend-dot" style="background: #155e75"></span>运维</span>
        <span><span class="kg-legend-dot" style="background: #5b21b6"></span>面试</span>
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
  height: { type: Number, default: 720 }
})

const chartRef = ref(null)
let chart = null
const graphData = ref(defaultGraphData)

const categoryColors = {
  basics: '#991b1b',
  datastruct: '#92400e',
  persist: '#166534',
  cluster: '#1e40af',
  jdk: '#3730a3',
  practice: '#9d174d',
  ops: '#155e75',
  interview: '#5b21b6'
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  const nodes = graphData.value.nodes.map(n => ({
    ...n,
    itemStyle: {
      color: categoryColors[n.category] || '#DC382D'
    },
    symbolSize: n.symbolSize || (n.value ? Math.min(60, 20 + n.value * 3) : 28),
    label: { show: true, position: 'right', fontSize: 11 }
  }))
  const links = graphData.value.links.map(l => ({
    ...l,
    lineStyle: { color: '#aaa', width: 1, curveness: 0.05 }
  }))
  chart.setOption({
    tooltip: {
      formatter: (p) => {
        if (p.dataType === 'node') {
          return `<b>${p.name}</b>`
        }
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
      force: { repulsion: 250, edgeLength: 100, gravity: 0.05 },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3, color: '#DC382D' }
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
