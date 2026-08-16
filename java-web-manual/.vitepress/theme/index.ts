import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import './style.css'

export default {
  setup() {
    setupReadingProgress()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
  }
}
