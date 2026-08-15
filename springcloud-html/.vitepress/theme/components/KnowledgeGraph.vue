<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置</button>
      <span class="kg-toolbar__legend">
        <span class="kg-legend-dot" style="background: #1e40af"></span>Spring Boot
        <span class="kg-legend-dot" style="background: #166534"></span>Nacos
        <span class="kg-legend-dot" style="background: #9d174d"></span>Gateway
        <span class="kg-legend-dot" style="background: #3730a3"></span>RPC
        <span class="kg-legend-dot" style="background: #155e75"></span>配置
        <span class="kg-legend-dot" style="background: #9f1239"></span>安全
        <span class="kg-legend-dot" style="background: #854d0e"></span>消息
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
  height: { type: Number, default: 600 }
})

const chartRef = ref(null)
let chart = null
const graphData = ref(defaultGraphData)

const categoryColors = {
  springboot: '#1e40af',
  cloud: '#166534',
  nacos: '#92400e',
  gateway: '#9d174d',
  rpc: '#3730a3',
  config: '#155e75',
  security: '#9f1239',
  msg: '#854d0e'
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  const nodes = graphData.value.nodes.map(n => ({
    ...n,
    itemStyle: {
      color: categoryColors[n.category] || '#6DB33F'
    },
    symbolSize: n.symbolSize || (n.value ? Math.min(60, 20 + n.value * 3) : 28),
    label: { show: true, position: 'right', fontSize: 11 }
  }))
  const links = graphData.value.links.map(l => ({
    ...l,
    lineStyle: { color: '#aaa', width: 1, curveness: 0.1 }
  }))
  chart.setOption({
    tooltip: {
      formatter: (p) => {
        if (p.dataType === 'node') {
          return `<b>${p.name}</b><br/>${p.value || ''}`
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
      force: { repulsion: 200, edgeLength: 80, gravity: 0.05 },
      emphasis: {
        focus: 'adjacency',
        lineStyle: { width: 3, color: '#6DB33F' }
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

<style scoped>
.kg-container { position: relative; }
.kg-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--vp-c-bg-soft);
  border-top: 1px solid var(--vp-c-divider);
  font-size: 12px;
  flex-wrap: wrap;
  gap: 8px;
}
.kg-toolbar__btn {
  padding: 4px 12px;
  background: var(--sc-green, #6DB33F);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.kg-toolbar__btn:hover { opacity: 0.85; }
.kg-toolbar__legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: var(--vp-c-text-2);
}
.kg-legend-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
}
</style>