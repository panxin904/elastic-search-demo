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
import * as echarts from 'echarts/core'; import { TreeChart } from 'echarts/charts'; import { TooltipComponent } from 'echarts/components'; import { CanvasRenderer } from 'echarts/renderers'
echarts.use([TreeChart, TooltipComponent, CanvasRenderer])
const props = defineProps({ height: { type: Number, default: 940 } }); const chartRef = ref(null); let chart = null
const mindMapData = { name: '企业级架构', symbolSize: 30, itemStyle: { color: '#1f2937' }, children: [
  { name: '🧠 并发理论', itemStyle: { color: '#475569' }, children: [
    { name: 'JMM 内存模型', link: '/01-concurrency-theory/jmm' }, { name: 'happens-before', link: '/01-concurrency-theory/happens-before' }, { name: 'CAS / Lock-Free', link: '/01-concurrency-theory/cas' }, { name: 'volatile / final', link: '/01-concurrency-theory/volatile' }
  ]},
  { name: '🧵 线程池原理', itemStyle: { color: '#0891b2' }, children: [
    { name: 'ThreadPoolExecutor', link: '/02-thread-pool/executor' }, { name: 'ForkJoinPool', link: '/02-thread-pool/forkjoin' }, { name: 'JDK 21 虚拟线程', link: '/02-thread-pool/virtual' }
  ]},
  { name: '🏛️ 高可用理论', itemStyle: { color: '#7c3aed' }, children: [
    { name: 'CAP 定理', link: '/03-ha-theory/cap' }, { name: 'BASE / 最终一致性', link: '/03-ha-theory/base' }, { name: 'Raft 共识', link: '/03-ha-theory/raft' }, { name: 'Quorum / 多数派', link: '/03-ha-theory/quorum' }, { name: '幂等性设计', link: '/03-ha-theory/idempotency' }
  ]},
  { name: '🚦 限流', itemStyle: { color: '#db2777' }, children: [
    { name: '令牌桶算法', link: '/04-rate-limit/token-bucket' }, { name: '漏桶 / 滑动窗口', link: '/04-rate-limit/leaky-bucket' }, { name: '分布式限流', link: '/04-rate-limit/distributed' }
  ]},
  { name: '⚡ 熔断降级', itemStyle: { color: '#ea580c' }, children: [
    { name: '熔断器三态', link: '/05-circuit-breaker/states' }, { name: 'Sentinel / Hystrix', link: '/05-circuit-breaker/impl' }, { name: 'Fallback 设计', link: '/05-circuit-breaker/fallback' }
  ]},
  { name: '🧩 微服务', itemStyle: { color: '#2563eb' }, children: [
    { name: '服务拆分原则', link: '/06-microservice/split' }, { name: '服务发现', link: '/06-microservice/discovery' }, { name: 'API 网关', link: '/06-microservice/gateway' }, { name: '配置中心', link: '/06-microservice/config' }
  ]},
  { name: '🔄 分布式事务', itemStyle: { color: '#16a34a' }, children: [
    { name: '2PC / 3PC', link: '/07-distributed-tx/2pc' }, { name: 'TCC 模式', link: '/07-distributed-tx/tcc' }, { name: 'Saga 模式', link: '/07-distributed-tx/saga' }, { name: '本地消息表', link: '/07-distributed-tx/local-table' }
  ]},
  { name: '📨 消息队列', itemStyle: { color: '#f59e0b' }, children: [
    { name: 'Kafka vs RabbitMQ', link: '/08-message-queue/compare' }, { name: '顺序 / 幂等', link: '/08-message-queue/idempotency' }, { name: '死信 / 重试', link: '/08-message-queue/dlq' }
  ]},
  { name: '💾 缓存', itemStyle: { color: '#ec4899' }, children: [
    { name: '多级缓存架构', link: '/09-cache/architecture' }, { name: '缓存穿透 / 击穿 / 雪崩', link: '/09-cache/breakdown' }, { name: '一致性策略', link: '/09-cache/consistency' }
  ]},
  { name: '🗄️ 分库分表', itemStyle: { color: '#0ea5e9' }, children: [
    { name: '垂直 / 水平拆分', link: '/10-database-sharding/strategy' }, { name: '路由 / 扩容', link: '/10-database-sharding/routing' }, { name: '分布式 ID', link: '/10-database-sharding/id' }
  ]},
  { name: '🧠 DDD 领域驱动', itemStyle: { color: '#f97316' }, children: [
    { name: '聚合 / 实体 / 值对象', link: '/11-ddd/basics' }, { name: '限界上下文', link: '/11-ddd/bounded-context' }, { name: '事件风暴', link: '/11-ddd/event-storming' }
  ]},
  { name: '🧱 微服务模式', itemStyle: { color: '#14b8a6' }, children: [
    { name: 'Service Mesh', link: '/12-microservice-patterns/service-mesh' }, { name: 'Sidecar', link: '/12-microservice-patterns/sidecar' }, { name: 'Saga / Bulkhead', link: '/12-microservice-patterns/saga' }
  ]},
  { name: '🔭 可观测', itemStyle: { color: '#9333ea' }, children: [
    { name: 'Metrics / Tracing / Logging', link: '/13-observability/three-pillars' }, { name: 'OpenTelemetry', link: '/13-observability/otel' }
  ]},
  { name: '🏢 企业案例', itemStyle: { color: '#dc2626' }, children: [
    { name: '秒杀系统', link: '/14-enterprise-cases/flash-sale' }, { name: '短链系统', link: '/14-enterprise-cases/short-url' }, { name: '异地多活', link: '/14-enterprise-cases/multi-region' }
  ]}
] }

function renderChart() {
  if (!chartRef.value) return
  chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' })
  chart.setOption({ tooltip: { trigger: 'item', triggerOn: 'mousemove', formatter: (p) => p.data?.link ? `<b>${p.name}</b><br/>点击跳转` : p.name },
    series: [{ type: 'tree', data: [mindMapData], top: '5%', left: '8%', bottom: '5%', right: '20%', symbolSize: 14, orient: 'LR', expandAndCollapse: true, initialTreeDepth: 2,
      label: { position: 'left', verticalAlign: 'middle', align: 'right', fontSize: 13, color: 'var(--vp-c-text-1, #333)' },
      leaves: { label: { position: 'right', verticalAlign: 'middle', align: 'left' } }, emphasis: { focus: 'descendant' }, animationDuration: 550, animationDurationUpdate: 750, lineStyle: { color: '#aaa', width: 1, curveness: 0.05 } }] })
  chart.on('click', (params) => { if (params.data?.link) window.location.href = params.data.link })
}
function expandAll() { if (!chart) return; const traverse = (node, depth) => { if (depth > 0 && node.children) chart.dispatchAction({ type: 'treeExpandAndCollapse', data: node, seriesIndex: 0 }); if (node.children) node.children.forEach(c => traverse(c, depth + 1)) }; traverse(mindMapData, 0) }
function collapseAll() { const traverse = (node) => { if (node.children) { node.children.forEach(c => { chart.dispatchAction({ type: 'treeExpandAndCollapse', data: c, seriesIndex: 0 }); traverse(c) }) } }; traverse(mindMapData) }
function resetView() { if (chart) chart.dispatchAction({ type: 'restore' }) }
onMounted(() => { renderChart(); window.addEventListener('resize', () => chart?.resize()) })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>