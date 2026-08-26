---
title: Snowflake 雪花算法
---

# Snowflake 雪花算法

> Twitter 2010 年开源的分布式 ID 生成算法。**64 bit、趋势递增、高性能**。

## 1. 分布式 ID 的要求

```
分布式系统的 ID 生成：
  - 全局唯一
  - 趋势递增（数据库友好）
  - 高性能（10w+ QPS）
  - 高可用（不能单点）
  - 信息安全（不能预测）
```

## 2. Snowflake 结构

```
64 bit 长整型：
  ┌─────────┬─────┬─────────┬──────────┐
  │ 0 (1b)  │ 时间戳 │ 数据中心 │ 序列号  │
  │ 符号位   │(41b) │+机器(10b)│ (12b)  │
  └─────────┴─────┴─────────┴──────────┘
  0 | 0000000... | 00000 00000 | 000000000000

  1 bit 符号：固定 0（正数）
 41 bit 时间戳：当前时间 - epoch
 10 bit 机器：5 bit 数据中心 + 5 bit 机器
 12 bit 序列号：毫秒内自增
```

容量：
```
- 时间戳：2^41 / 1000 / 60 / 60 / 24 / 365 ≈ 69 年
- 机器数：2^10 = 1024 台
- 每毫秒：2^12 = 4096 个 ID
- 总 QPS：1024 × 4096 = 4,194,304
```

## 3. 核心实现

```java
public class SnowflakeIdWorker {
    // epoch（开始时间）
    private final long twepoch = 1288834974657L;
    // 各部分位数
    private final long workerIdBits = 5L;
    private final long datacenterIdBits = 5L;
    private final long sequenceBits = 12L;
    // 最大值
    private final long maxWorkerId = -1L ^ (-1L << workerIdBits);     // 31
    private final long maxDatacenterId = -1L ^ (-1L << datacenterIdBits); // 31
    private final long sequenceMask = -1L ^ (-1L << sequenceBits);   // 4095
    // 移位
    private final long workerIdShift = sequenceBits;
    private final long datacenterIdShift = sequenceBits + workerIdBits;
    private final long timestampShift = sequenceBits + workerIdBits + datacenterIdBits;

    private long workerId;
    private long datacenterId;
    private long sequence = 0L;
    private long lastTimestamp = -1L;

    public SnowflakeIdWorker(long workerId, long datacenterId) {
        if (workerId > maxWorkerId || workerId < 0) {
            throw new IllegalArgumentException("workerId invalid");
        }
        if (datacenterId > maxDatacenterId || datacenterId < 0) {
            throw new IllegalArgumentException("datacenterId invalid");
        }
        this.workerId = workerId;
        this.datacenterId = datacenterId;
    }

    public synchronized long nextId() {
        long timestamp = timeGen();

        if (timestamp < lastTimestamp) {
            throw new RuntimeException(
                "Clock moved backwards. Refusing to generate id for "
                + (lastTimestamp - timestamp) + " milliseconds");
        }

        if (lastTimestamp == timestamp) {
            // 同一毫秒内，序列号自增
            sequence = (sequence + 1) & sequenceMask;
            if (sequence == 0) {
                // 序列号用尽，等下一毫秒
                timestamp = tilNextMillis(lastTimestamp);
            }
        } else {
            // 不同毫秒，序列号归零
            sequence = 0L;
        }

        lastTimestamp = timestamp;

        // 组装 64 bit ID
        return ((timestamp - twepoch) << timestampShift) |
               (datacenterId << datacenterIdShift) |
               (workerId << workerIdShift) |
               sequence;
    }

    private long tilNextMillis(long lastTimestamp) {
        long timestamp = timeGen();
        while (timestamp <= lastTimestamp) {
            timestamp = timeGen();
        }
        return timestamp;
    }

    private long timeGen() {
        return System.currentTimeMillis();
    }
}
```

## 4. 关键问题

### 4.1 时钟回拨

```
问题：
  - 系统时间被 NTP 调整往前
  - 当前时间 < 上次时间
  - 可能生成重复 ID

解决：
  1. 拒绝生成（最保守）
  2. 等待追上（业务可能超时）
  3. 启用备用 workerId
  4. 用逻辑时钟代替时间戳
```

### 4.2 workerId 分配

```
方案 1：配置文件
  - 每个实例启动时从配置读
  - 简单但易冲突

方案 2：数据库分配
  - workerId 表，分配后标记
  - 启动时 INSERT + SELECT
  - 简单可靠

方案 3：ZK 临时节点
  - 在 ZK 创建顺序节点
  - 节点编号 = workerId
  - 自动分配

方案 4：IP 转换
  - IP 段映射到 workerId
  - 例：10.0.0.0/24 → 1-254
```

### 4.3 序列号用尽

```
每毫秒最多 4096 个 ID：
  - 高并发下可能用尽
  - 等待下一毫秒（最多 1ms）

解决：
  - 增加 sequence 位（牺牲机器数）
  - 拆分多个 Snowflake worker
  - 业务层限流
```

### 4.4 业务扩展

```
原始 64 bit 分配未必适合所有业务：
  - 业务 ID 嵌入
  - 增加版本号
  - 增加环境标识

变体：
  - ShardingJDBC 雪花：41b 时间 + 9b 业务 + 1b 兼容 + 12b 序列
  - 百度 UidGenerator：借用未来时间
  - 美团 Leaf：基于 Snowflake + DB / ZK
```

## 5. 变体实现

### 5.1 百度 UidGenerator

```
改进：
  - 借用未来时间（解决时钟回拨）
  - RingBuffer 预分配
  - 性能提升 5x

结构：
  ┌─────────┬──────────┬────────┐
  │ 时间戳  │ workId  │ 序列号 │
  │ (28b)   │ (22b)   │ (13b)  │
  └─────────┴──────────┴────────┘
```

### 5.2 滴滴 TinyID

```
特点：
  - 基于 DB 号段模式
  - 批量获取 ID
  - 性能高
```

### 5.3 改进版（业务可定制）

```
实际项目推荐：
  ┌────┬─────────────┬──────┬──────┬──────┐
  │ 0  │ 时间戳(41b)  │ 业务 │ worker │ 序列 │
  │    │              │ (4b) │ (6b)  │(12b)│
  └────┴─────────────┴──────┴──────┴──────┘

  - 业务 bit：区分业务线（16 个）
  - worker：64 个
  - 序列：4096/ms
```

## 6. 性能测试

```
单机 Snowflake：
  - 4 核 8G
  - 100万 QPS
  - P99 < 1ms

集群（10 实例）：
  - 1000万 QPS

📌 Snowflake 是性能最高的 ID 方案
   远高于 DB 自增（1万 QPS）
```

## 7. 与其他 ID 方案对比

| 方案 | 性能 | 趋势递增 | 全局唯一 | 长度 | 信息安全 |
|---|---|---|---|---|---|
| **Snowflake** | 极高 | ✅ | ✅ | 64 bit | ❌（可推时间） |
| **DB 自增** | 低 | ✅ | ✅ | 64 bit | ❌ |
| **UUID v4** | 高 | ❌ | ✅ | 128 bit | ✅ |
| **Redis INCR** | 中 | ✅ | ✅ | 64 bit | ❌ |
| **Leaf** | 高 | ✅ | ✅ | 64 bit | ❌ |

## 8. 工程实现

### 8.1 Hutool 工具类

```java
import cn.hutool.core.lang.Snowflake;
import cn.hutool.core.net.NetUtil;
import cn.hutool.core.util.IdUtil;

long workerId = NetUtil.ipv4ToLong(NetUtil.getLocalhostStr()) % 32;
long datacenterId = 1L;
Snowflake snowflake = IdUtil.getSnowflake(workerId, datacenterId);

long id = snowflake.nextId();  // 1596221953575989248
String idStr = snowflake.nextIdStr();  // "1596221953575989248"
```

### 8.2 MyBatis-Plus 集成

```java
@Bean
public IdentifierGenerator idGenerator() {
    return new DefaultIdentifierGenerator();
}

// 实体
@TableId(type = IdType.ASSIGN_ID)
private Long id;

// 自动填充
INSERT INTO user (id, name) VALUES (1596221953575989248, 'Tom');
```

### 8.3 美团 Leaf（基于 Snowflake）

```java
// Leaf-snowflake 模式
LeafSnowflakeService service = new LeafSnowflakeService();
service.init();

// 生成 ID
long id = service.getId("order");

// Leaf 解决 workerId 分配 + 时钟回拨
```

## 9. 常见误区

### 9.1 64 bit 够用吗？

```
看起来 2^64 极大，但：
  - 高 QPS 下 1 年消耗 3.1×10^14
  - 2^64 ≈ 1.8×10^19
  - 理论能用 5 万年

但实际上：
  - 41 bit 时间戳 69 年用完
  - 是时间戳限制，不是位数限制
```

### 9.2 雪花 ID 能当主键吗？

```
能！优势：
  - 单调递增（聚簇索引友好）
  - 64 bit 不大

注意：
  - MySQL bigint = 8 字节，足够
  - 不要用 int（4 字节溢出）
```

### 9.3 Snowflake 必配 ZK 吗？

```
不一定：
  - workerId 可以从配置/IP/DB 分配
  - ZK 是一种方式
  - 小项目直接配即可
```

## 10. 一句话总结

```
📌 Snowflake = 1b 符号 + 41b 时间 + 10b 机器 + 12b 序列
📌 容量：1024 机器 × 4096 ID/ms × 69 年
📌 性能：单机 100万 QPS，集群 1000万 QPS
📌 关键问题：时钟回拨（拒绝/备用 workerId）、workerId 分配（IP/DB/ZK）
📌 变体：百度 UidGenerator（RingBuffer）/ 滴滴 TinyID（DB 号段）/ 美团 Leaf
📌 与 UUID 对比：雪花有序 64 bit（DB 友好），UUID 随机 128 bit（信息安全）
📌 框架集成：Hutool / MyBatis-Plus / 美团 Leaf
```

## 11. 参考资料

- Twitter 原始 Snowflake 论文
- 百度 UidGenerator（github.com/baidu/uid-generator）
- 滴滴 TinyID（github.com/didi/tinyid）
- 美团 Leaf（github.com/Meituan-Dianping/Leaf）
- Hutool Snowflake 实现
- MyBatis-Plus 雪花 ID 文档


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
