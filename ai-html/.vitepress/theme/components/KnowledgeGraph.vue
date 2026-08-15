<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #8b5cf6"></span>模型</span>
        <span><span class="kg-legend-dot" style="background: #06b6d4"></span>Coding工具</span>
        <span><span class="kg-legend-dot" style="background: #f59e0b"></span>SDK</span>
        <span><span class="kg-legend-dot" style="background: #10b981"></span>Agent框架</span>
        <span><span class="kg-legend-dot" style="background: #ec4899"></span>RAG</span>
        <span><span class="kg-legend-dot" style="background: #ef4444"></span>MCP</span>
        <span><span class="kg-legend-dot" style="background: #6366f1"></span>Prompt</span>
        <span><span class="kg-legend-dot" style="background: #d946ef"></span>微调</span>
        <span><span class="kg-legend-dot" style="background: #14b8a6"></span>评测</span>
        <span><span class="kg-legend-dot" style="background: #f97316"></span>部署</span>
        <span><span class="kg-legend-dot" style="background: #84cc16"></span>工具调用</span>
        <span><span class="kg-legend-dot" style="background: #0ea5e9"></span>安装</span>
        <span><span class="kg-legend-dot" style="background: #78716c"></span>安全</span>
        <span><span class="kg-legend-dot" style="background: #a855f7"></span>面试</span>
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

const props = defineProps({ height: { type: Number, default: 820 } })
const chartRef = ref(null)
let chart = null
const graphData = ref(defaultGraphData)

const categoryColors = {
  models: '#8b5cf6', coding: '#06b6d4', sdks: '#f59e0b', agents: '#10b981',
  rag: '#ec4899', mcp: '#ef4444', prompt: '#6366f1', finetuning: '#d946ef',
  eval: '#14b8a6', deploy: '#f97316', tools: '#84cc16', install: '#0ea5e9',
  security: '#78716c', interview: '#a855f7'
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
  const links = graphData.value.links.map(l => ({ ...l, lineStyle: { color: '#aaa', width: 1, curveness: 0.05 } }))
  chart.setOption({
    tooltip: { formatter: (p) => p.dataType === 'node' ? `<b>${p.name}</b>` : `${p.source} → ${p.target}` },
    series: [{
      type: 'graph', layout: 'force', roam: true, draggable: true, animation: true,
      data: nodes, links: links,
      force: { repulsion: 280, edgeLength: 110, gravity: 0.05 },
      emphasis: { focus: 'adjacency', lineStyle: { width: 3, color: '#8b5cf6' } }
    }]
  })
  chart.on('click', (params) => {
    if (params.dataType === 'node' && params.data.link) window.location.href = params.data.link
  })
}
function resetLayout() { if (chart) chart.dispatchAction({ type: 'restore' }) }
onMounted(() => { renderChart(); window.addEventListener('resize', () => chart?.resize()) })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>