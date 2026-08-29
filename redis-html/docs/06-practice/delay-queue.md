---
title: 延迟队列
---

# ⏰ 延迟队列

> **延迟队列（Delay Queue）**用于在指定时间后执行任务。Redis 提供基于 **ZSet** 的轻量级延迟队列方案。

## 🎯 应用场景

```
✅ 订单超时关闭（30 分钟未支付）
✅ 优惠券过期（24 小时未使用）
✅ 定时提醒（会议 10 分钟前提醒）
✅ 异步重试（失败任务 5 分钟后重试）
✅ 短信验证码（5 分钟失效）
```

## 🛠️ 方案：基于 ZSet 的延迟队列

> **核心思路**：用 ZSet 的 score 存任务执行时间戳，到期则取出执行。

### 数据结构

```
ZSet key:  delay:queue
Score:     执行时间戳（毫秒）
Member:    任务 JSON（包含任务 ID + payload）

示例：
  ZADD delay:queue 1698000060000 "{taskId:'t1', payload:'order:1001'}"
  ZADD delay:queue 1698000120000 "{taskId:'t2', payload:'order:1002'}"
```

### 完整实现

```java
@Service
public class DelayQueueService {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    private static final String DELAY_QUEUE = "delay:queue";
    
    // 1. 添加延迟任务
    public void addTask(String taskId, Object payload, long delayMs) {
        long executeTime = System.currentTimeMillis() + delayMs;
        String json = JSON.toJSONString(Map.of(
            "taskId", taskId,
            "payload", payload,
            "executeTime", executeTime
        ));
        
        redisTemplate.opsForZSet().add(DELAY_QUEUE, json, executeTime);
    }
    
    // 2. 取出到期任务（消费）
    public Task pollTask() {
        long now = System.currentTimeMillis();
        
        // Lua 脚本：原子取出到期任务
        String lua = "local tasks = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1], 'LIMIT', 0, 10) " +
                     "if #tasks > 0 then " +
                     "  redis.call('ZREM', KEYS[1], tasks[1]) " +
                     "  return tasks[1] " +
                     "else " +
                     "  return '' " +
                     "end";
        
        DefaultRedisScript<String> script = new DefaultRedisScript<>(lua, String.class);
        String json = redisTemplate.execute(script, Arrays.asList(DELAY_QUEUE), String.valueOf(now));
        
        if (json == null || json.isEmpty()) {
            return null;
        }
        
        return JSON.parseObject(json, Task.class);
    }
}
```

### 消费循环

```java
@Component
public class DelayQueueConsumer {
    
    @Autowired
    private DelayQueueService delayQueueService;
    
    @Autowired
    private OrderService orderService;
    
    // 每秒轮询一次
    @Scheduled(fixedDelay = 1000)
    public void consume() {
        Task task = delayQueueService.pollTask();
        if (task == null) return;
        
        try {
            switch (task.getType()) {
                case "ORDER_TIMEOUT":
                    orderService.closeOrder(task.getTaskId());
                    break;
                case "SEND_REMINDER":
                    notifyService.sendReminder(task.getTaskId());
                    break;
                // ...
            }
        } catch (Exception e) {
            log.error("Process task failed: {}", task.getTaskId(), e);
            // 失败重试：重新加入延迟队列（指数退避）
            delayQueueService.addTask(task.getTaskId(), task.getPayload(), 60_000);
        }
    }
}
```

## 🛠️ 实战：订单超时关闭

```java
@Service
public class OrderService {
    
    @Autowired
    private DelayQueueService delayQueue;
    
    // 创建订单（30 分钟未支付则关闭）
    public Order createOrder(OrderDTO dto) {
        Order order = new Order();
        order.setStatus("PENDING_PAYMENT");
        orderMapper.insert(order);
        
        // 加入延迟队列（30 分钟后执行）
        delayQueue.addTask(
            "order:" + order.getId(),
            Map.of("orderId", order.getId()),
            30 * 60 * 1000  // 30 分钟
        );
        
        return order;
    }
    
    // 支付订单（取消延迟任务）
    public void payOrder(String orderId) {
        orderMapper.updateStatus(orderId, "PAID");
        
        // 从延迟队列移除（避免重复关闭）
        redisTemplate.opsForZSet().remove(DELAY_QUEUE, "order:" + orderId);
    }
    
    // 消费者调用：关闭超时订单
    public void closeOrder(String taskId) {
        String orderId = taskId.replace("order:", "");
        Order order = orderMapper.findById(orderId);
        
        if (order == null || !"PENDING_PAYMENT".equals(order.getStatus())) {
            return;
        }
        
        // 关闭订单
        orderMapper.updateStatus(orderId, "CLOSED_TIMEOUT");
        // 释放库存
        stockService.unfreeze(orderId);
    }
}
```

## 🛠️ 进阶：多个延迟级别

```
需求：1 分钟、5 分钟、10 分钟、1 小时等多种延迟级别

方案：每个级别一个 ZSet
  delay:queue:1min
  delay:queue:5min
  delay:queue:10min
  delay:queue:1hour

或：使用 score = executeTime，多个级别共享一个 ZSet
```

## ⚙️ 高级特性

### 1. 任务幂等性

```java
// 业务侧保证幂等
public void closeOrder(String orderId) {
    Order order = orderMapper.findById(orderId);
    if (order == null) return;
    if (!"PENDING_PAYMENT".equals(order.getStatus())) return;  // 幂等检查
    
    orderMapper.updateStatus(orderId, "CLOSED_TIMEOUT");
}
```

### 2. 失败重试（指数退避）

```java
// 重试 3 次，每次间隔翻倍
public void retry(String taskId, int retryCount, Object payload) {
    long delay = (long) (60_000 * Math.pow(2, retryCount));  // 1min, 2min, 4min
    
    if (retryCount >= 3) {
        log.error("Task failed 3 times: {}", taskId);
        // 死信队列处理
        deadLetterQueue.add(taskId, payload);
        return;
    }
    
    delayQueue.addTask(taskId, payload, delay);
}
```

### 3. 死信队列

```java
// 任务失败 3 次后进入死信队列
// 运维人员手动处理
public static final String DEAD_LETTER = "delay:queue:dead";

public void addToDeadLetter(String taskId, Object payload) {
    String json = JSON.toJSONString(Map.of(
        "taskId", taskId,
        "payload", payload,
        "deadTime", System.currentTimeMillis()
    ));
    redisTemplate.opsForList().leftPush(DEAD_LETTER, json);
}
```

## 📊 延迟队列方案对比

| 方案 | 精度 | 性能 | 复杂度 | 适用场景 |
|------|------|------|--------|---------|
| **Redis ZSet** | 秒级 | 高 | 低 | 多数业务 |
| **RabbitMQ Delayed Message** | 毫秒级 | 中 | 中 | RabbitMQ 用户 |
| **RocketMQ 延迟消息** | 毫秒级 | 高 | 中 | RocketMQ 用户 |
| **JDK DelayQueue** | 毫秒级 | 极高 | 低 | 单机应用 |
| **Quartz 定时任务** | 秒级 | 中 | 高 | 复杂调度 |

## ⚠️ 常见问题

### 问题 1：空轮询浪费 CPU

```
场景：队列为空，pollTask() 每秒调用，Redis 压力大
解决：
  1. 用 BLPOP 阻塞（如果有）
  2. 间隔动态调整（空时延长到 5 秒）
  3. 用 Redis Stream 替代（支持阻塞）
```

### 问题 2：集群消费不均衡

```
场景：3 个消费节点都取任务，可能不均
解决：
  1. 用 Redis Stream 消费者组（自动分配）
  2. 用一致性 Hash 分配任务
```

### 问题 3：ZSet 内存占用

```
场景：百万级延迟任务，占用内存
解决：
  1. 定期清理（任务完成后立即 ZREM）
  2. 设置 expire（用 ZSet 的过期机制）
```

## 🛠️ 改进：基于 Stream 的延迟队列

```java
// 用 Stream 实现延迟队列（更强大的特性）
@Service
public class StreamDelayQueue {
    
    private static final String STREAM = "stream:delay:order";
    private static final String GROUP = "delay-group";
    
    // 1. 添加延迟任务
    public void addTask(String taskId, long delayMs) {
        long executeTime = System.currentTimeMillis() + delayMs;
        Map<String, String> data = Map.of(
            "taskId", taskId,
            "executeTime", String.valueOf(executeTime)
        );
        redisTemplate.opsForStream().add(STREAM, data);
    }
    
    // 2. 消费任务（延迟到时间才 ACK 接收）
    public void consume() {
        List<MapRecord<String, Object, Object>> records = redisTemplate.opsForStream()
            .read(
                Consumer.from(GROUP, "consumer1"),
                StreamReadOptions.empty().count(10).block(Duration.ofSeconds(1)),
                StreamOffset.create(STREAM, ReadOffset.lastConsumed())
            );
        
        for (MapRecord<String, Object, Object> record : records) {
            long executeTime = Long.parseLong((String) record.getValue().get("executeTime"));
            long now = System.currentTimeMillis();
            
            if (executeTime <= now) {
                // 时间到，执行任务
                processTask(record);
            } else {
                // 时间未到，放回 PEL（让其他消费者处理）
                // 或 sleep 后再处理
                try {
                    Thread.sleep(executeTime - now);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                processTask(record);
            }
            
            redisTemplate.opsForStream().acknowledge(STREAM, GROUP, record.getId());
        }
    }
}
```

## 🎯 总结

**延迟队列核心要点**：
- ✅ ZSet score 存执行时间戳
- ✅ ZRANGEBYSCORE 取出到期任务
- ✅ ZREM 原子删除（Lua 脚本）
- ✅ 业务幂等性 + 失败重试
- ✅ 死信队列兜底
- ⚠️ Redis Stream 提供更强大的方案

**下一步：** [🏆 排行榜](/06-practice/leaderboard) — ZSet 实现排行榜

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
