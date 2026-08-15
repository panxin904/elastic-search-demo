---
title: 数字签名与 PKI
---

# 数字签名与 PKI

<div class="nt-badge nt-badge-security">网络安全</div>
<div class="nt-badge nt-badge-cloud">基础设施</div>

数字签名（Digital Signature）证明数据**完整性 + 来源真实性**；PKI（Public Key Infrastructure）通过 CA 证书体系将公钥与身份绑定，构成全球信任基石。

## 1. 数字签名原理

```
签名：sign(hash(原文), 私钥) → 签名值
验证：verify(签名值, hash(原文), 公钥) → 合法/不合法
```

| 步骤 | 动作 |
| --- | --- |
| 1 | 发送方对原文做 hash（SHA-256） |
| 2 | 用私钥加密 hash → 签名 |
| 3 | 附原文 + 签名一并发送 |
| 4 | 接收方用公钥解密签名得到 hash1 |
| 5 | 对原文 hash 得到 hash2 |
| 6 | hash1 == hash2 则验签通过 |

## 2. 签名算法

| 算法 | 签名长度 | 性能 | 推荐 |
| --- | --- | --- | --- |
| RSA-1024 | 128B | 中 | ✗ |
| RSA-2048 | 256B | 中 | ✓ |
| RSA-3072 | 384B | 慢 | 高安全 |
| ECDSA-P256 | 64B | 快 | ✓ |
| EdDSA（Ed25519） | 64B | 极快 | **推荐** |
| SM2 | 64B | 快 | 国密 |

## 3. 签名 vs 加密

| 维度 | 签名 | 加密 |
| --- | --- | --- |
| 密钥 | 私钥签，公钥验 | 公钥加，私钥解 |
| 目标 | 完整性 + 身份 | 机密性 |
| 输出 | 短签名 | 长密文 |
| 算法 | RSA / ECDSA / EdDSA | RSA / AES |

## 4. 证书与 PKI

### 4.1 X.509 证书结构

```
Version: 3
Serial Number: 0a:1b:...
Signature Algorithm: sha256WithRSAEncryption
Issuer: CN=DigiCert Global G2, O=DigiCert Inc
Validity:
    Not Before: ...
    Not After : ...
Subject: CN=www.example.com
Subject Public Key Info:
    Public Key Algorithm: RSA
    RSA Public Key: ...
Extensions:
    Subject Alternative Name:
        DNS:www.example.com
        DNS:*.example.com
    Key Usage: Digital Signature, Key Encipherment
    Extended Key Usage: Server Auth, Client Auth
Signature Algorithm: sha256WithRSAEncryption
Signature Value: ...
```

### 4.2 PKI 组成

| 组件 | 作用 |
| --- | --- |
| CA（Certification Authority） | 签发证书 |
| RA（Registration Authority） | 审核申请 |
| CRL/OCSP | 证书吊销状态 |
| 证书存储 | 客户端信任库 |
| KMC | 私钥托管 |

### 4.3 信任链

```
Root CA (自签名)
   └─ Intermediate CA
         └─ 域名证书
              └─ 客户端验证根 CA 是否在系统信任库
```

## 5. 证书生命周期

```
1. CSR (Certificate Signing Request) 生成
2. CA 审核身份（DV/OV/EV）
3. CA 签发证书
4. 部署到服务器
5. 定期更新（Let's Encrypt 90 天）
6. 过期或主动吊销（CRL/OCSP）
```

### CSR

```bash
openssl req -new -newkey rsa:2048 -nodes \
  -keyout server.key \
  -out server.csr \
  -subj "/CN=www.example.com/O=Example Inc"
```

## 6. 证书类型

| 类型 | 验证强度 | 用途 | 签发时间 |
| --- | --- | --- | --- |
| DV | 域名控制 | 博客 | 分钟 |
| OV | 域名 + 组织 | 企业 | 1~3 天 |
| EV | 严格审核 | 金融 | 1~2 周 |
| 自签 | 无 | 内部 / 测试 | 立即 |

## 7. 证书吊销

| 方式 | 原理 |
| --- | --- |
| CRL | CA 定期发布吊销列表，文件大 |
| OCSP | 在线查询证书状态，实时 |
| OCSP Stapling | 服务器预取 OCSP 响应，提升速度 |
| CRLite | 压缩的 CRL |

```bash
# 查询 OCSP
openssl ocsp -issuer issuer.crt -cert server.crt -url http://ocsp.digicert.com
```

## 8. PKI 应用

| 场景 | 说明 |
| --- | --- |
| HTTPS / TLS | 网站证书 |
| S/MIME | 邮件签名加密 |
| 代码签名 | 软件发布 |
| 文档签名 | PDF / Office |
| IoT 设备证书 | 设备认证 |
| mTLS | 双向认证 |
| SSH | host 证书（与 .ssh/known_hosts 对应） |

## 9. mTLS 双向认证

```
Server 持有 server.crt
Client 持有 client.crt

握手时：
  Server → Client: server.crt（要求客户端验签）
  Client → Server: client.crt（要求服务端验签）
```

常用于服务网格（Istio）、零信任网络。

## 10. 实践

### 创建自签证书

```bash
# CA
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -days 3650 -out ca.crt -subj "/CN=MyRootCA"

# 服务器
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=www.example.com"
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365
```

### 查看证书

```bash
openssl x509 -in server.crt -text -noout
openssl s_client -connect example.com:443 -showcerts
```

## 11. 常见面试题

1. **数字签名三要素？** 私钥、原文 hash、签名算法。
2. **PKI 核心？** CA + 证书 + 信任链。
3. **证书链作用？** 客户端只需信任根 CA，就能验证所有子证书。
4. **DV 和 EV 证书区别？** EV 审核企业身份，浏览器地址栏显示公司名。
5. **证书过期怎么验证？** OCSP / CRL。
6. **CSR 是什么？** 包含公钥和身份信息，提交给 CA 签发证书。
