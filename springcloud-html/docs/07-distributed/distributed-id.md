---
title: 分布式 ID
---

# 🆔 分布式 ID

> 在分布式系统中生成**全局唯一**的 ID。

## 🎯 为什么需要分布式 ID？

**单机 DB** 用自增主键即可，**分布式场景**下：

| 场景 | 单机自增 ID 问题 |
|---|---|
| **分库分表** | 每个库独立自增，跨库 ID 冲突 |
| **高并发写入** | 单点性能瓶颈 |
| **数据合并** | 不同库数据合并时 ID 冲突 |
| **分布式追踪** | 需要趋势递增的 ID |

**分布式 ID 要求：**
- **全局唯一**：不同节点不同时间生成的 ID 不重复
- **高性能**：每秒生成上万 ID
- **高可用**：ID 生成服务不能挂
- **趋势递增**（可选）：方便 B+ 树索引排序

## 🛠️ 主流方案

### 1. UUID

```java
String id = UUID.randomUUID().toString();
// 550e8400-e29b-41d4-a716-446655440000
```

| 优点 | 缺点 |
|---|---|
| 本地生成，无网络调用 | **36 字符**，存储空间大 |
| 全球唯一（概率）| **无序**，B+ 树频繁分裂 |
| 实现简单 | 不适合做 DB 主键 |

### 2. 数据库自增 + 步长

```sql
-- 库 A
SET @@auto_increment_offset = 1;
SET @@auto_increment_increment = 2;
-- 生成 1, 3, 5, 7...

-- 库 B
SET @@auto_increment_offset = 2;
SET @@auto_increment_increment = 2;
-- 生成 2, 4, 6, 8...
```

| 优点 | 缺点 |
|---|---|
| 简单 | 扩容麻烦（步长需调整） |
| 单调递增 | 单点 DB 故障 |

### 3. 号段模式（Segment）

**原理：** 一次性从 DB 拿一段 ID 范围（如 1-1000），用完后异步拿下一段

```sql
CREATE TABLE id_generator (
    id INT PRIMARY KEY AUTO_INCREMENT,
    biz_type VARCHAR(64) UNIQUE,
    max_id BIGINT,
    step INT,
    version BIGINT
);
```

```java
// 美团 Leaf / 滴滴 TinyId 实现
public long nextId(String bizType) {
    Segment segment = cache.get(bizType);
    if (segment == null || !segment.hasNext()) {
        segment = loadSegmentFromDB(bizType);  // 加载下一段
        cache.put(bizType, segment);
    }
    return segment.next();
}
```

| 优点 | 缺点 |
|---|---|
| 高性能（本地）| DB 仍是单点 |
| 趋势递增 | 号段用完有延迟 |
| 可监控 | 需额外维护 |

### 4. Snowflake（雪花算法）

**Twitter 开源，64 位 Long 型 ID**

```
0 | 0000000 00000000 00000000 00000000 0 | 00000 | 00000 | 00000000 00000000 00000000
^                                  ^         ^         ^                          ^
符号位(1)                     时间戳(41)   数据中心(5) 机器ID(5)              序列号(12)
```

| 位数 | 用途 |
|---|---|
| 1 bit | 符号位（始终为 0）|
| 41 bit | 时间戳（毫秒，约可用 69 年）|
| 5 bit | 数据中心 ID（32 个）|
| 5 bit | 机器 ID（32 个）|
| 12 bit | 序列号（每毫秒 4096 个）|

**单机峰值：4096 × 1000 = 400 万/秒**

```java
public class SnowflakeIdWorker {
    private final long twepoch = 1288834974657L;
    private final long workerIdBits = 5L;
    private final long datacenterIdBits = 5L;
    private final long sequenceBits = 12L;
    // ...

    public synchronized long nextId() {
        long timestamp = timeGen();
        if (timestamp < lastTimestamp) {
            throw new RuntimeException("时钟回拨");
        }
        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & sequenceMask;
            if (sequence == 0) timestamp = tilNextMillis();
        } else {
            sequence = 0L;
        }
        lastTimestamp = timestamp;
        return ((timestamp - twepoch) << timestampLeftShift)
             | (datacenterId << datacenterIdShift)
             | (workerId << workerIdShift)
             | sequence;
    }
}
```

**问题与解决方案：**

| 问题 | 原因 | 解决方案 |
|---|---|---|
| **时钟回拨** | 系统时间被回退（NTP 校准）| 等待时间追上 / 拒绝生成 / 备用 ID |
| **workerId 分配** | 多节点启动需要分配 | ZooKeeper / Redis / 数据库分配 |
| **并发上限** | 单机 400 万/秒 | 调整 workerId 范围 / 多实例 |

### 5. Redis INCR

```bash
INCR order:id
```

**结合业务前缀：**
```bash
INCR order:id:20260101    # 每日一个 key，避免超长
```

| 优点 | 缺点 |
|---|---|
| 高性能 | Redis 持久化问题 |
| 单调递增 | 网络开销 |

### 6. Leaf（美团）

**Leaf-Snowflake**：Snowflake + ZooKeeper 分配 workerId

**Leaf-Segment**：号段模式 + 异步加载

### 7. TinyID（滴滴）

基于号段模式 + 多 DB 支持

## 📊 方案对比

| 方案 | 长度 | 有序 | 性能 | 依赖 | 适用 |
|---|---|---|---|---|---|
| UUID | 36 字符 | ❌ | ⭐⭐⭐⭐⭐ | 无 | 不适合 DB 主键 |
| DB 自增 | 8 字节 | ✅ | ⭐⭐ | DB | 单机 / 分库分表 |
| 号段模式 | 8 字节 | ✅ | ⭐⭐⭐⭐⭐ | DB + 缓存 | 通用（推荐）|
| Snowflake | 8 字节 | ✅ | ⭐⭐⭐⭐⭐ | ZooKeeper | 高并发（推荐）|
| Redis INCR | 8 字节 | ✅ | ⭐⭐⭐⭐ | Redis | 中小规模 |
| UUIDv7 | 36 字符 | ✅（时间排序）| ⭐⭐⭐⭐⭐ | 无 | 新兴方案 |

## 🎯 选型建议

```
                       业务规模？
                          │
              ┌───────────┴────────────┐
            小/中型                  大型
              │                       │
           数据合并？             是否需趋势递增？
              │                       │
        ┌─────┴─────┐         ┌──────┴──────┐
       是          否         是           否
        │           │          │            │
    UUIDv7       Snowflake   Snowflake    UUID
                                    │
                              时钟回拨敏感？
                              │
                          ┌───┴───┐
                          是      否
                          │       │
                       Leaf      简易
                       Snowflake Snowflake
```

## 🛠️ 实战：集成 Hutool / MyBatis-Plus

### Hutool Snowflake

```java
// 1. 配置 workerId（从配置中心 / DB 加载）
long workerId = 1;
long datacenterId = 1;

// 2. 创建生成器
Snowflake snowflake = new Snowflake(workerId, datacenterId);

// 3. 生成 ID
long id = snowflake.nextId();
```

### MyBatis-Plus

```java
// MyBatis-Plus 内置多种 IdType
@TableId(type = IdType.ASSIGN_ID)  // 雪花算法
private Long id;

@TableId(type = IdType.AUTO)       // DB 自增
private Long id;
```

### Leaf 集成示例

```yaml
# leaf.properties
leaf.name=order-leaf
leaf.segment.enable=true
leaf.jdbc.url=jdbc:mysql://127.0.0.1:3306/leaf
leaf.jdbc.username=root
leaf.jdbc.password=xxx
```

```java
SnowflakeService service = new SnowflakeService();
service.init();
long id = service.getId("order");
```

## ⚠️ 常见坑

### 1. 时钟回拨

```java
// Snowflake 中抛异常
if (timestamp < lastTimestamp) {
    throw new RuntimeException("时钟回拨，拒绝生成");
}
```

**生产环境处理：** 关闭 NTP 自动同步 / 使用备用 ID 生成器（Leaf Snowflake 自动切换）

### 2. workerId 冲突

两台机器 workerId 配置相同 → 生成的 ID 冲突

**解决：** 用 ZooKeeper 持久顺序节点分配 workerId

### 3. ID 泄露业务量

`Snowflake ID` 含时间戳，前端拿到后可推算业务量（如某日订单数）

**解决：** 自定义位分配 / 加密处理

### 4. 数据库主键越界

MySQL `BIGINT` 最大 2^63-1，使用 Snowflake 注意不要超过

**计算：2^63-1 = 9223372036854775807（足够使用几百年）**

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| 雪花算法原理？| 64 位：1 符号 + 41 时间戳 + 5 数据中心 + 5 机器 + 12 序列号 |
| 雪花算法问题？| 时钟回拨、workerId 分配 |
| 分布式 ID 方案？| UUID / DB 自增 / 号段 / Snowflake / Redis / Leaf / TinyID |
| 为什么不用 UUID？| 36 字符大、不是递增、索引效率低 |

---

- 上一章：[💰 分布式事务](/07-distributed/distributed-transaction)
- 下一章：[💬 分布式消息](/07-distributed/distributed-mq)