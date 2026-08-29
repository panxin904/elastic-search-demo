---
title: 相对时间
date: 2026-08-15  # date-auto-injected
---

# 相对时间

计算两个时间之间的相对时间，例如 "3 小时 25 分钟"。也支持"X 之前"/"X 之后"。

<script setup>
import { ref, computed } from 'vue'

// 默认现在
const now = ref(new Date().toISOString().slice(0, 19))
// 默认 1 小时前
const target = ref(new Date(Date.now() - 3600 * 1000).toISOString().slice(0, 19))

const diffMs = computed(() => {
  const n = Date.parse(now.value)
  const t = Date.parse(target.value)
  if (isNaN(n) || isNaN(t)) return null
  return t - n
})

const humanized = computed(() => {
  if (diffMs.value == null) return '无法解析'
  const ms = Math.abs(diffMs.value)
  const future = diffMs.value > 0
  // 内部使用中文输出
  const sec = Math.floor(ms / 1000)
  const min = Math.floor(sec / 60)
  const hour = Math.floor(min / 60)
  const day = Math.floor(hour / 24)

  const parts = []
  if (day) parts.push(`${day} 天`)
  if (hour % 24) parts.push(`${hour % 24} 小时`)
  if (min % 60) parts.push(`${min % 60} 分钟`)
  if (parts.length === 0) {
    if (sec) parts.push(`${sec} 秒`)
    else parts.push('0 秒')
  }
  const txt = parts.join(' ')
  return future ? `${txt}后` : `${txt}前`
})

const detailed = computed(() => {
  if (diffMs.value == null) return ''
  const abs = Math.abs(diffMs.value)
  return [
    `${abs} 毫秒`,
    `${Math.floor(abs / 1000)} 秒`,
    `${(abs / 1000).toFixed(3)} 秒`,
    `${Math.floor(abs / 60000)} 分钟`,
    `${(abs / 60000).toFixed(2)} 分钟`,
    `${Math.floor(abs / 3600000)} 小时`,
    `${(abs / 86400000).toFixed(2)} 天`,
    `${(abs / (86400000 * 7)).toFixed(3)} 周`,
    `${(abs / (86400000 * 30.4375)).toFixed(3)} 月（平均）`,
    `${(abs / (86400000 * 365.25)).toFixed(3)} 年（平均）`
  ].join('\n')
})

function presets(value) {
  target.value = new Date(Date.now() - value).toISOString().slice(0, 19)
}
function futurePresets(value) {
  target.value = new Date(Date.now() + value).toISOString().slice(0, 19)
}
function setNowNow() {
  now.value = new Date().toISOString().slice(0, 19)
}
function setNowTarget() {
  target.value = new Date().toISOString().slice(0, 19)
}
</script>

<ClientOnly>
<div class="tool-page">
  <div class="tool-row">
    <label class="muted" style="min-width:120px;">参考时间 (now)：</label>
    <input type="text" v-model="now" />
    <button class="tool-btn ghost" @click="setNowNow">现在</button>
  </div>
  <div class="tool-row">
    <label class="muted" style="min-width:120px;">目标时间：</label>
    <input type="text" v-model="target" />
    <button class="tool-btn ghost" @click="setNowTarget">现在</button>
  </div>

  <div class="tool-actions">
    <span class="muted">快捷预设：</span>
    <button class="tool-btn ghost" @click="presets(60_000)">1 分钟前</button>
    <button class="tool-btn ghost" @click="presets(3600_000)">1 小时前</button>
    <button class="tool-btn ghost" @click="presets(86400_000)">1 天前</button>
    <button class="tool-btn ghost" @click="presets(7 * 86400_000)">7 天前</button>
    <button class="tool-btn secondary" @click="futurePresets(3600_000)">1 小时后</button>
    <button class="tool-btn secondary" @click="futurePresets(7 * 86400_000)">7 天后</button>
  </div>

  <h3 style="margin-top:18px;">自然语言结果</h3>
  <div class="tool-pane">
    <div class="pane">
      <header><span class="label">"相对"格式</span></header>
      <textarea :value="humanized" readonly style="min-height:80px;font-size:18px;"></textarea>
    </div>
    <div class="pane">
      <header><span class="label">详细计算</span></header>
      <textarea :value="detailed" readonly style="min-height:80px;"></textarea>
    </div>
  </div>

  <p class="muted" style="margin-top:12px;font-size:12px;">
    输入 ISO 8601 字符串或能被 <code>Date</code> 解析的格式；正数 = 目标在参考之后，负数 = 之前。
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
