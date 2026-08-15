---
title: UUID 生成
---

# UUID 生成

生成 v1 / v4 / v7 风格的 UUID，支持批量。

<script setup>
import { ref } from 'vue'

const version = ref('v4')
const count = ref(5)
const upper = ref(false)
const list = ref([])
const status = ref('')

function uuidv4() {
  if (crypto.randomUUID) return crypto.randomUUID()
  // 后备
  const b = crypto.getRandomValues(new Uint8Array(16))
  b[6] = (b[6] & 0x0f) | 0x40
  b[8] = (b[8] & 0x3f) | 0x80
  const h = [...b].map(x => x.toString(16).padStart(2, '0'))
  return `${h.slice(0,4).join('')}-${h.slice(4,6).join('')}-${h.slice(6,8).join('')}-${h.slice(8,10).join('')}-${h.slice(10,16).join('')}`
}

function uuidv7() {
  // 48-bit unix ms + 80 bits random，按 RFC 草案
  const b = new Uint8Array(16)
  crypto.getRandomValues(b)
  const ms = BigInt(Date.now())
  b[0] = Number((ms >> 40n) & 0xffn)
  b[1] = Number((ms >> 32n) & 0xffn)
  b[2] = Number((ms >> 24n) & 0xffn)
  b[3] = Number((ms >> 16n) & 0xffn)
  b[4] = Number((ms >> 8n) & 0xffn)
  b[5] = Number(ms & 0xffn)
  b[6] = (b[6] & 0x0f) | 0x70 // version v7
  b[8] = (b[8] & 0x3f) | 0x80 // variant
  const h = [...b].map(x => x.toString(16).padStart(2, '0'))
  return `${h.slice(0,4).join('')}-${h.slice(4,6).join('')}-${h.slice(6,8).join('')}-${h.slice(8,10).join('')}-${h.slice(10,16).join('')}`
}

function uuidv1() {
  // 简版 v1（time_low/time_mid/time_hi + clock_seq + node），节点用随机
  const b = new Uint8Array(16)
  crypto.getRandomValues(b)
  const ms = Date.now()
  // 时间戳 split：time_low 32, time_mid 16, time_hi 12
  const tl = ms & 0xffffffff
  const tm = (ms / 0x100000000) & 0xffff
  const th = (ms / 0x1000000000000) & 0xfff
  b[0] = (tl >>> 24) & 0xff
  b[1] = (tl >>> 16) & 0xff
  b[2] = (tl >>> 8) & 0xff
  b[3] = tl & 0xff
  b[4] = (tm >>> 8) & 0xff
  b[5] = tm & 0xff
  b[6] = ((th >>> 8) & 0x0f) | 0x10
  b[7] = th & 0xff
  b[8] = (b[8] & 0x3f) | 0x80
  // node = b[10..15]（随机）
  const h = [...b].map(x => x.toString(16).padStart(2, '0'))
  return `${h.slice(0,4).join('')}-${h.slice(4,6).join('')}-${h.slice(6,8).join('')}-${h.slice(8,10).join('')}-${h.slice(10,16).join('')}`
}

function generate() {
  const n = Math.max(1, Math.min(1000, Number(count.value) || 1))
  const out = []
  for (let i = 0; i < n; i++) {
    let id
    if (version.value === 'v4') id = uuidv4()
    else if (version.value === 'v7') id = uuidv7()
    else id = uuidv1()
    if (upper.value) id = id.toUpperCase()
    out.push(id)
  }
  list.value = out
  status.value = `✓ 已生成 ${n} 个 UUID`
}

function copyAll() {
  if (!list.value.length) return
  navigator.clipboard?.writeText(list.value.join('\n'))
  status.value = '✓ 已复制全部'
}

function copyOne(idx) {
  navigator.clipboard?.writeText(list.value[idx])
  status.value = `✓ 已复制第 ${idx + 1} 个`
}
</script>

<ClientOnly>
<div class="tool-page">
  <div class="tool-row">
    <label class="muted">版本：</label>
    <select v-model="version">
      <option value="v4">v4 (随机)</option>
      <option value="v7">v7 (时间排序)</option>
      <option value="v1">v1 (时间+MAC)</option>
    </select>
    <label class="muted">数量：</label>
    <input type="number" v-model.number="count" min="1" max="1000" style="width:100px;" />
    <label class="muted">大写：</label>
    <input type="checkbox" v-model="upper" />
  </div>
  <div class="tool-actions">
    <button class="tool-btn" @click="generate">生成</button>
    <button class="tool-btn ghost" @click="copyAll" :disabled="!list.length">复制全部</button>
    <span class="muted" v-if="status">{{ status }}</span>
  </div>

  <h3 style="margin-top:18px;">结果</h3>
  <div v-if="!list.length" class="muted">生成结果将出现在这里。</div>
  <ul v-else style="list-style:none;padding:0;font-family:ui-monospace,Menlo,monospace;font-size:13px;">
    <li v-for="(id, i) in list" :key="i"
        style="display:flex;gap:8px;align-items:center;padding:6px 4px;border-bottom:1px solid var(--vp-c-divider);">
      <span class="muted" style="min-width:40px;">{{ i + 1 }}.</span>
      <code>{{ id }}</code>
      <button class="tool-btn ghost" @click="copyOne(i)">复制</button>
    </li>
  </ul>
</div>
</ClientOnly>
