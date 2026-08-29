---
title: Android 面试与常见问题
date: 2026-08-21  # date-auto-injected
---

# ❓ Android 面试与常见问题

> 分 Easy / Medium / Hard 三档，覆盖应用层、系统层、性能、跨平台。

## Easy（基础）

### Q1：Activity / Fragment 生命周期有哪些阶段？

**答**：

Activity 生命周期：

- onCreate：初始化（setContentView）
- onStart：可见但不可交互
- onResume：可见可交互（位于栈顶）
- onPause：失去焦点
- onStop：完全不可见
- onDestroy：销毁
- onRestart：从 Stopped 重新可见

**屏幕旋转**：默认销毁重建。解决：ViewModel 保留数据；或 configChanges 自己处理（不推荐）。

### Q2：ViewModel 为什么能在屏幕旋转后存活？

**答**：ViewModel 存在 ViewModelStore 里，ViewModelStore 由 NonConfigurationInstances 持有，与 Activity 重建无关。

**注意**：ViewModel 不应持有 Context，需要 Context 用 AndroidViewModel 或注入 Application。

### Q3：Kotlin 协程的 Dispatchers 有哪些？

**答**：

| Dispatcher | 线程 | 用途 |
|---|---|---|
| Main | 主线程 | UI 更新 |
| IO | 64 线程池 | 网络 / 数据库 / 文件 IO |
| Default | CPU 核数 | CPU 密集 |
| Unconfined | 调用者线程 | 不推荐生产 |

## Medium（进阶）

### Q4：Jetpack Compose 的"重组"是什么？如何避免过度重组？

**答**：

**重组** 是 Compose 在状态变化时重新执行 composable 函数生成新 UI。

**触发条件**：

- 读取的 State（mutableStateOf / StateFlow）变化
- 参数变化

**优化**：

- remember(key)：key 变化才重置
- derivedStateOf：依赖多 State 计算时缓存
- LaunchedEffect(key)：副作用 key 不变不重启
- @Stable / @Immutable 标注类

### Q5：Binder 为什么比 Socket 快？

**答**：

| 维度 | Binder | Socket |
|---|---|---|
| IPC 机制 | 内核态 mmap + 一次拷贝 | 内核态两次拷贝 |
| 性能 | < 1ms | > 10ms |
| 安全 | 内核 UID/PID 校验 | 应用层校验 |
| 跨设备 | 否 | 是 |

Binder 核心原理：

1. Server 在内核注册

2. Client 通过 ServiceManager 拿引用

3. 数据经 Binder 驱动到内核

4. 通过 mmap 映射到 Server 地址空间

5. Server 直接读到 Client 数据（只拷贝一次）

### Q6：为什么 Activity 不能在子线程 new？

**答**：

1. 生命周期回调必须在主线程

2. Window / ViewRootImpl 必须主线程操作

3. UI 操作只能在主线程（Looper 检查）

反例：子线程 new Activity 不会报错，但生命周期回调错乱，会变成"幽灵 Activity"。

## Hard（架构 / 性能）

### Q7：APK 体积怎么从 80MB 优化到 30MB？

**答**：分层优化：

- R8 移除未使用代码（~10MB）

- 资源压缩（图片 WebP、移除未引用）~8MB

- ABI split（只保留 arm64-v8a）~25MB

- App Bundle 按需下载（最终用户包 ~20MB）

**具体动作**：R8 + ProGuard、AndResGuard 图片 WebP/Lottie、动态库拆 .so、shrinkResources、定期清理。

### Q8：冷启动 2 秒怎么优化到 800ms？

**答**：

冷启动 = 进程创建 + Application 初始化 + 首帧绘制。

**瓶颈常在 onCreate 和首帧绘制**。

**优化**：

1. **Application.onCreate 异步化**：非必要初始化放子线程 / WorkManager；启动器 ContentProvider 黑科技延迟三方库加载

2. **首页布局扁平化**：ConstraintLayout 替代嵌套、ViewStub、merge 标签

3. **主题闪屏**：windowSplashScreenBackground 简单 logo

4. **Baseline Profile（关键！）**：Macrobenchmark 生成 profile，提前 AOT 编译，可缩短 30-50%

5. **dex 分包**：启动只 load classes.dex，其他懒加载

6. **资源优化**：移除启动时大 drawable / font

### Q9：跨平台 Flutter / RN / KMP 怎么选？

**答**：

| 维度 | Flutter | RN | KMP |
|---|---|---|---|
| 渲染 | 自绘 Skia | Native Bridge | Native UI |
| 性能 | 接近 Native | 弱 | 接近 Native |
| 包大小 | +6MB | +2MB | +500KB |
| 一致性 | 高 | 低 | 共享逻辑 |

**选型**：

- 新 App 多端需求 → Flutter

- 已有 Web 团队 → React Native

- 已有 Android / iOS 团队 → KMP

- 性能敏感 → Native + C++

## 一句话总结

Android 工程师的核心能力是懂一点 Kotlin + 懂一点 Compose + 懂一点系统层，三段都懂才能做端到端设计。


<!-- auto-enrich:do-not-edit -->

## 实战示例

```bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
```

```yaml
# TODO: 配置示例
key: value
```

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
