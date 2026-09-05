import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import KafkaPlayground from './components/KafkaPlayground.vue'
import KafkaTopology from './components/KafkaTopology.vue'
import ConsumerSimulator from './components/ConsumerSimulator.vue'
import CommandCheatsheet from './components/CommandCheatsheet.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import { injectReadingTime } from '@shared/vitepress-template/theme/composables/readingTime'
import { setupBackToTop } from '@shared/vitepress-template/theme/composables/backToTop'
import { setupSvgTheme } from '@shared/vitepress-template/theme/composables/svgTheme'
import { setupSvgZoom } from '@shared/vitepress-template/theme/composables/svgZoom'
import './style.css'
import QrShare from '@shared/vitepress-template/theme/components/QrShare.vue'

export default {
  setup() {
    setupReadingProgress()
    injectReadingTime()
    setupBackToTop()
    setupSvgTheme()
    setupSvgZoom()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('MindMap', MindMap)
    app.component('KafkaPlayground', KafkaPlayground)
    app.component('KafkaTopology', KafkaTopology)
    app.component('ConsumerSimulator', ConsumerSimulator)
    app.component('CommandCheatsheet', CommandCheatsheet)
    app.component('QrShare', QrShare)
  }
}
