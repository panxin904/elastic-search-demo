---
title: 速查表
date: 2026-08-29  # date-auto-injected
---

# 📋 Java Web 速查表

> 80+ 高频 Java Web 命令/代码速查，支持分类过滤和关键词搜索（Cmd+F 即可）。

## 🌐 Spring Boot 速查

| 场景 | 命令/代码 |
|------|----------|
| 启动应用 | `mvn spring-boot:run` 或 `java -jar app.jar` |
| 指定 profile | `--spring.profiles.active=prod` |
| 健康检查 | `curl http://localhost:8080/actuator/health` |
| 修改端口 | `server.port=9090` |
| 查看 Beans | `curl http://localhost:8080/actuator/beans` |
| 查看映射 | `curl http://localhost:8080/actuator/mappings` |
| 查看配置 | `curl http://localhost:8080/actuator/configprops` |

## 🗄️ 数据库操作

| 场景 | 命令/代码 |
|------|----------|
| MyBatis 插入 | `@Insert("INSERT INTO user(name) VALUES(#{name})")` |
| MyBatis 查询 | `@Select("SELECT * FROM user WHERE id = #{id}")` |
| JPA 分页 | `Pageable pageable = PageRequest.of(0, 10)` |
| 事务管理 | `@Transactional(rollbackFor = Exception.class)` |
| 连接池监控 | `HikariCP` + Druid Admin |

## 🔐 安全相关

| 场景 | 命令/代码 |
|------|----------|
| JWT 生成 | `Jwts.builder().setSubject("user")...` |
| 密码加密 | `BCryptPasswordEncoder().encode(password)` |
| CSRF 防护 | `http.csrf().disable()`（仅 API） |
| CORS 配置 | `@CrossOrigin(origins = "*")` |
| XSS 过滤 | `HtmlUtils.htmlEscape(input)` |
| SQL 注入 | 使用 `#{}` 而非 `${}` |

## 🚀 性能优化

| 场景 | 命令/代码 |
|------|----------|
| 缓存注解 | `@Cacheable("users")` |
| 异步执行 | `@Async` + `@EnableAsync` |
| 限流 | `@RateLimiter` 或 Sentinel |
| 批量操作 | `SqlSession.batch()` / `JDBC batchUpdate` |
| 索引命中 | `EXPLAIN SELECT * FROM user WHERE ...` |
| JVM 调优 | `-Xms4g -Xmx4g -XX:+UseG1GC` |

## 📡 接口与文档

| 场景 | 命令/代码 |
|------|----------|
| RESTful 注解 | `@GetMapping` / `@PostMapping` / `@PutMapping` / `@DeleteMapping` |
| 请求参数 | `@RequestParam` / `@PathVariable` / `@RequestBody` |
| Swagger | `springdoc-openapi-starter-webmvc-ui` |
| API 文档生成 | OpenAPI 3 + Swagger UI |
| 接口测试 | Postman / curl / IDEA HTTP Client |

## 🔍 监控与日志

| 场景 | 命令/代码 |
|------|----------|
| 日志级别 | `logging.level.root=INFO` |
| MDC 追踪 | `MDC.put("traceId", UUID.randomUUID().toString())` |
| Prometheus 指标 | `Micrometer + spring-boot-actuator` |
| 健康检查 | `/actuator/health` |
| 链路追踪 | `Sleuth + Zipkin` |


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
