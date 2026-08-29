---
title: 分布式 ID 生成
date: 2026-08-15  # date-auto-injected
---

# 🆔 分布式 ID 生成

> 分布式系统下，**全局唯一 ID** 是基础。MySQL 自增主键在分库分表下失效，必须用分布式 ID 生成方案。

## 🎯 为什么不用 MySQL 自增？

```
分库分表场景：
- 订单表分 4 库 × 4 表 = 16 个分片
- 每个分片 AUTO_INCREMENT 从 1 开始
- 订单 1：ds0.orders_0（id=1）
- 订单 2：ds1.orders_1（id=1）  ← ID 冲突！
```

**分布式 ID 要求：**
- ✅ **全局唯一**
- ✅ **趋势递增**（MySQL InnoDB 聚簇索引友好）
- ✅ **高性能**（分布式下高并发）
- ✅ **高可用**（不能单点）
- ✅ **信息安全**（避免暴露业务量）

## 📊 主流方案对比

| 方案 | 唯一性 | 趋势递增 | 性能 | 复杂度 | 适用 |
|---|---|---|---|---|---|
| UUID | ✅ | ❌ | 高 | 低 | 不在意顺序 |
| MySQL 自增 | ❌（分库分表） | ✅ | 中 | 低 | 单库 |
| 雪花算法 | ✅ | ✅ | 高 | 中 | **推荐** |
| Leaf（美团） | ✅ | ✅ | 极高 | 中 | 大厂首选 |
| 数据库号段 | ✅ | ✅ | 中 | 低 | 中小厂 |
| Redis INCR | ✅ | ✅ | 中 | 低 | 中小厂 |

## 🚀 方案 1：UUID（最简单）

```java
// Java 自带
String id = UUID.randomUUID().toString();
// 550e8400-e29b-41d4-a716-446655440000

// 去除连字符（节省 4 字节）
String id = UUID.randomUUID().toString().replace("-", "");
// 550e8400e29b41d4a716446655440000

// 优势
// ✅ 实现简单
// ✅ 全局唯一

// 劣势
// ❌ 36 字符过长（二进制存储也占 16 字节）
// ❌ 无序（InnoDB 主键聚集索引需要频繁页分裂）
// ❌ 信息泄露风险（业务量可推测）
```

**MySQL 存储：**
```sql
-- UUID 用 BINARY(16) 存储（16 字节）
id BINARY(16) PRIMARY KEY

-- 不用 VARCHAR(36)（占 36 字节）
```

## 🚀 方案 2：MySQL 自增（不推荐分库分表）

```sql
-- 单库可用
CREATE TABLE orders (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY
);
```

**优点：** 简单  
**缺点：** 分库分表会冲突

**变通：步长**
```sql
-- 库 1：AUTO_INCREMENT=1, INCREMENT=4
-- 库 2：AUTO_INCREMENT=2, INCREMENT=4
-- 库 3：AUTO_INCREMENT=3, INCREMENT=4
-- 库 4：AUTO_INCREMENT=4, INCREMENT=4

-- 库 1：1, 5, 9, 13, ...
-- 库 2：2, 6, 10, 14, ...
```

## 🚀 方案 3：雪花算法（Snowflake）⭐⭐⭐

### 算法原理

```
Snowflake ID = 1 bit 符号位 + 41 bit 时间戳 + 10 bit 工作机器 + 12 bit 序列号
           = 64 bit Long 类型
           = 单机每毫秒 4096 个 ID
           = 69 年不重复
```

```
0 | 0000000 00000000 00000000 00000000 00000000 0 | 00000 | 00000 | 000000000000
  |---------------------时间戳(41)---------------------|----机器(10)----|----序列(12)----|
```

### 1. 引入 Hutool（推荐，简单）

```xml
<dependency>
    <groupId>cn.hutool</groupId>
    <artifactId>hutool-all</artifactId>
    <version>5.8.22</version>
</dependency>
```

```java
// 简单使用
long id = IdUtil.getSnowflake(1, 1).nextId();
// 1, 1 是 workerId 和 datacenterId

// 配置全局
Snowflake snowflake = IdUtil.createSnowflake(1, 1);
long id = snowflake.nextId();
```

### 2. 自定义实现（生产级）

```java
public class SnowflakeIdGenerator {
    
    // 起始时间戳（2020-01-01）
    private static final long START_TIMESTAMP = 1577836800000L;
    
    // 各部分 bit 数
    private static final long SEQUENCE_BIT = 12;
    private static final long MACHINE_BIT = 5;
    private static final long DATACENTER_BIT = 5;
    
    // 最大值
    private static final long MAX_SEQUENCE = ~(-1L << SEQUENCE_BIT);
    private static final long MAX_MACHINE_BIT = ~(-1L << MACHINE_BIT);
    private static final long MAX_DATACENTER_BIT = ~(-1L << DATACENTER_BIT);
    
    // 位移
    private static final long TIMESTAMP_LEFT = SEQUENCE_BIT + MACHINE_BIT + DATACENTER_BIT;
    private static final long DATACENTER_LEFT = SEQUENCE_BIT + MACHINE_BIT;
    private static final long MACHINE_LEFT = SEQUENCE_BIT;
    
    private final long datacenterId;
    private final long machineId;
    private long sequence = 0L;
    private long lastTimestamp = -1L;
    
    public SnowflakeIdGenerator(long datacenterId, long machineId) {
        if (datacenterId > MAX_DATACENTER_BIT || datacenterId < 0) {
            throw new IllegalArgumentException("datacenterId 超出范围");
        }
        if (machineId > MAX_MACHINE_BIT || machineId < 0) {
            throw new IllegalArgumentException("machineId 超出范围");
        }
        this.datacenterId = datacenterId;
        this.machineId = machineId;
    }
    
    public synchronized long nextId() {
        long currentTimestamp = System.currentTimeMillis();
        
        if (currentTimestamp < lastTimestamp) {
            // 时钟回拨
            throw new RuntimeException("系统时钟回拨，拒绝生成 ID");
        }
        
        if (currentTimestamp == lastTimestamp) {
            // 同一毫秒内，序列号自增
            sequence = (sequence + 1) & MAX_SEQUENCE;
            if (sequence == 0L) {
                // 序列号用完，等下一毫秒
                currentTimestamp = waitNextMillis(lastTimestamp);
            }
        } else {
            // 不同毫秒，序列号归零
            sequence = 0L;
        }
        
        lastTimestamp = currentTimestamp;
        
        return ((currentTimestamp - START_TIMESTAMP) << TIMESTAMP_LEFT)
             | (datacenterId << DATACENTER_LEFT)
             | (machineId << MACHINE_LEFT)
             | sequence;
    }
    
    private long waitNextMillis(long lastTimestamp) {
        long timestamp = System.currentTimeMillis();
        while (timestamp <= lastTimestamp) {
            timestamp = System.currentTimeMillis();
        }
        return timestamp;
    }
}

// 使用
private static final SnowflakeIdGenerator ID_GENERATOR = 
    new SnowflakeIdGenerator(1, 1);  // datacenterId=1, machineId=1

public static long nextId() {
    return ID_GENERATOR.nextId();
}
```

### 3. MyBatis-Plus 集成

```yaml
mybatis-plus:
  global-config:
    db-config:
      id-type: assign_id  # 雪花算法
```

```java
@Data
@TableName("orders")
public class Order {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;  // 自动用雪花算法生成
}

// 插入时自动生成
orderService.save(order);
System.out.println(order.getId());  // 1592234567890121216
```

### 4. ShardingSphere 集成

```yaml
spring:
  shardingsphere:
    rules:
      sharding:
        key-generators:
          snowflake:
            type: SNOWFLAKE
            props:
              worker-id: 1
              max-vibration-offset: 1
              max-tolerate-time-difference-milliseconds: 10
        tables:
          orders:
            key-generate-strategy:
              snowflake:
                column: id
```

## 🚀 方案 4：Leaf（美团方案）⭐⭐⭐

### 原理

```
美团 Leaf：号段模式 + 雪花算法

号段模式：
- DB 一次分配一个号段（如 1-1000）
- 应用服务在内存中递增
- 用完再从 DB 取下一段
- 性能极高（DB 压力小）
```

### 1. 部署 Leaf Server

```sql
-- Leaf 号段表
CREATE TABLE leaf_alloc (
  biz_tag VARCHAR(50) PRIMARY KEY,
  max_id BIGINT UNSIGNED DEFAULT 1,
  step INT DEFAULT 100,
  description VARCHAR(100),
  update_time TIMESTAMP
) ENGINE=InnoDB;

INSERT INTO leaf_alloc (biz_tag, max_id, step, description) VALUES
('order', 1, 1000, '订单ID'),
('user', 1, 1000, '用户ID');
```

### 2. 启动 Leaf

```bash
git clone https://github.com/Meituan-Dianping/Leaf
cd leaf
mvn clean install
java -jar leaf-server/target/leaf-server.jar
```

### 3. 业务接入

```xml
<dependency>
    <groupId>com.sankuai.inf.leaf</groupId>
    <artifactId>leaf-core</artifactId>
    <version>1.0.2</version>
</dependency>
```

```java
@RestController
public class LeafController {
    
    @Autowired
    private SegmentService segmentService;
    
    @GetMapping("/api/leaf/{key}")
    public String getId(@PathVariable String key) {
        long id = segmentService.getId(key).getId();
        return "{\"id\":" + id + "}";
    }
}
```

```java
// 业务调用
public Long createOrder() {
    String response = restTemplate.getForObject(
        "http://leaf-server/api/leaf/order", String.class
    );
    return JSON.parseObject(response).getLong("id");
}
```

## 🚀 方案 5：Redis INCR

```java
@Autowired
private StringRedisTemplate redis;

// 简单使用
public Long nextId() {
    Long id = redis.opsForValue().increment("order:id");
    return id;
}

// 性能优化：批量获取
public Long[] nextIds(int count) {
    // 一次取 100 个
    return redis.opsForValue().increment("order:id", 100);
    // 业务自己分配 1-100
}
```

**优点：** 简单、高性能  
**缺点：** 依赖 Redis 高可用

## 📊 方案选型

| 业务规模 | 推荐方案 | 理由 |
|---|---|---|
| **小型项目** | UUID / Redis INCR | 简单够用 |
| **中型项目** | 雪花算法 | 性能好，无依赖 |
| **大型项目** | Leaf（号段模式） | 性能极致，可用 |
| **超大项目** | Leaf 集群 + 多 DB | 异地多活 |

## 🛠️ 实战：雪花算法 + 分布式 ID 服务

### 微服务方案

```
┌──────────┐
│  业务服务 │ → 调 HTTP → ┌──────────┐
└──────────┘              │  ID 服务  │ → Snowflake
                          │ (单独部署)│
                          └──────────┘
```

```java
// ID 服务（独立应用）
@RestController
public class IdController {
    
    private final SnowflakeIdGenerator generator = new SnowflakeIdGenerator(1, 1);
    
    @GetMapping("/next")
    public Result<Long> next() {
        return Result.success(generator.nextId());
    }
}

// 业务服务调用
@Service
public class OrderService {
    
    @Autowired
    private RestTemplate restTemplate;
    
    public Order createOrder(OrderDTO dto) {
        // 从 ID 服务获取 ID
        Long id = restTemplate.getForObject(
            "http://id-service/next", Long.class
        );
        dto.setId(id);
        
        orderMapper.insert(dto);
        return dto;
    }
}
```

### 性能优化：号段模式

```java
@Service
public class SegmentIdGenerator {
    
    @Autowired
    private SegmentMapper segmentMapper;
    
    private volatile Segment currentSegment;
    private volatile int currentPos;
    
    public long nextId() {
        if (currentSegment == null || currentPos >= currentSegment.getMax()) {
            // 当前号段用完，从 DB 取新号段
            currentSegment = segmentMapper.getNextSegment("order");
            currentPos = 0;
        }
        return currentSegment.getMin() + currentPos++;
    }
}
```

**性能对比：**
- 雪花算法：单机 10万 / 秒
- Leaf 号段：单机 **1000万+** / 秒
- Redis INCR：单机 5-10万 / 秒

## 🎯 总结

**分布式 ID 选型：**
- ✅ **中小项目**：雪花算法（MyBatis-Plus 内置）
- ✅ **大厂**：Leaf 号段模式（美团方案）
- ✅ **简单场景**：Redis INCR
- ✅ **不想引入依赖**：UUID

**雪花算法关键配置：**
- workerId：机器唯一（0-31）
- datacenterId：机房唯一（0-31）
- 起始时间戳：项目启动时间（减小时间戳长度）

**MyBatis-Plus 集成：**
```yaml
mybatis-plus:
  global-config:
    db-config:
      id-type: assign_id
```

**ShardingSphere 集成：**
```yaml
spring:
  shardingsphere:
    rules:
      sharding:
        key-generators:
          snowflake:
            type: SNOWFLAKE
```

**关键原则：**
- ✅ ID 趋势递增（InnoDB 友好）
- ✅ 全局唯一（分布式友好）
- ✅ 高性能（高并发）
- ✅ 长度合理（不超过 64 bit）

**下一步：** [🔄 数据一致性](/14-microservice/data-consistency) — 分布式场景下的数据一致性保障