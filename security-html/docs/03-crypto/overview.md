---
title: 密码学总览
---

# 密码学基础

## 一句话总结

> **密码学 = 数学算法 + 协议工程**。**三类原语：对称加密（AES / ChaCha20）/ 非对称加密（RSA / ECC）/ 哈希（SHA-256 / bcrypt）**。**应用层协议：TLS 1.3 / JWT / 数字签名**。**核心原则：永远用主流库，不要自己发明**。

---

## 三大基础原语

| 类别 | 作用 | 主流算法 | 典型场景 |
|------|------|----------|----------|
| **对称加密** | 加解密用同一密钥 | AES-256-GCM / ChaCha20-Poly1305 | 数据加密、磁盘加密 |
| **非对称加密** | 公钥加密、私钥解密 | RSA-2048 / ECC P-256 / Ed25519 | TLS 握手、数字签名 |
| **哈希** | 单向映射、固定长度 | SHA-256 / SHA-3 / bcrypt | 密码存储、完整性校验 |

## 关键概念

### 密钥长度对性能

| 算法 | 密钥长度 | 安全等效 | 性能 |
|------|---------|---------|------|
| RSA | 2048 bit | 112 bit 安全 | 慢 |
| RSA | 4096 bit | ~140 bit 安全 | 非常慢 |
| ECC | 256 bit | 128 bit 安全 | 快 |
| Ed25519 | 256 bit | 128 bit 安全 | 极快 |

**结论**：现代系统**优先 ECC / Ed25519**，RSA 仅用于兼容旧系统。

### 哈希密码 vs 哈希数据

| 场景 | 错误 | 正确 |
|------|------|------|
| 密码存储 | SHA-256（快） | bcrypt / scrypt / Argon2（慢） |
| 文件完整性 | bcrypt（慢） | SHA-256 / SHA-3（快） |
| 数字签名 | bcrypt | SHA-256（搭配 RSA/Ed25519） |

**核心**：密码哈希需要**慢**，因为攻击者要尝试亿级密码；数据哈希需要**快**，因为每秒百万次校验。

## 数字签名与证书

```
┌──────────────────────────────────────┐
│  数字签名 = 私钥签名 + 公钥验证      │
│  ┌──────────────────────────────────┐│
│  │  Alice 用私钥签"hello"          ││
│  │     → 签名                      ││
│  │  Bob 用 Alice 公钥验证          ││
│  │     → 通过                      ││
│  └──────────────────────────────────┘│
│                                      │
│  证书 = 公钥 + 身份 + CA 签名        │
│  ┌──────────────────────────────────┐│
│  │  域名 example.com               ││
│  │  公钥 0xAB12...                  ││
│  │  CA 签名（DigiCert / Let's Encrypt）│
│  └──────────────────────────────────┘│
└──────────────────────────────────────┘
```

## 实战：写一段加密代码

```python
# Python 3.10+ 标准库
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# 1. 对称加密（AES-256-GCM，认证加密）
key = AESGCM.generate_key(bit_length=256)  # 32 字节
aesgcm = AESGCM(key)
nonce = os.urandom(12)  # 12 字节随机数
ciphertext = aesgcm.encrypt(nonce, b"secret message", None)

# 2. 哈希密码
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash("user-password")
ph.verify(hash, "user-password")  # 验证
```

## 关联章节

- **01-web-top10/a02-crypto-failure**：A02 加密机制失效
- **02-auth/jwt**：JWT 签名算法（HS256 / RS256 / ES256）
- **04-network/tls-pki**：TLS 证书体系
- **05-container/supply-chain**：Cosign 镜像签名

## 一句话总结

> **对称加密（AES）= 大量数据**。**非对称加密（ECC）= 密钥交换 + 签名**。**哈希（SHA-256 / bcrypt）= 完整性 + 密码**。**TLS 1.3 = 一切安全通信的基础**。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
