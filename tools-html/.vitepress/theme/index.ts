import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import { setupReadingProgress } from '../../../../shared-assets/vitepress-template/theme/composables/readingProgress'
import './style.css'

// Vue 组件都需要客户端运行 — VitePress 默认 SSR 会失败，
// 用 ClientOnly 包裹动态组件即可。
const ClientOnly = {
  props: ['setup'],
  setup(_, { slots }) {
    return () => h('div', slots.default?.())
  }
}

export default {
  setup() {
    setupReadingProgress()
  },
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {})
  },
  enhanceApp({ app }) {
    app.component('ClientOnly', ClientOnly)
  }
}
