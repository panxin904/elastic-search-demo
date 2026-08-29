---
title: 性能优化
date: 2026-08-27  # date-auto-injected
---

# 性能优化

> 游戏性能五大维度：Draw Call / GC / 内存池 / 帧率稳定 / 移动端功耗。

## 🎯 核心要点

- Draw Call：合批（Batching）+ GPU Instancing + SRP Batcher
- GC：避免频繁 new + 对象池
- 内存池：复用对象（子弹 / 粒子）
- 帧率稳定：Profiler 找热点（CPU / GPU / IO）
- 移动端：降分辨率 + 限制后处理

## 🛠️ 实战示例

```csharp
// Unity Profiler 实时分析
Profiler.BeginSample("PlayerUpdate");
// ... 玩家逻辑 ...
Profiler.EndSample();

// GPU Profiler：Frame Debugger 看 Draw Call
```

## 🔗 相关链接

- [渲染管线](../02-render/pipeline)
- [上线运营](./launch)
- [← 返回 性能与上线 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[渲染管线](../02-render/pipeline) / [上线运营](./launch)

## 🛠️ 实战提示

先 Profiler 后优化，避免过早优化。

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
