---
title: 时区转换
---

# 时区转换

把一个时刻在不同时区之间互转。

<script setup>
import { ref, computed } from 'vue'

const allZones = [
  'UTC',
  'Asia/Shanghai',
  'Asia/Tokyo',
  'Asia/Seoul',
  'Asia/Singapore',
  'Asia/Hong_Kong',
  'Asia/Taipei',
  'Asia/Kolkata',
  'Asia/Dubai',
  'Europe/London',
  'Europe/Paris',
  'Europe/Berlin',
  'Europe/Moscow',
  'America/New_York',
  'America/Chicago',
  'America/Denver',
  'America/Los_Angeles',
  'America/Sao_Paulo',
  'Australia/Sydney',
  'Pacific/Auckland'
]

const sourceDate = ref(new Date().toISOString().slice(0, 19))
const sourceZone = ref(Intl.DateTimeFormat().resolvedOptions().timeZone)
const targets = ref(['UTC', 'America/New_York', 'Europe/London', 'Asia/Tokyo', 'Asia/Shanghai'])

function addTarget() {
  targets.value.push('UTC')
}
function removeTarget(i) {
  targets.value.splice(i, 1)
}

function getZoneOffsetMinutes(date, zone) {
  const fmt = new Intl.DateTimeFormat('en-US', {
    timeZone: zone,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false
  })
  const parts = fmt.formatToParts(date)
  const get = t => parseInt(parts.find(p => p.type === t).value, 10)
  let hour = get('hour')
  if (hour === 24) hour = 0
  const utc = Date.UTC(get('year'), get('month') - 1, get('day'), hour, get('minute'), get('second'))
  return Math.round((utc - date.getTime()) / 60000)
}

function fmtInZone(epoch, zone) {
  if (epoch == null) return ''
  const fmt = new Intl.DateTimeFormat('zh-CN', {
    timeZone: zone,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false,
    timeZoneName: 'short'
  })
  return fmt.format(epoch)
}

function utcIsoStr(epoch) {
  if (epoch == null) return ''
  return new Date(epoch).toISOString()
}

const sourceEpoch = computed(() => {
  const m = sourceDate.value.match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?/)
  if (!m) return null
  const [, y, mo, d, h, mi, s = '00'] = m
  const dt = new Date(Date.UTC(+y, +mo - 1, +d, +h, +mi, +s))
  if (isNaN(dt.getTime())) return null
  const offsetMin = getZoneOffsetMinutes(dt, sourceZone.value)
  return dt.getTime() - offsetMin * 60_000
})

const summaryText = computed(() => {
  if (sourceEpoch.value == null) return '无法解析输入'
  const lines = [
    `Epoch (ms): ${sourceEpoch.value}`,
    `UTC ISO: ${utcIsoStr(sourceEpoch.value)}`,
    `源区 (${sourceZone.value}): ${fmtInZone(sourceEpoch.value, sourceZone.value)}`
  ]
  targets.value.forEach(z => {
    lines.push(`${z.padEnd(22)}: ${fmtInZone(sourceEpoch.value, z)}`)
  })
  return lines.join('\n')
})

function setNowInLocal() {
  const z = Intl.DateTimeFormat().resolvedOptions().timeZone
  sourceZone.value = z
  const fmt = new Intl.DateTimeFormat('en-CA', {
    timeZone: z,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
  })
  const parts = fmt.formatToParts(new Date())
  const g = t => parts.find(p => p.type === t).value
  sourceDate.value = `${g('year')}-${g('month')}-${g('day')} ${g('hour')}:${g('minute')}:${g('second')}`
}

function copy(text) {
  if (!text) return
  navigator.clipboard?.writeText(text)
}
</script>

<ClientOnly>
<div class="tool-page">
  <div class="tool-row">
    <button class="tool-btn ghost" @click="setNowInLocal">使用本地当前时间</button>
    <span class="muted">解析输入视为该时区的本地时间（无时区标记时）。</span>
  </div>

  <div class="tool-pane">
    <div class="pane">
      <header><span class="label">源时间 + 时区</span></header>
      <textarea v-model="sourceDate" spellcheck="false" style="min-height:140px;"
        placeholder="2024-01-15 08:30:00"></textarea>
      <div class="tool-row">
        <label class="muted">源时区：</label>
        <select v-model="sourceZone" style="flex:1;max-width:280px;">
          <option v-for="z in allZones" :key="z" :value="z">{{ z }}</option>
        </select>
      </div>
    </div>
    <div class="pane">
      <header><span class="label">转换结果</span></header>
      <textarea :value="summaryText" readonly style="min-height:200px;font-family:ui-monospace,Menlo,Consolas,monospace;"></textarea>
    </div>
  </div>

  <h3 style="margin-top:18px;">目标时区列表</h3>
  <div v-for="(z, i) in targets" :key="i" class="tool-row">
    <label class="muted">{{ i + 1 }}.</label>
    <select v-model="targets[i]" style="flex:1;max-width:280px;">
      <option v-for="zz in allZones" :key="zz" :value="zz">{{ zz }}</option>
    </select>
    <code style="min-width:280px;font-size:12px;">{{ fmtInZone(sourceEpoch, z) }}</code>
    <button class="tool-btn ghost" @click="copy(fmtInZone(sourceEpoch, z))">复制</button>
    <button class="tool-btn ghost" @click="removeTarget(i)">删除</button>
  </div>
  <div class="tool-actions">
    <button class="tool-btn secondary" @click="addTarget">+ 添加目标时区</button>
    <button class="tool-btn ghost" @click="copy(summaryText)">复制全部结果</button>
  </div>

  <p class="muted" style="margin-top:12px;font-size:12px;">
    通过 <code>Intl.DateTimeFormat</code> 计算时区偏移，支持含夏令时的 IANA 时区。
  </p>
</div>
</ClientOnly>
