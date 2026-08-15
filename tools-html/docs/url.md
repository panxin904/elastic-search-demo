---
title: URL 编解码
---

# URL 编解码

URL / URI 组件编码、解码，以及查询字符串解析。

<script setup>
import { ref, computed } from 'vue'

const input = ref('https://example.com/search?q=你好 世界&page=2&sort=desc')
const direction = ref('encode')
const safeMode = ref('component') // 'component' | 'uri'
const status = ref({ kind: 'muted', text: '' })
const output = ref('')

const params = computed(() => {
  // 总是从 input 解码为对象；只对 component 模式有意义
  try {
    let raw = input.value
    if (raw.includes('?')) raw = raw.split('?').slice(1).join('?')
    if (raw.startsWith('?')) raw = raw.slice(1)
    if (!raw.includes('=')) return []
    return raw.split('&').map(pair => {
      const i = pair.indexOf('=')
      const k = i === -1 ? pair : pair.slice(0, i)
      const v = i === -1 ? '' : pair.slice(i + 1)
      return { key: tryDecode(k), value: tryDecode(v) }
    })
  } catch {
    return []
  }
})

function tryDecode(s) {
  try { return decodeURIComponent(s.replace(/\+/g, ' ')) } catch { return s }
}

function go() {
  if (direction.value === 'encode') {
    try {
      const fn = safeMode.value === 'component' ? encodeURIComponent : encodeURI
      output.value = fn(input.value)
      status.value = { kind: 'ok', text: '✓ 编码成功' }
    } catch (e) {
      status.value = { kind: 'error', text: `✗ 编码失败: ${e.message}` }
      output.value = ''
    }
  } else {
    try {
      const fn = safeMode.value === 'component' ? decodeURIComponent : decodeURI
      output.value = fn(input.value)
      status.value = { kind: 'ok', text: '✓ 解码成功' }
    } catch (e) {
      status.value = { kind: 'error', text: `✗ 解码失败: ${e.message}` }
      output.value = ''
    }
  }
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
      <option value="encode">编码</option>
      <option value="decode">解码</option>
    </select>
    <label class="muted">模式：</label>
    <select v-model="safeMode">
      <option value="component">component (编码 :/？等特殊字符)</option>
      <option value="uri">uri (只转义非保留字符)</option>
    </select>
    <button class="tool-btn" @click="go">运行</button>
    <span class="spacer"></span>
    <button class="tool-btn ghost" @click="copy" :disabled="!output">复制</button>
    <button class="tool-btn ghost" @click="clearAll">清空</button>
  </div>
  <div class="tool-pane">
    <div class="pane">
      <header><span class="label">输入</span></header>
      <textarea v-model="input" spellcheck="false"></textarea>
    </div>
    <div class="pane">
      <header><span class="label">输出</span></header>
      <textarea v-model="output" readonly></textarea>
    </div>
  </div>
  <div class="tool-status" :class="status.kind">{{ status.text }}</div>

  <h3 style="margin-top:18px;">查询字符串解析（自动）</h3>
  <div v-if="params.length">
    <table style="width:100%;border-collapse:collapse;font-size:13px;">
      <thead>
        <tr><th style="text-align:left;padding:6px;border-bottom:1px solid #ccc;">Key</th><th style="text-align:left;padding:6px;border-bottom:1px solid #ccc;">Value</th></tr>
      </thead>
      <tbody>
        <tr v-for="(p, i) in params" :key="i">
          <td style="padding:6px;border-bottom:1px solid #eee;font-family:ui-monospace,Menlo,monospace;">{{ p.key }}</td>
          <td style="padding:6px;border-bottom:1px solid #eee;font-family:ui-monospace,Menlo,monospace;">{{ p.value }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div v-else class="muted">输入 URL 或查询字符串以解析键值对。</div>
</div>
</ClientOnly>
