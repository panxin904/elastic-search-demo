---
title: 非对称加密
---

# 非对称加密

## 一句话总结

> **非对称加密 = 公钥加密 + 私钥解密**（或反向签名）。**两大主流：RSA（兼容）/ ECC（现代推荐）**。**实战：密钥 2048 bit RSA 或 256 bit ECC**。

---

## 主流算法对比

| 算法 | 密钥长度 | 安全等效 | 性能 | 现状 |
|------|---------|---------|------|------|
| **RSA** | 2048 bit | 112 bit | 慢 | 遗留 |
| **RSA** | 4096 bit | ~140 bit | 非常慢 | 高安全 |
| **DH** | 2048 bit | 112 bit | 中 | TLS 密钥交换 |
| **ECC（secp256r1）** | 256 bit | 128 bit | 快 | 标准 |
| **Ed25519** | 256 bit | 128 bit | 极快 | 现代推荐 |
| **X25519** | 256 bit | 128 bit | 极快 | TLS 1.3 推荐 |

## 实战：RSA 加密

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

# 1. 生成 RSA 密钥对
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# 2. 公钥加密
ciphertext = public_key.encrypt(
    b"secret",
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)

# 3. 私钥解密
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    ),
)
```

❌ **不要用 PKCS1v15**（已被 Bleichenbacher 攻击）

## 实战：Ed25519 签名

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

# 1. 生成密钥对
private_key = ed25519.Ed25519PrivateKey.generate()
public_key = private_key.public_key()

# 2. 签名
signature = private_key.sign(b"message")

# 3. 验证
public_key.verify(signature, b"message")
```

## 实战：X25519 ECDH 密钥交换

```python
from cryptography.hazmat.primitives.asymmetric import x25519

# Alice 和 Bob 各生成密钥对
alice_private = x25519.X25519PrivateKey.generate()
alice_public = alice_private.public_key()

bob_private = x25519.X25519PrivateKey.generate()
bob_public = bob_private.public_key()

# 双方计算共享密钥
alice_shared = alice_private.exchange(bob_public)
bob_shared = bob_private.exchange(alice_public)
# alice_shared == bob_shared
```

## 实战：OpenSSL 生成密钥

```bash
# RSA
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# Ed25519
openssl genpkey -algorithm Ed25519 -out private.pem
openssl pkey -in private.pem -pubout -out public.pem
```

## 实战：Java RSA

```java
import java.security.KeyPairGenerator;
import java.security.Signature;

KeyPairGenerator gen = KeyPairGenerator.getInstance("RSA");
gen.initialize(2048);
KeyPair pair = gen.generateKeyPair();

Signature signer = Signature.getInstance("SHA256withRSA");
signer.initSign(pair.getPrivate());
signer.update("message".getBytes());
byte[] signature = signer.sign();
```

## 实战：JWT RS256（OAuth 2.0）

```python
# Auth Server 用 private 签
token = jwt.encode(payload, private_key, algorithm="RS256")

# Resource Server 用 public 验
decoded = jwt.decode(token, public_key, algorithms=["RS256"])
```

## 实战：性能对比

```
        签名 / 验证（同等安全）
RSA 2048     1.0x
RSA 4096     ~7x 慢
ECC 256      ~3x 快
Ed25519      ~10x 快
```

## 关键陷阱

| 陷阱 | 危害 | 防御 |
|------|------|------|
| **RSA 1024** | 可被破解 | 至少 2048 |
| **PKCS1v15** | Bleichenbacher | 用 OAEP |
| **私钥泄漏** | 全失守 | Vault / HSM |
| **短秘钥** | 暴破 | 256 bit ECC |
| **不验证签名** | 中间人 | 强制 verify |

## 关联章节

- **03-crypto/symmetric**：对称加密
- **03-crypto/signature**：数字签名
- **03-crypto/tls-deep-dive**：TLS 1.3 用 ECDHE / Ed25519
- **04-network/tls-pki**：证书公钥

## 一句话总结

> **非对称加密 = RSA / ECC / Ed25519**。**新项目：Ed25519 签名 + X25519 密钥交换**。**遗留：RSA 2048 + OAEP**。**永远不要用 RSA 1024 / PKCS1v15**。
