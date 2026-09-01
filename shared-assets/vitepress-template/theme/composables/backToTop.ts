/**
 * backToTop — Back to top 按钮（C7·§8.81 P0-3）
 *
 * 自动在页面右下角插入按钮，滚动 > 300px 显示
 *
 * 用法：
 *   import { setupBackToTop } from '@shared/vitepress-template/theme/composables/backToTop'
 *   setupBackToTop()
 */

export function setupBackToTop() {
  if (typeof window === 'undefined' || typeof document === 'undefined') return

  let btn = document.querySelector<HTMLButtonElement>('.at-back-to-top')
  if (!btn) {
    btn = document.createElement('button')
    btn.className = 'at-back-to-top'
    btn.setAttribute('aria-label', '回到顶部')
    btn.innerHTML = `
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="18 15 12 9 6 15"></polyline>
      </svg>
    `
    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    })
    document.body.appendChild(btn)
  }

  let rafId: number | null = null
  function update() {
    if (rafId !== null) return
    rafId = requestAnimationFrame(() => {
      rafId = null
      if (!btn) return
      const scrollTop = window.scrollY || document.documentElement.scrollTop
      if (scrollTop > 300) {
        btn.classList.add('visible')
      } else {
        btn.classList.remove('visible')
      }
    })
  }

  window.addEventListener('scroll', update, { passive: true })

  // VitePress SPA 路由
  window.addEventListener('popstate', () => setTimeout(update, 50))

  setTimeout(update, 0)
}
