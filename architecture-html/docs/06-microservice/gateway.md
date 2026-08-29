---
title: API 网关
date: 2026-08-15  # date-auto-injected
---
# API 网关（API Gateway）

## 1. 解决的问题

```
客户端 A → 服务 B（10 个实例）
客户端 C → 服务 D（需要鉴权）
客户端 E → B + D

没有网关：客户端硬编码服务地址
  - 改 IP = 改客户端 = 重发布所有客户端
  - 每个客户端都重复鉴权 / 限流 / 监控
  - 多种协议难统一（REST / gRPC / WebSocket）

API 网关：所有流量的统一入口
  - 服务发现 / 负载均衡
  - 鉴权 / 限流 / 熔断
  - 灰度发布 / 协议转换
  - 监控 / 日志聚合
```

## 2. 核心功能

| 功能 | 说明 |
|------|------|
| **路由** | URL / header / cookie → 服务 |
| **鉴权** | OAuth2 / JWT / API Key 校验 |
| **限流** | 令牌桶 / 漏桶 / 滑动窗口 |
| **熔断** | 服务异常时快速失败 |
| **协议转换** | HTTP → gRPC / WebSocket |
| **灰度** | 按 header / cookie 路由到不同版本 |
| **聚合** | 一次请求调多个服务，组合返回 |
| **缓存** | 边缘缓存静态响应 |
| **监控** | 全局 metrics / 日志 / 链路追踪 |

## 3. 主流网关

| 系统 | 特点 |
|------|------|
| **Kong** | 老牌，OpenResty（Lua），插件丰富 |
| **APISIX** | Apache 出品，国产，Apache APISIX |
| **Spring Cloud Gateway** | Spring 生态，与 Spring 集成好 |
| **Envoy Gateway** | CNCF，Istio 用它做数据面 |
| **Kong / APISIX** | 高性能（OpenResty 协程） |
| **Spring Cloud Gateway** | WebFlux 响应式 |

## 4. Spring Cloud Gateway 实战

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/api/users/**
          filters:
            - StripPrefix=2
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 10
                redis-rate-limiter.burstCapacity: 20
                key-resolver: "#{@userKeyResolver}"
        - id: order-service
          uri: lb://order-service
          predicates:
            - Path=/api/orders/**
            - Header=X-Version, v2     # 灰度
          filters:
            - StripPrefix=2
```

```java
@Configuration
public class GatewayConfig {
  @Bean
  public RouteLocator routes(RouteLocatorBuilder builder) {
    return builder.routes()
      .route("user", r -> r.path("/api/users/**")
        .filters(f -> f.stripPrefix(2).rateLimit(c -> c.setCapacity(100).setRate(10)))
        .uri("lb://user-service"))
      .build();
  }
}
```

## 5. Kong 实战

```bash
# 加 route
curl -X POST http://kong:8001/services   -d name=user-service   -d url=http://user-service:8080

curl -X POST http://kong:8001/routes   -d service.name=user-service   -d paths[]=/api/users

# 加 rate-limit 插件
curl -X POST http://kong:8001/services/user-service/plugins   -d name=rate-limiting   -d config.minute=100   -d config.policy=local
```

## 6. APISIX 实战（国产最常用）

```bash
# Route
curl -X PUT 'http://apisix:9180/apisix/admin/routes/1'   -H 'X-API-KEY: xxx'   -d '{
    "uri": "/api/users/*",
    "upstream": {"type":"service-discovery","service_name":"USER-SVC"},
    "plugins": {"rate-limit": {"rate":100}}
  }'
```

## 7. 网关 vs Service Mesh

| | API Gateway | Service Mesh |
|--|---------------|---------------|
| 层 | L7 (HTTP) | L7 (任何协议) |
| 部署 | 独立集群（边缘） | Sidecar（与每个服务同 Pod） |
| 协议转换 | ✅ | 部分 |
| 灰度 | 简单（按 header / weight） | 强大（按 header / cookie / body） |
| 适用 | 外部流量入口 | 服务间通信 |

**最佳实践**：API Gateway（外部流量）+ Service Mesh（服务间流量）。

## 8. 网关安全

```yaml
# OAuth2 流程
plugins:
  oauth2:
    grant_type: client_credentials
    introspection_endpoint: http://idp:8080/oauth2/introspect
    client_id: my-service
    client_secret: secret
```

## 9. 性能与可靠性

| 指标 | 阈值 |
|------|------|
| 延迟 p99 | < 50ms |
| QPS | 10K+ |
| 可用性 | 99.99% |
| 部署方式 | 多实例 + LB |

## 10. 实战选型

```
Spring Cloud 生态    →  Spring Cloud Gateway
K8s 内部南北流量     →  Nginx Ingress / APISIX
K8s 内部东西流量     →  Service Mesh（应用无侵入）
混合                →  API Gateway（外）+ Mesh（内）
```

## 🔗 下一步
- [服务发现](/06-microservice/discovery)
- [配置中心](/06-microservice/config)
- [Service Mesh](/12-microservice-patterns/service-mesh)
