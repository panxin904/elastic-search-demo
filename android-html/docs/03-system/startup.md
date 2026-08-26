---
title: 启动流程
---

# 启动流程

> Android 启动链：Boot ROM → Bootloader → Kernel → Init → Zygote → SystemServer → 第一个 App。

## 🎯 核心要点

- Boot ROM：固化在芯片，初始化 RAM + 引导 Bootloader
- Init 进程：PID 1，挂载文件系统 + 启动服务
- Zygote：预加载 framework + 资源（孵化新进程）
- SystemServer：启动 AMS / WMS / PMS 等系统服务
- Launcher：从 AMS 启动到第一个可见 Activity

## 🛠️ 实战示例

```bash
# 查看启动耗时
adb shell am start -W -n com.example/.MainActivity
# 启动时间报告
TotalTime: 1234ms
WaitTime: 50ms
```

## 🔗 相关链接

- [IPC](./ipc)
- [ART 运行时](./runtime)
- [← 返回 系统层 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：冷启动 < 1.5s（推荐 < 1s），用 Macrobenchmark 测量
- **小贴士**：App Startup 库统一管理 ContentProvider 初始化
- **小贴士**：Baseline Profile 预编译热点代码，首启性能提升 30%+


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
