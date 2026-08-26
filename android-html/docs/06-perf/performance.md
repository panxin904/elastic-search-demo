---
title: 性能优化
---

# 性能优化

> Android 性能五大维度：启动 / 内存 / 流畅度 / 包大小 / 电量。

## 🎯 核心要点

- 启动优化：冷启动 < 1.5s（推荐 < 1s）+ Baseline Profile
- 内存：避免 OOM + 内存泄漏（LeakCanary 检测）
- 流畅度：Jank < 5%，Choreographer 监控
- ANR：主线程 5s 无响应（Input 2s）
- 包大小：APK Analyzer + R8 + 资源压缩

## 🛠️ 实战示例

```kotlin
# Macrobenchmark 启动性能测试（Kotlin）
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
  @Test
  fun startup() = benchmarkRule.measureRepeated {
    pressHome()
    startActivityAndWait()
  }
}
```

## 🔗 相关链接

- [ART 运行时](../03-system/runtime)
- [安全机制](./security)
- [← 返回 性能与安全 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：启动分三段：Application → Activity → 第一帧
- **小贴士**：Baseline Profile 用 macrobenchmark 生成
- **小贴士**：内存抖动用 Allocation Tracker 检测


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)

- **官方文档**：developer.android.com/topic/performance。


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
