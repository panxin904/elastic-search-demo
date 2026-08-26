---
title: 资源与适配
---

# 资源与适配

> Android 资源系统：颜色 / 主题 / 字符串 / Drawable / 多分辨率屏幕适配。

## 🎯 核心要点

- 主题：Material 3 / DayNight / 自定义 Theme
- 颜色：Color tokens（语义化命名）
- 国际化：strings.xml 多语言（values-zh / values-en）
- 屏幕适配：sw600dp / smallestWidth / 矢量图 / 多 Density 资源

## 🛠️ 实战示例

```xml
<!-- res/values/colors.xml -->
<resources>
  <color name="md_theme_light_primary">#0061A4</color>
  <color name="md_theme_light_onPrimary">#FFFFFF</color>
</resources>
```

## 🔗 相关链接

- [视图系统](./view-system)
- [Compose](./compose)
- [← 返回 UI 体系 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：矢量图（Vector Drawable）替代多分辨率 PNG
- **小贴士**：主题用语义化命名（colorPrimary / colorOnPrimary）
- **小贴士**：sw600dp / w820dp 分桶适配平板与折叠屏


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)

- **官方文档**：developer.android.com/training/multiscreen/screendensities。


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
