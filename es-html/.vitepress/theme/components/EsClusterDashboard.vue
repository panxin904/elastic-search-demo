<template>
  <div class="es-dash">
    <div class="es-dash__toolbar">
      <div class="es-dash__endpoint">
        <span class="es-dash__endpoint-label">📍</span>
        <span class="es-dash__endpoint-value">{{ endpoint }}</span>
      </div>
      <div class="es-dash__refresh-group">
        <label class="es-dash__auto">
          <input v-model="autoRefresh" type="checkbox" />
          <span>自动刷新</span>
        </label>
        <select v-if="autoRefresh" v-model.number="refreshInterval" class="es-dash__select">
          <option :value="5">5s</option>
          <option :value="15">15s</option>
          <option :value="30">30s</option>
          <option :value="60">1min</option>
        </select>
        <button class="es-dash__btn" @click="refreshAll" :disabled="loading">
          {{ loading ? '加载中...' : '↻ 刷新' }}
        </button>
        <span v-if="lastUpdated" class="es-dash__meta">
          上次更新：{{ lastUpdated }}
        </span>
      </div>
    </div>

    <div v-if="error" class="es-dash__error">
      <strong>请求失败：</strong> {{ error }}
      <div class="es-dash__error-hint">
        💡 请检查 endpoint 配置、CORS 设置（详见页面下方说明）
      </div>
    </div>

    <div v-else-if="!hasAnyData && !loading" class="es-dash__empty">
      暂无数据，请先点击「↻ 刷新」拉取数据
    </div>

    <div class="es-dash__subtabs">
      <button
        v-for="t in subTabs"
        :key="t.id"
        :class="['es-dash__subtab', { 'es-dash__subtab--active': activeSubTab === t.id }]"
        @click="activeSubTab = t.id"
      >
        {{ t.icon }} {{ t.label }}
      </button>
    </div>

    <!-- ========== 健康状态 ========== -->
    <div v-show="activeSubTab === 'health'" class="es-dash__pane">
      <div v-if="health" class="es-dash__health-grid">
        <div :class="['es-dash__status-card', `es-dash__status-card--${health.status}`]">
          <div class="es-dash__status-label">集群状态</div>
          <div class="es-dash__status-value">{{ health.status.toUpperCase() }}</div>
          <div class="es-dash__status-hint">{{ statusHint(health.status) }}</div>
        </div>

        <div class="es-dash__metric-card">
          <div class="es-dash__metric-label">节点数</div>
          <div class="es-dash__metric-value">{{ health.number_of_nodes }}</div>
          <div class="es-dash__metric-hint">含 {{ health.number_of_data_nodes }} 个数据节点</div>
        </div>

        <div class="es-dash__metric-card">
          <div class="es-dash__metric-label">活跃分片</div>
          <div class="es-dash__metric-value">{{ health.active_shards }}</div>
          <div class="es-dash__metric-hint">
            主 {{ health.active_primary_shards }} / 副 {{ activeReplicas }}
          </div>
        </div>

        <div class="es-dash__metric-card">
          <div class="es-dash__metric-label">未分配分片</div>
          <div :class="['es-dash__metric-value', health.unassigned_shards > 0 ? 'es-dash__metric-value--warn' : '']">
            {{ health.unassigned_shards }}
          </div>
          <div class="es-dash__metric-hint">
            initializing {{ health.initializing_shards }} / relocating {{ health.relocating_shards }}
          </div>
        </div>
      </div>

      <div v-if="health && health.unassigned_shards > 0" class="es-dash__warn-block">
        ⚠️ 集群存在 {{ health.unassigned_shards }} 个未分配分片
        <a href="https://www.elastic.co/guide/en/elasticsearch/reference/7.17/cluster-allocation-explain.html" target="_blank" rel="noopener">
          查看原因 →
        </a>
      </div>

      <div v-if="healthRaw" class="es-dash__raw">
        <details>
          <summary>查看原始 JSON</summary>
          <pre class="es-dash__pre">{{ formatJson(healthRaw) }}</pre>
        </details>
      </div>
    </div>

    <!-- ========== 节点指标 ========== -->
    <div v-show="activeSubTab === 'nodes'" class="es-dash__pane">
      <div v-if="nodes.length === 0 && !loading" class="es-dash__empty">
        暂无节点数据
      </div>
      <table v-else class="es-dash__table">
        <thead>
          <tr>
            <th @click="sortBy('name')">节点名 <span class="es-dash__sort">{{ sortIcon('name') }}</span></th>
            <th>角色</th>
            <th @click="sortBy('heapPercent')">Heap <span class="es-dash__sort">{{ sortIcon('heapPercent') }}</span></th>
            <th @click="sortBy('ramPercent')">RAM <span class="es-dash__sort">{{ sortIcon('ramPercent') }}</span></th>
            <th @click="sortBy('cpuPercent')">CPU <span class="es-dash__sort">{{ sortIcon('cpuPercent') }}</span></th>
            <th @click="sortBy('load1m')">Load <span class="es-dash__sort">{{ sortIcon('load1m') }}</span></th>
            <th @click="sortBy('diskPercent')">磁盘 <span class="es-dash__sort">{{ sortIcon('diskPercent') }}</span></th>
            <th>Master</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="n in sortedNodes" :key="n.name">
            <td><strong>{{ n.name }}</strong></td>
            <td><span class="es-dash__role">{{ n.roles || '-' }}</span></td>
            <td>
              <div class="es-dash__bar">
                <div
                  class="es-dash__bar-fill"
                  :class="barClass(n.heapPercent)"
                  :style="{ width: n.heapPercent + '%' }"
                ></div>
                <span class="es-dash__bar-text">{{ n.heapPercent }}%</span>
              </div>
            </td>
            <td>
              <div class="es-dash__bar">
                <div
                  class="es-dash__bar-fill"
                  :class="barClass(n.ramPercent)"
                  :style="{ width: n.ramPercent + '%' }"
                ></div>
                <span class="es-dash__bar-text">{{ n.ramPercent }}%</span>
              </div>
            </td>
            <td>{{ n.cpuPercent }}%</td>
            <td>{{ n.load1m }}</td>
            <td>
              <div class="es-dash__bar">
                <div
                  class="es-dash__bar-fill"
                  :class="barClass(n.diskPercent)"
                  :style="{ width: n.diskPercent + '%' }"
                ></div>
                <span class="es-dash__bar-text">{{ n.diskPercent }}%</span>
              </div>
            </td>
            <td>
              <span v-if="n.isMaster" class="es-dash__badge es-dash__badge--master">⭐</span>
              <span v-else>-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ========== 索引概览 ========== -->
    <div v-show="activeSubTab === 'indices'" class="es-dash__pane">
      <div class="es-dash__filter">
        <input
          v-model="indicesFilter"
          placeholder="按索引名过滤..."
          class="es-dash__filter-input"
        />
        <span class="es-dash__meta">共 {{ filteredIndices.length }} 个索引</span>
      </div>
      <table v-if="filteredIndices.length > 0" class="es-dash__table">
        <thead>
          <tr>
            <th @click="sortBy('index')">索引名 <span class="es-dash__sort">{{ sortIcon('index') }}</span></th>
            <th @click="sortBy('health')">健康 <span class="es-dash__sort">{{ sortIcon('health') }}</span></th>
            <th @click="sortBy('status')">状态 <span class="es-dash__sort">{{ sortIcon('status') }}</span></th>
            <th @click="sortBy('docsCount')">文档数 <span class="es-dash__sort">{{ sortIcon('docsCount') }}</span></th>
            <th @click="sortBy('storeSize')">存储大小 <span class="es-dash__sort">{{ sortIcon('storeSize') }}</span></th>
            <th @click="sortBy('pri')">主分片 <span class="es-dash__sort">{{ sortIcon('pri') }}</span></th>
            <th @click="sortBy('rep')">副本 <span class="es-dash__sort">{{ sortIcon('rep') }}</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="idx in sortedIndices" :key="idx.index">
            <td><strong>{{ idx.index }}</strong></td>
            <td>
              <span :class="['es-dash__pill', `es-dash__pill--${idx.health}`]">
                {{ idx.health }}
              </span>
            </td>
            <td>{{ idx.status }}</td>
            <td>{{ formatNumber(idx.docsCount) }}</td>
            <td>{{ idx.storeSize }}</td>
            <td>{{ idx.pri }}</td>
            <td>{{ idx.rep }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else-if="!loading" class="es-dash__empty">
        暂无索引数据
      </div>
    </div>

    <!-- ========== 分片分布 ========== -->
    <div v-show="activeSubTab === 'shards'" class="es-dash__pane">
      <div class="es-dash__filter">
        <input
          v-model="shardsFilter"
          placeholder="按索引名/节点过滤..."
          class="es-dash__filter-input"
        />
        <select v-model="shardsStateFilter" class="es-dash__select">
          <option value="">所有状态</option>
          <option value="STARTED">STARTED</option>
          <option value="UNASSIGNED">UNASSIGNED</option>
          <option value="INITIALIZING">INITIALIZING</option>
          <option value="RELOCATING">RELOCATING</option>
        </select>
        <span class="es-dash__meta">共 {{ filteredShards.length }} 条</span>
      </div>
      <table v-if="filteredShards.length > 0" class="es-dash__table">
        <thead>
          <tr>
            <th @click="sortBy('index')">索引 <span class="es-dash__sort">{{ sortIcon('index') }}</span></th>
            <th @click="sortBy('shard')">分片号 <span class="es-dash__sort">{{ sortIcon('shard') }}</span></th>
            <th @click="sortBy('prirep')">类型 <span class="es-dash__sort">{{ sortIcon('prirep') }}</span></th>
            <th @click="sortBy('state')">状态 <span class="es-dash__sort">{{ sortIcon('state') }}</span></th>
            <th>节点</th>
            <th>未分配原因</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(s, idx) in sortedShards" :key="idx + s.index + s.shard">
            <td>{{ s.index }}</td>
            <td>{{ s.shard }}</td>
            <td>
              <span :class="['es-dash__pill', s.prirep === 'p' ? 'es-dash__pill--primary' : 'es-dash__pill--replica']">
                {{ s.prirep === 'p' ? '主' : '副' }}
              </span>
            </td>
            <td>
              <span :class="['es-dash__pill', `es-dash__pill--${(s.state || '').toLowerCase()}`]">
                {{ s.state }}
              </span>
            </td>
            <td>{{ s.node || '—' }}</td>
            <td class="es-dash__reason">{{ s.unassignedReason || '—' }}</td>
          </tr>
        </tbody>
      </table>
      <div v-else-if="!loading" class="es-dash__empty">
        暂无分片数据
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const STORAGE_KEY = 'es-dash-config'

const subTabs = [
  { id: 'health', icon: '🏥', label: '集群健康' },
  { id: 'nodes', icon: '📈', label: '节点指标' },
  { id: 'indices', icon: '📂', label: '索引概览' },
  { id: 'shards', icon: '🧩', label: '分片分布' }
]

const endpoint = ref('http://localhost:9200')
const username = ref('')
const password = ref('')
const autoRefresh = ref(false)
const refreshInterval = ref(15)
const activeSubTab = ref('health')
const loading = ref(false)
const error = ref('')
const lastUpdated = ref('')

const health = ref(null)
const healthRaw = ref('')
const nodes = ref([])
const indices = ref([])
const shards = ref([])
const indicesFilter = ref('')
const shardsFilter = ref('')
const shardsStateFilter = ref('')

const sortKey = ref('name')
const sortDir = ref('asc')

let timer = null

function loadConfig() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const cfg = JSON.parse(raw)
    endpoint.value = cfg.endpoint || endpoint.value
    username.value = cfg.username || ''
    password.value = cfg.password || ''
  } catch (_) {}
}

function saveConfig() {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        endpoint: endpoint.value,
        username: username.value,
        password: password.value
      })
    )
  } catch (_) {}
}

const activeReplicas = computed(() =>
  health.value ? health.value.active_shards - health.value.active_primary_shards : 0
)

const hasAnyData = computed(() =>
  health.value !== null || nodes.value.length > 0 || indices.value.length > 0
)

const filteredIndices = computed(() => {
  const q = indicesFilter.value.trim().toLowerCase()
  if (!q) return indices.value
  return indices.value.filter((i) => i.index.toLowerCase().includes(q))
})

const filteredShards = computed(() => {
  const q = shardsFilter.value.trim().toLowerCase()
  let list = shards.value
  if (q) {
    list = list.filter(
      (s) =>
        (s.index || '').toLowerCase().includes(q) ||
        (s.node || '').toLowerCase().includes(q)
    )
  }
  if (shardsStateFilter.value) {
    list = list.filter((s) => s.state === shardsStateFilter.value)
  }
  return list
})

function sortBy(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function sortIcon(key) {
  if (sortKey.value !== key) return '↕'
  return sortDir.value === 'asc' ? '↑' : '↓'
}

function compare(a, b, key) {
  const av = typeof a[key] === 'number' ? a[key] : (a[key] || '').toString()
  const bv = typeof b[key] === 'number' ? b[key] : (b[key] || '').toString()
  if (av < bv) return -1
  if (av > bv) return 1
  return 0
}

const sortedNodes = computed(() => {
  const list = [...nodes.value]
  list.sort((a, b) => {
    const r = compare(a, b, sortKey.value)
    return sortDir.value === 'asc' ? r : -r
  })
  return list
})

const sortedIndices = computed(() => {
  const list = [...filteredIndices.value]
  list.sort((a, b) => {
    const r = compare(a, b, sortKey.value)
    return sortDir.value === 'asc' ? r : -r
  })
  return list
})

const sortedShards = computed(() => {
  const list = [...filteredShards.value]
  list.sort((a, b) => {
    const r = compare(a, b, sortKey.value)
    return sortDir.value === 'asc' ? r : -r
  })
  return list
})

function statusHint(status) {
  return {
    green: '所有分片正常运行',
    yellow: '主分片正常，副本缺失',
    red: '主分片缺失，数据有风险'
  }[status] || ''
}

function barClass(percent) {
  if (percent >= 85) return 'es-dash__bar-fill--critical'
  if (percent >= 70) return 'es-dash__bar-fill--warn'
  return 'es-dash__bar-fill--ok'
}

function formatNumber(n) {
  if (n == null) return '-'
  return Number(n).toLocaleString()
}

function formatJson(text) {
  try {
    return JSON.stringify(JSON.parse(text), null, 2)
  } catch (_) {
    return text
  }
}

function authHeaders() {
  const h = { 'Content-Type': 'application/json' }
  if (username.value) {
    h['Authorization'] = 'Basic ' + btoa(`${username.value}:${password.value}`)
  }
  return h
}

async function callEs(path) {
  const url = `${endpoint.value.replace(/\/+$/, '')}${path}`
  const res = await fetch(url, {
    method: 'GET',
    headers: authHeaders()
  })
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`)
  }
  return await res.json()
}

function parseCatOutput(json, columns) {
  if (Array.isArray(json)) return json
  if (typeof json === 'string') {
    return json
      .split('\n')
      .filter((line) => line.trim())
      .map((line) => {
        const parts = line.split(/\s+/)
        const row = {}
        columns.forEach((col, i) => (row[col] = parts[i]))
        return row
      })
  }
  return []
}

async function refreshHealth() {
  const json = await callEs('/_cluster/health?wait_for_status=yellow&timeout=2s')
  health.value = json
  healthRaw.value = JSON.stringify(json, null, 2)
}

async function refreshNodes() {
  const json = await callEs('/_nodes/stats?pretty')
  const masterJson = await callEs('/_cat/master?h=host&format=json').catch(() => [])
  const masters = new Set(
    Array.isArray(masterJson) ? masterJson.map((m) => m.host) : []
  )
  const list = []
  for (const [nodeId, node] of Object.entries(json.nodes || {})) {
    const jvm = node.jvm || {}
    const os = node.os || {}
    const fs = node.fs || {}
    const totalInBytes = (fs.total?.total_in_bytes) || 0
    const availableInBytes = (fs.total?.available_in_bytes) || 0
    const usedPercent = totalInBytes
      ? Math.round(((totalInBytes - availableInBytes) / totalInBytes) * 100)
      : 0
    list.push({
      name: node.name || nodeId,
      roles: (node.roles || []).map(formatRole).join('/'),
      heapPercent: jvm.mem?.heap_used_percent ?? 0,
      ramPercent: os.mem?.used_percent ?? 0,
      cpuPercent: Math.round((node.cpu?.percent || 0) * 10) / 10,
      load1m: (os.cpu?.load_average?.['1m'] ?? 0).toFixed(2),
      diskPercent: usedPercent,
      isMaster: masters.has(node.name) || nodeId.includes(masterJson[0]?.host || '___nope___')
    })
  }
  nodes.value = list
}

function formatRole(r) {
  return { master: 'M', data: 'D', ingest: 'I', voting_only: 'V', ml: 'L', coordinating: 'C' }[r] || r
}

async function refreshIndices() {
  const json = await callEs('/_cat/indices?h=index,health,status,docs.count,store.size,pri,rep&format=json&bytes=b')
  const list = Array.isArray(json) ? json : []
  indices.value = list.map((row) => ({
    index: row.index || '',
    health: row.health || 'unknown',
    status: row.status || '',
    docsCount: parseInt(row['docs.count'] || '0', 10),
    storeSize: humanBytes(parseInt(row['store.size'] || '0', 10)),
    pri: parseInt(row.pri || '0', 10),
    rep: parseInt(row.rep || '0', 10)
  }))
}

function humanBytes(b) {
  if (b < 1024) return `${b} B`
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`
  if (b < 1024 * 1024 * 1024) return `${(b / 1024 / 1024).toFixed(1)} MB`
  if (b < 1024 * 1024 * 1024 * 1024) return `${(b / 1024 / 1024 / 1024).toFixed(2)} GB`
  return `${(b / 1024 / 1024 / 1024 / 1024).toFixed(2)} TB`
}

async function refreshShards() {
  const json = await callEs('/_cat/shards?h=index,shard,prirep,state,node,unassigned.reason&format=json&v=false')
  const list = Array.isArray(json) ? json : []
  shards.value = list.map((row) => ({
    index: row.index || '',
    shard: row.shard || '',
    prirep: row.prirep || '',
    state: row.state || '',
    node: row.node || '',
    unassignedReason: row['unassigned.reason'] || ''
  }))
}

async function refreshAll() {
  loading.value = true
  error.value = ''
  try {
    saveConfig()
    const tasks = [
      refreshHealth(),
      refreshNodes(),
      refreshIndices(),
      refreshShards()
    ]
    await Promise.allSettled(tasks)
    const errors = tasks.length - arguments.length
    const results = await Promise.allSettled(tasks)
    const failures = results.filter((r) => r.status === 'rejected').map((r) => r.reason?.message)
    if (failures.length === results.length) {
      error.value = `无法访问 ES：${failures[0]}`
    } else if (failures.length > 0) {
      error.value = `部分失败：${failures.join('; ')}`
    }
    lastUpdated.value = new Date().toLocaleTimeString('zh-CN')
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

function startAutoRefresh() {
  if (timer) clearInterval(timer)
  if (autoRefresh.value && refreshInterval.value > 0) {
    timer = setInterval(refreshAll, refreshInterval.value * 1000)
  }
}

onMounted(() => {
  loadConfig()
  refreshAll()
})

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})

import { watch } from 'vue'
watch([autoRefresh, refreshInterval], () => {
  startAutoRefresh()
})
</script>

<style scoped>
.es-dash {
  margin: 16px 0;
}

.es-dash__toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-soft);
  border-radius: 8px;
  margin-bottom: 12px;
}

.es-dash__endpoint {
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 13px;
  color: var(--vp-c-text-2);
  display: flex;
  align-items: center;
  gap: 4px;
}

.es-dash__endpoint-value {
  color: var(--vp-c-text-1);
  font-weight: 600;
}

.es-dash__refresh-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.es-dash__auto {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  cursor: pointer;
  user-select: none;
}

.es-dash__select {
  padding: 4px 8px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 13px;
}

.es-dash__btn {
  padding: 6px 14px;
  border: 1px solid var(--vp-c-brand-1);
  border-radius: 4px;
  background: var(--vp-c-brand-1);
  color: white;
  font-size: 13px;
  cursor: pointer;
  font-weight: 600;
}

.es-dash__btn:hover:not(:disabled) {
  background: var(--vp-c-brand-2);
  border-color: var(--vp-c-brand-2);
}

.es-dash__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.es-dash__meta {
  font-size: 11px;
  color: var(--vp-c-text-2);
}

.es-dash__error {
  padding: 12px 16px;
  border: 1px solid #fca5a5;
  border-radius: 6px;
  background: #fef2f2;
  color: #b91c1c;
  margin-bottom: 12px;
}

.es-dash__error-hint {
  margin-top: 4px;
  font-size: 12px;
  color: #7f1d1d;
}

.es-dash__empty {
  padding: 24px;
  text-align: center;
  color: var(--vp-c-text-2);
  border: 1px dashed var(--vp-c-divider);
  border-radius: 6px;
}

.es-dash__subtabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
  padding: 8px 0;
  border-bottom: 1px dashed var(--vp-c-divider);
}

.es-dash__subtab {
  padding: 6px 12px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-2);
  border-radius: 16px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.15s;
}

.es-dash__subtab:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-text-1);
}

.es-dash__subtab--active {
  background: var(--vp-c-brand-1);
  color: white;
  border-color: var(--vp-c-brand-1);
  font-weight: 600;
}

.es-dash__pane {
  padding: 8px 0;
}

/* === 健康卡片 === */
.es-dash__health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.es-dash__status-card {
  padding: 16px;
  border-radius: 8px;
  text-align: center;
  color: white;
}

.es-dash__status-card--green {
  background: linear-gradient(135deg, #10b981, #059669);
}

.es-dash__status-card--yellow {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.es-dash__status-card--red {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.es-dash__status-label {
  font-size: 12px;
  opacity: 0.9;
}

.es-dash__status-value {
  font-size: 32px;
  font-weight: 700;
  margin: 8px 0;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
}

.es-dash__status-hint {
  font-size: 11px;
  opacity: 0.85;
}

.es-dash__metric-card {
  padding: 14px 16px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
}

.es-dash__metric-label {
  font-size: 11px;
  color: var(--vp-c-text-2);
  text-transform: uppercase;
}

.es-dash__metric-value {
  font-size: 26px;
  font-weight: 700;
  color: var(--vp-c-text-1);
  margin: 4px 0;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
}

.es-dash__metric-value--warn {
  color: #b91c1c;
}

.es-dash__metric-hint {
  font-size: 11px;
  color: var(--vp-c-text-2);
}

.es-dash__warn-block {
  padding: 10px 14px;
  border-radius: 6px;
  background: #fef3c7;
  color: #78350f;
  font-size: 13px;
  margin-bottom: 12px;
}

.es-dash__warn-block a {
  color: #78350f;
  font-weight: 600;
  margin-left: 4px;
}

.es-dash__raw {
  margin-top: 8px;
}

.es-dash__raw summary {
  cursor: pointer;
  color: var(--vp-c-brand-1);
  font-size: 12px;
  padding: 4px 0;
  user-select: none;
}

.es-dash__pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 12px;
  max-height: 400px;
  overflow: auto;
  white-space: pre-wrap;
}

/* === 节点表格 === */
.es-dash__filter {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.es-dash__filter-input {
  flex: 1;
  max-width: 300px;
  padding: 6px 10px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 13px;
}

.es-dash__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.es-dash__table th {
  text-align: left;
  padding: 8px 12px;
  border-bottom: 2px solid var(--vp-c-divider);
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-2);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

.es-dash__table td {
  padding: 8px 12px;
  border-bottom: 1px solid var(--vp-c-divider);
}

.es-dash__table tbody tr:hover {
  background: var(--vp-c-bg-mute);
}

.es-dash__sort {
  font-size: 10px;
  opacity: 0.5;
  margin-left: 2px;
}

.es-dash__role {
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 12px;
  color: var(--vp-c-text-2);
}

/* === 进度条 === */
.es-dash__bar {
  position: relative;
  width: 90px;
  height: 18px;
  background: var(--vp-c-bg-mute);
  border-radius: 4px;
  overflow: hidden;
}

.es-dash__bar-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  transition: width 0.3s;
}

.es-dash__bar-fill--ok {
  background: #10b981;
}

.es-dash__bar-fill--warn {
  background: #f59e0b;
}

.es-dash__bar-fill--critical {
  background: #ef4444;
}

.es-dash__bar-text {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10px;
  color: var(--vp-c-text-1);
  font-weight: 600;
  mix-blend-mode: difference;
  filter: invert(1);
}

/* === 徽章 === */
.es-dash__badge {
  font-size: 12px;
}

.es-dash__badge--master {
  color: #f59e0b;
}

.es-dash__pill {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-2);
}

.es-dash__pill--green {
  background: #d1fae5;
  color: #047857;
}

.es-dash__pill--yellow {
  background: #fef3c7;
  color: #b45309;
}

.es-dash__pill--red {
  background: #fee2e2;
  color: #b91c1c;
}

.es-dash__pill--unknown {
  background: #e5e7eb;
  color: #4b5563;
}

.es-dash__pill--primary {
  background: #dbeafe;
  color: #1e40af;
}

.es-dash__pill--replica {
  background: #ede9fe;
  color: #6d28d9;
}

.es-dash__pill--started {
  background: #d1fae5;
  color: #047857;
}

.es-dash__pill--unassigned {
  background: #fee2e2;
  color: #b91c1c;
}

.es-dash__pill--initializing {
  background: #dbeafe;
  color: #1e40af;
}

.es-dash__pill--relocating {
  background: #fef3c7;
  color: #b45309;
}

.es-dash__reason {
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 11px;
  color: var(--vp-c-text-2);
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 768px) {
  .es-dash__toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .es-dash__health-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .es-dash__table {
    font-size: 12px;
  }
  .es-dash__bar {
    width: 60px;
  }
}
</style>
