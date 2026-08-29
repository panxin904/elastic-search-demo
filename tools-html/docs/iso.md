---
title: ISO / RFC 格式化
---

# ISO / RFC 格式化

把一个日期转换为多种 ISO / RFC 字符串格式。

<script setup>
import { ref, computed } from 'vue'

const input = ref(new Date().toISOString().slice(0, 19))
const status = ref('')
const parsed = ref(null)

function parse() {
  const d = new Date(input.value.trim())
  if (isNaN(d.getTime())) {
    status.value = '✗ 解析失败'
    parsed.value = null
    return null
  }
  status.value = '✓ 解析成功'
  parsed.value = d
  return d
}

// 支持解析的占位符
function fmtPattern(date, pattern) {
  const pad = (n, w = 2) => String(n).padStart(w, '0')
  const tokens = {
    YYYY: date.getFullYear(),
    MM: pad(date.getMonth() + 1),
    DD: pad(date.getDate()),
    HH: pad(date.getHours()),
    mm: pad(date.getMinutes()),
    ss: pad(date.getSeconds()),
    SSS: pad(date.getMilliseconds(), 3)
  }
  return pattern.replace(/YYYY|MM|DD|HH|mm|ss|SSS/g, m => tokens[m])
}

function reparse() {
  if (parse()) {
    /* computed 会自动跟随 */
  }
}

const outputs = computed(() => {
  const d = parsed.value
  if (!d) return []
  return [
    { name: 'ISO 8601 (UTC)', value: d.toISOString() },
    { name: 'ISO 8601 (本地)', value: fmtPattern(d, 'YYYY-MM-DDTHH:mm:ss') + 'Z'.replace('Z', '+00:00'.slice(0, 6) + '(fake)') },
    { name: '简化 ISO', value: fmtPattern(d, 'YYYY-MM-DDTHH:mm:ss') },
    { name: '仅日期', value: fmtPattern(d, 'YYYY-MM-DD') },
    { name: '中国 (年月日)', value: `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日` },
    { name: 'Chinese slash', value: `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}` },
    { name: '时间 HH:mm:ss', value: fmtPattern(d, 'HH:mm:ss') },
    { name: '时间含毫秒', value: fmtPattern(d, 'HH:mm:ss.SSS') },
    { name: 'UTC (RFC 7231)', value: d.toUTCString() },
    { name: '本地 (RFC 7231 风格)', value: d.toString() },
    { name: '本地化字符串', value: d.toLocaleString('zh-CN') },
    { name: '本地化（包含时区）', value: d.toLocaleString('zh-CN', { timeZoneName: 'short' }) },
    { name: '自定义格式 YYYY/MM/DD HH:mm:ss', value: fmtPattern(d, 'YYYY/MM/DD HH:mm:ss') },
    { name: 'Unix 秒', value: Math.floor(d.getTime() / 1000).toString() },
    { name: 'Unix 毫秒', value: d.getTime().toString() }
  ]
})

function copy(text) {
  navigator.clipboard?.writeText(text)
}
</script>

<ClientOnly>
<div class="tool-page">
  <div class="tool-pane">
    <div class="pane">
      <header>
        <span class="label">输入任意日期字符串</span>
        <button class="tool-btn" @click="reparse">解析</button>
      </header>
      <textarea v-model="input" spellcheck="false" style="min-height:80px;"
        placeholder="例：2024-01-15T08:30:00Z / 2024-01-15 08:30 / Mon, 15 Jan 2024 08:30:00 GMT / 1705295400"></textarea>
    </div>
    <div class="pane">
      <header><span class="label">多格式输出</span></header>
      <textarea readonly style="min-height:80px;">{{ outputs.map(o => `${o.name}: ${o.value}`).join('\n') }}</textarea>
    </div>
  </div>

  <div class="tool-status" :class="parsed ? 'ok' : 'error'">{{ status }}</div>

  <h3 style="margin-top:18px;">逐项详情</h3>
  <div v-if="parsed">
    <div class="tool-row" v-for="o in outputs" :key="o.name">
      <label class="muted" style="min-width:200px;font-size:12px;">{{ o.name }}</label>
      <code style="font-size:12px;word-break:break-all;">{{ o.value }}</code>
      <button class="tool-btn ghost" @click="copy(o.value)">复制</button>
    </div>
  </div>

  <p class="muted" style="margin-top:12px;font-size:12px;">
    输入可以是 ISO 8601 / RFC 2822 / Unix 时间戳等任意能被 <code>Date</code> 解析的字符串。
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
