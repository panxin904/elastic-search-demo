---
title: 技术栈 总览
date: 2026-08-15  # date-auto-injected
---

# 技术栈

Java Web 开发的核心技术组件，涵盖**框架、数据库、中间件、工具链**。

## 技术栈全景

```
                          ┌─────────────────┐
                          │   Nginx / CDN    │  入口层
                          └────────┬────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │        Spring Boot          │  框架层
                    │  ┌──────────┬──────────┐    │
                    │  │Spring MVC│Spring Sec│    │
                    │  └──────────┴──────────┘    │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
  ┌───────┴───────┐      ┌────────┴────────┐      ┌───────┴───────┐
  │    MyBatis    │      │     Redis        │      │  消息队列 MQ  │  中间件层
  └───────┬───────┘      └────────┬────────┘      └───────┬───────┘
          │                       │                        │
  ┌───────┴───────┐      ┌────────┴────────┐      ┌───────┴───────┐
  │    MySQL      │      │   Redis Cluster │      │ RabbitMQ/Kafka │  数据层
  └───────────────┘      └─────────────────┘      └───────────────┘
```

## 框架层

| 技术 | 定位 | 核心功能 |
|---|---|---|
| [Spring Boot](/04-tech/spring-boot) | 开发框架 | 自动配置、起步依赖、内嵌容器、Actuator 监控 |
| [Spring MVC](/04-tech/spring-mvc) | Web 层框架 | 请求映射、参数绑定、拦截器、统一异常处理 |
| [Spring Security](/04-tech/spring-security) | 安全框架 | 认证、授权、JWT 集成、OAuth2 |

## 数据层

| 技术 | 定位 | 核心功能 |
|---|---|---|
| [MyBatis/Plus](/04-tech/mybatis) | ORM 框架 | XML/注解 SQL、动态 SQL、分页插件、代码生成 |
| [MySQL](/04-tech/mysql) | 关系型数据库 | 索引优化、SQL 调优、事务隔离、主从复制 |
| [Redis](/04-tech/redis) | 缓存/NoSQL | KV 存储、分布式锁、消息队列、排行榜、位图 |

## 中间件

| 技术 | 定位 | 核心功能 |
|---|---|---|
| [消息队列](/04-tech/message-queue) | 异步消息 | 解耦、削峰、异步处理、最终一致性 |
| [Nginx](/04-tech/nginx) | 反向代理 | 负载均衡、静态资源、HTTPS、限流 |

## 工具链

| 技术 | 定位 | 核心功能 |
|---|---|---|
| [构建工具](/04-tech/build-tools) | 项目构建 | 依赖管理、多模块、打包、profile 环境切换 |
| [Docker](/04-tech/docker) | 容器化 | 镜像构建、容器编排、环境一致性 |
| [测试框架](/04-tech/testing) | 测试 | JUnit5 + Mockito + SpringBootTest + H2 |
| [接口文档](/04-tech/api-doc) | API 文档 | Swagger/Knife4j 自动生成在线文档 |

## 技术选型建议

### 新手入门栈

```
Spring Boot + Spring MVC + MyBatis-Plus + MySQL + Redis + Maven
```

这套组合够用 80% 的中小型项目，社区资料丰富，上手快。

### 进阶企业栈

```
Spring Boot + Spring Cloud Alibaba (Nacos + Sentinel + Seata)
+ MyBatis-Plus + MySQL + Redis + RocketMQ + Docker + Nginx
```

适用于微服务架构、高并发场景、分布式事务需求。

## 本层在图谱中的位置

<KnowledgeGraph mode="full" :height="500" />

<!-- svg-injected:do-not-edit -->

## 图示：JVM 运行时内存模型

![JVM 运行时内存模型](/jvm-memory-model.svg)
