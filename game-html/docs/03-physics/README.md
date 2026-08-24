---
title: 物理
---

# 03 · 物理

游戏物理：碰撞 / 刚体 / 柔体。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [碰撞检测](./collision) | AABB / GJK / 空间分割 |
| [刚体动力学](./rigidbody) | Verlet / 约束 / PhysX |
| [柔体模拟](./softbody) | 弹簧质点 / 布料 / 流体 |

## 🎯 选型决策

- **简单碰撞**：引擎内置 Collider
- **复杂刚体**：PhysX / Bullet
- **布料 / 流体**：PBD / SPH（自研 / 插件）

## 📚 学习路径

- **入门**：引擎物理组件
- **进阶**：刚体积分 + 约束求解
- **高级**：GPU 物理 + 布料 / 流体模拟


## 📝 章节目录

[碰撞检测](./collision) / [刚体](./rigidbody) / [柔体](./softbody)

## 🛠️ 实战提示

游戏物理多数用 PhysX / Bullet，自研不划算。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)

- **实战提示**：从引擎默认配置入手，按需自定义。
- **官方文档**：参考 Unity / Unreal / Godot 最新 LTS 版本。
