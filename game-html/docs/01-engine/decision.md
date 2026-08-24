---
title: 选型决策
---

# 选型决策

> 引擎选型四问：平台目标 / 团队规模 / 预算 / 性能需求。

## 🎯 核心要点

- 平台目标：移动端 → Unity；PC/主机 3A → Unreal；2D 独立 → Godot
- 团队规模：< 10 人用现成引擎；50+ 人可考虑自研
- 预算：Unreal 5% 营收分成，Unity 订阅费，Godot 免费
- 性能需求：移动端 Unity；高画质 Unreal；轻量 Godot

## 🛠️ 实战示例

```text
# 决策清单（伪代码）
if 平台 == 移动 and 玩法 == 休闲:
    选择 Unity
elif 平台 == 主机 or 画质要求 == 顶级:
    选择 Unreal
elif 团队规模 == 1-3 or 类型 == 2D:
    选择 Godot
else:
    评估自研
```

## 🔗 相关链接

- [商业引擎](./commercial)
- [渲染](../02-render/pipeline)
- [← 返回 引擎层 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[商业引擎](./commercial)

## 🛠️ 实战提示

决策树：先看平台，再看团队，最后看预算。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)
