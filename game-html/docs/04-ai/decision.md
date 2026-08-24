---
title: 决策系统
---

# 决策系统

> NPC 决策：FSM（状态机）/ BT（行为树）/ Utility AI / GOAP（目标导向行动规划）。

## 🎯 核心要点

- FSM：简单状态切换，适合小型 NPC
- BT（行为树）：模块化 + 可视化，AAA 标准
- Utility AI：基于效用函数，适合复杂决策
- GOAP：规划式，模拟真实思考过程

## 🛠️ 实战示例

```text
// 行为树节点（伪代码）
Selector
├── Sequence
│   ├── HasEnemy?
│   └── Attack
└── Patrol
```

## 🔗 相关链接

- [寻路](./pathfinding)
- [机器学习](./ml)
- [← 返回 AI 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[寻路](./pathfinding)

## 🛠️ 实战提示

行为树是 AAA 标准，BehaviorTree 可视化节点（UE 内置）。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)

- **实战提示**：从引擎默认配置入手，按需自定义。
- **官方文档**：参考 Unity / Unreal / Godot 最新 LTS 版本。
