---
title: 路由与断言
date: 2026-08-15  # date-auto-injected
---

# 🛣️ Gateway 路由与断言详解

> 路由（Route）是 Gateway 的核心，断言（Predicate）决定**请求是否匹配**这条路由。

## 🎯 断言工厂（Predicate Factory）

Spring Cloud Gateway 内置 **12+ 断言工厂**，每个对应一个配置项：

| 断言 | 配置 | 说明 |
|---|---|---|
| Path | `- Path=/api/**` | 路径匹配（Ant 风格） |
| Method | `- Method=GET,POST` | HTTP 方法 |
| Host | `- Host=**.example.com` | 域名 |
| Header | `- Header=X-Tag, \d+` | Header + 正则 |
| Cookie | `- Cookie=session, [a-z]+` | Cookie |
| Query | `- Query=foo, bar.` | URL 参数 |
| Host | `- Host=**.foo.com` | 子域名 |
| RemoteAddr | `- RemoteAddr=192.168.0.1/24` | 客户端 IP |
| Weight | `- Weight=group1, 80` | 权重路由 |
| Between | 时间范围 | 时间段 |
| Before / After | 时间点 | 时间点 |
| Method | HTTP 方法 | 方法 |
| Cookie | Cookie 值 | Cookie |
| XForwardedRemoteAddr | 代理头 | 代理后真实 IP |

## 📍 实战：Path 断言（最常用）

```yaml
routes:
  # 1. 精确路径
  - id: exact_route
    uri: lb://user-service
    predicates:
      - Path=/api/user/info         # 精确匹配
  
  # 2. Ant 风格通配符
  - id: ant_route
    uri: lb://user-service
    predicates:
      - Path=/api/user/**           # /** 匹配多级路径
  
  # 3. 单级通配符
  - id: single_route
    uri: lb://user-service
    predicates:
      - Path=/api/*/list            # /* 匹配单级路径
  
  # 4. 路径变量
  - id: var_route
    uri: lb://user-service
    predicates:
      - Path=/api/{segment}         # {segment} 捕获变量
```

## 🔀 多路由组合

### 顺序匹配

```yaml
spring:
  cloud:
    gateway:
      routes:
        # 路由 1：先匹配（更具体的）
        - id: specific_route
          uri: lb://special-service
          predicates:
            - Path=/api/special/**
        
        # 路由 2：兜底
        - id: default_route
          uri: lb://common-service
          predicates:
            - Path=/api/**
```

### 权重路由（灰度发布）

```yaml
spring:
  cloud:
    gateway:
      routes:
        # 90% 流量到 v1
        - id: v1_route
          uri: lb://order-service-v1
          predicates:
            - Path=/api/order/**
            - Weight=group1, 90
        
        # 10% 流量到 v2（灰度）
        - id: v2_route
          uri: lb://order-service-v2
          predicates:
            - Path=/api/order/**
            - Weight=group1, 10
```

## 🎯 Method 断言

```yaml
routes:
  - id: order_get
    uri: lb://order-service
    predicates:
      - Path=/api/order/**
      - Method=GET
  
  - id: order_modify
    uri: lb://order-service
    predicates:
      - Path=/api/order/**
      - Method=POST,PUT,DELETE
```

## 🌐 Host 断言

```yaml
routes:
  # 域名匹配
  - id: api_route
    uri: lb://api-service
    predicates:
      - Host=api.example.com
  
  # 子域名通配
  - id: subdomain_route
    uri: lb://user-service
    predicates:
      - Host=**.user.example.com
```

## 🔐 Header / Cookie 断言

```yaml
routes:
  # Header 包含特定值
  - id: internal_route
    uri: lb://internal-service
    predicates:
      - Path=/api/**
      - Header=X-Internal-Token, \w+   # 必须带 token
  
  # 灰度：特定 Header 才走新版本
  - id: beta_route
    uri: lb://beta-service
    predicates:
      - Path=/api/**
      - Header=X-Beta-Tester, true
  
  # Cookie 鉴权
  - id: auth_route
    uri: lb://user-service
    predicates:
      - Path=/api/user/**
      - Cookie=sessionId, [a-zA-Z0-9]+
```

## 📊 Query 参数断言

```yaml
routes:
  # 必须带 token 参数
  - id: token_route
    uri: lb://user-service
    predicates:
      - Query=token, [a-zA-Z0-9]+
  
  # 版本号路由
  - id: v2_route
    uri: lb://service-v2
    predicates:
      - Query=version, 2\.
```

## ⏰ 时间断言

```yaml
routes:
  # 限时活动路由
  - id: campaign_route
    uri: lb://campaign-service
    predicates:
      - Between=2025-01-01T00:00:00+08:00,2025-12-31T23:59:59+08:00
  
  # 维护期路由（指向维护页）
  - id: maintenance_route
    uri: https://maintenance.example.com
    predicates:
      - After=2025-06-01T00:00:00+08:00
```

## 🌐 RemoteAddr 断言

```yaml
routes:
  # 内网 IP 直通
  - id: internal_route
    uri: lb://internal-service
    predicates:
      - RemoteAddr=192.168.0.0/16,10.0.0.0/8
  
  # 仅允许办公网 IP
  - id: office_route
    uri: lb://admin-service
    predicates:
      - RemoteAddr=203.0.113.0/24
```

## 🔧 编程式自定义断言

```java
@Component
public class CustomRoutePredicateFactory 
    extends AbstractRoutePredicateFactory<CustomRoutePredicateFactory.Config> {
    
    public CustomRoutePredicateFactory() {
        super(Config.class);
    }
    
    @Override
    public Predicate<ServerWebExchange> apply(Config config) {
        return exchange -> {
            String customHeader = exchange.getRequest()
                .getHeaders().getFirst(config.getHeaderName());
            return customHeader != null 
                && customHeader.startsWith(config.getPrefix());
        };
    }
    
    @Data
    public static class Config {
        private String headerName;
        private String prefix;
    }
}
```

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: custom_route
          uri: lb://service
          predicates:
            - name: Custom
              args:
                headerName: X-Custom-Token
                prefix: Bearer
```

## 🎯 实战：完整的路由策略

```yaml
spring:
  cloud:
    gateway:
      routes:
        # 1. 公开 API（无需鉴权）
        - id: public_api
          uri: lb://public-service
          predicates:
            - Path=/api/public/**
            - Method=GET
          filters:
            - StripPrefix=1
            - AddResponseHeader=Cache-Control, public, max-age=3600
        
        # 2. 内部 API（需鉴权）
        - id: internal_api
          uri: lb://internal-service
          predicates:
            - Path=/api/internal/**
            - Method=GET,POST
          filters:
            - StripPrefix=1
            - name: AuthFilter        # 自定义鉴权
        
        # 3. 管理后台（限内网）
        - id: admin_api
          uri: lb://admin-service
          predicates:
            - Path=/api/admin/**
            - RemoteAddr=192.168.0.0/16
            - Header=X-Admin-Token, \w+
          filters:
            - StripPrefix=1
        
        # 4. 灰度发布（按 Header）
        - id: beta_users
          uri: lb://service-v2
          predicates:
            - Path=/api/**
            - Header=X-Beta-Tester, true
          filters:
            - StripPrefix=1
        
        # 5. 维护期（特定时间）
        - id: maintenance
          uri: https://maintenance.example.com
          predicates:
            - After=2025-12-01T00:00:00+08:00
        
        # 6. 兜底路由
        - id: default_route
          uri: https://www.example.com
          predicates:
            - Path=/api/**
```

## 🎯 总结

**断言核心：**
- ✅ 12+ 内置断言工厂
- ✅ 组合断言（AND 关系）
- ✅ 路径变量（`{segment}`）
- ✅ 时间断言（`Between` / `After`）
- ✅ 编程式自定义断言

**最佳实践：**
- ✅ 路由顺序：具体路由在前，通用路由在后
- ✅ 限流：单路由配置（不全局）
- ✅ 鉴权：用 `GlobalFilter` 而非路由 Filter
- ✅ 灰度：用 `Header` + `Weight` 组合
- ✅ 维护期：临时改时间断言即可

**下一步：** [🔧 过滤器](/03-gateway/filter) — 自定义 Filter 与限流、鉴权实战