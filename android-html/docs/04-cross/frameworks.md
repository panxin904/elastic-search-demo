---
title: 跨平台框架
---

# 跨平台框架

> Android 之外的跨平台方案：Flutter（自绘 UI）/ React Native（JS 桥）/ KMP（共享逻辑）/ Compose Multiplatform（共享 UI）。

## 🎯 核心要点

- Flutter：Dart + Skia 自绘 UI，跨 Android/iOS/Web/Desktop
- React Native：JS 业务 + 原生组件桥接
- KMP：共享 Kotlin 业务逻辑，UI 端原生
- Compose Multiplatform：JetBrains 推出的 KMP 共享 UI 方案

## 🛠️ 实战示例

```dart
// Flutter Widget 示例
class Counter extends StatefulWidget {
  @override
  State<Counter> createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int _count = 0;
  @override
  Widget build(BuildContext context) => Scaffold(
    body: Center(child: Text("Count: $_count")),
    floatingActionButton: FloatingActionButton(
      onPressed: () => setState(() => _count++),
      child: Icon(Icons.add),
    ),
  );
}
```

## 🔗 相关链接

- [选型决策](./decision)
- [应用层](../01-app/language)
- [← 返回 跨平台 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：Flutter 性能接近原生（Skia 自绘 UI）
- **小贴士**：RN 启动快但动画 / 复杂 UI 性能略差
- **小贴士**：KMP 只共享逻辑，UI 端用原生（性能 + 一致性最佳）
