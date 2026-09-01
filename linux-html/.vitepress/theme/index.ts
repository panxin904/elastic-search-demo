import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
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
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('MindMap', MindMap)
    app.component('QrShare', QrShare)
  }
}