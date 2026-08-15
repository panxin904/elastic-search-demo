---
title: Gateway 过滤器
---

# 🔧 Gateway 过滤器详解

> 过滤器（Filter）是 Gateway 的灵魂，可以**修改请求 / 响应 / 限流 / 鉴权 / 日志**。

## 🎯 两种过滤器

| 类型 | 范围 | 数量 | 顺序 |
|---|---|---|---|
| **GatewayFilter** | 局部（单路由） | 可多个 | 路由内顺序 |
| **GlobalFilter** | 全局（所有路由） | 可多个 | 全局 + 路由内 |

## 🚀 内置过滤器速查

```yaml
spring:
  cloud:
    gateway:
      default-filters:    # 全局（所有路由生效）
        - AddRequestHeader=X-Gateway, true
        - StripPrefix=0
      
      routes:
        - id: order_route
          uri: lb://order-service
          predicates:
            - Path=/api/order/**
          filters:        # 局部（只对该路由生效）
            - StripPrefix=1
            - AddRequestHeader=X-Order, true
```

### 常用内置 Filter

```yaml
filters:
  # 路径处理
  - StripPrefix=1                # 去掉 1 层路径
  - PrefixPath=/api              # 加前缀
  - SetPath=/new-path            # 重设路径
  - SetStatus=200                 # 强制响应码
  
  # Header 处理
  - AddRequestHeader=X-Source, gateway
  - AddResponseHeader=X-Powered, my-gateway
  - RemoveRequestHeader=Cookie
  - RemoveResponseHeader=Server
  
  # 重定向
  - RedirectTo=302, https://example.com/
  
  # 重写
  - RewritePath=/api/(?<segment>.*), /$\{segment}
  
  # 限流（需 Redis）
  - name: RequestRateLimiter
    args:
      redis-rate-limiter.replenishRate: 100
      redis-rate-limiter.burstCapacity: 200
      key-resolver: "#{@userKeyResolver}"
  
  # 重试
  - name: Retry
    args:
      retries: 3
      statuses: BAD_GATEWAY
      backoff:
        firstBackoff: 10ms
        maxBackoff: 100ms
  
  # 熔断
  - name: CircuitBreaker
    args:
      name: orderServiceCircuitBreaker
      fallbackUri: forward:/fallback
```

## 🔧 自定义 GatewayFilter

### 鉴权 Filter

```java
@Component
public class AuthGatewayFilter implements GatewayFilter {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // 1. 提取 Token
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null || !token.startsWith("Bearer ")) {
            return unauthorized(exchange, "缺少 Token");
        }
        
        // 2. 验证 Token（调用 Auth Center 或本地验证 JWT）
        try {
            Claims claims = JwtUtil.parse(token.substring(7));
            // 把 userId 放到请求头，传递给下游
            exchange.getRequest().mutate()
                .header("X-User-Id", claims.get("userId").toString())
                .build();
        } catch (Exception e) {
            return unauthorized(exchange, "Token 无效");
        }
        
        return chain.filter(exchange);
    }
    
    private Mono<Void> unauthorized(ServerWebExchange exchange, String msg) {
        exchange.getResponse().setStatusCode(HttpStatus.UNAUTHORIZED);
        return exchange.getResponse().writeWith(
            Mono.just(exchange.getResponse().bufferFactory().wrap(msg.getBytes()))
        );
    }
}
```

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: auth_route
          uri: lb://user-service
          predicates:
            - Path=/api/user/**
          filters:
            - name: AuthGatewayFilter  # ⚠️ Bean 名（首字母小写）
```

## 🌍 自定义 GlobalFilter

### 日志 GlobalFilter

```java
@Component
public class LoggingGlobalFilter implements GlobalFilter, Ordered {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        long start = System.currentTimeMillis();
        ServerHttpRequest request = exchange.getRequest();
        
        log.info("→ {} {} from {}", 
            request.getMethod(), 
            request.getPath(),
            request.getRemoteAddress());
        
        return chain.filter(exchange).then(Mono.fromRunnable(() -> {
            long cost = System.currentTimeMillis() - start;
            ServerHttpResponse response = exchange.getResponse();
            log.info("← {} ({}ms)", 
                response.getStatusCode(), cost);
        }));
    }
    
    @Override
    public int getOrder() {
        return -100;  // 数字越小越先执行
    }
}
```

### Trace ID GlobalFilter

```java
@Component
public class TraceIdGlobalFilter implements GlobalFilter, Ordered {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // 1. 从请求头获取，没有则生成
        String traceId = exchange.getRequest().getHeaders().getFirst("X-Trace-Id");
        if (traceId == null) {
            traceId = UUID.randomUUID().toString().replace("-", "");
        }
        
        // 2. 放入请求头（传递给下游）
        ServerHttpRequest newRequest = exchange.getRequest().mutate()
            .header("X-Trace-Id", traceId)
            .build();
        
        // 3. 放入响应头
        exchange.getResponse().beforeCommit(() -> {
            exchange.getResponse().getHeaders().add("X-Trace-Id", traceId);
            return Mono.empty();
        });
        
        return chain.filter(exchange.mutate().request(newRequest).build());
    }
    
    @Override
    public int getOrder() {
        return -200;  // 最先执行
    }
}
```

## 🚦 限流实战

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
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token != null) {
            return Mono.just(token);
        }
        return Mono.just(exchange.getRequest().getRemoteAddress().getAddress().toString());
    };
}
```

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: api_route
          uri: lb://order-service
          predicates:
            - Path=/api/**
          filters:
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100   # 每秒 100 个令牌
                redis-rate-limiter.burstCapacity: 200  # 桶容量
                key-resolver: "#{@userKeyResolver}"
```

## 🔐 鉴权实战（JWT）

```java
@Component
public class JwtAuthFilter implements GatewayFilter {
    
    @Autowired
    private RestTemplate restTemplate;
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // 1. 跳过不需要鉴权的路径
        String path = exchange.getRequest().getPath().value();
        if (path.startsWith("/api/auth/") || path.startsWith("/api/public/")) {
            return chain.filter(exchange);
        }
        
        // 2. 检查 Token
        String token = exchange.getRequest().getHeaders().getFirst("Authorization");
        if (token == null) {
            return unauthorized(exchange, "缺少 Token");
        }
        
        // 3. 验证 Token（调用 Auth Center）
        try {
            ResponseEntity<Map> resp = restTemplate.exchange(
                "http://auth-center/api/auth/verify?token=" + token,
                HttpMethod.GET,
                null,
                Map.class
            );
            if (resp.getStatusCode() != HttpStatus.OK) {
                return unauthorized(exchange, "Token 无效");
            }
            
            // 4. 把 userId 放到请求头
            String userId = (String) resp.getBody().get("userId");
            ServerHttpRequest newRequest = exchange.getRequest().mutate()
                .header("X-User-Id", userId)
                .build();
            return chain.filter(exchange.mutate().request(newRequest).build());
            
        } catch (Exception e) {
            return unauthorized(exchange, "Token 验证失败");
        }
    }
}
```

## 🎯 过滤器顺序控制

```java
@Component
public class FilterA implements GlobalFilter {
    @Override
    public int getOrder() { return -100; }  // 先执行
}

@Component
public class FilterB implements GlobalFilter {
    @Override
    public int getOrder() { return 0; }     // 后执行
}
```

**执行顺序：FilterA → FilterB → 路由 Filter → 下游服务**

## 🎯 实战：完整过滤器链

```java
// 1. TraceId GlobalFilter（最先）
@Component
class TraceIdGlobalFilter implements GlobalFilter, Ordered {
    public int getOrder() { return -1000; }
}

// 2. 日志 GlobalFilter
@Component
class LoggingGlobalFilter implements GlobalFilter, Ordered {
    public int getOrder() { return -100; }
}

// 3. 鉴权 GatewayFilter（路由级）
class AuthGatewayFilter implements GatewayFilter { ... }

// 4. 限流（路由级）

// 5. 响应处理 GlobalFilter（最后）
@Component
class ResponseGlobalFilter implements GlobalFilter, Ordered {
    public int getOrder() { return 1000; }
}
```

**执行顺序：**
```
1. TraceId（-1000）生成 traceId
2. 日志（-100）记录请求
3. 路由 Filter：限流 → 鉴权
4. 转发到下游
5. 响应（1000）添加 header
```

## 🎯 总结

**过滤器核心：**
- ✅ GatewayFilter（局部，按路由）
- ✅ GlobalFilter（全局，所有路由）
- ✅ Ordered 接口控制顺序
- ✅ 责任链模式（preHandle → invoke → postHandle）

**实战模式：**
- ✅ 鉴权：GlobalFilter（统一处理）
- ✅ 限流：RequestRateLimiter + Redis
- ✅ 日志：GlobalFilter（自动 traceId）
- ✅ 异常处理：统一返回 JSON

**最佳实践：**
- ✅ 单一职责（一个 Filter 做一件事）
- ✅ 顺序控制（用 @Order 或 Ordered）
- ✅ 异常处理（不要让 Filter 抛异常）
- ✅ 性能考虑（Filter 逻辑要快）

**下一步：** [⚖️ Spring Cloud LoadBalancer](/04-loadbalancer/basic) — 客户端负载均衡