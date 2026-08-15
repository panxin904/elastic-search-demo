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
  height: { type: Number, default: 860 }
})

const chartRef = ref(null)
let chart = null

const mindMapData = {
  name: 'Kafka',
  symbolSize: 28,
  itemStyle: { color: '#231F20' },
  children: [
    {
      name: '🚀 Kafka 入门',
      itemStyle: { color: '#991b1b' },
      children: [
        { name: 'Kafka 是什么', link: '/01-basics/intro' },
        { name: '安装部署', link: '/01-basics/install' },
        { name: '核心概念', link: '/01-basics/concepts' },
        { name: 'Topic & Partition', link: '/01-basics/topic-partition' },
        { name: '消息模型', link: '/01-basics/message-model' }
      ]
    },
    {
      name: '🏗️ 架构原理',
      itemStyle: { color: '#92400e' },
      children: [
        { name: '整体架构', link: '/02-architecture/overview' },
        { name: 'Controller', link: '/02-architecture/controller' },
        { name: '分区副本机制', link: '/02-architecture/replica' },
        { name: 'Leader 选举', link: '/02-architecture/leader-election' },
        { name: '日志存储', link: '/02-architecture/log-storage' },
        { name: '零拷贝原理', link: '/02-architecture/zero-copy' },
        { name: '控制器演进', link: '/02-architecture/controller-evolution' }
      ]
    },
    {
      name: '🛠️ 命令行工具',
      itemStyle: { color: '#166534' },
      children: [
        { name: '常用命令总览', link: '/03-cli/overview' },
        { name: 'Topic 管理', link: '/03-cli/topic' },
        { name: '生产消费调试', link: '/03-cli/produce-consume' },
        { name: '消费者组', link: '/03-cli/consumer-group' }
      ]
    },
    {
      name: '✍️ 生产者 Producer',
      itemStyle: { color: '#1e40af' },
      children: [
        { name: '生产者原理', link: '/04-producer/principle' },
        { name: '消息发送流程', link: '/04-producer/send-flow' },
        { name: '幂等性', link: '/04-producer/idempotent' },
        { name: '事务', link: '/04-producer/transaction' },
        { name: '顺序保证', link: '/04-producer/order' },
        { name: '性能调优', link: '/04-producer/tuning' }
      ]
    },
    {
      name: '📥 消费者 Consumer',
      itemStyle: { color: '#3730a3' },
      children: [
        { name: '消费者原理', link: '/05-consumer/principle' },
        { name: '消费者组', link: '/05-consumer/group' },
        { name: '偏移量提交', link: '/05-consumer/offset' },
        { name: '再平衡', link: '/05-consumer/rebalance' },
        { name: '手动提交', link: '/05-consumer/manual-commit' },
        { name: '多线程消费', link: '/05-consumer/multi-thread' }
      ]
    },
    {
      name: '☕ Java SDK',
      itemStyle: { color: '#9d174d' },
      children: [
        { name: 'Producer API', link: '/06-jdk/producer-api' },
        { name: 'Consumer API', link: '/06-jdk/consumer-api' },
        { name: 'AdminClient', link: '/06-jdk/admin-client' },
        { name: '序列化反序列化', link: '/06-jdk/serialization' },
        { name: '自定义分区器', link: '/06-jdk/partitioner' },
        { name: '异常处理', link: '/06-jdk/exception' }
      ]
    },
    {
      name: '🌱 Spring 集成',
      itemStyle: { color: '#155e75' },
      children: [
        { name: 'Spring Kafka 入门', link: '/07-spring/intro' },
        { name: 'KafkaTemplate', link: '/07-spring/kafka-template' },
        { name: '@KafkaListener', link: '/07-spring/listener' },
        { name: 'Spring 事务', link: '/07-spring/transaction' },
        { name: 'Spring Boot 集成', link: '/07-spring/spring-boot' }
      ]
    },
    {
      name: '💼 企业实战',
      itemStyle: { color: '#5b21b6' },
      children: [
        { name: '消息幂等性', link: '/08-enterprise/idempotent' },
        { name: '顺序消费', link: '/08-enterprise/order-consume' },
        { name: '延迟消息', link: '/08-enterprise/delay' },
        { name: '死信队列', link: '/08-enterprise/dead-letter' },
        { name: '消息积压', link: '/08-enterprise/backlog' },
        { name: 'Kafka Connect', link: '/08-enterprise/connect' },
        { name: 'Kafka Streams', link: '/08-enterprise/streams' },
        { name: '监控告警', link: '/08-enterprise/monitoring' },
        { name: '多环境隔离', link: '/08-enterprise/multi-env' },
        { name: '集群部署', link: '/08-enterprise/cluster' }
      ]
    },
    {
      name: '🛠️ 运维调优',
      itemStyle: { color: '#9a3412' },
      children: [
        { name: '集群规划', link: '/09-ops/capacity' },
        { name: '性能压测', link: '/09-ops/benchmark' },
        { name: 'JVM 调优', link: '/09-ops/jvm' },
        { name: '日志清理', link: '/09-ops/log-cleanup' },
        { name: '监控指标', link: '/09-ops/metrics' },
        { name: '故障恢复', link: '/09-ops/disaster-recovery' }
      ]
    },
    {
      name: '🎯 面试手撕',
      itemStyle: { color: '#854d0e' },
      children: [
        { name: '高频面试题（上）', link: '/10-interview/basic' },
        { name: '高频面试题（下）', link: '/10-interview/advanced' },
        { name: '副本同步机制', link: '/10-interview/replica-sync' },
        { name: '消息丢失解决方案', link: '/10-interview/message-loss' },
        { name: 'Kafka vs RocketMQ', link: '/10-interview/kafka-vs-rocketmq' },
        { name: 'Leader 选举机制', link: '/10-interview/election' },
        { name: 'Exactly Once 实现', link: '/10-interview/exactly-once' },
        { name: 'Kafka 为什么快', link: '/10-interview/why-fast' }
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
