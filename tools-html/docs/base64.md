---
title: Base64 编解码
---

# Base64 编解码

字符串与 Base64 互转，支持 UTF-8（中文）。

<script setup>
import { ref } from 'vue'

const input = ref('你好，世界！Hello, World!')
const direction = ref('encode')
const status = ref({ kind: 'muted', text: '' })
const output = ref('')

function go() {
  try {
    if (direction.value === 'encode') {
      // 处理 UTF-8：先把字符串转为 UTF-8 字节再 btoa
      const bytes = new TextEncoder().encode(input.value)
      let bin = ''
      for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i])
      output.value = btoa(bin)
      status.value = { kind: 'ok', text: '✓ 编码成功' }
    } else {
      const bin = atob(input.value.trim())
      const bytes = new Uint8Array(bin.length)
      for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
      output.value = new TextDecoder('utf-8').decode(bytes)
      status.value = { kind: 'ok', text: '✓ 解码成功' }
    }
  } catch (e) {
    status.value = { kind: 'error', text: `✗ 失败: ${e.message}` }
    output.value = ''
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
      <option value="encode">编码 → Base64</option>
      <option value="decode">Base64 → 解码</option>
    </select>
    <button class="tool-btn" @click="go">运行</button>
    <span class="spacer"></span>
    <button class="tool-btn ghost" @click="copy" :disabled="!output">复制</button>
    <button class="tool-btn ghost" @click="clearAll">清空</button>
  </div>
  <div class="tool-pane">
    <div class="pane">
      <header><span class="label">输入（{{ direction === 'encode' ? '字符串' : 'Base64' }}）</span></header>
      <textarea v-model="input" spellcheck="false"></textarea>
    </div>
    <div class="pane">
      <header><span class="label">输出（{{ direction === 'encode' ? 'Base64' : '字符串' }}）</span></header>
      <textarea v-model="output" readonly></textarea>
    </div>
  </div>
  <div class="tool-status" :class="status.kind">{{ status.text }}</div>
  <p class="muted" style="margin-top:8px;font-size:12px;">
    使用 <code>TextEncoder / TextDecoder</code> 处理 UTF-8 字节，确保中文字符正确编解码。
  </p>
</div>
</ClientOnly>
