import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import { setupSvgTheme } from '@shared/vitepress-template/theme/composables/svgTheme'
import { setupSvgZoom } from '@shared/vitepress-template/theme/composables/svgZoom'
import QrShare from '@shared/vitepress-template/theme/components/QrShare.vue'
import './style.css'

export default {
  setup() {
    setupReadingProgress()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('MindMap', MindMap)
    app.component('QrShare', QrShare)
  }
}