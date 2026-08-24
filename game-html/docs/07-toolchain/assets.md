---
title: 资产管线
---

# 资产管线

> 资产管线：FBX / glTF 模型 + LOD 生成 + 纹理压缩 + Addressable 加载。

## 🎯 核心要点

- 模型格式：FBX（DCC 通用） / glTF（开放标准）
- LOD（Level of Detail）：远距离用低模 + 减少 Draw Call
- 纹理压缩：ASTC（移动）/ BC（PC）/ ETC2（OpenGL ES）
- 加载：Addressable（Unity 按需加载） / AssetBundle

## 🛠️ 实战示例

```csharp
# Unity Addressable 加载
using UnityEngine.AddressableAssets;
var handle = Addressables.LoadAssetAsync<GameObject>("Player");
yield return handle;
Instantiate(handle.Result);
```

## 🔗 相关链接

- [版本控制](./vcs)
- [构建发布](./build)
- [← 返回 工具链 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[版本控制](./vcs)

## 🛠️ 实战提示

Addressable 按需加载，避免一次性加载所有资源。

## 🔗 延伸阅读

- [GameDev.net](https://www.gamedev.net/)
- [GDC Vault](https://www.gdcvault.com/)
- [Unity Manual](https://docs.unity3d.com/Manual/index.html)
- [Unreal Engine Docs](https://docs.unrealengine.com/)

- **实战提示**：从引擎默认配置入手，按需自定义。
- **官方文档**：参考 Unity / Unreal / Godot 最新 LTS 版本。
