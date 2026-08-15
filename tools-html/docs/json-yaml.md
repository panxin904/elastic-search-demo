---
title: JSON ↔ YAML
---

# JSON ↔ YAML

JSON 与 YAML 互相转换。

<script setup>
import { ref, computed } from 'vue'

const sampleJson = `{\n  "service": "api",\n  "port": 8080,\n  "tags": ["prod", "v2"],\n  "db": { "host": "localhost", "user": "root" }\n}`

const input = ref(sampleJson)
const direction = ref('json2yaml')
const status = ref({ kind: 'muted', text: '' })
const output = ref('')

// 简易 YAML 序列化（足够覆盖 object/array/string/number/bool/null）
function toYaml(value, indent = 0) {
  const pad = '  '.repeat(indent)
  if (value === null) return 'null'
  if (typeof value === 'boolean') return String(value)
  if (typeof value === 'number') return String(value)
  if (typeof value === 'string') {
    // 简单规则：不强制加引号，但包含特殊字符时加双引号
    if (/[:#\-?\n"]/.test(value) || value === '' || value === 'true' || value === 'false' || value === 'null') {
      return JSON.stringify(value)
    }
    return value
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return '[]'
    return value.map(v => {
      const ser = toYaml(v, indent + 1)
      if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
        const body = ser.split('\n').map((l, i) => i === 0 ? l : pad + '  ' + l).join('\n')
        return `- ${body.replace(/^\s+/, '')}`
      }
      if (Array.isArray(v)) {
        return `- ${ser.replace(/\n/g, '\n' + pad + '  ')}`
      }
      return `- ${ser}`
    }).join('\n')
  }
  if (typeof value === 'object') {
    const keys = Object.keys(value)
    if (keys.length === 0) return '{}'
    return keys.map(k => {
      const v = value[k]
      const ser = toYaml(v, indent + 1)
      const key = /^[A-Za-z_][\w]*$/.test(k) ? k : JSON.stringify(k)
      if (v !== null && typeof v === 'object') {
        const body = ser.split('\n').map((l, i) => i === 0 ? l : pad + '  ' + l).join('\n')
        return `${key}:\n${pad}  ${body}`
      }
      return `${key}: ${ser}`
    }).join('\n')
  }
  return String(value)
}

// 简易 YAML 解析：支持缩进对象、- 列表、字符串、数字、布尔、null
function fromYaml(text) {
  const lines = text.replace(/\r\n/g, '\n').split('\n').filter(l => l.trim() !== '' && !l.trim().startsWith('#'))
  let i = 0
  function parse(indent) {
    const result = {}
    let listMode = null
    let listArr = null
    while (i < lines.length) {
      const line = lines[i]
      const ind = line.match(/^ */)[0].length
      if (ind < indent) break
      if (ind > indent) {
        // 越界，交给上层
        break
      }
      const body = line.slice(indent)
      if (body.startsWith('- ')) {
        // 列表项
        if (!listMode) {
          // 把 result 切换为 list 模式（需要外部识别）
        }
        if (!listArr) {
          listArr = []
        }
        // 把当前对象切换到 list——这里采用一种折中：如果上一层是空对象 {}，替换
        if (Object.keys(result).length === 0 && listArr.length === 0) {
          // ok
        }
        const rest = body.slice(2)
        i++
        if (rest.includes(': ') || rest.endsWith(':')) {
          // item is mapping
          const item = {}
          const key = rest.endsWith(':') ? rest.slice(0, -1) : rest.split(': ')[0]
          const v = rest.endsWith(':') ? null : rest.split(': ')[1]
          if (v === null) {
            // 子对象/列表
            const sub = parse(indent + 2)
            item[key] = sub
          } else if (v === undefined || v === '') {
            // 不存在
          } else {
            item[key] = coerce(v)
          }
          // 同一对象的后续缩进字段
          while (i < lines.length) {
            const nxt = lines[i]
            const nind = nxt.match(/^ */)[0].length
            if (nind <= indent) break
            if (nind === indent + 2 && !nxt.slice(indent + 2).startsWith('- ')) {
              const nb = nxt.slice(indent + 2)
              const ci = nb.indexOf(': ')
              if (ci === -1) continue
              const ck = nb.slice(0, ci)
              const cv = nb.slice(ci + 2)
              item[ck] = coerce(cv)
              i++
            } else {
              break
            }
          }
          listArr.push(item)
        } else {
          listArr.push(coerce(rest))
        }
      } else {
        const ci = body.indexOf(': ')
        if (ci === -1) {
          if (body.endsWith(':')) {
            const k = body.slice(0, -1)
            i++
            const sub = parse(indent + 2)
            if (listArr) {
              if (!result.__lastKey__) result.__lastKey__ = k
              // list item push
              const arr = result[result.__lastKey__] = result[result.__lastKey__] || []
              arr.push(sub)
            } else {
              result[k] = sub
            }
          } else {
            i++; break
          }
        } else {
          const k = body.slice(0, ci)
          const v = body.slice(ci + 2)
          i++
          if (v === '' || v === undefined) {
            const sub = parse(indent + 2)
            result[k] = sub
          } else {
            result[k] = coerce(v)
          }
        }
      }
    }
    return listArr || result
  }

  function coerce(s) {
    if (s === '') return ''
    if (s === 'null' || s === '~') return null
    if (s === 'true') return true
    if (s === 'false') return false
    if (/^-?\d+$/.test(s)) return parseInt(s, 10)
    if (/^-?\d+\.\d+$/.test(s)) return parseFloat(s)
    if (s.startsWith('"') && s.endsWith('"')) return s.slice(1, -1).replace(/\\"/g, '"').replace(/\\\\/g, '\\')
    if (s.startsWith("'") && s.endsWith("'")) return s.slice(1, -1).replace(/''/g, "'")
    return s
  }

  // 顶层类型识别
  // 简单地：扫描所有非空行，找最小缩进
  const minIndent = Math.min(
    ...lines.filter(l => l.trim() && !l.trim().startsWith('- ')).map(l => l.match(/^ */)[0].length)
  )
  i = 0
  const top = parse(minIndent)
  // 如果顶层只有一项 key 是 list 标识，提取
  if (top && typeof top === 'object' && !Array.isArray(top)) {
    const keys = Object.keys(top).filter(k => k !== '__lastKey__')
    if (keys.length === 1 && top.__lastKey__) {
      // list 形式被合并了
      return top[top.__lastKey__]
    }
  }
  return top
}

function doJson2Yaml() {
  try {
    const parsed = JSON.parse(input.value)
    output.value = toYaml(parsed)
    status.value = { kind: 'ok', text: '✓ JSON → YAML 成功' }
  } catch (e) {
    status.value = { kind: 'error', text: `✗ JSON 解析失败: ${e.message}` }
    output.value = ''
  }
}

function doYaml2Json() {
  try {
    const parsed = fromYaml(input.value)
    output.value = JSON.stringify(parsed, null, 2)
    status.value = { kind: 'ok', text: '✓ YAML → JSON 成功' }
  } catch (e) {
    status.value = { kind: 'error', text: `✗ YAML 解析失败: ${e.message}` }
    output.value = ''
  }
}

function go() {
  if (direction.value === 'json2yaml') doJson2Yaml()
  else doYaml2Json()
}

function swap() {
  const t = input.value
  input.value = output.value
  output.value = t
  direction.value = direction.value === 'json2yaml' ? 'yaml2json' : 'json2yaml'
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
      <option value="json2yaml">JSON → YAML</option>
      <option value="yaml2json">YAML → JSON</option>
    </select>
    <button class="tool-btn" @click="go">转换</button>
    <button class="tool-btn secondary" @click="swap">交换输入/输出</button>
    <span class="spacer"></span>
    <button class="tool-btn ghost" @click="copy" :disabled="!output">复制</button>
    <button class="tool-btn ghost" @click="clearAll">清空</button>
  </div>
  <div class="tool-pane">
    <div class="pane">
      <header><span class="label">输入（{{ direction === 'json2yaml' ? 'JSON' : 'YAML' }}）</span></header>
      <textarea v-model="input" spellcheck="false"></textarea>
    </div>
    <div class="pane">
      <header><span class="label">输出（{{ direction === 'json2yaml' ? 'YAML' : 'JSON' }}）</span></header>
      <textarea v-model="output" readonly></textarea>
    </div>
  </div>
  <div class="tool-status" :class="status.kind">{{ status.text }}</div>
  <p class="muted" style="margin-top:8px;font-size:12px;">
    简化版解析器，支持对象/列表/字符串/数字/布尔/null。复杂 YAML 特性（锚点、合并键、多行字符串）请使用专业工具。
  </p>
</div>
</ClientOnly>
