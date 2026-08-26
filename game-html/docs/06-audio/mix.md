---
title: 动态混音
---

# 动态混音

> 动态混音：Snapshot（场景切换）+ 实时参数（情绪/战斗）+ 音效总线（路由）。

## 🎯 核心要点

- Snapshot：预设混音状态（探索 / 战斗 / Boss）
- 实时参数：根据玩家状态动态调整（低血量增心跳）
- 音效总线：Master / Music / SFX / Voice 分层
- 工具：Wwise / FMOD 状态机驱动

## 🛠️ 实战示例

```cpp
// Wwise RTPC（实时参数）
// 设置血量参数（0-100）
AK::SoundEngine::SetRTPCValue("PlayerHealth", player.health);
// 低血量时心跳音效更明显
// 在 Wwise 中绑定 RTPC → HeartBeat Volume
```

## 🔗 相关链接

- [空间音频](./spatial)
- [音频引擎](./engine)
- [← 返回 音频 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[动态混音](./mix) / [音频引擎](./engine)

## 🛠️ 实战提示

Wwise 用 RTPC 实现动态混音。

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
