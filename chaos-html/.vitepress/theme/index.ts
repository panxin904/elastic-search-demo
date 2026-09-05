import DefaultTheme from 'vitepress/theme'
import WhyThisGraph from './components/WhyThisGraph.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import { setupSvgTheme } from '@shared/vitepress-template/theme/composables/svgTheme'
import { setupSvgZoom } from '@shared/vitepress-template/theme/composables/svgZoom'
import { injectReadingTime } from '@shared/vitepress-template/theme/composables/readingTime'
import { setupBackToTop } from '@shared/vitepress-template/theme/composables/backToTop'
import './style.css'
import QrShare from '@shared/vitepress-template/theme/components/QrShare.vue'

export default {
  setup() {
    setupReadingProgress()
    injectReadingTime()
    setupBackToTop()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('WhyThisGraph', WhyThisGraph)
    app.component('QrShare', QrShare)
  }
}
