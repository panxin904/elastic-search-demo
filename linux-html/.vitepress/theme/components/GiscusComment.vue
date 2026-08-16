<script setup lang="ts">
/**
 * GiscusComment.vue — GitHub Discussions 驱动的评论组件（C6）
 *
 * 用法（在 .md 末尾）：
 *   <ClientOnly>
 *     <GiscusComment />
 *   </ClientOnly>
 *
 * 部署前必读：
 *   1. 访问 https://giscus.app/zh-CN 配置你的仓库
 *   2. 选择 / 创建一个仓库承载评论（推荐共享 repo: Scholar-s-Atlas/comments）
 *   3. 在仓库启用 Discussions
 *   4. 创建一个分类（如 "Comments"）
 *   5. giscus.app 会生成 data-repo / data-repo-id / data-category / data-category-id
 *   6. 填到下方 props 默认值
 *
 * 数据映射策略：pathname（每个 .md 路径 → 一个 Discussion）
 * 优点：URL 唯一天然区分；切换页面评论独立
 */
interface Props {
  repo?: string
  repoId?: string
  category?: string
  categoryId?: string
  mapping?: 'pathname' | 'url' | 'title' | 'og:title' | 'specific' | 'number'
  theme?: string
  lang?: string
}

withDefaults(defineProps<Props>(), {
  repo: 'Scholar-s-Atlas/comments',           // ← 替换为你的仓库
  repoId: 'R_PLACEHOLDER_REPLACE_ME',         // ← giscus.app 生成的 repoId
  category: 'General',                         // ← 替换为你的分类名
  categoryId: 'DIC_PLACEHOLDER_REPLACE_ME',   // ← giscus.app 生成的 categoryId
  mapping: 'pathname',                         // 每个 .md 路径一个 Discussion
  theme: 'preferred_color_scheme',             // 自动跟随系统暗色
  lang: 'zh-CN',
})
</script>

<template>
  <div class="giscus-comment">
    <ClientOnly>
      <component
        :is="'script'"
        src="https://giscus.app/client.js"
        :data-repo="repo"
        :data-repo-id="repoId"
        :data-category="category"
        :data-category-id="categoryId"
        :data-mapping="mapping"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="top"
        :data-theme="theme"
        :data-lang="lang"
        crossorigin="anonymous"
        async
      />
    </ClientOnly>
  </div>
</template>

<style scoped>
.giscus-comment {
  margin: 3rem 0 1rem;
  padding-top: 2rem;
  border-top: 1px solid var(--vp-c-divider);
}
.giscus-comment::before {
  content: '💬 评论';
  display: block;
  margin-bottom: 1rem;
  font-weight: 600;
  color: var(--vp-c-text-2);
  font-size: 0.95rem;
}
</style>
