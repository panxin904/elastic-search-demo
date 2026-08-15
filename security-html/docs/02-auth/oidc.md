---
title: OpenID Connect（OIDC）详解
---

# OpenID Connect（OIDC）

## 一句话总结

> **OIDC = OAuth 2.0 + 身份层**。**核心：ID Token（JWT 格式身份断言）+ UserInfo Endpoint**。**3 个流派：Auth0 / Keycloak / Spring Authorization Server**。**现代 SSO / SaaS 标配**。

---

## OAuth 2.0 vs OIDC

| 维度 | OAuth 2.0 | OIDC |
|------|-----------|------|
| 目的 | 授权 | 身份认证 |
| 令牌 | access_token | access_token + id_token |
| 用户信息 | 无 | ID Token + UserInfo |
| 标准 | RFC 6749 | OpenID Connect Core 1.0 |

## ID Token = JWT 身份断言

```json
{
  "iss": "https://accounts.google.com",
  "sub": "1234567890",
  "aud": "client-id",
  "exp": 1691678400,
  "iat": 1691674800,
  "auth_time": 1691674800,
  "nonce": "abc123",
  "name": "Alice",
  "email": "alice@example.com",
  "email_verified": true,
  "picture": "https://..."
}
```

| 字段 | 含义 |
|------|------|
| `iss` | 颁发者（Authorization Server URL）|
| `sub` | 用户唯一 ID |
| `aud` | 客户端 ID |
| `exp` | 过期时间 |
| `iat` | 颁发时间 |
| `nonce` | 防重放（必须绑定）|

## 实战：OIDC 登录流程

```
1. 用户点击"用 Google 登录"
   GET /authorize?
     response_type=code
     &scope=openid+profile+email  ← 关键：openid scope
     &client_id=xxx
     &redirect_uri=https://app.com/callback
     &nonce=random123  ← 防 replay

2. Google 登录 + 同意 → 返回 code

3. 后端用 code 换 token
   {
     "access_token": "...",
     "id_token": "...",  ← JWT 身份
     "refresh_token": "..."
   }

4. 验证 ID Token
   - 检查 iss == "https://accounts.google.com"
   - 检查 aud == client_id
   - 检查 exp > now
   - 检查 nonce == random123
   - 用 JWKS 验证签名
```

## 实战：前端解析 ID Token

```javascript
// OIDC 客户端库（oidc-client-ts）
const userManager = new UserManager({
  authority: "https://accounts.google.com",
  client_id: "xxx.apps.googleusercontent.com",
  redirect_uri: "https://app.com/callback",
  response_type: "code",
  scope: "openid profile email",
});

userManager.signinRedirect();
// 登录完成后自动获取 id_token
const user = await userManager.getUser();
console.log(user.profile);  // 用户信息
```

## 实战：后端校验 ID Token

```python
import jwt
from jwt import PyJWKClient

jwks_client = PyJWKClient("https://accounts.google.com/.well-known/jwks.json")

def verify_id_token(id_token: str, client_id: str, nonce: str):
    signing_key = jwks_client.get_signing_key_from_jwt(id_token)
    payload = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=client_id,
        issuer="https://accounts.google.com",
    )
    if payload["nonce"] != nonce:
        raise ValueError("Invalid nonce")
    return payload
```

## 实战：OIDC Discovery

每个 OIDC 提供商都暴露 `.well-known/openid-configuration`：

```json
{
  "issuer": "https://accounts.google.com",
  "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
  "token_endpoint": "https://oauth2.googleapis.com/token",
  "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
  "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs",
  "scopes_supported": ["openid", "email", "profile"],
  "response_types_supported": ["code", "id_token", "token id_token"]
}
```

## OIDC 提供商对比

| 提供商 | 特点 | 适合 |
|--------|------|------|
| **Auth0** | 商业、SaaS 领先 | 中小企业 |
| **Keycloak** | 开源、CNCF 沙箱 | 自托管 / 企业 |
| **Okta** | 商业、企业级 | 大企业 |
| **AWS Cognito** | AWS 生态 | AWS 架构 |
| **Spring Authorization Server** | Java 开源 | Spring 项目 |
| **Ory Hydra** | Go 开源 | 云原生 |

## 关联章节

- **02-auth/oauth2**：OAuth 2.0 基础
- **02-auth/jwt**：JWT 详细结构
- **02-auth/saml**：SAML 企业 SSO（XML 时代）

## 一句话总结

> **OIDC = OAuth 2.0 + ID Token（JWT）**。**关键 scope：openid**。**三件套：authorization / token / userinfo**。**前端 SPA 用 oidc-client-ts，后端用 JWKS 验证签名**。
