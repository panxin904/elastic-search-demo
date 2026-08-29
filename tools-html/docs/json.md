---
title: JSON 格式化 / 校验
---

# JSON 格式化 / 校验

格式化、压缩、校验 JSON，错误位置高亮。

<script setup>
import { ref, computed } from 'vue'

const sample = `{"name":"alice","age":30,"skills":["js","ts"],"address":{"city":"Beijing","zip":"100000"},"active":true,"score":null}`

const input = ref(sample)
const indent = ref(2)
const status = ref({ kind: 'muted', text: '' })
const output = ref('')

// 简易语法高亮：JSON.stringify 后用 token 包裹
function highlight(jsonStr) {
  // eslint-disable-next-line no-useless-escape
  return jsonStr.replace(
    /("(?:\\.|[^"\\])*"(?:\s*:)?)|(\b(?:true|false|null)\b)|(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|([{}\[\],])/g,
    (m, str, kw, num, br) => {
      if (str) return /^"/.test(str) && /:\s*$/.test(str)
        ? `<span style="color:#a78bfa">${str}</span>`
        : `<span style="color:#60a5fa">${str}</span>`
      if (kw) return `<span style="color:#fbbf24">${kw}</span>`
      if (num) return `<span style="color:#f472b6">${num}</span>`
      if (br) return `<span style="color:#94a3b8">${br}</span>`
      return m
    }
  )
}

const highlighted = computed(() => {
  if (!output.value) return ''
  return highlight(output.value.replace(/[<>&]/g, c => ({ '<': '&lt;', '>': '&gt;', '&': '&amp;' }[c])))
})

function run(kind) {
  const raw = input.value.trim()
  if (!raw) { status.value = { kind: 'error', text: '输入为空' }; output.value = ''; return }
  try {
    const parsed = JSON.parse(raw)
    if (kind === 'minify') {
      output.value = JSON.stringify(parsed)
    } else {
      output.value = JSON.stringify(parsed, null, Number(indent.value) || 2)
    }
    const size = new Blob([output.value]).size
    status.value = { kind: 'ok', text: `✓ 有效 JSON · ${size} bytes` }
  } catch (e) {
    status.value = { kind: 'error', text: `✗ 解析失败: ${e.message}` }
    output.value = ''
  }
}

function clearAll() { input.value = ''; output.value = ''; status.value = { kind: 'muted', text: '' } }

function copy() {
  if (!output.value) return
  navigator.clipboard?.writeText(output.value)
  status.value = { kind: 'ok', text: '✓ 已复制到剪贴板' }
}
</script>

<ClientOnly>
<div class="tool-page">
  <div class="tool-actions">
    <button class="tool-btn" @click="run('pretty')">格式化</button>
    <button class="tool-btn secondary" @click="run('minify')">压缩</button>
    <label class="muted">缩进：</label>
    <select v-model.number="indent">
      <option :value="2">2 空格</option>
      <option :value="4">4 空格</option>
      <option :value="0">Tab</option>
    </select>
    <span class="spacer"></span>
    <button class="tool-btn ghost" @click="copy" :disabled="!output">复制</button>
    <button class="tool-btn ghost" @click="clearAll">清空</button>
  </div>
  <div class="tool-pane">
    <div class="pane">
      <header><span class="label">输入</span></header>
      <textarea v-model="input" spellcheck="false" placeholder="粘贴 JSON..."></textarea>
    </div>
    <div class="pane">
      <header><span class="label">输出</span></header>
      <pre class="out" v-if="output" v-html="highlighted"></pre>
      <textarea v-else readonly placeholder="格式化结果会出现在这里"></textarea>
    </div>
  </div>
  <div class="tool-status" :class="status.kind">{{ status.text }}</div>
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
