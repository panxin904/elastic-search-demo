import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import SqlPlayground from './components/SqlPlayground.vue'
import LockDemo from './components/LockDemo.vue'
import SqlCheatsheet from './components/SqlCheatsheet.vue'
import PerfCalculator from './components/PerfCalculator.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('MindMap', MindMap)
    app.component('SqlPlayground', SqlPlayground)
    app.component('LockDemo', LockDemo)
    app.component('SqlCheatsheet', SqlCheatsheet)
    app.component('PerfCalculator', PerfCalculator)
  }
}