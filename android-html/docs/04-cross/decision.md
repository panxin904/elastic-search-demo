---
title: 选型决策
---

# 选型决策

> 跨平台方案选型：性能 vs 一致性 / 包大小 / 团队能力 / 业务场景。

## 🎯 核心要点

- 性能要求高：原生（Kotlin / Swift）
- UI 一致性要求高：Flutter
- 团队 JS 强：React Native
- 只共享业务逻辑：KMP
- 业务场景：短视频/电商（Flutter）/ 中后台工具（RN）

## 🛠️ 实战示例

```text
# 决策清单（伪代码）
if (性能瓶颈 in 动画 OR 渲染) → Flutter
elif (团队主力是前端) → React Native
elif (Android + iOS 双端都要原生体验) → 原生 + KMP 共享逻辑
else → 原生开发
```

## 🔗 相关链接

- [跨平台框架](./frameworks)
- [性能优化](../06-perf/performance)
- [← 返回 跨平台 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：MVP / 验证期用 React Native（开发快）
- **小贴士**：用户量上来后逐步迁移到原生（性能 + 体验）
- **小贴士**：电商类业务优先 Flutter（UI 一致性要求高）
