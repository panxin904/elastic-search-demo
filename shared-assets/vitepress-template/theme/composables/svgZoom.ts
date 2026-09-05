/**
 * setupSvgZoom — SVG 交互（C-2 + C-3 升级）
 *
 * 为所有 inline SVG 提供两种交互：
 *   1. 点击 .at-expand-trigger 切换 .at-expandable.is-collapsed（折叠/展开分组）
 *   2. 点击 SVG 其他区域 → 全屏 modal 查看大图
 *
 * 比每张 SVG 定制分组折叠更通用，且为所有 SVG 提供统一的全屏查看体验。
 *
 * 使用方式（在子站 .vitepress/theme/index.ts）：
 *   import { setupSvgZoom } from '@shared/vitepress-template/theme/composables/svgZoom'
 *   setupSvgZoom()
 *
 * 注意：
 *   - 必须在 setupSvgTheme() 之后调用（依赖 SVG 已 inline 化）
 *   - 仅对含 at-svg-bg / at-svg-title 的 SVG 生效
 */

let modal: HTMLDivElement | null = null

function createModal(): HTMLDivElement {
  const el = document.createElement('div')
  el.className = 'at-svg-modal'
  el.setAttribute('role', 'dialog')
  el.setAttribute('aria-modal', 'true')
  el.innerHTML = `
    <button class="at-svg-modal-close" aria-label="关闭">✕</button>
    <div class="at-svg-modal-content"></div>
    <div class="at-svg-modal-hint">按 ESC 关闭 · 滚轮缩放查看细节</div>
  `
  document.body.appendChild(el)

  el.querySelector('.at-svg-modal-close')?.addEventListener('click', closeModal)
  el.addEventListener('click', (ev) => {
    if (ev.target === el) closeModal()
  })

  return el
}

function closeModal(): void {
  if (!modal) return
  modal.classList.remove('is-open')
  document.body.style.overflow = ''
  const content = modal.querySelector('.at-svg-modal-content')
  if (content) content.innerHTML = ''
}

function openModal(svg: SVGElement): void {
  if (!modal) modal = createModal()
  const content = modal.querySelector('.at-svg-modal-content')
  if (!content) return

  const clone = svg.cloneNode(true) as SVGElement
  clone.removeAttribute('width')
  clone.removeAttribute('height')
  clone.style.maxWidth = '95vw'
  clone.style.maxHeight = '85vh'
  content.innerHTML = ''
  content.appendChild(clone)

  modal.classList.add('is-open')
  document.body.style.overflow = 'hidden'
}

function handleSvgClick(ev: MouseEvent, svg: SVGSVGElement): void {
  const target = ev.target as Element
  if (!target) return

  // 1. trigger 点击：切换折叠
  const trigger = target.closest('.at-expand-trigger') as SVGElement | null
  if (trigger && svg.contains(trigger)) {
    const expandId = trigger.getAttribute('data-target')
    if (expandId) {
      const group = svg.querySelector(`.at-expandable[data-expand-id="${expandId}"]`) as SVGElement | null
      if (group) {
        group.classList.toggle('is-collapsed')
        // 更新 trigger 文字（▶ ↔ ▼）
        const text = trigger.textContent || ''
        trigger.textContent = text.startsWith('▶') ? text.replace('▶', '▼') : text.replace('▼', '▶')
      }
    }
    return
  }

  // 2. 其他区域点击：全屏查看
  openModal(svg)
}

function bindSvg(svg: SVGSVGElement): void {
  if (svg.getAttribute('data-at-zoom-bound') === '1') return

  // 跳过 UI 图标
  if (svg.closest('.at-back-to-top, .at-reading-progress, button, nav, .VPNavBar')) return
  // 必须含主题感知 class（inline 化的内容 SVG）
  if (!svg.querySelector('.at-svg-bg, .at-svg-title')) return

  svg.setAttribute('data-at-zoom-bound', '1')
  svg.style.cursor = 'zoom-in'

  svg.addEventListener('click', (ev) => handleSvgClick(ev, svg))
}

function processAll(): void {
  const svgs = document.querySelectorAll<SVGSVGElement>('main svg, .VPDoc svg, article svg, .at-svg-wrapper svg')
  svgs.forEach(bindSvg)
}

function bindEsc(): void {
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && modal?.classList.contains('is-open')) {
      closeModal()
    }
  })
}

let initialized = false

export function setupSvgZoom(): void {
  if (typeof window === 'undefined' || typeof document === 'undefined') return
  if (initialized) return
  initialized = true

  bindEsc()

  // 延迟等待 setupSvgTheme 完成 inline 化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(processAll, 300), { once: true })
  } else {
    setTimeout(processAll, 300)
  }

  // SPA 路由切换
  window.addEventListener('popstate', () => setTimeout(processAll, 400))
  const origPush = history.pushState
  history.pushState = function (...args) {
    const ret = origPush.apply(this, args as Parameters<typeof origPush>)
    setTimeout(processAll, 400)
    return ret
  }
}
