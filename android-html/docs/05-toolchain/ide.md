---
title: Android Studio
---

# Android Studio

> 官方 IDE：编码 / 调试 / 性能分析一体化工具集。

## 🎯 核心要点

- Profiler：CPU / Memory / Network / Energy 实时分析
- Layout Inspector：运行时 View 树可视化
- APK Analyzer：APK 包结构 / 资源占用分析
- Database Inspector：SQLite / Room 数据库浏览

## 🛠️ 实战示例

```bash
# 命令行工具（与 IDE 等效）
adb shell am start -n com.example/.MainActivity
# LeakCanary 检测内存泄漏
```

## 🔗 相关链接

- [构建系统](./gradle)
- [性能优化](../06-perf/performance)
- [← 返回 工具链 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：Profiler 火焰图看 CPU 热点
- **小贴士**：Layout Inspector 看 Compose 树（2023+）
- **小贴士**：APK Analyzer 找重复资源 / 未使用方法


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)

- **必备插件**：Kotlin / Android WiFi ADB / Rainbow Brackets。

- **实战提示**：Hedgehog / Iguana / Jellyfish 版本对应 AGP 8.x。
