/**
 * setupReadingProgress — 通用阅读进度条（C7）
 *
 * 使用方式（在子站 .vitepress/theme/index.ts）：
 *   import { setupReadingProgress } from '../../../../shared-assets/vitepress-template/theme/composables/readingProgress'
 *
 *   export default {
 *     extends: DefaultTheme,
 *     setup() {
 *       setupReadingProgress()
 *     },
 *     ...
 *   }
 *
 * 行为：
 *   - 在 body 末尾插入 <div class="at-reading-progress"></div>
 *   - 监听 scroll/resize 更新 width
 *   - SSR safe（typeof window 检查）
 *   - 路由切换时（VitePress SPA）自动重新计算
 */
export function setupReadingProgress() {
  if (typeof window === 'undefined') return

  // 避免重复插入
  let bar = document.querySelector<HTMLDivElement>('.at-reading-progress')
  if (!bar) {
    bar = document.createElement('div')
    bar.className = 'at-reading-progress'
    bar.setAttribute('aria-hidden', 'true')
    document.body.appendChild(bar)
  }

  let rafId: number | null = null

  function update() {
    if (rafId !== null) return
    rafId = requestAnimationFrame(() => {
      rafId = null
      const scrollTop = window.scrollY || document.documentElement.scrollTop
      const docHeight =
        document.documentElement.scrollHeight - window.innerHeight
      const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
      if (bar) bar.style.width = `${Math.min(Math.max(progress, 0), 100)}%`
    })
  }

  window.addEventListener('scroll', update, { passive: true })
  window.addEventListener('resize', update)

  // VitePress SPA 路由切换：监听 popstate / pushstate
  window.addEventListener('popstate', () => setTimeout(update, 50))

  // 初始计算（延迟一帧确保 DOM 完成渲染）
  setTimeout(update, 0)

  // MutationObserver：内容变化时重算（路由切换 + lazy load 图片）
  const observer = new MutationObserver(() => {
    setTimeout(update, 100)
  })
  observer.observe(document.body, { childList: true, subtree: false })

  // 1 分钟后停止 MutationObserver（避免长期性能开销）
  setTimeout(() => observer.disconnect(), 60_000)
}
