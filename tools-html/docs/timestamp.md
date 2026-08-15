---
title: 时间戳 ↔ 日期
---

# 时间戳 ↔ 日期

Unix 时间戳（秒/毫秒）与人类可读日期互转。

<script setup>
import { ref, computed, onMounted } from 'vue'

const now = ref(Date.now())
const timestamp = ref(Math.floor(Date.now() / 1000))
const unit = ref('s')
const localTzOffset = -new Date().getTimezoneOffset() / 60
const tzLabel = ref(Intl.DateTimeFormat().resolvedOptions().timeZone)

const dateInput = ref('')

onMounted(() => {
  // 同步时间
  setInterval(() => { now.value = Date.now() }, 1000)
  updateFromTimestamp()
})

function getTargetMs() {
  let v = Number(timestamp.value)
  if (isNaN(v)) return null
  if (Math.abs(v) < 1e10) v *= 1000 // 自动判断秒
  return v
}

const dateStr = computed(() => {
  const ms = getTargetMs()
  if (ms === null) return ''
  const d = new Date(ms)
  if (isNaN(d.getTime())) return ''
  return [
    d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'),
    String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0') + ':' + String(d.getSeconds()).padStart(2, '0')
  ].join(' ')
})

const isoStr = computed(() => {
  const ms = getTargetMs()
  if (ms === null) return ''
  return new Date(ms).toISOString()
})

const utcStr = computed(() => {
  const ms = getTargetMs()
  if (ms === null) return ''
  return new Date(ms).toUTCString()
})

const rfcStr = computed(() => {
  const ms = getTargetMs()
  if (ms === null) return ''
  return new Date(ms).toString()
})

function updateFromTimestamp() {
  // 时间戳变 → 触发日期联动（computed 自动跟随）
}

function applyDate() {
  if (!dateInput.value) return
  const ts = Date.parse(dateInput.value)
  if (isNaN(ts)) return
  timestamp.value = Math.floor(ts / 1000) // 默认以秒展示
}

function setNow() {
  timestamp.value = unit.value === 's' ? Math.floor(Date.now() / 1000) : Date.now()
}

function copy(text) {
  navigator.clipboard?.writeText(text)
}

function unitChange() {
  // 保持数值不超过 1e10，按当前单位切分
  const cur = Number(timestamp.value)
  if (isNaN(cur)) return
  if (unit.value === 's' && cur > 1e10) timestamp.value = Math.floor(cur / 1000)
  if (unit.value === 'ms' && Math.abs(cur) < 1e10) timestamp.value = cur * 1000
}
</script>

<ClientOnly>
<div class="tool-page">
  <div class="tool-row">
    <label>单位：</label>
    <select v-model="unit" @change="unitChange">
      <option value="s">秒</option>
      <option value="ms">毫秒</option>
    </select>
    <span class="tag">当前时区：{{ tzLabel }} (UTC{{ localTzOffset >= 0 ? '+' : '' }}{{ localTzOffset }})</span>
    <span class="spacer" style="flex:1"></span>
    <span class="muted">现在: {{ new Date(now).toLocaleString() }}</span>
  </div>

  <div class="tool-pane">
    <div class="pane">
      <header>
        <span class="label">Unix 时间戳 ({{ unit }})</span>
        <button class="tool-btn ghost" @click="setNow">现在</button>
      </header>
      <textarea v-model="timestamp" spellcheck="false" style="min-height:100px;"></textarea>
    </div>
    <div class="pane">
      <header>
        <span class="label">日期时间输入</span>
        <button class="tool-btn ghost" @click="dateInput = new Date(Number(timestamp) * (unit === 's' && Math.abs(Number(timestamp)) < 1e10 ? 1000 : 1)).toISOString().slice(0, 19) && applyDate()">应用</button>
      </header>
      <textarea v-model="dateInput" spellcheck="false" style="min-height:100px;"
        placeholder="如：2024-01-01 12:00:00 / 2024-01-01T12:00:00Z"></textarea>
    </div>
  </div>

  <h3 style="margin-top:24px;">转换结果</h3>
  <div class="tool-row">
    <label class="muted" style="min-width:120px;">本地时间：</label>
    <code>{{ dateStr || '—' }}</code>
    <button class="tool-btn ghost" @click="copy(dateStr)">复制</button>
  </div>
  <div class="tool-row">
    <label class="muted" style="min-width:120px;">ISO 8601：</label>
    <code>{{ isoStr || '—' }}</code>
    <button class="tool-btn ghost" @click="copy(isoStr)">复制</button>
  </div>
  <div class="tool-row">
    <label class="muted" style="min-width:120px;">UTC：</label>
    <code>{{ utcStr || '—' }}</code>
    <button class="tool-btn ghost" @click="copy(utcStr)">复制</button>
  </div>
  <div class="tool-row">
    <label class="muted" style="min-width:120px;">RFC 2822：</label>
    <code>{{ rfcStr || '—' }}</code>
    <button class="tool-btn ghost" @click="copy(rfcStr)">复制</button>
  </div>

  <p class="muted" style="margin-top:12px;font-size:12px;">
    时间戳输入支持自动判断（绝对值 ≥ 1e10 按毫秒处理，否则按秒处理）。
  </p>
</div>
</ClientOnly>
