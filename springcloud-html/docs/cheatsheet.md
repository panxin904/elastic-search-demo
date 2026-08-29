---
title: 组件速查
date: 2026-08-15  # date-auto-injected
---

# 📋 Spring Cloud 组件速查

> 30+ 常用配置模板，**支持搜索 + 一键复制**。覆盖 Nacos / Gateway / 负载均衡 / 安全 / Sentinel / Seata / OpenFeign / 消息 8 大类。

<ComponentCheatsheet />

## 🎯 常用配置速查

### 🚀 项目脚手架（start.spring.io）

```xml
<!-- 必选依赖 -->
- Spring Boot DevTools
- Spring Web
- Spring Data JPA（或 MyBatis-Plus）
- MySQL Driver
- Lombok
- Validation
- Spring Security（如果做认证）
- Spring Cloud Alibaba Nacos Discovery
- Spring Cloud Alibaba Nacos Config
- Spring Cloud LoadBalancer
- OpenFeign
- Gateway
```

### 🔧 通用 application.yml 模板

```yaml
server:
  port: 8080
  servlet:
    context-path: /api
  compression:
    enabled: true
    mime-types: application/json

spring:
  application:
    name: my-service
  profiles:
    active: dev
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: GMT+8
    default-property-inclusion: non_null

# 日志
logging:
  level:
    root: info
    com.example: debug
  pattern:
    console: '%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n'
```

### 🐛 常见端口冲突

| 服务 | 默认端口 |
|---|---|
| Nacos Server | 8848 |
| Nacos Console | 8080 |
| Sentinel Dashboard | 8080 |
| Gateway | 8080（要改！） |
| 业务服务 | 8081+ |

## 🔗 关联工具

- [⚙️ 配置模拟器](#) - 实时生成 application.yml
- [🌊 请求链路演示](#) - 微服务请求流程可视化
- [💼 综合实战项目](/06-practice/comprehensive) - 完整电商项目