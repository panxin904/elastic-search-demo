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
const mindMapData = { name: '大数据全栈', symbolSize: 30, itemStyle: { color: '#1f2937' }, children: [
  { name: '🧠 大数据基础', itemStyle: { color: '#2563eb' }, children: [
    { name: '4V 特征', link: '/01-basics/4v' }, { name: 'Hadoop 生态', link: '/01-basics/hadoop-eco' }, { name: '批 / 流计算', link: '/01-basics/batch-stream' }
  ]},
  { name: '📦 HDFS', itemStyle: { color: '#0891b2' }, children: [
    { name: '架构', link: '/02-hdfs/architecture' }, { name: '副本机制', link: '/02-hdfs/replication' }, { name: 'NameNode HA', link: '/02-hdfs/ha' }
  ]},
  { name: '⚙️ MapReduce / Spark', itemStyle: { color: '#dc2626' }, children: [
    { name: 'MapReduce 原理', link: '/03-mapreduce/principle' }, { name: 'Spark Core / RDD', link: '/04-spark/rdd' }, { name: 'Spark SQL', link: '/04-spark/dataframe' }, { name: 'Spark 调优', link: '/04-spark/tuning' }
  ]},
  { name: '🌊 Flink', itemStyle: { color: '#7c3aed' }, children: [
    { name: '架构', link: '/05-flink/architecture' }, { name: '状态与 Checkpoint', link: '/05-flink/state' }, { name: 'Exactly-once', link: '/05-flink/exactly-once' }, { name: 'Flink CDC', link: '/05-flink/cdc' }
  ]},
  { name: '🏛️ Hive', itemStyle: { color: '#b45309' }, children: [
    { name: '架构', link: '/06-hive/architecture' }, { name: '优化', link: '/06-hive/optimize' }, { name: 'Hive on Spark', link: '/06-hive/engine' }
  ]},
  { name: '📨 Kafka 流', itemStyle: { color: '#be185d' }, children: [
    { name: 'Kafka Streams', link: '/07-kafka-streaming/streams' }, { name: 'CDC 同步', link: '/07-kafka-streaming/cdc' }, { name: '数据血缘', link: '/07-kafka-streaming/lineage' }
  ]},
  { name: '🏛️ 数据建模', itemStyle: { color: '#a21caf' }, children: [
    { name: 'OLAP vs OLTP', link: '/08-modeling/olap-oltp' }, { name: 'Inmon vs Kimball', link: '/08-modeling/inmon-kimball' }, { name: '星型 / 雪花', link: '/08-modeling/star-snowflake' }, { name: 'Data Vault', link: '/08-modeling/data-vault' }
  ]},
  { name: '🏢 数仓架构', itemStyle: { color: '#1e40af' }, children: [
    { name: 'Snowflake', link: '/09-dw-architecture/snowflake' }, { name: 'Redshift / BigQuery', link: '/09-dw-architecture/redshift-bigquery' }
  ]},
  { name: '💧 数据湖', itemStyle: { color: '#0e7490' }, children: [
    { name: '数据湖 三剑客', link: '/10-data-lake/three-pillars' }, { name: 'Delta / Iceberg / Hudi', link: '/10-data-lake/delta-iceberg-hudi' }, { name: 'Lakehouse', link: '/10-data-lake/lakehouse' }
  ]},
  { name: '🔄 ELT', itemStyle: { color: '#047857' }, children: [
    { name: 'Airflow / dbt', link: '/11-elt-pipeline/airflow-dbt' }, { name: 'CDC 同步', link: '/11-elt-pipeline/cdc' }, { name: '血缘', link: '/11-elt-pipeline/lineage' }
  ]},
  { name: '📊 OLAP 引擎', itemStyle: { color: '#c2410c' }, children: [
    { name: 'ClickHouse', link: '/12-olap-engine/clickhouse' }, { name: 'Doris / StarRocks', link: '/12-olap-engine/doris-starrocks' }, { name: 'OLAP 选型', link: '/12-olap-engine/selection' }
  ]},
  { name: '🏢 企业案例', itemStyle: { color: '#5b21b6' }, children: [
    { name: '用户画像', link: '/13-cases/user-profile' }, { name: '推荐系统', link: '/13-cases/recommendation' }, { name: '风控特征', link: '/13-cases/risk-control' }, { name: '日志分析', link: '/13-cases/log-platform' }
  ]},
  { name: '🎯 面试', itemStyle: { color: '#9a3412' }, children: [
    { name: '高频题', link: '/14-interview-practice/questions' }, { name: '项目案例', link: '/14-interview-practice/cases' }
  ]}
] }
function renderChart() { if (!chartRef.value) return; chart = echarts.init(chartRef.value, undefined, { renderer: 'canvas' }); chart.setOption({ tooltip: { trigger: 'item', formatter: (p) => p.data?.link ? `<b>${p.name}</b><br/>点击跳转` : p.name }, series: [{ type: 'tree', data: [mindMapData], top: '5%', left: '8%', bottom: '5%', right: '20%', symbolSize: 14, orient: 'LR', expandAndCollapse: true, initialTreeDepth: 2, label: { position: 'left', verticalAlign: 'middle', align: 'right', fontSize: 13, color: 'var(--vp-c-text-1, #333)' }, leaves: { label: { position: 'right', verticalAlign: 'middle', align: 'left' } }, emphasis: { focus: 'descendant' }, animationDuration: 550, animationDurationUpdate: 750, lineStyle: { color: '#aaa', width: 1, curveness: 0.05 } }] }); chart.on('click', (params) => { if (params.data?.link) window.location.href = params.data.link }) }
function expandAll() { if (!chart) return; const t = (n) => { if (n.children) { chart.dispatchAction({ type: 'treeExpandAndCollapse', data: n, seriesIndex: 0 }); n.children.forEach(t) } }; t(mindMapData) }
function collapseAll() { if (!chart) return; const t = (n) => { if (n.children) { n.children.slice().reverse().forEach(c => { chart.dispatchAction({ type: 'treeExpandAndCollapse', data: c, seriesIndex: 0 }); t(c) }) } }; t(mindMapData) }
function resetView() { if (chart) chart.dispatchAction({ type: 'restore' }) }
onMounted(() => { renderChart(); window.addEventListener('resize', () => chart?.resize()) })
onBeforeUnmount(() => { chart?.dispose(); chart = null })
</script>
