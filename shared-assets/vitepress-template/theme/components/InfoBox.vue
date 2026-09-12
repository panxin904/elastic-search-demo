<script setup lang="ts">
/**
 * InfoBox.vue — 信息提示组件（§8.82 v31）
 *
 * TipBox 别名，专注 info 变体。保持命名简洁，便于调用方语义清晰。
 */
interface Props {
  icon?: string
  title?: string
}

withDefaults(defineProps<Props>(), {
  icon: '📘',
  title: '相关信息',
})
</script>

<template>
  <TipBox :icon="icon" :title="title" variant="info">
    <slot />
  </TipBox>
</template>
