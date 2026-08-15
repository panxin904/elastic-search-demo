<template>
  <div class="topo-container">
    <div class="topo-toolbar">
      <button class="topo-toolbar__btn" @click="simulateScrape">▶ 开始爬取</button>
      <button class="topo-toolbar__btn" @click="reset">🔄 重置</button>
      <button class="topo-toolbar__btn" @click="simulateFailure">⚠️ 模拟失败</button>
      <span style="margin-left:auto;font-size:12px;color:var(--vp-c-text-2);">
        爬虫流程演示 · 5 阶段
      </span>
    </div>

    <div class="topo-grid">
      <div
        v-for="(stage, idx) in stages"
        :key="stage.name"
        :class="['topo-stage', stage.state]"
      >
        <div class="topo-stage__icon">{{ stage.icon }}</div>
        <div class="topo-stage__name">{{ stage.name }}</div>
        <div class="topo-stage__desc">{{ stage.desc }}</div>
        <div v-if="stage.state !== 'idle'" style="margin-top:6px;font-size:10px;">
          <span v-if="stage.state === 'active'" style="color:#3b82f6;">⟳ 处理中</span>
          <span v-if="stage.state === 'success'" style="color:#16a34a;">✓ 完成</span>
          <span v-if="stage.state === 'error'" style="color:#dc2626;">✗ 失败</span>
        </div>
      </div>
    </div>

    <div class="ds-info-panel" style="padding: 12px 16px; background: var(--vp-c-bg-soft); border-top: 1px solid var(--vp-c-divider); font-size: 13px; line-height: 1.7;">
      <div v-if="phase === 'idle'">
        <b>待开始：</b> 点击「开始爬取」观察 5 阶段流程：URL 队列 → HTTP 请求 → 解析 HTML → 数据提取 → 数据存储
      </div>
      <div v-else-if="phase === 'running'">
        <b>爬取中：</b> 当前阶段：<span style="color: var(--py-blue);">{{ currentStage }}</span>。流程会逐步推进，每阶段约 800ms。
      </div>
      <div v-else-if="phase === 'success'">
        <b>爬取完成：</b> 已成功爬取 100 条数据，耗时 ~4 秒。流程：URL 队列 → HTTP 请求 → 解析 HTML → 数据提取 → 数据存储
      </div>
      <div v-else-if="phase === 'failed'">
        <b>爬取失败：</b> HTTP 请求阶段遇到反爬（403 Forbidden）。生产中需加 User-Agent、代理、限速、重试等策略。
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const initialStages = [
  { name: 'URL 队列', icon: '📋', desc: '待爬取的 URL 列表', state: 'idle' },
  { name: 'HTTP 请求', icon: '🌐', desc: '发送 GET 请求获取 HTML', state: 'idle' },
  { name: '解析 HTML', icon: '🔍', desc: 'BeautifulSoup 解析 DOM', state: 'idle' },
  { name: '数据提取', icon: '📦', desc: '提取目标字段（标题、价格）', state: 'idle' },
  { name: '数据存储', icon: '💾', desc: '入库或保存为 JSON/CSV', state: 'idle' }
]

const stages = ref(JSON.parse(JSON.stringify(initialStages)))
const phase = ref('idle')
const currentStage = ref('')
let timers = []

function clearTimers() {
  timers.forEach(t => clearTimeout(t))
  timers = []
}

function reset() {
  clearTimers()
  stages.value = JSON.parse(JSON.stringify(initialStages))
  phase.value = 'idle'
  currentStage.value = ''
}

function simulateScrape() {
  reset()
  phase.value = 'running'

  const stageNames = ['URL 队列', 'HTTP 请求', '解析 HTML', '数据提取', '数据存储']

  stageNames.forEach((name, idx) => {
    timers.push(setTimeout(() => {
      // 标记前一阶段为完成
      if (idx > 0) {
        stages.value[idx - 1].state = 'success'
      }
      // 当前阶段为活跃
      stages.value[idx].state = 'active'
      currentStage.value = name
    }, idx * 800))

    // 标记当前阶段完成
    timers.push(setTimeout(() => {
      stages.value[idx].state = 'success'
      if (idx === stageNames.length - 1) {
        phase.value = 'success'
      }
    }, (idx + 1) * 800))
  })
}

function simulateFailure() {
  reset()
  phase.value = 'failed'
  stages.value[0].state = 'success'
  stages.value[1].state = 'error'
  currentStage.value = 'HTTP 请求'
}
</script>
