---
title: RESTful 风格
date: 2026-08-15  # date-auto-injected
---

# RESTful API 设计

REST（Representational State Transfer）是一种资源导向的 API 设计风格。

## 核心原则

| 原则 | 说明 |
|---|---|
| 资源导向 | URL 表示资源（名词），而非动作（动词） |
| HTTP 方法表达操作 | GET查/POST增/PUT改/DELETE删 |
| 无状态 | 服务端不存客户端状态，每次请求自包含 |
| 统一接口 | 一致的 URL 格式、响应格式、错误码 |

## 最佳实践

```
GET    /api/v1/users          # 用户列表（分页）
GET    /api/v1/users/{id}     # 用户详情
POST   /api/v1/users          # 创建用户
PUT    /api/v1/users/{id}     # 全量更新
PATCH  /api/v1/users/{id}     # 部分更新
DELETE /api/v1/users/{id}     # 删除用户

GET    /api/v1/users/{id}/orders  # 用户的订单（子资源）
```

## 版本控制

```java
// URL 路径版本（推荐）
@GetMapping("/api/v1/users")
@GetMapping("/api/v2/users")  // v2 破坏性变更

// 请求头版本
Header: API-Version: v1
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="restful-api" :height="400" />
