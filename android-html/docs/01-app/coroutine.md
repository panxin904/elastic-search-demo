---
title: Kotlin 协程
date: 2026-08-27  # date-auto-injected
---

# Kotlin 协程

> Kotlin 协程：轻量级线程（百万级并发）+ 结构化并发 + 取消传播。

## 🎯 核心要点

- Dispatchers：Main（UI）/ IO（网络磁盘）/ Default（CPU）
- Scope 层级：GlobalScope / viewModelScope / lifecycleScope
- 异常处理：CoroutineExceptionHandler / SupervisorJob
- Channel / Flow：冷热流、背压、组合操作符

## 🛠️ 实战示例

```kotlin
// 并行请求 + 组合
suspend fun fetchDashboard(): Dashboard = coroutineScope {
  val user = async { api.getUser() }
  val posts = async { api.getPosts() }
  Dashboard(user.await(), posts.await())
}
```

## 🔗 相关链接

- [Jetpack](./jetpack)
- [性能优化](../06-perf/performance)
- [← 返回 应用层 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：ViewModel 销毁时 viewModelScope 自动取消，避免泄漏
- **小贴士**：用 SupervisorJob 让子协程失败不影响父
- **小贴士**：Flow 用 shareIn / stateIn 共享，避免重复订阅


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)

- **官方文档**：kotlinlang.org/docs/coroutines-overview.html。


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
