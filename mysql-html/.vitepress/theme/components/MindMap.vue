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
  height: { type: Number, default: 700 }
})

const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: 'MySQL',
  symbolSize: 24,
  itemStyle: { color: '#00758F' },
  children: [
    {
      name: '🏛️ 基础层',
      itemStyle: { color: '#00758F' },
      children: [
        { name: '体系结构', link: '/01-foundation/architecture' },
        { name: '存储引擎 (InnoDB/MyISAM)', link: '/01-foundation/storage-engine' },
        { name: '数据类型', link: '/01-foundation/data-types' },
        { name: '字符集 utf8mb4', link: '/01-foundation/charset' }
      ]
    },
    {
      name: '🌲 索引',
      itemStyle: { color: '#16a34a' },
      children: [
        { name: 'B+Tree 原理', link: '/02-index/btree' },
        { name: '聚簇索引', link: '/02-index/clustered' },
        { name: '覆盖索引', link: '/02-index/covering' },
        { name: 'ICP 索引下推', link: '/02-index/icp' }
      ]
    },
    {
      name: '📝 SQL',
      itemStyle: { color: '#f59e0b' },
      children: [
        { name: 'CRUD & DDL', link: '/03-sql/crud' },
        { name: 'JOIN 7 种', link: '/03-sql/join' },
        { name: '窗口函数', link: '/03-sql/window-functions' },
        { name: '函数与 CTE', link: '/03-sql/functions' }
      ]
    },
    {
      name: '🔒 事务锁',
      itemStyle: { color: '#ec4899' },
      children: [
        { name: 'ACID & 隔离级别', link: '/04-transaction/isolation' },
        { name: 'InnoDB 锁', link: '/04-transaction/locks' },
        { name: '死锁分析', link: '/04-transaction/deadlock' },
        { name: 'MVCC', link: '/04-transaction/mvcc' }
      ]
    },
    {
      name: '🚀 性能',
      itemStyle: { color: '#6366f1' },
      children: [
        { name: 'EXPLAIN 解读', link: '/05-optimization/explain' },
        { name: '慢查询定位', link: '/05-optimization/slow-query' },
        { name: '索引优化', link: '/05-optimization/index-tuning' },
        { name: 'SQL 改写', link: '/05-optimization/sql-rewrite' }
      ]
    },
    {
      name: '🔁 复制',
      itemStyle: { color: '#06b6d4' },
      children: [
        { name: 'binlog', link: '/06-replication/binlog' },
        { name: '主从同步', link: '/06-replication/replication' },
        { name: '主从延迟', link: '/06-replication/lag' },
        { name: '读写分离', link: '/06-replication/read-write-split' }
      ]
    },
    {
      name: '🛡️ 高可用',
      itemStyle: { color: '#ef4444' },
      children: [
        { name: 'MHA', link: '/07-ha/mha' },
        { name: 'MGR', link: '/07-ha/mgr' },
        { name: 'ProxySQL', link: '/07-ha/proxysql' }
      ]
    },
    {
      name: '💾 备份',
      itemStyle: { color: '#854d0e' },
      children: [
        { name: 'mysqldump', link: '/08-backup/mysqldump' },
        { name: 'xtrabackup', link: '/08-backup/xtrabackup' },
        { name: 'binlog 恢复', link: '/08-backup/binlog-recovery' }
      ]
    },
    {
      name: '📈 监控',
      itemStyle: { color: '#8b5cf6' },
      children: [
        { name: '慢查询日志', link: '/09-monitoring/slow-log' },
        { name: 'performance_schema', link: '/09-monitoring/performance-schema' },
        { name: 'Prometheus', link: '/09-monitoring/prometheus' }
      ]
    },
    {
      name: '🧩 分库分表',
      itemStyle: { color: '#312e81' },
      children: [
        { name: '拆分策略', link: '/10-sharding/strategy' },
        { name: 'ShardingSphere', link: '/10-sharding/shardingsphere' },
        { name: 'MyCat', link: '/10-sharding/mycat' },
        { name: '一致性 Hash', link: '/10-sharding/sharding-key' }
      ]
    },
    {
      name: '🛠️ 工具',
      itemStyle: { color: '#10b981' },
      children: [
        { name: 'mysql client', link: '/11-tools/mysql-client' },
        { name: 'pt-toolkit', link: '/11-tools/pt-toolkit' },
        { name: 'SQL 速查', link: '/11-tools/cheatsheet' }
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
      left: '12%',
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
      expandAndCollapse: true,
      animationDuration: 550,
      animationDurationUpdate: 750,
      lineStyle: { color: '#aaa', width: 1, curveness: 0.1 }
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

<style scoped>
.mindmap-container {
  position: relative;
}
.mm-toolbar {
  display: flex;
  gap: 8px;
  padding: 8px 12px;
  background: var(--vp-c-bg-soft);
  border-top: 1px solid var(--vp-c-divider);
}
.mm-toolbar__btn {
  padding: 4px 12px;
  background: var(--vp-c-brand-1);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}
.mm-toolbar__btn:hover { opacity: 0.85; }
</style>