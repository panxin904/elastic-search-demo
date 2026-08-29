---
title: Android 知识图谱
date: 2026-08-21  # date-auto-injected
---

# 🗺️ Android 知识图谱

> 本页用 Mermaid mindmap 展示 Android 全栈知识结构。

```mermaid
mindmap
  root((Android 安卓))
    应用层
      语言
        Kotlin
        Java
        C++ NDK
      Jetpack
        ViewModel
        LiveData / Flow
        Navigation
        Room / DataStore
        Hilt DI
        WorkManager
      协程
        Dispatchers
        Scope 层级
        异常处理
        Channel / Flow
    UI 体系
      视图系统
        Activity
        Fragment
        View 树
        RecyclerView
      Compose
        状态管理
        Modifier
        Material 3
        重组优化
        主题切换
      资源
        主题 / 颜色
        字符串 / 国际化
        屏幕适配
        Drawable
    系统层
      启动流程
        Boot ROM
        Bootloader
        Init 进程
        Zygote
        SystemServer
      IPC
        Binder
        AIDL
        Messenger
        ContentProvider
      运行时
        ART
        Dex2oat / AOT
        GC
        ClassLoader
      框架服务
        AMS
        WMS
        PMS
        IMS
    跨平台
      框架
        Flutter
        React Native
        Kotlin Multiplatform
        Compose Multiplatform
      决策
        性能 vs 一致性
        包大小 vs 开发效率
        团队能力
        业务场景
    工具链
      构建
        Gradle KTS
        AGP Plugin
        Build Variants
        CI/CD
      IDE
        Android Studio
        Profiler
        Layout Inspector
        APK Analyzer
      发布
        App Bundle
        Play Console
        Firebase
    性能与安全
      性能
        启动优化
        Baseline Profile
        内存 / OOM
        ANR / 卡顿
        包大小
      安全
        权限模型
        Scoped Storage
        Network Security Config
        密钥库 Keystore
        证书钉扎
```

## 阅读建议

- **应用开发者**：从 Jetpack → Compose → 协程 入手，再看性能章节
- **系统开发者**：启动流程 → IPC → ART 运行时 → 框架服务
- **跨端架构师**：先看跨平台决策树，再深入某一框架

## 在图谱中的位置

Android 是 frontend（客户端开发）+ java-language（JVM 基础）+ linux（底层 Kernel）+ iot（嵌入式延伸）的横切。如果只看应用层开发，前端基础就够；要做系统层或 NDK，需要补 linux + rust 基础。
