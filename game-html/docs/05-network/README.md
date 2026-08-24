---
title: 网络
---

# 05 · 网络

游戏网络：同步 / 一致性 / 反外挂 / 联机架构。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [同步模型](./sync) | 状态 / 帧同步 / 快照 |
| [一致性](./consistency) | 客户端预测 / 服务器仲裁 / 回放 |
| [反外挂](./anticheat) | 服务器权威 / 加密 / 行为检测 |
| [联机架构](./arch) | C/S / P2P / Matchmaker |

## 🎯 选型决策

- **MOBA / MMO**：状态同步 + 服务器权威
- **RTS**：帧同步 + 确定性
- **FPS**：快照同步 + 客户端预测
- **反外挂**：关键逻辑放服务器 + EAC / BattlEye

## 📚 学习路径

- **入门**：Photon / Mirror 框架
- **进阶**：自研同步协议 + 预测 / 回滚
- **高级**：反作弊 + Matchmaker 算法


## 📝 章节目录

[同步模型](./sync) / [一致性](./consistency) / [反外挂](./anticheat) / [架构](./arch)

## 🛠️ 实战提示

联机游戏三大难题：同步、一致性、反外挂。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)
