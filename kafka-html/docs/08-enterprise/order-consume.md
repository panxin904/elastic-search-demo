---
title: 顺序消费
date: 2026-08-15  # date-auto-injected
---

# 📊 顺序消费

> 很多业务场景要求消息**严格有序**（如订单状态变更、账户余额变动）。Kafka 保证单 Partition 内有序，但跨 Partition 需要业务设计。

## 🎯 顺序消费场景

```
✅ 订单状态：创建 → 支付 → 发货 → 完成
✅ 账户余额：A 扣 100 → B 加 100
✅ 数据库变更：INSERT → UPDATE → DELETE（CDC）
✅ 金融交易：下单 → 风控 → 清算
✅ 库存变更：减库存 → 创建订单 → 扣减记录
```

## 🔧 Kafka 顺序保证级别

### 单 Partition 顺序

```
✅ 单 Producer 发送 → 单 Partition 接收 → 单 Consumer 消费
   严格有序

⚠️ 限制：
   - 单 Partition 吞吐受限（~10MB/s）
   - 只能用一个 Consumer 消费
```

### 单 Key 顺序

```
✅ 同 Key 消息进入同一 Partition
   - 单 Key 内严格有序
   - 跨 Key 可并行处理
   - 兼顾顺序和性能
```

## 📊 顺序保证方案对比

| 方案 | 顺序保证 | 性能 | 复杂度 | 适用 |
|------|---------|------|--------|------|
| **单 Partition** | 全局有序 | ❌ 低 | 低 | 数据量小 |
| **单 Key** | 单 Key 有序 | ✅ 高 | 低 | 大多数场景 |
| **业务排序** | 全局有序 | ✅ 中 | 高 | 复杂场景 |
| **时间戳排序** | 准有序 | ⚠️ 中 | 中 | 时序场景 |

## 🔧 方案 1：单 Partition 全局有序

### 适用场景

```
✅ 业务数据量小（< 10MB/s）
✅ 严格要求全局有序
✅ 简单即可（不想设计复杂方案）
```

### 配置

```bash
# 创建单 Partition 的 Topic
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 1 \
    --replication-factor 3
```

### 代码

```java
// 单 Partition：所有消息严格有序
@KafkaListener(topics = "orders")
public void consume(OrderEvent event) {
    // 严格按照发送顺序处理
    processOrder(event);
}

// 限制：单 Partition 吞吐受限
```

**优缺点**：
- ✅ 实现最简单
- ❌ 单 Partition 上限（~10MB/s）
- ❌ 单 Consumer 消费

## 🔧 方案 2：按 Key 路由（推荐）

### 适用场景

```
✅ 大多数业务（订单、用户操作、状态变更）
✅ 只需同 Key 顺序
✅ 需高吞吐
```

### 核心思想

```
按 Key 路由到同一 Partition：
  - 同 Key 顺序保证
  - 跨 Key 可并行（不同 Partition）
  - 单 Consumer 处理单 Partition

实战：
  - Key = orderId → 同订单事件进同一 Partition
  - Key = userId → 同用户事件进同一 Partition
  - Key = accountId → 同账户事件进同一 Partition
```

### 代码

```java
@Service
public class OrderProducer {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    public void publishOrderEvent(OrderEvent event) {
        // ✅ Key = orderId：同订单事件进同一 Partition
        kafkaTemplate.send("orders", event.getOrderId(), event);
    }
    
    public void publishAccountEvent(AccountEvent event) {
        // ✅ Key = accountId：同账户事件进同一 Partition
        kafkaTemplate.send("accounts", event.getAccountId(), event);
    }
}
```

```java
@Service
public class OrderConsumer {
    
    // ✅ 单 Consumer 处理单 Partition（保证同 orderId 顺序）
    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void consume(OrderEvent event, Acknowledgment ack) {
        try {
            processOrder(event);
            ack.acknowledge();
        } catch (Exception e) {
            log.error("Process failed", e);
        }
    }
}
```

### Hash Tag 技巧

```java
// 使用 Hash Tag 强制路由
// 例：订单 1001 的创建事件和支付事件必须同 Partition
kafkaTemplate.send("orders", "order:create:{1001}", orderCreatedEvent);
kafkaTemplate.send("orders", "order:pay:{1001}", orderPayEvent);

// {} 内的内容作为 hash key → 两个消息进同一 Partition
```

```bash
# Kafka 会用 {} 内的内容作为 hash 依据
# "order:create:{1001}" 和 "order:pay:{1001}" → 都用 "1001" 计算 hash
# → 同一 Partition
```

## 🔧 方案 3：业务排序（窗口内）

### 适用场景

```
✅ 跨 Partition 也需有序
✅ 接受窗口内延迟
```

### 思想

```
每个消息带时间戳或序号
Consumer 收集到一定数量后排序处理
```

### 代码

```java
public class TimeWindowSorter {
    
    private final PriorityBlockingQueue<EventWithTime> queue = 
        new PriorityBlockingQueue<>(10000, Comparator.comparing(EventWithTime::getTimestamp));
    
    public void onMessage(OrderEvent event, Acknowledgment ack) {
        // 1. 按时间戳放入优先队列
        queue.offer(new EventWithTime(event, System.currentTimeMillis()));
        
        // 2. 定时或按窗口大小触发 flush
        if (shouldFlush()) {
            flush();
        }
        
        ack.acknowledge();
    }
    
    private void flush() {
        EventWithTime event;
        while ((event = queue.poll()) != null) {
            // 严格按时间戳顺序处理
            processOrder(event.getEvent());
        }
    }
    
    private boolean shouldFlush() {
        // 每 100ms flush 一次
        return queue.size() >= 100;
    }
}
```

**优缺点**：
- ✅ 全局有序
- ❌ 延迟（窗口大小）
- ❌ 复杂

## 🔧 方案 4：事务保证跨 Partition 原子

### 适用场景

```
✅ 跨 Partition 原子写入
✅ 状态变更强一致
```

### 代码

```java
@Service
public class TransferService {
    
    @Autowired
    private KafkaTemplate<String, AccountEvent> kafkaTemplate;
    
    public void transfer(String from, String to, int amount) {
        kafkaTemplate.executeInTransaction(operations -> {
            // A 账户扣款（Account-A Partition 0）
            operations.send("accounts", from, 
                new AccountEvent(from, -amount, "TRANSFER_OUT"));
            
            // B 账户加款（Account-B Partition 1）
            operations.send("accounts", to, 
                new AccountEvent(to, amount, "TRANSFER_IN"));
            
            // 审计日志（Audit Partition）
            operations.send("audit", "transfer-" + from + "-" + to,
                new AuditEvent("TRANSFER", from, to, amount));
            
            return null;
            // 事务提交：3 个 Partition 原子写入
        });
    }
}
```

## 🔧 实战：订单状态顺序消费

### 完整示例

```java
// 1. 实体
@Data
public class OrderEvent {
    private String orderId;
    private String status;     // CREATED / PAID / SHIPPED / COMPLETED
    private Long timestamp;
}

// 2. Producer
@Service
public class OrderEventProducer {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    public void publishEvent(String orderId, String status) {
        OrderEvent event = new OrderEvent();
        event.setOrderId(orderId);
        event.setStatus(status);
        event.setTimestamp(System.currentTimeMillis());
        
        // ✅ Key = orderId：同订单事件进同一 Partition
        kafkaTemplate.send("order-events", orderId, event);
    }
}

// 3. Consumer
@Service
public class OrderEventConsumer {
    
    @Autowired
    private OrderRepository orderRepository;
    
    @KafkaListener(topics = "order-events", groupId = "order-processor")
    public void consume(OrderEvent event, Acknowledgment ack) {
        // ✅ 同 orderId 顺序到达（因为 Key 路由到同一 Partition）
        
        Order order = orderRepository.findById(event.getOrderId()).orElseThrow();
        
        // 状态机校验
        if (isValidTransition(order.getStatus(), event.getStatus())) {
            order.setStatus(event.getStatus());
            orderRepository.save(order);
        } else {
            log.warn("Invalid transition: orderId={}, {} -> {}", 
                event.getOrderId(), order.getStatus(), event.getStatus());
        }
        
        ack.acknowledge();
    }
    
    private boolean isValidTransition(String from, String to) {
        Map<String, Set<String>> transitions = Map.of(
            "CREATED", Set.of("PAID", "CANCELLED"),
            "PAID", Set.of("SHIPPED", "REFUNDED"),
            "SHIPPED", Set.of("COMPLETED", "RETURNED")
        );
        return transitions.getOrDefault(from, Set.of()).contains(to);
    }
}
```

## 🔧 顺序保证的最佳实践

### 设计原则

```
✅ 优先按 Key 路由（最常见）
   - Key = 业务主键（orderId、userId 等）
   - 保证同 Key 内顺序

⚠️ 跨 Partition 顺序用事务
   - 原子写入
   - 牺牲性能换一致性

⚠️ 全局有序用单 Partition
   - 仅适合小数据量
   - 不推荐生产用

✅ 业务幂等是基础
   - 即使有顺序保证，仍需幂等
   - 网络抖动可能乱序
```

### 顺序保证清单

```
✅ Producer 端：
   1. 启用幂等性（enable.idempotence=true）
   2. acks=all
   3. retries > 0
   4. max.in.flight.requests.per.connection ≤ 5

✅ Consumer 端：
   1. 单线程处理单个 Partition
   2. 按 Key 路由的业务处理
   3. 业务状态机校验

✅ Topic 设计：
   1. Key 设计（业务主键）
   2. Partition 数 = 期望并行度
   3. 多副本（replication.factor ≥ 3）
```

## ⚠️ 常见问题

### 问题 1：同 Key 跨 Partition

```
原因：增加 Partition 后，Key 路由改变
解决：
  1. 不减少 Partition（仅增加）
  2. 增加 Partition 时谨慎（同 Key 顺序会破坏）
```

### 问题 2：Consumer 多线程破坏顺序

```
原因：多线程并行处理同一 Partition
解决：
  1. 单 Consumer 单线程
  2. 多 Consumer 但不同 Partition
```

### 问题 3：幂等性丢失导致重复

```
现象：消息被处理多次，状态变更错乱
解决：
  1. 业务状态机校验
  2. 数据库乐观锁
```

## 🎯 总结

**顺序消费核心要点**：
- ✅ 按 Key 路由（最常见，推荐）
- ✅ 单 Partition 全局有序（仅小数据量）
- ✅ 事务保证跨 Partition 原子
- ✅ Producer 启用幂等性
- ✅ Consumer 单线程处理单 Partition
- ⚠️ 顺序保证不是免费的（性能 vs 一致性）
- ⚠️ 业务幂等仍是基础

**下一步：** [⏰ 延迟消息](/08-enterprise/delay) — 延迟队列实现
