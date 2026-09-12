<script setup lang="ts">
/**
 * TipBox.vue — 提示框组件（§8.82 v31）
 *
 * 替代 markdown 引用块：
 *   > 💡 鼠标拖动节点...
 *
 * 用法：
 *   <TipBox icon="💡" title="提示">
 *     支持任意 markdown / HTML 内容
 *   </TipBox>
 */
interface Props {
  icon?: string
  title?: string
  variant?: 'tip' | 'info' | 'warn' | 'danger' | 'success' | 'note'
}

withDefaults(defineProps<Props>(), {
  icon: '💡',
  title: '提示',
  variant: 'tip',
})
</script>

<template>
  <div class="at-tipbox" :class="`at-tipbox--${variant}`">
    <div class="at-tipbox__header">
      <span class="at-tipbox__icon">{{ icon }}</span>
      <span class="at-tipbox__title">{{ title }}</span>
    </div>
    <div class="at-tipbox__body">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.at-tipbox {
  margin: 1rem 0;
  padding: clamp(0.75rem, 1.5vw, 1.25rem);
  border-radius: var(--at-radius-md, 8px);
  border-left: 4px solid;
  background: var(--vp-c-bg-soft, #f8fafc);
}
.at-tipbox__header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.at-tipbox__icon {
  font-size: 1.1rem;
}
.at-tipbox__title {
  font-weight: 600;
  font-size: clamp(0.9rem, 0.5vw + 0.85rem, 1rem);
}
.at-tipbox__body {
  font-size: clamp(0.85rem, 0.5vw + 0.8rem, 0.95rem);
  line-height: 1.7;
  color: var(--vp-c-text-1, #1e293b);
}
.at-tipbox__body :deep(p) {
  margin: 0.4rem 0;
}
.at-tipbox__body :deep(p:first-child) {
  margin-top: 0;
}
.at-tipbox__body :deep(p:last-child) {
  margin-bottom: 0;
}

/* === 变体 === */
.at-tipbox--tip     { border-left-color: #f59e0b; background: rgba(245, 158, 11, 0.08); }
.at-tipbox--info    { border-left-color: #3b82f6; background: rgba(59, 130, 246, 0.08); }
.at-tipbox--warn    { border-left-color: #f97316; background: rgba(249, 115, 22, 0.08); }
.at-tipbox--danger  { border-left-color: #ef4444; background: rgba(239, 68, 68, 0.08); }
.at-tipbox--success { border-left-color: #10b981; background: rgba(16, 185, 129, 0.08); }
.at-tipbox--note    { border-left-color: #8b5cf6; background: rgba(139, 92, 246, 0.08); }
</style>
