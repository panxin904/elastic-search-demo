---
title: JSON Diff
---

# JSON Diff

对比两个 JSON 的差异并以行级方式展示。

<script setup>
import { ref, computed } from 'vue'

const left = ref(`{\n  "name": "alice",\n  "age": 30,\n  "city": "Beijing"\n}`)
const right = ref(`{\n  "name": "alice",\n  "age": 31,\n  "country": "China"\n}`)
const leftParsed = ref(null)
const rightParsed = ref(null)
const status = ref({ kind: 'muted', text: '' })

function parseSide(side) {
  try {
    const parsed = JSON.parse(side)
    if (side === 'left') leftParsed.value = parsed
    else rightParsed.value = parsed
  } catch (e) {
    if (side === 'left') leftParsed.value = null
    else rightParsed.value = null
    status.value = { kind: 'error', text: `${side} 解析失败: ${e.message}` }
    return
  }
  status.value = { kind: 'ok', text: '✓ 解析完成' }
}

// 扁平化 JSON 为 key path → primitive
function flatten(obj, prefix = '') {
  const out = {}
  if (obj === null) { out[prefix || '∅'] = 'null'; return out }
  if (typeof obj !== 'object') {
    out[prefix || '∅'] = JSON.stringify(obj)
    return out
  }
  if (Array.isArray(obj)) {
    if (obj.length === 0) { out[prefix] = '[]'; return out }
    obj.forEach((v, i) => {
      Object.assign(out, flatten(v, `${prefix}[${i}]`))
    })
    return out
  }
  const keys = Object.keys(obj)
  if (keys.length === 0) { out[prefix] = '{}'; return out }
  keys.forEach(k => {
    const path = prefix ? `${prefix}.${k}` : k
    Object.assign(out, flatten(obj[k], path))
  })
  return out
}

const diff = computed(() => {
  // 仅当两侧都已解析
  if (leftParsed.value === null || rightParsed.value === null) return []
  const l = flatten(leftParsed.value)
  const r = flatten(rightParsed.value)
  const keys = new Set([...Object.keys(l), ...Object.keys(r)])
  const rows = [...keys].sort().map(k => {
    if (l[k] === undefined) return { key: k, kind: 'add', l: '', r: r[k] }
    if (r[k] === undefined) return { key: k, kind: 'del', l: l[k], r: '' }
    if (l[k] !== r[k]) return { key: k, kind: 'mod', l: l[k], r: r[k] }
    return { key: k, kind: 'eq', l: l[k], r: r[k] }
  })
  return rows
})

function runBoth() { parseSide('left'); parseSide('right') }
function copy(text) {
  if (!text) return
  navigator.clipboard?.writeText(text)
}
</script>

<ClientOnly>
<div class="tool-page">
  <div class="tool-actions">
    <button class="tool-btn" @click="runBoth">解析两份 JSON</button>
    <span class="spacer"></span>
    <span class="muted" v-if="status.text" :class="status.kind">{{ status.text }}</span>
  </div>
  <div class="tool-pane">
    <div class="pane">
      <header><span class="label">左（原始）</span></header>
      <textarea v-model="left" spellcheck="false"></textarea>
    </div>
    <div class="pane">
      <header><span class="label">右（修改后）</span></header>
      <textarea v-model="right" spellcheck="false"></textarea>
    </div>
  </div>

  <h3 style="margin-top:18px;">差异</h3>
  <div class="muted" v-if="leftParsed === null || rightParsed === null">先点击"解析两份 JSON"。</div>
  <div v-else>
    <div class="muted" style="margin-bottom:8px;font-size:13px;">
      <span class="diff-eq" style="padding:2px 6px;">= 未变</span>
      <span class="diff-add" style="padding:2px 6px;margin-left:6px;">+ 新增</span>
      <span class="diff-del" style="padding:2px 6px;margin-left:6px;">− 删除</span>
      <span style="background:#fbbf2433;color:#fbbf24;padding:2px 6px;margin-left:6px;">~ 修改</span>
    </div>
    <table style="width:100%;border-collapse:collapse;font-size:13px;font-family:ui-monospace,Menlo,monospace;">
      <thead>
        <tr style="background:var(--vp-c-bg-soft);">
          <th style="text-align:left;padding:6px;">路径</th>
          <th style="text-align:left;padding:6px;">左</th>
          <th style="text-align:left;padding:6px;">右</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in diff" :key="i"
          :style="row.kind === 'add' ? 'background:rgba(16,185,129,0.10)' :
                  row.kind === 'del' ? 'background:rgba(239,68,68,0.10)' :
                  row.kind === 'mod' ? 'background:rgba(251,191,36,0.10)' : ''">
          <td style="padding:6px;border-bottom:1px solid var(--vp-c-divider);">{{ row.key }}</td>
          <td style="padding:6px;border-bottom:1px solid var(--vp-c-divider);">{{ row.l }}</td>
          <td style="padding:6px;border-bottom:1px solid var(--vp-c-divider);">{{ row.r }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
</ClientOnly>


<!-- auto-enrich:do-not-edit -->

## 实战示例

\`\`\`bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
\`\`\`

\`\`\`yaml
# TODO: 配置示例
key: value
\`\`\`

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
