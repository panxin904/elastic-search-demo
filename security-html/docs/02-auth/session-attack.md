---
title: Session 攻击
date: 2026-08-15  # date-auto-injected
---

# Session 攻击矩阵

## 一句话总结

> **Session = 服务端识别用户身份**。**4 大攻击：Session 固定 / 劫持 / 伪造 / CSRF**。**防御：HttpOnly + Secure + SameSite + 短 TTL + 重新生成**。

---

## Session 4 大攻击

### 1. Session 固定（Session Fixation）

```python
# 攻击者先获取一个 session_id
# 然后诱导用户用这个 session_id 登录
# 用户登录后，session_id 不变 → 攻击者接管

# 攻击流程
1. 攻击者访问 https://app.com → 拿到 session_id=ATTACKER_SESSION
2. 攻击者诱导用户：https://app.com/?session_id=ATTACKER_SESSION
3. 用户登录，session_id 不变
4. 攻击者用 ATTACKER_SESSION 接管账号
```

```python
# ✅ 防御：登录后重新生成 session_id
@app.post("/login")
def login(req: LoginRequest, response: Response):
    user = authenticate(req)
    session.regenerate()  # ← 关键
    session["user_id"] = user.id
    return {"token": session.id}
```

### 2. Session 劫持（Session Hijacking）

```python
# 攻击者通过 XSS / 网络嗅探 / 物理访问 拿到 session_id

# XSS 攻击
document.cookie  // 偷 cookie
# 防御：HttpOnly（JavaScript 无法访问）

# 中间人攻击
# 嗅探 HTTP 流量拿到 session_id
# 防御：HTTPS + Secure cookie
```

```python
# ✅ 防御
response.set_cookie(
    "session_id",
    value=session_id,
    httponly=True,    # 防止 XSS 偷 cookie
    secure=True,      # 只走 HTTPS
    samesite="strict", # 防 CSRF
)
```

### 3. Session 伪造（Session Forgery）

```python
# 攻击者构造假的 session_id（前提：算法被猜到）

# ❌ 弱 session_id
session_id = "user123"  # 可预测

# ✅ 加密随机
import secrets
session_id = secrets.token_urlsafe(32)  # 256 bit 不可预测
```

### 4. CSRF（Cross-Site Request Forgery）

```html
<!-- 攻击者网站诱导用户发起请求 -->
<img src="https://bank.com/transfer?to=attacker&amount=1000" />
<!-- 用户的银行 cookie 自动附上 -->
```

```python
# ✅ 防御：SameSite Cookie + CSRF Token
response.set_cookie("session_id", ..., samesite="strict")

# 或 CSRF Token
@app.post("/transfer")
def transfer(req: TransferRequest, csrf_token: str = Header(...)):
    if csrf_token != session["csrf_token"]:
        raise HTTPException(403, "CSRF token mismatch")
    return do_transfer(req)
```

## 实战：Spring Security Session 配置

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .sessionManagement(session -> session
                .sessionFixationProtection()
                .sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
                .maximumSessions(1)  // 单点登录
                .maxSessionsPreventsLogin(false)
            )
            .csrf(csrf -> csrf
                .csrfTokenRepository(CookieCsrfTokenRepository.withHttpOnlyFalse())
            );
        return http.build();
    }
}
```

## 实战：分布式 Session

### 方案 1：Redis 集中存储

```python
# Spring Session
spring.session.store-type=redis
spring.session.redis.namespace=myapp:session

# 多个应用实例共享 Redis
```

### 方案 2：JWT 替代

```python
# 完全无状态（JWT 自包含）
# 缺点：注销难、不能改
```

### 方案 3：粘性 Session

```nginx
# Nginx ip_hash
upstream backend {
    ip_hash;
    server backend1;
    server backend2;
}
# 缺点：负载不均
```

## 安全清单

| 措施 | 落地 |
|------|------|
| HttpOnly | 防 XSS |
| Secure | 仅 HTTPS |
| SameSite=Strict | 防 CSRF |
| 短 TTL | 30 分钟过期 |
| 重新生成 | 登录后 regen |
| 强随机 | secrets.token_urlsafe(32) |
| 多 session 限制 | 单点登录 |
| 异常检测 | 新地点告警 |

## 关联章节

- **02-auth/oauth2**：OAuth 2.0 替代 Session
- **02-auth/jwt**：JWT 替代 Session
- **01-web-top10/a07-auth-failure**：A07 认证失效

## 一句话总结

> **Session 4 大攻击 = 固定 / 劫持 / 伪造 / CSRF**。**防御：HttpOnly + Secure + SameSite + 重新生成 + 强随机**。**分布式 Session 用 Redis**。


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
