---
title: Trace / Span 概念
description: 链路追踪核心数据模型
---

# Trace / Span 核心概念

> **TL;DR**：Trace 是**一次请求的完整故事**，Span 是**故事里的一段情节**。Span 通过 `trace_id` 串联，形成调用树。**理解这两个概念 = 理解 80% 的链路追踪**。

## 一句话定义

| 概念 | 含义 |
|---|---|
| **Trace** | 一次端到端请求在分布式系统中的完整调用路径 |
| **Span** | Trace 中的一个工作单元（一次 RPC、一次 DB 查询、一次 HTTP 调用） |
| **SpanContext** | Span 之间关联的上下文（trace_id、span_id、baggage） |

## 一个具体例子

```
用户下单（trace_id = abc123）
│
├── Span A: API Gateway 收到请求 [0-800ms]
│   │
│   ├── Span B: 验证用户身份 [10-50ms]
│   │   └── Span C: 查 DB 拿用户信息 [20-30ms]
│   │
│   ├── Span D: 创建订单 [100-700ms]
│   │   ├── Span E: 写订单表 [120-200ms]
│   │   ├── Span F: 扣库存 [250-450ms]
│   │   │   └── Span G: 调用库存服务 [300-440ms]
│   │   └── Span H: 发消息到 Kafka [600-650ms]
│   │
│   └── Span I: 返回响应 [780-800ms]
```

**可视化**：

```
0ms   100ms  200ms  300ms  400ms  500ms  600ms  700ms  800ms
├─────┼──────┼──────┼──────┼──────┼──────┼──────┼──────┤
│ A (api-gateway)            ←────────────────────────────→│
│   ├ B (auth)                                                │
│   │   └ C (mysql)                                            │
│   ├ D (create-order)                                         │
│   │   ├ E (mysql)                                            │
│   │   ├ F (inventory)        ←─────────────→                │
│   │   │   └ G (inventory-svc)                                │
│   │   └ H (kafka)                                            │
│   └ I (response)                                             │
```

## Span 数据结构

```protobuf
message Span {
  string trace_id = 1;        // 全局唯一，16 字节
  string span_id = 2;         // 8 字节
  string parent_span_id = 3;  // 父 span，没有则为 0
  string name = 4;            // 操作名，如 "GET /api/orders"
  uint64 start_time_ns = 5;   // 纳秒精度
  uint64 duration_ns = 6;     // 纳秒精度
  SpanKind kind = 7;          // SERVER / CLIENT / PRODUCER / CONSUMER / INTERNAL
  Status status = 8;          // OK / ERROR / UNSET
  repeated KeyValue attributes = 9;  // 属性
  repeated Event events = 10;        // 事件
  repeated Link links = 11;          // 跨 trace 链接
}

message SpanContext {
  string trace_id = 1;
  string span_id = 2;
  uint64 trace_flags = 3;   // 是否采样等
  string trace_state = 4;   // W3C trace state
  repeated KeyValue baggage = 5;  // 跨服务携带的键值
}
```

## Span Kind（5 种角色）

| Kind | 含义 | 例子 |
|---|---|---|
| **SERVER** | 处理请求的服务器端 | HTTP Server、gRPC Server |
| **CLIENT** | 发起请求的客户端 | HTTP Client、gRPC Client |
| **PRODUCER** | 消息生产者 | Kafka Producer |
| **CONSUMER** | 消息消费者 | Kafka Consumer |
| **INTERNAL** | 内部操作，不跨网络 | 函数调用、内存操作 |

```java
// Java OpenTelemetry 示例
Span serverSpan = tracer.spanBuilder("POST /orders")
    .setSpanKind(SpanKind.SERVER)
    .startSpan();

Span clientSpan = tracer.spanBuilder("GET http://user-service/users/123")
    .setSpanKind(SpanKind.CLIENT)
    .startSpan();

Span internalSpan = tracer.spanBuilder("calculate-price")
    .setSpanKind(SpanKind.INTERNAL)
    .startSpan();
```

## Span 属性（Attributes）

键值对，描述 Span 的元信息。OTel 有标准化的语义约定：

```yaml
# HTTP 服务端 Span
http.request.method: "GET"
http.route: "/api/orders/{id}"
http.response.status_code: 200
url.path: "/api/orders/12345"
server.address: "order-service"

# 数据库客户端 Span
db.system: "postgresql"
db.statement: "SELECT * FROM orders WHERE id = $1"
db.name: "shop"
db.operation: "SELECT"

# RPC 客户端 Span
rpc.system: "grpc"
rpc.service: "UserService"
rpc.method: "GetUser"
peer.address: "user-service:8080"
```

> **属性是高基数（high-cardinality）数据的载体**。例如 user_id、order_id 这种每个请求都不同的值应该放属性，不要放标签（labels）。

## Span 事件（Events）

Span 生命周期内的离散事件：

```java
span.addEvent("cache_miss", Attributes.of(
    stringKey("cache.key"), "user:12345",
    stringKey("cache.system"), "redis"
));

span.addEvent("retry", Attributes.of(
    stringKey("retry.attempt"), 2,
    stringKey("retry.reason"), "timeout"
));

try {
    processOrder();
} catch (Exception e) {
    span.recordException(e);  // 记录异常，自动写 event + 改 status
    span.setStatus(StatusCode.ERROR);
}
```

## Trace Context Propagation（上下文传播）

**问题**：跨服务调用时，下游怎么知道这次请求属于哪个 trace？

**答案**：通过 HTTP 头传播 `traceparent` + `tracestate`。

### W3C Trace Context（标准）

```
# HTTP 头
traceparent: 00-{trace_id}-{span_id}-{flags}
tracestate: vendorname=xxx

# 例
traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
            │  │                                     │         │      │
            │  └─ trace_id (16字节)                   │         │      └─ flags (01 = 采样)
            │                                         │         └─ span_id (8字节)
            └─ version (00 = W3C v1)
```

### 传播流程

```
Gateway (span_id=A) 
  ↓ 注入 traceparent 到 header
  ↓  traceparent: 00-{trace_id}-A-01
User Service (parent_span_id=A, span_id=B)
  ↓ 提取 traceparent, 创建 child span
  ↓ 注入到下游
  ↓  traceparent: 00-{trace_id}-B-01
DB Client (parent_span_id=B, span_id=C)
```

> **W3C Trace Context** 已成为业界标准（OpenTelemetry、Jaeger、Tempo、Zipkin 都支持）。

### Baggage（行李）

跨服务携带的额外键值对（如 user_id、tenant_id）：

```java
// 在 user-service 中设置 baggage
Baggage.current().toBuilder()
    .put("user.id", "u_456")
    .put("tenant.id", "t_789")
    .build()
    .store();

// baggage 会通过 tracestate 头传播到下游服务
// 下游服务可以通过 Baggage.current() 获取
```

> **注意**：baggage 会被传递到所有下游，**不要放敏感数据**（如密码、token）。

## 采样（Sampling）

**问题**：100% 采样 = 每个请求都产生 span = 存储爆炸。怎么办？

**解决**：采样。

### 采样策略

#### 1. Head-based Sampling（头采样）

```
请求进入 → 立刻决定是否采样 → 是 → 记录完整 trace
                              → 否 → 丢弃
```

**优点**：决策早，简单
**缺点**：可能丢掉关键的错误请求

```yaml
# 10% 采样
otlp_config:
  sampler:
    trace_id_ratio_based:
      ratio: 0.1
```

#### 2. Tail-based Sampling（尾采样）

```
请求进入 → 记录所有 span → 请求结束时决策
                            → 错误 / 慢 / 重要 → 保留
                            → 普通请求 → 丢弃
```

**优点**：能保留错误和慢请求
**缺点**：决策晚，需要临时存储（OTel Collector 维护）

```yaml
# OTel Collector tail_sampling processor
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 500 }
      - name: probabilistic
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

#### 3. Adaptive Sampling（自适应）

基于当前负载动态调整采样率。

### 实战建议

```
低流量（< 1000 QPS）   → 100% 采样
中流量（1000-10000 QPS）→ 10%-50% + 错误 100%
高流量（> 10000 QPS）  → 1%-10% + 错误 100% + 重要接口 100%
```

## 跨 trace 链接（Links）

有时一个 trace 包含异步触发另一个 trace，需要关联：

```java
// Producer 端：创建 trace 时 link 到消费 trace
Span producerSpan = tracer.spanBuilder("send-kafka")
    .addLink(consumerSpanContext)  // link 到未来的消费 trace
    .startSpan();

// Consumer 端：link 回生产 trace
Span consumerSpan = tracer.spanBuilder("consume-kafka")
    .addLink(producerSpanContext)
    .startSpan();
```

## 实战：Java Spring Boot + OTel 自动埋点

```java
// 1. 加依赖
// pom.xml
<dependency>
    <groupId>io.opentelemetry.instrumentation</groupId>
    <artifactId>opentelemetry-spring-boot-starter</artifactId>
    <version>2.4.0</version>
</dependency>

// 2. application.yml 配置 OTLP 导出
otel:
  exporter:
    otlp:
      endpoint: http://otel-collector:4317
  service:
    name: order-service
  traces:
    sampler: traceidratio
    sampler.arg: 0.1

// 3. 业务代码加 @WithSpan 注解自动埋点
@Service
public class OrderService {

    @WithSpan("create-order")
    public Order createOrder(@SpanAttribute("user.id") String userId) {
        // 自动产生 span，无需手动埋点
        return orderRepository.save(new Order(userId));
    }
}

// 4. RestTemplate / WebClient 自动埋点
// HTTP 调用自动产生 CLIENT span，自动注入 traceparent
```

## 常见问题

### Q1：trace_id 重复怎么办？

A：trace_id 是 128 bit 随机数，**碰撞概率几乎为 0**。如果重复，要么是实现 bug，要么是 hardcode 了 trace_id。

### Q2：异步调用 trace 断了怎么办？

A：OTel 的 `Context.current().wrap()` 可以跨线程传播 context。Kafka/RabbitMQ 拦截器会自动注入 traceparent 头。

### Q3：跨服务 trace 关联不上？

A：检查 `traceparent` 头是否在网关上被剥掉（Nginx 反代默认会）。要在 Nginx 配置中保留：

```nginx
location / {
    proxy_pass http://backend;
    proxy_set_header traceparent $http_traceparent;
    proxy_set_header tracestate $http_tracestate;
}
```

### Q4：trace 太多了性能怎么办？

A：降采样（1%）+ 尾采样保留错误 + 限制 span 数（避免一个 trace 上千 span）。

## 一句话总结

> **Trace = 全局 ID + Span 树；Span = 时间段 + 父子关系 + 属性 + 事件**。
> 掌握 trace_id / span_id / parent_span_id 三个 ID 和 traceparent 头传播机制，**就掌握了链路追踪的核心**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集

<!-- svg-injected:do-not-edit -->

![distributed trace](/distributed-trace.svg)
