---
title: REST 规范 / OpenAPI
---

# REST 规范 / OpenAPI

## 🌟 RESTful 是什么

Roy Fielding 2000 年提出的架构风格：**资源 + 表现层 + 状态转移**。

- **资源**（Resource）：一个 URL = 一个资源
- **HTTP 动词**：GET（读）/ POST（建）/ PUT（改）/ DELETE（删）/ PATCH（部分改）
- **无状态**：请求自带身份 / 上下文
- **统一接口**：可缓存、可分层

## 📐 URL 设计

```
GET    /users               列表
GET    /users/:id           详情
POST   /users               创建
PUT    /users/:id           覆盖更新
PATCH  /users/:id           部分更新
DELETE /users/:id           删除

# 嵌套资源
GET    /users/:id/orders    该用户的订单

# 复杂查询用 query string
GET    /orders?status=paid&page=2&sort=createdAt:desc
```

## 📬 HTTP 语义细节

| 状态码 | 含义 |
|--------|------|
| 200 | OK |
| 201 | 已创建 |
| 204 | 无内容（删除成功） |
| 301 | 永久重定向 |
| 304 | 缓存命中 |
| 400 | 客户端错误（请求格式） |
| 401 | 未认证 |
| 403 | 已认证但权限不够 |
| 404 | 资源不存在 |
| 409 | 冲突 |
| 422 | 校验失败 |
| 500 | 服务器错误 |

## 🛡️ 幂等性

```
PUT / DELETE / GET  → 幂等（多次调用结果一致）
POST / PATCH        → 不幂等（多次创建可能新增多份）
```

合理利用幂等性保证安全。

## 📦 常见响应格式

```json
// 列表 + 分页
{
  "data": [{ "id": 1, "name": "alice" }],
  "pagination": { "page": 1, "pageSize": 20, "total": 100 }
}

// 错误
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "用户不存在",
    "details": { "userId": 1 }
  }
}
```

## 🧾 OpenAPI（Swagger）

**机器可读的 API 描述**：用于 codegen、文档、Mock。

```yaml
# openapi.yaml
openapi: 3.1.0
info:
  title: 用户 API
  version: 1.0.0
paths:
  /users:
    get:
      summary: 用户列表
      parameters:
        - name: page
          in: query
          schema: { type: integer, default: 1 }
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:    { type: string }
        name:  { type: string }
```

### 工具

| 工具 | 作用 |
|------|------|
| Swagger UI | 文档 + Try it out |
| Redoc | 美观的文档 |
| openapi-typescript | OpenAPI → TypeScript |
| zod-to-openapi | zod schema → OpenAPI |
| Stoplight Elements | 交互式文档 |

```ts
// openapi-typescript 自动生成类型
import type { paths } from './openapi'

type User = paths['/users/{id}']['get']['responses']['200']['content']['application/json']
```

## 🆚 REST vs GraphQL vs tRPC

| | REST | GraphQL | tRPC |
|--|------|---------|------|
| 类型 | OpenAPI（外部） | Schema | TS 本身 |
| 学习 | 最低 | 中 | 低 |
| 缓存 | 浏览器原生 | 客户端实现 | Query 实现 |
| 多端 | ✅ | ✅ | ❌ 仅 TS |
| 文档 | OpenAPI 工具 | 自带 | 类型即文档 |

## 🔗 下一步

- [GraphQL](/09-data/graphql)
- [tRPC](/09-data/trpc)
- [WebSocket / SSE](/09-data/realtime)
