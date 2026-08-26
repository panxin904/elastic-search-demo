---
title: 后处理
---

# 后处理

> 屏幕空间后处理：Bloom / DOF / SSAO / TAA / Color Grading，营造氛围。

## 🎯 核心要点

- Bloom：发光物体光晕
- DOF（Depth of Field）：景深虚化
- SSAO / HBAO：环境光遮蔽
- TAA（Temporal AA）：时序抗锯齿
- Color Grading：色调映射 + LUT

## 🛠️ 实战示例

```csharp
# Unity URP Post Processing Volume
var volume = gameObject.AddComponent<UnityEngine.Rendering.Volume>();
volume.profile = ScriptableObject.CreateInstance<UnityEngine.Rendering.VolumeProfile>();
var bloom = volume.profile.Add<UnityEngine.Rendering.Universal.Bloom>();
bloom.intensity.value = 1.5f;
```

## 🔗 相关链接

- [渲染管线](./pipeline)
- [性能优化](../08-ship/perf)
- [← 返回 渲染 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[渲染管线](./pipeline) / [性能优化](../08-ship/perf)

## 🛠️ 实战提示

后处理是 GPU 大户，移动端要谨慎。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)

- **实战提示**：从引擎默认配置入手，按需自定义。
- **官方文档**：参考 Unity / Unreal / Godot 最新 LTS 版本。


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
