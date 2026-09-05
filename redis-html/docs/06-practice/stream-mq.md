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

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis Stream 消费者组</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">XREADGROUP · PEL 机制 · XACK · 消息不丢</text>

  <!-- Stream 内部结构 -->
  <g>
    <text x="60" y="90" font-size="13" font-weight="700" fill="#1e293b">① Stream 数据结构（ID 有序 + 链表）</text>

    <rect class="at-hover-card" x="40" y="105" width="520" height="65" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="55" y="120" width="80" height="35" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="95" y="138" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">1234-0</text>
    <text x="95" y="152" text-anchor="middle" font-size="8" fill="#475569">user:1</text>

    <path d="M 135 137 L 155 137" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="155" y="120" width="80" height="35" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="195" y="138" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">1235-0</text>
    <text x="195" y="152" text-anchor="middle" font-size="8" fill="#475569">order:99</text>

    <path d="M 235 137 L 255 137" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="255" y="120" width="80" height="35" rx="3" fill="#dcfce7" stroke="#10b981" stroke-width="2"/>
    <text x="295" y="138" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">1236-0</text>
    <text x="295" y="152" text-anchor="middle" font-size="8" fill="#475569">pay:done</text>

    <path d="M 335 137 L 355 137" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="355" y="120" width="80" height="35" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="395" y="138" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">1237-0</text>
    <text x="395" y="152" text-anchor="middle" font-size="8" fill="#475569">user:2</text>

    <path d="M 435 137 L 455 137" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="455" y="120" width="100" height="35" rx="3" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
    <text x="505" y="138" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">1238-0 ↑</text>
    <text x="505" y="152" text-anchor="middle" font-size="8" fill="#475569">最新</text>
  </g>

  <!-- 消费者组 -->
  <g>
    <text x="60" y="195" font-size="13" font-weight="700" fill="#1e293b">② 消费者组（group1）· 3 worker 协同消费</text>

    <rect class="at-hover-card" x="40" y="210" width="520" height="115" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <!-- Worker A -->
    <rect class="at-hover-card" x="55" y="225" width="150" height="85" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="130" y="245" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Consumer A</text>
    <text x="130" y="263" text-anchor="middle" font-size="9" fill="#475569">last_delivered:</text>
    <text x="130" y="277" text-anchor="middle" font-size="9" font-family="monospace" fill="#1e293b">1235-0</text>
    <text x="130" y="295" font-size="9" fill="#475569">PEL: [1234-0]</text>

    <!-- Worker B -->
    <rect class="at-hover-card" x="225" y="225" width="150" height="85" rx="4" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="300" y="245" text-anchor="middle" font-size="11" font-weight="700" fill="#065f46">Consumer B</text>
    <text x="300" y="263" text-anchor="middle" font-size="9" fill="#475569">last_delivered:</text>
    <text x="300" y="277" text-anchor="middle" font-size="9" font-family="monospace" fill="#1e293b">1236-0</text>
    <text x="300" y="295" font-size="9" fill="#475569">PEL: []</text>

    <!-- Worker C -->
    <rect class="at-hover-card" x="395" y="225" width="150" height="85" rx="4" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="470" y="245" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">Consumer C</text>
    <text x="470" y="263" text-anchor="middle" font-size="9" fill="#475569">last_delivered:</text>
    <text x="470" y="277" text-anchor="middle" font-size="9" font-family="monospace" fill="#1e293b">1238-0</text>
    <text x="470" y="295" font-size="9" fill="#475569">PEL: [1237-0]</text>
  </g>

  <!-- ACK 流程 -->
  <g>
    <text x="60" y="345" font-size="13" font-weight="700" fill="#1e293b">③ 消息 ACK 生命周期（PEL 机制）</text>

    <rect class="at-hover-card" x="40" y="360" width="520" height="100" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <!-- 步骤 -->
    <rect class="at-hover-card" x="55" y="375" width="115" height="35" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="112" y="392" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">XREADGROUP</text>
    <text x="112" y="406" text-anchor="middle" font-size="8" fill="#475569">→ PEL 加入</text>

    <path d="M 170 392 L 195 392" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="195" y="375" width="115" height="35" rx="3" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="252" y="392" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">业务处理</text>
    <text x="252" y="406" text-anchor="middle" font-size="8" fill="#475569">消费逻辑</text>

    <path d="M 310 392 L 335 392" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="335" y="375" width="115" height="35" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="392" y="392" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">XACK</text>
    <text x="392" y="406" text-anchor="middle" font-size="8" fill="#475569">→ PEL 移除</text>

    <path d="M 450 392 L 475 392" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="475" y="375" width="75" height="35" rx="3" fill="#fee2e2" stroke="#dc2626"/>
    <text x="512" y="392" text-anchor="middle" font-size="10" font-weight="700" fill="#991b1b">crash?</text>
    <text x="512" y="406" text-anchor="middle" font-size="8" fill="#475569">重投</text>

    <text x="60" y="438" font-size="10" fill="#1e293b">PEL = Pending Entries List，记录已读未 ACK，重启后用 XREADGROUP 0 重新投递未确认消息</text>
  </g>
</svg>
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
