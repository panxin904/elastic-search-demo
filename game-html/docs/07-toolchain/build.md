---
title: 构建发布
date: 2026-08-27  # date-auto-injected
---

# 构建发布

> 构建发布：多平台构建脚本 + CI/CD（GitHub Actions / Jenkins） + 平台 SDK 接入。

## 🎯 核心要点

- 平台构建：Unity BuildPipeline / Unreal UAT
- CI/CD：GitHub Actions / Jenkins + 缓存 Library/
- Steam：Steamworks SDK + 上架审核
- 主机：Sony / Microsoft / Nintendo 认证流程（数月）

## 🛠️ 实战示例

```yaml
# GitHub Actions Unity Build 示例
- name: Build StandaloneLinux64
  run: |
    mkdir -p build/Linux
    /opt/unity/Editor/Unity \
      -batchmode -quit -nographics \
      -projectPath ${{ github.workspace }} \
      -buildTarget Linux64 \
      -executeMethod BuildScript.Linux64 \
      -logFile -
  env:
    UNITY_LICENSE: ${{ secrets.UNITY_LICENSE }}
```

## 🔗 相关链接

- [资产管线](./assets)
- [性能优化](../08-ship/perf)
- [← 返回 工具链 目录](./)
- [← 返回 game 首页](../)


## 📝 章节目录

[资产管线](./assets) / [性能优化](../08-ship/perf)

## 🛠️ 实战提示

CI/CD 用 Library 缓存，构建时间从 1h 降到 5min。

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
