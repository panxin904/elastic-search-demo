---
title: Stream
---

# 🌊 Stream

> Stream 是 Redis 5.0 引入的**持久化消息流**，弥补了 Pub/Sub 一次性、不确认、不重放的缺陷。它用 Rax 树索引 + listpack 节点存储消息 ID，支持消费者组（Consumer Group）、消费确认（ACK）、Pending 重试和 PEL（Pending Entries List），是 Redis 唯一带"消息中间件"色彩的数据类型。

<ClientOnly>
  <DataStructureViz />
</ClientOnly>

## 一、Stream 的设计目标

List + Pub/Sub 都不能完整覆盖消息队列需求：

```text
List (LPUSH/BRPOP)
  ├─ ✅ 持久化 / ✅ 阻塞
  ├─ ❌ 多消费者争抢要靠 BLPOP 多连接硬拼
  ├─ ❌ 没有 ACK，重连后重复消费整条
  └─ ❌ 没有"已读位置"，只能粗暴 BRPOP

Pub/Sub
  ├─ ✅ 多消费者广播
  ├─ ❌ 离线即丢失（fire-and-forget）
  └─ ❌ 无持久化、无 ACK

Stream (XADD/XREADGROUP)
  ├─ ✅ 持久化（RDB / AOF 都支持）
  ├─ ✅ 消费者组：每条消息只被组内一个消费者处理
  ├─ ✅ XPENDING / XACK 精确重试
  ├─ ✅ 阻塞 XREADGROUP
  └─ ✅ 消息 ID 单调递增、可按 ID 区间查
```

简单一句话：**Stream 让 Redis 第一次拥有了 Kafka 风格的"消息流"语义**。

## 二、底层结构：Rax + listpack

Stream 由三层结构组成：

```text
stream
├── rax *rax;              // 全局消息 ID 索引树
├── streamID last_id;      // 当前最大 ID（XADD 自动续号）
├── streamCG *cgroups;     // 消费者组字典（dict 形式）
└── listpack entries[];    // 消息体（实际存储）
```

消息布局：

```text
┌──────────────────────────────────────────────────┐
│ listpack[0]   listpack[1]   listpack[2]   ...   │
│ ┌─────────┐  ┌─────────┐  ┌─────────┐           │
│ │1690...-0│  │1690...-1│  │1690...-2│           │
│ │k1 v1 k2 │  │k1 v1 k2 │  │k1 v1 k2 │           │
│ │  v2 ... │  │  v2 ... │  │  v2 ... │           │
│ └─────────┘  └─────────┘  └─────────┘           │
└──────────────────────────────────────────────────┘
       │             │             │
       ▼             ▼             ▼
   ┌───────────────────────────────────────┐
   │            rax (基数树)               │
   │   key=ms-seq  value=listpack 偏移    │
   │   ┌────────┐                          │
   │   │ root   │                          │
   │   │  ├─1   │                          │
   │   │  ├─6   │                          │
   │   │  └─9   │  → offset=42             │
   │   │   └─0  │  → offset=80             │
   │   └────────┘                          │
   └───────────────────────────────────────┘
```

每条消息的 listpack entry 结构：

```text
┌────────────┬────────────┬─────┬─────┬─────┬─────┐
│   ID len   │  "1690-0"  │k1 l │ "a" │k2 l │ "1" │
└────────────┴────────────┴─────┴─────┴─────┴─────┘
   编码ID        ID字符串    字段1   值1  字段2  值2
```

`rax` 是 Redis 自研的**基数树**（Radix Tree），相比 zset 的 skiplist，rax 更节省内存且支持按 ID 前缀快速定位。

## 三、消息 ID：ms-seq 编码

每条消息的 ID 由两部分组成：

```text
<millisecondsTime>-<sequenceNumber>
        ↑                   ↑
   服务器当前毫秒         同一毫秒内的递增序号
```

```bash
127.0.0.1:6379> XADD orders * user_id 1001 amount 99
"1690123456789-0"          # 时间戳 1690123456789 毫秒，第 0 条
127.0.0.1:6379> XADD orders * user_id 1002 amount 50
"1690123456789-1"          # 同一毫秒，序号自增
127.0.0.1:6379> XADD orders * user_id 1003 amount 30
"1690123456790-0"          # 跨毫秒，序号重置为 0
```

ID 的几个性质：

| 性质 | 说明 |
|------|------|
| **全局单调** | 服务器保证每条新消息的 ID > 上一条 |
| **可指定** | `XADD mystream 1690123456790-0 f v` 显式给定 |
| **可范围查** | `XRANGE orders 1690123456789-0 1690123456790-0` |
| **特殊符号** | `*` 表示自动分配；`$` 表示当前最新；`-` / `+` 表示最小/最大 |

## 四、消费者组（Consumer Group）

Stream 最核心的能力是**消费者组**：让一组消费者协同消费，每条消息仅被组内一个消费者处理。

```text
                ┌───────────────────────┐
                │      Stream: orders   │
                │  [m1][m2][m3][m4][m5] │
                └───────────┬───────────┘
                            │
                            ▼ XREADGROUP
                ┌───────────────────────┐
                │   Group: order_group  │
                │   last_delivered_id  │
                └───────────┬───────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
      Consumer A       Consumer B       Consumer C
      [m1][m3]         [m2]             [m4]
      
      PEL: m1*, m3*     PEL: m2*         PEL: m4*
      (* 已读未确认)
```

每个消费者组维护：

- `last_delivered_id`：组已投递给消费者的最后一条 ID。
- `pel`：Pending Entries List，记录"已读未确认"的消息。
- `entries_read`：消费者已成功 ACK 的数量（Redis 7 引入）。

```bash
127.0.0.1:6379> XGROUP CREATE orders order_group $ MKSTREAM
OK
127.0.0.1:6379> XGROUP CREATE orders order_group 0        # 已有 stream 时
OK
```

## 五、核心命令速查

### XADD：生产消息

```bash
127.0.0.1:6379> XADD orders * user 1001 amount 99
"1690123456789-0"
127.0.0.1:6379> XADD orders MAXLEN ~ 1000 * user 1002 amount 50
"1690123456789-1"
# MAXLEN ~ N 表示"近似裁剪到 N"，性能比精确裁剪好
```

### XREAD：独立消费者（无组）

```bash
# 从 ID 1690123456789-0 开始读，最多 10 条，阻塞 5 秒
127.0.0.1:6379> XREAD COUNT 10 BLOCK 5000 STREAMS orders 1690123456789-0
1) 1) "orders"
   2) 1) 1) "1690123456789-0"
         2) 1) "user"
            2) "1001"
```

### XREADGROUP：消费者组消费

```bash
# worker-1 从 order_group 读 5 条
127.0.0.1:6379> XREADGROUP GROUP order_group worker-1 COUNT 5 STREAMS orders >
1) 1) "orders"
   2) 1) 1) "1690123456789-0"
         2) 1) "user"
            2) "1001"

# 同组 worker-2 再读，只能看到 worker-1 没读过的
127.0.0.1:6379> XREADGROUP GROUP order_group worker-2 COUNT 5 STREAMS orders >
1) 1) "orders"
   2) 1) 1) "1690123456789-1"
         2) 1) "user"
            2) "1002"
```

注意 `>` 表示"从未投递给任何消费者的下一条"。

### XACK：确认消息

```bash
# worker-1 处理完后确认
127.0.0.1:6379> XACK orders order_group 1690123456789-0
(integer) 1
```

### XPENDING：查询未确认消息

```bash
127.0.0.1:6379> XPENDING orders order_group
1) (integer) 1             # 总待确认数
2) "1690123456789-1"       # 最小 ID
3) "1690123456789-1"       # 最大 ID
4) 1) 1) "worker-2"        # 消费者
      2) "1"               # 待确认数

# 查看详情
127.0.0.1:6379> XPENDING orders order_group - + 10 worker-2
1) 1) "1690123456789-1"
   2) "worker-2"
   3) (integer) 12345      # 已空闲 12345 ms
   4) (integer) 1          # 投递次数
```

### XCLAIM：转移未确认消息

```bash
# worker-2 挂了，worker-1 接管
127.0.0.1:6379> XCLAIM orders order_group worker-1 60000 1690123456789-1
1) 1) "1690123456789-1"
   2) 1) "user"
      2) "1002"
```

## 六、消息流转全景

```text
                       XADD orders * f v
                            │
                            ▼
                ┌──────────────────────┐
                │   listpack append    │
                │   rax insert         │
                │   last_id 更新       │
                └──────────────────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │  XREADGROUP >        │
                │  组 last_id 推进     │
                │  加入消费者 PEL      │
                └──────────────────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │   业务处理           │
                └──────────────────────┘
                            │
                          XACK
                            │
                            ▼
                ┌──────────────────────┐
                │  从 PEL 移除         │
                └──────────────────────┘
```

## 七、与 Kafka / RocketMQ 的对比

| 维度 | Redis Stream | Kafka | RocketMQ |
|------|--------------|-------|----------|
| 单机 QPS | 10 万级 | 百万级 | 10 万级 |
| 多分片 | ❌ 单实例 | ✅ Partition | ✅ Queue |
| 持久化 | RDB/AOF 落盘 | ✅ 顺序文件，零拷贝 | ✅ CommitLog |
| 消费者组 | ✅ | ✅ | ✅ |
| 消费位点管理 | PEL + last_delivered_id | Offset（Broker） | Offset（Broker） |
| 回溯消费 | ✅ XRANGE | ✅ Offset 重置 | ✅ Offset 重置 |
| 事务消息 | ❌ | ✅ | ✅ |
| 死信队列 | ❌ 需手写 | ❌ 需手写 | ✅ 内置 |
| 运维成本 | 极低 | 高（ZK / KRaft） | 中（NameServer） |
| 适用场景 | 轻量流 / 中小业务 | 大流量日志 / 事件溯源 | 金融级可靠消息 |

实战选择建议：

```text
消息量 < 50 万/天  ─►  Redis Stream（够用、零运维）
消息量 50 万~数千万  ─►  Kafka（吞吐 + 分片扩展）
消息量 > 千万 且需要事务/严格不丢 ─► RocketMQ
```

## 八、面试要点

- **Stream 持久化吗**？是的。RDB 全量、AOF 增量都支持，重启后数据保留。
- **Stream 满了会怎样**？默认无限增长；`XADD ... MAXLEN` / `XADD ... MINID` 可裁剪；近似裁剪 `~` 性能更好。
- **PEL 无限增长怎么办**？定期用 `XPENDING + XCLAIM` 重平衡；过期 PEL 用 `XPENDING ... IDLE 60000` 配合 `XCLAIM` 自动转移。
- **Stream 是阻塞的吗**？`XREAD BLOCK` / `XREADGROUP BLOCK` 都是客户端阻塞等待 Redis 推送。
- **Redis Stream 能做分布式限流吗**？能。配合 `XADD MAXLEN ~ N` 与 `XLEN` 实现滑动窗口。

## 九、下一步

Stream 让 Redis 第一次拥有消息中间件的能力，但这一切的"持久化保证"仍然依赖 RDB / AOF。下一篇我们系统梳理 Redis 的两种持久化机制。

**下一步：** [💾 持久化总览](/03-persistence/overview)