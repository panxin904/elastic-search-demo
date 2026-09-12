import DefaultTheme from 'vitepress/theme'
import WhyThisGraph from './components/WhyThisGraph.vue'
import { setupReadingProgress } from '@shared/vitepress-template/theme/composables/readingProgress'
import { setupSvgTheme } from '@shared/vitepress-template/theme/composables/svgTheme'
import { setupSvgZoom } from '@shared/vitepress-template/theme/composables/svgZoom'
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
    app.component('WhyThisGraph', WhyThisGraph)
    app.component('QrShare', QrShare)
    app.component('GiscusComment', GiscusComment)
  }
}
