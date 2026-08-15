<template>
  <div class="mindmap-container">
    <div ref="chartRef" :style="{ width: '100%', height: height + 'px' }"></div>
    <div class="mm-toolbar">
      <button class="mm-toolbar__btn" @click="expandAll">📖 全部展开</button>
      <button class="mm-toolbar__btn" @click="collapseAll">📕 全部收起</button>
      <button class="mm-toolbar__btn" @click="resetView">🎯 重置视图</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { TreeChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([TreeChart, TooltipComponent, CanvasRenderer])

const props = defineProps({
  height: { type: Number, default: 880 }
})

const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: 'Python',
  symbolSize: 28,
  itemStyle: { color: '#3776AB' },
  children: [
    {
      name: '🐍 Python 入门',
      itemStyle: { color: '#1e40af' },
      children: [
        { name: 'Python 是什么', link: '/01-basics/intro' },
        { name: '安装与环境', link: '/01-basics/install' },
        { name: '基础语法', link: '/01-basics/syntax' },
        { name: '数据结构', link: '/01-basics/data-structures' },
        { name: '控制流', link: '/01-basics/control-flow' }
      ]
    },
    {
      name: '🔬 底层原理',
      itemStyle: { color: '#92400e' },
      children: [
        { name: 'Python 解释器', link: '/02-principles/interpreter' },
        { name: '字节码与执行', link: '/02-principles/bytecode' },
        { name: '对象模型', link: '/02-principles/object-model' },
        { name: '内存管理', link: '/02-principles/memory' },
        { name: 'GIL 全局锁', link: '/02-principles/gil' },
        { name: '垃圾回收', link: '/02-principles/gc' },
        { name: '性能剖析', link: '/02-principles/profiling' }
      ]
    },
    {
      name: '📚 常用库',
      itemStyle: { color: '#166534' },
      children: [
        { name: '标准库概览', link: '/03-libraries/stdlib' },
        { name: 'requests HTTP', link: '/03-libraries/requests' },
        { name: 'BeautifulSoup', link: '/03-libraries/beautifulsoup' },
        { name: 'SQLAlchemy ORM', link: '/03-libraries/sqlalchemy' },
        { name: 'pandas 数据分析', link: '/03-libraries/pandas' },
        { name: 'pytest 测试', link: '/03-libraries/pytest' }
      ]
    },
    {
      name: '⚡ 并发与异步',
      itemStyle: { color: '#9d174d' },
      children: [
        { name: 'threading 多线程', link: '/04-concurrency/threading' },
        { name: 'multiprocessing', link: '/04-concurrency/multiprocessing' },
        { name: 'asyncio 协程', link: '/04-concurrency/asyncio' },
        { name: '同步原语', link: '/04-concurrency/sync-primitives' },
        { name: '线程池与进程池', link: '/04-concurrency/pool' },
        { name: '并发模式', link: '/04-concurrency/patterns' }
      ]
    },
    {
      name: '🕷️ Python 爬虫',
      itemStyle: { color: '#155e75' },
      children: [
        { name: '爬虫基础', link: '/05-scraping/basics' },
        { name: 'requests+BS4', link: '/05-scraping/requests-bs4' },
        { name: 'Scrapy 框架', link: '/05-scraping/scrapy' },
        { name: '动态渲染', link: '/05-scraping/dynamic' },
        { name: '反爬对抗', link: '/05-scraping/anti-crawl' }
      ]
    },
    {
      name: '🤖 AI 与机器学习',
      itemStyle: { color: '#5b21b6' },
      children: [
        { name: 'AI 应用概览', link: '/06-ai-ml/overview' },
        { name: '机器学习基础', link: '/06-ai-ml/ml-basics' },
        { name: 'Hugging Face', link: '/06-ai-ml/huggingface' },
        { name: 'LLM 应用开发', link: '/06-ai-ml/llm-apps' },
        { name: '计算机视觉', link: '/06-ai-ml/cv' },
        { name: '自然语言处理', link: '/06-ai-ml/nlp' }
      ]
    },
    {
      name: '📊 数据处理',
      itemStyle: { color: '#9a3412' },
      children: [
        { name: 'pandas 入门', link: '/07-data/pandas' },
        { name: 'NumPy 数值计算', link: '/07-data/numpy' },
        { name: 'Matplotlib 可视化', link: '/07-data/matplotlib' },
        { name: '数据清洗', link: '/07-data/cleaning' },
        { name: '数据分析实战', link: '/07-data/analysis' },
        { name: '大数据处理', link: '/07-data/big-data' }
      ]
    },
    {
      name: '🧮 算法与数据结构',
      itemStyle: { color: '#854d0e' },
      children: [
        { name: '复杂度分析', link: '/08-algorithms/complexity' },
        { name: '内置数据结构', link: '/08-algorithms/builtin' },
        { name: '排序算法', link: '/08-algorithms/sort' },
        { name: '搜索算法', link: '/08-algorithms/search' },
        { name: '树与图', link: '/08-algorithms/tree-graph' },
        { name: '动态规划', link: '/08-algorithms/dp' }
      ]
    },
    {
      name: '💼 企业实战',
      itemStyle: { color: '#991b1b' },
      children: [
        { name: '项目结构', link: '/09-enterprise/structure' },
        { name: '依赖管理', link: '/09-enterprise/dependencies' },
        { name: '单元测试', link: '/09-enterprise/testing' },
        { name: '性能优化', link: '/09-enterprise/performance' },
        { name: 'FastAPI Web 实战', link: '/09-enterprise/fastapi' },
        { name: 'Docker 部署', link: '/09-enterprise/docker' },
        { name: '日志与监控', link: '/09-enterprise/logging' },
        { name: '安全最佳实践', link: '/09-enterprise/security' }
      ]
    }
  ]
}

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  chart.setOption({
    tooltip: {
      trigger: 'item',
      triggerOn: 'mousemove',
      formatter: (p) => {
        if (p.data?.link) return `<b>${p.name}</b><br/>点击跳转`
        return p.name
      }
    },
    series: [{
      type: 'tree',
      data: [mindMapData],
      top: '5%',
      left: '8%',
      bottom: '5%',
      right: '20%',
      symbolSize: 14,
      orient: 'LR',
      expandAndCollapse: true,
      initialTreeDepth: 2,
      label: {
        position: 'left',
        verticalAlign: 'middle',
        align: 'right',
        fontSize: 13,
        color: 'var(--vp-c-text-1, #333)'
      },
      leaves: {
        label: {
          position: 'right',
          verticalAlign: 'middle',
          align: 'left'
        }
      },
      emphasis: { focus: 'descendant' },
      animationDuration: 550,
      animationDurationUpdate: 750,
      lineStyle: { color: '#aaa', width: 1, curveness: 0.05 }
    }]
  })
  chart.on('click', (params) => {
    if (params.data?.link) {
      window.location.href = params.data.link
    }
  })
}

function expandAll() {
  if (!chart) return
  const traverse = (node, depth) => {
    if (depth > 0 && node.children) {
      chart.dispatchAction({ type: 'treeExpandAndCollapse', data: node, seriesIndex: 0 })
    }
    if (node.children) node.children.forEach(c => traverse(c, depth + 1))
  }
  traverse(mindMapData, 0)
}

function collapseAll() {
  if (!chart) return
  const traverse = (node) => {
    if (node.children) {
      node.children.forEach(c => {
        chart.dispatchAction({ type: 'treeExpandAndCollapse', data: c, seriesIndex: 0 })
        traverse(c)
      })
    }
  }
  traverse(mindMapData)
}

function resetView() {
  if (!chart) return
  chart.dispatchAction({ type: 'restore' })
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
