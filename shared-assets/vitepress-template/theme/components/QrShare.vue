<script setup lang="ts">
/**
 * QrShare.vue — 二维码分享（C7·§8.81 P1-5）
 *
 * 扫码可以在手机上继续阅读当前页面
 *
 * 用法（在 .md 末尾）：
 *   <ClientOnly>
 *     <QrShare />
 *   </ClientOnly>
 *
 * 实现：使用 api.qrserver.com 在线 QR API（零依赖）
 */
import { ref, computed } from 'vue'

const pageUrl = ref('')
const showQr = ref(false)

if (typeof window !== 'undefined') {
  pageUrl.value = window.location.href
}

const qrSrc = computed(() => {
  if (!pageUrl.value) return ''
  // qrserver.com 免费 API，零依赖
  return `https://api.qrserver.com/v1/create-qr-code/?size=200x200&margin=2&data=${encodeURIComponent(pageUrl.value)}`
})

function toggle() {
  showQr.value = !showQr.value
}
</script>

<template>
  <div class="at-qr-share">
    <button @click="toggle" class="at-qr-btn" :aria-expanded="showQr">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="7" height="7"></rect>
        <rect x="14" y="3" width="7" height="7"></rect>
        <rect x="14" y="14" width="7" height="7"></rect>
        <path d="M3 14 h7 v7"></path>
      </svg>
      <span>{{ showQr ? '隐藏二维码' : '扫码在手机上继续阅读' }}</span>
    </button>
    
    <Transition name="qr">
      <div v-if="showQr" class="at-qr-panel">
        <img :src="qrSrc" :alt="`QR code for ${pageUrl}`" width="200" height="200" />
        <p class="at-qr-tip">用手机相机扫描上方二维码<br>即可在移动端继续阅读本文</p>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.at-qr-share {
  margin: 24px 0 0;
  padding: 16px;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
}
.at-qr-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  font-size: 13px;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.15s;
}
.at-qr-btn:hover {
  background: var(--vp-c-brand-soft);
  border-color: var(--vp-c-brand);
  color: var(--vp-c-brand);
}
.at-qr-panel {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.at-qr-panel img {
  border-radius: 6px;
  background: white;
  padding: 4px;
  border: 1px solid var(--vp-c-divider);
}
.at-qr-tip {
  margin: 0;
  font-size: 12px;
  color: var(--vp-c-text-3);
  text-align: center;
  line-height: 1.5;
}
.qr-enter-active, .qr-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.qr-enter-from, .qr-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
