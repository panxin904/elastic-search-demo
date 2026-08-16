import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import WhyThisGraph from './components/WhyThisGraph.vue'
import MindMap from './components/MindMap.vue'
import './style.css'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'

export default {
  setup() {
    setupReadingProgress()
  }, extends: DefaultTheme, enhanceApp({ app }) { app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('WhyThisGraph', WhyThisGraph); app.component('MindMap', MindMap) } }
