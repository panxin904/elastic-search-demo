import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import './style.css'
export default { extends: DefaultTheme, enhanceApp({ app }) { app.component('KnowledgeGraph', KnowledgeGraph); app.component('MindMap', MindMap) } }