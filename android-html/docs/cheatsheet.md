---
title: Android 速查表
date: 2026-08-21  # date-auto-injected
---

# 🧾 Android 速查表

> Gradle / Manifest / 常用命令 / 关键 API 一页速查。

## Gradle 关键配置

```kotlin
// build.gradle.kts
plugins {
    id("com.android.application") version "8.5.0" apply false
    id("org.jetbrains.kotlin.android") version "2.0.0" apply false
}

android {
    compileSdk = 34
    minSdk = 24
    targetSdk = 34
    buildFeatures { compose = true }
    defaultConfig {
        applicationId = "com.example.app"
        versionCode = 1
        versionName = "1.0.0"
        ndk { abiFilters += listOf("arm64-v8a") }
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
        }
    }
}
```

## AndroidManifest 常用标签

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <application android:allowBackup="false"
        android:networkSecurityConfig="@xml/network_security_config">
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

## ADB 常用命令

```bash
adb install app-debug.apk
adb install -r -d app.apk
adb uninstall com.example.app
adb shell am start -n com.example.app/.MainActivity
adb shell am force-stop com.example.app
adb logcat -s MyTag:V *:E
adb logcat -d | grep "FATAL EXCEPTION"
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png
adb shell screenrecord --time-limit 10 /sdcard/video.mp4
adb shell am start -W -n com.example.app/.MainActivity
adb shell dumpsys gfxinfo com.example.app
adb shell dumpsys meminfo com.example.app
adb devices -l
```

## 协程作用域

| 作用域 | 生命周期 | 典型用途 |
|---|---|---|
| GlobalScope | 整个应用进程 | 慎用 |
| MainScope | 手动管理 | 替代 GlobalScope |
| lifecycleScope | Activity/Fragment | UI 层业务 |
| viewModelScope | ViewModel | 业务逻辑 + 网络 |
| repeatOnLifecycle | 配合 lifecycleScope | Compose 收 Flow |
| 自定义 SupervisorJob | 自定义 | 后台任务 |

## 启动模式

| 模式 | 行为 | 用途 |
|---|---|---|
| standard | 每次新建实例 | 普通跳转 |
| singleTop | 栈顶复用 | 通知跳转 |
| singleTask | 栈内唯一 | 入口 Activity |
| singleInstance | 系统唯一 | 系统级分享 |

## 关键版本 API

| Android | API | 关键特性 |
|---|---|---|
| 14 | 34 | 强制 targetSdk |
| 13 | 33 | 通知权限运行时申请 |
| 12 | 31/32 | SplashScreen、Material You |
| 11 | 30 | Scoped Storage |
| 10 | 29 | 暗黑模式 |
| 9 | 28 | 自适应图标 |
| 8.0 | 26 | 通知渠道 |
| 7.0 | 24 | 多窗口 |
| 6.0 | 23 | 运行时权限 |

## 性能基线参考

| 指标 | 推荐值 | 工具 |
|---|---|---|
| 冷启动 | < 1.5s | Macrobenchmark |
| 热启动 | < 500ms | Logcat + am start |
| 首帧 FCP | < 1s | Choreographer |
| FPS | 60/90/120 | gfxinfo |
| 丢帧率 | < 1% | JankStats |
| ANR 率 | < 0.1% | Play Console |
| 内存峰值 | < 200MB | Memory Profiler |
| APK 大小 | < 40MB | APK Analyzer |

## 一句话总结

现代 Android = Kotlin + Jetpack Compose + Coroutine + Hilt + Room；系统层只在性能优化或 Framework 二次开发时深入。
