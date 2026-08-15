<template>
  <div class="perf-calc">
    <div class="pc-tabs">
      <button
        v-for="t in tabs"
        :key="t.key"
        :class="['pc-tab', { 'pc-tab--active': active === t.key }]"
        @click="active = t.key"
      >
        {{ t.label }}
      </button>
    </div>

    <!-- B+Tree 树高度计算 -->
    <div v-if="active === 'btree'" class="pc-panel">
      <h4>🌳 B+Tree 树高度计算</h4>
      <p class="pc-desc">根据数据量和扇出（fanout）估算 B+Tree 索引树的高度</p>
      <div class="perf-calc__input-row">
        <label>总数据量 (rows):</label>
        <input v-model.number="rows" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__input-row">
        <label>叶子节点每页记录数 (fanout_leaf):</label>
        <input v-model.number="fanoutLeaf" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__input-row">
        <label>非叶子节点 fanout:</label>
        <input v-model.number="fanoutInternal" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__result" v-if="btreeResult">
        {{ btreeResult }}
      </div>
    </div>

    <!-- 索引大小估算 -->
    <div v-if="active === 'indexsize'" class="pc-panel">
      <h4>💾 索引大小估算</h4>
      <p class="pc-desc">根据数据量估算 B+Tree 索引占用的磁盘空间</p>
      <div class="perf-calc__input-row">
        <label>总行数:</label>
        <input v-model.number="idxRows" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__input-row">
        <label>索引字段平均字节数 (B):</label>
        <input v-model.number="idxKeyBytes" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__input-row">
        <label>主键字节数 (B):</label>
        <input v-model.number="pkBytes" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__input-row">
        <label>页大小 (KB):</label>
        <input v-model.number="pageSize" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__result" v-if="idxSizeResult">
        {{ idxSizeResult }}
      </div>
    </div>

    <!-- InnoDB Buffer Pool 估算 -->
    <div v-if="active === 'bufferpool'" class="pc-panel">
      <h4>🧠 InnoDB Buffer Pool 估算</h4>
      <p class="pc-desc">推荐 Buffer Pool 大小（一般设为物理内存的 60-80%）</p>
      <div class="perf-calc__input-row">
        <label>服务器物理内存 (GB):</label>
        <input v-model.number="serverMem" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__input-row">
        <label>数据库总大小 (GB):</label>
        <input v-model.number="dbSize" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__result" v-if="bpResult">
        {{ bpResult }}
      </div>
    </div>

    <!-- QPS / TPS 容量估算 -->
    <div v-if="active === 'qps'" class="pc-panel">
      <h4>📊 InnoDB QPS/TPS 容量估算</h4>
      <p class="pc-desc">根据磁盘 IOPS 估算最大 QPS 容量</p>
      <div class="perf-calc__input-row">
        <label>磁盘 IOPS (随机写):</label>
        <input v-model.number="diskIops" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__input-row">
        <label>平均每个事务磁盘读 (次):</label>
        <input v-model.number="readsPerTx" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__input-row">
        <label>平均每个事务磁盘写 (次):</label>
        <input v-model.number="writesPerTx" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__input-row">
        <label>Buffer Pool 命中率 (%):</label>
        <input v-model.number="bpHitRate" type="number" class="perf-calc__input" />
      </div>
      <div class="perf-calc__result" v-if="qpsResult">
        {{ qpsResult }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const tabs = [
  { key: 'btree', label: '🌳 B+Tree 高度' },
  { key: 'indexsize', label: '💾 索引大小' },
  { key: 'bufferpool', label: '🧠 Buffer Pool' },
  { key: 'qps', label: '📊 QPS 容量' }
]
const active = ref('btree')

// B+Tree 计算
const rows = ref(10000000)
const fanoutLeaf = ref(200)
const fanoutInternal = ref(100)

const btreeResult = computed(() => {
  if (!rows.value || !fanoutLeaf.value || !fanoutInternal.value) return null
  // 叶子节点数 = rows / fanout_leaf
  // 非叶子节点 = ceil(leaves / fanout_internal)
  // 树高度 = 根到叶子的层级数
  const leaves = Math.ceil(rows.value / fanoutLeaf.value)
  let internal = Math.ceil(leaves / fanoutInternal.value)
  let height = 2 // 根 + 叶子
  while (internal > fanoutInternal.value) {
    internal = Math.ceil(internal / fanoutInternal.value)
    height++
  }
  const totalNodes = leaves + Math.ceil(leaves / fanoutInternal.value) * (height - 1)
  return [
    `📊 数据量: ${rows.value.toLocaleString()} 行`,
    `🌿 叶子节点数: ${leaves.toLocaleString()}`,
    `📏 B+Tree 树高度: ${height} 层（${height - 1} 层非叶子 + 1 层叶子）`,
    `📦 总节点数: ${totalNodes.toLocaleString()}`,
    `💡 解读:`,
    height <= 3
      ? '   ✅ 树很矮！即使 1 亿行也只需 3 次磁盘 IO，索引效率极高'
      : height <= 4
      ? '   ⚠️ 树高度 4，单次查询最多 4 次 IO，可接受但建议优化'
      : '   ❌ 树太高！建议：①增加 fanout ②减小主键宽度 ③考虑分库分表'
  ].join('\n')
})

// 索引大小估算
const idxRows = ref(10000000)
const idxKeyBytes = ref(20)
const pkBytes = ref(8)
const pageSize = ref(16)

const idxSizeResult = computed(() => {
  if (!idxRows.value) return null
  const pageSizeBytes = pageSize.value * 1024
  // 每条索引项大小 = 主键 + 索引字段 + 子节点指针(4B) + 事务ID等开销
  const perEntry = pkBytes.value + idxKeyBytes.value + 4 + 13
  const entriesPerPage = Math.floor(pageSizeBytes / perEntry)
  const totalPages = Math.ceil(idxRows.value / entriesPerPage)
  const totalBytes = totalPages * pageSizeBytes
  const totalMB = (totalBytes / 1024 / 1024).toFixed(2)
  const totalGB = (totalBytes / 1024 / 1024 / 1024).toFixed(2)

  return [
    `📊 总行数: ${idxRows.value.toLocaleString()}`,
    `📏 每页记录数: ${entriesPerPage}`,
    `📄 总页数: ${totalPages.toLocaleString()}`,
    `💾 索引大小: ${totalMB} MB (${totalGB} GB)`,
    `💡 解读:`,
    idxRows.value < 10000000
      ? '   ✅ 索引大小可控，全部放内存即可获得最佳性能'
      : idxRows.value < 100000000
      ? '   ⚠️ 大索引需要关注 innodb_buffer_pool_size 配置'
      : '   ❌ 索引极大，建议：①前缀索引 ②覆盖索引 ③分库分表'
  ].join('\n')
})

// Buffer Pool 估算
const serverMem = ref(32)
const dbSize = ref(100)

const bpResult = computed(() => {
  if (!serverMem.value) return null
  const recommended = Math.round(serverMem.value * 0.7)
  const ratio = (recommended / dbSize.value * 100).toFixed(0)
  return [
    `🖥️ 服务器内存: ${serverMem.value} GB`,
    `📊 数据库大小: ${dbSize.value} GB`,
    `✅ 推荐 Buffer Pool: ${recommended} GB（内存的 70%）`,
    `📈 缓存覆盖率: ${ratio}%（${dbSize.value > recommended ? '⚠️ 部分数据需要磁盘 IO' : '✅ 全部可缓存'}）`,
    ``,
    `💡 推荐配置（my.cnf）:`,
    `   [mysqld]`,
    `   innodb_buffer_pool_size = ${recommended}G`,
    `   innodb_buffer_pool_instances = ${Math.min(8, recommended)}`,
    `   # 建议实例数 = min(8, 内存GB数)`,
    ``,
    `⚠️ 注意：Buffer Pool 过大时建议开启大页：`,
    `   innodb_buffer_pool_chunk_size = 128M`
  ].join('\n')
})

// QPS 估算
const diskIops = ref(20000)
const readsPerTx = ref(3)
const writesPerTx = ref(1)
const bpHitRate = ref(95)

const qpsResult = computed(() => {
  if (!diskIops.value) return null
  // 实际磁盘读 = 总读 × (1 - 命中率)
  const effectiveReads = readsPerTx.value * (1 - bpHitRate.value / 100)
  const ioPerTx = effectiveReads + writesPerTx.value
  const maxQps = Math.floor(diskIops.value / ioPerTx)

  return [
    `💽 磁盘 IOPS: ${diskIops.value.toLocaleString()} (随机写)`,
    `📖 平均事务读: ${readsPerTx.value} 次（命中率 ${bpHitRate.value}%）`,
    `📝 平均事务写: ${writesPerTx.value} 次`,
    `🎯 每次事务磁盘 IO: ${ioPerTx.toFixed(2)} 次`,
    ``,
    `📊 最大 QPS 容量: ~${maxQps.toLocaleString()} ops/sec`,
    ``,
    `💡 解读:`,
    bpHitRate.value >= 95
      ? '   ✅ 缓存命中率良好，IO 主要由写事务消耗'
      : bpHitRate.value >= 80
      ? '   ⚠️ 命中率偏低，建议优化热点数据或增大 Buffer Pool'
      : '   ❌ 命中率太低！大量 IO 在读磁盘，性能瓶颈严重',
    ``,
    `🚀 提升 QPS 的方向:`,
    `   ① 提升 Buffer Pool 命中率（最有效）`,
    `   ② 用 SSD / NVMe 替代 HDD（提升 IOPS 10-100x）`,
    `   ③ 读写分离，分散主库压力`,
    `   ④ 减少大事务（避免单事务写过多行）`
  ].join('\n')
})
</script>

<style scoped>
.pc-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--vp-c-divider);
}
.pc-tab {
  padding: 8px 14px;
  background: transparent;
  border: none;
  color: var(--vp-c-text-2);
  font-size: 13px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}
.pc-tab--active {
  color: var(--mysql-blue, #00758F);
  border-bottom-color: var(--mysql-blue, #00758F);
  font-weight: 500;
}
.pc-panel h4 {
  margin: 0 0 8px 0;
}
.pc-desc {
  font-size: 13px;
  color: var(--vp-c-text-2);
  margin: 0 0 12px 0;
}
</style>