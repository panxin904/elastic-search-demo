---
title: 分布式 ID
---
# 分布式 ID

## 1. 核心要求

分布式系统主键生成，不能再依赖 auto_increment（每库独立）。

```
✅ 唯一性（全局不重复）
✅ 高性能（每库每秒 1 万+生成）
✅ 趋势递增（索引友好）
✅ 信息安全（不能被猜出业务量）
✅ 高可用（无单点）
✅ 短（64-bit 足够）
```

## 2. 主流方案

### 2.1 UUID

```java
UUID.randomUUID();
// 9a3b3b80-1f87-4c9d-a3f0-d83f5e2c6b34
```

**优**：简单，无单点。
**缺**：128-bit 太大（浪费）；无序（索引碎片化）；v4 信息熵大但无业务含义。

### 2.2 UUIDv7（推荐）

UUIDv7 = 时间戳（前 48 bit）+ 随机后缀
**优**：趋势递增（类似 Snowflake）、标准 RFC。

```java
UUID v7 = UUID.fromString("018a3b3b-1f87-4c9d-...");
// 前 48 bit = 毫秒时间戳 → 天然排序
```

### 2.3 Snowflake（Twitter / 经典）

```
+---------------------------------------------------------------+
| 1 bit unused | 41 bit timestamp | 10 bit machine | 12 bit seq |
+---------------------------------------------------------------+
  sign         毫秒（69 年）     1024 节点       4096/ms/节点
```

```java
// Twitter Snowflake（简版）
long id = (System.currentTimeMillis() - TWITTER_EPOCH) << 22
       | (machineId & 0x3FF) << 12
       | (sequence & 0xFFF);
```

**优**：64-bit，趋势递增，高性能。
**缺**：时钟回拨问题（ntpdate）。

### 2.4 美团 Leaf

```java
// Snowflake 变种：8 byte ID
// bit: 1 sign | 41 timestamp | 5 datacenter | 5 worker | 12 sequence
// 优化：依赖 MySQL/zk 分配 datacenter+worker
```

**优**：弱依赖（DB / zk）。
**缺**：需要部署 Leaf 集群。

### 2.5 滴滴 TinyID

类似 Leaf，更简单。

### 2.6 百度 uid-generator

```java
long id = UidGenerator.getUID();
// Snowflake + 弱依赖
```

## 3. 实战选型

| 场景 | 选 | 原因 |
|------|----|------|
| 中小规模 | UUID v7 | 标准，趋势递增 |
| 高并发 / 不想依赖 | Snowflake | 64-bit 简单 |
| 强业务量 | 美团 Leaf | 实战证明 |
| 内部 ID | 雪花自研 | 5 分钟 |
| 订单 ID | UUID v7 / Snowflake | 趋势递增，索引友好 |
| 用户 ID | UUID v4 | 隐私优先 |

## 4. UUIDv7 vs Snowflake 对比

| 维度 | UUIDv7 | Snowflake |
|------|--------|-----------|
| 标准 | RFC 9562 | 无（各家自定） |
| 长度 | 128 bit | 64 bit |
| 趋势 | 强（48 bit 时间戳） | 强（41 bit） |
| 随机后缀 | 74 bit | 22 bit |
| 信息泄漏 | 少 | 节点 ID 暴露 |
| 依赖 | 无 | worker ID 分配 |
| 跨语言 | 各语言 SDK | 各语言实现 |

**Java 19+ 内置 `UUID v7`**：

```java
UUID uuid = UUID.randomUUID();
// 当前可能是 v4（随机），Java 21+ 提供 v7
```

## 5. 实战：Snowflake（自研）

```java
public class IdWorker {
  private final long epoch = 1700000000000L;  // 起点
  private long lastTs = -1L;
  private long seq = 0L;
  private final long datacenterId;  // 0-31
  private final long workerId;     // 0-31

  public synchronized long nextId() {
    long ts = System.currentTimeMillis() - epoch;
    if (ts == lastTs) {
      seq = (seq + 1) & 0xFFF;  // 4096/ms
      if (seq == 0) ts = waitNextMillis(ts);
    } else {
      seq = 0;
    }
    if (ts < lastTs) throw new RuntimeException("Clock moved backwards");
    lastTs = ts;
    return (ts << 22) | (datacenterId << 17) | (workerId << 12) | seq;
  }
}
```

**关键**：
- 41 bit 时间戳 = 69 年
- 5 bit datacenter + 5 bit worker = 1024 节点
- 12 bit sequence = 4096/ms/节点
- 单机 QPS：4096 × 1000 = 4M/s

## 6. 时钟回拨处理

| 方案 | 描述 |
|------|------|
| 抛错拒绝 | 简单，但引发小规模不可用 |
| 等待追上 | 回拨 ≤ 5ms：sleep 等待 |
| 预留扩展位 | 41 bit → 42 bit，多 1 bit |
| 多 ID 中心 | 切换到备用集群 |

## 7. 实战：分布式 ID 服务

```java
@RestController
public class IdService {
  @Autowired IdWorker idWorker;
  @GetMapping("/id")
  public Map<String, Object> next() {
    return Map.of("id", idWorker.nextId());
  }
}
```

**部署**：3-5 个 worker 节点 + Redis / ZK 分配 workerId。

## 8. 选型

| 场景 | 选 |
|------|-----|
| 中小 | UUID v7（Java 19+） |
| 高并发 | Snowflake（自研 / 框架） |
| 不想自研 | 美团 Leaf / 滴滴 TinyID / 百度 uid-generator |
| 严格顺序 | Snowflake（41 bit 时间戳天然递增） |
| 业务 ID（订单） | UUID v7 + 分库分表 |
| 用户 ID | UUID v4（隐私优先） |

## 9. 实战选型

```xml
<!-- 美团 Leaf -->
<dependency>
  <groupId>com.uber</groupId>
  <artifactId>RLeaf</artifactId>
  <version>1.0.0</version>
</dependency>

<!-- 百度 uid-generator -->
<dependency>
  <groupId>com.baidu.fsg</groupId>
  <artifactId>uid-generator</artifactId>
</dependency>
```

## 🔗 下一步
- [水平 / 垂直拆分](/10-database-sharding/strategy)
- [幂等性设计](/03-ha-theory/idempotency)
