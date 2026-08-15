---
title: 分层架构
---

# 分层架构

分层架构是 Java Web 开发最核心的架构思想，核心原则是**上层依赖下层，下层不感知上层**。

## 经典三层

```
┌───────────────────────────────────────┐
│  Controller (表现层)                    │
│  - 接收 HTTP 请求                      │
│  - 参数校验 (@Valid)                    │
│  - 调用 Service                        │
│  - 封装返回 Result<T>                  │
├───────────────────────────────────────┤
│  Service (业务层)                       │
│  - 核心业务逻辑                         │
│  - 事务管理 (@Transactional)            │
│  - 调用多个 Mapper/外部服务              │
├───────────────────────────────────────┤
│  DAO/Mapper (持久层)                    │
│  - 数据库 CRUD                         │
│  - SQL 执行                            │
│  - 不包含业务逻辑                        │
└───────────────────────────────────────┘
```

## 层次边界规则

| 规则 | 说明 |
|---|---|
| Controller 不写业务 | 只做参数校验、调用 Service、返回结果 |
| Service 不碰 Request/Response | 参数和返回值用 DTO/VO，不依赖 Web 层 |
| Mapper 只做数据操作 | 不包含业务判断，不调用其他 Mapper |
| 跨层调用？不允许！ | Controller 不能直接调 Mapper |

## 对象转换链

```
HTTP Request → DTO → Service处理 → Entity → Mapper → DB
DB → Entity → Service组装 → VO → HTTP Response
```

```java
// DTO: 接收前端参数
public class UserCreateDTO {
    @NotBlank private String username;
    @NotBlank private String phone;
}

// VO: 返回给前端
public class UserVO {
    private Long id;
    private String username;
    private String phone;
    private LocalDateTime createTime;
}

// Entity: 数据库映射
@TableName("t_user")
public class User {
    private Long id;
    private String username;
    private String phone;
    private LocalDateTime createTime;
}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="layered-architecture" :height="400" />
