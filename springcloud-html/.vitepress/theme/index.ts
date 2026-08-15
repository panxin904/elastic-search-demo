import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import ComponentCheatsheet from './components/ComponentCheatsheet.vue'
import ConfigPlayground from './components/ConfigPlayground.vue'
import RequestFlow from './components/RequestFlow.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('MindMap', MindMap)
    app.component('ComponentCheatsheet', ComponentCheatsheet)
    app.component('ConfigPlayground', ConfigPlayground)
    app.component('RequestFlow', RequestFlow)
  }
}