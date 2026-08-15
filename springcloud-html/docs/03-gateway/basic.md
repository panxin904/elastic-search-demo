---
title: Gateway 基础
---

# 🌊 Spring Cloud Gateway 基础

> Spring Cloud Gateway 是 Spring Cloud 官方推出的**第二代网关**，基于 Spring 5 + WebFlux + Reactor，**性能是 Zuul 的 1.6 倍**。

## 🎯 为什么用 Gateway？

| 维度 | Zuul 1.x | Spring Cloud Gateway |
|---|---|---|
| 性能 | 阻塞 | **响应式（非阻塞）** |
| 长连接支持 | 弱 | **WebSocket 长连接** |
| 限流 | 需集成 Hystrix | **内置 RequestRateLimiter** |
| 动态路由 | 弱 | **支持（Nacos 集成）** |
| 协议 | HTTP | **HTTP + WebSocket + gRPC** |

## 🏗️ 三大核心概念

```
Route（路由）：
- 路由 ID
- 目标 URI
- 断言（Predicate）
- 过滤器（Filter）

Predicate（断言）：
- 匹配请求条件（Path / Method / Header / 时间）
- 匹配上才路由

Filter（过滤器）：
- 修改请求 / 响应
- 添加 / 删除 Header
- 限流 / 鉴权
```

## 🚀 快速开始

### 1. 添加依赖

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-gateway</artifactId>
</dependency>

<!-- Nacos 服务发现 -->
<dependency>
    <groupId>com.alibaba.cloud</groupId>
    <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
</dependency>
```

### 2. application.yml

```yaml
spring:
  application:
    name: gateway-service
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
    gateway:
      # 路由配置
      routes:
        - id: order_route
          uri: lb://order-service       # ⚠️ lb:// = 负载均衡
          predicates:
            - Path=/api/order/**
          filters:
            - StripPrefix=1              # 去掉 /api 前缀
```

### 3. 启动类

```java
@SpringBootApplication
@EnableDiscoveryClient
public class GatewayApplication { }
```

### 4. 第一个路由

```yaml
# 访问 http://gateway-host:8080/api/order/list
# ↓
# Predicate 匹配：/api/order/**
# ↓
# 转发到：http://order-service:8081/order/list
# （StripPrefix=1 去掉 /api 前缀）
```

## 🎯 断言（Predicate）

### Path 断言

```yaml
predicates:
  - Path=/api/order/**         # Ant 风格路径匹配
  - Path=/api/{segment}        # 路径变量
```

### Method 断言

```yaml
predicates:
  - Method=GET,POST             # 只匹配这些方法
```

### Host 断言

```yaml
predicates:
  - Host=**.example.com         # 域名匹配
```

### Header 断言

```yaml
predicates:
  - Header=X-Request-Id, \d+    # Header 值匹配正则
```

### 时间断言

```yaml
predicates:
  - Between=2025-01-01T00:00:00+08:00,2025-12-31T23:59:59+08:00
```

### Cookie 断言

```yaml
predicates:
  - Cookie=sessionId, [a-zA-Z0-9]+
```

### Query 参数断言

```yaml
predicates:
  - Query=foo, bar.            # 参数名 foo，值匹配 bar.
```

### 组合断言（AND 关系）

```yaml
predicates:
  - Path=/api/order/**
  - Method=GET
# 路径匹配 AND 方法是 GET
```

## 🔧 过滤器（Filter）

### 内置过滤器

```yaml
filters:
  # 1. 添加请求头
  - AddRequestHeader=X-Request-Source, gateway
  
  # 2. 添加响应头
  - AddResponseHeader=X-Powered-By, Spring Cloud Gateway
  
  # 3. 去前缀
  - StripPrefix=1            # 去掉 1 层路径
  
  # 4. 加前缀
  - PrefixPath=/api
  
  # 5. 设置路径
  - SetPath=/new-path
  
  # 6. 限流（需 Redis）
  - name: RequestRateLimiter
    args:
      redis-rate-limiter.replenishRate: 100
      redis-rate-limiter.burstCapacity: 200
      key-resolver: "#{@userKeyResolver}"
  
  # 7. 重试
  - name: Retry
    args:
      retries: 3
      statuses: BAD_GATEWAY
```

### 全局过滤器

```yaml
spring:
  cloud:
    gateway:
      default-filters:
        - AddRequestHeader=X-Gateway, true
        - StripPrefix=0
```

## 🔧 自定义过滤器

### GatewayFilter（局部）

```java
@Component
public class AuthGatewayFilter implements GatewayFilter {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
            return exchange.getResponse().setComplete();
        }
        return chain.filter(exchange);
    }
}
```

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: order_route
          uri: lb://order-service
          predicates:
            - Path=/api/order/**
          filters:
            - name: AuthGatewayFilter  # ⚠️ Bean 名称（首字母小写）
```

### GlobalFilter（全局）

```java
@Component
public class LoggingGlobalFilter implements GlobalFilter, Ordered {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        long start = System.currentTimeMillis();
        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            long cost = System.currentTimeMillis() - start;
            log.info("Request: {} {}, cost: {}ms",
                exchange.getRequest().getMethod(),
                exchange.getRequest().getPath(),
                cost);
        }));
    }
    
    @Override
    public int getOrder() {
        return -100;  // 数字越小越先执行
    }
}
```

## 🌐 CORS 跨域

```yaml
spring:
  cloud:
    gateway:
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOriginPatterns: "*"
            allowedMethods: "*"
            allowedHeaders: "*"
            allowCredentials: true
            maxAge: 3600
```

## 📊 限流

### Redis 令牌桶

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis-reactive</artifactId>
</dependency>
```

```java
@Bean
public KeyResolver userKeyResolver() {
    return exchange -> {
        // 从 token 中获取 userId 作为限流 key
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        return Mono.just(token != null ? token : exchange.getRequest().getRemoteAddress().getAddress().toString());
    };
}
```

```yaml
filters:
  - name: RequestRateLimiter
    args:
      redis-rate-limiter.replenishRate: 100     # 每秒 100 个令牌
      redis-rate-limiter.burstCapacity: 200    # 桶容量 200
      key-resolver: "#{@userKeyResolver}"
```

## 🎯 实战：完整路由配置

```yaml
spring:
  cloud:
    gateway:
      # 全局 CORS
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOriginPatterns: "*"
            allowedMethods: "*"
      
      # 路由
      routes:
        # 1. 订单服务
        - id: order_route
          uri: lb://order-service
          predicates:
            - Path=/api/order/**
            - Method=GET,POST,PUT,DELETE
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 200
                redis-rate-limiter.burstCapacity: 400
                key-resolver: "#{@userKeyResolver}"
        
        # 2. 用户服务
        - id: user_route
          uri: lb://user-service
          predicates:
            - Path=/api/user/**
          filters:
            - StripPrefix=1
            - AddRequestHeader=X-Gateway, true
        
        # 3. 商品服务
        - id: product_route
          uri: lb://product-service
          predicates:
            - Path=/api/product/**
          filters:
            - StripPrefix=1
      
      # 默认路由（404 兜底）
      - id: default_route
        uri: https://example.com
        predicates:
          - Path=/api/**
      
      # 全局过滤器
      default-filters:
        - AddResponseHeader=X-Powered-By, My-Gateway
```

## 🎯 总结

**Gateway 核心：**
- ✅ 三大概念：Route / Predicate / Filter
- ✅ 断言匹配请求（Path / Method / Host / Header）
- ✅ 过滤器修改请求 / 响应
- ✅ 内置限流、熔断、CORS

**实战模式：**
- ✅ 简单路由：Path + StripPrefix
- ✅ 动态路由：集成 Nacos（自动发现服务）
- ✅ 鉴权：自定义 GlobalFilter
- ✅ 限流：RequestRateLimiter + Redis

**性能优势：**
- ✅ 基于 WebFlux（响应式）
- ✅ 比 Zuul 快 1.6 倍
- ✅ 支持长连接

**下一步：** [🛣️ 路由与断言](/03-gateway/route) — 深入各种 Predicate 用法