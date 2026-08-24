---
title: 性能与安全
---

# 06 · 性能与安全

性能与安全：启动 / 内存 / ANR / 权限 / 加密。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [性能优化](./performance) | 启动 / Baseline Profile / 内存 / ANR / 包大小 |
| [安全机制](./security) | 权限 / Scoped Storage / Network Security / Keystore |

## 🎯 选型决策

- **性能**：先 Profile 后优化（避免过早优化）
- **安全**：默认权限最小化 + HTTPS + ProGuard/R8
- **合规**：用户隐私 + 数据加密 + 第三方 SDK 审计

## 📚 学习路径

- **入门**：LeakCanary + Macrobenchmark + StrictMode
- **进阶**：Perfetto + Baseline Profile + R8 规则
- **高级**：ART 源码 + Choreographer + Kernel Scheduler

## 📝 章节目录

- `06-perf/performance`：启动 / 内存 / ANR
- `06-perf/security`：权限 / 加密 / 证书

- **小贴士**：性能优化先 Profile 后优化
- **小贴士**：安全从设计阶段就考虑（最小权限原则）


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)
