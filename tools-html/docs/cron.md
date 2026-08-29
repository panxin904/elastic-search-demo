---
title: Cron 表达式
---

# Cron 表达式

解析 5/6 字段 Cron 表达式，描述字段含义，并列出接下来 5 次运行时间。

<script setup>
import { ref, computed } from 'vue'

const expr = ref('0 */2 * * *')
const status = ref({ kind: 'muted', text: '' })

// 解析为 6 字段（缺少年份则补 *）
const fields = computed(() => {
  const parts = expr.value.trim().split(/\s+/)
  if (parts.length === 5) parts.push('*')
  if (parts.length !== 6) {
    status.value = { kind: 'error', text: `✗ Cron 应有 5 或 6 个字段（当前 ${parts.length}）` }
    return null
  }
  return {
    minute: parts[0],
    hour: parts[1],
    dayOfMonth: parts[2],
    month: parts[3],
    dayOfWeek: parts[4],
    year: parts[5]
  }
})

// 单个字段展开为值集合
function expand(field, min, max) {
  if (field === '*') return new Set([...Array(max - min + 1).keys()].map(i => i + min))
  if (field.includes(',')) {
    const s = new Set()
    field.split(',').forEach(p => { expand(p, min, max).forEach(v => s.add(v)) })
    return s
  }
  // 步长
  const stepMatch = field.match(/^(\*|\d+)\/(\d+)$/)
  if (stepMatch) {
    const start = stepMatch[1] === '*' ? min : parseInt(stepMatch[1], 10)
    const step = parseInt(stepMatch[2], 10)
    const s = new Set()
    for (let v = start; v <= max; v += step) s.add(v)
    return s
  }
  // 范围
  const rangeMatch = field.match(/^(\d+)-(\d+)(?:\/(\d+))?$/)
  if (rangeMatch) {
    const lo = parseInt(rangeMatch[1], 10)
    const hi = parseInt(rangeMatch[2], 10)
    const step = rangeMatch[3] ? parseInt(rangeMatch[3], 10) : 1
    const s = new Set()
    for (let v = lo; v <= hi; v += step) s.add(v)
    return s
  }
  // 单值
  const single = parseInt(field, 10)
  if (!isNaN(single) && single >= min && single <= max) return new Set([single])
  return new Set()
}

// 计算下一次触发
function nextRun(f, after) {
  const minutes = expand(f.minute, 0, 59)
  const hours = expand(f.hour, 0, 23)
  const days = expand(f.dayOfMonth, 1, 31)
  const months = expand(f.month, 1, 12)
  const dows = expand(f.dayOfWeek, 0, 6) // 0 = Sunday

  const d = new Date(after.getTime())
  // 每分钟最多循环 24 * 366 * 60 ≈ 528K 次，循环最多约 5 次。
  for (let i = 0; i < 24 * 366 * 60; i++) {
    d.setMinutes(d.getMinutes() + 1)
    d.setSeconds(0, 0)
    if (!months.has(d.getMonth() + 1)) continue
    if (!days.has(d.getDate())) continue
    // dayOfWeek 语义：原始 cron 是 0=Sunday；如果同时指定 dom 和 dow，多数实现取 OR
    // 这里采用 OR 语义（更宽松）
    const domStar = f.dayOfMonth === '*'
    const dowStar = f.dayOfWeek === '*'
    if (!domStar && !dowStar) {
      if (!(days.has(d.getDate()) || dows.has(d.getDay()))) continue
    } else if (!domStar) {
      if (!days.has(d.getDate())) continue
    } else if (!dowStar) {
      if (!dows.has(d.getDay())) continue
    }
    if (!hours.has(d.getHours())) continue
    if (!minutes.has(d.getMinutes())) continue
    return new Date(d.getTime())
  }
  return null
}

const nextRuns = computed(() => {
  if (!fields.value) return []
  const f = fields.value
  const runs = []
  let cur = new Date()
  for (let i = 0; i < 5; i++) {
    const r = nextRun(f, cur)
    if (!r) break
    runs.push(r)
    cur = r
  }
  return runs
})

const humanDesc = computed(() => {
  if (!fields.value) return ''
  const f = fields.value
  const fmt = field => {
    if (field === '*') return '每'
    if (field.includes('/')) {
      const m = field.match(/^\*\/(\d+)$/)
      if (m) return `每 ${m[1]}`
      const m2 = field.match(/^(\d+)-(\d+)\/(\d+)$/)
      if (m2) return `${m2[1]}-${m2[2]} 范围内每 ${m2[3]}`
      return `步长 ${field}`
    }
    if (field.includes(',')) return field.split(',').join(' / ')
    if (field.includes('-')) {
      const m = field.match(/^(\d+)-(\d+)$/)
      if (m) return `${m[1]} 到 ${m[2]}`
      return field
    }
    return `第 ${field}`
  }
  return [
    `在 ${fmt(f.minute)} 分钟，`,
    `${fmt(f.hour)} 小时，`,
    `${fmt(f.dayOfMonth)} 日，`,
    `第 ${fmt(f.month)} 月，`,
    `星期 ${fmt(f.dayOfWeek)}，`,
    f.year === '*' ? '' : `${f.year} 年`
  ].filter(Boolean).join('')
})

function update() {
  if (!fields.value) return
  status.value = { kind: 'ok', text: '✓ 解析成功' }
}

function fmtRun(d) {
  if (!d) return '—'
  return d.toLocaleString('zh-CN', { hour12: false })
}

function copy(text) {
  if (!text) return
  navigator.clipboard?.writeText(text)
}
</script>

<ClientOnly>
<div class="tool-page">
  <div class="tool-row">
    <label class="muted" style="min-width:120px;">Cron 表达式：</label>
    <input type="text" v-model="expr" @input="update" style="flex:1;min-width:280px;" />
    <button class="tool-btn" @click="update">解析</button>
  </div>
  <div class="tool-status" :class="status.kind">{{ status.text }}</div>

  <h3 style="margin-top:18px;">字段说明</h3>
  <div v-if="fields" class="tool-pane" style="grid-template-columns:repeat(3,1fr);">
    <div class="pane"><header><span class="label">分钟 (0-59)</span></header><textarea :value="fields.minute" readonly style="min-height:60px;"></textarea></div>
    <div class="pane"><header><span class="label">小时 (0-23)</span></header><textarea :value="fields.hour" readonly style="min-height:60px;"></textarea></div>
    <div class="pane"><header><span class="label">日 (1-31)</span></header><textarea :value="fields.dayOfMonth" readonly style="min-height:60px;"></textarea></div>
    <div class="pane"><header><span class="label">月 (1-12)</span></header><textarea :value="fields.month" readonly style="min-height:60px;"></textarea></div>
    <div class="pane"><header><span class="label">星期 (0-6)</span></header><textarea :value="fields.dayOfWeek" readonly style="min-height:60px;"></textarea></div>
    <div class="pane"><header><span class="label">年份</span></header><textarea :value="fields.year" readonly style="min-height:60px;"></textarea></div>
  </div>

  <h3 style="margin-top:18px;">描述</h3>
  <div class="tool-pane">
    <div class="pane">
      <header><span class="label">自然语言</span></header>
      <textarea :value="humanDesc" readonly style="min-height:80px;"></textarea>
    </div>
    <div class="pane">
      <header><span class="label">接下来 5 次运行</span></header>
      <textarea :value="nextRuns.map(fmtRun).join('\n')" readonly style="min-height:80px;"></textarea>
    </div>
  </div>

  <div class="tool-actions">
    <button class="tool-btn ghost" @click="copy(nextRuns.map(fmtRun).join('\n'))">复制运行时间</button>
    <button class="tool-btn ghost" @click="copy(humanDesc)">复制描述</button>
  </div>

  <p class="muted" style="margin-top:12px;font-size:12px;">
    5 字段会被自动补 <code>*</code> 作为年份。星期 0=周日。当同时指定日和星期时，多数实现取 OR 语义。
  </p>
</div>
</ClientOnly>


<!-- auto-enrich:do-not-edit -->

## 实战示例

```bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
```

```yaml
# TODO: 配置示例
key: value
```

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
