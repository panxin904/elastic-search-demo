---
title: 数字签名
date: 2026-08-15  # date-auto-injected
---

# 数字签名

## 一句话总结

> **数字签名 = 私钥签名 + 公钥验证**。**核心：身份认证 + 不可否认 + 完整性**。**3 大算法：RSA-PSS / ECDSA / Ed25519**。**应用：JWT / TLS 证书 / 软件签名 / 区块链**。

---

## 签名 vs 加密

| | 加密 | 签名 |
|---|------|------|
| **目的** | 保密 | 认证 + 不可否认 |
| **公钥** | 加密 | 验证 |
| **私钥** | 解密 | 签名 |
| **谁能解密** | 接收方 | 所有人（验证） |

## 主流签名算法

| 算法 | 密钥 | 签名长度 | 性能 | 场景 |
|------|------|---------|------|------|
| **RSA-PSS** | 2048 bit | 256 byte | 慢 | 遗留 |
| **ECDSA** | 256 bit | 64 byte | 快 | 标准 |
| **Ed25519** | 256 bit | 64 byte | 极快 | 现代推荐 |
| **BLS** | 256 bit | 32 byte | 慢 | 区块链 |

## 实战：Ed25519 签名

```python
from cryptography.hazmat.primitives.asymmetric import ed25519

# 签名
private_key = ed25519.Ed25519PrivateKey.generate()
signature = private_key.sign(b"message")

# 验证
public_key = private_key.public_key()
try:
    public_key.verify(signature, b"message")
    print("Valid")
except:
    print("Invalid")
```

## 实战：JWT 签名（RS256 / ES256 / EdDSA）

```python
import jwt

# RS256：用 RSA 私钥签
token = jwt.encode(payload, rsa_private_key, algorithm="RS256")

# ES256：用 ECDSA 私钥签
token = jwt.encode(payload, ec_private_key, algorithm="ES256")

# EdDSA：用 Ed25519 私钥签
token = jwt.encode(payload, ed25519_private_key, algorithm="EdDSA")
```

## 实战：软件签名（Cosign）

```bash
# 签名容器镜像
cosign sign --key cosign.key myregistry.io/myapp:1.0.0

# 验证
cosign verify --key cosign.pub myregistry.io/myapp:1.0.0

# K8s 准入控制（拒绝未签名）
# Kyverno + cosign
```

## 实战：TLS 证书签名

```bash
# 1. 生成 CSR
openssl req -new -key server.key -out server.csr

# 2. CA 签名
openssl x509 -req -in server.csr     -CA ca.crt -CAkey ca.key -CAcreateserial     -out server.crt -days 365

# 3. 验证
openssl verify -CAfile ca.crt server.crt
```

## 实战：软件包签名（apt / npm）

```bash
# apt
apt-key adv --recv-keys --keyserver keyserver.ubuntu.com KEYID

# npm（cosign 集成）
npm publish --provenance  # npm 自动生成 SBOM + 签名
```

## 实战：Web3 区块链签名

```javascript
// MetaMask 签名
const accounts = await ethereum.request({ method: "eth_requestAccounts" });
const signature = await ethereum.request({
    method: "personal_sign",
    params: ["Hello, world!", accounts[0]],
});

// 验证（服务端）
import { ethers } from "ethers";
const recovered = ethers.verifyMessage("Hello, world!", signature);
console.log(recovered === accounts[0]);  // true
```

## 实战：ECDSA 签名陷阱

```python
# ❌ 错误：使用临时密钥也要 nonce
# 攻击者通过两次签名（同 message + 不同 nonce）推出私钥
# 解决方案：RFC 6979 确定性 nonce

# ✅ Python 库已默认使用
from cryptography.hazmat.primitives.asymmetric import ec
private_key = ec.generate_private_key(ec.SECP256R1())
signature = private_key.sign(b"message", ec.ECDSA(hashes.SHA256()))
# cryptography 库默认用 RFC 6979
```

## 签名信任链

```
┌────────────────────────────────────────┐
│  Root CA（操作系统信任）                 │
│    └─ Intermediate CA                  │
│          └─ 域名证书                    │
│              └─ 你的公钥                │
│  信任链：device trust → root           │
└────────────────────────────────────────┘
```

## 实战：PKCS#7 / CMS 签名

```python
from cryptography.hazmat.primitives.serialization import pkcs7
import os

# 签名文件
signature = private_key.sign(
    open("file.pdf", "rb").read(),
    padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
    hashes.SHA256(),
)
```

## 关联章节

- **03-crypto/asymmetric**：非对称加密
- **03-crypto/hash**：哈希函数
- **04-network/tls-pki**：证书签名
- **05-container/supply-chain**：Cosign 镜像签名

## 一句话总结

> **数字签名 = 私钥签 + 公钥验**。**现代用 Ed25519 / ECDSA**。**应用：JWT / TLS / 镜像 / 软件包 / 区块链**。**关键：私钥保护 + 确定性 nonce（ECDSA）**。


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
