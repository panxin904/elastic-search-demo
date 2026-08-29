---
title: 音频引擎
date: 2026-08-27  # date-auto-injected
---

# 音频引擎

> 游戏音频中间件：Wwise / FMOD / 引擎内置音频（Unity Audio / Unreal Sound）。

## 🎯 核心要点

- Wwise（Audiokinetic）：行业标准，AAA 主流，按授权收费
- FMOD：轻量 + 集成简单，独立 / 中型项目主流
- 内置：Unity Audio / Unreal Sound，简单场景够用
- 选型：3A → Wwise；中型 → FMOD；休闲 → 内置

## 🛠️ 实战示例

```csharp
# FMOD 事件触发（Unity C#）
RuntimeManager.PlayOneShot("event:/SFX/Explosion", transform.position);
# 事件驱动：美术 / 音频设计师配置，无需改代码
```

## 🔗 相关链接

- [空间音频](./spatial)
- [动态混音](./mix)
- [← 返回 音频 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[空间音频](./spatial) / [动态混音](./mix)

## 🛠️ 实战提示

Wwise / FMOD 都提供可视化编辑器。

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
