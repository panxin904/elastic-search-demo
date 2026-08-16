import DefaultTheme from 'vitepress/theme'
import WhyThisGraph from './components/WhyThisGraph.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import './style.css'

export default {
  setup() {
    setupReadingProgress()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('WhyThisGraph', WhyThisGraph)
  }
}
