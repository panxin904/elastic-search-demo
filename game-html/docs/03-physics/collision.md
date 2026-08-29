---
title: 碰撞检测
date: 2026-08-27  # date-auto-injected
---

# 碰撞检测

> 碰撞检测基础：AABB / OBB / GJK / SAT + 空间分割（四叉树 / BVH / NavMesh）。

## 🎯 核心要点

- AABB：轴对齐包围盒，O(1) 检测，精度低
- OBB：旋转包围盒，更精确
- GJK：凸体碰撞，O(log n)
- SAT：分离轴定理
- 空间分割：四叉树（2D）/ 八叉树（3D）/ BVH / NavMesh

## 🛠️ 实战示例

```csharp
// Unity AABB 检测
bool AABBOverlap(Bounds a, Bounds b) {
  return a.min.x <= b.max.x && a.max.x >= b.min.x &&
         a.min.y <= b.max.y && a.max.y >= b.min.y &&
         a.min.z <= b.max.z && a.max.z >= b.min.z;
}
```

## 🔗 相关链接

- [刚体动力学](./rigidbody)
- [寻路](../04-ai/pathfinding)
- [← 返回 物理 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[刚体动力学](./rigidbody) / [寻路](../04-ai/pathfinding)

## 🛠️ 实战提示

引擎内置 Collider 够用，自定义检测用于复杂形状。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
