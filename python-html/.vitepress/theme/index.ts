import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import PythonPlayground from './components/PythonPlayground.vue'
import ScrapyFlow from './components/ScrapyFlow.vue'
import SortVisualizer from './components/SortVisualizer.vue'
import ApiReference from './components/ApiReference.vue'
import Cheatsheet from './components/Cheatsheet.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import './style.css'

export default {
  setup() {
    setupReadingProgress()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('MindMap', MindMap)
    app.component('PythonPlayground', PythonPlayground)
    app.component('ScrapyFlow', ScrapyFlow)
    app.component('SortVisualizer', SortVisualizer)
    app.component('ApiReference', ApiReference)
    app.component('Cheatsheet', Cheatsheet)
  }
}
