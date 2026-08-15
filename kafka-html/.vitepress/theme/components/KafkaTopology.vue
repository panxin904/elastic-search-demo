<template>
  <div class="topo-container">
    <div class="topo-toolbar">
      <button class="topo-toolbar__btn" @click="simulateBrokerDown">💥 Broker 宕机</button>
      <button class="topo-toolbar__btn" @click="simulateLeaderFail">🚨 Leader 故障</button>
      <button class="topo-toolbar__btn" @click="addBroker">➕ 扩容</button>
      <button class="topo-toolbar__btn" @click="resetCluster">🔄 重置</button>
      <span style="margin-left:auto;font-size:12px;color:var(--vp-c-text-2);">
        Kafka Cluster · 3 Broker · 2 Topic · ISR 副本同步
      </span>
    </div>

    <div class="topo-grid">
      <div v-for="b in brokers" :key="b.id"
        :class="['topo-broker', {
          'topo-broker--leader': b.role === 'leader' && !b.down,
          'topo-broker--follower': b.role !== 'leader' && !b.down,
          'topo-broker--down': b.down
        }]">
        <div class="topo-broker__title">Broker {{ b.id }}</div>
        <div class="topo-broker__role">
          <span v-if="b.down">⚠️ Down</span>
          <span v-else-if="b.role === 'leader'">👑 Leader</span>
          <span v-else>📡 Follower</span>
        </div>
        <div class="topo-broker__partitions">
          <div v-for="t in b.topics" :key="t.topic + '-' + t.partition">
            {{ t.topic }}-{{ t.partition }}
            <span v-if="t.leader" style="color:#F29111;">👑</span>
          </div>
        </div>
      </div>
    </div>

    <div style="padding:0 16px;">
      <div style="font-size:13px;font-weight:600;margin:8px 0 4px;">Topic & Partition 分布</div>
      <div v-for="topic in topics" :key="topic.name" class="topic-row">
        <div class="topic-row__name">{{ topic.name }}</div>
        <div class="topic-row__partitions">
          <div v-for="p in topic.partitions" :key="p.id" class="partition-pill">
            P{{ p.id }} <span v-if="p.leader === downBroker">(down)</span>
          </div>
        </div>
      </div>
    </div>

    <div class="topo-info-panel">
      <div v-if="mode === 'broker-down'">
        <b>Broker 宕机处理：</b>
        <br/>① Controller 监测到心跳超时
        <br/>② 该 Broker 上所有 Leader 分区触发 Leader 选举
        <br/>③ ISR 列表中的 Follower 提升为新 Leader
        <br/>④ 客户端收到 Metadata 刷新，重新连接到新 Leader
      </div>
      <div v-else-if="mode === 'leader-fail'">
        <b>Leader 故障处理：</b>
        <br/>① 该 Partition 的 Follower 检测到 Leader 失联
        <br/>② 第一个发现故障的 Follower 进入竞选（向 Controller 发送 LeaderAndIsr 请求）
        <br/>③ Controller 验证后从 ISR 列表中选新 Leader
        <br/>④ 客户端收到通知，自动重连新 Leader
      </div>
      <div v-else-if="mode === 'expanded'">
        <b>扩容完成：</b>
        <br/>① 新 Broker 加入集群
        <br/>② 触发 Reassign 操作，将部分 Partition 迁移到新 Broker
        <br/>③ 分区副本在新 Broker 上同步数据
        <br/>④ Reassign 完成，集群负载更均衡
      </div>
      <div v-else>
        <b>正常状态：</b>3 Broker × 2 Topic × 多 Partition，每个分区有 Leader + Follower。
        点击上方按钮模拟不同场景。
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const baseBrokers = [
  { id: 1, role: 'leader',   down: false, topics: [
    { topic: 'orders', partition: 0, leader: true },
    { topic: 'payments', partition: 0, leader: true }
  ]},
  { id: 2, role: 'follower', down: false, topics: [
    { topic: 'orders', partition: 1, leader: true },
    { topic: 'payments', partition: 1, leader: true }
  ]},
  { id: 3, role: 'follower', down: false, topics: [
    { topic: 'orders', partition: 2, leader: true }
  ]}
]

const baseTopics = [
  { name: 'orders',   partitions: [{id: 0, leader: 1}, {id: 1, leader: 2}, {id: 2, leader: 3}] },
  { name: 'payments', partitions: [{id: 0, leader: 1}, {id: 1, leader: 2}] }
]

const brokers = ref(JSON.parse(JSON.stringify(baseBrokers)))
const topics = ref(JSON.parse(JSON.stringify(baseTopics)))
const mode = ref(null)
const downBroker = ref(null)

function simulateBrokerDown() {
  resetCluster()
  brokers.value[0].down = true
  downBroker.value = 1
  mode.value = 'broker-down'
}

function simulateLeaderFail() {
  resetCluster()
  // 选 broker 1 上的 partition 0 让 leader 故障
  topics.value[0].partitions[0].leader = -1
  mode.value = 'leader-fail'
}

function addBroker() {
  resetCluster()
  brokers.value.push({
    id: 4, role: 'follower', down: false,
    topics: [{ topic: 'orders', partition: 3, leader: false }]
  })
  topics.value[0].partitions.push({ id: 3, leader: 4 })
  mode.value = 'expanded'
}

function resetCluster() {
  brokers.value = JSON.parse(JSON.stringify(baseBrokers))
  topics.value = JSON.parse(JSON.stringify(baseTopics))
  mode.value = null
  downBroker.value = null
}
</script>
