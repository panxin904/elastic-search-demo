---
title: 综合实战项目
---

# 💼 综合实战项目：电商微服务

> 整合 Spring Cloud Alibaba 全部组件，搭建一个**完整的电商微服务系统**。

## 🎯 项目目标

构建一个包含以下微服务的电商系统：

```
- gateway-service      (统一网关 + JWT 验证)
- auth-center          (统一认证)
- user-service         (用户管理)
- product-service      (商品管理)
- order-service        (订单管理)
- inventory-service    (库存管理)
- payment-service      (支付)
- notification-service (通知)
```

## 🏗️ 整体架构

```
┌─────────────────────────────────────────────┐
│                  Client (Web/App)              │
└─────────────────────┬───────────────────────┘
                      │
              ┌───────▼────────┐
              │  gateway-service │ ← Nacos 发现 + JWT 验证 + 限流
              │  port: 8080      │
              └───────┬────────┘
                      │
   ┌──────┬───────┬───┴────┬───────┬──────┐
   ▼      ▼       ▼        ▼       ▼      ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐
│ auth ││ user ││product││order ││invent││pay- │
│center││      ││      ││      ││ory   ││ment │
│9000  ││8081  ││8082  ││8083  ││8084  ││8085  │
└──────┘└──────┘└──────┘└──────┘└──────┘└──────┘
   │      │       │        │       │      │
   └──────┴───────┴────────┴───────┴──────┘
                      │
              ┌───────▼────────┐
              │     Nacos       │ ← 服务发现 + 配置中心
              │   127.0.0.1:8848│
              └────────────────┘
                      │
              ┌───────▼────────┐
              │    Sentinel    │ ← 流控 / 熔断
              │   Dashboard    │
              └────────────────┘
                      │
              ┌───────▼────────┐
              │     Seata      │ ← 分布式事务
              │     Server      │
              └────────────────┘
```

## 🚀 核心流程

### 1. 用户下单完整流程

```java
// 1. 前端：用户点击「提交订单」
POST /api/order/create
Authorization: Bearer <jwt>

// 2. Gateway
// - 验证 JWT
// - 限流检查（Sentinel）
// - 提取 userId，放到 header
// - 路由到 order-service

// 3. order-service（核心事务）
@GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
public Order createOrder(OrderDTO dto) {
    // 3.1 创建订单（写本服务 order_db）
    orderMapper.insert(dto);
    
    // 3.2 远程调用 inventory-service（Feign）
    inventoryClient.tryDecrease(dto);
    
    // 3.3 远程调用 account-service（Feign）
    accountClient.tryDebit(dto);
    
    // 3.4 发布订单创建事件
    kafkaTemplate.send("order.created", JSON.toJSONString(dto));
    
    return order;
}

// 4. inventory-service（监听事件）
@KafkaListener(topics = "order.created")
@Transactional
public void onOrderCreated(String message) {
    OrderDTO dto = JSON.parseObject(message, OrderDTO.class);
    inventoryMapper.decreaseAtomic(dto.getProductId(), dto.getQuantity());
    
    // 发布「库存已扣减」事件
    kafkaTemplate.send("inventory.decreased", message);
}

// 5. account-service（监听事件）
@KafkaListener(topics = "inventory.decreased")
public void onInventoryDecreased(String message) {
    OrderDTO dto = JSON.parseObject(message, OrderDTO.class);
    accountMapper.debit(dto.getUserId(), dto.getAmount());
    
    // 发布「账户已扣款」事件
    kafkaTemplate.send("account.debited", message);
}

// 6. notification-service（监听订单创建）
@KafkaListener(topics = "order.created")
public void onOrderCreated(String message) {
    // 发送短信 / 邮件通知
    notificationService.sendOrderCreated(message);
}
```

### 2. 失败补偿（Saga）

```
订单创建 → 库存扣减 → 账户扣款
    ↓            ↓           ↓
   成功         成功        失败！
    ↓            ↓           ↓
  正常       正常        触发补偿
                            ↓
                  补偿库存（加回去）
                            ↓
                  补偿订单（标记取消）
                            ↓
                       返回用户
```

## 📁 项目目录结构

```
ecommerce-microservices/
├── pom.xml                    # 父 POM（统一管理版本）
├── gateway-service/           # 网关
│   ├── pom.xml
│   └── src/main/
│       ├── java/com/example/gateway/
│       │   ├── GatewayApplication.java
│       │   └── filter/
│       │       ├── AuthGlobalFilter.java
│       │       └── RateLimitGlobalFilter.java
│       └── resources/application.yml
├── auth-center/              # 认证中心
├── user-service/             # 用户服务
├── product-service/          # 商品服务
├── order-service/            # 订单服务
├── inventory-service/        # 库存服务
├── payment-service/          # 支付服务
├── notification-service/     # 通知服务
└── docker-compose.yml        # 一键启动所有服务
```

## 🔧 父 POM

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
</parent>

<properties>
    <spring-boot.version>3.2.0</spring-boot.version>
    <spring-cloud.version>2023.0.1</spring-cloud.version>
    <spring-cloud-alibaba.version>2023.0.1.0</spring-cloud-alibaba.version>
    <mybatis-plus.version>3.5.5</mybatis-plus.version>
</properties>

<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.cloud</groupId>
            <artifactId>spring-cloud-dependencies</artifactId>
            <version>${spring-cloud.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
        <dependency>
            <groupId>com.alibaba.cloud</groupId>
            <artifactId>spring-cloud-alibaba-dependencies</artifactId>
            <version>${spring-cloud-alibaba.version}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

## 🚀 Gateway 完整配置

```yaml
# gateway-service/src/main/resources/application.yml
server:
  port: 8080

spring:
  application:
    name: gateway-service
  cloud:
    nacos:
      discovery:
        server-addr: 127.0.0.1:8848
    gateway:
      # 全局 CORS
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOriginPatterns: "*"
            allowedMethods: "*"
            allowedHeaders: "*"
            allowCredentials: true
      
      # 路由
      routes:
        - id: user_route
          uri: lb://user-service
          predicates:
            - Path=/api/user/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 200
                redis-rate-limiter.burstCapacity: 400
        
        - id: product_route
          uri: lb://product-service
          predicates:
            - Path=/api/product/**
          filters:
            - StripPrefix=1
        
        - id: order_route
          uri: lb://order-service
          predicates:
            - Path=/api/order/**
          filters:
            - StripPrefix=1
            - name: RequestRateLimiter
              args:
                redis-rate-limiter.replenishRate: 100
                redis-rate-limiter.burstCapacity: 200
        
        - id: inventory_route
          uri: lb://inventory-service
          predicates:
            - Path=/api/inventory/**
          filters:
            - StripPrefix=1
      
        - id: auth_route
          uri: lb://auth-center
          predicates:
            - Path=/api/auth/**
          filters:
            - StripPrefix=1
```

## 🐳 Docker Compose 一键启动

```yaml
# docker-compose.yml
version: '3.8'
services:
  nacos:
    image: nacos/nacos-server:v2.3.2
    container_name: nacos
    ports:
      - "8848:8848"
    environment:
      - MODE=standalone
  
  sentinel:
    image: bladex/sentinel-dashboard:1.8.5
    container_name: sentinel
    ports:
      - "8080:8080"
  
  seata:
    image: seataio/seata-server:1.7.0
    container_name: seata
    ports:
      - "8091:8091"
  
  redis:
    image: redis:7.2-alpine
    container_name: redis
    ports:
      - "6379:6379"
  
  mysql:
    image: mysql:8.0
    container_name: mysql
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: xxx
    volumes:
      - ./db:/docker-entrypoint-initdb.d
  
  gateway-service:
    build: ./gateway-service
    ports:
      - "8080:8080"
    depends_on: [nacos, redis]
  
  user-service:
    build: ./user-service
    ports:
      - "8081:8081"
    depends_on: [nacos, mysql]
  
  # ... 其他服务
```

## 📊 部署后的效果

```bash
$ docker-compose up -d
Creating network "ecommerce_default" with the default driver
Creating nacos ... done
Creating mysql ... done
Creating redis ... done
Creating gateway-service ... done
Creating user-service ... done
...

$ curl http://localhost:8848/nacos/
# 看到 8 个微服务都已注册

$ curl -X POST http://localhost:8080/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}'
{"code":200,"data":{"token":"eyJhbGciOiJIUzI1NiJ9..."}}

$ curl -X POST http://localhost:8080/api/order/create \
    -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9..." \
    -H "Content-Type: application/json" \
    -d '{"productId":1,"quantity":2,"amount":99.00}'
{"code":200,"data":{"orderId":10001,"status":"created"}}
```

## 🎯 关键设计决策

### 1. 同步 vs 异步

```
同步调用（Feign）：
- 业务强依赖（如扣库存、扣款）
- 必须等结果
- 用 @GlobalTransactional（Seata）

异步事件（Kafka）：
- 业务弱依赖（如通知、日志）
- 不需要立即处理
- 用 Saga 补偿
```

### 2. 服务发现 vs 配置

```
服务发现（Nacos）：
- 服务间互相调用
- 实例动态变化

配置（Nacos）：
- 统一配置管理
- 动态刷新
```

### 3. 容错设计

```
超时：避免无限等待
重试：临时错误可重试
熔断：避免雪崩
降级：返回兜底数据
```

## 🎯 总结

**实战项目核心：**
- ✅ 微服务拆分（按业务边界）
- ✅ Gateway 统一入口
- ✅ Nacos 服务发现 + 配置中心
- ✅ JWT 统一认证
- ✅ Seata 分布式事务
- ✅ Kafka 异步事件
- ✅ Sentinel 流控熔断
- ✅ Docker 一键部署

**下一步：** [⚠️ 常见坑与最佳实践](/06-practice/pitfalls) — 避坑指南


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):微服务架构
- [system-design](https://java-px.bot.cd/system-design/):系统设计
- [cloud-native](https://java-px.bot.cd/cloud-native/):Docker / K8s 落地
