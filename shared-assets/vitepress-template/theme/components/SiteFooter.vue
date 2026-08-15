<script setup lang="ts">
/**
 * SiteFooter.vue — 站点底部统一组件
 *
 * Props:
 *   siteTitle: 站点名（如 "AI 工程全栈"）
 *   message:   自定义文案（可选；空时用默认）
 *   copyright: 版权说明（默认 "MIT License"）
 *
 * 使用：在 .vitepress/theme/index.ts 注册后，
 *       在 config.mts 的 themeConfig.footer 使用
 */
interface Props {
  siteTitle: string
  message?: string
  copyright?: string
}
withDefaults(defineProps<Props>(), {
  message: '',
  copyright: 'MIT License'
})
</script>

<template>
  <div class="at-footer">
    <div v-if="message" v-html="message"></div>
    <div v-else>{{ siteTitle }} · Scholar's Atlas 子站</div>
    <div style="margin-top: 0.5rem; font-size: 0.75rem; opacity: 0.7;">
      © {{ new Date().getFullYear() }} {{ copyright }} ·
      🏠 <a href="https://java-px.bot.cd/" target="_blank" rel="noopener">门户首页</a>
    </div>
  </div>
</template>
