/**
 * setupSvgTheme — SVG 主题感知（C-1 交互性升级）
 *
 * 自动将所有 <img src="*.svg"> 转为 inline <svg>，让外部 CSS 变量
 * （如站点 light/dark 主题）能影响 SVG 内部元素的 fill/stroke。
 *
 * 原理：
 *   - 浏览器把 <img> 引入的 SVG 当独立文档，外部 CSS 无法穿透
 *   - fetch + inline 注入后，SVG 成为 DOM 的一部分，CSS var 生效
 *   - 站点 .dark 类切换时，已 inline 的 SVG 自动跟随主题
 *
 * 使用方式（在子站 .vitepress/theme/index.ts）：
 *   import { setupSvgTheme } from '@shared/vitepress-template/theme/composables/svgTheme'
 *   setupSvgTheme()
 *
 * 配合：
 *   - shared-assets/svg/*.svg 中的 .at-svg-bg / .at-svg-title class
 *   - style.css 中的 --at-svg-bg / --at-svg-title CSS 变量
 *
 * 风险：
 *   - 失败时降级为 <img>（不破坏现有显示）
 *   - 重复 inline 防护（data-at-themed 标记）
 */

const PROCESSED = 'data-at-themed'

async function inlineSvg(img: HTMLImageElement): Promise<void> {
  if (img.getAttribute(PROCESSED) === '1') return

  const src = img.getAttribute('src')
  if (!src || !src.endsWith('.svg')) return

  try {
    const url = new URL(src, window.location.href)
    const res = await fetch(url.toString())
    if (!res.ok) return
    const text = await res.text()

    // 提取 <svg>...</svg>
    const match = text.match(/<svg[\s\S]*?<\/svg>/i)
    if (!match) return

    const wrapper = document.createElement('div')
    wrapper.className = 'at-svg-wrapper'
    wrapper.innerHTML = match[0]

    const svgEl = wrapper.firstElementChild as SVGElement
    if (!svgEl || svgEl.tagName.toLowerCase() !== 'svg') return

    // 保留 alt 文案作为 title（无障碍）
    const alt = img.getAttribute('alt')
    if (alt) {
      const titleEl = document.createElementNS('http://www.w3.org/2000/svg', 'title')
      titleEl.textContent = alt
      svgEl.insertBefore(titleEl, svgEl.firstChild)
    }

    // 标记 + 替换
    img.setAttribute(PROCESSED, '1')
    img.replaceWith(svgEl)
  } catch (err) {
    // 静默失败：保留 <img> 降级
    if (typeof console !== 'undefined') {
      console.warn('[svgTheme] failed to inline', src, err)
    }
  }
}

export function setupSvgTheme(): void {
  if (typeof window === 'undefined' || typeof document === 'undefined') return

  // 批量处理（懒加载不阻断）
  function processAll(): void {
    const imgs = document.querySelectorAll<HTMLImageElement>(`img[src$=".svg"]:not([${PROCESSED}])`)
    imgs.forEach((img) => {
      void inlineSvg(img)
    })
  }

  // 首次执行
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', processAll, { once: true })
  } else {
    processAll()
  }

  // VitePress SPA 路由切换：监听 popstate / pushstate
  window.addEventListener('popstate', () => setTimeout(processAll, 100))
  const origPush = history.pushState
  history.pushState = function (...args) {
    const ret = origPush.apply(this, args as Parameters<typeof origPush>)
    setTimeout(processAll, 100)
    return ret
  }
}
