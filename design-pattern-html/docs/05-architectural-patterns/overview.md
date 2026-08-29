---
title: 架构模式（微服务 / 分层 / 事件溯源等）
date: 2026-08-15  # date-auto-injected
---

# 架构模式总览

> 微服务时代的「系统级设计模式」。它们不再是单个类与对象的组合，而是**跨服务、跨进程、跨节点**的协作模式。每个架构模式都是一组 GoF 模式的「架构升级版」，并对应一套成熟的开源实现。

## 为什么需要架构模式

单体应用时代，业务逻辑放在同一个进程内，类与类的协作靠 OOP 设计模式就能搞定。但微服务时代，每个服务都是独立部署的进程，业务逻辑必须跨网络协作：

1. **数据一致性**：订单服务扣款 + 库存服务扣货，不能用本地事务 → Saga
2. **读写分离**：报表查询 vs 在线交易，写模型和读模型不同 → CQRS
3. **服务降级**：下游服务挂了，怎么保护上游不被拖死 → Circuit Breaker / Bulkhead
4. **旧系统迁移**：怎么从 monolith 渐进迁移到微服务 → Strangler Fig

这些问题的解决方案被称为「架构模式」，它们是**部署单元级别的设计模式**。

## 8 种架构模式速览

| 模式 | 核心问题 | 典型案例 |
|---|---|---|
| **CQRS** | 读写模型分离 | Axon / EventStoreDB / Kafka Streams |
| **Event Sourcing** | 用事件序列保存状态 | Axon / EventStoreDB |
| **Saga** | 分布式事务 | Camunda / Temporal / Apache ServiceComb Saga |
| **Sidecar** | 把辅助能力从主应用剥离 | Istio / Linkerd / Dapr |
| **Circuit Breaker** | 下游故障时快速失败 | Resilience4j / Hystrix / Sentinel |
| **Bulkhead** | 资源隔离，防止故障扩散 | Resilience4j / Hystrix 线程池 |
| **Strangler Fig** | 渐进式迁移 monolith | Netflix 绞杀者模式 / 蚂蚁金服 SOFA |
| **Outbox** | 事务性发件箱 | Debezium / debezium-cdc |

## CQRS（Command Query Responsibility Segregation）

### 核心思想

把**写操作（Command）**和**读操作（Query）**分离到不同的模型/服务/数据库上。

### 为什么要分离

传统 CRUD 模型：

```
Client → Service → Database（同一张表同时承担读和写）
```

问题：
- **读写竞争**：写加锁影响读性能
- **模型冲突**：写模型要范式化，读模型要反范式化
- **扩展困难**：报表查询（OLAP）跟在线交易（OLTP）放一个库不合理

### CQRS 解决方案

```
Client → CommandService → WriteDB → EventBus → QueryService → ReadDB（优化索引）
                                          ↑
                                  Materialized View
```

读模型和写模型可以是完全不同的存储：

| 写模型 | 读模型 |
|---|---|
| PostgreSQL（事务强一致） | Elasticsearch（全文检索） |
| MySQL | ClickHouse（OLAP） |
| MongoDB | Redis（缓存） |

### 实战：Axon Framework

```java
// 命令端：写操作
@CommandHandler
public void handle(CreateOrderCommand cmd, Repository<Order> repo) {
    Order order = new Order(cmd.getOrderId(), cmd.getItems());
    repo.add(order);  // 写库
}

// 事件投影：自动同步到读库
@EventHandler
public void on(OrderCreatedEvent event, EntityManager em) {
    OrderView view = new OrderView(event.getOrderId(), event.getTotal());
    em.persist(view);  // 读库
}

// 查询端：读操作
@QueryHandler
public OrderView findOrder(String orderId) {
    return em.find(OrderView.class, orderId);
}
```

### 何时用 / 避免

✅ **使用**：读写比例严重失衡（1:1000）/ 读写模型差异巨大 / 多查询数据源
❌ **避免**：简单 CRUD / 单体应用 / 团队无 ES / DDD 经验

## Event Sourcing 事件溯源

### 核心思想

不保存对象的当前状态，而是保存**导致状态变化的全部事件**。当前状态 = replay 所有事件。

### 与传统 CRUD 对比

```sql
-- 传统：只保留最新状态
UPDATE accounts SET balance = 100 WHERE id = 'alice';
-- 历史丢失

-- Event Sourcing：保留事件流
-- 1. AccountCreated{alice, 0}
-- 2. MoneyDeposited{alice, +1000}
-- 3. MoneyWithdrawn{alice, -500}
-- 4. MoneyDeposited{alice, +200}
-- replay 后: balance = 700
```

### 优势

1. **完整审计**：所有状态变化可追溯
2. **时间旅行**：可以查询任意时间点的状态
3. **事件驱动**：天然适合 Event-Driven Architecture
4. **回放调试**：测试时 replay 真实事件

### 劣势

1. **复杂查询困难**：要算当前状态必须 replay 全部事件（用 snapshot 缓解）
2. **schema 演进**：事件结构变了要兼容老事件
3. **存储成本**：事件不断增长，需要冷热分离

### 实战：Axon + EventStoreDB

```java
// 聚合根只产生事件，不直接修改字段
@Aggregate
public class BankAccount {
    private BigDecimal balance;

    @CommandHandler
    public BankAccount(OpenAccountCommand cmd) {
        apply(new AccountOpenedEvent(cmd.getAccountId(), cmd.getInitialBalance()));
    }

    @EventSourcingHandler
    public void on(AccountOpenedEvent event) {
        this.balance = event.getInitialBalance();
    }
}
```

### 与 CQRS 的关系

Event Sourcing 是 CQRS 的**写端实现**，CQRS 是 Event Sourcing 的**读端优化**。两者经常一起使用（Event Sourcing + CQRS = EDA 完整方案）。

## Saga 分布式事务模式

### 核心思想

把分布式长事务拆成多个**本地事务 + 补偿操作**，最终一致性。

### 两种 Saga

| 类型 | 实现 | 适用 |
|---|---|---|
| **Orchestration（编排）** | 中央协调器逐步调用 | 流程清晰 / 适合复杂业务 |
| **Choreography（编排）** | 各服务通过事件相互触发 | 简单流程 / 服务解耦 |

### 实战：电商下单 Saga

```typescript
// Orchestration Saga
class OrderSaga {
    constructor(
        private orderService: OrderService,
        private paymentService: PaymentService,
        private inventoryService: InventoryService,
        private shippingService: ShippingService,
    ) {}

    async execute(orderReq: OrderRequest) {
        const sagaId = uuid();
        try {
            // 1. 创建订单（本地事务）
            const order = await this.orderService.create(orderReq);

            // 2. 扣款（本地事务）
            await this.paymentService.charge(order);

            // 3. 扣库存（本地事务）
            await this.inventoryService.reserve(order.items);

            // 4. 创建发货单（本地事务）
            await this.shippingService.createShipment(order);

            await this.orderService.markCompleted(order.id);
        } catch (e) {
            // 失败时反向补偿
            await this.compensate(order, e);
        }
    }

    async compensate(order: Order, error: Error) {
        if (order.shipped) await this.shippingService.cancelShipment(order.id);
        if (order.inventoryReserved) await this.inventoryService.release(order.items);
        if (order.paid) await this.paymentService.refund(order);
        await this.orderService.markFailed(order.id);
        throw error;
    }
}
```

### 实战工具

- **Apache ServiceComb Saga**：Java 实现的 Saga 协调器
- **Temporal**：跨语言的 workflow 引擎
- **Camunda**：BPMN 驱动的 Saga 编排
- **AWS Step Functions**：云厂商实现

## Sidecar 边车模式

### 核心思想

把与业务无关的辅助能力（日志 / 监控 / 配置 / 网络代理）从主应用中剥离，部署在同一个 Pod/Host 的「边车」容器/进程中。

### Kubernetes Pod 实战

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-sidecar
spec:
  containers:
    - name: app          # 主应用
      image: myapp:1.0
      ports:
        - containerPort: 8080

    - name: sidecar      # 边车：日志收集
      image: fluent-bit:2.0
      volumeMounts:
        - name: logs
          mountPath: /var/log/app

    - name: istio-proxy  # 边车：服务网格数据面
      image: istio/proxyv2:1.20.0

  volumes:
    - name: logs
      emptyDir: {}
```

### Sidecar 解决什么问题

1. **语言无关**：用 Go 写主应用，日志收集可以选任意技术栈
2. **主应用纯净**：业务代码不需要包含网络/日志/监控逻辑
3. **独立升级**：升级边车不需要重新部署主应用
4. **多边车**：一个 Pod 可以挂多个 Sidecar（链路追踪 + 监控 + 日志）

### 典型应用

- **Istio / Linkerd**：服务网格数据面
- **Dapr**：分布式应用运行时
- **Filebeat / Fluent-bit**：日志收集
- **Envoy**：API Gateway / Sidecar 代理

## Circuit Breaker 熔断模式

### 核心思想

当下游服务故障率超过阈值时，熔断器打开，直接快速失败（fallback），避免雪崩效应。

### 三种状态

```
       失败率 < 阈值        失败率 ≥ 阈值
CLOSED ──────────────→ OPEN
   ↑                      │
   │    经过 sleepWindow   │
   └──── HALF_OPEN ←──────┘
            │
            │ 试探请求成功 → CLOSED
            │ 试探失败 → OPEN
```

### 实战：Resilience4j

```java
@Service
public class PaymentService {
    @CircuitBreaker(name = "payment", fallbackMethod = "paymentFallback")
    public PaymentResult pay(PaymentRequest req) {
        return paymentClient.charge(req);
    }

    // 熔断后的 fallback
    private PaymentResult paymentFallback(PaymentRequest req, Throwable t) {
        log.warn("payment service unavailable: {}", t.getMessage());
        // 排队等待 / 异步重试 / 返回默认值
        return PaymentResult.deferred(req.getOrderId());
    }
}
```

### 配置项

```yaml
resilience4j:
  circuitbreaker:
    instances:
      payment:
        failureRateThreshold: 50        # 失败率 50% 触发熔断
        slowCallRateThreshold: 100      # 慢调用 100% 触发
        slowCallDurationThreshold: 2s   # 2 秒算慢调用
        slidingWindowSize: 100          # 滑动窗口 100 个请求
        minimumNumberOfCalls: 10        # 至少 10 个请求才计算
        waitDurationInOpenState: 10s    # OPEN 状态保持 10 秒
        permittedNumberOfCallsInHalfOpenState: 3  # HALF_OPEN 试 3 次
```

## Bulkhead 舱壁隔离模式

### 核心思想

把资源（线程池 / 连接池 / CPU）按业务隔离，避免一个慢请求占满所有资源拖垮整个应用。

### 实战：舱壁化线程池

```java
// ❌ 没有隔离：慢请求占满所有线程
@HystrixCommand
public String slowService() {
    return httpClient.get("https://slow.example.com");
}

// ✅ 舱壁化：每个服务独立线程池
@HystrixCommand(
    groupKey = "orderService",
    threadPoolKey = "orderPool",
    threadPoolProperties = {
        @HystrixProperty(name = "coreSize", value = "20")
    })
public Order createOrder(OrderRequest req) {
    // 独立线程池，不受 slowService 影响
}
```

### 实战：舱壁化连接池

```typescript
// TypeScript: 给每个下游服务独立连接池
const httpClients = {
    payment: axios.create({
        baseURL: 'https://payment.example.com',
        maxSockets: 10,
    }),
    inventory: axios.create({
        baseURL: 'https://inventory.example.com',
        maxSockets: 10,
    }),
    // 即使 payment 服务挂掉，inventory 仍有自己的 10 个连接可用
};
```

### K8s 实战

```yaml
# K8s 的 resource limit 也是舱壁
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m     # 不能超过 0.5 核
    memory: 512Mi # 不能超过 512MB
```

## Strangler Fig 绞杀者模式

### 核心思想

不重写旧系统，而是逐步用新服务**包裹**旧系统，逐步把流量从旧系统迁移到新服务。

### 三阶段迁移

```
阶段 1（共存）：新服务上线，流量通过 Facade 分发，旧服务承担所有写，新服务承担部分读
阶段 2（迁移）：逐步把业务功能从旧服务迁移到新服务
阶段 3（绞杀）：旧服务只剩壳子，最终下线
```

### 实战：API Gateway 流量切换

```nginx
# Nginx 把 10% 流量切到新服务
upstream old_service {
    server old.internal:8080;
}

upstream new_service {
    server new.internal:8080;
}

server {
    location / {
        # 90% 流量到旧服务
        set $backend old_service;
        if ($request_id ~* "^.{0}$") {  # 10% 抽样
            set $backend new_service;
        }
        proxy_pass http://$backend;
    }
}
```

### 实战案例

- **Netflix**：从 monolith 迁移到微服务用了 7 年（2008-2015）
- **Amazon**：2002 年开始迁移 monolith 到 SOA，2010 年代完成
- **京东**：618 大促前用 Strangler 迁移订单系统
- **蚂蚁金服**：从 IOE 到 SOFA 的渐进迁移

### 何时用

✅ **业务不能中断**：在线系统不能停机
✅ **代码历史包袱**：旧系统代码无法维护，但业务价值高
✅ **团队分批交付**：新功能要分批上线，避免大爆炸发布

❌ **避免**：旧系统可以直接重写（业务简单）/ 流量太小不值得拆分

## Outbox 事务性发件箱模式

### 核心思想

把"业务数据变更 + 发送消息"合并到同一个本地事务中，确保**消息不丢不重**。

### 问题背景

```java
// ❌ 双写问题：业务写库成功 + 消息发送失败
@Transactional
public void createOrder(Order o) {
    orderRepo.save(o);
    kafka.send(new OrderCreatedEvent(o));  // 失败 → 消息丢失
}

@Transactional
public void createOrder(Order o) {
    orderRepo.save(o);
    // 事务提交后再发送？可能发送前进程崩溃
    TransactionSynchronizationManager.register(...);
}
```

### 解决方案

```java
// ✅ Outbox：消息作为业务数据的一部分入库
@Transactional
public void createOrder(Order o) {
    orderRepo.save(o);
    // 同时把事件写入 outbox 表（同事务）
    outboxRepo.save(new OutboxEvent(
        UUID.randomUUID(),
        "OrderCreated",
        serialize(o),
        Instant.now()
    ));
}

// 单独的 relay 进程轮询 outbox 表，发到 Kafka
@Scheduled(fixedDelay = 1000)
public void relay() {
    List<OutboxEvent> events = outboxRepo.findUnpublished();
    for (OutboxEvent e : events) {
        kafka.send(e.getTopic(), e.getPayload());
        outboxRepo.markPublished(e.getId());
    }
}
```

### 实战工具

- **Debezium**：监听 binlog 自动生成 outbox 事件
- **Spring Modulith Outbox**：Spring 官方支持
- **Axon Server**：内置 outbox + event store
- **Kafka Connect**：CDC 模式

## 8 架构模式决策树

```
需要跨服务协作？
├── 业务事务跨多个服务 → Saga
├── 读写模型差异巨大 → CQRS
├── 需要完整审计 + 重放 → Event Sourcing
├── 下游服务不可靠 → Circuit Breaker
├── 一个慢请求拖垮整体 → Bulkhead
└── 业务消息不能丢 → Outbox

需要部署/迁移？
├── 业务不能中断迁移 → Strangler Fig
└── 辅助能力剥离主应用 → Sidecar
```

## 与 GoF 23 模式的关系

| 架构模式 | GoF 对应 | 升级版特性 |
|---|---|---|
| CQRS | Command + Strategy | 跨服务 |
| Event Sourcing | Memento + Observer | 跨进程 |
| Saga | Command + State Machine | 跨服务编排 |
| Sidecar | Decorator + Proxy | 跨进程部署 |
| Circuit Breaker | State Machine | 跨服务状态管理 |
| Bulkhead | Façade | 跨服务资源隔离 |
| Strangler Fig | Adapter + Facade | 跨版本迁移 |
| Outbox | Command + Observer | 跨系统消息可靠性 |

## 实战建议

1. **CQRS 不要全用**：80% 业务用传统 CRUD 即可，只在「读写严重失衡」时用 CQRS
2. **Event Sourcing 慎用**：事件 schema 演进是噩梦，先有 CQRS 经验再上 ES
3. **Saga 优先 Orchestration**：中央协调器比事件链更容易调试
4. **Circuit Breaker 必须配 fallback**：不配 fallback 等于没熔断
5. **Bulkhead 用 K8s limit 实现**：Java 应用层 Bulkhead 容易被绕过
6. **Strangler 一定要灰度**：10% → 50% → 100%，不要直接切流量
7. **Outbox 是事务消息的标准答案**：不要再写 `tx.commit() + kafka.send()`

## 下一步

- 阅读每篇单独的架构模式细节：[CQRS](./cqrs) / [Event Sourcing](./event-sourcing) / [Saga](./saga) / [Sidecar](./sidecar) / [Circuit Breaker](./circuit-breaker) / [Bulkhead](./bulkhead) / [Strangler Fig](./strangler-fig) / [Outbox](./outbox)
- 进阶：[行为型 · 命令](../03-gof-behavioral/command)（Saga 的基础）
- 反向自查：反模式 · 单点故障（架构层常见病）

## 相关站点

- **system-design**：分布式系统理论 + 经典系统设计题
- **architecture**：DDD + 微服务架构
- **devops**：灰度发布 / 监控 / 告警
- **observability**：日志 / 指标 / 链路追踪

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
