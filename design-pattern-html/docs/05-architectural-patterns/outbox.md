---
title: Outbox 事务性发件箱
description: 业务数据 + 消息同事务 + Debezium / Spring Modulith + 防止消息丢失
---

# Outbox 事务性发件箱

## 核心问题

业务系统经常需要「写业务数据 + 发消息」（订单创建后发订单事件），但两个操作不在同一个事务中：

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

**问题**：
1. **消息丢失**：业务写库成功 + 消息发送失败 → 状态不一致
2. **消息重复**：业务写库失败 + 消息发送成功 → 重复消息
3. **顺序错乱**：业务库的事务回滚了，消息已经发出

## 核心思想

把"业务数据变更 + 发送消息"合并到**同一个本地事务**中：

1. 业务表写入数据
2. 同时把消息写入 **outbox 表**（同事务）
3. 单独的 **relay 进程**轮询 outbox 表，把消息发到 Kafka / RabbitMQ
4. 发送成功后标记 outbox 记录为已发布
5. 定期清理已发布记录（避免表无限增长）

## Java 实战

```java
// Outbox 实体
@Entity
@Table(name = "outbox")
public class OutboxEvent {
    @Id private UUID id;
    private String aggregateType;       // 'Order'
    private String aggregateId;         // 'order-123'
    private String eventType;           // 'OrderCreated'
    @Column(columnDefinition = "TEXT") private String payload;  // JSON
    private Instant createdAt;
    private Instant publishedAt;        // null 表示未发布
}

// 业务操作：写订单 + 写 outbox 在同一事务
@Service
@Transactional
public class OrderService {
    @Autowired private OrderRepository orderRepo;
    @Autowired private OutboxRepository outboxRepo;

    public void createOrder(OrderRequest req) {
        Order order = Order.create(req);
        orderRepo.save(order);

        // 同事务：写 outbox 事件
        OutboxEvent event = new OutboxEvent();
        event.setId(UUID.randomUUID());
        event.setAggregateType("Order");
        event.setAggregateId(order.getId());
        event.setEventType("OrderCreated");
        event.setPayload(toJson(order));
        event.setCreatedAt(Instant.now());
        outboxRepo.save(event);
    }
}

// Relay 进程：轮询 outbox 表发送消息
@Component
public class OutboxRelay {
    @Autowired private OutboxRepository outboxRepo;
    @Autowired private KafkaTemplate<String, String> kafka;

    @Scheduled(fixedDelay = 1000)  // 每秒轮询
    public void relay() {
        List<OutboxEvent> unpublished = outboxRepo.findUnpublished(100);
        for (OutboxEvent e : unpublished) {
            try {
                kafka.send("order-events", e.getAggregateId(), e.getPayload()).get(5, TimeUnit.SECONDS);
                e.setPublishedAt(Instant.now());
                outboxRepo.save(e);
            } catch (Exception ex) {
                log.error("Failed to publish outbox event {}", e.getId(), ex);
                // 不标记已发布，下次重试
            }
        }
    }
}

// 定时清理已发布记录（30 天前）
@Scheduled(cron = "0 3 * * *")  // 每天凌晨 3 点
public void cleanup() {
    Instant cutoff = Instant.now().minus(30, ChronoUnit.DAYS);
    outboxRepo.deleteByPublishedAtBefore(cutoff);
}
```

## Debezium CDC 模式

更优雅的方案：用 Debezium 监听 binlog 自动生成消息，**不需要写 outbox 代码**：

```yaml
# Debezium 配置：监听 MySQL binlog
name: outbox-connector
config:
  connector.class: io.debezium.connector.mysql.MySqlConnector
  database.hostname: mysql
  database.port: 3306
  database.user: debezium
  database.password: dbz
  database.server.id: 184054
  database.server.name: dbserver1
  database.include.list: mydb
  table.include.list: mydb.outbox
  transforms: outbox
  transforms.outbox.type: io.debezium.transforms.outbox.EventRouter
```

应用代码只需要把事件写到 outbox 表（任意表结构），Debezium 自动：
1. 监听 binlog
2. 把 outbox 表的新行转成 Kafka 消息
3. 自动发布到 Kafka topic

**优势**：
- 应用代码简单（不写 relay 进程）
- 自动 exactly-once（基于 binlog offset）
- 业务侵入小

## Spring Modulith Outbox

```java
@Service
@Transactional
public class OrderService {
    @Autowired private OrderRepository orderRepo;
    @Autowired private ApplicationEventPublisher events;

    public void createOrder(OrderRequest req) {
        Order order = Order.create(req);
        orderRepo.save(order);

        // Spring Modulith 自动把事件写入 outbox 表
        events.publishEvent(new OrderCreatedEvent(order));
    }
}

// application.yml：Spring Modulith 自动启用 outbox
spring:
  modulith:
    events:
      outbox:
        enabled: true
```

## outbox 表设计

```sql
CREATE TABLE outbox (
    id              UUID PRIMARY KEY,
    aggregate_type  VARCHAR(255) NOT NULL,
    aggregate_id    VARCHAR(255) NOT NULL,
    event_type      VARCHAR(255) NOT NULL,
    payload         TEXT NOT NULL,
    metadata        JSONB,              -- 额外信息（trace_id / user_id 等）
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at    TIMESTAMP,          -- null = 未发布
    retry_count     INT DEFAULT 0,
    last_error      TEXT
);

CREATE INDEX idx_outbox_unpublished ON outbox (created_at) WHERE published_at IS NULL;
CREATE INDEX idx_outbox_cleanup ON outbox (published_at);
```

## 关键字段

| 字段 | 用途 |
|---|---|
| `aggregate_type` | 聚合根类型（Order / User） |
| `aggregate_id` | 聚合根 ID |
| `event_type` | 事件类型（OrderCreated / OrderPaid） |
| `payload` | JSON 序列化的事件 |
| `published_at` | 已发布时间（null = 未发布）|
| `retry_count` | 重试次数（避免无限重试）|
| `last_error` | 最后一次错误（调试用）|

## 实战：Debezium + Kafka 完整链路

```text
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌─────────┐
│ Order   │────→│ MySQL   │────→│ Debezium │────→│ Kafka   │
│ Service │     │ outbox  │     │ CDC      │     │ topic   │
└─────────┘     │ table   │     └──────────┘     └────┬────┘
                └─────────┘                            │
                                                       ▼
                                                ┌──────────┐
                                                │ Downstream│
                                                │ Services │
                                                └──────────┘

1. OrderService 写入 orders 表 + outbox 表（同事务）
2. Debezium 监听 outbox 表的 binlog
3. Debezium 把新行转成 Kafka 消息（自动）
4. 下游服务（payment / inventory / notification）消费 Kafka
5. exactly-once 投递（基于 binlog offset）
```

**优势**：
- **不丢失**：outbox 表与业务表同事务
- **不重复**：Kafka exactly-once 语义 + Debezium offset
- **保序**：binlog 顺序保证
- **低耦合**：业务不直接调下游，通过事件驱动

## 适用边界

✅ **使用场景**：
- 业务写库 + 发消息必须原子
- 不能容忍消息丢失（订单 / 支付事件）
- 高可靠性要求的金融系统

❌ **避免场景**：
- 消息丢失可接受（日志 / 监控事件）
- 业务能容忍最终一致
- 没有 outbox 表的基础设施

🔄 **演进路径**：
- 直接发消息 → 事务后异步发 → Outbox → Debezium CDC
- Debezium CDC 是当前最佳实践

💡 **最佳实践**：
- outbox 表和业务表同库（避免分布式事务）
- 用 Debezium 而不是手写 relay
- 配置清理策略（30 天前的已发布事件）
- 监控 outbox 表堆积（未发布 > 1 万告警）
- 给下游消费者设置幂等
