---
title: IPC 机制
---

# IPC 机制

> Android 进程间通信核心机制：Binder（高频）/ AIDL（强类型）/ Messenger（队列）/ ContentProvider（数据共享）。

## 🎯 核心要点

- Binder：基于 mmap 的 IPC，单次拷贝性能高
- AIDL：定义跨进程接口（编译期生成 Stub/Proxy）
- Messenger：Handler + Parcelable 序列化消息
- ContentProvider：标准数据访问接口（可授权）

## 🛠️ 实战示例

```java
// AIDL 定义（IUserService.aidl）
interface IUserService {
  User getUser(long id);
  void updateUser(in User user);
}
```

## 🔗 相关链接

- [启动流程](./startup)
- [框架服务](./services)
- [← 返回 系统层 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：Binder 单进程内也可使用（不跨进程性能也 OK）
- **小贴士**：AIDL 的 in / out / inout 标记参数方向
- **小贴士**：oneway 关键字让方法异步返回（fire-and-forget）


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)
