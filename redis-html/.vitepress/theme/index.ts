import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import CommandPlayground from './components/CommandPlayground.vue'
import DataStructureViz from './components/DataStructureViz.vue'
import ClusterTopology from './components/ClusterTopology.vue'
import DistributedLock from './components/DistributedLock.vue'
import CommandCheatsheet from './components/CommandCheatsheet.vue'
import { setupReadingProgress } from '../../../../shared-assets/vitepress-template/theme/composables/readingProgress'
import './style.css'

export default {
  setup() {
    setupReadingProgress()
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
  }
}
