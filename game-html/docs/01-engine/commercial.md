---
title: 商业引擎选型
date: 2026-08-27  # date-auto-injected
---

# 商业引擎选型

> Unity / Unreal Engine / Godot 三大商业引擎对比，按场景选最适合的。

## 🎯 核心要点

- Unity：C# + 庞大生态 + Asset Store + 移动端霸主（Hyper Casual / 中小规模）
- Unreal：AAA + 图形（C++ / Nanite / Lumen）+ 主机 + PC 3A
- Godot：开源 + 轻量 + 2D 强 + 独立游戏
- 选型：移动休闲 → Unity；3A → Unreal；独立/2D → Godot

## 🛠️ 实战示例

```csharp
# Unity C# MonoBehaviour
using UnityEngine;

public class Player : MonoBehaviour {
  public float speed = 5f;
  void Update() {
    float h = Input.GetAxis("Horizontal");
    float v = Input.GetAxis("Vertical");
    transform.Translate(new Vector3(h, 0, v) * speed * Time.deltaTime);
  }
}
```

## 🔗 相关链接

- [自研引擎](./custom)
- [选型决策](./decision)
- [← 返回 引擎层 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[选型决策](./decision) / [自研引擎](./custom)

## 🛠️ 实战提示

试用 Unity / Unreal / Godot 的 LTS 版本，对比工具链和生态。

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
