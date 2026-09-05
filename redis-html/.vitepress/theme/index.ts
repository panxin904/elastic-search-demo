import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import CommandPlayground from './components/CommandPlayground.vue'
import DataStructureViz from './components/DataStructureViz.vue'
import ClusterTopology from './components/ClusterTopology.vue'
import DistributedLock from './components/DistributedLock.vue'
import CommandCheatsheet from './components/CommandCheatsheet.vue'
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
    app.component('MindMap', MindMap)
    app.component('CommandPlayground', CommandPlayground)
    app.component('DataStructureViz', DataStructureViz)
    app.component('ClusterTopology', ClusterTopology)
    app.component('DistributedLock', DistributedLock)
    app.component('CommandCheatsheet', CommandCheatsheet)
    app.component('QrShare', QrShare)
  }
}
