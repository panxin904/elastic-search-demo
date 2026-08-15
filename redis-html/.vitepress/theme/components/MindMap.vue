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
  height: { type: Number, default: 800 }
})

const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: 'Redis',
  symbolSize: 28,
  itemStyle: { color: '#DC382D' },
  children: [
    {
      name: '🚀 基础入门',
      itemStyle: { color: '#991b1b' },
      children: [
        { name: 'Redis 是什么', link: '/01-basics/intro' },
        { name: '安装部署', link: '/01-basics/install' },
        { name: '5 大基础类型', link: '/01-basics/datatypes' },
        { name: 'Key 通用操作', link: '/01-basics/keys' },
        { name: '过期策略', link: '/01-basics/expiration' }
      ]
    },
    {
      name: '🧬 数据结构',
      itemStyle: { color: '#92400e' },
      children: [
        { name: 'SDS 简单动态字符串', link: '/02-datastruct/sds' },
        { name: 'Dict 哈希表', link: '/02-datastruct/dict' },
        { name: 'SkipList 跳表', link: '/02-datastruct/skiplist' },
        { name: 'List 压缩列表', link: '/02-datastruct/listpack' },
        { name: 'QuickList', link: '/02-datastruct/quicklist' },
        { name: 'Stream', link: '/02-datastruct/stream' },
        { name: 'RedisObject', link: '/02-datastruct/object' }
      ]
    },
    {
      name: '💾 持久化',
      itemStyle: { color: '#166534' },
      children: [
        { name: '持久化总览', link: '/03-persistence/overview' },
        { name: 'RDB 快照', link: '/03-persistence/rdb' },
        { name: 'AOF 日志', link: '/03-persistence/aof' },
        { name: '混合持久化', link: '/03-persistence/mixed' },
        { name: '数据恢复策略', link: '/03-persistence/recovery' }
      ]
    },
    {
      name: '🔗 集群',
      itemStyle: { color: '#1e40af' },
      children: [
        { name: '主从复制', link: '/04-cluster/replication' },
        { name: 'Sentinel 哨兵', link: '/04-cluster/sentinel' },
        { name: 'Cluster 集群', link: '/04-cluster/cluster' },
        { name: '哈希槽分片', link: '/04-cluster/slots' },
        { name: 'Gossip 协议', link: '/04-cluster/gossip' },
        { name: '数据迁移', link: '/04-cluster/migration' },
        { name: '集群扩容', link: '/04-cluster/scale' }
      ]
    },
    {
      name: '☕ Java SDK',
      itemStyle: { color: '#3730a3' },
      children: [
        { name: 'Jedis', link: '/05-jdk/jedis' },
        { name: 'Lettuce', link: '/05-jdk/lettuce' },
        { name: 'Redisson', link: '/05-jdk/redisson' },
        { name: '连接池 HikariCP', link: '/05-jdk/connection-pool' },
        { name: 'Spring Data Redis', link: '/05-jdk/spring-data-redis' },
        { name: 'Spring Cache 集成', link: '/05-jdk/spring-cache' }
      ]
    },
    {
      name: '💼 企业实战',
      itemStyle: { color: '#9d174d' },
      children: [
        { name: '分布式锁', link: '/06-practice/distributed-lock' },
        { name: '分布式 Session', link: '/06-practice/session' },
        { name: '全局唯一 ID', link: '/06-practice/global-id' },
        { name: '限流', link: '/06-practice/ratelimit' },
        { name: '分布式限流', link: '/06-practice/distributed-ratelimit' },
        { name: '消息队列 Stream', link: '/06-practice/stream-mq' },
        { name: '延迟队列', link: '/06-practice/delay-queue' },
        { name: '排行榜', link: '/06-practice/leaderboard' },
        { name: '计数器', link: '/06-practice/counter' },
        { name: '缓存一致性', link: '/06-practice/cache-consistency' }
      ]
    },
    {
      name: '🛠️ 运维调优',
      itemStyle: { color: '#155e75' },
      children: [
        { name: '内存淘汰策略', link: '/07-ops/eviction' },
        { name: '内存管理与优化', link: '/07-ops/memory' },
        { name: '大 Key 热 Key', link: '/07-ops/bigkey-hotkey' },
        { name: '慢查询分析', link: '/07-ops/slowlog' },
        { name: '监控告警', link: '/07-ops/monitoring' },
        { name: 'Redis 7 新特性', link: '/07-ops/redis7-features' }
      ]
    },
    {
      name: '🎯 面试手撕题',
      itemStyle: { color: '#5b21b6' },
      children: [
        { name: '高频面试题（上）', link: '/08-interview/basic' },
        { name: '高频面试题（下）', link: '/08-interview/advanced' },
        { name: '分布式锁实现', link: '/08-interview/lock-coding' },
        { name: 'LRU 算法手撕', link: '/08-interview/lru' },
        { name: 'Redis 跳表实现', link: '/08-interview/skiplist-coding' },
        { name: '缓存穿透/击穿/雪崩', link: '/08-interview/avalanche' },
        { name: '一致性 Hash', link: '/08-interview/consistent-hash' },
        { name: 'Paxos/Raft 概述', link: '/08-interview/consensus' }
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
