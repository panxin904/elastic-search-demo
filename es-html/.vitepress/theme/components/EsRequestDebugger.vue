<template>
  <div class="es-curl">
    <div class="es-curl__panel">
      <div class="es-curl__row">
        <label class="es-curl__label">服务端地址</label>
        <input
          v-model="endpoint"
          class="es-curl__input"
          placeholder="http://localhost:9200"
          @input="saveConfig"
        />
        <span class="es-curl__hint">支持 localStorage 持久化</span>
      </div>

      <div class="es-curl__row">
        <label class="es-curl__label">认证</label>
        <input
          v-model="username"
          placeholder="username"
          class="es-curl__input es-curl__input--sm"
          @input="saveConfig"
        />
        <input
          v-model="password"
          type="password"
          placeholder="password"
          class="es-curl__input es-curl__input--sm"
          @input="saveConfig"
        />
        <span class="es-curl__hint">ES 7.x 需启用 xpack.security</span>
      </div>

      <div class="es-curl__tabs es-curl__tabs--main">
        <button
          :class="['es-curl__tab', { 'es-curl__tab--active': tab === 'debug' }]"
          @click="tab = 'debug'"
        >
          🚀 请求调试
        </button>
        <button
          :class="['es-curl__tab', { 'es-curl__tab--active': tab === 'curl' }]"
          @click="tab = 'curl'"
        >
          🖥️ 等效 curl
        </button>
      </div>

      <!-- ============ 调试器 Tab ============ -->
      <div v-show="tab === 'debug'">
        <div class="es-curl__row">
          <select v-model="method" class="es-curl__select">
            <option value="GET">GET</option>
            <option value="POST">POST</option>
            <option value="PUT">PUT</option>
            <option value="DELETE">DELETE</option>
            <option value="HEAD">HEAD</option>
          </select>
          <input
            v-model="path"
            class="es-curl__input es-curl__input--path"
            placeholder="/products/_search"
          />
          <button
            class="es-curl__btn es-curl__btn--primary"
            :disabled="sending"
            @click="send"
          >
            {{ sending ? '发送中...' : '发送请求' }}
          </button>
        </div>

        <div class="es-curl__tabs es-curl__tabs--sub">
          <button
            :class="['es-curl__tab', { 'es-curl__tab--active': subTab === 'body' }]"
            @click="subTab = 'body'"
          >
            Body
          </button>
          <button
            :class="['es-curl__tab', { 'es-curl__tab--active': subTab === 'headers' }]"
            @click="subTab = 'headers'"
          >
            Headers
          </button>
        </div>

        <div v-show="subTab === 'body'" class="es-curl__editor">
          <textarea
            v-model="bodyRaw"
            class="es-curl__textarea"
            placeholder='{"query":{"match_all":{}}}'
            spellcheck="false"
          ></textarea>
          <div class="es-curl__actions">
            <button class="es-curl__btn" @click="formatBody">✨ 格式化 JSON</button>
            <button class="es-curl__btn" @click="clearBody">清空</button>
          </div>
        </div>

        <div v-show="subTab === 'headers'" class="es-curl__editor">
          <div
            v-for="key in Object.keys(headers)"
            :key="key"
            class="es-curl__header-row"
          >
            <input
              :value="key"
              @input="updateHeaderKey(key, $event.target.value)"
              placeholder="Header name"
              class="es-curl__input es-curl__input--sm"
            />
            <input
              :value="headers[key]"
              @input="updateHeaderValue(key, $event.target.value)"
              placeholder="Header value"
              class="es-curl__input"
            />
            <button
              class="es-curl__btn es-curl__btn--danger"
              @click="removeHeader(key)"
            >
              删除
            </button>
          </div>
          <button class="es-curl__btn" @click="addHeader">+ 添加 Header</button>
        </div>

        <div v-if="response || error" class="es-curl__response-block">
          <div v-if="response" class="es-curl__response">
            <div class="es-curl__response-header">
              <span :class="['es-curl__status', `es-curl__status--${responseStatusClass}`]">
                {{ response.status }} {{ response.statusText }}
              </span>
              <span class="es-curl__meta">
                {{ responseTime }} ms · {{ formatSize(responseText.length) }}
              </span>
              <button class="es-curl__btn es-curl__btn--xs" @click="clearResponse">
                关闭
              </button>
            </div>
            <pre class="es-curl__pre">{{ formatResponse(responseText) }}</pre>
          </div>

          <div v-if="error" class="es-curl__error-panel">
            <strong>请求失败：</strong>
            <pre class="es-curl__pre es-curl__pre--error">{{ error }}</pre>
            <button class="es-curl__btn es-curl__btn--xs" @click="clearResponse">
              关闭
            </button>
          </div>
        </div>

        <div v-if="!response && !error" class="es-curl__hint-block">
          💡 没有可执行 ES 服务？试试
          <button class="es-curl__btn-link" @click="loadSample('health')">健康检查</button>
        </div>
      </div>

      <!-- ============ curl Tab ============ -->
      <div v-show="tab === 'curl'" class="es-curl__editor">
        <pre class="es-curl__curl">{{ curlCommand }}</pre>
        <div class="es-curl__actions">
          <button class="es-curl__btn" @click="copyCurl">📋 复制</button>
          <span v-if="copySuccess" class="es-curl__success">已复制 ✓</span>
        </div>
        <div class="kg-note kg-note-warning">
          <strong>💡 CORS 提示：</strong>浏览器直接调用 ES 会受 CORS 限制。
          在 <code>elasticsearch.yml</code> 中添加：
          <pre>http.cors.enabled: true
http.cors.allow-origin: "*"
http.cors.allow-headers: "Authorization,Content-Type"</pre>
          如不想改 ES 配置，可复制 curl 命令到本地终端运行。
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const STORAGE_KEY = 'es-curl-config'

const endpoint = ref('http://localhost:9200')
const username = ref('')
const password = ref('')
const method = ref('GET')
const path = ref('/_cluster/health')
const bodyRaw = ref('')
const tab = ref('debug')
const subTab = ref('body')
const sending = ref(false)
const response = ref(null)
const responseText = ref('')
const error = ref('')
const copySuccess = ref(false)
const headers = ref({ 'Content-Type': 'application/json' })
const responseTime = ref(0)

function loadConfig() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const cfg = JSON.parse(raw)
    endpoint.value = cfg.endpoint || endpoint.value
    username.value = cfg.username || ''
    password.value = cfg.password || ''
  } catch (_) {}
}

function saveConfig() {
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        endpoint: endpoint.value,
        username: username.value,
        password: password.value
      })
    )
  } catch (_) {}
}

const formattedBody = computed(() => {
  if (!bodyRaw.value.trim()) return ''
  try {
    return JSON.stringify(JSON.parse(bodyRaw.value), null, 2)
  } catch (_) {
    return bodyRaw.value
  }
})

const responseStatusClass = computed(() => {
  if (!response.value) return ''
  const s = response.value.status
  if (s >= 200 && s < 300) return 'ok'
  if (s >= 300 && s < 400) return 'redirect'
  if (s >= 400 && s < 500) return 'client'
  return 'server'
})

const curlCommand = computed(() => {
  const auth = username.value
    ? `-u "${username.value}:${password.value}"`
    : ''
  const headerLines = Object.entries(headers.value)
    .filter(([_, v]) => v)
    .map(([k, v]) => `-H "${k}: ${v}"`)
    .join(' \\\n  ')
  const body = formattedBody.value
    ? `--data '${formattedBody.value.replace(/'/g, "'\\''")}'`
    : ''
  const url = `${endpoint.value.replace(/\/+$/, '')}${path.value}`
  return `curl -X ${method.value} ${auth} \\\n  ${headerLines} \\\n  ${body} \\\n  "${url}"`.trim()
})

async function send() {
  if (sending.value) return
  sending.value = true
  error.value = ''
  response.value = null
  responseText.value = ''

  const start = performance.now()
  try {
    const url = `${endpoint.value.replace(/\/+$/, '')}${path.value}`
    const options = {
      method: method.value,
      headers: { ...headers.value }
    }
    if (username.value) {
      options.headers['Authorization'] =
        'Basic ' + btoa(`${username.value}:${password.value}`)
    }
    if (['POST', 'PUT', 'DELETE'].includes(method.value) && bodyRaw.value.trim()) {
      try {
        JSON.parse(bodyRaw.value)
        options.body = bodyRaw.value
      } catch (e) {
        throw new Error('Body 不是合法 JSON：' + e.message)
      }
    }

    const res = await fetch(url, options)
    const text = await res.text()
    response.value = res
    responseText.value = text
    responseTime.value = Math.round(performance.now() - start)
  } catch (e) {
    error.value = (e && e.message) || String(e)
    responseTime.value = Math.round(performance.now() - start)
  } finally {
    sending.value = false
  }
}

function formatBody() {
  if (!bodyRaw.value.trim()) return
  try {
    bodyRaw.value = JSON.stringify(JSON.parse(bodyRaw.value), null, 2)
  } catch (e) {
    alert('JSON 解析失败：' + e.message)
  }
}

function clearBody() {
  bodyRaw.value = ''
}

function addHeader() {
  const key = `X-Custom-${Object.keys(headers.value).length + 1}`
  headers.value[key] = ''
}

function updateHeaderKey(oldKey, newKey) {
  if (!newKey || newKey === oldKey) return
  const value = headers.value[oldKey]
  delete headers.value[oldKey]
  headers.value[newKey] = value
  headers.value = { ...headers.value }
}

function updateHeaderValue(key, value) {
  headers.value[key] = value
}

function removeHeader(key) {
  delete headers.value[key]
  headers.value = { ...headers.value }
}

function clearResponse() {
  response.value = null
  responseText.value = ''
  error.value = ''
}

function loadSample(kind) {
  if (kind === 'health') {
    method.value = 'GET'
    path.value = '/_cluster/health'
    bodyRaw.value = ''
  }
  send()
}

async function copyCurl() {
  try {
    await navigator.clipboard.writeText(curlCommand.value)
    copySuccess.value = true
    setTimeout(() => (copySuccess.value = false), 1500)
  } catch (_) {}
}

function formatResponse(text) {
  if (!text) return ''
  try {
    return JSON.stringify(JSON.parse(text), null, 2)
  } catch (_) {
    return text
  }
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(2)} MB`
}

onMounted(() => {
  loadConfig()
  try {
    const raw = sessionStorage.getItem('es-prefill')
    if (raw) {
      const p = JSON.parse(raw)
      method.value = p.method || method.value
      path.value = p.path || path.value
      bodyRaw.value = p.body || bodyRaw.value
      subTab.value = 'body'
      sessionStorage.removeItem('es-prefill')
    }
  } catch (_) {}
})

defineExpose({
  loadConfig: () => {
    method.value = 'POST'
    path.value = ''
    bodyRaw.value = ''
  }
})
</script>

<style scoped>
.es-curl {
  margin: 16px 0;
}

.es-curl__panel {
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
  padding: 16px;
}

.es-curl__row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.es-curl__label {
  font-weight: 600;
  min-width: 80px;
  font-size: 14px;
  color: var(--vp-c-text-1);
}

.es-curl__input,
.es-curl__select {
  padding: 8px 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
}

.es-curl__input {
  flex: 1;
  min-width: 200px;
}

.es-curl__input--sm {
  flex: 0 1 140px;
  min-width: 100px;
}

.es-curl__input--path {
  flex: 1;
}

.es-curl__select {
  font-weight: 600;
  min-width: 100px;
}

.es-curl__hint {
  font-size: 12px;
  color: var(--vp-c-text-2);
}

.es-curl__hint-block {
  margin-top: 12px;
  padding: 12px;
  background: var(--vp-c-bg-mute);
  border-radius: 4px;
  font-size: 13px;
  color: var(--vp-c-text-2);
}

.es-curl__btn {
  padding: 8px 16px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s;
}

.es-curl__btn:hover:not(:disabled) {
  background: var(--vp-c-bg-mute);
  border-color: var(--vp-c-brand-1);
}

.es-curl__btn--primary {
  background: var(--vp-c-brand-1);
  color: white;
  border-color: var(--vp-c-brand-1);
  font-weight: 600;
}

.es-curl__btn--primary:hover:not(:disabled) {
  background: var(--vp-c-brand-2);
  border-color: var(--vp-c-brand-2);
}

.es-curl__btn--danger {
  color: #ef4444;
  border-color: #fca5a5;
}

.es-curl__btn--xs {
  padding: 2px 8px;
  font-size: 11px;
}

.es-curl__btn-link {
  background: none;
  border: none;
  color: var(--vp-c-brand-1);
  cursor: pointer;
  padding: 0 4px;
  font-size: inherit;
  text-decoration: underline;
}

.es-curl__btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.es-curl__tabs {
  display: flex;
  gap: 4px;
  border-bottom: 1px solid var(--vp-c-divider);
  margin: 16px 0 12px;
  overflow-x: auto;
}

.es-curl__tabs--main {
  border-bottom: 2px solid var(--vp-c-divider);
}

.es-curl__tabs--sub {
  border-bottom-width: 1px;
  margin-top: 8px;
}

.es-curl__tab {
  padding: 8px 16px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: var(--vp-c-text-2);
  border-bottom: 2px solid transparent;
  white-space: nowrap;
  transition: all 0.15s;
}

.es-curl__tab--active {
  color: var(--vp-c-brand-1);
  border-bottom-color: var(--vp-c-brand-1);
  font-weight: 600;
}

.es-curl__editor {
  margin-bottom: 16px;
}

.es-curl__textarea {
  width: 100%;
  min-height: 200px;
  padding: 12px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 13px;
  line-height: 1.5;
  resize: vertical;
}

.es-curl__actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.es-curl__success {
  color: #10b981;
  font-size: 12px;
}

.es-curl__header-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

.es-curl__curl {
  background: #1e293b;
  color: #e2e8f0;
  padding: 16px;
  border-radius: 6px;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.es-curl__response-block {
  margin-top: 16px;
}

.es-curl__response {
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 12px;
}

.es-curl__response-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--vp-c-bg-mute);
  border-bottom: 1px solid var(--vp-c-divider);
}

.es-curl__status {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 600;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 13px;
}

.es-curl__status--ok {
  background: #d1fae5;
  color: #047857;
}

.es-curl__status--redirect {
  background: #fef3c7;
  color: #b45309;
}

.es-curl__status--client {
  background: #fee2e2;
  color: #b91c1c;
}

.es-curl__status--server {
  background: #fecaca;
  color: #7f1d1d;
}

.es-curl__meta {
  font-size: 12px;
  color: var(--vp-c-text-2);
  flex: 1;
}

.es-curl__pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 16px;
  margin: 0;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  max-height: 500px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.es-curl__pre--error {
  background: #1f0f0f;
  color: #fca5a5;
}

.es-curl__error-panel {
  border: 1px solid #fca5a5;
  border-radius: 6px;
  background: #fef2f2;
  padding: 12px;
  margin-bottom: 12px;
  position: relative;
}

.es-curl__error-panel strong {
  color: #b91c1c;
}

.dark .es-curl__pre {
  background: #000;
}

@media (max-width: 768px) {
  .es-curl__row {
    flex-direction: column;
    align-items: stretch;
  }
  .es-curl__input,
  .es-curl__select {
    width: 100%;
  }
  .es-curl__input--sm {
    flex: 1;
  }
}
</style>
