---
title: 同步模型
date: 2026-08-27  # date-auto-injected
---

# 同步模型

> 联机游戏三种同步模型：状态同步 / 帧同步（Lockstep）/ 快照同步。

## 🎯 核心要点

- 状态同步：服务器权威，发送状态，MOBA 主流
- 帧同步：所有客户端按帧执行相同输入，RTS 主流
- 快照同步：定期发完整快照，FPS 主流
- 选择：MOBA → 状态；RTS → 帧同步；FPS → 快照

## 🛠️ 实战示例

```text
# 状态同步示例（伪代码）
# 服务器
def on_player_move(player, target):
  player.position = target
  broadcast({"type": "move", "id": player.id, "pos": target})

# 客户端
def on_message(msg):
  if msg.type == "move":
    entities[msg.id].position = msg.pos
```

## 🔗 相关链接

- [一致性](./consistency)
- [反外挂](./anticheat)
- [← 返回 网络 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[一致性](./consistency) / [架构](./arch)

## 🛠️ 实战提示

同步模型选型决定后续所有架构。

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
