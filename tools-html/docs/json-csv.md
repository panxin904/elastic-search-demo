---
title: JSON ↔ CSV
date: 2026-08-15  # date-auto-injected
---

# JSON ↔ CSV

JSON 数组（对象数组）转换为 CSV，反之亦然。

<script setup>
import { ref } from 'vue'

const sampleJson = `[\n  {"name":"alice","age":30,"city":"Beijing"},\n  {"name":"bob","age":25,"city":"Shanghai"},\n  {"name":"carol","age":35,"city":"Beijing"}\n]`
const sampleCsv = `name,age,city\nalice,30,Beijing\nbob,25,Shanghai`

const input = ref(sampleJson)
const direction = ref('json2csv')
const delimiter = ref(',')
const status = ref({ kind: 'muted', text: '' })
const output = ref('')

// CSV 转义
function escapeCsv(value, delim) {
  if (value === null || value === undefined) return ''
  const s = String(value)
  if (/[",\n\r"]/.test(s) || s.includes(delim)) {
    return '"' + s.replace(/"/g, '""') + '"'
  }
  return s
}

function jsonToCsv(json, delim) {
  if (!Array.isArray(json)) throw new Error('JSON 顶层必须是数组')
  if (json.length === 0) return ''
  // 收集所有列（key 的并集，保序）
  const keySet = new Set()
  json.forEach(row => {
    if (typeof row !== 'object' || row === null) return
    Object.keys(row).forEach(k => keySet.add(k))
  })
  const keys = [...keySet]
  const header = keys.map(k => escapeCsv(k, delim)).join(delim)
  const rows = json.map(row => {
    if (typeof row !== 'object' || row === null) {
      return escapeCsv(typeof row === 'object' ? JSON.stringify(row) : row, delim)
    }
    return keys.map(k => {
      const v = row[k]
      if (v === null || v === undefined) return ''
      if (typeof v === 'object') return escapeCsv(JSON.stringify(v), delim)
      return escapeCsv(v, delim)
    }).join(delim)
  })
  return [header, ...rows].join('\n')
}

// 简单 CSV 解析（支持双引号转义 + 换行）
function parseCsv(text, delim) {
  const rows = []
  let row = []
  let field = ''
  let inQ = false
  for (let i = 0; i < text.length; i++) {
    const c = text[i]
    if (inQ) {
      if (c === '"') {
        if (text[i + 1] === '"') { field += '"'; i++ }
        else { inQ = false }
      } else {
        field += c
      }
    } else {
      if (c === '"') { inQ = true }
      else if (c === delim) { row.push(field); field = '' }
      else if (c === '\n') { row.push(field); rows.push(row); row = []; field = '' }
      else if (c === '\r') {/* skip */}
      else { field += c }
    }
  }
  // last
  if (field !== '' || row.length > 0) { row.push(field); rows.push(row) }
  if (rows.length === 0) return []
  const header = rows[0]
  const result = rows.slice(1).filter(r => r.some(c => c !== '')).map(r => {
    const obj = {}
    header.forEach((k, idx) => { obj[k] = r[idx] ?? '' })
    return obj
  })
  return result
}

function go() {
  try {
    if (direction.value === 'json2csv') {
      const parsed = JSON.parse(input.value)
      output.value = jsonToCsv(parsed, delimiter.value)
      status.value = { kind: 'ok', text: `✓ 共 ${Array.isArray(parsed) ? parsed.length : 0} 行` }
    } else {
      const arr = parseCsv(input.value, delimiter.value)
      output.value = JSON.stringify(arr, null, 2)
      status.value = { kind: 'ok', text: `✓ 共 ${arr.length} 行` }
    }
  } catch (e) {
    status.value = { kind: 'error', text: `✗ 失败: ${e.message}` }
    output.value = ''
  }
}

function swap() {
  const t = input.value
  input.value = output.value
  output.value = t
  direction.value = direction.value === 'json2csv' ? 'csv2json' : 'json2csv'
}

function copy() {
  if (!output.value) return
  navigator.clipboard?.writeText(output.value)
  status.value = { kind: 'ok', text: '✓ 已复制' }
}

function clearAll() { input.value = ''; output.value = ''; status.value = { kind: 'muted', text: '' } }
</script>

<ClientOnly>
<div class="tool-page">
  <div class="tool-actions">
    <select v-model="direction">
      <option value="json2csv">JSON → CSV</option>
      <option value="csv2json">CSV → JSON</option>
    </select>
    <label class="muted">分隔符：</label>
    <select v-model="delimiter">
      <option value=",">逗号 ,</option>
      <option value=";">分号 ;</option>
      <option value="\t">Tab</option>
      <option value="|">竖线 |</option>
    </select>
    <button class="tool-btn" @click="go">转换</button>
    <button class="tool-btn secondary" @click="swap">交换</button>
    <span class="spacer"></span>
    <button class="tool-btn ghost" @click="copy" :disabled="!output">复制</button>
    <button class="tool-btn ghost" @click="clearAll">清空</button>
  </div>
  <div class="tool-pane">
    <div class="pane">
      <header><span class="label">输入（{{ direction === 'json2csv' ? 'JSON' : 'CSV' }}）</span></header>
      <textarea v-model="input" spellcheck="false"></textarea>
    </div>
    <div class="pane">
      <header><span class="label">输出（{{ direction === 'json2csv' ? 'CSV' : 'JSON' }}）</span></header>
      <textarea v-model="output" readonly></textarea>
    </div>
  </div>
  <div class="tool-status" :class="status.kind">{{ status.text }}</div>
  <p class="muted" style="margin-top:8px;font-size:12px;">
    JSON 须为对象数组。CSV 解析支持双引号转义与嵌入换行。
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
