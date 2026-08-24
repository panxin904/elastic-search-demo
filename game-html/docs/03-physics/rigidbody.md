---
title: 刚体动力学
---

# 刚体动力学

> 刚体模拟：积分（Verlet / Euler）+ 约束求解 + 现成物理引擎（PhysX / Bullet / Havok）。

## 🎯 核心要点

- Verlet 积分：稳定 + 速度隐式
- Euler 积分：简单但易爆
- 约束求解：PBD（Position Based Dynamics）/ Sequential Impulse
- PhysX（NVIDIA）：Unity / Unreal 默认
- Bullet：开源，游戏 + 电影

## 🛠️ 实战示例

```csharp
// Unity Rigidbody + Force
void FixedUpdate() {
  rb.AddForce(transform.forward * thrust);
  rb.AddTorque(transform.up * torque);
}
```

## 🔗 相关链接

- [碰撞检测](./collision)
- [柔体模拟](./softbody)
- [← 返回 物理 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[碰撞检测](./collision) / [柔体模拟](./softbody)

## 🛠️ 实战提示

Verlet 积分稳定，适合布料；Euler 简单但易爆。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)

- **实战提示**：从引擎默认配置入手，按需自定义。
- **官方文档**：参考 Unity / Unreal / Godot 最新 LTS 版本。
