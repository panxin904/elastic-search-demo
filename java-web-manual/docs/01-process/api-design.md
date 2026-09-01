---
title: 接口设计
date: 2026-08-15  # date-auto-injected
---

# 接口设计

接口是前后端协作的契约，设计好坏直接影响开发效率和系统质量。

## RESTful 设计原则

### URL 命名规范

```
GET     /api/users          # 查询用户列表
GET     /api/users/{id}     # 查询单个用户
POST    /api/users          # 创建用户
PUT     /api/users/{id}     # 全量更新用户
PATCH   /api/users/{id}     # 部分更新用户
DELETE  /api/users/{id}     # 删除用户
```

<div class="kg-note">
<strong>规范</strong>：URL 用名词复数、小写、短横线分隔；资源嵌套不超过两层。
</div>

### 统一响应体

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "username": "zhangsan"
  },
  "traceId": "a1b2c3d4"
}
```

```java
public class Result<T> {
    private int code;
    private String message;
    private T data;
    private String traceId;

    public static <T> Result<T> success(T data) { ... }
    public static <T> Result<T> error(int code, String message) { ... }
}
```

### 错误码规范

| 范围 | 含义 | 示例 |
|---|---|---|
| 0 | 成功 | |
| 1xxx | 参数错误 | 1001-参数缺失, 1002-参数格式错误 |
| 2xxx | 业务错误 | 2001-库存不足, 2002-订单已取消 |
| 3xxx | 权限错误 | 3001-未登录, 3002-无权限 |
| 5xxx | 系统错误 | 5001-数据库异常, 5002-第三方服务异常 |

### 分页规范

请求：
```
GET /api/orders?page=1&size=20&sort=create_time,desc
```

响应：
```json
{
  "code": 0,
  "data": {
    "records": [...],
    "total": 100,
    "page": 1,
    "size": 20,
    "pages": 5
  }
}
```

### 接口文档

每个接口需要包含：

```markdown
## 创建订单

**URL**: POST /api/orders
**描述**: 用户创建新订单
**认证**: Bearer Token

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| items | List | 是 | 商品列表 |
| addressId | Long | 是 | 收货地址ID |
| remark | String | 否 | 备注 |

**请求示例**:
```json
{
  "items": [
    {"productId": 1, "quantity": 2}
  ],
  "addressId": 100,
  "remark": "尽快发货"
}
```

**响应示例**:
```json
{
  "code": 0,
  "data": {
    "orderId": 12345,
    "totalAmount": 19900
  }
}
```
```

## 接口设计检查清单

- [ ] URL 使用 RESTful 风格（名词复数）
- [ ] 统一响应体格式（code/message/data）
- [ ] 定义了错误码体系
- [ ] 分页接口统一参数（page/size）
- [ ] 敏感接口加了认证鉴权
- [ ] 幂等接口有防重复提交机制
- [ ] 接口文档已同步（Swagger/Knife4j）
- [ ] 大字段/文件上传用 multipart

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="api-design" :height="400" />
