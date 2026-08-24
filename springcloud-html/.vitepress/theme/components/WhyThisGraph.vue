<script setup lang="ts">
/**
 * WhyThisGraph.vue — 「为什么写这个图谱」双栏 + 相关站点推荐
 *
 * 用法（在子站 docs/index.md）：
 *   <ClientOnly>
 *     <WhyThisGraph
 *       :pain-points="[...]"
 *       :goals="[...]"
 *       :related-sites="[
 *         { site: 'bigdata', path: '/12-olap-engine/clickhouse', label: 'OLAP 对比' },
 *         ...
 *       ]"
 *       title="🎯 为什么写这个图谱？"
 *     />
 *   </ClientOnly>
 *
 * 规范存放位置：shared-assets/vitepress-template/theme/components/
 * 当前实现：每个子站 theme/components/ 复制一份
 * 跨站关联词典：shared-assets/glossary/keywords.json
 */
interface RelatedSite {
  site: string  // 站点 ID（不带 -html）
  path: string  // 子站内的相对路径（以 / 开头）
  label: string // 显示文本
}

interface Props {
  painPoints: string[]
  goals: string[]
  relatedSites?: RelatedSite[]
  title?: string
}

withDefaults(defineProps<Props>(), {
  title: '🎯 为什么写这个图谱？',
  relatedSites: () => []
})
</script>

<template>
  <div class="why-this-graph">
    <h2 v-if="title" class="why-this-graph-title">{{ title }}</h2>
    <div class="why-this-graph-grid">
      <div class="why-this-graph-col why-this-graph-col-pain">
        <div class="why-this-graph-label">痛点</div>
        <ul class="why-this-graph-list why-this-graph-list-pain">
          <li v-for="(item, i) in painPoints" :key="i">{{ item }}</li>
        </ul>
      </div>
      <div class="why-this-graph-col why-this-graph-col-goal">
        <div class="why-this-graph-label">目标</div>
        <ul class="why-this-graph-list why-this-graph-list-goal">
          <li v-for="(item, i) in goals" :key="i">{{ item }}</li>
        </ul>
      </div>
    </div>

    <div v-if="relatedSites && relatedSites.length > 0" class="why-this-graph-related">
      <div class="why-this-graph-related-label">🔗 相关站点</div>
      <div class="why-this-graph-related-grid">
        <a
          v-for="(rs, i) in relatedSites"
          :key="i"
          :href="`https://java-px.bot.cd/${rs.site}/${rs.path}`"
          target="_blank"
          rel="noopener"
          class="why-this-graph-related-card"
        >
          <span class="why-this-graph-related-site">{{ rs.site }}</span>
          <span class="why-this-graph-related-label-text">{{ rs.label }}</span>
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.why-this-graph {
  margin: 2rem 0;
}
.why-this-graph-title {
  margin: 0 0 1rem 0;
  font-size: 1.4rem;
  font-weight: 600;
}
.why-this-graph-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}
@media (max-width: 768px) {
  .why-this-graph-grid {
    grid-template-columns: 1fr;
  }
}
.why-this-graph-col {
  border-radius: 8px;
  padding: 1rem 1.25rem;
  border: 1px solid var(--vp-c-divider);
}
.why-this-graph-col-pain {
  background: rgba(220, 38, 38, 0.04);
  border-left: 3px solid #dc2626;
}
.why-this-graph-col-goal {
  background: rgba(34, 197, 94, 0.04);
  border-left: 3px solid #22c55e;
}
.why-this-graph-label {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  letter-spacing: 0.05em;
}
.why-this-graph-col-pain .why-this-graph-label {
  color: #dc2626;
}
.why-this-graph-col-goal .why-this-graph-label {
  color: #22c55e;
}
.why-this-graph-list {
  margin: 0;
  padding-left: 1.25rem;
  line-height: 1.7;
}
.why-this-graph-list-pain li::marker {
  color: #dc2626;
}
.why-this-graph-list-goal li::marker {
  color: #22c55e;
}

/* === 相关站点 === */
.why-this-graph-related {
  margin-top: 1.5rem;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  background: rgba(139, 92, 246, 0.04);
  border: 1px solid var(--vp-c-divider);
  border-left: 3px solid #8b5cf6;
}
.why-this-graph-related-label {
  font-weight: 600;
  font-size: 0.9rem;
  margin-bottom: 0.75rem;
  letter-spacing: 0.05em;
  color: #8b5cf6;
}
.why-this-graph-related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
}
.why-this-graph-related-card {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-1);
  text-decoration: none;
  transition: all .15s;
}
.why-this-graph-related-card:hover {
  border-color: #8b5cf6;
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(139, 92, 246, .15);
}
.why-this-graph-related-site {
  font-size: 0.75rem;
  font-weight: 600;
  color: #8b5cf6;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.why-this-graph-related-label-text {
  font-size: 0.875rem;
  color: var(--vp-c-text-1);
  margin-top: 2px;
}
</style>
