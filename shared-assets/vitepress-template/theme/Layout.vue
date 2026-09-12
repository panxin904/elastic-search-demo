<script setup lang="ts">
/**
 * Layout.vue — 共享 VitePress Layout 包装（§8.82 v31）
 *
 * 目的：
 *  - 全局在每篇文档末尾注入 Giscus 评论（替代每个 md 手写 <ClientOnly><GiscusComment /></ClientOnly>）
 *  - 自动透传 VitePress 默认 Layout 的所有 slot（避免破坏默认行为）
 *
 * 用法：在每个 .vitepress/theme/index.ts 中：
 *   import { h } from 'vue'
 *   import DefaultTheme from 'vitepress/theme'
 *   import SharedLayout from '@shared/vitepress-template/theme/Layout.vue'
 *
 *   export default {
 *     ...,
 *     Layout() {
 *       return h(SharedLayout, null, {})
 *     }
 *   }
 *
 * 关键点：必须保留对 DefaultTheme.Layout 的继承，并通过 <component :is> 透传所有 slots。
 */
import { useRoute } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import GiscusComment from './components/GiscusComment.vue'

const route = useRoute()
const isHome = route.path === '/' || route.path.endsWith('/index.html')
</script>

<template>
  <component :is="DefaultTheme.Layout">
    <!-- 透传所有默认 slot（doc-before / doc-footer / sidebar-content / etc） -->
    <template v-for="(_, name) in $slots" #[name]="slotProps">
      <slot :name="name" v-bind="slotProps" />
    </template>

    <!-- 自动在文档末尾注入评论（除首页外） -->
    <template #doc-after>
      <slot name="doc-after" />
      <ClientOnly>
        <GiscusComment v-if="!isHome" />
      </ClientOnly>
    </template>
  </component>
</template>
