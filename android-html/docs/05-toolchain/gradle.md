---
title: 构建系统
---

# 构建系统

> Gradle KTS + AGP（Android Gradle Plugin）：模块化 + Build Variants + CI/CD。

## 🎯 核心要点

- Gradle KTS：Kotlin DSL（强类型 + IDE 补全）
- AGP 8+：编译缓存 + 增量注解处理
- Build Variants：productFlavors（多渠道包）
- CI/CD：GitHub Actions / GitLab CI + 缓存 ~/.gradle

## 🛠️ 实战示例

```kotlin
// app/build.gradle.kts
android {
  buildTypes {
    release {
      isMinifyEnabled = true
      proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
    }
  }
  flavorDimensions += "channel"
  productFlavors {
    create("google") { dimension = "channel" }
    create("huawei") { dimension = "channel" }
  }
}
```

## 🔗 相关链接

- [Android Studio](./ide)
- [发布与上架](./publish)
- [← 返回 工具链 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：构建缓存放 ~/.gradle/caches，CI 用本地缓存
- **小贴士**：KSP 替代 KAPT，编译快 2-3x
- **小贴士**：BuildConfig 字段用 buildConfigField 注入


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)

- **官方推荐**：AGP 8+ 配合 Gradle 8+。

- **实战提示**：用 `./gradlew assembleRelease` 编译 AAB 上架。
