---
title: Jetpack Compose
---

# Jetpack Compose

> 声明式 UI 框架，Kotlin DSL + 状态驱动 + 自动重组（Recomposition）。

## 🎯 核心要点

- 状态管理：State / MutableState / remember / rememberSaveable
- Modifier 链：顺序决定行为（padding 后点击 vs 点击后 padding）
- Material 3：动态颜色 / 主题切换
- 重组优化：稳定参数 + Lambda memoization + derivedStateOf

## 🛠️ 实战示例

```kotlin
@Composable
fun Counter() {
  var count by remember { mutableStateOf(0) }
  Button(onClick = { count++ }) {
    Text("Clicked $count times")
  }
}
```

## 🔗 相关链接

- [视图系统](./view-system)
- [性能优化](../06-perf/performance)
- [← 返回 UI 体系 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：@Stable / @Immutable 标注可重组稳定类
- **小贴士**：Lambda 用 remember 包裹避免重组失效
- **小贴士**：derivedStateOf 派生状态减少不必要的重组


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)

- **官方文档**：developer.android.com/jetpack/compose。


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
