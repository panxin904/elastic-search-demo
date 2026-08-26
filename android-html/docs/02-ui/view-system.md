---
title: 视图系统
---

# 视图系统

> 传统 View 体系：Activity / Fragment / View 树 / RecyclerView，掌握底层原理有助于 Compose 优化。

## 🎯 核心要点

- Activity：单一屏幕入口 + 生命周期
- Fragment：模块化 UI + FragmentManager 栈
- View 树：Measure / Layout / Draw 三阶段
- RecyclerView：ViewHolder 复用 + DiffUtil 增量更新

## 🛠️ 实战示例

```kotlin
// RecyclerView Adapter + DiffUtil
class UserAdapter : ListAdapter<User, UserViewHolder>(DIFF) {
  companion object {
    val DIFF = object : DiffUtil.ItemCallback<User>() {
      override fun areItemsTheSame(a: User, b: User) = a.id == b.id
      override fun areContentsTheSame(a: User, b: User) = a == b
    }
  }
}
```

## 🔗 相关链接

- [Compose](./compose)
- [资源与适配](./resource)
- [← 返回 UI 体系 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：RecyclerView 必备 ViewHolder 模式 + DiffUtil 增量更新
- **小贴士**：Fragment 嵌套注意 savedState 处理
- **小贴士**：自定义 View 重写 onMeasure / onLayout / onDraw 三件套


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
