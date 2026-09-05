---
title: OAuth 2.0 详解
date: 2026-08-15  # date-auto-injected
---

# OAuth 2.0 详解

![Oauth2 Flow Comparison](/oauth2-flow-comparison.svg)

## 一句话总结

> **OAuth 2.0 = 授权框架**（不是认证）。**核心：让第三方应用代表用户访问资源**。**4 种 flow：authorization code（最常用）/ client credentials / implicit（废弃）/ password（遗留）**。**PKCE 强制要求**。

---

## 为什么需要 OAuth 2.0

```
┌────────────────────────────────────────┐
│  场景：照片打印 App 想访问你的 Google Photos│
├────────────────────────────────────────┤
│  ❌ 不用 OAuth：                        │
│     用户把 Google 密码给打印 App（危险）│
│  ✅ 用 OAuth：                          │
│     Google 授权打印 App 一个受限的 token│
│     用户随时可撤销                       │
└────────────────────────────────────────┘
```

## 4 个角色

| 角色 | 例子 |
|------|------|
| **Resource Owner** | 用户（你） |
| **Client** | 照片打印 App |
| **Authorization Server** | Google OAuth Server |
| **Resource Server** | Google Photos API |

## 4 种 Flow 对比

| Flow | 适用 | 客户端 | 关键 |
|------|------|--------|------|
| **Authorization Code** | Web 应用 | 服务端 | 最安全 |
| **Authorization Code + PKCE** | 移动 App / SPA | 公共客户端 | 防 code 拦截 |
| **Client Credentials** | M2M | 后端服务 | 无用户 |
| **Password** | 遗留迁移 | 受信第一方 | 不推荐 |
| **Device Code** | TV / IoT | 无浏览器 | 用户在另一端 |

## 实战：Authorization Code Flow

```
1. 用户点"用 Google 登录"
   GET /authorize?
     response_type=code
     &client_id=app123
     &redirect_uri=https://app.com/callback
     &scope=openid+profile+email
     &state=xyz123
     &code_challenge=BASE64URL(SHA256(verifier))
     &code_challenge_method=S256

2. Google 登录 + 同意 → 302 redirect
   https://app.com/callback?
     code=abc123
     &state=xyz123

3. App 后端用 code 换 token
   POST /token
     grant_type=authorization_code
     &code=abc123
     &redirect_uri=https://app.com/callback
     &client_id=app123
     &client_secret=xxx
     &code_verifier=original_verifier

4. Google 返回
   {
     "access_token": "...",
     "refresh_token": "...",
     "id_token": "...",
     "expires_in": 3600
   }
```

## 实战：PKCE（防 code 拦截）

```python
import secrets, hashlib, base64

# 1. 生成 verifier 和 challenge
verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b'=').decode()
challenge = base64.urlsafe_b64encode(
    hashlib.sha256(verifier.encode()).digest()
).rstrip(b'=').decode()

# 2. 跳转授权时带 challenge
authorize_url = f"https://oauth.provider.com/authorize?code_challenge={challenge}&code_challenge_method=S256"

# 3. 换 token 时带 verifier
token = requests.post("https://oauth.provider.com/token", data={
    "grant_type": "authorization_code",
    "code": code,
    "code_verifier": verifier,
    "client_id": "app123",
    "redirect_uri": "https://app.com/callback",
})
```

## 实战：Spring Authorization Server 配置

```yaml
spring:
  security:
    oauth2:
      client:
        registration:
          google:
            client-id: xxx.apps.googleusercontent.com
            client-secret: xxx
            scope: openid, profile, email
            redirect-uri: "{baseUrl}/login/oauth2/code/{registrationId}"
        provider:
          google:
            authorization-uri: https://accounts.google.com/o/oauth2/v2/auth
            token-uri: https://oauth2.googleapis.com/token
```

## 实战：常见陷阱

| 陷阱 | 危害 |
|------|------|
| redirect_uri 未校验 | 钓鱼攻击 |
| client_secret 泄漏 | 攻击者伪造请求 |
| 不校验 state | CSRF 攻击 |
| scope 过大 | 权限过度 |
| 不验证 audience | confused deputy |
| 不用 PKCE | mobile/SPA 拦截 |

## 关联章节

- **02-auth/oidc**：OIDC = OAuth 2.0 + 身份
- **02-auth/jwt**：access_token 通常是 JWT
- **02-auth/session-attack**：传统 Session 攻击

## 一句话总结

> **OAuth 2.0 = 授权（不是认证）**。**Web 用 Authorization Code + PKCE**。**M2M 用 Client Credentials**。**永远验证 redirect_uri 和 state**。


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

<!-- svg-injected:do-not-edit -->

![oauth2 flow](/oauth2-flow.svg)
