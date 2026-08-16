import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import EsClusterDashboard from './components/EsClusterDashboard.vue'
import EsRequestDebugger from './components/EsRequestDebugger.vue'
import EsDslRecipes from './components/EsDslRecipes.vue'
import EsJavaSnippets from './components/EsJavaSnippets.vue'
import EsScenarios from './components/EsScenarios.vue'
import EsDeploymentConfig from './components/EsDeploymentConfig.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import './style.css'

export default {
  setup() {
    setupReadingProgress()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('EsClusterDashboard', EsClusterDashboard)
    app.component('EsRequestDebugger', EsRequestDebugger)
    app.component('EsDslRecipes', EsDslRecipes)
    app.component('EsJavaSnippets', EsJavaSnippets)
    app.component('EsScenarios', EsScenarios)
    app.component('EsDeploymentConfig', EsDeploymentConfig)
  }
}
