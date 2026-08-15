<template>
  <div class="cl-container">
    <div class="cl-toolbar">
      <button class="cl-toolbar__btn" @click="simulateFailure">💥 模拟故障</button>
      <button class="cl-toolbar__btn" @click="simulateRecovery">🔧 故障恢复</button>
      <button class="cl-toolbar__btn" @click="addNode">➕ 扩容新节点</button>
      <button class="cl-toolbar__btn" @click="resetCluster">🔄 重置</button>
      <span style="margin-left:auto;font-size:12px;color:var(--vp-c-text-2);">
        Cluster: 3 主 3 从 · 16384 槽位 · Gossip 协议
      </span>
    </div>

    <div class="cl-grid">
      <div v-for="(node, idx) in nodes" :key="idx" :class="['cl-node', {
        'cl-node--master': node.role === 'master' && !node.failed,
        'cl-node--replica': node.role === 'replica' && !node.failed,
        'cl-node--fail':   node.failed
      }]">
        <div class="cl-node__title">
          {{ node.icon }} {{ node.id }}
          <small v-if="node.role === 'master'">(master)</small>
          <small v-else>(replica)</small>
        </div>
        <div class="cl-node__slots">
          IP: {{ node.ip }}
        </div>
        <div class="cl-node__slots">
          负责槽位: {{ node.slots.length > 0 ? node.slots.join(', ') : '无' }}
        </div>
        <div v-if="node.failed" style="color:#ef4444;font-weight:600;margin-top:4px;">⚠️ 故障中</div>
      </div>
    </div>

    <div style="padding:0 16px;">
      <div style="font-size:13px;font-weight:600;margin:8px 0 4px;">槽位分配（16384 个槽，每段 5461）</div>
      <div class="cl-slot-grid">
        <div
          v-for="slot in 64" :key="slot"
          :class="['cl-slot', slotClass(slot)]"
        >{{ slot - 1 }}</div>
      </div>
      <div style="font-size:11px;color:var(--vp-c-text-2);margin:8px 16px;">
        注：仅展示前 64 个槽位（0-63），实际共 16384 个槽位均匀分布在 3 个 master 上
      </div>
    </div>

    <div class="ds-info-panel">
      <div v-if="failMode === 'master'">
        <b>主节点故障处理：</b>
        <br/>① 其他 master 通过 Gossip 协议发现 M1 失联<br/>
        ② R1（replica）通过选举晋升为新的 master<br/>
        ③ 客户端路由表更新（CLUSTER SLOTS 命令）<br/>
        ④ 槽位重新由 R1 提供读写
      </div>
      <div v-else-if="failMode === 'replica'">
        <b>从节点故障处理：</b>
        <br/>① 主节点失去该 replica，心跳超时<br/>
        ② M1 复制缓冲区持续累积（repl-backlog-size）<br/>
        ③ R1 重启后发送 PSYNC 命令，从 M1 的 backlog 同步<br/>
        ④ 若 offset 已被覆盖，则全量同步（RDB + 命令重放）
      </div>
      <div v-else-if="failMode === 'recovered'">
        <b>故障恢复完成：</b>
        <br/>✅ 所有节点正常运转<br/>
        ✅ 客户端路由表已同步<br/>
        ✅ 数据不丢失（replica 已自动晋升）
      </div>
      <div v-else-if="failMode === 'reshard'">
        <b>扩容完成（reshard）：</b>
        <br/>① 新节点 M4 加入集群，分配 4096 个槽位<br/>
        ② 客户端写入 SET key val 时，通过 CRC16(key) % 16384 计算槽位<br/>
        ③ MOVED 响应返回新节点地址，客户端路由表更新<br/>
        ④ 整个过程对客户端透明
      </div>
      <div v-else>
        <b>正常状态：</b>3 主 3 从，每主 ~5461 个槽位，Gossip 协议保持节点间拓扑同步。<br/>
        点击上方按钮模拟不同场景。
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const baseNodes = [
  { id: 'M1', role: 'master',  ip: '10.0.1.1', slots: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21], failed: false },
  { id: 'R1', role: 'replica', ip: '10.0.1.2', slots: [], failed: false },
  { id: 'M2', role: 'master',  ip: '10.0.2.1', slots: [22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43], failed: false },
  { id: 'R2', role: 'replica', ip: '10.0.2.2', slots: [], failed: false },
  { id: 'M3', role: 'master',  ip: '10.0.3.1', slots: [44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63], failed: false },
  { id: 'R3', role: 'replica', ip: '10.0.3.2', slots: [], failed: false }
]

const nodes = ref(JSON.parse(JSON.stringify(baseNodes)))
const failMode = ref(null)

function slotClass(slot) {
  const s = slot - 1
  const node = nodes.value.find(n => n.role === 'master' && n.slots.includes(s))
  if (!node) return 'cl-slot--empty'
  if (node.id === 'M1') return 'cl-slot--m1'
  if (node.id === 'M2') return 'cl-slot--m2'
  if (node.id === 'M3') return 'cl-slot--m3'
  if (node.id === 'M4') return 'cl-slot--m4'
  return 'cl-slot--empty'
}

function simulateFailure() {
  resetCluster()
  const master = nodes.value.find(n => n.id === 'M2')
  if (master) master.failed = true
  failMode.value = 'master'
}

function simulateRecovery() {
  resetCluster()
  const master = nodes.value.find(n => n.id === 'M1')
  const replica = nodes.value.find(n => n.id === 'R1')
  if (master) master.failed = true
  if (replica) replica.failed = true
  failMode.value = 'recovered'
}

function addNode() {
  resetCluster()
  const newNode = { id: 'M4', role: 'master', ip: '10.0.4.1', slots: [], failed: false }
  nodes.value.push(newNode)
  failMode.value = 'reshard'
}

function resetCluster() {
  nodes.value = JSON.parse(JSON.stringify(baseNodes))
  failMode.value = null
}
</script>
