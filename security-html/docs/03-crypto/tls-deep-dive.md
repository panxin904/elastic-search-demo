---
title: TLS 1.3 握手
---

# TLS 1.3 握手详解

## 一句话总结

> **TLS 1.3 = 现代安全通信的事实标准**。**1-RTT 握手（比 TLS 1.2 快 1 轮）+ 强制 AEAD + 0-RTT 模式（慎用）**。**核心：ECDHE 密钥交换 + X25519 / Ed25519**。

---

## TLS 1.3 vs TLS 1.2

| 维度 | TLS 1.2 | TLS 1.3 |
|------|---------|---------|
| 握手轮次 | 2-RTT | 1-RTT（0-RTT 可选）|
| 加密套件 | 数十种 | 5 种（强制 AEAD）|
| 密钥交换 | RSA / DHE / ECDHE | 仅 ECDHE（无 RSA）|
| 加密 | CBC + MAC | AEAD（GCM / ChaCha20）|
| 性能 | 中 | 高 |
| 安全性 | 已发现 POODLE / BEAST | 目前安全 |

## TLS 1.3 1-RTT 握手

```
Client                                              Server
   │                                                  │
   │ ─── ClientHello ─────────────────────────────→ │
   │     - 随机数 client_random                       │
   │     - 支持的密码套件                             │
   │     - key_share（X25519 公钥）                  │
   │                                                  │
   │                                                  │
   │ ←── ServerHello ──────────────────────────── │
   │     - 随机数 server_random                       │
   │     - 选定密码套件                               │
   │     - key_share（X25519 公钥）                  │
   │     - 加密扩展（EncryptedExtensions）           │
   │     - 证书（Certificate）                       │
   │     - 证书验证（CertificateVerify）              │
   │     - Finished（协商完成）                       │
   │                                                  │
   │ （共享密钥：X25519 ECDH）                       │
   │                                                  │
   │ ─── Finished ─────────────────────────────────→ │
   │     - 摘要确认                                  │
   │                                                  │
   │ ←═══ 加密通信 ════════════════════════════════ │ 
```

## TLS 1.3 5 种密码套件

```nginx
# nginx ssl_ciphers 配置
ssl_ciphers TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256;
```

| 套件 | 加密 | 哈希 |
|------|------|------|
| **TLS_AES_256_GCM_SHA384** | AES-256-GCM | SHA-384 |
| **TLS_CHACHA20_POLY1305_SHA256** | ChaCha20-Poly1305 | SHA-256 |
| **TLS_AES_128_GCM_SHA256** | AES-128-GCM | SHA-256 |
| **TLS_AES_128_CCM_SHA256** | AES-128-CCM | SHA-256 |
| **TLS_AES_128_CCM_8_SHA256** | AES-128-CCM-8 | SHA-256 |

## 实战：抓 TLS 1.3 握手

```bash
# 客户端
openssl s_client -tls1_3 -connect example.com:443 -msg

# 输出
# New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384
# ...
# Protocol  : TLSv1.3
# Cipher    : TLS_AES_256_GCM_SHA384
```

## 实战：Wireshark 抓包

1. 打开 Wireshark
2. 过滤 `tls.handshake.type == 1`（ClientHello）
3. 查看 `Handshake Protocol: Client Hello`
4. 跟踪 `key_share` 扩展：椭圆曲线 + 公钥

## 实战：Node.js TLS 1.3

```javascript
const https = require("https");
const fs = require("fs");

const options = {
    key: fs.readFileSync("server.key"),
    cert: fs.readFileSync("server.crt"),
    minVersion: "TLSv1.2",
    maxVersion: "TLSv1.3",
    ciphers: "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256",
};

https.createServer(options, (req, res) => {
    res.writeHead(200);
    res.end("Hello TLS 1.3!");
}).listen(443);
```

## 实战：0-RTT 模式

```
┌────────────────────────────────────────┐
│  0-RTT：客户端在第一次连接时收到       │
│  Session Ticket，第二次连接时           │
│  立即发送加密数据（0-RTT）               │
│                                        │
│  ⚠️ 风险：重放攻击                      │
│  攻击者重放 0-RTT 数据                   │
│  服务端无法区分"原始请求" vs "重放"     │
│  → 仅用于幂等 GET，禁用 POST/PUT        │
└────────────────────────────────────────┘
```

```nginx
# nginx 0-RTT 配置
ssl_early_data on;
proxy_set_header Early-Data $ssl_early_data;
```

## 实战：Nginx 配置 TLS 1.3

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;          # TLS 1.3 让客户端选
    ssl_early_data off;                     # 默认禁用 0-RTT
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
}
```

## 实战：测试 TLS 1.3

```bash
# testssl.sh
testssl.sh --protocols example.com

# 输出：
# TLS 1.2   offered
# TLS 1.3   offered (default)
```

## 关联章节

- **03-crypto/asymmetric**：ECDHE 密钥交换
- **03-crypto/signature**：Ed25519 / ECDSA
- **04-network/tls-pki**：证书体系
- **04-network/mtls**：双向认证

## 一句话总结

> **TLS 1.3 = 1-RTT + 强制 AEAD + ECDHE**。**5 种密码套件**。**X25519 密钥交换 + Ed25519 签名**。**0-RTT 慎用（重放风险）**。


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
