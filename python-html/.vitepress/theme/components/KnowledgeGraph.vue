<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #1e40af"></span>入门</span>
        <span><span class="kg-legend-dot" style="background: #92400e"></span>底层</span>
        <span><span class="kg-legend-dot" style="background: #166534"></span>常用库</span>
        <span><span class="kg-legend-dot" style="background: #9d174d"></span>并发</span>
        <span><span class="kg-legend-dot" style="background: #155e75"></span>爬虫</span>
        <span><span class="kg-legend-dot" style="background: #5b21b6"></span>AI/ML</span>
        <span><span class="kg-legend-dot" style="background: #9a3412"></span>数据</span>
        <span><span class="kg-legend-dot" style="background: #854d0e"></span>算法</span>
        <span><span class="kg-legend-dot" style="background: #991b1b"></span>企业</span>
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
  height: { type: Number, default: 760 }
})

const chartRef = ref(null)
let chart = null
const graphData = ref(defaultGraphData)

const categoryColors = {
  basics: '#1e40af',
  principles: '#92400e',
  libraries: '#166534',
  concurrency: '#9d174d',
  scraping: '#155e75',
  'ai-ml': '#5b21b6',
  data: '#9a3412',
  algorithms: '#854d0e',
  enterprise: '#991b1b'
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  const nodes = graphData.value.nodes.map(n => ({
    ...n,
    itemStyle: { color: categoryColors[n.category] || '#3776AB' },
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
      force: { repulsion: 250, edgeLength: 100, gravity: 0.05 },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3, color: '#FFD43B' }
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
