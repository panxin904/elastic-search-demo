---
title: 光照与阴影
---

# 光照与阴影

> PBR 物理光照 + IBL 间接光 + 全局光照（GI）+ 阴影算法。

## 🎯 核心要点

- PBR（Physically Based Rendering）：基于物理的 BRDF（金属 / 粗糙度）
- IBL（Image Based Lighting）：环境贴图采样，模拟间接光
- GI（Global Ill）：实时光追（Lumen / RT）/ 烘焙（Lightmap）
- 阴影：Shadow Map / Cascaded Shadow Map（CSM）/ VSM / 软阴影

## 🛠️ 实战示例

```hlsl
// HLSL PBR 计算（简化版）
float3 BRDF(float3 albedo, float metallic, float roughness, float3 L, float3 V, float3 N) {
  float3 H = normalize(L + V);
  float NdotL = max(dot(N, L), 0.0);
  float NdotH = max(dot(N, H), 0.0);
  float D = DistributionGGX(NdotH, roughness);
  float G = GeometrySmith(NdotL, dot(N,V), roughness);
  return (albedo * (1-metallic) + F0) * D * G / (4 * NdotL);
}
```

## 🔗 相关链接

- [渲染管线](./pipeline)
- [着色器](./shader)
- [← 返回 渲染 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[渲染管线](./pipeline) / [着色器](./shader)

## 🛠️ 实战提示

PBR 是工业标准，UE5 的 Lumen 简化了实时光照配置。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)
