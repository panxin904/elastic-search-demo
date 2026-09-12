<script setup lang="ts">
/**
 * WarnBox.vue — 警告提示组件（§8.82 v31）
 *
 * 替换 `> ⚠️ **Note**: ...` 这类风险提示块。
 */
interface Props {
  icon?: string
  title?: string
  variant?: 'warn' | 'danger'
}

withDefaults(defineProps<Props>(), {
  icon: '⚠️',
  title: '注意',
  variant: 'warn',
})
</script>

<template>
  <TipBox :icon="icon" :title="title" :variant="variant">
    <slot />
  </TipBox>
</template>
