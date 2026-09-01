import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import WhyThisGraph from './components/WhyThisGraph.vue'
import MindMap from './components/MindMap.vue'
import GiscusComment from './components/GiscusComment.vue'
import QrShare from '@shared/vitepress-template/theme/components/QrShare.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import { injectReadingTime } from '@shared/vitepress-template/theme/composables/readingTime'
import { setupBackToTop } from '@shared/vitepress-template/theme/composables/backToTop'
import './style.css'


export default {
  setup() {
    setupReadingProgress()
    injectReadingTime()
    setupBackToTop()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('WhyThisGraph', WhyThisGraph)
    app.component('MindMap', MindMap)
    app.component('GiscusComment', GiscusComment)
    app.component('QrShare', QrShare)
  }
}