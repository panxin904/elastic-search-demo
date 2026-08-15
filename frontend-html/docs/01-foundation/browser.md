---
title: 浏览器渲染原理
---

# 浏览器渲染原理

## 🏗️ 多进程架构

| 进程 | 职责 |
|------|------|
| Browser | 界面、Tab 管理、子进程协调 |
| Renderer | 单个 Tab 的渲染（HTML 解析、布局、绘制） |
| GPU | 加速绘制、3D CSS |
| Network | 网络请求 |
| Plugin | 第三方插件（已废弃） |

每个 Tab 默认一个 Renderer 进程（Site Isolation 后跨域 iframe 也是独立进程）。

## 🔄 Critical Rendering Path

```
HTML ──► 解析 ──► DOM
                          ─► Render Tree ─► Layout (布局) ─► Paint (绘制) ─► Composite (合成)
CSS ──► 解析 ──► CSSOM
JS ─► 执行 ─► 可能修改 DOM / CSSOM ─► 重新 Layout / Paint
```

### DOM 构建
- 边下载边解析（HTML Parser）
- 遇到 `<script>`（非 async/defer）会阻塞解析
- CSS 解析也会阻塞 JS 执行（避免 JS 读错样式）

### Render Tree
- 只包含**可见节点**（`display: none` 不进入）
- `visibility: hidden` 在，`<div>` 也在，但 `opacity: 0` 也还在

### Layout / Reflow
计算每个节点的位置和大小。**Layout 影响 Layout**（递归），代价高。

### Paint
绘制成位图（layer）。

### Composite
把多个 layer 合成一张图。**GPU 加速**：
- `transform`
- `opacity`
- `will-change`
- `position: fixed`

**只触发 Composite 的属性最便宜**，只触发 Paint 的次之，触发 Layout 的最贵。

```
Layout       ← width / height / padding / margin / display / position
Paint        ← color / background / visibility / box-shadow
Composite    ← transform / opacity / filter / will-change
```

## ⚡ 性能优化方向

1. **避免 Layout Thrashing**：批量读 / 批量写（先 `for` 读，再 `for` 写）
2. **动画用 transform/opacity**：避免触发 Layout
3. **CSS 放头部**：浏览器可以尽早解析
4. **JS 放底部 / defer**：避免阻塞解析
5. **字体加载策略**：`font-display: swap` / 预加载

## 📚 关键概念

- **CRP (Critical Rendering Path)**：关键渲染路径
- **First Paint (FP)**：第一个像素被绘制
- **FCP**：第一个内容渲染
- **LCP**：最大内容渲染
- **TBT**：主线程阻塞总时长
- **CLS**：累计布局偏移

## 🔗 下一步

- [Core Web Vitals](/12-perf/cwv)
- [加载性能 (CDN/SSR)](/12-perf/loading)
- [运行时性能](/12-perf/runtime)
