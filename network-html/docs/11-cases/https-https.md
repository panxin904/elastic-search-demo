---
title: HTTPS 性能优化
date: 2026-08-15  # date-auto-injected
---

# HTTPS 性能优化

<div class="nt-badge nt-badge-cases">企业案例</div>
<div class="nt-badge nt-badge-security">HTTPS</div>

HTTPS 在安全之外也带来性能开销，本章梳理典型优化手段。

## 1. HTTPS 的开销

| 阶段 | 开销 |
| --- | --- |
| TLS 握手 | 1~2 RTT |
| 非对称运算 | RSA 2048 ~ 5ms |
| 对称加密 | AES-GCM 性能可忽略 |
| 证书传输 | 2~5 KB |

总增加延迟：100~300ms（首屏）。

## 2. 优化手段

### 2.1 TLS 1.3

- 1-RTT 握手（甚至 0-RTT）
- 强制 ECDHE（AES-GCM）
- 移除不安全算法

### 2.2 会话复用

| 方式 | 描述 |
| --- | --- |
| Session ID | 服务端缓存 |
| Session Ticket | 加密票据 |
| TLS 1.3 PSK | 0-RTT |

```nginx
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_session_tickets off;   # 关闭可减弱重放
```

### 2.3 OCSP Stapling

- 服务端预取 OCSP 响应
- 避免客户端查 CA

```nginx
ssl_stapling on;
ssl_stapling_verify on;
```

### 2.4 ECDSA 证书

| 类型 | 签名长度 |
| --- | --- |
| RSA 2048 | 256B |
| ECDSA P-256 | 64B |

- 签名验证更快
- 握手更小

### 2.5 False Start

- 客户端提前发数据
- TLS 1.3 中不再需要

### 2.6 HTTP/2 / HTTP/3

- 多路复用：解决并发
- HTTP/3 0-RTT：移动场景提速

### 2.7 ChaCha20-Poly1305

- 移动 ARM 比 AES-GCM 快
- CloudFlare 等自动切换

### 2.8 硬件加速

- Intel QAT：SSL 加解密卸载
- 专用 SSL 加速卡
- 国产密码卡（SM 系列）

## 3. 证书优化

| 优化 | 效果 |
| --- | --- |
| 短链证书 | 减小传输 |
| 多域名合并 | 减少握手 |
| 通配符 | 简化运维 |
| 自动化 | ACME (Let's Encrypt) |

## 4. 实战：Nginx 优化

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/ssl/certs/ecdsa.crt;
    ssl_certificate_key /etc/ssl/private/ecdsa.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;     # TLS 1.3 让客户端选
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;

    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    ssl_ecdh_curve X25519:secp384r1;

    ssl_stapling on;
    ssl_stapling_verify on;

    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

## 5. 客户端优化

```java
// 启用 TLS 1.3
SSLContext ctx = SSLContext.getInstance("TLSv1.3");
ctx.init(null, null, null);

// 启用会话复用
SSLSessionContext sessCtx = ctx.getServerSessionContext();
sessCtx.setSessionCacheSize(1000);
sessCtx.setSessionTimeout(86400);
```

```go
tlsConfig := &tls.Config{
    MinVersion: tls.VersionTLS12,
    CurvePreferences: []tls.CurveID{tls.X25519, tls.CurveP256},
}
http.Transport{TLSClientConfig: tlsConfig}
```

## 6. CDN 侧优化

| 优化 | 做法 |
| --- | --- |
| TLS 终结 | CDN 终结 TLS |
| 协议优化 | HTTP/2、HTTP/3 |
| 会话复用 | 全球会话共享 |
| OCSP Stapling | CDN 预取 |
| 0-RTT | 启用 |

## 7. 性能数据

| 优化 | TTFB 改进 |
| --- | --- |
| TLS 1.3 | -1 RTT（~100ms） |
| Session Resumption | -1 RTT |
| OCSP Stapling | -50ms |
| ECDSA | -20ms |
| HTTP/2 | 多请求并发 |
| 0-RTT | -1 RTT（额外 0-RTT 数据） |

## 8. 常见问题

| 问题 | 原因 | 解决 |
| --- | --- | --- |
| 握手慢 | 密钥交换 | TLS 1.3 / 0-RTT |
| CPU 高 | RSA 验证 | 硬件 / ECDSA |
| 5xx 升高 | 加密 CPU 满 | 终端卸载 / CDN |
| 证书过期 | 监控缺失 | 自动化 + 监控 |

## 9. 监控

```promql
# TLS 握手时间
histogram_quantile(0.99, sum(rate(ssl_handshake_duration_seconds_bucket[5m])) by (le))

# 失败率
rate(ssl_handshake_failures_total[5m]) / rate(ssl_handshakes_total[5m])
```

## 10. 常见面试题

1. **HTTPS 慢在哪？** TLS 握手、证书传输、非对称运算。
2. **怎么优化？** TLS 1.3、Session Resumption、ECDSA、HTTP/2/3。
3. **OCSP Stapling 价值？** 减少客户端查询。
4. **0-RTT 风险？** 重放攻击。
5. **ECDSA 优势？** 短、签名快。
6. **为什么推荐 TLS 1.3？** 1-RTT、强制 PFS、安全算法。


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 网络栈
- [security](https://java-px.bot.cd/security/):网络安全
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 网络
