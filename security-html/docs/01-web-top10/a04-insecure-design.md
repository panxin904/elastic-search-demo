---
title: A04 不安全设计
date: 2026-08-15  # date-auto-injected
---

# A04 · Insecure Design（不安全设计）

## 一句话总结

> **A04 = 设计阶段的安全缺失**。**不是 bug，是 architecturally flawed**。**核心：威胁建模（STRIDE / PASTA） + 安全设计模式 + 限流 / 幂等 / 状态机**。

---

## 什么是"不安全设计"

A04 是 2025 新独立的类别——**有些问题无法通过代码修复，只能重设计**：

| 错误的设计 | 危害 |
|----------|------|
| 密码重置无状态机（任何人都能无限次重试） | 邮箱轰炸 / 暴力破解 |
| 找回密码返回原密码 | 数据库泄漏 = 密码全裸 |
| 业务流程允许跳过验证步骤 | 跳过 KYC / 风控 |
| 无速率限制 | 暴力破解 / 资源耗尽 |
| 关键操作无二次验证 | 单一密码泄漏 = 全面失守 |
| 单一密码当唯一 MFA | 钓鱼失败 |

## 案例：密码找回流程设计

```python
# ❌ 不安全设计：返回数据库里明文密码
@app.post("/forgot-password")
def forgot(email: str):
    user = db.users.find_one(email=email)
    return {"password": user.password}  # 灾难！

# ✅ 安全设计：发邮件 + 一次性 token + 强制改密码
@app.post("/forgot-password")
def forgot(email: str):
    user = db.users.find_one(email=email)
    token = secrets.token_urlsafe(32)
    db.reset_tokens.insert({"user_id": user.id, "token": token, "expires_at": now + 15min})
    send_email(email, f"https://example.com/reset?token={token}")
    return {"message": "Check your email"}
```

## 威胁建模（STRIDE）

| 维度 | 威胁 | 缓解 |
|------|------|------|
| **S**poofing 欺骗 | 伪造身份 | MFA / 数字证书 |
| **T**ampering 篡改 | 改数据 | 签名 / 哈希 |
| **R**epudiation 抵赖 | 否认操作 | 审计日志 |
| **I**nformation Disclosure | 数据泄漏 | 加密 / 最小权限 |
| **D**enial of Service | 拒绝服务 | 限流 / 熔断 |
| **E**levation of Privilege | 提权 | RBAC / 最小权限 |

### 实战：电商下单流程 STRIDE

```
┌────────────────────────────────────────┐
│  流程：浏览 → 加购 → 支付 → 完成        │
├────────────────────────────────────────┤
│  S 欺骗：登录态伪造 → MFA 强制          │
│  T 篡改：订单金额改 → 服务端校验        │
│  R 抵赖：支付失败纠纷 → 完整操作日志    │
│  I 泄漏：消费数据 → 静态加密            │
│  D 拒绝：黄牛抢 → 限流 + 验证码         │
│  E 提权：普通用户改价格 → RBAC 校验     │
└────────────────────────────────────────┘
```

## 实战：限流（Rate Limiting）

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/login")
@limiter.limit("5/minute")  # 每分钟最多 5 次
def login(req: LoginRequest):
    ...
```

## 实战：幂等设计

```python
# 关键操作幂等（防止重复扣款）
@app.post("/api/v1/payment")
def pay(req: PaymentReq, idempotency_key: str = Header(...)):
    # 用 idempotency_key 防止重复
    if redis.exists(f"payment:{idempotency_key}"):
        return redis.get(f"payment:{idempotency_key}")
    result = do_payment(req)
    redis.setex(f"payment:{idempotency_key}", 3600, result)
    return result
```

## 关联章节

- **01-web-top10/a07-auth-failure**：A07 认证失效
- **02-auth/mfa**：MFA 强制补齐"Crucial operation"
- **06-zero-trust/overview**：零信任 = 持续验证

## 一句话总结

> **A04 不安全设计 = 架构层缺陷**。**修复需要：威胁建模 + 安全设计模式 + 限流 + 幂等 + 状态机**。**代码层补不回来的要回到设计**。


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
