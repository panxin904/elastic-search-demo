---
title: 常见坑与最佳实践
---

# ⚠️ Spring Cloud 常见坑与最佳实践

> 总结 Spring Boot + Spring Cloud Alibaba 开发中最常踩的 10 个坑，以及 12 条企业级最佳实践。

## 🚨 10 个常见坑

### 坑 1：Nacos 服务注册失败

```yaml
# ❌ 服务名不一致
# 提供方：spring.application.name=order-service
# 消费方：@FeignClient("Order-Service")  # ⚠️ 大小写不一致！
```

**解决：服务名严格统一，区分大小写敏感**

```yaml
# ✅ 统一用小写中划线
spring:
  application:
    name: order-service
```

### 坑 2：Feign 调用 404

```java
// ❌ @FeignClient 路径与 Controller 不一致
@FeignClient("user-service")
public interface UserClient {
    @GetMapping("/users/{id}")  // ⚠️ 没有 /api 前缀
    User getById(@PathVariable Long id);
}

// Controller
@RequestMapping("/api/users")  // ⚠️ 有 /api 前缀
public class UserController {
    @GetMapping("/{id}")
    public User getById(@PathVariable Long id) { ... }
}
```

**解决：路径完全一致，或用 StripPrefix 去掉**

### 坑 3：OpenFeign 超时默认 1 秒

```java
// ❌ 业务慢但 Feign 超时 1 秒
@FeignClient("product-service")
public interface ProductClient {
    @GetMapping("/api/products/{id}")
    Product getById(@PathVariable Long id);
}
```

**解决：显式配置超时**

```yaml
spring:
  cloud:
    openfeign:
      client:
        config:
          default:
            connect-timeout: 5000
            read-timeout: 30000
        # 启用 Feign 自带的 LoadBalancer
        loadbalancer:
          enabled: true
```

### 坑 4：Sentinel 流控不生效

```java
// ❌ 资源名写错（@SentinelResource 的 value 必须与方法名一致）
@SentinelResource(value = "getOrder", fallback = "fallback")
public Order getOrder(Long id) { ... }  // ⚠️ value 与方法名不一致
```

**解决：资源名要规范**

```java
// ✅ 资源名 = 方法名（推荐）
@SentinelResource(value = "OrderService:getOrder", fallback = "fallback")
```

### 坑 5：Seata 事务不生效

```java
// ❌ 跨服务调用没走 OpenFeign（直接用 RestTemplate / HttpClient）
@Transactional  // ⚠️ 本地事务，不是 Seata 全局事务
public boolean createOrder(OrderDTO dto) {
    orderMapper.insert(dto);
    // 直接 HTTP 调用（不走 Seata）
    restTemplate.postForObject("http://inventory/decrease", dto, Boolean.class);
    return true;
}
```

**解决：必须用 @GlobalTransactional + OpenFeign**

```java
// ✅ 用 @GlobalTransactional
@GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
public boolean createOrder(OrderDTO dto) {
    orderMapper.insert(dto);
    inventoryClient.decrease(dto);  // OpenFeign（Seata 拦截）
    accountClient.debit(dto);
    return true;
}
```

### 坑 6：JWT 密钥泄露

```java
// ❌ 硬编码密钥
signWith(SignatureAlgorithm.HS256, "my-secret-key-123")
```

**解决：从环境变量读取**

```java
@Value("${jwt.secret}")
private String secret;
```

```bash
# 启动时通过环境变量传入
JWT_SECRET="your-production-key-256-bits" java -jar app.jar
```

### 坑 7：Gateway 跨域配置不生效

```java
// ❌ 只在 Controller 上加 @CrossOrigin
@CrossOrigin(origins = "*")
@RestController
public class UserController { ... }
```

**解决：在 Gateway 统一配置 CORS**

```yaml
spring:
  cloud:
    gateway:
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOriginPatterns: "*"
            allowedMethods: "*"
```

### 坑 8：微服务雪崩

```
场景：用户服务慢 → 调用用户服务的订单服务也慢 → 前端请求堆积 → 全服务雪崩
```

**解决：Sentinel 熔断 + 降级**

```java
@SentinelResource(
    value = "getUser",
    fallback = "getUserFallback",
    blockHandler = "getUserBlock"
)
public User getUser(Long id) {
    return userClient.getById(id);
}

public User getUserFallback(Long id) {
    return User.empty();  // 降级返回空对象
}
```

### 坑 9：分布式 ID 冲突

```java
// ❌ MySQL 自增主键（分库分表后会冲突）
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;
```

**解决：用雪花算法**

```java
// ✅ 雪花 ID（全局唯一）
@TableId(type = IdType.ASSIGN_ID)
private Long id;
```

### 坑 10：Nacos 配置覆盖问题

```
场景：本地 application.yml 的配置没生效
```

```yaml
# Nacos 配置
server:
  port: 8080

# 本地 application.yml
server:
  port: 8081
# ⚠️ 哪个生效？
```

**加载顺序：**
```
Nacos 配置（order-service.yaml）
  + Nacos 共享配置（common.yaml）
  > 本地 application.yml
  > 本地 application-{profile}.yml
```

**解决：** 关键配置放 Nacos（统一管理），环境特定配置放本地

## 🏆 12 条最佳实践

### 1. 统一版本管理

```xml
<!-- 父 POM 统一管理 -->
<properties>
    <spring-boot.version>3.2.0</spring-boot.version>
    <spring-cloud.version>2023.0.1</spring-cloud.version>
    <spring-cloud-alibaba.version>2023.0.1.0</spring-cloud-alibaba.version>
</properties>
```

### 2. 服务命名规范

```
服务名：小写中划线
- order-service ✅
- OrderService ❌
- orderService ❌

包名：小写点分
- com.example.order ✅
- com.example.Order ❌

类名：大驼峰
- OrderService ✅
- orderService ❌
```

### 3. 配置外置

```yaml
# 不同环境用 namespace 隔离
spring:
  cloud:
    nacos:
      config:
        namespace: ${NACOS_NAMESPACE:dev}  # 环境变量指定
```

### 4. 统一异常返回

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(Exception.class)
    public Result<Void> handle(Exception e) {
        log.error("系统异常", e);
        return Result.error(500, "系统繁忙");
    }
}
```

### 5. 接口幂等性

```java
// 关键操作：创建订单、支付等必须幂等
@PostMapping("/create")
public Result<Order> createOrder(
    @RequestHeader("Idempotency-Key") String idempotencyKey,
    @RequestBody OrderDTO dto
) {
    // 1. 检查 Idempotency-Key 是否已使用
    if (redis.hasKey("idempotency:" + idempotencyKey)) {
        Order exist = (Order) redis.opsForValue().get("idempotency:" + idempotencyKey);
        return Result.success(exist);
    }
    
    // 2. 执行业务
    Order order = orderService.create(dto);
    
    // 3. 记录 Idempotency-Key
    redis.opsForValue().set("idempotency:" + idempotencyKey, order, Duration.ofHours(24));
    
    return Result.success(order);
}
```

### 6. 链路追踪

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-sleuth</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-sleuth-zipkin</artifactId>
</dependency>
```

```yaml
spring:
  zipkin:
    base-url: http://zipkin:9411
  sleuth:
    sampler:
      probability: 1.0  # 生产环境 0.1
```

### 7. 健康检查

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics
  endpoint:
    health:
      show-details: always
      probes:
        enabled: true
  health:
    db:
      enabled: true
    redis:
      enabled: true
    rabbit:
      enabled: true
```

```bash
curl http://localhost:8081/actuator/health
{"status":"UP","components":{"db":{"status":"UP"},"redis":{"status":"UP"}}}
```

### 8. 优雅停机

```yaml
server:
  shutdown: graceful

spring:
  lifecycle:
    timeout-per-shutdown-phase: 30s
```

```java
@Component
public class GracefulShutdown implements DisposableBean {
    
    @Autowired
    private RabbitMQTemplate rabbitTemplate;
    
    @Override
    public void destroy() throws Exception {
        // 停止接收新消息
        rabbitTemplate.stop();
    }
}
```

### 9. 限流保护

```java
// Gateway 限流
filters:
  - name: RequestRateLimiter
    args:
      redis-rate-limiter.replenishRate: 200
      redis-rate-limiter.burstCapacity: 400

// Sentinel 限流
@SentinelResource(value = "createOrder", blockHandler = "handleBlock")
public boolean createOrder(OrderDTO dto) { ... }
```

### 10. 监控告警

```yaml
management:
  endpoints:
    web:
      exposure:
        include: prometheus
```

```bash
# Prometheus 抓取
scrape_configs:
  - job_name: 'spring-cloud'
    static_configs:
      - targets: ['user-service:8081', 'order-service:8082']
```

```promql
# 告警规则
ALERT ServiceDown
  IF up{job="spring-cloud"} == 0
  FOR 1m
```

### 11. 日志规范

```yaml
logging:
  level:
    root: info
    com.example: debug
    org.springframework.cloud: warn
  pattern:
    console: '%d{yyyy-MM-dd HH:mm:ss.SSS} [%thread] [%X{traceId},%X{spanId}] %-5level %logger{36} - %msg%n'
```

### 12. 容器化部署

```dockerfile
# Dockerfile
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

```yaml
# docker-compose.yml
services:
  user-service:
    image: user-service:1.0.0
    environment:
      - NACOS_ADDR=nacos:8848
    depends_on: [nacos, mysql]
```

## 🎯 总结

**最常踩的 10 个坑：**
1. Nacos 服务名大小写不一致
2. Feign 路径不匹配
3. OpenFeign 默认超时 1 秒
4. Sentinel 资源名不规范
5. Seata 必须用 @GlobalTransactional + OpenFeign
6. JWT 密钥硬编码
7. Gateway 跨域配置错位置
8. 微服务雪崩无熔断
9. 分布式 ID 冲突
10. 配置覆盖顺序不清楚

**12 条最佳实践：**
- 统一版本管理
- 服务命名规范
- 配置外置（Nacos namespace）
- 统一异常返回
- 接口幂等性
- 链路追踪（Sleuth + Zipkin）
- 健康检查（Actuator）
- 优雅停机
- 限流保护（Gateway + Sentinel）
- 监控告警（Prometheus）
- 日志规范（含 traceId）
- 容器化部署（Docker）

**下一步：** [🎯 高频面试题](/06-practice/interview) — 面试必备