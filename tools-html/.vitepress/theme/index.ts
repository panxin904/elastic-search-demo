import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import { injectReadingTime } from '@shared/vitepress-template/theme/composables/readingTime'
import { setupBackToTop } from '@shared/vitepress-template/theme/composables/backToTop'
import GiscusComment from '@shared/vitepress-template/theme/components/GiscusComment.vue'
import './style.css'
import QrShare from '@shared/vitepress-template/theme/components/QrShare.vue'
import CrossSiteNav from '@shared/vitepress-template/theme/components/CrossSiteNav.vue'
import TipBox from '@shared/vitepress-template/theme/components/TipBox.vue'
import InfoBox from '@shared/vitepress-template/theme/components/InfoBox.vue'
import WarnBox from '@shared/vitepress-template/theme/components/WarnBox.vue'

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
    injectReadingTime()
    setupBackToTop()
  },
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {})
  },
  enhanceApp({ app }) {
    app.component('CrossSiteNav', CrossSiteNav)
    app.component('TipBox', TipBox)
    app.component('InfoBox', InfoBox)
    app.component('WarnBox', WarnBox)
    app.component('ClientOnly', ClientOnly)
    app.component('QrShare', QrShare)
    app.component('GiscusComment', GiscusComment)
  }
}
