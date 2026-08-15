<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #2563eb"></span>基础</span>
        <span><span class="kg-legend-dot" style="background: #0891b2"></span>HDFS</span>
        <span><span class="kg-legend-dot" style="background: #d97706"></span>MapReduce</span>
        <span><span class="kg-legend-dot" style="background: #dc2626"></span>Spark</span>
        <span><span class="kg-legend-dot" style="background: #7c3aed"></span>Flink</span>
        <span><span class="kg-legend-dot" style="background: #b45309"></span>Hive</span>
        <span><span class="kg-legend-dot" style="background: #be185d"></span>Kafka Stream</span>
        <span><span class="kg-legend-dot" style="background: #a21caf"></span>建模</span>
        <span><span class="kg-legend-dot" style="background: #1e40af"></span>数仓架构</span>
        <span><span class="kg-legend-dot" style="background: #0e7490"></span>数据湖</span>
        <span><span class="kg-legend-dot" style="background: #047857"></span>ELT</span>
        <span><span class="kg-legend-dot" style="background: #c2410c"></span>OLAP</span>
        <span><span class="kg-legend-dot" style="background: #5b21b6"></span>案例</span>
        <span><span class="kg-legend-dot" style="background: #9a3412"></span>面试</span>
      </span>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'; import { GraphChart } from 'echarts/charts'; import { TitleComponent, TooltipComponent, LegendComponent } from 'echarts/components'; import { CanvasRenderer } from 'echarts/renderers'
import { graphData as defaultGraphData } from '../composables/graphData'
echarts.use([GraphChart, TitleComponent, TooltipComponent, LegendComponent, CanvasRenderer])
const props = defineProps({ height: { type: Number, default: 820 } }); const chartRef = ref(null); let chart = null
const graphData = ref(defaultGraphData)
const categoryColors = { basics:'#2563eb', hdfs:'#0891b2', mapreduce:'#d97706', spark:'#dc2626', flink:'#7c3aed', hive:'#b45309', kafka:'#be185d', modeling:'#a21caf', dwarch:'#1e40af', datalake:'#0e7490', elt:'#047857', olap:'#c2410c', cases:'#5b21b6', interview:'#9a3412' }
function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  const nodes = graphData.value.nodes.map(n => ({ ...n, itemStyle: { color: categoryColors[n.category] || '#1f2937' }, symbolSize: n.symbolSize || (n.value ? Math.min(60, 22 + n.value * 3) : 28), label: { show: true, position: 'right', fontSize: 11 } }))
  const links = graphData.value.links.map(l => ({ ...l, lineStyle: { color: '#aaa', width: 1, curveness: 0.05 } }))
  chart.setOption({ tooltip: { formatter: (p) => p.dataType === 'node' ? `<b>${p.name}</b>` : `${p.source} → ${p.target}` }, series: [{ type: 'graph', layout: 'force', roam: true, draggable: true, animation: true, data: nodes, links: links, force: { repulsion: 280, edgeLength: 110, gravity: 0.05 }, emphasis: { focus: 'adjacency', lineStyle: { width: 3, color: '#0891b2' } } }] })
  chart.on('click', (params) => { if (params.dataType === 'node' && params.data.link) window.location.href = params.data.link })
}
function resetLayout() { if (chart) chart.dispatchAction({ type: 'restore' }) }
onMounted(() => { renderChart(); window.addEventListener('resize', () => chart?.resize()) })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>
