<script setup lang="ts">
/**
 * SitePortalLink.vue — 顶部"返回门户"链接组件
 * 用法：在 config.mts 的 nav 中使用（见 config.mts.tpl）
 *
 *   { text: '🏠 门户', link: 'https://java-px.bot.cd/', target: '_blank' }
 *
 * 样式已通过全局 .at-portal-link 提供，无需在此组件内硬编码。
 */
</script>

<template>
  <a class="at-portal-link" href="https://java-px.bot.cd/" target="_blank" rel="noopener">
    🏠 门户首页
  </a>
</template>
