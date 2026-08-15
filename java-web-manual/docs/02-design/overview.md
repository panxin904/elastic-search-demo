---
title: 实现思路 总览
---

# 实现思路

Java Web 开发的实现思路涵盖**架构设计、设计模式、编程范式**三个层面。好的思路让代码可读、可扩展、可维护。

## 思路体系

| 维度 | 核心要点 |
|---|---|
| **架构模式** | 分层架构、MVC、领域驱动DDD、微服务 |
| **核心机制** | 依赖注入（IoC/DI）、AOP切面、RESTful设计 |
| **设计模式** | 责任链、策略、模板方法、工厂、代理 |

## 架构设计

### 经典三层架构

```
┌─────────────────────────────────────────┐
│              表现层 Controller           │
│  接收请求、参数校验、返回响应               │
├─────────────────────────────────────────┤
│              业务层 Service              │
│  核心业务逻辑、事务管理、组装调用            │
├─────────────────────────────────────────┤
│              持久层 DAO/Mapper           │
│  数据库操作、SQL执行、ORM映射              │
└─────────────────────────────────────────┘
```

### Spring 核心机制

| 机制 | 说明 |
|---|---|
| [依赖注入](/02-design/dependency-injection) | IoC 容器管理 Bean 创建与依赖，@Autowired 自动装配 |
| [AOP切面](/02-design/aop) | 在不修改业务代码的前提下，横向织入日志、事务、权限 |
| [MVC模式](/02-design/mvc-pattern) | DispatcherServlet 分发请求 → HandlerMapping → Controller → ViewResolver |

### API 设计规范

| 规范 | 说明 |
|---|---|
| [RESTful风格](/02-design/restful-api) | 资源导向：URL 用名词复数，HTTP 方法表达操作 |
| 统一响应体 | `{ code, message, data }` 结构，前端统一处理 |
| 错误码体系 | 业务错误码 + HTTP 状态码双重标识 |

## 设计模式应用

| 模式 | 典型场景 |
|---|---|
| [责任链模式](/02-design/chain-of-responsibility) | 过滤器链（Filter）、拦截器（Interceptor）、审批流 |
| [策略模式](/02-design/strategy-pattern) | 多种支付方式、多种通知渠道、多种计费规则 |
| [模板方法模式](/02-design/template-method) | 抽象 BaseService 定义流程骨架，子类实现具体逻辑 |
| [工厂模式](/02-design/factory-pattern) | BeanFactory、各种 XXXFactory 创建复杂对象 |
| [代理模式](/02-design/proxy-pattern) | Spring AOP 底层（JDK 动态代理 + CGLIB）、MyBatis Mapper 代理 |

## 架构演进

```
单体应用 → 分层架构 → SOA → 微服务 → 领域驱动DDD
   ↓           ↓        ↓       ↓          ↓
 简单业务    职责分离   服务化   独立部署    复杂领域建模
```

| 阶段 | 适用场景 | 关键挑战 |
|---|---|---|
| 单体 | 初创项目、小团队 | 代码耦合、扩展困难 |
| 分层 | 中型项目 | 层级边界模糊 |
| [微服务](/02-design/microservices) | 大型项目、多团队 | 服务治理、数据一致性 |
| [DDD](/02-design/ddd) | 复杂业务领域 | 学习成本、建模难度 |

## 本层在图谱中的位置

<KnowledgeGraph mode="full" :height="500" />
