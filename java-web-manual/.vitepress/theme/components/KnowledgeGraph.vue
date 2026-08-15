<template>
  <div class="kg-wrapper">
    <div ref="chartRef" class="kg-container" :style="{ height: `${height}px` }" />
    <div v-if="mode === 'full' && data?.categories" class="kg-legend">
      <span
        v-for="cat in data.categories"
        :key="cat.id"
        class="kg-legend-item"
        :style="{ background: cat.color }"
        @click="toggleCategory(cat.id)"
      >
        {{ cat.name }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick, computed } from 'vue'
import * as echarts from 'echarts/core'
import { GraphChart } from 'echarts/charts'
import {
  TooltipComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useGraphData } from '../composables/useGraphData'

echarts.use([
  GraphChart,
  TooltipComponent,
  LegendComponent,
  CanvasRenderer
])

const { graphData } = useGraphData()

const props = defineProps({
  mode: { type: String, default: 'full' },
  focusNodeId: { type: String, default: '' },
  height: { type: Number, default: 600 }
})

const data = computed(() => graphData.value)

const chartRef = ref(null)
let chartInstance = null
const hiddenCategories = ref(new Set())

const getCategoryColor = (categoryId) => {
  if (!data.value || !data.value.categories) return '#94a3b8'
  const cat = data.value.categories.find((c) => c.id === categoryId)
  return cat ? cat.color : '#94a3b8'
}

const buildFullOption = () => {
  const { nodes, edges } = data.value
  return {
    tooltip: {
      formatter: (params) => {
        if (params.dataType === 'edge') {
          return `${params.data.source} → ${params.data.target}<br/>关系: ${params.data.relation}`
        }
        return `<b>${params.data.name}</b><br/>${params.data.summary || ''}<br/><span style="color:#94a3b8">点击查看详情</span>`
      }
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        force: {
          repulsion: 350,
          edgeLength: [70, 140],
          gravity: 0.05,
          friction: 0.35
        },
        animationDurationUpdate: 600,
        label: {
          show: true,
          position: 'right',
          fontSize: 11,
          color: '#475569'
        },
        edgeSymbol: ['none', 'arrow'],
        edgeLabel: { show: false },
        data: nodes.map((n) => ({
          id: n.id,
          name: n.name,
          category: n.category,
          docPath: n.docPath,
          summary: n.summary,
          symbolSize: 24,
          itemStyle: {
            color: getCategoryColor(n.category),
            opacity: hiddenCategories.value.has(n.category) ? 0.1 : 1
          },
          label: { show: !hiddenCategories.value.has(n.category) }
        })),
        links: edges.map((e) => ({
          source: e.source,
          target: e.target,
          relation: e.relation,
          label: e.label,
          lineStyle: {
            color: '#cbd5e1',
            curveness: 0.05,
            width: 1
          }
        })),
        emphasis: {
          focus: 'adjacency',
          lineStyle: { width: 3 }
        }
      }
    ]
  }
}

const buildNeighborOption = () => {
  const { nodes, edges } = data.value
  const focusId = props.focusNodeId
  if (!focusId) return buildFullOption()

  const neighborIds = new Set([focusId])
  edges.forEach((e) => {
    if (e.source === focusId) neighborIds.add(e.target)
    if (e.target === focusId) neighborIds.add(e.source)
  })

  const subNodes = nodes.filter((n) => neighborIds.has(n.id))
  const subEdges = edges.filter(
    (e) => e.source === focusId || e.target === focusId
  )

  return {
    tooltip: {
      formatter: (params) => {
        if (params.dataType === 'edge') {
          return `${params.data.source} → ${params.data.target}<br/>关系: ${params.data.relation}`
        }
        const isFocus = params.data.id === focusId
        return `<b>${params.data.name}</b>${isFocus ? ' (当前节点)' : ''}<br/>${params.data.summary || ''}`
      }
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        draggable: true,
        force: {
          repulsion: 400,
          edgeLength: 100,
          gravity: 0.1
        },
        label: {
          show: true,
          position: 'right',
          fontSize: 12,
          color: '#475569'
        },
        edgeSymbol: ['none', 'arrow'],
        edgeLabel: { show: true, formatter: '{c}', fontSize: 10 },
        data: subNodes.map((n) => ({
          id: n.id,
          name: n.name,
          category: n.category,
          docPath: n.docPath,
          summary: n.summary,
          symbolSize: n.id === focusId ? 40 : 24,
          itemStyle: {
            color: getCategoryColor(n.category),
            borderColor: n.id === focusId ? '#000' : 'transparent',
            borderWidth: n.id === focusId ? 2 : 0
          }
        })),
        links: subEdges.map((e) => ({
          source: e.source,
          target: e.target,
          relation: e.relation,
          label: e.relation,
          lineStyle: { color: '#94a3b8', curveness: 0.1, width: 1.5 }
        })),
        emphasis: { focus: 'adjacency' }
      }
    ]
  }
}

const initChart = () => {
  if (!chartRef.value || !data.value) return
  if (chartInstance) {
    chartInstance.dispose()
  }
  chartInstance = echarts.init(chartRef.value)

  const option =
    props.mode === 'neighbor' ? buildNeighborOption() : buildFullOption()
  chartInstance.setOption(option)

  chartInstance.on('click', (params) => {
    if (params.dataType === 'node' && params.data.docPath) {
      const path = params.data.docPath
      if (typeof window !== 'undefined') {
        window.location.href = path
      }
    }
  })

  const handleResize = () => chartInstance && chartInstance.resize()
  window.addEventListener('resize', handleResize)
  chartRef.value.__resizeHandler = handleResize
}

const toggleCategory = (catId) => {
  if (hiddenCategories.value.has(catId)) {
    hiddenCategories.value.delete(catId)
  } else {
    hiddenCategories.value.add(catId)
  }
  nextTick(() => {
    if (props.mode === 'full' && chartInstance) {
      chartInstance.setOption(buildFullOption())
    }
  })
}

onMounted(() => {
  nextTick(() => initChart())
})

onBeforeUnmount(() => {
  if (chartRef.value && chartRef.value.__resizeHandler) {
    window.removeEventListener('resize', chartRef.value.__resizeHandler)
  }
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})

watch(
  () => [data.value, props.mode, props.focusNodeId],
  () => {
    nextTick(() => initChart())
  },
  { deep: true }
)
</script>

<style scoped>
.kg-wrapper {
  position: relative;
  width: 100%;
  margin: 16px 0;
}

.kg-container {
  width: 100%;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
}

.kg-legend {
  position: absolute;
  top: 12px;
  left: 12px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  z-index: 10;
}

.kg-legend-item {
  display: inline-block;
  padding: 4px 10px;
  font-size: 12px;
  color: white;
  border-radius: 12px;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s;
  opacity: 0.85;
}

.kg-legend-item:hover {
  opacity: 1;
}
</style>
