<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置</button>
      <span class="kg-toolbar__legend">
        <span class="kg-legend-dot" style="background: #00758F"></span>基础层
        <span class="kg-legend-dot" style="background: #16a34a"></span>索引
        <span class="kg-legend-dot" style="background: #f59e0b"></span>SQL
        <span class="kg-legend-dot" style="background: #ec4899"></span>事务锁
        <span class="kg-legend-dot" style="background: #6366f1"></span>性能
        <span class="kg-legend-dot" style="background: #06b6d4"></span>复制
        <span class="kg-legend-dot" style="background: #ef4444"></span>高可用
        <span class="kg-legend-dot" style="background: #8b5cf6"></span>监控
        <span class="kg-legend-dot" style="background: #10b981"></span>工具
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useData } from 'vitepress'
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
const { site } = useData()
let chart = null
const graphData = ref(defaultGraphData)

const categoryColors = {
  foundation: '#00758F',
  index: '#16a34a',
  sql: '#f59e0b',
  transaction: '#ec4899',
  optimization: '#6366f1',
  replication: '#06b6d4',
  ha: '#ef4444',
  backup: '#854d0e',
  monitoring: '#8b5cf6',
  sharding: '#312e81',
  tool: '#10b981'
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  const nodes = graphData.value.nodes.map(n => ({
    ...n,
    itemStyle: {
      color: categoryColors[n.category] || '#00758F'
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
        lineStyle: { width: 3, color: '#00758F' }
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
.kg-container {
  position: relative;
}
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
  background: var(--vp-c-brand-1);
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