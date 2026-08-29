---
title: MFA 多因素认证
date: 2026-08-15  # date-auto-injected
---

# MFA 多因素认证

## 一句话总结

> **MFA = 多因素认证**（密码 + 第二个因子）**。**3 因子：知识（密码）/ 持有（手机）/ 物理特征（指纹）**。**3 种实现：TOTP（短信/Authenticator）/ WebAuthn（FIDO2 硬件密钥）/ Push（Auth0 Guardian）**。**强 MFA = 99.9% 防账号接管**。

---

## 3 因子 + 4 主流实现

| 因子 | 例子 |
|------|------|
| **知识** | 密码 / PIN / 密保问题 |
| **持有** | 手机 / 硬件密钥 / 智能卡 |
| **物理特征** | 指纹 / 面部 / 虹膜 |

| MFA 方式 | 用户体验 | 安全性 | 成本 |
|---------|---------|--------|------|
| **短信验证码** | ★★★★★ | ★★ | 低 |
| **TOTP（Authenticator）** | ★★★★ | ★★★ | 低 |
| **Push 通知** | ★★★★ | ★★★ | 中 |
| **WebAuthn / FIDO2** | ★★★ | ★★★★★ | 中 |
| **硬件密钥（YubiKey）** | ★★★ | ★★★★★ | 高 |

## 实战：TOTP（Google Authenticator）

```python
import pyotp

# 用户注册：生成 secret
secret = pyotp.random_base32()
db.user.update(secret=secret)

# 生成 QR code（用户扫码）
import qrcode
uri = pyotp.totp.TOTP(secret).provisioning_uri(
    name=user.email,
    issuer_name="MyApp"
)
qrcode.make(uri).save("qr.png")

# 登录验证
@app.post("/login-mfa")
def verify_mfa(user_id: int, code: str):
    secret = db.user.get(user_id).secret
    totp = pyotp.TOTP(secret)
    if totp.verify(code, valid_window=1):  # ±30 秒
        return "Login success"
    return "Invalid"
```

## 实战：WebAuthn（FIDO2）

```javascript
// 注册
const credential = await navigator.credentials.create({
    publicKey: {
        challenge: new Uint8Array([...]),
        rp: { name: "MyApp" },
        user: {
            id: new Uint8Array([...]),
            name: "alice@example.com",
            displayName: "Alice"
        },
        pubKeyCredParams: [
            { type: "public-key", alg: -7 }  // ES256
        ],
    }
});

// 登录
const assertion = await navigator.credentials.get({
    publicKey: {
        challenge: new Uint8Array([...]),
        allowCredentials: [{ type: "public-key", id: credentialId }],
    }
});
```

## 实战：SMS 验证码（次优）

```python
import random

# 1. 生成 6 位
code = "".join(random.choices("0123456789", k=6))

# 2. 存 Redis（5 分钟过期）
redis.setex(f"sms:code:{phone}", 300, code)

# 3. 发短信
send_sms(phone, f"您的验证码：{code}，5 分钟内有效")

# 4. 验证
@app.post("/verify-sms")
def verify(phone: str, code: str):
    stored = redis.get(f"sms:code:{phone}")
    if stored and stored.decode() == code:
        redis.delete(f"sms:code:{phone}")
        return "OK"
    raise HTTPException(400, "Invalid")
```

## 实战：SMS 嗅探攻击 + 防御

| 攻击 | 防御 |
|------|------|
| SIM 卡交换 | 运营商 PIN / 强身份验证 |
| SS7 协议嗅探 | 不用 SMS |
| 短信木马 | 不用 SMS |
| 钓鱼 | 用户教育 |

**结论**：SMS MFA 不安全，**优先 TOTP / WebAuthn**。

## 实战：风险感知 MFA

```python
def require_mfa(user, request):
    if mfa_check_required(user, request):
        # 强制 MFA
        ...
    else:
        # 跳过 MFA（信任设备）
        ...

def mfa_check_required(user, request):
    # 设备不在白名单
    if not is_trusted_device(user, request.device_id):
        return True
    # 新地点
    if geo_distance(user.last_login_geo, request.geo) > 1000:
        return True
    # 5 个月内没 MFA
    if user.last_mfa_at < datetime.now() - timedelta(days=150):
        return True
    return False
```

## 实战：Spring Security MFA

```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/admin/**").hasAuthority("MFA_VERIFIED")
        )
        .addFilterAfter(new MfaFilter(), BasicAuthenticationFilter.class);
    return http.build();
}
```

## 实战：恢复码（Backup Codes）

```python
# 用户首次开 MFA 时生成 10 个一次性恢复码
recovery_codes = [secrets.token_hex(8) for _ in range(10)]
db.user.update(recovery_codes=recovery_codes)

# 用一次就标记
def use_recovery_code(user, code):
    codes = db.user.get(user).recovery_codes
    if code in codes:
        codes.remove(code)
        db.user.update(recovery_codes=codes)
        return True
    return False
```

## 关联章节

- **02-auth/overview**：认证协议地图
- **01-web-top10/a07-auth-failure**：A07 认证失效
- **01-web-top10/a04-insecure-design**：A04 不安全设计

## 一句话总结

> **MFA = 密码 + 第二因子**。**优先 TOTP / WebAuthn，避免 SMS**。**强 MFA = 99.9% 防账号接管**。**高敏操作（转账 / 改密）= 强制 MFA**。


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
