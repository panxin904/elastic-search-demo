---
title: 延迟消息
---

# ⏰ 延迟消息

> Kafka 本身**不直接支持**延迟消息（类似 RabbitMQ 的延迟队列）。但通过**ZSet 模式**或**自定义延迟 Topic** 可以实现。

## 🎯 延迟消息场景

```
✅ 订单超时关闭（30 分钟未支付）
✅ 优惠券过期（24 小时未使用）
✅ 短信验证码（5 分钟失效）
✅ 定时提醒（会议 10 分钟前）
✅ 异步重试（失败任务 5 分钟后重试）
✅ 定时任务调度（替代 cron）
```

## 🔧 方案 1：定时扫描模式

### 思想

```
发送消息时携带"执行时间"
Consumer 接收后暂存
定时器定期扫描，找到到期的消息执行
```

### 内存版实现

```java
// 简单的内存延迟队列（仅适合单机）
@Component
public class InMemoryDelayQueue {
    
    private final PriorityBlockingQueue<DelayedTask> queue = 
        new PriorityBlockingQueue<>(1000, Comparator.comparing(DelayedTask::getExecuteAt));
    
    private final ScheduledExecutorService scheduler = 
        Executors.newSingleThreadScheduledExecutor();
    
    @PostConstruct
    public void start() {
        // 定时扫描
        scheduler.scheduleAtFixedRate(this::scan, 0, 100, TimeUnit.MILLISECONDS);
    }
    
    public void submit(Runnable task, long delayMs) {
        long executeAt = System.currentTimeMillis() + delayMs;
        queue.offer(new DelayedTask(task, executeAt));
    }
    
    private void scan() {
        long now = System.currentTimeMillis();
        while (true) {
            DelayedTask task = queue.peek();
            if (task == null || task.getExecuteAt() > now) break;
            
            queue.poll();
            task.getTask().run();
        }
    }
}

// 使用
delayQueue.submit(() -> {
    System.out.println("Executed at: " + System.currentTimeMillis());
}, 5000);  // 5 秒后执行
```

**缺点**：
- ❌ 单机
- ❌ 进程崩溃丢失任务

## 🔧 方案 2：MySQL 定时扫描

### 思想

```
消息入 MySQL 表（status='PENDING', execute_at <= now()）
定时器扫描并执行
```

### 表设计

```sql
CREATE TABLE delay_messages (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    topic VARCHAR(255) NOT NULL,
    key_name VARCHAR(255),
    payload TEXT NOT NULL,
    execute_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',  -- PENDING / DONE / FAILED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status_execute (status, execute_at)
);
```

### 代码实现

```java
@Service
public class MySQLDelayQueue {
    
    @Autowired
    private DelayMessageRepository repository;
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    // 提交延迟消息
    public void submit(String topic, String key, String payload, long delayMs) {
        DelayMessage msg = new DelayMessage();
        msg.setTopic(topic);
        msg.setKeyName(key);
        msg.setPayload(payload);
        msg.setExecuteAt(new Date(System.currentTimeMillis() + delayMs));
        msg.setStatus("PENDING");
        repository.save(msg);
    }
    
    // 定时扫描执行
    @Scheduled(fixedRate = 1000)
    public void scan() {
        Date now = new Date();
        List<DelayMessage> dueMessages = repository.findByStatusAndExecuteAtBefore(
            "PENDING", now);
        
        for (DelayMessage msg : dueMessages) {
            // 1. 标记为已处理（乐观锁防止重复执行）
            msg.setStatus("DONE");
            int updated = repository.updateStatusWithOptimisticLock(msg.getId(), "PENDING", "DONE");
            
            if (updated > 0) {
                // 2. 发送到 Kafka
                kafkaTemplate.send(msg.getTopic(), msg.getKeyName(), msg.getPayload())
                    .whenComplete((result, ex) -> {
                        if (ex != null) {
                            log.error("Send failed: {}", msg.getId(), ex);
                            // 失败回滚（可选重试）
                            msg.setStatus("PENDING");
                            repository.save(msg);
                        }
                    });
            }
        }
    }
}
```

**优缺点**：
- ✅ 持久化（重启不丢失）
- ✅ 简单
- ❌ 数据库轮询开销
- ❌ 精度差（秒级）

## 🔧 方案 3：Redis ZSet 模式（推荐）

### 思想

```
消息存入 Redis ZSet
  - Score = 执行时间戳
  - Member = 消息内容（JSON）

定时扫描 ZSet
  - ZRANGEBYSCORE 0 now
  - 取出到期的消息
  - 发送到 Kafka
```

### 代码实现

```java
@Service
public class RedisDelayQueue {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    // 提交延迟消息
    public void submit(String topic, String key, String payload, long delayMs) {
        long executeAt = System.currentTimeMillis() + delayMs;
        String member = String.format("%s:%s:%s", topic, key, payload);
        
        redisTemplate.opsForZSet().add(
            "delay:queue",
            member,
            executeAt
        );
    }
    
    // 定时扫描执行
    @Scheduled(fixedRate = 100)
    public void scan() {
        long now = System.currentTimeMillis();
        
        // Lua 脚本：原子取出到期消息（避免并发问题）
        String lua = "local tasks = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1], 'LIMIT', 0, 10) " +
                     "if #tasks > 0 then " +
                     "  for i, task in ipairs(tasks) do " +
                     "    redis.call('ZREM', KEYS[1], task) " +
                     "  end " +
                     "  return tasks " +
                     "else " +
                     "  return {} " +
                     "end";
        
        DefaultRedisScript<List> script = new DefaultRedisScript<>(lua, List.class);
        List<String> tasks = redisTemplate.execute(script, 
            Arrays.asList("delay:queue"), 
            String.valueOf(now));
        
        for (String task : tasks) {
            // 解析任务并发送到 Kafka
            String[] parts = task.split(":", 3);
            String topic = parts[0];
            String key = parts[1];
            String payload = parts[2];
            
            kafkaTemplate.send(topic, key, payload);
        }
    }
}
```

**优缺点**：
- ✅ 高性能（Redis 内存）
- ✅ 精度高（毫秒级）
- ✅ 持久化（AOF / RDB）
- ⚠️ 依赖 Redis

## 🔧 方案 4：多层 Topic 模式

### 思想

```
创建多个延迟层级的 Topic：
  - delay.5s  （5 秒延迟）
  - delay.1m  （1 分钟延迟）
  - delay.10m （10 分钟延迟）
  - delay.1h  （1 小时延迟）

消息发到对应层级的 Topic
Consumer 等待层级对应的时间后再发送到目标 Topic
```

### 实现

```java
// 1. 预创建延迟 Topic
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic delay.5s --partitions 3 --replication-factor 2
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic delay.1m --partitions 3 --replication-factor 2

// 2. Producer：发送到对应延迟 Topic
@Service
public class DelayProducer {
    
    public void sendWithDelay(String targetTopic, String key, String payload, long delayMs) {
        String delayTopic = selectDelayTopic(delayMs);
        
        kafkaTemplate.send(delayTopic, key, payload)
            .whenComplete((result, ex) -> {
                if (ex == null) log.info("Sent to delay topic: {}", delayTopic);
            });
    }
    
    private String selectDelayTopic(long delayMs) {
        if (delayMs <= 5_000) return "delay.5s";
        if (delayMs <= 60_000) return "delay.1m";
        if (delayMs <= 600_000) return "delay.10m";
        return "delay.1h";
    }
}

// 3. Consumer：每个延迟 Topic 一个 Consumer，等待对应时间后转发
@Service
public class DelayForwarder {
    
    @KafkaListener(topics = "delay.5s", groupId = "delay-forwarder")
    public void forward5s(Message<String> message) {
        try { Thread.sleep(5_000); } catch (InterruptedException e) {}
        kafkaTemplate.send(extractTarget(message), message.getKey(), message.getPayload());
    }
    
    @KafkaListener(topics = "delay.1m", groupId = "delay-forwarder")
    public void forward1m(Message<String> message) {
        try { Thread.sleep(60_000); } catch (InterruptedException e) {}
        kafkaTemplate.send(extractTarget(message), message.getKey(), message.getPayload());
    }
    
    private String extractTarget(Message<String> message) {
        // 从 header 读取目标 topic
        return new String(message.getHeaders().get("X-Target-Topic"));
    }
}

// 4. 发送时设置目标 topic 到 header
kafkaTemplate.send(MessageBuilder.withPayload(payload)
    .setHeader(KafkaHeaders.TOPIC, "delay.5s")
    .setHeader("X-Target-Topic", "orders")
    .build());
```

**优缺点**：
- ✅ 简单
- ✅ 不依赖外部存储
- ❌ 精度受层级限制（5s、1m、10m）
- ❌ Consumer 需要 sleep（占用连接）

## 🔧 方案 5：Kafka Stream 实现（高级）

```java
// 使用 Kafka Streams 处理延迟消息
StreamsBuilder builder = new StreamsBuilder();

KStream<String, OrderEvent> source = builder.stream("orders");
KStream<String, OrderEvent> delayed = source
    .transform(() -> new DelayTransformer(Duration.ofMinutes(30)));  // 延迟 30 分钟

delayed.to("delayed-orders");
```

**优缺点**：
- ✅ Kafka 官方方案
- ✅ 精确延迟
- ❌ 需要 Kafka Streams 集群
- ❌ 复杂

## 🛠️ 实战：订单超时关闭（Redis ZSet 方案）

```java
@Service
public class OrderTimeoutScheduler {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    @Autowired
    private OrderRepository orderRepository;
    
    // 创建订单时：30 分钟后关闭
    public void scheduleOrderTimeout(String orderId) {
        long executeAt = System.currentTimeMillis() + 30 * 60 * 1000;
        
        String task = String.format("timeout:%s:%s", orderId, orderId);
        redisTemplate.opsForZSet().add("order-timeout-queue", task, executeAt);
    }
    
    // 支付成功：取消延迟任务
    public void cancelOrderTimeout(String orderId) {
        String task = "timeout:" + orderId + ":" + orderId;
        redisTemplate.opsForZSet().remove("order-timeout-queue", task);
    }
    
    // 定时扫描：每秒一次
    @Scheduled(fixedRate = 1000)
    public void scanTimeouts() {
        long now = System.currentTimeMillis();
        long limit = now;
        
        // 取出到期任务（Lua 原子）
        String lua = "local tasks = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1], 'LIMIT', 0, 100) " +
                     "if #tasks > 0 then " +
                     "  for i, task in ipairs(tasks) do " +
                     "    redis.call('ZREM', KEYS[1], task) " +
                     "  end " +
                     "  return tasks " +
                     "end " +
                     "return {}";
        
        DefaultRedisScript<List> script = new DefaultRedisScript<>(lua, List.class);
        List<String> tasks = redisTemplate.execute(script,
            Collections.singletonList("order-timeout-queue"),
            String.valueOf(limit));
        
        for (String task : tasks) {
            // 解析：timeout:orderId:orderId
            String orderId = task.split(":")[1];
            
            // 检查订单状态（避免重复关闭）
            Order order = orderRepository.findById(orderId).orElse(null);
            if (order != null && "PENDING".equals(order.getStatus())) {
                // 发送关闭事件到 Kafka
                OrderEvent event = new OrderEvent();
                event.setOrderId(orderId);
                event.setStatus("CLOSED_TIMEOUT");
                kafkaTemplate.send("order-events", orderId, event);
            }
        }
    }
}
```

## 🔧 方案选型

```
✅ 小数据量 + 简单：内存版
✅ 中等数据量 + 简单：MySQL 轮询
✅ 高性能 + 实时：Redis ZSet（推荐）
✅ 精确延迟 + 高可用：Kafka Streams
⚠️ 多层级精度：多层 Topic
```

| 方案 | 精度 | 性能 | 可靠性 | 复杂度 |
|------|------|------|--------|--------|
| 内存版 | ms | 高 | ❌ | 低 |
| MySQL | s | 中 | ✅ | 中 |
| Redis ZSet | ms | 高 | ✅ | 中 |
| 多层 Topic | s | 中 | ✅ | 中 |
| Kafka Streams | ms | 高 | ✅✅ | 高 |

## ⚠️ 常见问题

### 问题 1：延迟精度不够

```
场景：要求毫秒级精度，MySQL 轮询 1 秒
解决：
  1. 减小轮询间隔（CPU 消耗）
  2. 改用 Redis ZSet（毫秒级）
  3. 改用 Kafka Streams
```

### 问题 2：消息堆积

```
场景：高频延迟消息，扫描速度跟不上
解决：
  1. 增加扫描线程
  2. 优化 Lua 脚本
  3. 限制每个 topic 的延迟消息数
```

### 问题 3：Redis 故障

```
场景：Redis 故障导致延迟消息丢失
解决：
  1. Redis 持久化（AOF + RDB）
  2. 多 Redis 实例（主从 / Sentinel）
  3. Redis 故障降级（直接执行）
```

## 🎯 总结

**延迟消息核心要点**：
- ✅ Kafka 不直接支持延迟消息
- ✅ Redis ZSet 是推荐方案（高性能 + 持久化）
- ✅ 多层 Topic 简单但精度受限
- ✅ Kafka Streams 适合复杂场景
- ✅ 业务幂等是基础
- ⚠️ 延迟消息可能丢失（需持久化）
- ⚠️ 延迟精度 vs 性能 trade-off

**下一步：** [☠️ 死信队列](/08-enterprise/dead-letter) — 失败消息处理
