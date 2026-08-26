---
title: 发布与上架
---

# 发布与上架

> 从 App Bundle 到 Play Console / 国内应用市场的发布流程。

## 🎯 核心要点

- App Bundle（.aab）：按设备 ABI / Density 拆分，包体积减 30%+
- Play Console：上传 .aab + 商店信息 + 隐私政策
- 国内应用市场：腾讯 / 华为 / 小米 / OPPO / VIVO 多渠道
- Firebase：Crashlytics / Analytics / Remote Config

## 🛠️ 实战示例

```bash
# 生成 Release AAB
./gradlew bundleRelease
# 产物路径
app/build/outputs/bundle/release/app-release.aab
```

## 🔗 相关链接

- [构建系统](./gradle)
- [性能优化](../06-perf/performance)
- [← 返回 工具链 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：Play Asset Delivery 按需下载资源
- **小贴士**：Play Console Internal Testing 通道先跑灰度
- **小贴士**：国内多渠道用 umeng / bugly + 各市场 SDK


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
