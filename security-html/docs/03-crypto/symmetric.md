---
title: 对称加密
---

# 对称加密

## 一句话总结

> **对称加密 = 加解密用同一密钥**。**两大主流：AES-256-GCM（标准）/ ChaCha20-Poly1300（移动 ARM）**。**实战必备：nonce/IV 唯一 + Authenticated Encryption（AEAD）**。

---

## 主流算法

| 算法 | 块/流 | 密钥长度 | 性能 | 场景 |
|------|-------|---------|------|------|
| **AES-256-GCM** | 块（128 bit） | 256 bit | 极快 + 硬件 AES-NI | 通用首选 |
| **ChaCha20-Poly1305** | 流 | 256 bit | 移动 ARM 更快 | 移动 / IoT |
| **AES-128-GCM** | 块 | 128 bit | 极快 | 通用 |
| **3DES** | 块 | 168 bit | 慢 | 遗留 |
| **DES** | 块 | 56 bit | 已破 | 禁用 |

## AES 5 种模式

| 模式 | 特点 | 推荐 |
|------|------|------|
| **ECB** | 每块独立（不安全）| ❌ 禁用 |
| **CBC** | 链式，需 padding | ❌ 不推荐 |
| **CTR** | 计数器流模式 | ❌ 不带认证 |
| **GCM** | CTR + 认证（AEAD）| ✅ 推荐 |
| **CCM** | CTR + CBC-MAC | ✅ 嵌入式 |

## 实战：Python AES-GCM

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# 1. 生成密钥（32 字节 = 256 bit）
key = AESGCM.generate_key(bit_length=256)

# 2. 加密
aesgcm = AESGCM(key)
nonce = os.urandom(12)  # 12 字节（96 bit）唯一值
plaintext = b"secret message"
ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)
# ciphertext = nonce + ciphertext + tag

# 3. 解密
plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
```

## 实战：Java AES-GCM

```java
import javax.crypto.Cipher;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;

public byte[] encrypt(byte[] plaintext, byte[] key) throws Exception {
    SecureRandom random = new SecureRandom();
    byte[] nonce = new byte[12];
    random.nextBytes(nonce);

    Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
    SecretKeySpec keySpec = new SecretKeySpec(key, "AES");
    GCMParameterSpec gcmSpec = new GCMParameterSpec(128, nonce);

    cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec);
    return cipher.doFinal(plaintext);
}
```

## 实战：Go ChaCha20-Poly1305

```go
import (
    "crypto/chacha20poly1305"
    "crypto/rand"
    "io"
)

func encrypt(plaintext, key []byte) (nonce, ciphertext []byte) {
    aead, _ := chacha20poly1305.NewX(key)
    nonce = make([]byte, aead.NonceSize())
    io.ReadFull(rand.Reader, nonce)
    ciphertext = aead.Seal(nil, nonce, plaintext, nil)
    return
}
```

## 关键陷阱

| 陷阱 | 危害 | 防御 |
|------|------|------|
| **IV / nonce 重用** | 加密失效 | 密码学安全随机 |
| **ECB 模式** | 图像可识别 | 不用 |
| **缺失认证** | 篡改不可知 | 用 GCM / CCM |
| **密钥硬编码** | Git 泄漏 | KMS / Vault |
| **密钥长度不足** | 暴力破解 | 至少 256 bit |

## 密钥派生（KDF）

```python
# 从密码派生密钥（PBKDF2）
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=600_000,  # OWASP 推荐
)
key = kdf.derive(password.encode())
```

```python
# 推荐：Argon2id
from argon2.low_level import hash_secret_raw, Type

key = hash_secret_raw(
    secret=password.encode(),
    salt=salt,
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    type=Type.ID,
)
```

## 关联章节

- **03-crypto/asymmetric**：非对称加密
- **03-crypto/hash**：哈希函数
- **03-crypto/tls-deep-dive**：TLS 1.3 握手

## 一句话总结

> **对称加密 = AES-256-GCM（首选）/ ChaCha20（移动）**。**关键：nonce 唯一 + AEAD + 密钥管理**。**永远不要用 ECB / CBC + HMAC 手动组合**。


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
