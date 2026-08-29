---
title: 分布式追踪
date: 2026-08-15  # date-auto-injected
---

# 🔍 分布式追踪

> 在微服务架构下追踪**跨服务的完整调用链路**。

## 🎯 为什么需要分布式追踪？

**单体应用：** 一个线程一个调用栈，debug 简单

```
Client → Controller → Service → DAO
（一个线程栈，一目了然）
```

**微服务架构：** 一个请求可能跨 N 个服务

```
Client → Gateway → Order-Service → Inventory-Service → DB
              ↓
         Payment-Service → Account-Service → DB

传统日志无法关联
```

**分布式追踪解决的问题：**
- **链路追踪**：一个请求完整经过哪些服务
- **耗时分析**：每个服务耗时多少
- **故障定位**：哪个服务出错
- **依赖分析**：服务间依赖关系

## 📐 核心概念

### Trace / Span / Parent

```
Trace（一次完整请求）
  ├─ Span 1: HTTP 请求（gateway）
  │   ├─ Span 2: Order Service
  │   │   ├─ Span 3: HTTP 请求（inventory）
  │   │   │   └─ Span 4: DB Query
  │   │   └─ Span 5: MQ 发送（异步）
  │   └─ Span 6: Payment Service
  └─ ...
```

| 概念 | 含义 |
|---|---|
| **Trace** | 一次完整请求链路（树形结构）|
| **Span** | 一个操作单元（如一次 HTTP 调用）|
| **Parent Span** | 父级 Span |
| **Span ID** | Span 唯一标识 |
| **Trace ID** | Trace 唯一标识 |
| **SpanContext** | 跨服务传递的上下文 |

### Trace ID 生成

```
TraceId = 32 字符 hex（如 a1b2c3d4e5f6...）
SpanId  = 16 字符 hex（如 1234567890abcdef）
```

## 🛠️ 主流方案对比

| 特性 | **Sleuth + Zipkin** | **SkyWalking** | **Jaeger** | **Pinpoint** |
|---|---|---|---|---|
| **开发方** | Spring | Apache（华为）| Uber | Naver |
| **接入方式** | 字节码增强 / 注解 | 字节码增强 | 客户端库 | 字节码增强 |
| **存储** | ES / MySQL / Cassandra | ES / H2 / MySQL | ES / Cassandra | HBase |
| **UI** | Zipkin UI | SkyWalking UI | Jaeger UI | Pinpoint UI |
| **性能损耗** | 小 | 极小 | 小 | 极小 |
| **依赖图** | ✅ | ✅ | ✅ | ✅ |
| **告警** | ❌ | ✅ | ❌ | ✅ |
| **多语言** | Java | 多语言 | 多语言 | Java |
| **侵入性** | 中（需配置）| 低（自动）| 中 | 低（自动）|
| **适用** | Spring Cloud | 大型分布式 | 多语言 | 大型企业 |

## 🌟 SkyWalking 详解

### 架构

```
              ┌─────────────────────┐
              │   SkyWalking UI     │
              └──────────┬──────────┘
                         │ Query
              ┌──────────▼──────────┐
              │   SkyWalking OAP    │（集群）
              │   ┌──────┐ ┌──────┐ │
              │   │Receiver│ │Query│ │
              │   └──────┘ └──────┘ │
              └──────────┬──────────┘
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
   ┌─────────┐      ┌─────────┐      ┌─────────┐
   │ Agent  │      │ Agent   │      │ Agent   │
   │Service-A│      │Service-B│      │Service-C│
   └─────────┘      └─────────┘      └─────────┘
```

| 组件 | 作用 |
|---|---|
| **Agent** | 探针，采集数据 |
| **OAP** | 后端服务，接收 + 存储 + 查询 |
| **UI** | Web 控制台 |
| **Storage** | ES / H2 / MySQL 等 |

### 部署 OAP

```yaml
# docker-compose.yml
services:
  skywalking-oap:
    image: apache/skywalking-oap-server:9.0.0
    ports:
      - "11800:11800"   # gRPC
      - "12800:12800"   # HTTP
    environment:
      SW_STORAGE: elasticsearch
      SW_ES_SERVER_URLES: http://elasticsearch:9200

  skywalking-ui:
    image: apache/skywalking-ui:9.0.0
    ports:
      - "8080:8080"
    depends_on:
      - skywalking-oap
```

### Java 应用集成 Agent

```bash
# 启动时挂载 Agent
java -javaagent:/skywalking/agent/skywalking-agent.jar \
     -Dskywalking.agent.service_name=order-service \
     -Dskywalking.collector.backend_service=127.0.0.1:11800 \
     -jar order-service.jar
```

**零代码侵入**，自动采集 HTTP / JDBC / MQ 等调用

### UI 核心功能

| 功能 | 说明 |
|---|---|
| **Trace 查询** | 按 Trace ID / 服务 / 时间查找 |
| **拓扑图** | 自动绘制服务依赖关系 |
| **慢调用分析** | 按耗时排序 |
| **错误率** | 异常调用统计 |
| **告警** | 配置规则（如错误率 > 5%）|

## 🔬 Sleuth + Zipkin 实战

### Sleuth 依赖

```xml
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-sleuth</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.cloud</groupId>
    <artifactId>spring-cloud-starter-zipkin</artifactId>
</dependency>
```

### 配置

```yaml
spring:
  application:
    name: order-service
  zipkin:
    base-url: http://127.0.0.1:9411
  sleuth:
    sampler:
      probability: 1.0  # 100% 采样（生产建议 0.1）
```

### 日志中自动出现 Trace ID

```
2024-01-15 10:23:45 [order-service,a1b2c3d4e5f6,1234567890abcdef,true]
INFO  com.example.OrderController - 处理订单请求
```

| 字段 | 含义 |
|---|---|
| `order-service` | 服务名 |
| `a1b2c3d4e5f6` | Trace ID |
| `1234567890abcdef` | Span ID |
| `true` | 是否采样 |

### 自定义 Span

```java
@RestController
public class OrderController {

    @Autowired
    private Tracer tracer;

    @GetMapping("/order/{id}")
    public Order get(@PathVariable Long id) {
        // 创建自定义 Span
        Span newSpan = tracer.nextSpan().name("customLogic").start();
        try (Tracer.SpanInScope ws = tracer.withSpan(newSpan)) {
            // 业务逻辑
            return orderService.findById(id);
        } finally {
            newSpan.end();
        }
    }
}
```

## 🏷️ Trace ID 跨服务传递

```
HTTP Header: 
  X-B3-TraceId: a1b2c3d4e5f6
  X-B3-SpanId:  1234567890abcdef
  X-B3-ParentSpanId: ...
```

**Spring Cloud 自动通过 RestTemplate / OpenFeign 传递**

## 📊 采样策略

| 策略 | 适用 |
|---|---|
| **100% 全采样** | 测试 / 低流量 |
| **比例采样** | 生产（如 10%）|
| **限流采样** | QPS 高时按比例降级 |
| **尾部采样** | 只保留异常 / 慢调用 |

```yaml
spring:
  sleuth:
    sampler:
      probability: 0.1   # 10% 采样
```

## ⚠️ 分布式追踪的坑

### 1. 日志关联

日志中找不到 Trace ID

**解决：** Logback 配置 Pattern
```xml
<pattern>%d{yyyy-MM-dd HH:mm:ss.SSS} [%X{X-B3-TraceId},%X{X-B3-SpanId}] %-5level %logger{36} - %msg%n</pattern>
```

### 2. 异步调用丢失上下文

```java
// 错误：异步线程拿不到 TraceContext
executor.submit(() -> {
    log.info("异步处理");  // 没有 Trace ID
});

// 正确：包装 Runnable / Callable
ExecutorService executor = Executors.newFixedThreadPool(10);
Runnable wrapped = RunnableWrapper.wrap(originalRunnable);
executor.submit(wrapped);
```

### 3. MQ 消息上下文

MQ 消费时丢失 Trace ID

**解决：** 发送消息时把 Trace Context 放入 Header，消费者取出并恢复

```java
// 生产者
Message message = new Message();
message.setHeader("X-B3-TraceId", currentTraceId);
producer.send(message);

// 消费者
String traceId = message.getHeader("X-B3-TraceId");
MDC.put("X-B3-TraceId", traceId);
```

### 4. 性能开销

**Agent 字节码增强**会带来 1-5% 的性能损耗

**解决：** 生产环境降采样到 10%

## 🎯 选型建议

```
                  Spring Cloud 项目？
                        │
                  ┌─────┴─────┐
                 是           否（多语言）
                  │                │
           Sleuth + Zipkin       Jaeger
                  │
            需要完整 APM？
            （告警 / 依赖图 / 拓扑）
                  │
              ┌───┴───┐
             是       否（只要追踪）
              │         │
          SkyWalking   Zipkin
```

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| 分布式追踪的原理？| Trace + Span + TraceContext 传递 |
| Trace ID 如何传递？| HTTP Header / MQ Header / 线程上下文 |
| Sleuth vs SkyWalking？| Sleuth 简单轻量，SkyWalking 功能完整 |
| 异步线程如何传递？| 包装 Runnable / ThreadLocal 拷贝 |

---

- 上一章：[🔄 分布式协调](/07-distributed/distributed-coordination)
- 下一章：[🛡️ 高可用 / 限流熔断](/07-distributed/high-availability)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):微服务架构
- [system-design](https://java-px.bot.cd/system-design/):系统设计
- [cloud-native](https://java-px.bot.cd/cloud-native/):Docker / K8s 落地
