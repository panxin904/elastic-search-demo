---
title: RESTful API 设计
---

# RESTful API 设计

<div class="nt-badge nt-badge-app">应用层</div>
<div class="nt-badge nt-badge-basics">基础</div>

REST（Representational State Transfer）是一种基于 HTTP 的**资源导向**架构风格，被广泛用于 Web API 设计。

## 1. REST 六大原则

| 原则 | 含义 |
| --- | --- |
| 客户端-服务器 | 前后端分离 |
| 无状态 | 每个请求独立，服务器不保存会话 |
| 可缓存 | 响应需明确是否可缓存 |
| 统一接口 | URI 资源 + HTTP 动词 |
| 分层系统 | 客户端不感知代理、网关 |
| 按需代码（可选） | 服务器可下发脚本（如 JS） |

## 2. URL 设计

### 2.1 资源（名词）

```
GET    /users              用户列表
GET    /users/123          单个用户
POST   /users              新建用户
PUT    /users/123          整体替换
PATCH  /users/123          部分更新
DELETE /users/123          删除用户

GET    /users/123/orders   用户的订单
```

### 2.2 避免动词

```
✗  /getUsers
✗  /createUser
✗  /deleteUser?id=123
✓  GET /users
✓  POST /users
✓  DELETE /users/123
```

### 2.3 复数名词

```
✓  /users /orders /products
✗  /user /order /product
```

## 3. HTTP 动词

| 动词 | 幂等 | 安全 | 用途 |
| --- | --- | --- | --- |
| GET | ✓ | ✓ | 获取 |
| POST | ✗ | ✗ | 创建 / 触发 |
| PUT | ✓ | ✗ | 全量更新 |
| PATCH | ✗ | ✗ | 部分更新 |
| DELETE | ✓ | ✗ | 删除 |

## 4. 状态码

| 场景 | 状态码 |
| --- | --- |
| 成功 | 200 / 201 / 204 |
| 客户端错误 | 400 / 401 / 403 / 404 / 409 / 422 / 429 |
| 服务端错误 | 500 / 502 / 503 / 504 |
| 重定向 | 301 / 302 / 304 |

**最佳实践**：
- 成功创建返回 201 + Location 头
- 删除成功返回 204 No Content
- 部分成功（如批量）可返回 207 Multi-Status

## 5. 命名规范

### 5.1 路径

```
小写 + 短横线：/user-profiles
不用下划线：/user_profiles  ✗
不用驼峰：/userProfiles      ✗
```

### 5.2 字段

```
snake_case:  user_id, created_at   ← JSON / 数据库常用
camelCase:   userId, createdAt     ← 前后端 JS
```

### 5.3 版本

```
URL:       /api/v1/users
Header:    Accept: application/vnd.example.v1+json
Subdomain: api.v1.example.com
```

## 6. 过滤 / 排序 / 分页

```
GET /users?status=active&role=admin
GET /users?sort=-created_at            ← 降序
GET /users?page=2&size=20              ← 偏移分页
GET /users?limit=20&offset=40
GET /users?cursor=eyJpZCI6MTIzfQ==     ← 游标分页
```

## 7. 响应结构

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "id": 123,
    "name": "Alice",
    "email": "alice@example.com"
  }
}
```

或列表：

```json
{
  "code": 0,
  "data": [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"}
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "size": 20
  }
}
```

## 8. 错误响应

```json
{
  "code": 40001,
  "message": "Invalid email format",
  "errors": [
    {
      "field": "email",
      "code": "INVALID_FORMAT",
      "message": "Must be a valid email"
    }
  ],
  "requestId": "abc-123"
}
```

| 字段 | 作用 |
| --- | --- |
| code | 业务错误码（数字 / 字符串） |
| message | 人类可读描述 |
| errors | 字段级错误（用于表单） |
| requestId | 服务端追踪 ID |

## 9. HATEOAS

响应中包含相关链接：

```json
{
  "id": 123,
  "name": "Alice",
  "links": {
    "self": "/users/123",
    "orders": "/users/123/orders",
    "avatar": "/users/123/avatar"
  }
}
```

## 10. 内容协商

```
Accept: application/json
Accept-Language: zh-CN,en-US;q=0.9
Accept-Encoding: gzip, br
User-Agent: ...
```

## 11. 幂等性

- 客户端可通过**幂等键**（Idempotency-Key 头）保证重试安全
- 服务器缓存本次结果，重试时返回同样响应

```
POST /payments
Idempotency-Key: pay-2026-08-05-abc
```

## 12. 鉴权

| 方式 | 适用 |
| --- | --- |
| Basic Auth | 内部 |
| Bearer Token | API |
| OAuth 2.0 | 第三方授权 |
| API Key | 简单场景 |
| JWT | 无状态 |
| mTLS | 高安全 |

## 13. 限流

| Header | 含义 |
| --- | --- |
| X-RateLimit-Limit | 配额 |
| X-RateLimit-Remaining | 剩余 |
| X-RateLimit-Reset | 重置时间（秒） |
| Retry-After | 触发限流后多久可重试 |

## 14. REST 优劣

| 优势 | 不足 |
| --- | --- |
| 简单、通用 | 多次请求（Over-fetching） |
| 无状态、易水平扩展 | 难以表达复杂关系 |
| 工具链丰富 | 实时性弱 |
| 缓存友好 | 不适合流式 |

## 15. 常见面试题

1. **REST 核心思想？** 资源 + HTTP 动词 + 状态码。
2. **PUT vs PATCH？** PUT 全量，PATCH 部分。
3. **幂等性？** 多次请求结果一致。
4. **状态码 401 vs 403？** 401 未认证，403 已认证但无权限。
5. **分页策略？** offset/limit（小数据集）或 cursor（大数据）。
6. **REST vs RPC？** REST 面向资源 + 文本；RPC 面向动作 + 二进制（如 gRPC）。
