---
title: 思维导图
---

# 🧭 Spring Cloud 思维导图

> 按 **6 大主题** 分类的结构化导图，支持展开/收起，点击叶子节点跳转对应文档。

<MindMap :height="720" />

## 📚 主题地图

### 🍃 Spring Boot 基础

- [🚀 快速开始](/01-springboot/quickstart) - 第一个 Spring Boot 应用
- [⚙️ 自动配置原理](/01-springboot/auto-config) - @SpringBootApplication 背后的魔法
- [🌐 Web 开发](/01-springboot/web) - REST API、参数校验、统一异常
- [💾 数据访问](/01-springboot/data) - Spring Data JPA、MyBatis-Plus
- [🔄 事务管理](/01-springboot/transaction) - @Transactional 的传播机制

### ☁️ Spring Cloud Alibaba 核心

- [📚 Spring Cloud Alibaba 总览](/02-overview/intro) - 生态与版本对应
- [🌐 Nacos 服务发现](/02-overview/nacos-discovery) - 替代 Eureka
- [⚙️ Nacos 配置中心](/02-overview/nacos-config) - 动态配置 + Namespace

### 🚪 微服务网关

- [🌊 Gateway 基础](/03-gateway/basic) - 三大核心：路由 / 断言 / 过滤器
- [🛣️ 路由与断言](/03-gateway/route) - Path、Host、Method 各种断言
- [🔧 过滤器](/03-gateway/filter) - GlobalFilter 和 GatewayFilter

### ⚖️ 负载均衡

- [🔄 Spring Cloud LoadBalancer](/04-loadbalancer/basic) - 替代 Ribbon
- [🎯 负载均衡策略](/04-loadbalancer/strategy) - 轮询 / 随机 / 一致性 Hash

### 🔐 认证授权

- [🛡️ Spring Security 基础](/05-security/basic) - 认证与授权
- [🔑 OAuth2 + JWT 实战](/05-security/oauth2) - 主流方案
- [🏛️ 统一认证中心](/05-security/auth-center) - Auth Center 完整实现

### 🛠️ 实战与面试

- [💼 综合实战项目](/06-practice/comprehensive) - 电商微服务全流程
- [⚠️ 常见坑与最佳实践](/06-practice/pitfalls) - 避坑指南
- [🎯 高频面试题](/06-practice/interview) - Spring Cloud 面试必备