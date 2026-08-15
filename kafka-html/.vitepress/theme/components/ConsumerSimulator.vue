<template>
  <div class="consumer-container">
    <div class="consumer-toolbar">
      <button class="consumer-toolbar__btn" @click="startSimulation">▶ 启动消费</button>
      <button class="consumer-toolbar__btn" @click="addConsumer">➕ 新增 Consumer</button>
      <button class="consumer-toolbar__btn" @click="triggerRebalance">🔄 触发再平衡</button>
      <button class="consumer-toolbar__btn" @click="reset">🗑️ 重置</button>
      <span style="margin-left:auto;font-size:12px;color:var(--vp-c-text-2);">
        Consumer Group: order-processor · Topic: orders · 3 Partitions
      </span>
    </div>

    <div class="consumer-grid">
      <div style="background:var(--vp-c-bg-soft);padding:12px;border-radius:6px;margin-bottom:12px;font-size:13px;">
        <b>📌 场景：</b> 3 个 Partition 的 orders topic，模拟消费者组扩容/缩容/再平衡
      </div>
      <div v-for="c in consumers" :key="c.id" :class="['consumer-row', `consumer-row--${c.status}`]">
        <div class="consumer-row__id">{{ c.id }}</div>
        <div class="consumer-row__msg">
          {{ c.message }}
          <div class="consumer-row__assigned" v-if="c.assigned.length">
            分配分区: {{ c.assigned.map(p => 'P' + p).join(', ') }}
          </div>
        </div>
        <div :class="['consumer-row__status', `consumer-row__status--${c.status}`]">
          {{ c.status === 'consuming' ? '消费中' : c.status === 'idle' ? '空闲' : '再平衡中' }}
        </div>
      </div>
    </div>

    <div class="topo-info-panel">
      <div v-if="phase === 'idle'">
        <b>初始分配：</b>3 个 Partition 分给 1 个 Consumer（C1 → P0/P1/P2）。
        点击「新增 Consumer」模拟扩容场景。
      </div>
      <div v-else-if="phase === 'rebalancing'">
        <b>再平衡进行中：</b>
        <br/>① 消费者组检测到成员变化
        <br/>② 所有 Consumer 暂停消费（revoke 阶段）
        <br/>③ Group Coordinator 重新分配分区
        <br/>④ Consumer 收到新分配（assign 阶段）
        <br/>⑤ 恢复消费
      </div>
      <div v-else-if="phase === 'rebalanced'">
        <b>再平衡完成：</b>分区重新分配后，每个 Consumer 负责不同 Partition。
        Round-Robin 分配策略：P0 → C1, P1 → C2, P2 → C3。
      </div>
      <div v-else>
        <b>正常消费中：</b>每个 Consumer 独立消费分配的分区，互不干扰。
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const consumers = ref([
  { id: 'C1', status: 'idle', assigned: [0, 1, 2], message: '等待启动' }
])
const phase = ref('idle')

let timers = []

function clearTimers() {
  timers.forEach(t => clearTimeout(t))
  timers = []
}

function reset() {
  clearTimers()
  consumers.value = [{ id: 'C1', status: 'idle', assigned: [0, 1, 2], message: '等待启动' }]
  phase.value = 'idle'
}

function startSimulation() {
  clearTimers()
  consumers.value.forEach(c => {
    c.status = 'consuming'
    c.message = '正在消费分区消息...'
  })
  phase.value = 'running'
}

function addConsumer() {
  // 模拟加入新 consumer 触发再平衡
  const newId = 'C' + (consumers.value.length + 1)
  consumers.value.push({ id: newId, status: 'rebalancing', assigned: [], message: '加入消费者组...' })
  consumers.value.forEach(c => c.status = 'rebalancing')
  phase.value = 'rebalancing'

  // 重新分配
  timers.push(setTimeout(() => {
    const total = consumers.value.length
    const partitions = [0, 1, 2]
    consumers.value.forEach((c, idx) => {
      c.assigned = partitions.filter(p => p % total === idx)
      c.status = 'idle'
      c.message = `已分配 ${c.assigned.length} 个分区`
    })
    phase.value = 'rebalanced'
    timers.push(setTimeout(() => startSimulation(), 1000))
  }, 2000))
}

function triggerRebalance() {
  // 模拟模拟 C1 故障触发再平衡
  if (consumers.value.length < 2) {
    addConsumer()
    return
  }
  consumers.value.forEach(c => c.status = 'rebalancing')
  phase.value = 'rebalancing'
  timers.push(setTimeout(() => {
    // C1 离开
    consumers.value = consumers.value.filter(c => c.id !== 'C1')
    const total = consumers.value.length
    const partitions = [0, 1, 2]
    consumers.value.forEach((c, idx) => {
      c.assigned = partitions.filter(p => p % total === idx)
      c.status = 'idle'
      c.message = 'C1 已下线，重新分配分区'
    })
    phase.value = 'rebalanced'
    timers.push(setTimeout(() => startSimulation(), 1000))
  }, 2000))
}
</script>
