---
title: 设备安全
---

# 设备安全

> X.509 证书 / mTLS / 密钥管理 / OTA 签名四大支柱。

## 🎯 核心要点

- X.509 证书：设备身份认证（每设备唯一证书）
- mTLS：双向 TLS 认证，云端 + 设备互相验证
- 密钥管理：硬件安全模块（HSM）/ TrustZone / SE 芯片
- OTA 签名：固件必须签名才能升级

## 🛠️ 实战示例

```text
# mTLS 配置（mosquitto MQTT broker）
listener 8883
cafile /etc/mosquitto/ca_cert.pem
certfile /etc/mosquitto/server_cert.pem
keyfile /etc/mosquitto/server_key.pem
require_certificate true
use_identity_as_username true
```

## 🔗 相关链接

- [OTA](./ota)
- [公有云 IoT](../06-platform/public-cloud)
- [← 返回 设备管理 目录](./)
- [← 返回 iot 首页](../)
## 🎯 安全四支柱

1. **X.509 证书**：设备唯一身份（每设备一张）
2. **mTLS**：双向 TLS 认证（client + server 互相验证）
3. **硬件安全**：HSM / TrustZone / SE 芯片
4. **OTA 签名**：固件升级必须签名
**轮换**：定期轮换证书 / 密钥

- **小贴士**：证书签发用 CFSSL + 自建 CA 或 Let's Encrypt。


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
