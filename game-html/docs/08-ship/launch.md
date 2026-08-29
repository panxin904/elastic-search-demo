---
title: 上线运营
date: 2026-08-27  # date-auto-injected
---

# 上线运营

> 游戏上线：多平台适配 / 主机认证 / 反作弊 / 数据埋点 / 运营活动。

## 🎯 核心要点

- 多平台：PC（Steam / Epic）/ 主机（PS/Xbox/Switch）/ 移动（iOS/Android）
- 主机认证：Sony / Microsoft / Nintendo TRC 认证
- 反作弊：EAC / BattlEye + 自研检测
- 数据埋点：玩家行为 + 付费漏斗 + 关卡热度

## 🛠️ 实战示例

```csharp
# 数据埋点（Unity Analytics）
using UnityEngine.Analytics;
Analytics.CustomEvent("level_complete", new Dictionary<string, object> {
  {"level_id", 3},
  {"time_spent", 120.5f},
  {"deaths", 2}
});
```

## 🔗 相关链接

- [性能优化](./perf)
- [构建发布](../07-toolchain/build)
- [← 返回 性能与上线 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[性能优化](./perf) / [构建发布](../07-toolchain/build)

## 🛠️ 实战提示

多平台适配：先 Steam PC，再移植到主机 / 移动。

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
