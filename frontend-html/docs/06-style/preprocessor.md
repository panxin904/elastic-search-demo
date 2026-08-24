---
title: CSS 预处理器
---

# CSS 预处理器

## 🎯 Sass / SCSS / Less

```scss
// scss 语法
$primary: #06b6d4;

.button {
  background: $primary;
  &:hover { background: darken($primary, 10%); }

  &.large {
    padding: 16px 24px;
    font-size: 18px;
  }

  @media (max-width: 768px) {
    padding: 8px 16px;
  }
}
```

特性：
- **变量** `$var`
- **嵌套** `&`
- **mixin** `@mixin` / `@include`
- **继承** `@extend`
- **运算** `+`、`*`、`darken()`

## ⚠️ 现代 CSS 已能覆盖大部分场景

| 需求 | 旧（SCSS） | 现在 |
|------|-----------|------|
| 变量 | `$primary` | `--var-primary` |
| 嵌套 | Sass | CSS Nesting (Chrome 120+) |
| 函数 | `@mixin` | CSS Custom Functions Draft |
| 复用 | `@extend` | `@layer` / `@scope` |

## 🎯 还值得用 SCSS 的场景

- 设计 token 是变量集合且团队规模大
- 主题切换需要做编译时差异
- 想用 `@function` 做复杂计算

否则**直接用现代 CSS + 自定义属性**会更轻量。

## 🔗 下一步

- [Tailwind / UnoCSS](/06-style/tailwind)
- [CSS Modules](/06-style/css-modules)
## 🎯 现代 CSS 工程化建议

- 中小项目：原生 CSS + 自定义属性（无需 SCSS 编译）
- 大型项目 / 设计系统：用 SCSS 维护 token + 设计规范
- 工具替代：Tailwind / UnoCSS 提供 utility-first 思维，比 SCSS 更适合组件化
- PostCSS 插件链：autoprefixer + postcss-preset-env（无需 SCSS 也能用未来语法）

迁移建议：旧 SCSS 项目不必强制迁移，渐进式替换即可。
