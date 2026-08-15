<template>
  <div class="rf-container">
    <div class="rf-header">
      <h4 style="margin: 0">🌊 请求链路：{{ currentDemo.title }}</h4>
      <select v-model="active" class="cp-input" style="width: auto; padding: 4px 8px">
        <option v-for="(d, i) in demos" :key="i" :value="i">{{ d.title }}</option>
      </select>
    </div>
    <p style="font-size: 13px; color: var(--vp-c-text-2); margin: 0 0 12px 0">{{ currentDemo.desc }}</p>

    <div class="rf-scenario">
      <div
        v-for="(step, i) in state"
        :key="i"
        :class="['rf-step', { 'rf-step--active': step.status === 'running', 'rf-step--error': step.status === 'error', 'rf-step--done': step.status === 'done' }]"
      >
        <div class="rf-step__num">{{ i + 1 }}</div>
        <div class="rf-step__body">
          <div class="rf-step__name">{{ step.name }}</div>
          <div class="rf-step__desc">{{ step.desc }}</div>
        </div>
        <div v-if="step.time" class="rf-step__time">{{ step.time }}ms</div>
      </div>
    </div>

    <div class="rf-actions">
      <button class="rf-btn" @click="step" :disabled="finished || running">{{ running ? '处理中...' : '▶ 下一步' }}</button>
      <button class="rf-btn" @click="reset">🔄 重置</button>
      <button class="rf-btn" @click="runAll" :disabled="running || finished">⏩ 一键演示</button>
    </div>

    <div class="rf-explain">
      <strong>💡 解读：</strong>
      <p v-for="(line, i) in currentExplain" :key="i">{{ line }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const demos = [
  {
    title: '微服务请求全链路',
    desc: '用户请求 → Gateway → 鉴权 → 限流 → 业务服务 → 数据库',
    steps: [
      { name: '客户端请求', desc: 'GET /api/order/list', status: 'done' },
      { name: 'Gateway 路由匹配', desc: 'Path=/api/** 匹配 order_route', status: 'pending' },
      { name: 'Gateway 限流', desc: 'Sentinel 限流检查（100 QPS）', status: 'pending' },
      { name: 'Gateway 鉴权', desc: '从 Authorization 头解析 JWT，验证签名', status: 'pending' },
      { name: '负载均衡', desc: '从 Nacos 拉取 order-service 实例列表，选择目标', status: 'pending' },
      { name: '业务服务', desc: 'order-service 接收请求，处理业务逻辑', status: 'pending' },
      { name: '数据库访问', desc: 'MyBatis-Plus 查询 MySQL（走 master/slave）', status: 'pending' },
      { name: '链路追踪', desc: 'Sleuth 生成 traceId，写入日志', status: 'pending' },
      { name: '响应返回', desc: '结果通过 Gateway 返回客户端', status: 'pending' }
    ],
    explain: [
      '✅ Gateway 是所有请求的统一入口（南北流量）',
      '✅ 限流保护下游不被流量打垮',
      '✅ JWT 鉴权在网关层统一做，下游服务信任网关',
      '✅ 负载均衡从 Nacos 拉取实例列表（实时变化）',
      '✅ 链路 traceId 贯穿全链路，便于排查问题'
    ]
  },
  {
    title: '服务注册与发现',
    desc: '应用启动 → 注册到 Nacos → 其他服务发现',
    steps: [
      { name: '应用启动', desc: 'order-service 启动，读取配置', status: 'pending' },
      { name: '读取 Nacos 地址', desc: '从 application.yml 读取 Nacos Server 地址', status: 'pending' },
      { name: '健康检查', desc: '向 Nacos 发送健康检查 URL（默认 /actuator/health）', status: 'pending' },
      { name: '发送注册请求', desc: 'POST /nacos/v1/ns/instance，包含 IP/Port/Metadata', status: 'pending' },
      { name: '心跳维持', desc: '每 5 秒发送一次心跳，证明存活', status: 'pending' },
      { name: '健康检查失败', desc: '15 秒没收到心跳 → 实例标记为不健康', status: 'pending' },
      { name: '从 Nacos 剔除', desc: '从服务列表中删除', status: 'pending' }
    ],
    explain: [
      '✅ Spring Cloud Alibaba 集成 Nacos Discovery 自动注册',
      '✅ 心跳机制保证实例状态实时性',
      '✅ 不健康实例自动从负载均衡中剔除',
      '✅ 客户端缓存 + 定时拉取，减少 Nacos 压力'
    ]
  },
  {
    title: 'JWT 鉴权全流程',
    desc: '用户登录 → 获取 token → 携带 token 访问资源',
    steps: [
      { name: '用户登录', desc: 'POST /auth/login 提交 username/password', status: 'pending' },
      { name: '认证服务验证', desc: 'Auth Center 验证密码（BCrypt）', status: 'pending' },
      { name: '生成 JWT', desc: '用私钥签名生成 JWT（含 userId, roles, exp）', status: 'pending' },
      { name: '返回 token', desc: 'JWT 返回给客户端', status: 'pending' },
      { name: '客户端存储', desc: '前端存到 localStorage 或 Cookie', status: 'pending' },
      { name: '携带 token 访问', desc: 'Authorization: Bearer <token>', status: 'pending' },
      { name: 'Gateway 验证', desc: '解析 token，验证签名和有效期', status: 'pending' },
      { name: '传递 userId', desc: '把 userId 放到请求头传给下游', status: 'pending' },
      { name: '下游服务使用', desc: '从请求头获取 userId 处理业务', status: 'pending' }
    ],
    explain: [
      '✅ JWT 自包含，Auth Center 无状态（无需 Session）',
      '✅ Gateway 统一验证，下游服务信任 Gateway',
      '✅ token 有效期通常 30 分钟，可配 refresh_token',
      '⚠️ 私钥必须严格保密（泄露=系统沦陷）',
      '⚠️ 必须用 HTTPS 传输（防 token 被窃取）'
    ]
  }
]

const active = ref(0)
const stepIdx = ref(0)
const running = ref(false)
const state = ref([])

const finished = computed(() => stepIdx.value >= currentDemo.value.steps.length)
const currentDemo = computed(() => demos[active.value])
const currentExplain = computed(() => currentDemo.value.explain)

function statusText(s) {
  const map = { pending: '待执行', running: '执行中', done: '已完成', error: '异常' }
  return map[s] || s
}

function reset() {
  stepIdx.value = 0
  state.value = currentDemo.value.steps.map(s => ({ ...s, status: 'pending' }))
  state.value[0].status = 'done'  // 第一个步骤默认已完成
}

async function step() {
  if (finished.value) return
  const s = state.value[stepIdx.value]
  const start = Date.now()
  s.status = 'running'
  await new Promise(r => setTimeout(r, 300 + Math.random() * 200))
  s.time = Date.now() - start
  s.status = 'done'
  stepIdx.value++
  if (stepIdx.value < state.value.length) {
    // 不预先激活下一步
  }
}

async function runAll() {
  running.value = true
  reset()
  while (!finished.value) {
    await step()
    await new Promise(r => setTimeout(r, 100))
  }
  running.value = false
}

watch(active, reset)
watch(currentDemo, reset, { immediate: true })
</script>

<style scoped>
.cp-input { padding: 4px 8px; }
</style>