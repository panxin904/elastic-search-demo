---
title: TLS PKI 体系
date: 2026-08-15  # date-auto-injected
---

# TLS PKI 证书体系

## 一句话总结

> **TLS PKI = 公钥基础设施（公钥 + 身份 + CA 签名）**。**核心组件：CA（证书颁发机构）/ CSR（证书签名请求）/ 证书链 / OCSP（吊销检查）**。**Let's Encrypt 让 HTTPS 平民化**，**mTLS 服务网格 + SPIFFE 让零信任落地**。

---

## 为什么需要 PKI

对称加密有"密钥分发"难题——怎么把同一个密钥安全地给 Alice 和 Bob？非对称加密解决了这个问题：
- Alice 拿 Bob 的公钥加密 → 只有 Bob 私钥能解
- 但 Bob 的公钥怎么证明"真的属于 Bob"？→ 第三方 CA 签名证明

```
┌────────────────────────────────────────┐
│  Alice                  Bob            │
│    │  1. 我要 Bob 的公钥证书           │
│    │ ─────────────────→               │
│    │  2. 证书（Bob 公钥+CA签名）      │
│    │ ←─────────────────                │
│    │  3. 用 CA 公钥验证签名            │
│    │  4. 确认是 Bob                    │
│    │  5. 用 Bob 公钥加密通信           │
└────────────────────────────────────────┘
```

## 核心组件

| 组件 | 作用 |
|------|------|
| **CA**（Certificate Authority） | 颁发证书的受信第三方 |
| **CSR**（Certificate Signing Request） | 申请证书的标准化请求 |
| **Certificate** | 公钥 + 身份 + CA 签名 |
| **Root CA** | 信任锚（预装在操作系统 / 浏览器） |
| **Intermediate CA** | 中间 CA（隔离 Root CA 风险） |
| **CRL** | 证书吊销列表 |
| **OCSP** | 在线证书状态协议 |

## 证书层级（Chain of Trust）

```
Root CA（操作系统预装，DigiCert / Sectigo / ISRG）
    │
    ├─ Intermediate CA 1（Let's Encrypt R3 / R10）
    │      │
    │      └─ example.com（域名证书，叶子证书）
    │
    └─ Intermediate CA 2
```

## 实战：用 OpenSSL 生成自签名证书

```bash
# 1. 生成私钥
openssl genrsa -out server.key 2048

# 2. 生成 CSR（包含公钥 + 域名 + 组织信息）
openssl req -new -key server.key -out server.csr \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=Acme/CN=example.com"

# 3. 自签名（仅用于测试）
openssl x509 -req -days 365 -in server.csr \
    -signkey server.key -out server.crt

# 4. 验证证书
openssl x509 -in server.crt -text -noout | head -20
```

## Let's Encrypt 自动化

```bash
# 安装 certbot
apt install certbot

# 一键申请 + 自动续期
certbot --nginx -d example.com -d www.example.com

# 证书位于 /etc/letsencrypt/live/example.com/
# 自动 cron 续期（90 天）
```

## 证书格式

| 格式 | 扩展名 | 用途 |
|------|--------|------|
| **PEM** | `.pem` / `.crt` / `.cer` | Base64 编码的 ASCII（最常用） |
| **DER** | `.der` | 二进制（Java / Windows） |
| **PKCS#12** | `.p12` / `.pfx` | 私钥 + 证书打包（密码保护） |
| **JKS** | `.jks` | Java KeyStore（Java 专用） |

## 实战：Nginx 配置 TLS

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;          # 不允许 TLS 1.0/1.1
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;          # 客户端优先（TLS 1.3）
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
}
```

## 关联章节

- **03-crypto/tls-deep-dive**：TLS 1.3 握手原理
- **04-network/mtls**：双向认证（mTLS）
- **04-network/hsts-csp**：HSTS 强制 HTTPS
- **06-zero-trust/spiffe**：SPIFFE 用 X.509 SVID 标识工作负载

## 一句话总结

> **TLS PKI = X.509 证书 + CA 信任链**。**Root CA 不可信 → 整个链崩塌**。**Let's Encrypt 90 天自动续期 + certbot 让 HTTPS 零成本**。**mTLS = 客户端也给证书，服务网格标配**。


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
