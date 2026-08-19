/**
 * Mermaid 基础配置 — 跨子站共享
 *
 * vitepress-plugin-mermaid v2 的 mermaid 字段会被 JSON.stringify 注入到
 * virtual:mermaid-config 模块。Mermaid.vue 在 onMounted 时加载并与默认设置合并。
 *
 * 设计目标：
 *   1. 跨站视觉一致（字体 / 字号 / 安全设置）
 *   2. 暗色模式由 plugin 自动切 theme='dark'，themeVariables 保持不变
 *   3. 各站通过 spread 加 themeVariables 注入品牌色
 *
 * 使用（config.mts.tpl / 已生成 config.mts）：
 *   不从 config.mts 阶段 import 本文件：Vite alias 不会参与 Node ESM 解析。
 *   由渲染器将下面 mermaidBase + mermaidTheme 内联到 VitePress 配置。
 *   修改共享字段时，请同步更新 config.mts.tpl 与已应用的两个站点。
 */
export const mermaidBase = {
  securityLevel: 'loose',     // 允许 mermaid 块内嵌图片 / 链接（教学场景常用）
  startOnLoad: false,         // VitePress SPA 模式下禁用自动启动，由 Mermaid.vue 接管
  theme: 'base',              // 用 base 主题，让 themeVariables 完整生效
  fontFamily: '"Inter", "PingFang SC", "Microsoft YaHei", system-ui, -apple-system, sans-serif',
} as const

/**
 * 生成站点专属 themeVariables（基于品牌色 hex）
 *
 * themeVariables 是 mermaid 内置变量集（颜色 / 字体 / 字号），覆盖默认 base 主题。
 * 字段集参考 https://mermaid.js.org/schemas/config.themeVariables.html
 *
 * @param brand 主色 hex（如 '#6DB33F'），用于节点边框 / 文本色 / 连线高亮
 * @returns themeVariables 对象，spread 到 mermaid 配置即可
 */
export function mermaidTheme(brand: string): Record<string, string> {
  // 推导浅色背景（主色 + 高透明度 → 节点背景）
  // mermaid 接受 hex，不接受 rgba()，所以预生成近似色
  const soft = lightenHex(brand, 0.85)  // 节点背景（≈85% 透明度叠白）
  const ink = '#1f2937'                 // 主文本色（中性深灰，跨站一致）
  const line = '#94a3b8'                // 连线色（中性灰，不抢主色）
  return {
    primaryColor: brand,           // 节点填充色
    primaryTextColor: ink,         // 节点文字色
    primaryBorderColor: brand,     // 节点边框色
    lineColor: line,               // 连线色
    secondaryColor: soft,          // 次要节点填充色（如 subgraph 嵌套）
    tertiaryColor: '#fafafa',      // 背景底色
    fontFamily: mermaidBase.fontFamily,
    fontSize: '14px',
  }
}

/**
 * hex 颜色调亮（往白色方向混合 alpha）
 *
 * 纯 hex 不能表达透明度，但 mermaid 渲染节点时会用 background 叠加。
 * 把 brand hex 调到 85% 亮度（接近白），视觉上等价于原色 + 透明叠加。
 *
 * @param hex 原始颜色（如 '#6DB33F'）
 * @param ratio 0=原色，1=白色
 */
function lightenHex(hex: string, ratio: number): string {
  const m = hex.replace('#', '').match(/^([0-9a-f]{6})$/i)
  if (!m) return hex
  const r = parseInt(m[1].slice(0, 2), 16)
  const g = parseInt(m[1].slice(2, 4), 16)
  const b = parseInt(m[1].slice(4, 6), 16)
  const mix = (c: number) => Math.round(c + (255 - c) * ratio)
  return '#' + [mix(r), mix(g), mix(b)].map(c => c.toString(16).padStart(2, '0')).join('')
}
