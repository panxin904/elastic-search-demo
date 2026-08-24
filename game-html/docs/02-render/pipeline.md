---
title: 渲染管线
---

# 渲染管线

> 四大主流渲染管线：前向 / 延迟 / Clustered / 光线追踪，各有适用场景。

## 🎯 核心要点

- 前向渲染：移动端首选（low power），带宽低
- 延迟渲染：PC / 主机主流，多光源场景好
- Clustered / Tiled：Forward+ / Deferred+，效率与质量兼顾（UE5 默认）
- 光线追踪：电影级画质，硬件要求高（RTX / PS5 / XSX）

## 🛠️ 实战示例

```text
// Unreal 选择渲染管线（Project Settings → Rendering）
// Deferred Shading（默认 PC/主机）
// Forward Shading（VR / 移动端）
// Forward+ / Deferred+
```

## 🔗 相关链接

- [光照](./lighting)
- [着色器](./shader)
- [← 返回 渲染 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[光照](./lighting) / [着色器](./shader)

## 🛠️ 实战提示

引擎默认管线足够多数项目，需要时切到 Forward+。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)
