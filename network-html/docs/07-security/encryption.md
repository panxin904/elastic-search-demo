---
title: 对称加密与非对称加密
date: 2026-08-15  # date-auto-injected
---

# 对称加密与非对称加密

<div class="nt-badge nt-badge-security">网络安全</div>
<div class="nt-badge nt-badge-basics">基础</div>

加密是网络安全的基石。本章系统讲解对称加密、非对称加密、摘要算法、数字签名等核心概念。

## 1. 对称加密

**特点**：加解密使用**同一把密钥**。

```
明文 ──[密钥 K 加密]──> 密文 ──[密钥 K 解密]──> 明文
```

| 算法 | 密钥长度 | 块大小 | 状态 |
| --- | --- | --- | --- |
| DES | 56 bit | 64 bit | 已淘汰 |
| 3DES | 168 bit | 64 bit | 弃用 |
| AES | 128/192/256 bit | 128 bit | **主流** |
| ChaCha20 | 256 bit | 流密码 | 移动端主流 |
| SM4 | 128 bit | 128 bit | 国密 |
| RC4 | 40~2048 bit | 流密码 | 不安全，弃用 |

### AES 工作模式

| 模式 | 描述 | 典型场景 |
| --- | --- | --- |
| ECB | 每块独立加密（最弱） | 不推荐 |
| CBC | 块链，需 IV，前块密文 XOR 当前 | TLS、磁盘加密 |
| CFB | 流模式 | 旧应用 |
| OFB | 流模式 | 旧应用 |
| CTR | 计数器模式 | 磁盘加密 |
| GCM | 认证加密（AEAD） | **TLS 1.2/1.3 主流** |
| CCM | 认证加密 | 嵌入式 |

### 优缺点

| 优点 | 缺点 |
| --- | --- |
| 速度快 | 密钥分发难 |
| 适合大数据 | N 个人需要 N(N-1)/2 密钥 |

## 2. 非对称加密

**特点**：一对密钥，**公钥加密**、**私钥解密**（或反之用于签名）。

```
明文 ──[公钥 Pub 加密]──> 密文 ──[私钥 Pri 解密]──> 明文
```

| 算法 | 基于 | 密钥长度 | 用途 |
| --- | --- | --- | --- |
| RSA | 大数分解 | 2048+ bit | 加密、签名 |
| ECC | 椭圆曲线离散对数 | 256 bit | 移动端、签名 |
| DSA | 离散对数 | 1024+ bit | 签名（已不推荐） |
| ElGamal | 离散对数 | — | 加密 |
| SM2 | 椭圆曲线 | 256 bit | 国密 |

### RSA 原理（简）

```
n = p * q        （p, q 大素数）
φ(n) = (p-1)(q-1)
e * d ≡ 1 (mod φ(n))

公钥 = (n, e)
私钥 = (n, d)

加密: c = m^e mod n
解密: m = c^d mod n
```

### ECC 优势

- 256 bit ECC ≈ 3072 bit RSA 安全强度
- 签名更快、密文更小
- 移动端 / IoT 主流（ECDSA、Ed25519）

## 3. 混合加密

实战中**结合两者**优势：

```
1. A 用非对称加密传输对称密钥 K
2. A、B 用 K 对称加密大数据
```

TLS、PGP、SSH 都用此模式。

## 4. 摘要算法（Hash）

任意长度 → 固定长度输出，**单向**。

| 算法 | 输出长度 | 状态 |
| --- | --- | --- |
| MD5 | 128 bit | 已破解，仅校验 |
| SHA-1 | 160 bit | 已被破解 |
| SHA-256 | 256 bit | **主流** |
| SHA-384 | 384 bit | 高安全 |
| SHA-512 | 512 bit | 高安全 |
| SHA-3 / Keccak | 224/256/384/512 | NIST 2015 |
| SM3 | 256 bit | 国密 |
| BLAKE2 | 256/512 | 高速 |

### 特性

| 特性 | 说明 |
| --- | --- |
| 单向 | 无法反推原文 |
| 抗碰撞 | 难找不同输入同输出 |
| 雪崩 | 输入 1 bit 变化输出大幅变化 |

### 应用

| 场景 | 用法 |
| --- | --- |
| 密码存储 | bcrypt / Argon2 / PBKDF2 + salt |
| 文件校验 | MD5 / SHA-256 |
| 数字签名 | 签名 hash 而非原文 |
| HMAC | 带密钥的 hash 认证 |
| Merkle Tree | 区块链、IPFS |

## 5. 数字签名

```
签名：hash(原文) ──[私钥加密]──> 签名值
验证：签名值 ──[公钥解密]──> hash，对比原文 hash
```

| 算法 | 标准 |
| --- | --- |
| RSA-PSS | PKCS#1 v2.1 |
| ECDSA | FIPS 186 |
| EdDSA（Ed25519） | 高性能 |
| SM2 | 国密 |

## 6. HMAC

带密钥的 MAC：

```
HMAC(K, m) = H((K ⊕ opad) || H((K ⊕ ipad) || m))
```

- 验证**消息完整 + 来源**
- 常见：HMAC-SHA256

## 7. 密钥交换

| 协议 | 原理 | 安全性 |
| --- | --- | --- |
| DH | 离散对数 | 依赖参数 |
| ECDH | 椭圆曲线 | 现代 |
| X25519 | Curve25519 ECDH | **推荐** |

## 8. 实践

### Node.js AES-GCM

```js
const crypto = require('crypto');

function encrypt(key, plaintext) {
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
    const tag = cipher.getAuthTag();
    return { iv, ciphertext, tag };
}
```

### Python ECDH

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()
shared_key = private_key.exchange(ec.ECDH(), public_key)
derived_key = HKDF(hashes.SHA256(), 32, None, b'app').derive(shared_key)
```

## 9. 常见面试题

1. **对称 vs 非对称？** 对称同密钥快；非对称不同密钥慢但安全分发。
2. **HTTPS 怎么结合？** RSA/ECDH 传密钥 + AES-GCM 加密数据。
3. **hash 用来干嘛？** 完整性、口令存储、签名、索引。
4. **数字签名怎么验？** 公钥解密签名得到 hash，对比原文 hash。
5. **MD5 为什么不再安全？** 已被碰撞攻击破解。
6. **密钥长度推荐？** RSA ≥ 2048，ECC ≥ 256，对称 ≥ 128。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 网络栈
- [security](https://java-px.bot.cd/security/):网络安全
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 网络
