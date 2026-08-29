---
title: Jetpack 套件
date: 2026-08-27  # date-auto-injected
---

# Jetpack 套件

> Google Jetpack 一站式 Android 架构组件，覆盖 UI / 数据 / 生命周期 / 依赖注入。

## 🎯 核心要点

- ViewModel：UI 数据持有者（屏幕旋转不丢）
- LiveData / Flow：响应式数据流
- Room：SQLite ORM
- Hilt：编译期 DI
- WorkManager：后台任务调度
- DataStore：替代 SharedPreferences

## 🛠️ 实战示例

```kotlin
// Hilt + ViewModel + Flow
@HiltViewModel
class UserViewModel @Inject constructor(
  private val repo: UserRepository
) : ViewModel() {
  val users: StateFlow<List<User>> = repo.usersFlow
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
}
```

## 🔗 相关链接

- [协程](./coroutine)
- [UI 体系](../02-ui/view-system)
- [← 返回 应用层 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：ViewModel + Hilt + Compose 是 Google 推荐的三件套
- **小贴士**：Room 用 KSP（Kotlin Symbol Processing）替代 KAPT，编译快 2x+
- **小贴士**：DataStore 替代 SharedPreferences，协程 + Flow 原生支持


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)


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

<!-- svg-injected:do-not-edit -->

## 图示：Jetpack Compose + ViewModel + Repository

![Jetpack Compose + ViewModel + Repository](/android-jetpack-arch.svg)
