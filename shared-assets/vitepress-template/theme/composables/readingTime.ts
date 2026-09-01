/**
 * readingTime — 阅读时长估算（C7·§8.81 P0-2）
 *
 * 中文 250 字/分钟，英文 200 词/分钟，含代码块加权
 * 用法（在 .md frontmatter 或 layout 中调用）：
 *   {{ readingTime(content) }} 分钟
 *
 * 也可通过 ReadingTimeBadge.vue 组件在文档头部展示
 */

const CN_CHAR = /[\u4e00-\u9fff]/g
const EN_WORD = /[a-zA-Z]+/g

/**
 * 计算文本的"字数"
 */
export function countWords(text: string): number {
  // 移除代码块（不计入阅读时间）
  const noCode = text.replace(/```[\s\S]*?```/g, '').replace(/`[^`]+`/g, '')
  return (noCode.match(CN_CHAR)?.length || 0) + (noCode.match(EN_WORD)?.length || 0)
}

/**
 * 估算阅读时长（分钟，向上取整最少 1 分钟）
 *
 * 基准：中文 250 字/分钟，英文 200 词/分钟
 * 折中：取 220 字/分钟
 */
export function readingTime(text: string): number {
  const words = countWords(text)
  const minutes = words / 220
  return Math.max(1, Math.ceil(minutes))
}

/**
 * 格式化显示：「5 分钟」「约 3 分钟」「< 1 分钟」
 */
export function formatReadingTime(minutes: number): string {
  if (minutes < 1) return '< 1 分钟'
  return `约 ${minutes} 分钟`
}

/**
 * 自动注入到页面：在 .vp-doc 的 h1 后插入阅读时长标签
 *
 * 用法（在 layout 或 theme）：
 *   import { injectReadingTime } from '@shared/vitepress-template/theme/composables/readingTime'
 *   injectReadingTime()
 */
export function injectReadingTime() {
  if (typeof window === 'undefined') return
  if (typeof document === 'undefined') return

  function update() {
    const article = document.querySelector('.vp-doc')
    if (!article) return

    // 避免重复插入
    let badge = article.querySelector<HTMLElement>('.at-reading-time')
    if (!badge) {
      badge = document.createElement('div')
      badge.className = 'at-reading-time'
      article.insertBefore(badge, article.firstChild)
    }

    // 抓取正文文本
    const text = article.innerText || article.textContent || ''
    const minutes = readingTime(text)
    badge.textContent = `📖 ${formatReadingTime(minutes)} · ${countWords(text).toLocaleString()} 字`
  }

  // 初始 + 路由切换
  setTimeout(update, 100)

  // VitePress SPA 路由
  const observer = new MutationObserver(() => setTimeout(update, 200))
  observer.observe(document.body, { childList: true, subtree: true })

  // 30s 后停止
  setTimeout(() => observer.disconnect(), 30_000)
}
