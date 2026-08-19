# Mermaid 跨站共享配置

> vitepress-plugin-mermaid v2 跨站配置参考（fontFamily / fontSize / 品牌色 themeVariables）。
> 详见 §8.46（C11 图片/图表优化收尾）。

## 文件

| 文件 | 导出 | 用途 |
|------|------|------|
| `base.ts` | `mermaidBase` / `mermaidTheme(brand)` | 配置模板的内联同步源与维护参考 |

## 设计

- **`mermaidBase`** — 基础安全配置 + 跨站一致的字体 / 字号 / 主题
  - `securityLevel: 'loose'`：允许 mermaid 内嵌图片 / 链接（教学场景常用）
  - `theme: 'base'`：base 主题才能让 `themeVariables` 完整生效
  - `fontFamily`：与 VitePress 全局一致（Inter → PingFang SC → Microsoft YaHei → system）

- **`mermaidTheme(brand)`** — 站点专属 themeVariables
  - 主节点色 = `brand`（站点品牌色 hex）
  - 次节点色 = `brand` 调亮 85%（节点背景）
  - 文本色 / 连线色中性化（避免抢主色）

## 加载约束

`shared-assets/mermaid-config/base.ts` **不作为运行时模块 import**：

- Vite alias（`@shared`）只在 Vite/Rollup 阶段生效，不参与 Node ESM 加载 `config.mts`
- `vitepress-plugin-mermaid` 的 `virtual:mermaid-config` 会在配置加载阶段读取 `mermaid` 字段
- 因此 `config.mts.tpl` 与已应用站点直接内联 `mermaidBase` / `mermaidTheme`

`base.ts` 是同步源和人工复核依据。修改字段时必须同步更新：

1. `shared-assets/mermaid-config/base.ts`
2. `shared-assets/vitepress-template/config.mts.tpl`
3. 实际应用该配置的两个 Mermaid 站点

## 暗色模式

`vitepress-plugin-mermaid` v2 在 `Mermaid.vue` 里 `MutationObserver` 检测 `<html>` 的 `.dark` class，自动把 `theme` 切到 `'dark'`。`themeVariables` **不变**（mermaid 不支持 CSS var() 表达式）：

- 暗色模式下 `themeVariables.primaryColor` 仍是站点品牌色 hex
- mermaid `dark` 主题自动用深色背景 / 浅色文本
- 视觉结果：节点主色与品牌色一致（亮 / 暗都一样），背景 / 文本由 mermaid `dark` 主题接管

## 使用示例

### config.mts（springcloud-html）

```ts
export default withMermaid(defineConfig({
  ...
  mermaid: {
    ...mermaidBase,
    themeVariables: mermaidTheme('#6DB33F'),
  },
  ...
}))
```

### 模板（config.mts.tpl）

```ts
export default withMermaid(defineConfig({
  ...
  mermaid: {
    ...mermaidBase,
    themeVariables: mermaidTheme('@SITE_ACCENT'),
  },
  ...
}))
```

## 验证

- 重新 build 后，mermaid 节点主色 = 站点品牌色
- 切换暗色模式，节点主色不变，背景变深
- SVG 文本字体 = `Inter, PingFang SC, ...`
