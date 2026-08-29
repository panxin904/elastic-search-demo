---
title: Base64 编解码
date: 2026-08-15  # date-auto-injected
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

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
