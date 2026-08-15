<script setup lang="ts">
/**
 * WhyThisGraph.vue — 「为什么写这个图谱」双栏组件
 *
 * 用法（在子站 docs/index.md）：
 *   <WhyThisGraph
 *     :pain-points="[...]"
 *     :goals="[...]"
 *     title="="🎯 为什么写这个图谱？""
 *   />
 *
 * 规范存放位置：shared-assets/vitepress-template/theme/components/
 * 当前实现：每个子站 theme/components/ 复制一份（C1 完成后改为 npm 包）
 */
interface Props {
  painPoints: string[]
  goals: string[]
  title?: string
}
withDefaults(defineProps<Props>(), {
  title: '🎯 为什么写这个图谱？'
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
</style>
