---
title: 全局唯一 ID
---

# 🆔 全局唯一 ID

> 在分布式系统中，多个节点需要生成**全局唯一**的 ID（订单号、用户 ID、消息 ID 等）。Redis 是实现高性能全局 ID 的常用方案。

## 🎯 为什么需要全局唯一 ID？

```
场景：
  - 电商订单号（order_id）：唯一、可读、单调递增
  - 用户 ID：唯一、长期有效
  - 消息 ID：唯一、有序、避免冲突

需求：
  ✅ 全局唯一（不重复）
  ✅ 高性能（每秒生成 10 万+）
  ✅ 有序性（部分场景需要）
  ✅ 可读性（运维友好）
  ✅ 占用空间小
```

## 📊 4 种方案对比

| 方案 | 唯一性 | 性能 | 有序性 | 可读性 | 推荐度 |
|------|--------|------|--------|--------|--------|
| **UUID** | ✅ | ⭐⭐⭐⭐⭐ | ❌ 无序 | ❌ 36 字符串 | 一般 |
| **Snowflake** | ✅ | ⭐⭐⭐⭐ | ✅ 趋势递增 | ❌ 18 位数字 | ✅✅ |
| **Redis INCR** | ✅ | ⭐⭐⭐⭐⭐ | ✅ 单调递增 | ✅ 可定制 | ✅✅ |
| **DB auto_increment** | ✅ | ⭐⭐ | ✅ 单调递增 | ✅ | ❌ |

## 📝 方案 1：UUID

```java
// Java 生成 UUID
String uuid = UUID.randomUUID().toString();
// 550e8400-e29b-41d4-a716-446655440000

// 优势
✅ 本地生成，无网络调用
✅ 全球唯一
✅ 实现简单

// 劣势
❌ 36 位字符串，占空间
❌ 无序（不能用作数据库主键，影响 B+Tree 性能）
❌ 不可读
```

**UUID 作为数据库主键的问题**：
- 无序 → B+Tree 频繁页分裂 → 写入性能差
- 长字符串 → 占用更多磁盘和内存
- 无法按时间排序

## ❄️ 方案 2：Snowflake（雪花算法）

> Twitter 开源的分布式 ID 算法，**64 位 long 型**。

### 结构

```
1 bit      41 bits            10 bits        12 bits
符号位      时间戳              机器ID         序列号
|         |                  |            |
0         xxxxxxx...          xxxxxx       xxxxxx
|         |                  |            |
保留      毫秒时间差            1024节点      4096/ms
正数     (69年)              支持集群        每毫秒

最大：1 + 41 + 10 + 12 = 64 位
```

### Java 实现

```java
public class SnowflakeIdGenerator {
    
    // 起始时间戳（2020-01-01）
    private static final long START_TIMESTAMP = 1577836800000L;
    
    // 每部分占用的位数
    private static final long SEQUENCE_BIT = 12;
    private static final long MACHINE_BIT = 10;
    
    // 最大值
    private static final long MAX_SEQUENCE = -1L ^ (-1L << SEQUENCE_BIT);
    private static final long MAX_MACHINE = -1L ^ (-1L << MACHINE_BIT);
    
    // 位移
    private static final long MACHINE_LEFT = SEQUENCE_BIT;
    private static final long TIMESTAMP_LEFT = SEQUENCE_BIT + MACHINE_BIT;
    
    private long machineId;
    private long sequence = 0L;
    private long lastTimestamp = -1L;
    
    public SnowflakeIdGenerator(long machineId) {
        if (machineId > MAX_MACHINE || machineId < 0) {
            throw new IllegalArgumentException("machineId out of range");
        }
        this.machineId = machineId;
    }
    
    public synchronized long nextId() {
        long timestamp = currentTime();
        
        if (timestamp < lastTimestamp) {
            throw new RuntimeException("Clock moved backwards");
        }
        
        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & MAX_SEQUENCE;
            if (sequence == 0) {
                timestamp = waitNextMillis(lastTimestamp);
            }
        } else {
            sequence = 0L;
        }
        
        lastTimestamp = timestamp;
        
        return (timestamp - START_TIMESTAMP) << TIMESTAMP_LEFT
             | machineId << MACHINE_LEFT
             | sequence;
    }
    
    private long waitNextMillis(long lastTimestamp) {
        long timestamp = currentTime();
        while (timestamp <= lastTimestamp) {
            timestamp = currentTime();
        }
        return timestamp;
    }
    
    private long currentTime() {
        return System.currentTimeMillis();
    }
}
```

### 优缺点

```
✅ 优势
  - 64 位 long，数据库主键友好
  - 趋势递增（按时间）
  - 每毫秒 4096 个 ID（单节点）
  - 不依赖外部系统

❌ 劣势
  - 依赖机器时钟（时钟回拨会出问题）
  - 需要分配机器 ID（管理复杂）
  - 单节点故障导致 ID 不连续
```

## ✅ 方案 3：Redis INCR（推荐）

```java
@Service
public class RedisIdGenerator {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    public long nextId(String bizType) {
        // 每天一个 key，过期后重新从 1 开始
        String date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String key = "id:" + bizType + ":" + date;
        
        // INCR 原子递增
        Long id = redisTemplate.opsForValue().increment(key);
        
        // 设置过期时间（首次 INCR 时）
        if (id != null && id == 1) {
            redisTemplate.expire(key, 25, TimeUnit.HOURS);
        }
        
        return id;
    }
    
    // 生成业务 ID（带前缀）
    public String nextOrderId() {
        long id = nextId("order");
        // 格式：业务前缀 + 时间戳 + 序列号
        return "ORD" + System.currentTimeMillis() / 1000 + id;
    }
}
```

### 优势

```
✅ 性能极高（Redis 单线程，INCR 是 O(1)）
✅ 单调递增（可读性好）
✅ 简单易用（无需 Snowflake 复杂的位运算）
✅ 高可用（Redis Sentinel/Cluster 支持）
✅ 可定制业务前缀
```

### 实战：电商订单号

```java
public String generateOrderId() {
    // 格式：yyyyMMddHHmmss + 6 位序列号
    // 示例：20240715143001 + 000001 = 20240715143001000001
    
    String timestamp = LocalDateTime.now().format(
        DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
    String key = "id:order:" + LocalDate.now();
    
    Long seq = redisTemplate.opsForValue().increment(key);
    if (seq != null && seq == 1) {
        redisTemplate.expire(key, 25, TimeUnit.HOURS);
    }
    
    return timestamp + String.format("%06d", seq);
}
```

## 📊 方案 4：DB auto_increment

```sql
CREATE TABLE `id_generator` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `biz_type` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `biz_type` (`biz_type`)
) ENGINE=InnoDB;

INSERT INTO id_generator (biz_type) VALUES ('order');
-- MySQL: ALTER TABLE id_generator AUTO_INCREMENT = 1;

-- 取下一个 ID
START TRANSACTION;
REPLACE INTO id_generator (biz_type) VALUES ('order');
SELECT LAST_INSERT_ID();
COMMIT;
```

### 优缺点

```
✅ 简单稳定
✅ 单调递增
❌ 性能差（每秒最多几千）
❌ 单点故障（可用 MySQL 双主）
```

## 🆚 Redis INCR vs Snowflake

| 维度 | Redis INCR | Snowflake |
|------|------------|-----------|
| 性能 | 10w+ QPS | 50w+ QPS（本地） |
| 单调递增 | ✅ 严格递增 | ⚠️ 趋势递增 |
| 高可用 | ✅ Redis Cluster | ⚠️ 需管理机器 ID |
| 依赖 | Redis | 无 |
| 实现复杂度 | 低 | 高 |
| 跨语言 | ✅ | ⚠️ 需实现 |
| 时钟回拨 | ❌ 不影响 | ⚠️ 有问题 |
| 推荐 | ✅ 多数场景 | 极致性能 |

## 🛠️ 美团 Leaf（开源）

> 美团开源的分布式 ID 生成系统，结合了 **号段模式 + Snowflake**。

```
Leaf-Snowflake：基于 Snowflake + ZooKeeper 管理 workerId
Leaf-号段模式：DB 分配号段，应用内存消费

Leaf 号段模式原理：
  1. 每次从 DB 取一个号段（如 1-1000）
  2. 应用内存中自增分配
  3. 用完后再取下一个号段
  4. DB 压力极小，性能接近本地生成
```

## ⚠️ 常见问题

### 问题 1：Redis INCR 持久化

```
场景：Redis 重启后，INCR 计数是否丢失？
解决：
  - 开启 AOF（appendfsync everysec）
  - 主从切换时可能丢数据（少量）
```

### 问题 2：Snowflake 时钟回拨

```
现象：服务器时钟回拨后，Snowflake 抛异常
解决：
  1. NTP 校时（小幅回拨）
  2. 等待时钟追上（大幅回拨）
  3. 切换到备用节点
```

### 问题 3：跨天/跨月 ID

```
场景：每天 1 个 key，跨天后从 1 开始
解决：在 key 中加入日期
key: id:order:20240715
```

## 🎯 总结

**全局唯一 ID 核心要点**：
- ✅ Redis INCR：简单、高性能、推荐
- ✅ Snowflake：极致性能，但依赖时钟
- ⚠️ UUID：无序，不推荐作 DB 主键
- ❌ DB auto_increment：性能差，不推荐高并发

**下一步：** [🚦 限流](/06-practice/ratelimit) — 接口限流实战
