---
title: HTTPS 与 TLS
date: 2026-08-15  # date-auto-injected
---

# HTTPS 与 TLS

<div class="nt-badge nt-badge-app">应用层</div>
<div class="nt-badge nt-badge-security">加密</div>

HTTPS = HTTP + TLS（早期为 SSL），在传输层与应用层之间插入**加密层**，保护数据的**机密性、完整性、真实性**。

## 1. 为什么需要 HTTPS

| 风险 | 后果 |
| --- | --- |
| 明文传输 | 中间人可窃听 |
| 无校验 | 数据可被篡改 |
| 无身份 | 可被冒充钓鱼 |

## 2. TLS 作用（三性）

| 目标 | 实现 |
| --- | --- |
| 机密性 | 对称加密（AES-GCM、ChaCha20） |
| 完整性 | HMAC / AEAD 摘要 |
| 真实性 | 数字证书 + 签名 |

## 3. TLS 握手流程（TLS 1.2）

```
Client                                        Server
  |  ──ClientHello──>                          |
  |    (TLS 版本、加密套件、随机数)              |
  |                                             |
  |  <──ServerHello──                           |
  |     (选定套件、随机数)                       |
  |  <──Certificate──                           |
  |     (服务器证书链)                          |
  |  <──ServerKeyExchange── (可选)              |
  |  <──ServerHelloDone──                       |
  |                                             |
  |  ──ClientKeyExchange──>                     |
  |    (Pre-master secret，公钥加密)             |
  |  ──ChangeCipherSpec──>                      |
  |  ──Finished──>                              |
  |  <──ChangeCipherSpec──                      |
  |  <──Finished──                              |
  |                                             |
  |  ════应用数据（加密）═════>                  |
```

> TLS 1.3 简化为 **1-RTT**（甚至 0-RTT）。

## 4. 加密套件

格式：

```
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
       │       │      │         │     │
       │       │      │         │     └─ MAC 算法
       │       │      │         └─ 对称加密
       │       │      └─ 密钥交换
       │       └─ 认证
       └─ 协议版本
```

**现代推荐**：

- TLS 1.3：`TLS_AES_128_GCM_SHA256`、`TLS_AES_256_GCM_SHA384`、`TLS_CHACHA20_POLY1305_SHA256`
- TLS 1.2：`ECDHE-ECDSA-AES128-GCM-SHA256`

## 5. 密钥交换

| 算法 | 说明 | 前向保密 |
| --- | --- | --- |
| RSA | 客户端用服务器公钥加密 Pre-master | ✗ |
| DH（Diffie-Hellman） | 双方协商共享密钥 | ✗ |
| ECDHE | 椭圆曲线 DH，每次会话新密钥 | ✓ |

**前向保密（PFS）**：即使长期私钥泄露，历史会话也安全。

## 6. 证书与 CA

### 6.1 证书内容

```
Subject: CN=www.example.com
Issuer: CN=DigiCert Global G2
Valid From / To
Public Key: RSA/ECDSA
Signature: Issuer 对证书签名
```

### 6.2 信任链

```
Root CA（自签名）
   └─ Intermediate CA
         └─ 域名证书
              └─ 客户端验证：Root CA 在系统信任库
```

### 6.3 证书类型

| 类型 | 验证 | 适用 |
| --- | --- | --- |
| DV | 域名控制 | 个人 / 博客 |
| OV | 组织身份 | 企业 |
| EV | 严格审核 | 金融 / 大型 |
| 自签 | 无 | 内部 / 测试 |

## 7. TLS 1.2 vs TLS 1.3

| 维度 | TLS 1.2 | TLS 1.3 |
| --- | --- | --- |
| 握手 RTT | 2 RTT | 1 RTT（0-RTT 可选） |
| 加密套件 | 多 | 仅 AEAD（AES-GCM、ChaCha20） |
| 密钥交换 | RSA / DH / ECDHE | 仅 ECDHE / DHE（强制 PFS） |
| 可见算法 | 多，易配置错误 | 默认安全 |
| 重协商 | 有 | 无 |

## 8. 0-RTT（TLS 1.3）

- 客户端首次握手时，服务器发 **PSK**（pre-shared key）
- 下次连接，客户端用 PSK 加密数据 + 第一个数据包
- **风险**：0-RTT 数据可重放攻击

## 9. 实战配置（Nginx）

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/ssl/certs/example.crt;
    ssl_certificate_key /etc/ssl/private/example.key;

    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache   shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
}
```

## 10. 常见问题

| 现象 | 原因 |
| --- | --- |
| 证书不受信任 | 未在系统信任库 / 过期 / 链不全 |
| 域名不匹配 | 证书 CN/SAN 与访问域名不一致 |
| 协议不匹配 | 服务器只支持老协议 |
| 加密套件无重叠 | 客户端与服务端无共同算法 |
| mixed content | HTTPS 页面加载 HTTP 资源 |
| SNI 问题 | 同 IP 多证书未配 SNI |

## 11. 抓包（Wireshark）

```
No.  Time   Source     Dest       Protocol  Info
1    0.000  client     server     TLS       Client Hello
2    0.050  server     client     TLS       Server Hello, Certificate, Server Hello Done
3    0.060  client     server     TLS       Client Key Exchange, Change Cipher Spec
4    0.100  server     client     TLS       Application Data
```

## 12. 常见面试题

1. **HTTPS 加密流程？** TLS 握手交换密钥，对称加密传输。
2. **什么是对称 / 非对称加密？** 对称同密钥；非对称公私钥。
3. **证书作用？** 证明服务端身份，携带公钥。
4. **CA 干什么？** 第三方签发证书，建立信任链。
5. **前向保密？** 长期密钥泄露不影响历史会话。
6. **TLS 1.3 优势？** 1-RTT、强制 PFS、移除不安全算法。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 网络栈
- [security](https://java-px.bot.cd/security/):网络安全
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 网络

<!-- svg-injected:do-not-edit -->

![https handshake](/https-handshake.svg)
