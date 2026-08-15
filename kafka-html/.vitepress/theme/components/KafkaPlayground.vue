<template>
  <div class="cmd-container">
    <div class="cmd-toolbar">
      <button class="cmd-toolbar__btn" @click="runCommands">▶ 执行</button>
      <button class="cmd-toolbar__btn" @click="clearAll">🗑️ 清空</button>
      <button class="cmd-toolbar__btn" @click="loadSample">📝 示例</button>
      <span style="margin-left:auto;font-size:12px;color:var(--vp-c-text-2);">
        模拟 Kafka CLI · Topic / Producer / Consumer / Consumer Group
      </span>
    </div>
    <div class="cmd-grid">
      <div class="cmd-input-panel">
        <div style="font-size:12px;color:var(--vp-c-text-2);margin-bottom:6px;">kafka-console-commands</div>
        <textarea
          v-model="input"
          class="cmd-input-area"
          spellcheck="false"
          placeholder="例如：&#10;CREATE TOPIC orders 3 2&#10;PRODUCE orders 'order-001'&#10;CONSUMER orders GROUP order-processor&#10;DESCRIBE TOPIC orders"
        />
        <div class="cmd-suggestion">
          💡 支持：CREATE TOPIC / LIST TOPICS / DESCRIBE TOPIC / PRODUCE / CONSUMER / GROUP LIST / GROUP DESCRIBE / OFFSETS
        </div>
      </div>
      <div class="cmd-output-panel">
        <div style="font-size:12px;color:var(--vp-c-text-2);margin-bottom:6px;">output</div>
        <pre v-if="!output.length" class="cmd-output-area">点击「执行」运行命令</pre>
        <div v-else class="cmd-output-area">
          <div v-for="(line, idx) in output" :key="idx" :class="['cmd-result-line', `cmd-result-line--${line.type}`]">
            <span v-if="line.type === 'err'">[ERROR] {{ line.text }}</span>
            <span v-else-if="line.type === 'warn'">[WARN] {{ line.text }}</span>
            <span v-else-if="line.type === 'info'">[INFO] {{ line.text }}</span>
            <span v-else>{{ line.text }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const input = ref('CREATE TOPIC orders 3 2\nLIST TOPICS\nPRODUCE orders "order-001 alice 99.9"\nPRODUCE orders "order-002 bob 88.8"\nCONSUMER orders GROUP order-processor 5')
const output = ref([])

const state = ref({
  topics: new Map(),  // name -> { partitions, replicas }
  messages: new Map(), // topic -> [{partition, offset, key, value, ts}]
  groups: new Map(),   // group -> { topic, offsets: {partition: offset} }
})

let globalOffset = 0

function clearAll() {
  input.value = ''
  output.value = []
  state.value = { topics: new Map(), messages: new Map(), groups: new Map() }
}

function loadSample() {
  input.value = [
    'CREATE TOPIC orders 3 2',
    'CREATE TOPIC payments 2 2',
    'LIST TOPICS',
    'DESCRIBE TOPIC orders',
    'PRODUCE orders "order-001 alice 99.9"',
    'PRODUCE orders "order-002 bob 88.8"',
    'PRODUCE payments "pay-001"',
    'CONSUMER orders GROUP order-processor 3',
    'GROUP LIST',
    'GROUP DESCRIBE order-processor',
    'OFFSETS orders order-processor'
  ].join('\n')
  output.value = []
}

function runCommands() {
  output.value = []
  const lines = input.value.split('\n').filter(l => l.trim().length > 0)
  for (const line of lines) {
    const tokens = parseLine(line)
    if (!tokens.length) continue
    const cmd = tokens[0].toUpperCase()
    output.value.push({ type: 'info', text: '$ ' + line })
    const handler = handlers[cmd]
    if (!handler) {
      output.value.push({ type: 'err', text: `unknown command '${cmd}'` })
      continue
    }
    handler(tokens.slice(1), output)
  }
}

function parseLine(line) {
  const tokens = []
  let cur = ''
  let inStr = false
  for (let i = 0; i < line.length; i++) {
    const ch = line[i]
    if (ch === '"' && !inStr) inStr = true
    else if (ch === '"' && inStr) inStr = false
    else if (ch === ' ' && !inStr) {
      if (cur.length > 0) { tokens.push(cur); cur = '' }
    } else {
      cur += ch
    }
  }
  if (cur.length > 0) tokens.push(cur)
  return tokens
}

// ===== Command handlers =====

function cmdCreateTopic(args, out) {
  if (args.length < 1) { out.push({ type: 'err', text: 'TOPIC_NAME required' }); return }
  const name = args[0]
  const partitions = parseInt(args[1]) || 1
  const replicas = parseInt(args[2]) || 1
  if (state.value.topics.has(name)) {
    out.push({ type: 'warn', text: `Topic '${name}' already exists` })
    return
  }
  state.value.topics.set(name, { partitions, replicas })
  state.value.messages.set(name, [])
  out.push({ type: 'info', text: `Created topic '${name}' with ${partitions} partition(s), replication factor ${replicas}` })
  out.push({ type: 'info', text: `  Partition assignments: brokers -> leader replicas: [1,2,3] -> [1,2,3]` })
}

function cmdListTopics(args, out) {
  out.push({ type: 'info', text: `__TOPICS__ (${state.value.topics.size}):` })
  if (state.value.topics.size === 0) {
    out.push({ type: 'info', text: '  (empty)' })
    return
  }
  for (const [name, conf] of state.value.topics) {
    const count = state.value.messages.get(name)?.length || 0
    out.push({ type: 'info', text: `  ${name}  partitions=${conf.partitions}  replicas=${conf.replicas}  messages=${count}` })
  }
}

function cmdDescribeTopic(args, out) {
  if (args.length < 1) { out.push({ type: 'err', text: 'TOPIC_NAME required' }); return }
  const name = args[0]
  const topic = state.value.topics.get(name)
  if (!topic) { out.push({ type: 'err', text: `Topic '${name}' does not exist` }); return }
  out.push({ type: 'info', text: `Topic: ${name}  Partitions: ${topic.partitions}  ReplicationFactor: ${topic.replicas}` })
  for (let p = 0; p < topic.partitions; p++) {
    const msgs = (state.value.messages.get(name) || []).filter(m => m.partition === p)
    out.push({ type: 'info', text: `  Partition: ${p}  Leader: ${(p % 3) + 1}  Replicas: [${(p % 3) + 1},${((p + 1) % 3) + 1}]  Messages: ${msgs.length}` })
  }
}

function cmdProduce(args, out) {
  if (args.length < 2) { out.push({ type: 'err', text: 'TOPIC and MESSAGE required' }); return }
  const topic = args[0]
  const value = args.slice(1).join(' ')
  if (!state.value.topics.has(topic)) {
    out.push({ type: 'warn', text: `Topic '${topic}' does not exist. Auto-creating.` })
    state.value.topics.set(topic, { partitions: 1, replicas: 1 })
    state.value.messages.set(topic, [])
  }
  const conf = state.value.topics.get(topic)
  // Hash partition: simple round-robin
  const partition = globalOffset % conf.partitions
  const offset = (state.value.messages.get(topic) || []).filter(m => m.partition === partition).length
  const msg = {
    partition,
    offset,
    key: null,
    value,
    ts: new Date().toISOString().substring(11, 19)
  }
  state.value.messages.get(topic).push(msg)
  globalOffset++
  out.push({ type: 'info', text: `Sent message to partition=${partition} offset=${offset} ts=${msg.ts}` })
}

function cmdConsumer(args, out) {
  if (args.length < 2) { out.push({ type: 'err', text: 'TOPIC and GROUP required' }); return }
  const topic = args[0]
  const group = args[1]
  const limit = parseInt(args[2]) || 10
  if (!state.value.topics.has(topic)) { out.push({ type: 'err', text: `Topic '${topic}' does not exist` }); return }
  // Get or create group
  if (!state.value.groups.has(group)) {
    const conf = state.value.topics.get(topic)
    state.value.groups.set(group, { topic, offsets: {}, assignment: {} })
    // Assign all partitions to this group
    for (let p = 0; p < conf.partitions; p++) {
      state.value.groups.get(group).assignment[p] = 0
    }
  }
  const groupData = state.value.groups.get(group)
  const msgs = state.value.messages.get(topic) || []
  const newMsgs = msgs.filter(m => m.offset >= (groupData.assignment[m.partition] || 0))
  const toShow = newMsgs.slice(0, limit)
  if (toShow.length === 0) {
    out.push({ type: 'info', text: `(consumer group ${group} on ${topic}: no new messages)` })
    return
  }
  out.push({ type: 'info', text: `__CONSUMED__ (group=${group}, topic=${topic}, limit=${limit}):` })
  for (const m of toShow) {
    out.push({ type: 'info', text: `  partition=${m.partition}  offset=${m.offset}  ts=${m.ts}  value="${m.value}"` })
    groupData.assignment[m.partition] = m.offset + 1
  }
}

function cmdGroupList(args, out) {
  out.push({ type: 'info', text: `Consumer groups (${state.value.groups.size}):` })
  for (const [name, data] of state.value.groups) {
    out.push({ type: 'info', text: `  ${name}  topic=${data.topic}  state=Stable` })
  }
}

function cmdGroupDescribe(args, out) {
  if (args.length < 1) { out.push({ type: 'err', text: 'GROUP required' }); return }
  const name = args[0]
  const data = state.value.groups.get(name)
  if (!data) { out.push({ type: 'err', text: `Group '${name}' does not exist` }); return }
  out.push({ type: 'info', text: `Group: ${name}  Topic: ${data.topic}  State: Stable` })
  out.push({ type: 'info', text: `  Members: 1 (consumer-1)` })
  out.push({ type: 'info', text: `  Assignment:` })
  for (const [partition, offset] of Object.entries(data.assignment)) {
    out.push({ type: 'info', text: `    partition=${partition}  offset=${offset}  lag=${Math.max(0, (state.value.messages.get(data.topic) || []).filter(m => m.partition === parseInt(partition)).length - offset)}` })
  }
}

function cmdOffsets(args, out) {
  if (args.length < 2) { out.push({ type: 'err', text: 'TOPIC and GROUP required' }); return }
  const topic = args[0]
  const group = args[1]
  const data = state.value.groups.get(group)
  if (!data) { out.push({ type: 'err', text: `Group '${group}' does not exist` }); return }
  out.push({ type: 'info', text: `Offsets for group=${group}, topic=${topic}:` })
  for (const [partition, offset] of Object.entries(data.assignment)) {
    out.push({ type: 'info', text: `  partition=${partition}  current-offset=${offset}` })
  }
}

const handlers = {
  'CREATE': (args, out) => {
    if (args[0]?.toUpperCase() === 'TOPIC') cmdCreateTopic(args.slice(1), out)
    else out.push({ type: 'err', text: 'unknown CREATE command' })
  },
  'LIST': (args, out) => {
    if (args[0]?.toUpperCase() === 'TOPICS') cmdListTopics(args.slice(1), out)
    else out.push({ type: 'err', text: 'unknown LIST command' })
  },
  'DESCRIBE': (args, out) => {
    if (args[0]?.toUpperCase() === 'TOPIC') cmdDescribeTopic(args.slice(1), out)
    else out.push({ type: 'err', text: 'unknown DESCRIBE command' })
  },
  'PRODUCE': cmdProduce,
  'CONSUMER': cmdConsumer,
  'GROUP': (args, out) => {
    const subCmd = args[0]?.toUpperCase()
    if (subCmd === 'LIST') cmdGroupList(args.slice(1), out)
    else if (subCmd === 'DESCRIBE') cmdGroupDescribe(args.slice(1), out)
    else out.push({ type: 'err', text: 'unknown GROUP command' })
  },
  'OFFSETS': cmdOffsets
}
</script>
