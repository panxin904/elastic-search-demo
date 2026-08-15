<template>
  <div class="cp-container">
    <h4 style="margin-top: 0">⚙️ Spring Cloud 配置模拟器</h4>
    <p style="font-size: 13px; color: var(--vp-c-text-2); margin: 0 0 12px 0">
      调整参数，查看生成的 application.yml 和效果
    </p>

    <div class="cp-grid">
      <div class="cp-panel">
        <h4>📝 基础配置</h4>
        <label class="cp-label">应用名称</label>
        <input v-model="appName" class="cp-input" placeholder="应用名" />

        <label class="cp-label">端口</label>
        <input v-model.number="port" type="number" class="cp-input" />

        <label class="cp-label">环境</label>
        <select v-model="env" class="cp-input">
          <option value="dev">dev（开发）</option>
          <option value="test">test（测试）</option>
          <option value="prod">prod（生产）</option>
        </select>
      </div>

      <div class="cp-panel">
        <h4>☁️ Nacos 配置</h4>
        <label class="cp-label">Nacos 地址</label>
        <input v-model="nacosAddr" class="cp-input" placeholder="127.0.0.1:8848" />

        <label class="cp-label">命名空间</label>
        <select v-model="namespace" class="cp-input">
          <option value="public">public（默认）</option>
          <option value="dev">dev</option>
          <option value="test">test</option>
          <option value="prod">prod</option>
        </select>

        <label class="cp-label">是否开启配置中心</label>
        <input v-model="enableConfig" type="checkbox" /> 开启
      </div>
    </div>

    <h4 style="margin: 16px 0 8px 0">📄 生成的 application.yml</h4>
    <pre class="cp-output">{{ generatedYaml }}</pre>

    <h4 style="margin: 16px 0 8px 0">💡 配置说明</h4>
    <div class="cp-explain">{{ explain }}</div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const appName = ref('order-service')
const port = ref(8081)
const env = ref('dev')
const nacosAddr = ref('127.0.0.1:8848')
const namespace = ref('public')
const enableConfig = ref(true)

const generatedYaml = computed(() => {
  let yaml = `spring:
  application:
    name: ${appName.value}
  profiles:
    active: ${env.value}
  cloud:
    nacos:
      discovery:
        server-addr: ${nacosAddr.value}
        namespace: ${namespace.value}
        group: DEFAULT_GROUP
`
  if (enableConfig.value) {
    yaml += `      config:
        server-addr: ${nacosAddr.value}
        namespace: ${namespace.value}
        file-extension: yaml
        refresh-enabled: true
`
  }
  yaml += `server:
  port: ${port.value}

# 日志
logging:
  level:
    root: info
    com.example: debug
`
  return yaml
})

const explain = computed(() => {
  const lines = []
  lines.push(`1. spring.application.name: 服务名（注册到 Nacos 的唯一标识）`)
  lines.push(`2. spring.profiles.active: 激活环境（对应 application-{env}.yml）`)
  lines.push(`3. nacos.discovery.server-addr: Nacos 服务端地址（生产环境建议集群）`)
  lines.push(`4. nacos.namespace: 命名空间，隔离不同环境（dev/test/prod）`)
  lines.push(`5. nacos.config.refresh-enabled: 配置变更自动刷新（需要 @RefreshScope）`)
  lines.push(`6. server.port: 服务端口（集群内必须唯一）`)
  if (env.value === 'prod') {
    lines.push(`\n⚠️ 生产环境建议：`)
    lines.push(`   - 关闭配置刷新（用 MQ 通知代替）`)
    lines.push(`   - Nacos 集群（3 节点以上）`)
    lines.push(`   - 配置加密（敏感信息加密）`)
  }
  return lines.join('\n')
})
</script>

<style scoped>
</style>