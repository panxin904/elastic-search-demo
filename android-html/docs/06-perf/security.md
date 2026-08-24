---
title: 安全机制
---

# 安全机制

> Android 安全栈：权限模型 / Scoped Storage / Network Security / Keystore / 证书钉扎。

## 🎯 核心要点

- 权限模型：Runtime Permission（Android 6+）
- Scoped Storage（Android 10+）：应用沙箱 + MediaStore
- Network Security Config：明文 HTTP 禁用 / 证书信任配置
- Keystore：硬件级密钥存储（StrongBox）
- 证书钉扎（Certificate Pinning）：防中间人攻击

## 🛠️ 实战示例

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
  <base-config cleartextTrafficPermitted="false">
    <trust-anchors>
      <certificates src="system" />
    </trust-anchors>
  </base-config>
</network-security-config>
```

## 🔗 相关链接

- [性能优化](./performance)
- [构建系统](../05-toolchain/gradle)
- [← 返回 性能与安全 目录](./)
- [← 返回 android 首页](../)

## 📝 补充

- **小贴士**：所有敏感数据用 EncryptedSharedPreferences
- **小贴士**：BiometricPrompt 替代指纹 API
- **小贴士**：定期审计第三方 SDK 收集的数据


## 🔗 延伸阅读

- [Android 官方文档](https://developer.android.com/)
- [Android 源码（AOSP）](https://cs.android.com/)
- [Jetpack 概览](https://developer.android.com/jetpack)
