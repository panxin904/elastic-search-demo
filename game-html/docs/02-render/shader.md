---
title: 着色器
---

# 着色器

> HLSL（GLSL/MSL/Slang）+ Shader Graph 可视化 + Compute Shader 通用计算。

## 🎯 核心要点

- HLSL：DirectX + Xbox + PC，Unity ShaderLab / UE Material 编译为目标
- GLSL：Vulkan / OpenGL，跨平台
- Shader Graph：节点式可视化（Unity / UE 都有），适合美术
- Compute Shader：GPU 通用计算（GPGPU），用于粒子 / 后处理 / AI

## 🛠️ 实战示例

```hlsl
// HLSL Compute Shader 示例
[numthreads(8,8,1)]
void CSMain(uint3 id : SV_DispatchThreadID) {
  Result[id.xy] = float4(id.x / 255.0, id.y / 255.0, 0.5, 1.0);
}
```

## 🔗 相关链接

- [光照](./lighting)
- [后处理](./postprocess)
- [← 返回 渲染 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[光照](./lighting) / [后处理](./postprocess)

## 🛠️ 实战提示

Shader Graph 适合美术，手写 HLSL 适合性能关键路径。

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
