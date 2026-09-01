---
title: 外部链接中转
---

# 🔗 外部链接中转

<script setup>
import { useRoute, useRouter } from 'vitepress'
import { ref, onMounted } from 'vue'

const route = useRoute()
const router = useRouter()
const targetUrl = ref('')
const hostname = ref('')
const isBlocked = ref(false)
const isInternal = ref(false)

const BLOCKLIST = [
  'malicious-site.com',
  'phishing-example.com',
]

onMounted(() => {
  const url = route.query.url as string
  if (!url) {
    router.push('/')
    return
  }
  try {
    const parsed = new URL(url, window.location.origin)
    if (parsed.hostname === window.location.hostname || parsed.hostname === 'java-px.bot.cd') {
      // 内部链接直接跳转
      window.location.href = url
      return
    }
    if (BLOCKLIST.some(d => parsed.hostname.includes(d))) {
      isBlocked.value = true
    }
    targetUrl.value = url
    hostname.value = parsed.hostname
  } catch (e) {
    router.push('/')
  }
})

function go() {
  if (!isBlocked.value && targetUrl.value) {
    window.location.href = targetUrl.value
  }
}
</script>

<div v-if="targetUrl" class="go-container">
  <div class="go-icon">⚠️</div>
  <h1>您即将离开本站</h1>
  <p>本站点不隶属于以下网站，请谨慎核实其真实性：</p>
  
  <div class="go-target">
    <strong>{{ hostname }}</strong>
    <code class="go-url">{{ targetUrl }}</code>
  </div>
  
  <div v-if="isBlocked" class="go-blocked">
    🚫 该域名已被加入拦截列表，不建议访问
  </div>
  
  <div class="go-actions">
    <button v-if="!isBlocked" @click="go" class="btn-primary">
      继续访问 →
    </button>
    <a href="/" class="btn-secondary">
      返回本站
    </a>
  </div>
  
  <p class="go-tip">
    💡 出于安全考虑，建议在新标签页打开外部链接（按住 Ctrl/Cmd 点击）
  </p>
</div>

<div v-else class="go-loading">
  <p>正在跳转...</p>
</div>

<style scoped>
.go-container {
  max-width: 640px;
  margin: 64px auto;
  padding: 32px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  text-align: center;
}
.go-icon {
  font-size: 64px;
  margin-bottom: 16px;
}
h1 {
  font-size: 24px;
  margin: 16px 0;
}
.go-target {
  margin: 24px 0;
  padding: 16px;
  background: var(--vp-c-bg);
  border-radius: 8px;
}
.go-target strong {
  display: block;
  font-size: 18px;
  margin-bottom: 8px;
  color: var(--vp-c-brand);
}
.go-url {
  display: block;
  font-size: 13px;
  color: var(--vp-c-text-3);
  word-break: break-all;
}
.go-blocked {
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border-radius: 8px;
  margin: 16px 0;
}
.go-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin: 24px 0 16px;
}
.btn-primary, .btn-secondary {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
  border: none;
}
.btn-primary {
  background: var(--vp-c-brand);
  color: white;
}
.btn-primary:hover {
  background: var(--vp-c-brand-dark);
}
.btn-secondary {
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  border: 1px solid var(--vp-c-divider);
}
.go-tip {
  font-size: 13px;
  color: var(--vp-c-text-3);
  margin-top: 16px;
}
.go-loading {
  text-align: center;
  padding: 64px;
}
</style>
