import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import WhyThisGraph from './components/WhyThisGraph.vue'
import MindMap from './components/MindMap.vue'
import GiscusComment from './components/GiscusComment.vue'
import './style.css'

import { setupReadingProgress } from '../../../../shared-assets/vitepress-template/theme/composables/readingProgress'

export default {
  setup() {
    setupReadingProgress()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('WhyThisGraph', WhyThisGraph)
    app.component('MindMap', MindMap)
    app.component('GiscusComment', GiscusComment)
  }
}