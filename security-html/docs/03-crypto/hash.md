---
title: 哈希函数
---

# 哈希函数

## 一句话总结

> **哈希 = 单向映射 + 固定输出**。**3 大类：SHA-256（数据完整性）/ bcrypt（密码）/ HMAC（消息认证）**。**核心：抗碰撞 + 抗前缀 + 抗第二原像**。

---

## 主流哈希对比

| 算法 | 输出长度 | 安全性 | 性能 | 用途 |
|------|---------|--------|------|------|
| **MD5** | 128 bit | 已破 | 极快 | ❌ 禁用 |
| **SHA-1** | 160 bit | 已破 | 快 | ❌ 禁用 |
| **SHA-256** | 256 bit | 安全 | 快 | ✅ 通用 |
| **SHA-3** | 256 bit | 安全 | 略慢 | 备选 |
| **BLAKE2** | 256 bit | 安全 | 极快 | 现代 |
| **bcrypt** | 184 bit | 安全 | 慢 | 密码 |
| **Argon2id** | 可变 | 安全 | 可调 | 密码首选 |

## 哈希 3 大安全属性

| 属性 | 含义 |
|------|------|
| **抗碰撞**（Collision） | 难找 x ≠ y 使 H(x) = H(y) |
| **抗第二原像** | 给定 x，难找 y 使 H(x) = H(y) |
| **抗前缀** | 给定 x，难找 y 使 H(y) = H(x) |

## 实战：SHA-256

```python
import hashlib

# 文件完整性
sha = hashlib.sha256()
with open("file.zip", "rb") as f:
    while chunk := f.read(8192):
        sha.update(chunk)
print(sha.hexdigest())
```

```bash
# 命令行
sha256sum file.zip
```

## 实战：密码哈希

```python
# ❌ MD5（彩虹表秒破）
hashlib.md5(password.encode()).hexdigest()

# ✅ bcrypt
import bcrypt
salt = bcrypt.gensalt(rounds=12)  # cost 12 = 2^12 迭代
hash = bcrypt.hashpw(password.encode(), salt)
# 验证
bcrypt.checkpw(password.encode(), hash)
```

```python
# ✅ Argon2id（OWASP 首选）
from argon2 import PasswordHasher
ph = PasswordHasher()
hash = ph.hash(password)
ph.verify(hash, password)
```

## 实战：HMAC（消息认证）

```python
import hmac
import hashlib

# 验证消息完整性
def verify(message: bytes, signature: bytes, key: bytes) -> bool:
    expected = hmac.new(key, message, hashlib.sha256).digest()
    return hmac.compare_digest(signature, expected)  # 防时序攻击
```

## 实战：JWT 签名

```python
# HS256（HMAC-SHA256）
jwt.encode(payload, secret, algorithm="HS256")

# RS256（RSA-SHA256）
jwt.encode(payload, private_key, algorithm="RS256")

# ES256（ECDSA-SHA256）
jwt.encode(payload, ec_private_key, algorithm="ES256")
```

## 实战：彩虹表 + Salt

```python
# ❌ 无 salt（两个用户密码相同 → 哈希相同）
hash1 = hashlib.sha256(b"password123").hexdigest()
hash2 = hashlib.sha256(b"password123").hexdigest()  # 相同

# ✅ 有 salt（每个用户唯一）
salt = os.urandom(16)
hash = hashlib.sha256(salt + b"password123").hexdigest()
# 不同用户有不同 salt
```

## 实战：HKDF（密钥派生）

```python
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# 从 master key 派生多个子密钥
master_key = b"master-secret-32-bytes"
hkdf = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"encryption-key",
)
key1 = hkdf.derive(master_key)
```

## 关键陷阱

| 陷阱 | 危害 | 防御 |
|------|------|------|
| **MD5 / SHA-1** | 碰撞攻击 | 用 SHA-256 |
| **无 salt** | 彩虹表 | 随机 salt |
| **密码用 SHA-256** | GPU 暴力 | bcrypt / Argon2 |
| **自己写 HMAC** | 长度扩展 | 用 HMAC 标准 |
| **错误比较** | 时序攻击 | `hmac.compare_digest` |

## 实战：密码哈希参数

| 算法 | 参数 | 目标耗时 |
|------|------|---------|
| bcrypt | cost=12 | ~250ms |
| bcrypt | cost=14 | ~1s |
| Argon2id | t=3, m=64MB, p=4 | ~500ms |
| PBKDF2 | iter=600000 | ~500ms |

## 关联章节

- **03-crypto/symmetric**：AEAD 内部用哈希
- **03-crypto/signature**：数字签名
- **01-web-top10/a02-crypto-failure**：A02 加密失效

## 一句话总结

> **哈希 = SHA-256（数据）+ bcrypt / Argon2（密码）+ HMAC（认证）**。**密码必加 salt，用慢哈希**。**MD5 / SHA-1 已破，禁用**。
