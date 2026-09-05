import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import WhyThisGraph from './components/WhyThisGraph.vue'
import MindMap from './components/MindMap.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import { injectReadingTime } from '@shared/vitepress-template/theme/composables/readingTime'
import { setupBackToTop } from '@shared/vitepress-template/theme/composables/backToTop'
import { setupSvgTheme } from '@shared/vitepress-template/theme/composables/svgTheme'
import './style.css'
import QrShare from '@shared/vitepress-template/theme/components/QrShare.vue'


export default {
  setup() {
    setupReadingProgress()
    injectReadingTime()
    setupBackToTop()
    setupSvgTheme()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('WhyThisGraph', WhyThisGraph)
    app.component('MindMap', MindMap)
    app.component('QrShare', QrShare)
  }
}