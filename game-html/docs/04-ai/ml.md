---
title: 机器学习 AI
---

# 机器学习 AI

> 游戏 AI 与机器学习结合：强化学习（RL）/ 神经网络 NPC / 群体模拟 Boids。

## 🎯 核心要点

- 强化学习（RL）：DQN / PPO 训练 NPC 策略
- 神经网络 NPC：模仿学习 / 决策网络
- Boids：群体行为（鸟群 / 鱼群）
- 应用：赛车 AI / RTS 微操 / NPC 对话生成

## 🛠️ 实战示例

```python
# Stable Baselines3 DQN 训练 CartPole
from stable_baselines3 import DQN
model = DQN("MlpPolicy", "CartPole-v1", verbose=1)
model.learn(total_timesteps=10_000)
```

## 🔗 相关链接

- [决策系统](./decision)
- [联机架构](../05-network/arch)
- [← 返回 AI 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[决策系统](./decision)

## 🛠️ 实战提示

ML-Agents 是 Unity 的强化学习框架，适合实验。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)

- **实战提示**：从引擎默认配置入手，按需自定义。
- **官方文档**：参考 Unity / Unreal / Godot 最新 LTS 版本。
