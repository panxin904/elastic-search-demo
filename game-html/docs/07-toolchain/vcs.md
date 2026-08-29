---
title: 版本控制
date: 2026-08-27  # date-auto-injected
---

# 版本控制

> 游戏版本控制：Git LFS（小团队） / Perforce Helix（大团队） + 分支策略。

## 🎯 核心要点

- Git LFS：大文件（美术资产）扩展，GitHub / GitLab 支持
- Perforce Helix：游戏行业标配，TB 级资产友好
- 分支策略：main / develop / feature/*
- 锁定文件：二进制资产（场景 / Prefab）避免冲突

## 🛠️ 实战示例

```bash
# Git LFS 跟踪大文件
git lfs install
git lfs track "*.fbx" "*.png" "*.wav"
git lfs track "*.unity" "*.prefab"
git add .gitattributes
```

## 🔗 相关链接

- [资产管线](./assets)
- [构建发布](./build)
- [← 返回 工具链 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[资产管线](./assets) / [构建发布](./build)

## 🛠️ 实战提示

Perforce 适合大团队，Git LFS 适合小团队。

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
