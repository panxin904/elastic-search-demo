---
title: A07 认证失效
---

# A07 · Identification & Authentication Failures（认证失效）

## 一句话总结

> **A07 = 身份认证机制被突破**。**典型：弱密码 / 明文凭证 / Session ID 暴露 / 登录端点 brute force**。**防御：强密码策略 + MFA + 限流 + 安全的 Session 管理**。

---

## 常见认证失效

| 失效点 | 危害 |
|--------|------|
| 允许弱密码（如 `123456`） | 字典攻击秒破 |
| 密码明文传输 | 中间人窃取 |
| Session ID 在 URL | referer 泄漏 |
| Session 永不过期 | 一次性登录终身有效 |
| 登录端点无限次试 | 暴力破解 |
| 密码找回流程缺陷 | 接管任意账号 |
| 凭证填充（Credential Stuffing） | 撞库 |
| 暴露测试账号 | demo:guest/123 |

## 实战：密码策略

```python
# ❌ 弱密码
def validate_password(pwd):
    return len(pwd) >= 6

# ✅ NIST SP 800-63B 标准
def validate_password(pwd: str) -> bool:
    if len(pwd) < 12:
        return False
    # 检查 HIBP 泄漏库（k-anonymity API）
    import hashlib
    sha = hashlib.sha1(pwd.encode()).hexdigest().upper()
    prefix, suffix = sha[:5], sha[5:]
    r = httpx.get(f"https://api.pwnedpasswords.com/range/{prefix}")
    return suffix not in r.text
```

## 实战：登录限流

```python
# Redis 滑动窗口
def is_rate_limited(ip: str, attempts: int = 5) -> bool:
    key = f"login:fail:{ip}"
    count = redis.incr(key)
    redis.expire(key, 900)  # 15 分钟
    if count > attempts:
        return True
    return False

# 锁定 15 分钟
def lock_account(user_id: int):
    redis.setex(f"account:locked:{user_id}", 900, "1")
```

## 实战：Session 管理

```python
# ❌ Session ID in URL（referer 泄漏）
@app.get("/dashboard")
def dashboard(session_id: str):  # 危险！
    return check_session(session_id)

# ✅ Cookie + HttpOnly + Secure + SameSite
response.set_cookie(
    "session_id",
    value=secrets.token_urlsafe(32),
    httponly=True,
    secure=True,
    samesite="strict",
    max_age=3600,  # 1 小时过期
)
```

nginx 安全头：

```nginx
add_header Set-Cookie "session_id=xxx; HttpOnly; Secure; SameSite=Strict";
add_header X-Frame-Options "DENY";
add_header X-Content-Type-Options "nosniff";
```

## 实战：MFA 实现

```python
# TOTP (Time-based One-Time Password)
import pyotp

# 用户注册时生成 secret
secret = pyotp.random_base32()
db.user.update(mfa_secret=secret)

# 登录时
totp = pyotp.TOTP(secret)
user_token = input("Enter MFA code: ")
if totp.verify(user_token, valid_window=1):
    return "Login success"
```

## 实战：密码找回安全

```python
# ❌ 缺陷：返回当前密码
@app.post("/forgot-password")
def forgot(email: str):
    user = db.users.find_by(email=email)
    return {"current_password": user.password}

# ✅ 安全：发邮件 + 一次性 token
@app.post("/forgot-password")
def forgot(email: str):
    user = db.users.find_by(email=email)
    token = secrets.token_urlsafe(32)
    db.reset_tokens.insert({
        "user_id": user.id,
        "token": hashlib.sha256(token.encode()).hexdigest(),
        "expires_at": datetime.now() + timedelta(minutes=15),
    })
    send_email(email, f"https://example.com/reset?token={token}")
```

## 防御清单

| 措施 | 落地 |
|------|------|
| 强密码 | NIST 800-63B / HIBP 检查 |
| 密码哈希 | Argon2 / bcrypt |
| MFA | TOTP / WebAuthn / FIDO2 |
| 限流 | 登录 5 次/15min 锁 |
| 安全的 Session | HttpOnly + Secure + SameSite + 短 TTL |
| 找回流程 | 一次性 token + 15 分钟过期 |
| 业务防御 | 异常登录告警 / 异地提醒 |

## 关联章节

- **02-auth/overview**：认证协议地图
- **02-auth/jwt**：JWT Session 化
- **02-auth/mfa**：MFA 进阶
- **02-auth/session-attack**：Session 攻击矩阵

## 一句话总结

> **A07 认证失效 = 弱认证或认证失效**。**核心：强密码 + MFA + 安全 Session + 限流 + 找回流程设计**。**永远不要相信前端校验**。


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
