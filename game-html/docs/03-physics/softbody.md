---
title: 柔体模拟
---

# 柔体模拟

> 柔体（软体）模拟：弹簧质点 + 布料 + 流体 SPH，常用于角色头发 / 旗帜 / 爆炸。

## 🎯 核心要点

- 弹簧质点（Mass-Spring）：布料 / 软组织
- PBD（Position Based Dynamics）：稳定 + 实时
- SPH（Smoothed Particle Hydrodynamics）：流体
- XFEM / FEM：精确但昂贵（电影用）
- 性能：通常用 GPU + Compute Shader

## 🛠️ 实战示例

```text
// 弹簧质点更新（伪代码）
for each spring (a, b, restLength, stiffness):
  delta = positions[b] - positions[a]
  current = length(delta)
  offset = (current - restLength) / current * stiffness * dt
  positions[a] += delta * 0.5 * offset
  positions[b] -= delta * 0.5 * offset
```

## 🔗 相关链接

- [刚体动力学](./rigidbody)
- [物理](./)
- [← 返回 物理 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[刚体动力学](./rigidbody)

## 🛠️ 实战提示

布料 / 流体通常用商业中间件（Havok Cloth / NVIDIA Flex）。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)
