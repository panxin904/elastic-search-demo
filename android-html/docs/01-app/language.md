---
title: Kotlin / Java / NDK
---

# Kotlin / Java / NDK

> Android 三大语言路径：Kotlin（首选）/ Java（遗留）/ C++ NDK（性能关键 + 跨平台）。

## 🎯 核心要点

- Kotlin：Google 2019 官方首选，null 安全 + 协程 + 扩展函数，Java 100% 互操作
- Java：遗留代码 + Android 11 以下设备支持
- C++ NDK：游戏 / 音视频 / 加密算法 / OpenGL 等性能敏感场景
- 选型：默认 Kotlin；性能瓶颈模块用 NDK；老项目逐步迁移

## 🛠️ 实战示例

```kotlin
// Kotlin: data class + 协程
data class User(val id: Long, val name: String)

suspend fun fetchUser(id: Long): User = withContext(Dispatchers.IO) {
    api.getUser(id)
}
```

## 🔗 相关链接

- [Kotlin 协程](./coroutine)
- [Jetpack](./jetpack)
- [← 返回 应用层 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：Kotlin 已成 Android 首选（官方推荐 + Google 自家应用已用）
- **小贴士**：NDK 模块用 CMake 编译，源码放 `app/src/main/cpp/`
- **小贴士**：Java 兼容模式仅用于遗留代码，新代码统一 Kotlin
