---
title: HSTS / CSP / 安全头
---

# HTTP 安全响应头

## 一句话总结

> **HTTP 安全头 = 浏览器层的最后防线**。**5 大头：HSTS（强制 HTTPS）/ CSP（防 XSS）/ X-Frame-Options（防 clickjacking）/ X-Content-Type-Options（防 MIME 嗅探）/ Referrer-Policy（防 referer 泄漏）**。**不可替代代码层防御，但能加一层皮**。

---

## 5 大安全头

| Header | 作用 | 默认 |
|--------|------|------|
| **Strict-Transport-Security** | 强制 HTTPS | ❌ |
| **Content-Security-Policy** | 限制 JS / 资源来源 | ❌ |
| **X-Frame-Options** | 防 iframe 嵌套 | ❌ |
| **X-Content-Type-Options** | 禁止 MIME 嗅探 | ❌ |
| **Referrer-Policy** | 控制 referer 字段 | ❌ |

## HSTS：强制 HTTPS

```nginx
# 强制 HTTPS（1 年 + 子域名 + 预加载）
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

```python
# Flask / FastAPI
@app.after_request
def hsts(response):
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return response
```

**执行机制**：
- 浏览器首次访问 HTTPS → 收到 HSTS 头 → 记忆 1 年
- 后续 HTTP 访问 → 浏览器自动转 HTTPS（即使你输入 http://）

**预加载（preload）**：提交到 https://hstspreload.org → 浏览器内置列表。

## CSP：限制资源来源

```nginx
# 严格 CSP（仅允许同源 + 指定 CDN）
add_header Content-Security-Policy "
    default-src 'self';
    script-src 'self' https://cdn.jsdelivr.net;
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self' https://fonts.gstatic.com;
    connect-src 'self' https://api.example.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
" always;
```

```python
# CSP nonce（推荐）
import secrets

nonce = secrets.token_urlsafe(16)
response.headers["Content-Security-Policy"] = f"script-src 'nonce-{nonce}' 'strict-dynamic'"

# HTML：<script nonce="..." src="..."></script>
```

**CSP 关键指令**：

| 指令 | 作用 |
|------|------|
| `default-src` | 默认策略 |
| `script-src` | JS 来源 |
| `style-src` | CSS 来源 |
| `img-src` | 图片来源 |
| `connect-src` | XHR / fetch |
| `frame-ancestors` | 替代 X-Frame-Options |
| `form-action` | 表单提交目标 |
| `base-uri` | <base> 标签 |
| `report-uri` | 违规上报 |

## X-Frame-Options：防 Clickjacking

```nginx
# DENY：完全禁止 iframe
add_header X-Frame-Options "DENY" always;

# SAMEORIGIN：仅同源
add_header X-Frame-Options "SAMEORIGIN" always;
```

```python
# Modern：frame-ancestors 已替代
add_header Content-Security-Policy "frame-ancestors 'none'"
```

## X-Content-Type-Options：禁 MIME 嗅探

```nginx
add_header X-Content-Type-Options "nosniff" always;
```

效果：浏览器严格按 Content-Type 解析，不"猜"。

## Referrer-Policy：防 referer 泄漏

```nginx
# 严格：仅同源带 referer
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

| 策略 | 含义 |
|------|------|
| `no-referrer` | 不发送 |
| `same-origin` | 仅同源 |
| `strict-origin` | 仅同源 + origin |
| `strict-origin-when-cross-origin` | 推荐 |

## Permissions-Policy：浏览器 API 限制

```nginx
add_header Permissions-Policy "
    camera=(),
    microphone=(),
    geolocation=(self),
    payment=()
" always;
```

## 实战：完整 Nginx 配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    # SSL 配置
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # 6 大安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; frame-ancestors 'none'" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    # 不暴露 Server
    server_tokens off;
}
```

## 实战：Spring Security 配置

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http.headers(headers -> headers
            .contentSecurityPolicy("default-src 'self'")
            .and()
            .httpStrictTransportSecurity(hsts -> hsts
                .includeSubDomains(true)
                .preload(true)
                .maxAgeInSeconds(31536000))
        );
        return http.build();
    }
}
```

## 实战：检测安全头

```bash
# Mozilla Observatory
https://observatory.mozilla.org/

# 自动化
nmap --script http-security-headers example.com
```

## 关联章节

- **04-network/tls-pki**：TLS 基础
- **04-network/cors**：CORS 跨域
- **01-web-top10/a05-misconfig**：A05 配置错误

## 一句话总结

> **6 大安全头 = HSTS + CSP + X-Frame-Options + X-Content-Type-Options + Referrer-Policy + Permissions-Policy**。**Nginx 5 行配置就能加满**。**CSP nonce 模式最安全**。
