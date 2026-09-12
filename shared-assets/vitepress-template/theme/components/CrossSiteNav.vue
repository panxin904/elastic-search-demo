<script setup lang="ts">
/**
 * CrossSiteNav.vue — 跨站推荐组件（§8.82 v31 公共组件化）
 *
 * 用途：替代硬编码 markdown 块
 *   <!-- xlink-subpage-injected:do-not-edit -->
 *   本页相关主题的跨站入口:
 *   - [linux](https://java-px.bot.cd/linux/):Linux 文件系统
 *   - [observability](https://java-px.bot.cd/observability/):存储监控
 *   ...
 *
 * 优势：
 *  - 样式集中维护（无需在 385 个 md 里散落硬编码）
 *  - 支持点击打开新页（target=_blank）
 *  - SSR 友好（无需 ClientOnly）
 *  - 静态 props 构建时可缓存
 *
 * 用法 1（props 显式传入）— 推荐，编译期确定：
 *   <CrossSiteNav
 *     :items="[
 *       { site: 'linux',         label: 'Linux 文件系统',  url: 'https://java-px.bot.cd/linux/' },
 *       { site: 'observability', label: '存储监控',        url: 'https://java-px.bot.cd/observability/' },
 *       { site: 'postgresql',    label: 'PG 存储引擎',     url: 'https://java-px.bot.cd/postgresql/' },
 *     ]"
 *     title="本页相关主题的跨站入口"
 *   />
 */
interface CrossSiteItem {
  site: string
  label: string
  url?: string
}

interface Props {
  items?: CrossSiteItem[]
  title?: string
  limit?: number
  baseUrl?: string
}

const props = withDefaults(defineProps<Props>(), {
  items: undefined,
  title: '🔗 相关阅读（跨站导航）',
  limit: 6,
  baseUrl: 'https://java-px.bot.cd',
})

const buildUrl = (site: string) => `${props.baseUrl}/${site}/`

const display = (props.items || []).slice(0, props.limit)
</script>

<template>
  <section v-if="display.length" class="at-cross-site-nav">
    <h3 class="at-cross-site-nav__title">{{ title }}</h3>
    <p class="at-cross-site-nav__hint">本页相关主题的跨站入口：</p>
    <div class="at-grid-cards at-cross-site-nav__grid">
      <a
        v-for="item in display"
        :key="item.site"
        class="at-link-card at-cross-site-nav__card"
        :href="item.url || buildUrl(item.site)"
        target="_blank"
        rel="noopener"
      >
        <span class="at-cross-site-nav__badge">{{ item.site }}</span>
        <span class="at-cross-site-nav__label">{{ item.label }}</span>
      </a>
    </div>
  </section>
</template>

<style scoped>
.at-cross-site-nav {
  margin: 2rem 0;
  padding: clamp(1rem, 2vw, 1.5rem);
  background: var(--vp-c-bg-soft, #f8fafc);
  border-radius: var(--at-radius-md, 8px);
  border: 1px solid var(--vp-c-divider, #e5e7eb);
}
.at-cross-site-nav__title {
  margin: 0 0 0.25rem 0;
  font-size: clamp(1.1rem, 1.5vw + 0.3rem, 1.4rem);
  font-weight: 600;
}
.at-cross-site-nav__hint {
  margin: 0 0 1rem 0;
  font-size: clamp(0.85rem, 0.5vw + 0.8rem, 0.95rem);
  color: var(--vp-c-text-2, #64748b);
}
.at-cross-site-nav__grid {
  margin: 0 !important;
}
.at-cross-site-nav__card {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.at-cross-site-nav__badge {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: clamp(0.7rem, 0.3vw + 0.65rem, 0.8rem);
  padding: 0.15rem 0.5rem;
  background: var(--vp-c-brand-soft, rgba(139, 92, 246, 0.12));
  color: var(--at-brand, #8b5cf6);
  border-radius: var(--at-radius-sm, 4px);
  align-self: flex-start;
  font-weight: 600;
}
.at-cross-site-nav__label {
  font-size: clamp(0.85rem, 0.5vw + 0.8rem, 0.95rem);
  color: var(--vp-c-text-1, #1e293b);
}
</style>
