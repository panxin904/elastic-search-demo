---
layout: home
title: Java Web Dev Manual
hero:
  name: "Java Web Dev Manual"
  text: "用知识图谱系统化掌握 Java Web 开发全流程"
  tagline: "开发流程 · 实现思路 · 重点关注 · 技术栈 · 48 个核心节点"
  actions:
    - theme: brand
      text: 开始学习
      link: /01-process/overview
    - theme: alt
      text: 查看完整图谱
      link: "#complete-graph"
    - theme: alt
      text: 需求入手指南
      link: /01-process/requirement-analysis

features:
  - title: 开发流程
    details: 从拿到需求到部署上线的 13 个关键环节：需求分析 → 技术方案 → 数据库设计 → 接口设计 → 编码开发 → 代码评审 → 测试 → 部署 → 监控 → 迭代优化
    link: /01-process/overview
    linkText: 查看开发流程 →
  - title: 实现思路
    details: 分层架构、MVC模式、依赖注入、AOP切面、RESTful风格、DDD领域驱动、微服务架构，以及责任链/策略/模板方法/工厂/代理等核心设计模式
    link: /02-design/overview
    linkText: 查看实现思路 →
  - title: 重点关注
    details: 异常处理、日志规范、参数校验、事务管理、缓存策略、安全实践、性能优化、代码规范、接口幂等、数据脱敏、限流熔断、并发控制等 12 项开发红线
    link: /03-practice/overview
    linkText: 查看重点关注 →
  - title: 技术栈
    details: Spring Boot / Spring MVC / Spring Security / MyBatis / MySQL / Redis / 消息队列 / Maven / Docker / Nginx / JUnit / Swagger 等技术组件详解
    link: /04-tech/overview
    linkText: 查看技术栈 →
---


<ClientOnly>
  <WhyThisGraph
    :pain-points="[
      "Java 知识图谱太广（基础 / JVM / 并发 / 框架 / 中间件）怎么系统学？",
      "JVM 内存模型（堆 / 栈 / Metaspace / 直接内存）？",
      "并发编程（synchronized / Lock / JUC / 线程池）？",
      "Spring / Spring Boot / MyBatis 源码怎么读？",
      "分布式场景（RPC / 消息 / 缓存 / 数据库）实战？"
    ]"
    :goals="[
      "Java 基础（语法 / 集合 / 泛型 / 反射 / 注解）",
      "JVM 原理（内存模型 / GC / 类加载 / 字节码）",
      "并发编程（JUC / 线程池 / CompletableFuture）",
      "Spring 全家桶（IoC / AOP / Transaction / Boot）",
      "中间件实战（MySQL / Redis / Kafka / ES）",
      "分布式（RPC / 消息 / 缓存 / 配置中心）"
    ]"
    :related-sites="[
      { site: "java-language", path: "/04-jvm/overview", label: "JVM 原理" },
      { site: "system-design", path: "/01-theory/cap-theorem", label: "CAP 定理" },
      { site: "kafka", path: "/01-basics/architecture", label: "Kafka 架构" },
      { site: "mysql", path: "/01-basics/intro", label: "MySQL 基础" },
      { site: "redis", path: "/01-basics/intro", label: "Redis 基础" }
    ]"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>

## 完整知识图谱 {#complete-graph}

> 鼠标拖拽节点、滚轮缩放、**点击节点跳转到对应文档**。点击顶部图例可切换层级显隐。

<KnowledgeGraph mode="full" :height="700" />

## 站点统计

<div class="kg-stats">
  <div class="kg-stat">
    <div class="kg-stat-num">48</div>
    <div class="kg-stat-label">核心概念节点</div>
  </div>
  <div class="kg-stat">
    <div class="kg-stat-num">60+</div>
    <div class="kg-stat-label">关系边</div>
  </div>
  <div class="kg-stat">
    <div class="kg-stat-num">4</div>
    <div class="kg-stat-label">知识维度</div>
  </div>
  <div class="kg-stat">
    <div class="kg-stat-num">50+</div>
    <div class="kg-stat-label">深度文档</div>
  </div>
</div>

## 学习路径建议

### 新手入门（1-2天）— 拿到需求怎么办？

1. [需求分析](/01-process/requirement-analysis) → 拿到需求怎么拆解、确认边界
2. [技术方案](/01-process/tech-solution) → 技术选型与架构设计思路
3. [数据库设计](/01-process/database-design) → 建表、索引、ER图
4. [接口设计](/01-process/api-design) → RESTful API设计与文档
5. [分层架构](/02-design/layered-architecture) → Controller-Service-Dao 三层职责

### 进阶掌握（3-5天）— 如何写出高质量的代码？

- **开发流程**：[编码开发](/01-process/coding) → [代码评审](/01-process/code-review) → [单元测试](/01-process/unit-test)
- **实现思路**：[MVC模式](/02-design/mvc-pattern) → [依赖注入](/02-design/dependency-injection) → [AOP切面](/02-design/aop)
- **重点关注**：[异常处理](/03-practice/exception-handling) → [日志规范](/03-practice/logging) → [参数校验](/03-practice/validation) → [事务管理](/03-practice/transaction)
- **技术栈**：[Spring Boot](/04-tech/spring-boot) → [Spring MVC](/04-tech/spring-mvc) → [MyBatis](/04-tech/mybatis) → [MySQL](/04-tech/mysql)

### 高级深化（1-2周）— 企业级项目实战

- [缓存策略](/03-practice/cache-strategy) + [Redis](/04-tech/redis)：多级缓存、缓存穿透/击穿/雪崩
- [安全实践](/03-practice/security) + [Spring Security](/04-tech/spring-security)：认证授权、JWT/OAuth2
- [性能优化](/03-practice/performance) + [并发控制](/03-practice/concurrency)：SQL调优、连接池、锁机制
- [微服务架构](/02-design/microservices) + [消息队列](/04-tech/message-queue)：服务拆分、异步解耦
- [接口幂等](/03-practice/idempotency) + [限流熔断](/03-practice/rate-limiting)：高并发稳定性保障
- [领域驱动DDD](/02-design/ddd)：复杂业务的建模与划分

## 推荐资源

- [Spring Boot 官方文档](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)
- [MyBatis-Plus 官方文档](https://baomidou.com/)
- [Spring Security 参考](https://docs.spring.io/spring-security/reference/)
- [阿里 Java 开发手册](https://github.com/alibaba/p3c)
- [Design Patterns in Java](https://refactoring.guru/design-patterns/java)
