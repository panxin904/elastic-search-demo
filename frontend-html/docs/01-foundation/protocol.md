---
title: Web 协议与安全
---

# Web 协议与安全

## 🌐 常见协议

| 协议 | 端口 | 加密 | 备注 |
|------|------|------|------|
| HTTP | 80 | ❌ | 已逐步淘汰 |
| HTTPS | 443 | ✅ (TLS) | 现代标准 |
| WSS | 443 | ✅ | WebSocket Secure |
| HTTP/2 | 80/443 | 可选 | 多路复用、首部压缩 |
| HTTP/3 | 443 | ✅ | 基于 QUIC/UDP |

## 🔒 HTTPS / TLS 握手（简化）

```
Client                       Server
  │── ClientHello ──────────►│
  │                          │
  │◄── ServerHello + Cert ───│
  │                          │
  │── Key Exchange ─────────►│
  │── Finished ──────────────►│
  │                          │
  │◄── Finished ─────────────│
  │  Encrypted traffic flows ▶
```

- 用非对称加密交换会话密钥
- 之后用对称加密传输

## 🚨 常见攻击与防御

### 1. XSS（跨站脚本）

**类型**：
- 存储型（恶意内容存入 DB）
- 反射型（URL 参数回显）
- DOM 型（前端不安全的 innerHTML）

**防御**：
- 输出转义（永远不要信任用户输入）
- CSP：`Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-xxx'`
- Cookie 用 `HttpOnly` / `Secure` / `SameSite=Strict`

### 2. CSRF（跨站请求伪造）

**防御**：
- CSRF Token（每个请求带一次性 token）
- `SameSite=Strict` / `Lax`
- 验证 `Origin` / `Referer`

### 3. 点击劫持

**防御**：`X-Frame-Options: DENY` 或 CSP `frame-ancestors 'none'`。

## 🛡️ 关键响应头

```nginx
add_header Content-Security-Policy "default-src 'self';" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=()" always;
```

## 🔐 CORS

```js
// Node + cors 中间件
app.use(cors({
  origin: ['https://app.example.com'],
  credentials: true,
  methods: ['GET','POST']
}))

// 浏览器跨域时携带 Cookie
fetch('https://api.example.com/me', {
  credentials: 'include'
})
```

**预检**：非简单请求（PUT/DELETE / application/json）会先发 OPTIONS。

## 🍪 Cookie 细节

- 默认浏览器跨域不携带 → `credentials: 'include'` + 响应 `Access-Control-Allow-Credentials: true` + `Access-Control-Allow-Origin` 不能是 `*`
- 作用域：`Path`、`Domain`
- 过期：`Max-Age` / `Expires`

## 📝 常见问题

- **HTTPS 下 mixed content**：所有资源也必须 HTTPS
- **`.env` 暴露**：永远别把 API key 打到前端 bundle
- **localStorage vs Cookie**：localStorage 不参与 HTTP，不会自动携带，XSS 风险更高

## 🔗 下一步

- [Node 后端 Express / Koa](/11-node/express)
- [REST 规范 / OpenAPI](/09-data/rest)
