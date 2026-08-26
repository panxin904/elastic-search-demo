---
title: 联机架构
---

# 联机架构

> 联机架构：C/S 房间制 / P2P Host 迁移 / Matchmaker 匹配系统。

## 🎯 核心要点

- C/S 房间制：MMO / MOBA 主流（大厅 + 房间服务器）
- P2P：CS / DotA 早期模式，Host 迁移复杂
- 专用服务器：3A FPS 主流（Valorant / CS:GO）
- Matchmaker：基于 ELO / MMR 匹配（Open Skill / TrueSkill）

## 🛠️ 实战示例

```python
# Matchmaker 简化（ELO）
def match(players):
  # 按分数排序
  players.sort(key=lambda p: p.rating)
  # 分组
  return [(players[i], players[i+1]) for i in range(0, len(players), 2)]
# 评分更新
def update_rating(winner, loser, k=32):
  expected = 1 / (1 + 10 ** ((loser.rating - winner.rating) / 400))
  winner.rating += k * (1 - expected)
  loser.rating -= k * (1 - expected)
```

## 🔗 相关链接

- [同步模型](./sync)
- [上线运营](../08-ship/launch)
- [← 返回 网络 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[同步模型](./sync) / [上线运营](../08-ship/launch)

## 🛠️ 实战提示

Matchmaker 算法：ELO / TrueSkill / Open Skill。

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
