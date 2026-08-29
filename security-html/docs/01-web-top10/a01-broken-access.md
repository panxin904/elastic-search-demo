---
title: A01 访问控制失效
date: 2026-08-15  # date-auto-injected
---

# A01 · Broken Access Control（访问控制失效）

## 一句话总结

> **访问控制失效 = 越权访问**。**典型：水平越权（看别人的订单）/ 垂直越权（普通用户拿管理员权限）**。**防御：服务端校验 + 最小权限 + 资源所有权检查**。

---

## 什么是访问控制失效

访问控制是 Web 应用最基础的安全机制——**谁被允许做什么**。失效意味着：
- 用户 A 能访问用户 B 的资源（**水平越权 / IDOR**）
- 普通用户能调管理员 API（**垂直越权 / Privilege Escalation**）
- 没登录用户能访问登录后页面（**认证缺失**）

OWASP 2021 起，**A01 连续 4 年位居 Top 10 第一**。

## 典型攻击场景

### 1. 水平越权（IDOR）

```http
GET /api/v1/orders/12345
```

```http
GET /api/v1/orders/12346    ← 改个 ID，看别人的订单
GET /api/v1/users/789       ← 改个 ID，看别人的资料
```

```python
# ❌ 错误代码：直接信任 URL 里的 ID
@app.get("/api/v1/orders/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    return db.get(Order, order_id)

# ✅ 正确：校验资源所有权
@app.get("/api/v1/orders/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    order = db.get(Order, order_id)
    if order.user_id != current_user.id:
        raise HTTPException(403, "Forbidden")
    return order
```

### 2. 垂直越权

```http
# 普通用户尝试访问管理员路由
POST /api/v1/admin/users
Body: {"role": "admin"}
```

```python
# 防御：基于角色的访问控制（RBAC）
def require_admin(current_user: User = Depends(get_current_user)):
    if "admin" not in current_user.roles:
        raise HTTPException(403, "Admin only")
    return current_user

@app.delete("/api/v1/users/{user_id}", dependencies=[Depends(require_admin)])
def delete_user(user_id: int):
    db.delete(User, user_id)
```

## 实战案例：GitHub 私有仓库泄漏

某 API 端点没校验仓库归属，攻击者用 GitHub ID 遍历拿到私有仓库元数据。修复：服务端强制校验 `current_user` 对资源的所有权。

## 防御清单

| 措施 | 落地 |
|------|------|
| 默认拒绝 | `AuthorizationPolicy` 默认 deny |
| 所有权校验 | Service 层强制校验 `resource.owner_id == user.id` |
| 最小权限 | RBAC / OAuth 2.0 Scope |
| 失效访问 token | JWT blacklisting / 短 TTL |
| 审计日志 | 关键操作全留痕 |

## 关联章节

- **01-web-top10/a07-auth-failure**：A07 认证失效（前置）
- **02-auth/jwt**：JWT 无状态 vs 状态化撤销
- **06-zero-trust**：零信任 = 默认 deny + 持续验证

## 实战案例：GitHub 2018 私有仓库泄漏

```bash
# 2018 年 GitHub 事件：攻击者通过 GitHub API 遍历
# 枚举私有仓库 ID（数字递增）
# 拿到 1.6 万个私有仓库元数据
# 漏洞：API 端点 /repositories/:id 无 owner 校验
```

## 实战：Spring Security 权限注解

```java
@PreAuthorize("hasRole('ADMIN')")
public void deleteUser(Long id) { ... }

@PreAuthorize("@userSecurity.canDelete(#userId, authentication)")
public void deleteUser(Long userId) { ... }

@PostAuthorize("returnObject.owner == authentication.name")
public Order getOrder(Long id) { ... }
```

## 实战：OPA 策略统一管理

```rego
package api.authz

default allow = false

allow {
    input.method == "GET"
    input.path == "/api/v1/orders"
    input.user.role == "customer"
    input.resource.user_id == input.user.id
}

allow {
    input.method == "POST"
    input.path == "/api/v1/orders"
    input.user.role in ["customer", "guest"]
}
```

## 实战：审计日志（关键操作）

```python
@app.delete("/api/v1/users/{user_id}")
@require_admin
def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    user = db.get(User, user_id)
    audit_log.info(
        "user.deleted",
        actor=current_user.id,
        target=user_id,
        ip=request.remote_addr,
        user_agent=request.headers.get("User-Agent"),
    )
    db.delete(user)
```

## 一句话总结

> **A01 访问控制失效 = 越权访问**。**防护核心：每个 API 都校验「当前用户对资源的权限」**。**永远不要相信客户端传来的 ID**。


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
