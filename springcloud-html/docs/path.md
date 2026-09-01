---
title: Spring Cloud 学习路径
date: 2026-08-15  # date-auto-injected
---

# 📖 Spring Cloud Alibaba 学习路径

> 不知道从哪里开始？按照这个路径，**5 阶段从入门到精通**，每阶段 1-3 周。

## 🛤️ 阶段一：Spring Boot 基础（1-2 周）

### 🎯 目标
掌握 Spring Boot 开发，能独立搭建 REST API 服务。

### 📚 学习内容

1. [🚀 快速开始](/01-springboot/quickstart) — 第一个 Spring Boot 应用
2. [⚙️ 自动配置原理](/01-springboot/auto-config) — @SpringBootApplication 魔法
3. [🌐 Web 开发](/01-springboot/web) — REST API、参数校验、统一异常
4. [💾 数据访问](/01-springboot/data) — Spring Data JPA、MyBatis-Plus
5. [🔄 事务管理](/01-springboot/transaction) — @Transactional 传播机制

### ✅ 检验标准

- ✅ 独立搭建 Spring Boot 项目
- ✅ 熟练使用常用注解
- ✅ 理解自动配置原理
- ✅ 能写 REST API + 异常处理

---

## 📚 阶段零：分布式理论基础（1 周，建议提前学习）

### 🎯 目标
掌握分布式系统的核心理论，从原理层面理解微服务架构。

### 📚 学习内容

1. [⚖️ CAP 与 BASE 理论](/07-distributed/cap-base) — 分布式理论基石
2. [🏗️ 分布式架构模式](/07-distributed/architecture) — 微服务 / SOA / 事件驱动
3. [🔐 分布式锁](/07-distributed/distributed-lock) — Redis / ZooKeeper 方案
4. [💰 分布式事务](/07-distributed/distributed-transaction) — 2PC / TCC / AT / Saga
5. [🆔 分布式 ID](/07-distributed/distributed-id) — Snowflake / 号段模式
6. [💬 分布式消息队列](/07-distributed/distributed-mq) — Kafka / RocketMQ
7. [📊 分布式存储](/07-distributed/distributed-storage) — 分库分表
8. [🔄 分布式协调](/07-distributed/distributed-coordination) — ZooKeeper / etcd
9. [🔍 分布式追踪](/07-distributed/distributed-tracing) — Sleuth / SkyWalking
10. [🛡️ 高可用与限流熔断](/07-distributed/high-availability) — Sentinel / 熔断降级

### ✅ 检验标准

- ✅ 理解 CAP / BASE 理论
- ✅ 掌握分布式锁的多种实现
- ✅ 理解分布式事务的多种方案
- ✅ 掌握分布式追踪原理
- ✅ 理解雪崩场景与防护策略

---

## ⚡ 阶段二：微服务核心组件（2-3 周）

### 🎯 目标
掌握 Nacos + Gateway + LoadBalancer 三大核心组件。

### 📚 学习内容

1. [📚 Spring Cloud Alibaba 总览](/02-overview/intro) — 生态与版本
2. [🌐 Nacos 服务发现](/02-overview/nacos-discovery) — 替代 Eureka
3. [⚙️ Nacos 配置中心](/02-overview/nacos-config) — 动态配置 + Namespace
4. [🌊 Gateway 基础](/03-gateway/basic) — 路由 / 断言 / 过滤器
5. [🛣️ 路由与断言](/03-gateway/route) — 各种 Predicate
6. [🔧 过滤器](/03-gateway/filter) — 自定义 Filter
7. [🔄 LoadBalancer](/04-loadbalancer/basic) — 客户端负载均衡
8. [🎯 负载均衡策略](/04-loadbalancer/strategy) — 轮询 / 随机 / 自定义

### ✅ 检验标准

- ✅ 搭建 Nacos Server 集群
- ✅ 微服务注册到 Nacos
- ✅ Gateway 统一路由
- ✅ 理解负载均衡原理

---

## 🔐 阶段三：认证授权（2-3 周）

### 🎯 目标
掌握 Spring Security + OAuth2 + JWT 完整方案。

### 📚 学习内容

1. [🛡️ Spring Security 基础](/05-security/basic) — 认证与授权
2. [🔑 OAuth2 + JWT 实战](/05-security/oauth2) — 主流方案
3. [🏛️ 统一认证中心](/05-security/auth-center) — 完整实现

### ✅ 检验标准

- ✅ 理解 OAuth2 四种模式
- ✅ JWT 的生成与验证
- ✅ 搭建统一认证中心
- ✅ Gateway 集成 JWT 验证

---

## 🏗️ 阶段四：稳定性保障（1-2 周）

### 🎯 目标
掌握 Sentinel + Seata，保障系统稳定性。

### 📚 学习内容

1. [💼 综合实战项目](/06-practice/comprehensive) — Sentinel + Seata 完整集成
2. [⚠️ 常见坑与最佳实践](/06-practice/pitfalls) — 避坑指南

### ✅ 检验标准

- ✅ Sentinel 流控 / 熔断 / 降级
- ✅ Seata 分布式事务
- ✅ 完整电商微服务项目

---

## 🎯 阶段五：面试与进阶（持续）

### 🎯 目标
掌握高频面试题，准备面试。

### 📚 学习内容

1. [🎯 高频面试题](/06-practice/interview) — 50+ 面试题详解
2. [💼 综合实战项目](/06-practice/comprehensive) — 完整项目经验

---

## 📊 学习路径自测

| 阶段 | 预计耗时 | 关键里程碑 |
|---|---|---|
| 一、Spring Boot 基础 | 1-2 周 | 独立搭建 REST API |
| 二、微服务核心 | 2-3 周 | 搭建 3 服务集群 |
| 三、认证授权 | 2-3 周 | 统一认证中心 |
| 四、稳定性保障 | 1-2 周 | Sentinel + Seata 集成 |
| 五、面试进阶 | 持续 | 50+ 面试题 |

## 🎓 推荐资源

- 📖 官方文档：[Spring Cloud Alibaba](https://spring.io/projects/spring-cloud-alibaba)
- 🎬 视频课程：尚硅谷 Spring Cloud 教程
- 📚 书籍：《Spring Cloud Alibaba 微服务原理与实战》
- 🔧 工具：Nacos、Sentinel、Seata 控制台


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
