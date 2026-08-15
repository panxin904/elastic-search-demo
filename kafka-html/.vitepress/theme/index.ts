import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import KafkaPlayground from './components/KafkaPlayground.vue'
import KafkaTopology from './components/KafkaTopology.vue'
import ConsumerSimulator from './components/ConsumerSimulator.vue'
import CommandCheatsheet from './components/CommandCheatsheet.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('MindMap', MindMap)
    app.component('KafkaPlayground', KafkaPlayground)
    app.component('KafkaTopology', KafkaTopology)
    app.component('ConsumerSimulator', ConsumerSimulator)
    app.component('CommandCheatsheet', CommandCheatsheet)
  }
}
