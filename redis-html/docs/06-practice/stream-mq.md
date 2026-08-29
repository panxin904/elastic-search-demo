---
title: Stream 消息队列
date: 2026-08-15  # date-auto-injected
---

# 📨 Stream 消息队列

> **Redis Stream**是 Redis 5.0 引入的**消息队列数据结构**，支持**消费者组**、**消息确认**、**消息回溯**等高级特性，是 Redis 作为轻量级 MQ 的核心方案。

## 🎯 Stream vs 其他 MQ 方案

| 维度 | Pub/Sub | List | Stream |
|------|---------|------|--------|
| **消息持久化** | ❌ 不持久 | ✅ 部分 | ✅ 持久 |
| **消费者组** | ❌ | ❌ | ✅ |
| **消息确认** | ❌ | ❌ | ✅ |
| **消息回溯** | ❌ | ❌ | ✅ |
| **多消费者** | ⚠️ 全部收到 | ⚠️ 抢消费 | ✅ 各自消费一部分 |
| **适用场景** | 实时通知 | 简单队列 | 轻量级 MQ |

## 📝 Stream 核心命令

### 生产消息

```bash
# XADD：追加消息
XADD stream:order * userId 1001 amount 99.9
# 返回消息 ID：1698000000000-0
# * = 自动生成 ID（毫秒时间戳 + 序列号）

# 字段是 key-value 对
XADD stream:order * type "create" userId 1001 timestamp 1698000000
```

### 消费消息

```bash
# XLEN：消息总数
XLEN stream:order

# XRANGE：按 ID 范围读取
XRANGE stream:order - +               # 所有消息
XRANGE stream:order 1698000000000-0 1698000000999-0 COUNT 10
# - 和 + 表示最小/最大 ID

# XREVRANGE：反向读取
XREVRANGE stream:order + - COUNT 10   # 最新 10 条

# XREAD：阻塞式读取（类似 XREADGROUP，但不分组）
XREAD COUNT 10 BLOCK 5000 STREAMS stream:order $
# $ 表示从最新位置开始读
```

## 🛠️ 消费者组（核心特性）

> **消费者组（Consumer Group）**允许多个消费者协同消费，每个消息只会被组内的一个消费者处理。

### 创建消费者组

```bash
# 创建消费者组（从 ID 0 开始消费所有历史消息）
XGROUP CREATE stream:order group1 $ MKSTREAM
# $ = 只消费新消息
# 0 = 从头消费
# MKSTREAM = 流不存在则创建

# 查看消费者组
XINFO GROUPS stream:order
```

### 消费消息

```bash
# XREADGROUP：消费者组读取
XREADGROUP GROUP group1 consumer1 COUNT 10 BLOCK 5000 STREAMS stream:order >
# > 表示未消费的消息（next message）
```

### 确认消息

```bash
# XACK：确认消息已处理（关键！）
XACK stream:order group1 1698000000000-0
# 未确认的消息会被保留到 PEL（Pending Entry List）

# 查看 PEL
XPENDING stream:order group1

# 查看 PEL 详情
XPENDING stream:order group1 - + 10
```

### 消费者组工作流程

```
1. 消息进入 stream:order
2. XREADGROUP 读取（标记为 unack）
3. 消费者处理消息
4. XACK 确认（消息从 PEL 移除）
5. 消费者异常崩溃 → PEL 保留 → 重新分配
```

## 📋 完整示例

```bash
# 1. 创建流和消费者组
XGROUP CREATE stream:order group1 $ MKSTREAM

# 2. 生产消息
XADD stream:order * orderId 1001 amount 99.9
XADD stream:order * orderId 1002 amount 88.8

# 3. consumer1 消费
XREADGROUP GROUP group1 consumer1 COUNT 1 STREAMS stream:order >
# 返回：orderId 1001 ...

# 4. consumer2 消费
XREADGROUP GROUP group1 consumer2 COUNT 1 STREAMS stream:order >
# 返回：orderId 1002 ...

# 5. 确认消息
XACK stream:order group1 1698000000000-0
XACK stream:order group1 1698000000001-0

# 6. consumer1 崩溃后，重新读取 PEL
XREADGROUP GROUP group1 consumer1 COUNT 10 STREAMS stream:order 0
# 0 表示从 PEL 读取已读未确认的消息
```

## 🚨 故障转移

```
场景：consumer1 崩溃，PEL 中有 1000 条未确认消息

故障转移流程：
  1. XCLAIM 转移 PEL 到 consumer2
     XCLAIM stream:order group1 consumer2 60000 1698000000000-0
     # 60000 = 最小空闲时间（毫秒）

  2. 或自动转移：
     XAUTOCLAIM stream:order group1 consumer2 60000 0
     # Redis 7.0+ 自动转移 PEL
```

## 🛠️ Spring Boot 实战

```java
@Service
public class StreamService {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    private static final String STREAM = "stream:order";
    private static final String GROUP = "group1";
    
    // 1. 生产消息
    public String produce(String type, Map<String, String> data) {
        Map<String, String> message = new HashMap<>();
        message.put("type", type);
        message.putAll(data);
        
        RecordId id = redisTemplate.opsForStream().add(STREAM, message);
        return id.getValue();
    }
    
    // 2. 创建消费者组
    public void createGroup() {
        try {
            redisTemplate.opsForStream().createGroup(STREAM, ReadOffset.from("0"), GROUP);
        } catch (RedisSystemException e) {
            // 组已存在
        }
    }
    
    // 3. 消费消息
    @Scheduled(fixedDelay = 1000)
    public void consume() {
        // 从 group1 / consumer1 读取
        List<MapRecord<String, Object, Object>> records = redisTemplate.opsForStream()
            .read(
                Consumer.from(GROUP, "consumer1"),
                StreamReadOptions.empty().count(10).block(Duration.ofSeconds(5)),
                StreamOffset.create(STREAM, ReadOffset.lastConsumed())
            );
        
        if (records == null) return;
        
        for (MapRecord<String, Object, Object> record : records) {
            try {
                // 业务处理
                processOrder(record);
                
                // 确认消息
                redisTemplate.opsForStream().acknowledge(STREAM, GROUP, record.getId());
            } catch (Exception e) {
                log.error("Process failed", e);
                // 不 ACK，下次重新消费
            }
        }
    }
    
    // 4. 故障转移（PEL 转交）
    public void transferPending(String consumerName) {
        redisTemplate.opsForStream().claim(STREAM, GROUP, 
            Consumer.from(GROUP, consumerName),
            Duration.ofMinutes(1),
            RecordId.of("0-0"));
    }
}
```

## 📊 Stream vs Kafka/RabbitMQ

| 维度 | Redis Stream | Kafka | RabbitMQ |
|------|--------------|-------|----------|
| **性能** | 10w+ msg/s | 100w+ msg/s | 几万 msg/s |
| **持久化** | AOF/RDB | 磁盘 | 磁盘 |
| **运维复杂度** | 低 | 高 | 中 |
| **适合规模** | 轻量级 | 海量数据 | 中等规模 |
| **功能丰富度** | 基础 | 非常丰富 | 丰富 |
| **推荐场景** | 内部消息队列 | 日志、事件流 | 业务消息 |

**选择建议**：
```
✅ 简单 MQ：Redis Stream（已够用）
✅ 海量数据 / 高吞吐：Kafka
✅ 复杂路由 / 死信队列：RabbitMQ
```

## ⚠️ 常见问题

### 问题 1：消息丢失

```
场景：消费者崩溃，消息未确认
解决：
  1. XCLAIM 转交 PEL
  2. 启用 XAUTOCLAIM 自动转移
  3. 监控 PEL 长度
```

### 问题 2：重复消费

```
场景：ACK 失败导致重复消费
解决：
  1. 业务侧幂等
  2. 用消息 ID 去重
  3. 数据库唯一约束
```

### 问题 3：流无限增长

```
场景：消息堆积，占用大量内存
解决：
  1. MAXLEN 限制流长度
     XADD stream:order MAXLEN 1000000 * type "create"
  2. 定期清理历史消息
     XTRIM stream:order MAXLEN 1000000
```

## 🎯 总结

**Stream 核心要点**：
- ✅ Redis 5.0+ 内置消息队列
- ✅ 消费者组 + 消息确认
- ✅ 消息持久化（AOF/RDB）
- ✅ PEL 故障转移
- ⚠️ 性能不如 Kafka
- ⚠️ 不支持复杂路由

**下一步：** [⏰ 延迟队列](/06-practice/delay-queue) — 基于 ZSet 的延迟队列
