---
title: ART 运行时
---

# ART 运行时

> Android Runtime（替代 Dalvik）：Dex2oat AOT 编译 + GC + ClassLoader。

## 🎯 核心要点

- AOT（Ahead-of-Time）：安装时编译为本地代码（Android 7+）
- JIT（Just-in-Time）：运行时编译（兼顾冷启动 + 热路径）
- GC：分代回收 + Concurrent Mark Sweep
- ClassLoader：BootClassLoader → PathClassLoader → DexPathList

## 🛠️ 实战示例

```bash
# 查看运行时信息
adb shell getprop ro.build.version.sdk
adb shell getprop dalvik.vm.heapsize
# TraceView / Perfetto 分析 GC
```

## 🔗 相关链接

- [启动流程](./startup)
- [框架服务](./services)
- [← 返回 系统层 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：R8 默认开启，Dex2oat 安装时已编译为本地代码
- **小贴士**：GC Log 通过 `-XX:+PrintGCDetails` 开启
- **小贴士**：ClassLoader 双亲委派模型防止核心类被篡改


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)
