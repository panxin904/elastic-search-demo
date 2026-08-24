---
title: 固件 OTA
---

# 固件 OTA

> 空中升级（Firmware Over-The-Air），分块传输 + 签名验证 + 回滚机制。

## 🎯 核心要点

- 分块传输：A/B 分区或流式写入（避免大文件一次性写入失败）
- 签名验证：ECDSA / RSA 签名 + 公钥校验（防止恶意固件）
- 回滚机制：升级失败自动回退到上一版本
- 灰度发布：按设备 ID / 区域 / 版本分组升级

## 🛠️ 实战示例

```c
# OTA 签名验证伪代码（C / ESP32）
int verify_firmware(uint8_t* fw, size_t len, uint8_t* sig) {
  if (mbedtls_rsa_verify(fw, len, sig, PUBLIC_KEY) != 0) {
    return -1;  // 验签失败，拒绝升级
  }
  return 0;
}
```

## 🔗 相关链接

- [设备影子](./shadow)
- [设备安全](./security)
- [← 返回 设备管理 目录](./)
- [← 返回 iot 首页](../)
## 🎯 OTA 实施要点

- **A/B 分区**：双固件分区，失败自动回滚
- **签名验证**：ECDSA / RSA + 公钥校验
- **灰度发布**：按区域 / 设备类型 / 版本分组
- **断点续传**：大文件分块 + 校验和
