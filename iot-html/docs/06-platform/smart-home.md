---
title: 智能家居 Matter
---

# 智能家居 Matter

> Matter 协议（Project CHIP），CSA 标准，跨 Apple / Google / Amazon / 三星。

## 🎯 核心要点

- Matter 1.0：基于 IPv6 / Wi-Fi / Thread / Ethernet
- 多生态互操作：Apple HomeKit / Google Home / Amazon Alexa
- 设备发现：mDNS / DNS-SD
- 配网：BLE 辅助 / Wi-Fi 简化配网

## 🛠️ 实战示例

```text
# Matter 设备配网流程伪代码
1. 设备广播 mDNS 服务 _matter._tcp.local
2. 手机扫码 / 蓝牙发现设备
3. Commissioning（密钥交换 + 认证）
4. 加入 Fabric（用户家庭网络）
```

## 🔗 相关链接

- [公有云](./public-cloud)
- [工业互联网](./iiot)
- [← 返回 云平台与行业落地 目录](./)
- [← 返回 iot 首页](../)
## 🎯 Matter 协议要点

- **Matter 1.0**：基于 IPv6 / Wi-Fi / Thread / Ethernet
- **多生态**：Apple HomeKit / Google Home / Amazon Alexa
- **配网**：BLE 辅助 + mDNS 发现
- **本地优先**：不依赖云，断网仍可控制
**认证**：设备需 Matter 认证（兼容性测试）
