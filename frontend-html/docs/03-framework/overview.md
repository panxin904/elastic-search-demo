---
title: UI 框架总览与选型
---

# UI 框架总览与选型

> 框架是手段，不是目的。先用对场景，再选技术栈。

## 📊 主流框架对比

| 框架 | 学习曲线 | 生态 | 体积 | 适用场景 |
|------|---------|------|------|---------|
| React | 中等 | 极大 | ~45KB | 通用首选、大型企业 / SaaS |
| Vue | 平缓 | 大 | ~33KB | 中文社区、上手快、中后台 |
| Angular | 陡 | 大 | 130KB+ | 企业级大型应用、复杂表单 |
| Svelte | 平缓 | 中 | ~12KB | 性能敏感、独立产品 |
| Solid | 中等 | 小 | ~7KB | 性能敏感、组件级订阅 |

## 🎯 选型维度

```
1. 团队熟悉度       — 选大家都能上手的
2. 项目规模        — 大项目看生态、文档
3. 性能要求        — 高交互（编辑器、可视化）选 Svelte/Solid
4. 招聘难度        — React/Vue 池子最大
5. SEO / SSR      — 是否有现成元框架支持
6. 第三方组件库    — Ant Design (React/Angular?)、Element Plus (Vue)、Arco (React/Vue)
```

## 📈 各框架核心心智模型

| 框架 | 核心范式 |
|------|----------|
| React | 函数式 + 单向数据流 + 不可变状态 |
| Vue | 反应式 ref + 计算属性 + 模板/渲染函数 |
| Angular | DI + RxJS + Zone.js |
| Svelte | 编译时响应式 + 简洁语法 |
| Solid | 细粒度响应式（无虚拟 DOM） |

## 🧩 跨框架方案

- **Web Components**：浏览器原生，但生态弱
- **Lit**：轻量封装 Web Components
- **Stencil**：Angular 团队出品的编译器

```html
<script type="module">
  import 'https://cdn.jsdelivr.net/npm/lit@3/+esm'
</script>
<my-element name="alice"></my-element>
```

## 🛠️ 状态管理选型

| 规模 | 推荐 |
|------|------|
| 小型 / 一个表单 | `useState` / `ref` |
| 中型 | Zustand / Pinia |
| 大型 / 多人协作 | Redux Toolkit / Pinia |
| 服务端数据 | React Query / SWR / VueQuery |

## 📦 常见误区

1. **不要追新**：团队熟练 > "新潮"
2. **框架是工具**：业务沉淀比框架重要
3. **大型项目也用 React**：但要锁版本 + 强 lint
4. **Vue 3 完全能打**：Composition API 与 Hooks 心智一致

## 🔗 下一步

- [React 核心与 Hooks](/03-framework/react)
- [Vue 3 组合式 API](/03-framework/vue)
- [Next.js](/04-meta/nextjs)
