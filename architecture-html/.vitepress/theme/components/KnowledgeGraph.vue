<template>
  <div class="kg-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="kg-toolbar">
      <button class="kg-toolbar__btn" @click="resetLayout">🔄 重置布局</button>
      <span class="kg-toolbar__legend">
        <span><span class="kg-legend-dot" style="background: #475569"></span>并发理论</span>
        <span><span class="kg-legend-dot" style="background: #0891b2"></span>线程池</span>
        <span><span class="kg-legend-dot" style="background: #7c3aed"></span>HA 理论</span>
        <span><span class="kg-legend-dot" style="background: #db2777"></span>限流</span>
        <span><span class="kg-legend-dot" style="background: #ea580c"></span>熔断</span>
        <span><span class="kg-legend-dot" style="background: #2563eb"></span>微服务</span>
        <span><span class="kg-legend-dot" style="background: #16a34a"></span>分布式事务</span>
        <span><span class="kg-legend-dot" style="background: #f59e0b"></span>消息队列</span>
        <span><span class="kg-legend-dot" style="background: #ec4899"></span>缓存</span>
        <span><span class="kg-legend-dot" style="background: #0ea5e9"></span>分库分表</span>
        <span><span class="kg-legend-dot" style="background: #f97316"></span>DDD</span>
        <span><span class="kg-legend-dot" style="background: #14b8a6"></span>微服务模式</span>
        <span><span class="kg-legend-dot" style="background: #9333ea"></span>可观测</span>
        <span><span class="kg-legend-dot" style="background: #dc2626"></span>企业案例</span>
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
const categoryColors = { concurrency:'#475569', threadpool:'#0891b2', ha:'#7c3aed', ratelimit:'#db2777', circuit:'#ea580c', microservice:'#2563eb', disttx:'#16a34a', mq:'#f59e0b', cache:'#ec4899', shard:'#0ea5e9', ddd:'#f97316', patterns:'#14b8a6', observability:'#9333ea', cases:'#dc2626' }
function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  const nodes = graphData.value.nodes.map(n => ({ ...n, itemStyle: { color: categoryColors[n.category] || '#1f2937' }, symbolSize: n.symbolSize || (n.value ? Math.min(60, 22 + n.value * 3) : 28), label: { show: true, position: 'right', fontSize: 11 } }))
  const links = graphData.value.links.map(l => ({ ...l, lineStyle: { color: '#aaa', width: 1, curveness: 0.05 } }))
  chart.setOption({ tooltip: { formatter: (p) => p.dataType === 'node' ? `<b>${p.name}</b>` : `${p.source} → ${p.target}` }, series: [{ type: 'graph', layout: 'force', roam: true, draggable: true, animation: true, data: nodes, links: links, force: { repulsion: 280, edgeLength: 110, gravity: 0.05 }, emphasis: { focus: 'adjacency', lineStyle: { width: 3, color: '#7c3aed' } } }] })
  chart.on('click', (params) => { if (params.dataType === 'node' && params.data.link) window.location.href = params.data.link })
}
function resetLayout() { if (chart) chart.dispatchAction({ type: 'restore' }) }
onMounted(() => { renderChart(); window.addEventListener('resize', () => chart?.resize()) })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>