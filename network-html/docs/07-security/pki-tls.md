---
title: PKI 与 TLS 实战
---

# PKI 与 TLS 实战

<div class="nt-badge nt-badge-security">网络安全</div>
<div class="nt-badge nt-badge-tools">实战</div>

本章聚焦 PKI 与 TLS 在生产环境中的落地：证书签发、TLS 部署、配置加固、故障排查。

## 1. Let's Encrypt 自动化

```bash
# Certbot 申请
certbot certonly --nginx -d example.com -d www.example.com

# 自动续期
certbot renew --dry-run
```

证书路径：

```
/etc/letsencrypt/live/example.com/
├── cert.pem       服务器证书
├── chain.pem      中间证书链
├── fullchain.pem  完整链
└── privkey.pem    私钥
```

## 2. 内部 PKI 搭建（私有 CA）

适合企业内网、IoT、测试环境。

### step-ca 部署

```bash
# 初始化
step ca init --name "MyCA" \
  --dns "ca.example.com" \
  --address ":443" \
  --provisioner "admin"

# 签发
step ca certificate www.internal.example.com server.crt server.key
```

### OpenSSL 自建

```bash
# 见 07-security/signature-pki.md
```

## 3. TLS 服务端配置（Nginx 模板）

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    ssl_certificate     /etc/ssl/certs/example.fullchain.pem;
    ssl_certificate_key /etc/ssl/private/example.key;

    # 协议
    ssl_protocols TLSv1.2 TLSv1.3;

    # 算法套件
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers on;

    # 会话复用
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    # 椭圆曲线
    ssl_ecdh_curve X25519:secp384r1;

    # OCSP Stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    # HSTS
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # 自动 HTTP → HTTPS
    error_page 497 https://$host$request_uri;
}
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}
```

## 4. TLS 客户端配置（常见语言）

### Go

```go
import (
    "crypto/tls"
)
config := &tls.Config{
    MinVersion:               tls.VersionTLS12,
    CurvePreferences:         []tls.CurveID{tls.X25519, tls.CurveP256},
    PreferServerCipherSuites: true,
}
```

### Java

```java
SSLContext ctx = SSLContext.getInstance("TLSv1.3");
ctx.init(null, null, null);
```

### mTLS

```nginx
ssl_client_certificate /etc/ssl/ca.crt;
ssl_verify_client on;
ssl_verify_depth 2;
```

## 5. TLS 性能优化

| 优化 | 收益 |
| --- | --- |
| TLS 1.3 | 1-RTT 减少延迟 |
| 0-RTT | 0-RTT 数据（需防重放） |
| OCSP Stapling | 节省 OCSP 查询 |
| Session Resumption | 减少握手 |
| False Start | 客户端提前发数据 |
| ChaCha20 | 移动端 ARM 性能更优 |
| ECC 证书 | 比 RSA 短 |

## 6. SNI（Server Name Indication）

同一 IP 多证书：

```nginx
server {
    listen 443 ssl;
    server_name a.example.com;
    ssl_certificate /etc/ssl/a.crt;
    ssl_certificate_key /etc/ssl/a.key;
}
server {
    listen 443 ssl;
    server_name b.example.com;
    ssl_certificate /etc/ssl/b.crt;
    ssl_certificate_key /etc/ssl/b.key;
}
```

## 7. 测试工具

### testssl.sh

```bash
./testssl.sh example.com
```

### SSL Labs

```
https://www.ssllabs.com/ssltest/analyze.html?d=example.com
```

### openssl s_client

```bash
openssl s_client -connect example.com:443 -tls1_3
openssl s_client -connect example.com:443 -cipher 'ECDHE-RSA-AES256-GCM-SHA384'
```

## 8. 常见故障排查

| 现象 | 排查 |
| --- | --- |
| 证书不受信任 | 浏览器导出证书，验证链 |
| 域名不匹配 | 证书 CN/SAN |
| 协议不匹配 | 客户端只支持 SSLv3 |
| 握手失败 | 加密套件无交集 |
| 性能差 | 关闭 Session Tickets、用 ECDHE |
| 中间人攻击 | 检查客户端 CA 信任 |

## 9. CT（Certificate Transparency）

- CA 必须将签发证书记录到 CT Log
- 浏览器验证 SCT 才信任证书
- 监控工具：crt.sh

## 10. 最佳实践清单

```
[ ] 使用 TLS 1.3 + TLS 1.2 兜底
[ ] 启用 HSTS（预加载）
[ ] 启用 OCSP Stapling
[ ] 自动化证书更新
[ ] 私钥权限 600
[ ] 关闭不安全的协议和算法
[ ] 监控证书到期（提前 30 天告警）
[ ] 启用 CAA 限制 CA
[ ] 使用 ECDSA 证书
[ ] 部署 WAF / Rate Limit
```

## 11. 常见面试题

1. **TLS 1.3 怎么提速？** 1-RTT 握手 + 0-RTT。
2. **HSTS 作用？** 强制浏览器使用 HTTPS，防降级。
3. **OCSP Stapling 优势？** 减少客户端查询，节省时间。
4. **TLS 握手为什么慢？** 多次 RTT + 非对称运算 + 证书传输。
5. **SNI 解决了什么？** 同一 IP 多 HTTPS 站点。
6. **TLS 性能优化方法？** 硬件加速、会话复用、ECC 证书、TLS 1.3。
