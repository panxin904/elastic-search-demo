---
title: Android 学习路径
---

# 🚶 Android 学习路径

> 三条路径覆盖"应用开发者 / 系统/性能优化者 / 跨端架构师"三种角色。按背景选择即可。

## 路径 1：应用开发者（3 周）

适合：Java 转 Android / 前端转移动端 / 从零入门。

| Day | 主题 | 关键交付 |
|---|---|---|
| D1 | Kotlin 基础（语法糖 / 空安全 / 扩展函数） | 第一个 Kotlin 工程 |
| D2-3 | Activity / Fragment 生命周期 | 跑通屏幕旋转 / 进程被杀后状态恢复 |
| D4-5 | ViewModel + LiveData / StateFlow | 替换 setText 时代的数据流 |
| D6-7 | RecyclerView + Adapter + DiffUtil | 跑通联系人列表 1000 条 |
| W2 D1-2 | Kotlin 协程（Coroutine / Flow / Channel） | viewModelScope + retry 实战 |
| W2 D3 | Navigation 组件 + Safe Args | 单 Activity 多 Fragment 导航 |
| W2 D4-5 | Room 数据库 + DataStore | 替换 SharedPreferences |
| W2 D6 | Hilt 依赖注入 | @HiltAndroidApp / @Inject |
| W2 D7 | WorkManager 后台任务 | 周期同步 + 约束条件 |
| W3 D1-3 | Jetpack Compose（State / Modifier / Layout） | 改写一个页面为 Compose |
| W3 D4-5 | Material 3 主题 + 自适应布局 | 横竖屏 + 平板布局 |
| W3 D6-7 | 实战项目：仿掘金客户端首页 | 全流程：网络 + 数据库 + UI |

## 路径 2：系统/性能优化者（4 周）

适合：工作 2 年以上，想往系统层 / 性能 / Framework 走。

| 周 | 主题 | 关键交付 |
|---|---|---|
| W1 D1-2 | Android 系统架构（5 层 + Zygote） | 画出启动流程时序图 |
| W1 D3-4 | Binder IPC 原理（mmap / ioctl） | 手写一个 AIDL 跨进程 demo |
| W1 D5-6 | ActivityManagerService / WindowManagerService | 理解 Activity 启动链路 |
| W1 D7 | PackageManagerService | APK 安装 / 解析流程 |
| W2 D1-2 | ART 运行时（Dex2oat / AOT / JIT） | 解释冷启动为何慢 |
| W2 D3-4 | ClassLoader 机制 | 理解 DexPathList / 热修复原理 |
| W2 D5-6 | 内存模型（Native 堆 / Java 堆 / GC） | LeakCanary 源码阅读 |
| W2 D7 | 线程模型（Handler / MessageQueue / Looper） | 理解主线程消息循环 |
| W3 D1-2 | 启动优化（Baseline Profile / Macrobenchmark） | 启动时间从 2s → 800ms |
| W3 D3-4 | 内存优化（LeakCanary / Memory Profiler） | OOM 率从 1% → 0.1% |
| W3 D5-6 | ANR 与卡顿（Choreographer / Systrace） | 定位并修复 ANR |
| W3 D7 | 包大小优化（R8 / ABI split / 资源压缩） | APK 从 80MB → 35MB |
| W4 D1-2 | Gradle 构建优化（KTS / Build Cache） | 构建从 5min → 1min |
| W4 D3-4 | NDK / JNI / Native Hook | 接入一个 C++ 库 |
| W4 D5 | 渲染机制（HWUI / RenderThread） | 解释 Compose 重组为何 60fps |
| W4 D6-7 | 源码阅读：Choreographer / Handler / AMS | 写读书笔记 |

## 路径 3：跨端架构师（2 周）

适合：客户端老兵，要做技术选型 / 跨平台方案决策。

| 周 | 主题 | 关键交付 |
|---|---|---|
| W1 D1-2 | Flutter 架构（Widget / Element / RenderObject） | 跑通 Flutter Counter |
| W1 D3-4 | Flutter 状态管理（Provider / Riverpod / Bloc） | 三选一实战 |
| W1 D5 | Flutter 与原生互调（Platform Channel） | MethodChannel demo |
| W1 D6-7 | React Native 架构（Bridge / JSI / Hermes） | 跑通 RN 列表 + 网络 |
| W2 D1-2 | Kotlin Multiplatform（KMP / Compose Multiplatform） | KMP 共享业务模块 demo |
| W2 D3-4 | 跨端决策树（性能 / 一致性 / 团队） | 写一篇选型决策文档 |
| W2 D5 | 包大小 vs 性能 vs 开发效率（量化对比） | benchmark 三个框架 |
| W2 D6-7 | 实战：用一个跨端框架重写一个真实页面 | 含性能 + 包大小数据 |

## 一句话定义

Android = **基于 Linux Kernel 的移动设备操作系统**：应用层用 Kotlin + Jetpack Compose / 系统层是 Java + C++ + Binder IPC 的横切栈。

## 关键 takeaway

- **不要一上来就学系统层**：90% 应用开发者只要掌握 Jetpack + Compose + 协程就够
- **协程是 Android 异步的事实标准**：AsyncTask / RxJava / Thread 都应淘汰，新项目直接 Coroutine + Flow
- **Compose 是未来**：Google 全力推 Compose，View 体系只维护不开发
- **包大小是生死线**：APK 每涨 5MB，安装转化率掉 2%；R8 + ABI split 必须做
- **跨平台 ROI 看团队**：纯 Android 团队上 Flutter 收益高；iOS+Android 团队 RN/KMP 更划算
