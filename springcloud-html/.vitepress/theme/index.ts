import DefaultTheme from 'vitepress/theme'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import MindMap from './components/MindMap.vue'
import ComponentCheatsheet from './components/ComponentCheatsheet.vue'
import ConfigPlayground from './components/ConfigPlayground.vue'
import RequestFlow from './components/RequestFlow.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import { injectReadingTime } from '@shared/vitepress-template/theme/composables/readingTime'
import { setupBackToTop } from '@shared/vitepress-template/theme/composables/backToTop'
import GiscusComment from '@shared/vitepress-template/theme/components/GiscusComment.vue'
import './style.css'
import QrShare from '@shared/vitepress-template/theme/components/QrShare.vue'
import CrossSiteNav from '@shared/vitepress-template/theme/components/CrossSiteNav.vue'
import TipBox from '@shared/vitepress-template/theme/components/TipBox.vue'
import InfoBox from '@shared/vitepress-template/theme/components/InfoBox.vue'
import WarnBox from '@shared/vitepress-template/theme/components/WarnBox.vue'

export default {
  setup() {
    setupReadingProgress()
    injectReadingTime()
    setupBackToTop()
  },
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('CrossSiteNav', CrossSiteNav)
    app.component('TipBox', TipBox)
    app.component('InfoBox', InfoBox)
    app.component('WarnBox', WarnBox)
    app.component('KnowledgeGraph', KnowledgeGraph)
    app.component('MindMap', MindMap)
    app.component('ComponentCheatsheet', ComponentCheatsheet)
    app.component('ConfigPlayground', ConfigPlayground)
    app.component('RequestFlow', RequestFlow)
    app.component('QrShare', QrShare)
    app.component('GiscusComment', GiscusComment)
  }
}