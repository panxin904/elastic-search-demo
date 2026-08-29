---
title: JWT 详解
date: 2026-08-15  # date-auto-injected
---

# JWT（JSON Web Token）详解

## 一句话总结

> **JWT = 自包含的令牌**（Header + Payload + Signature）**。**3 类算法：HS256（对称）/ RS256（非对称）/ ES256（椭圆曲线）**。**优势：无状态 / 跨域 / 可携信息**。**陷阱：注销难 / 体积大 / 不能放敏感数据**。

---

## JWT 结构

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.  ← Header
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIn0.  ← Payload
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  ← Signature
```

### Header（算法 + 类型）

```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

### Payload（声明）

```json
{
  "iss": "https://auth.example.com",
  "sub": "user_123",
  "aud": "api.example.com",
  "exp": 1691678400,
  "iat": 1691674800,
  "jti": "abc-123",
  "scope": "read:user write:user",
  "role": "admin"
}
```

### Signature

```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  secret
)
```

## 3 类签名算法

| 算法 | 密钥 | 性能 | 场景 |
|------|------|------|------|
| **HS256** | 共享密钥 | 快 | 单体应用 |
| **RS256** | RSA 公私钥 | 慢 | 多服务验证 |
| **ES256** | ECDSA 公私钥 | 极快 | 现代推荐 |
| **EdDSA** | Ed25519 | 极快 | 高安全 |

## 实战：Python 用 JWT

```python
import jwt
from datetime import datetime, timedelta

# 签发
payload = {
    "sub": "user_123",
    "role": "admin",
    "exp": datetime.utcnow() + timedelta(hours=1),
    "iat": datetime.utcnow(),
}
token = jwt.encode(payload, "secret", algorithm="HS256")

# 验证
try:
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    return "Token expired"
except jwt.InvalidTokenError:
    return "Invalid token"
```

## 实战：RS256（非对称，微服务场景）

```bash
# 1. 生成密钥对
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem

# 2. Auth Server 用 private 签
# 3. Resource Server 用 public 验（无需密钥协商）
```

```java
// Auth Server 签发
String jwt = Jwts.builder()
    .setSubject("user_123")
    .signWith(SignatureAlgorithm.RS256, privateKey)
    .compact();

// Resource Server 验证
Jws<Claims> claims = Jwts.parserBuilder()
    .setSigningKey(publicKey)
    .build()
    .parseClaimsJws(jwt);
```

## 实战：JWT 攻击 + 防御

### 攻击 1：none 算法

```python
# ❌ 漏洞：允许 alg=none
header = {"alg": "none", "typ": "JWT"}
# 攻击者构造无签名 token
# 某些库会接受

# ✅ 防御：强制验证算法
jwt.decode(token, key, algorithms=["HS256"])  # 显式指定
```

### 攻击 2：算法混淆

```python
# 攻击者用公钥当 HMAC 密钥（前提：服务端误用 RS256 公钥做 HS256 验签）
# 攻击 payload：alg=HS256
# HMAC token with public_key

# ✅ 防御：显式验证算法，不让攻击者切换
```

### 攻击 3：弱密钥

```python
# ❌ 密钥太短
jwt.encode(payload, "secret", algorithm="HS256")

# ✅ 至少 256 bit
jwt.encode(payload, "0" * 32, algorithm="HS256")
```

### 防御清单

| 措施 | 落地 |
|------|------|
| 强制算法 | 显示传入 `algorithms=["HS256"]` |
| 短 TTL | access_token 15 min、refresh_token 7 天 |
| 黑名单 | 注销时加入 Redis blacklist |
| HTTPS 强制 | 防中间人 |
| 不放敏感数据 | Payload 是 base64 不是加密 |
| 密钥轮换 | 季度轮换 |

## 实战：JWT 注销

```python
# JWT 默认无状态，注销难
# 方案：黑名单 + Redis
def revoke_jwt(jti: str):
    redis.setex(f"jwt:revoked:{jti}", remaining_ttl, "1")

# 验证时检查
def is_revoked(jti: str) -> bool:
    return redis.exists(f"jwt:revoked:{jti}")
```

## 实战：Spring Security JWT 过滤器

```java
@Component
public class JwtFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain) {
        String token = extractToken(req);
        if (token != null) {
            Claims claims = Jwts.parserBuilder()
                .setSigningKey(publicKey)
                .build()
                .parseClaimsJws(token)
                .getBody();
            // 验证黑名单
            if (jwtBlacklist.isRevoked(claims.getId())) {
                throw new JwtException("Revoked");
            }
            SecurityContextHolder.getContext().setAuthentication(
                new JwtAuthentication(claims)
            );
        }
        chain.doFilter(req, res);
    }
}
```

## 关联章节

- **02-auth/oauth2**：OAuth 2.0 access_token 通常是 JWT
- **02-auth/oidc**：OIDC ID Token = JWT
- **01-web-top10/a07-auth-failure**：A07 认证失效

## 一句话总结

> **JWT = 自包含令牌**。**单体用 HS256，微服务用 RS256/ES256**。**不存敏感数据，强制算法白名单，TTL 短**。**注销用黑名单**。


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

![jwt structure](/jwt-structure.svg)
