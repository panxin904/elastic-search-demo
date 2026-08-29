---
title: 高频面试题
date: 2026-08-15  # date-auto-injected
---

# 🎯 Spring Cloud 高频面试题

> 整理 Spring Boot + Spring Cloud Alibaba 面试中**最高频**的 30 道题，含详细答案。

## 🚀 Spring Boot 篇

### 1. Spring Boot 的自动配置原理？

**答：**
```
@SpringBootApplication = @Configuration + @EnableAutoConfiguration + @ComponentScan

@EnableAutoConfiguration 启用自动配置：
1. @Import(AutoConfigurationImportSelector.class)
2. 读取 META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
3. 加载所有自动配置类
4. 每个配置类用 @Conditional 判断是否生效
5. 满足条件的加入 Spring 容器
```

### 2. Spring Boot Starter 的原理？

**答：**
- Starter 是一个**空 jar 包**，只包含 `pom.xml`（依赖管理）+ `META-INF/spring/.../AutoConfiguration.imports`（自动配置声明）
- 用户引入 starter → 自动加载所有依赖 → 自动配置类生效

### 3. @SpringBootApplication 三个注解的作用？

**答：**
- `@SpringBootConfiguration`：标记为 Spring Boot 配置类
- `@EnableAutoConfiguration`：**启用自动配置**
- `@ComponentScan`：扫描包内组件

### 4. Spring Boot 内嵌 Tomcat 原理？

**答：**
- spring-boot-starter-web 依赖 spring-boot-starter-tomcat
- SpringApplication.run() 时创建 Spring 容器 → 启动内嵌 Tomcat → 监听 8080
- 整个应用打包成 fat jar，直接 `java -jar` 启动

### 5. Spring Boot 怎么读取外部配置？

**答：**
```
加载顺序（优先级从高到低）：
1. 命令行参数（--server.port=8081）
2. SPRING_APPLICATION_JSON
3. application-{profile}.yml（如 application-prod.yml）
4. application.yml
5. @PropertySource 注解
6. 默认值
```

## ☁️ Spring Cloud 篇

### 6. Spring Cloud 的核心组件有哪些？

**答：**
- 服务发现：Nacos / Eureka / Consul
- 配置中心：Nacos / Config / Apollo
- 网关：Spring Cloud Gateway / Zuul
- 负载均衡：LoadBalancer / Ribbon
- 熔断降级：Sentinel / Hystrix
- 分布式事务：Seata
- 消息：Spring Cloud Stream / RocketMQ
- 调用：OpenFeign / Feign

### 7. Eureka 和 Nacos 的区别？

**答：**
| 维度 | Eureka | Nacos |
|---|---|---|
| 一致性 | AP | **AP/CP 可切换** |
| 健康检查 | 心跳 | **心跳 + HTTP/TCP** |
| 功能 | 仅服务发现 | **服务发现 + 配置中心** |
| 维护 | 停止维护 | **活跃** |
| 性能 | 一般 | **高** |

### 8. Ribbon 和 LoadBalancer 的区别？

**答：**
- Ribbon：Netflix，已停止维护
- LoadBalancer：Spring Cloud 官方替代
- 架构：Ribbon 阻塞，LoadBalancer **响应式（Reactor）**
- 性能：LoadBalancer **更好**
- 集成：LoadBalancer 与 Spring Cloud **无缝集成**

### 9. Spring Cloud Gateway 三大核心？

**答：**
- **Route（路由）**：包含 ID、URI、断言、过滤器
- **Predicate（断言）**：匹配条件（Path / Method / Header）
- **Filter（过滤器）**：修改请求 / 响应

执行流程：客户端请求 → Predicate 匹配 → Filter 链 → 目标服务

### 10. Gateway 和 Zuul 的区别？

**答：**
| 维度 | Zuul 1.x | Spring Cloud Gateway |
|---|---|---|
| 性能 | 阻塞 | **响应式** |
| 长连接 | 弱 | **强（WebSocket）** |
| 维护 | 停止 | **活跃** |
| 易用性 | 一般 | **好（注解配置）** |

## 🛡️ Nacos 篇

### 11. Nacos 的两个核心功能？

**答：**
- **服务发现**：服务注册 + 健康检查 + 服务列表拉取
- **配置中心**：配置存储 + 动态推送 + Namespace 隔离

### 12. Nacos 如何保证高可用？

**答：**
- 集群部署（至少 3 节点）
- 节点间数据同步（Raft 协议 CP 模式）
- Client 缓存 + 本地容错
- 集群 Nacos 域名访问

### 13. Nacos 配置变更如何实时生效？

**答：**
1. Nacos Server 接收配置变更
2. 通过长连接推送给 Client
3. Client 收到变更后，刷新 `@RefreshScope` 标注的 Bean
4. 业务代码下次访问时拿到新值

业务代码要：
```java
@RestController
@RefreshScope  // ⚠️ 必须加
public class DemoController {
    @Value("${myapp.timeout}")
    private int timeout;
}
```

## 🔐 认证授权篇

### 14. JWT 的三部分？

**答：**
```
JWT = Header.Payload.Signature

Header: 算法和 token 类型
  {"alg":"HS256","typ":"JWT"}

Payload: 数据（用户信息）
  {"sub":"1001","name":"张三","exp":1700000000}

Signature: 签名（防篡改）
  HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)
```

### 15. JWT vs Session 区别？

**答：**
| 维度 | Session | JWT |
|---|---|---|
| 存储 | 服务端 | 客户端 |
| 扩展 | 难（需共享 session） | 易（无状态） |
| 适用 | 传统 Web | 前后端分离 / 微服务 |
| 安全性 | 较好 | 依赖签名密钥 |
| 性能 | 查 session 存储 | 仅验证签名 |

### 16. OAuth2 四种模式？

**答：**
- **授权码模式**（最常用，第三方登录）
- **密码模式**（自有应用）
- **简化模式**（纯前端，不推荐）
- **客户端模式**（服务对服务）

### 17. Spring Security 过滤器链执行流程？

**答：**
```
请求 → SecurityFilterChain:
  1. SecurityContextPersistenceFilter
  2. CsrfFilter（API 项目禁用）
  3. LogoutFilter
  4. UsernamePasswordAuthenticationFilter（登录）
  5. JwtAuthFilter（自定义）
  6. AuthorizationFilter（权限检查）
  → Controller
```

### 18. @PreAuthorize 是怎么生效的？

**答：**
- `@EnableMethodSecurity` 启用方法级权限
- Spring AOP 拦截方法调用
- 在 MethodSecurityInterceptor 中调用 MethodSecurityExpressionHandler
- 解析 `@PreAuthorize` 表达式（如 `hasRole('ADMIN')`）
- 与当前用户权限对比，失败抛 AccessDeniedException

## 🛡️ Sentinel 篇

### 19. Sentinel 核心功能？

**答：**
- **流量控制**（Flow）：QPS / 并发线程数限流
- **熔断降级**（Circuit Breaker）：服务降级、熔断、恢复
- **系统保护**（System）：Load / CPU 使用率 / RT 保护
- **热点参数限流**（Hot Param）：针对特定参数限流

### 20. Sentinel 流控规则？

```yaml
# Nacos 配置
spring:
  cloud:
    sentinel:
      datasource:
        ds1:
          nacos:
            server-addr: 127.0.0.1:8848
            dataId: sentinel-flow-rules
            ruleType: flow
```

```json
[
  {
    "resource": "createOrder",
    "limitApp": "default",
    "grade": 1,
    "count": 100,
    "strategy": 0,
    "controlBehavior": 0
  }
]
```

**关键参数：**
- `grade`：阈值类型（0=QPS, 1=线程数）
- `count`：阈值
- `strategy`：流控模式（0=直接拒绝, 1=关联, 2=链路）
- `controlBehavior`：效果（0=快速失败, 1=Warm Up, 2=排队等待）

## 🔄 分布式事务篇

### 21. Seata AT 模式原理？

**答：**
```
AT（Automatic Transaction）模式：
1. 一阶段：业务 SQL 执行前后，解析前后镜像（before/after image）
2. 把 before image 写入 undo_log
3. 提交前向 TC（Transaction Coordinator）注册全局锁
4. 二阶段：
   - 提交：删除 undo_log
   - 回滚：根据 undo_log 自动生成反向 SQL 补偿
```

### 22. 2PC 和 Seata AT 的区别？

**答：**
- **2PC（数据库层）**：同步阻塞、性能差
- **Seata AT（应用层）**：异步、性能好、自动生成补偿 SQL

### 23. 分布式事务选型？

**答：**
- 简单场景：本地消息表
- RocketMQ 生态：事务消息
- 强一致：Seata AT 模式
- 金融场景：TCC
- 长事务：Saga

## 🏗️ 微服务篇

### 24. 微服务拆分的原则？

**答：**
- **单一职责**：一个服务只做一件事
- **业务边界**：按业务领域拆分（DDD 限界上下文）
- **高内聚低耦合**：服务内部紧耦合，服务间松耦合
- **数据自治**：每个服务有独立数据库
- **演进式拆分**：不要一上来就拆太细

### 25. 微服务怎么保证数据一致性？

**答：**
- **最终一致性**（推荐）：本地消息表、Saga、事件驱动
- **强一致性**：Seata AT / TCC（性能差）
- **避免跨服务事务**：通过数据冗余 + 最终一致性

### 26. CAP 理论？

**答：**
- **C**onsistency：一致性
- **A**vailability：可用性
- **P**artition tolerance：分区容错（必须）

微服务必须在 C 和 A 之间二选一：
- 选 C：强一致（如 Seata）
- 选 A：最终一致（大多数场景）

### 27. 服务降级和熔断的区别？

**答：**
- **服务降级**：服务不可用时，返回兜底数据（如空对象、缓存值）
- **服务熔断**：当服务失败率超过阈值时，**快速失败**（不调用），避免雪崩

Sentinel 同时支持：
```java
@SentinelResource(
    value = "getUser",
    fallback = "fallbackMethod",  // 降级
    blockHandler = "blockHandler"  // 熔断
)
```

## 🚀 性能与监控篇

### 28. 微服务性能瓶颈排查思路？

**答：**
```
1. Gateway：看 QPS / 限流触发数
2. 服务调用：Sleuth traceId 追踪慢调用
3. JVM：看 GC / 堆内存 / 线程数
4. DB：慢查询日志 + EXPLAIN
5. 缓存：命中率（Redis stats）
6. 消息：消费 lag
```

### 29. 分布式 ID 生成方案对比？

**答：**
| 方案 | 性能 | 唯一 | 趋势递增 | 复杂度 |
|---|---|---|---|---|
| UUID | 高 | ✅ | ❌ | 低 |
| 雪花算法 | **高** | ✅ | ✅ | 中 |
| Leaf 号段 | **极高** | ✅ | ✅ | 中 |
| Redis INCR | 中 | ✅ | ✅ | 低 |
| DB 自增 | 低 | ❌（分库分表） | ✅ | 低 |

### 30. 如何设计千万级 QPS 系统？

**答：**
1. **读写分离**：扩展读能力
2. **分库分表**：扩展写能力
3. **缓存**：Redis 多级缓存
4. **消息队列**：削峰填谷
5. **限流熔断**：保护系统
6. **CDN**：静态资源
7. **服务降级**：保证核心功能

## 🎯 总结

**面试准备建议：**
- ✅ 理解原理（不要只背 API）
- ✅ 结合项目经验（举实际例子）
- ✅ 关注源码（看关键类）
- ✅ 关注生产实践（性能、坑、监控）
- ✅ 准备 2-3 个深度问题

**30 道题覆盖：**
- Spring Boot：5 道
- Spring Cloud 核心：5 道
- Nacos：3 道
- 认证授权：5 道
- Sentinel：2 道
- 分布式事务：3 道
- 微服务架构：4 道
- 性能监控：3 道

**下一步：** 回到 [学习路径](/path) 继续学习，或访问 [首页](/) 查看所有内容。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):微服务架构
- [system-design](https://java-px.bot.cd/system-design/):系统设计
- [cloud-native](https://java-px.bot.cd/cloud-native/):Docker / K8s 落地
