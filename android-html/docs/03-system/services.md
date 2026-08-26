---
title: 框架服务
---

# 框架服务

> SystemServer 启动的核心系统服务：AMS / WMS / PMS / IMS。

## 🎯 核心要点

- AMS（Activity Manager Service）：管理 Activity 栈 + 进程优先级
- WMS（Window Manager Service）：窗口 Z-Order + Surface 管理
- PMS（Package Manager Service）：APK 安装 / 卸载 / 权限查询
- IMS（Input Manager Service）：触摸 / 按键事件分发

## 🛠️ 实战示例

```bash
# dumpsys 查看 AMS 状态
adb shell dumpsys activity activities | head -50
adb shell dumpsys window windows | grep -A 5 "mCurrentFocus"
```

## 🔗 相关链接

- [启动流程](./startup)
- [IPC](./ipc)
- [← 返回 系统层 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：dumpsys 是分析框架服务的瑞士军刀
- **小贴士**：AMS 优先级管理（前台 / 可见 / 服务 / 后台）
- **小贴士**：低内存时按优先级杀进程（oom_adj）


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
