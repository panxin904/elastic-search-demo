---
title: A02 加密机制失效
---

# A02 · Cryptographic Failures（加密机制失效）

## 一句话总结

> **加密失效 = 数据裸奔**。**典型：明文存密码 / 用 MD5 / HTTP 传输敏感数据 / 弱 TLS 算法**。**防御：TLS 1.3 + bcrypt + 静态加密 + 密钥管理**。

---

## 什么是加密机制失效

A02 涵盖**所有与加密相关的失误**——不是"没用加密"，而是"用错了"或"用得太弱"：

| 场景 | 错误 | 风险 |
|------|------|------|
| 密码存储 | 明文存数据库 | 数据库泄漏 = 全员密码 |
| 密码哈希 | MD5 / SHA-1 | 彩虹表秒破 |
| 传输 | HTTP 传输密码 | 中间人窃取 |
| 静态加密 | 自制 XOR 算法 | 几乎不加密 |
| 密钥管理 | 硬编码在源码 | Git 泄漏 = 全公司失守 |

## 错误 vs 正确做法

### 密码哈希

```python
# ❌ MD5 / SHA-1（彩虹表秒破）
import hashlib
password = hashlib.md5(user_input.encode()).hexdigest()

# ❌ SHA-256（GPU 每秒 10 亿次，太快）
password = hashlib.sha256(user_input.encode()).hexdigest()

# ✅ Argon2id（OWASP 推荐）
from argon2 import PasswordHasher
ph = PasswordHasher()
password_hash = ph.hash(user_input)

# ✅ bcrypt（成熟、广泛支持）
import bcrypt
password_hash = bcrypt.hashpw(user_input.encode(), bcrypt.gensalt(rounds=12))
```

### TLS 配置

```nginx
# ❌ 启用 TLS 1.0 / 1.1（POODLE / BEAST 漏洞）
ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;

# ✅ 仅 TLS 1.2 / 1.3
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;

# ✅ 强制 HTTPS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## 实战：Equifax 1.45 亿用户泄漏（2017）

Equifax 因 **Apache Struts 已知 CVE** + **TLS 证书管理混乱** + **加密策略错误**，导致 1.45 亿用户数据泄漏。**教训**：加密不是单一环节，是体系。

## 防御清单

| 措施 | 落地 |
|------|------|
| 强密码哈希 | Argon2id / bcrypt（cost ≥ 12）|
| 敏感字段加密 | 用户手机号 / 身份证（AES-256-GCM）|
| 密钥管理 | HashiCorp Vault / AWS KMS / Azure Key Vault |
| TLS 1.3 强制 | nginx / Spring Boot 全栈 |
| 不存敏感数据 | 信用卡只存 token（PCI-DSS 要求） |
| 强制 HTTPS | HSTS preload |

## 关联章节

- **03-crypto**：密码学算法选型
- **03-crypto/hash**：bcrypt / Argon2
- **04-network/tls-pki**：TLS PKI 体系
- **04-network/hsts-csp**：HSTS 强制 HTTPS

## 实战：CVEs 真实案例

| 漏洞 | 危害 | 修复 |
|------|------|------|
| **Apache Struts 2 (S2-045)** | Equifax 1.45 亿泄漏 | 立即升级 |
| **OpenSSL Heartbleed (CVE-2014-0160)** | 内存泄漏（含私钥）| 升级 OpenSSL |
| **WPA2 KRACK (2017)** | WiFi 流量解密 | 升级路由器 / 客户端 |
| **Log4j (CVE-2021-44228)** | RCE | 升级 Log4j 2.17.0+ |
| **Polkit (CVE-2021-4034)** | Linux 通用提权 | 升级 polkit |

## 实战：等保 2.0 三级加密要求

```
┌────────────────────────────────────────┐
│  等保 2.0 三级 · 密码应用要求            │
├────────────────────────────────────────┤
│  机密性：SM4 / AES-256                 │
│  完整性：HMAC-SHA256 / SM3             │
│  签名：RSA-2048 / SM2 / ECDSA P-256    │
│  密钥管理：专用的 KMC（密钥管理中心）   │
│  协商协议：IPSec VPN / SSL VPN（TLS 1.2+）│
└────────────────────────────────────────┘
```

## 实战：使用 HashiCorp Vault 管理密钥

```bash
# 1. 写入密钥
vault kv put secret/myapp/db password=$(openssl rand -hex 32)

# 2. 应用读取（动态密钥）
vault read secret/myapp/db

# 3. 数据库动态凭证（自动过期）
vault read database/creds/myapp-readonly
# username: v-myapp-readonly-abc123
# password: xxx（1 小时过期）
```

## 实战：KMS 集成（AWS KMS）

```python
import boto3

kms = boto3.client("kms")

# 加密
response = kms.encrypt(
    KeyId="alias/myapp-key",
    Plaintext=b"sensitive data",
)
ciphertext = response["CiphertextBlob"]

# 解密
response = kms.decrypt(CiphertextBlob=ciphertext)
plaintext = response["Plaintext"]

# 优势：密钥永不出 KMS、审计日志、自动轮换
```

## 一句话总结

> **A02 加密机制失效 = 用错加密**。**核心：密码用 bcrypt/Argon2，传输用 TLS 1.3，密钥用 Vault/GMS**。**永远不要自己发明加密算法**。
