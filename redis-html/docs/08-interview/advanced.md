---
title: 高频面试题（下）
date: 2026-08-15  # date-auto-injected
---

# 📝 高频面试题（下）

> 20 道进阶面试题，覆盖 Redis 6/7 新特性、集群细节、一致性、性能调优、企业实战。每题深度 200~300 字，包含原理 + 代码示例 + 实战建议。

## 一、新特性篇

### Q1. Redis 7 多线程 vs Redis 6 多线程区别？

**参考答案**

两者都引入了 IO 多线程（`io-threads`），但差异显著：

| 维度 | Redis 6 | Redis 7 |
|------|---------|---------|
| IO 线程默认值 | 必须手动开启 | 默认 1（关闭） |
| IO 线程参与解析命令 | 否 | 否 |
| 多线程 AOF 刷盘 | 否 | 是（`io-threads-do-reads` 配合 `aof-use-rdb-preamble`） |
| Functions | 不支持 | 支持（替代 EVAL 脚本持久化） |
| List 编码 | quicklist + ziplist | quicklist + listpack（替代 ziplist） |
| 集群负载均衡 | 仅 reshard | 支持自动 rebalance |

**核心改进**

Redis 7 把 listpack 全面替换 ziplist，解决级联更新问题；Functions 让脚本能持久化到库，跨重启可用。

**追问**

为什么 IO 多线程不默认开启？社区发现 IO 多线程在大多数场景下提升不明显（5~10%），仅在**极高 QPS 大 value 场景**才有显著收益。

---

### Q2. Redis Cluster 节点间通信机制？

**参考答案**

Cluster 节点用 **Gossip 协议**（流行病协议）通信，每秒随机选几个节点发送 PING/PONG 消息，最终全集群收敛。

**消息类型**

- **MEET**：新节点加入，向已知节点发送 MEET 让其认识自己。
- **PING**：周期性心跳，带上自己认识的节点列表（前缀）。
- **PONG**：对 PING 的响应，同步发送者自己的节点信息。
- **FAIL**：节点宕机广播。
- **PUBLISH**：客户端 `PUBLISH` 命令的扇出。

**心跳包结构**

```c
typedef struct {
    char magic[4];           // "RCmb"
    uint16_t ver;            // 协议版本
    uint16_t port;           // 端口
    uint16_t type;           // 消息类型
    uint16_t count;          // gossip 节点数
    uint64_t currentEpoch;
    uint64_t configEpoch;
    uint64_t offset;
    char sender[CLUSTER_NAMELEN]; // 节点名
    unsigned char slots[CLUSTER_SLOTS/8]; // 槽位图
    clusterNodeData nodes[count];  // gossip 节点列表
} clusterMsg;
```

**加分项**

Cluster 节点选 5 个最久未通信节点发送 PING（前 1 个携带节点列表，后 4 个仅 PING），最大化收敛速度。

---

### Q3. Redis 慢查询如何优化？

**参考答案**

慢查询指执行时间超过 `slowlog-log-slower-than`（默认 10000 微秒 = 10ms）的命令。通过 `SLOWLOG GET` 查看。

**优化思路**

1. **避免大 Key**：`HGETALL` 一个百万字段的 Hash 会阻塞。
2. **避免复杂命令**：`KEYS *` 是 O(N)，用 `SCAN` 替代。
3. **批量操作用 Pipeline**：减少 RTT 次数。
4. **合理设置过期时间**：避免大量 key 同时过期触发 `activeExpireCycle`。
5. **使用 Lazy Free**：大 Key 删除用 `UNLINK` 替代 `DEL`，后台线程释放内存。

**诊断命令**

```bash
SLOWLOG RESET              # 清空慢日志
SLOWLOG LEN                # 当前条数
SLOWLOG GET 10             # 最近 10 条

CONFIG SET slowlog-log-slower-than 5000
```

**追问**

为什么用 SCAN 替代 KEYS？KEYS 会一次性遍历整个 keyspace 阻塞主线程，SCAN 用游标分批返回 O(1) per call。

---

### Q4. 大 Key 热 Key 怎么处理？

**参考答案**

**大 Key**（BigKey）指 value 占用空间大（String > 10KB，集合元素 > 10000）的 key。

| 类型 | 阈值建议 |
|------|----------|
| String | > 10 KB |
| Hash / List / Set / ZSet | 元素数 > 5000 |

**危害**

- 阻塞主线程（删除 / 序列化）。
- 网络带宽打满。
- 内存分布不均，集群迁移困难。

**发现工具**

```bash
redis-cli --bigkeys        # 扫描所有 key 的 size 分布
redis-cli --memkeys        # 按内存排序
DEBUG SLEEP <seconds>      # 模拟阻塞
```

**热 Key**（HotKey）：短时间内访问频率极高的 key。发现方法：

1. `redis-cli --hotkeys`（Redis 7+）。
2. `MONITOR` 命令采样（生产慎用）。
3. 业务侧埋点统计。

**处理方案**

- 大 Key：拆分（按 hash / range 切分）+ UNLINK。
- 热 Key：本地缓存 + 多副本 + 读写分离。

---

### Q5. Redis 脑裂问题？

**参考答案**

**脑裂（Split-Brain）** 指主从集群中，主节点与从节点/Sentinel 网络分区，主未真正下线但 Sentinel 误判为主观下线，触发自动选主。

**后果**

旧主恢复后会变成新主的从，期间写入旧主的数据全部丢失。

**解决方案**

Redis Sentinel 提供两个配置：

```conf
# 旧主恢复后，禁止自动晋升为主
replica-priority 0

# 至少多少从节点落后小于 N 秒，才允许故障转移
min-replicas-to-write 1
min-replicas-max-lag 10
```

`min-replicas-to-write` 让主节点发现从节点断开超过 `min-replicas-max-lag` 秒时，**拒绝写入**，避免脑裂期间的数据丢失。

**追问**

为什么不用 Redlock？Redlock 在时钟跳跃、网络分区等情况下也并非完美，工程上脑裂问题的兜底是**业务幂等 + 数据校验**。

---

### Q6. Redis 分布式锁的 Redlock 算法？

**参考答案**

Redlock 是 Redis 官方提出的多 Redis 实例的分布式锁算法，**不依赖主从复制**，向 N 个（推荐 5 个）独立 Redis 实例依次加锁，超过半数（N/2+1）成功才算获取。

**算法步骤**

```text
1. 获取当前时间 T1
2. 依次向 N 个实例发送 SET key value NX PX ttl
3. 获取当前时间 T2
4. 当且仅当满足：
   - 多数实例加锁成功（N/2+1）
   - T2 - T1 < ttl（获取锁的总耗时小于锁超时时间）
   才算加锁成功
5. 有效时间 = ttl - (T2 - T1)
6. 否则向所有实例发送 DEL 释放锁
```

**争议**

Martin Kleppmann 在《How to do distributed locking》中指出 Redlock 在系统时钟跳跃的情况下不安全；antirez 撰文反驳。生产中**更多用 Zookeeper / etcd 实现强一致分布式锁**。

---

### Q7. Redis Stream 和 Kafka 的区别？

| 维度 | Redis Stream | Kafka |
|------|--------------|-------|
| 持久化 | RDB + AOF | 磁盘顺序写 + 副本 |
| 吞吐量 | 万级 QPS | 百万级 QPS |
| 消费模型 | 消费者组 + ACK | 消费者组 + offset |
| 分区 | 无（单节点 Stream） | Topic 分区并行 |
| 回溯消费 | 支持（按 ID） | 支持 |
| 消息堆积 | 受内存限制 | 磁盘几乎无限 |
| 适用场景 | 轻量级 MQ / 延迟队列 | 大流量日志 / 事件溯源 |

**加分项**

Stream 的 ID 是毫秒时间戳 + 序号，天然有序；Consumer Group 通过 PEL（Pending Entries List）记录未 ACK 消息，支持 XCLAIM 转移。

**生产建议**

- 业务简单、量小（< 1 万 QPS）：Redis Stream 足够。
- 业务复杂、量大：Kafka / RabbitMQ / Pulsar。

---

![Redis Stream + Consumer Group](/redis-stream-consumer-group.svg)

## 二、集群深入篇

### Q8. Redis Pipeline 原理？

**参考答案**

Pipeline 把多条命令打包一次性发送，服务端按顺序执行后批量返回结果，减少 RTT（Round-Trip Time）。

**性能对比**

```text
# 1000 次 SET
不使用 Pipeline: 1000 RTT × 0.5ms = 500ms
使用 Pipeline:    1 RTT × 0.5ms + 服务端执行 ≈ 5ms
```

**注意**

- Pipeline 不保证原子性，命令之间可能被其他客户端插入。
- 一次 Pipeline 内的命令数量不宜过大（建议 < 10000），避免服务端缓冲区溢出。
- Pipeline 内的命令应独立无依赖，否则后续命令拿不到前面命令的结果。

**代码示例**

```java
Jedis jedis = new Jedis("localhost");
Pipeline p = jedis.pipelined();
for (int i = 0; i < 1000; i++) {
    p.set("k" + i, "v" + i);
}
p.sync();  // 批量返回结果
```

---

### Q9. Redis 事务与 Lua 脚本区别？

**参考答案**

| 维度 | MULTI/EXEC 事务 | EVAL Lua |
|------|------------------|----------|
| 原子性 | 命令排队原子执行 | 整段脚本原子执行 |
| 逻辑判断 | 不支持 | 支持 if/else/for |
| 错误回滚 | 部分失败不回滚 | 整段失败回滚 |
| 集群限制 | 所有 key 必须在同一槽 | 所有 key 必须在同一槽（`EVALSHA` 校验） |
| 性能 | 略快（无脚本解析） | 略慢（每次 eval）但可用 evalsha 缓存 |

**实战选择**

- 简单原子操作（多条独立 SET）：MULTI/EXEC。
- 需要逻辑分支（如 CAS、滑动窗口）：Lua 脚本。

**Redis 7 Functions**

Functions 把脚本**持久化到 Redis 库**（`FUNCTION LOAD`），重启后还在；通过 `FCALL` 调用，调试支持更好。

---

### Q10. Redis 内存碎片率高怎么办？

**参考答案**

碎片率 = `used_memory_rss / used_memory`，正常 1.0~1.5，超过 1.5 需要关注。

**碎片产生原因**

- jemalloc 按固定 size class 分配（如 64 / 128 / 256 字节）。
- 高频修改（DEL + SET）导致不同大小对象混用。
- 大量 key 同时过期 + 新 key 不同大小分配。

**解决方案**

```bash
# 1. 重启 Redis（最直接）
# 2. 启用自动碎片整理（Redis 4+）
CONFIG SET activedefrag yes
CONFIG SET active-defrag-enabled yes
CONFIG SET active-defrag-threshold-lower 10
CONFIG SET active-defrag-threshold-upper 100
```

**追问**

为什么不频繁重启？重启会清空内存，对缓存场景意味着冷启动雪崩。自动碎片整理在后台以低优先级线程合并碎片内存块。

---

### Q11. 缓存一致性方案：Cache-Aside / Read-Through / Write-Behind？

**参考答案**

三种典型缓存读写模式：

**1. Cache-Aside（最常用）**

应用直接操作缓存和数据库：

```text
读：miss → 读 DB → 写 cache → 返回
写：先写 DB → 再删 cache（不要更新 cache，容易并发写覆盖）
```

**2. Read-Through**

应用只读缓存，由缓存层（Cache Provider）回源到 DB 并回填。对应用透明，类似 Lazy Load。

**3. Write-Behind / Write-Back**

应用写缓存，缓存层异步批量写 DB。性能高但有数据丢失风险，需要 WAL 或操作日志兜底。

**对比**

| 模式 | 读性能 | 写性能 | 一致性 |
|------|--------|--------|--------|
| Cache-Aside | 中 | 中 | 最终一致 |
| Read-Through | 中 | 中 | 最终一致 |
| Write-Behind | 中 | 高 | 弱一致 |

**加分项**

Cache-Aside 写 DB 后删 cache 而非更新，是基于"懒加载"的考虑：避免并发更新写覆盖，失效通过下次读回填。

---

### Q12. Redis 集群扩容步骤？

**参考答案**

向现有 Cluster 添加新节点的标准流程：

```bash
# 1. 启动新节点
redis-server --port 6380 --cluster-enabled yes --cluster-config-file nodes-6380.conf

# 2. 加入集群
redis-cli --cluster add-node 127.0.0.1:6380 127.0.0.1:6379

# 3. 重新分配槽位（从旧节点迁移）
redis-cli --cluster reshard 127.0.0.1:6379
# 系统提示：How many slots do you want to move? 16384/N
#             What is the receiving node ID? <新节点 ID>
#             Source node IDs? all

# 4. 给新主节点添加从节点（可选）
redis-cli --cluster add-node 127.0.0.1:6381 127.0.0.1:6379 --cluster-slave --cluster-master-id <新主节点 ID>

# 5. 检查集群状态
redis-cli --cluster check 127.0.0.1:6379
```

**底层数据迁移**

槽迁移以 key 为单位，逐个 `MIGRATE` 命令把 key 从源节点迁到目标节点，期间源节点对迁移中 key 标记 `MIGRATING`，目标标记 `IMPORTING`，客户端请求自动重定向。

---

### Q13. Redis 集群数据迁移原理？

**参考答案**

单槽迁移流程（Redis 内部实现）：

```text
1. 源节点标记 slot 为 MIGRATING 状态
2. 目标节点标记 slot 为 IMPORTING 状态
3. 对该 slot 中的每个 key：
   a. 源节点 GET key → 序列化
   b. RESTORE key ttl value 到目标节点
   c. DEL key 从源节点删除
4. 全部 key 迁移完成，通过 SETSLOT 通知所有节点
5. 集群配置纪元 configEpoch + 1
```

**客户端感知**

迁移期间客户端访问流程：

```text
GET key
  │
  ├─ key 在本节点 → 正常返回
  │
  ├─ key 在 MIGRATING slot 但 key 还在本节点 → 返回 ASK 重定向
  │      客户端发 ASKING 命令后访问目标节点
  │
  └─ key 不在本节点 → 返回 MOVED 重定向（一次性更新路由）
```

**加分项**

ASK 和 MOVED 的区别？MOVED 表示槽已永久迁移，客户端应更新路由表；ASK 表示正在迁移，本次特殊请求。

---

## 三、企业实战篇

### Q14. Redis RDB 备份的最佳实践？

**参考答案**

```bash
# 1. 手动触发全量备份
redis-cli BGSAVE
# 返回 Background saving started

# 2. 定时备份脚本（每天凌晨）
0 3 * * * /usr/local/bin/redis-cli bgsave && \
           cp /var/lib/redis/dump.rdb /backup/redis-$(date +\%Y\%m\%d).rdb

# 3. 校验 RDB 文件
redis-check-rdb /backup/dump.rdb

# 4. 上传到 OSS / S3
ossutil cp /backup/redis-*.rdb oss://bucket/backup/
```

**RDB 文件结构**

```text
┌─────────────────────────┐
│  REDIS0009 (9 字节魔数)  │
├─────────────────────────┤
│  aux 字段（redis-ver 等）│
├─────────────────────────┤
│  DB 选择器 (FE 0x00/0x01)│
├─────────────────────────┤
│  hash table of key-value│
│  expire time / type      │
├─────────────────────────┤
│  EOF (FF)               │
├─────────────────────────┤
│  8 字节 CRC64 校验       │
└─────────────────────────┘
```

**加分项**

远程备份时不要用 `cp` 复制正在写入的 RDB，先 `BGSAVE` 再复制或用 `redis-cli --rdb` 远程 dump。

---

### Q15. Redis 6 客户端缓存（Tracking）？

**参考答案**

**服务端辅助的客户端缓存（Server-Assisted Client-Side Caching）**：Redis 6 提供，让客户端缓存 key 的值，失效时由服务端主动通知。

**两种模式**

1. **默认模式（invalidation messages）**：

```bash
CLIENT TRACKING ON                   # 开启追踪
CLIENT TRACKING ON REDIRECT 100      # 失效消息转发给 client-id 100
```

服务端维护一个 `tracking_table`，记录哪些客户端缓存了哪些 key。当 key 被修改时，服务端通过 RESP3 协议推送失效消息给客户端。

2. **广播模式（broadcasting）**：所有客户端缓存所有 key 的失效，流量大。

**对比**

```text
普通缓存: client → server → miss → 回源 DB
客户端缓存: client → 本地 cache → 命中返回 → 失效时 server 通知
                                       ↓
                                  几乎无网络 IO
```

**加分项**

Tracking 让某些读多写少场景的 QPS 提升 10 倍以上，但需要客户端实现完整的 Cache 失效处理。

---

### Q16. Redis 多级缓存方案？

**参考答案**

典型三层缓存架构：

```text
              请求
               ↓
        ┌──────────────┐
        │  L1 本地缓存  │ Caffeine / Guava (JVM 内)
        │   100ms 级   │
        └──────────────┘
               ↓ miss
        ┌──────────────┐
        │ L2 分布式缓存 │ Redis Cluster
        │   1~5ms 级   │
        └──────────────┘
               ↓ miss
        ┌──────────────┐
        │   L3 数据库   │ MySQL / ES
        │   10~100ms   │
        └──────────────┘
```

**Java 实现**

```java
public class MultiLevelCache {
    private final LoadingCache<String, Object> l1 =
        Caffeine.newBuilder()
            .maximumSize(10_000)
            .expireAfterWrite(Duration.ofSeconds(30))
            .build(this::loadFromL2);

    private final RedisTemplate<String, Object> l2;

    private Object loadFromL2(String key) {
        Object v = l2.opsForValue().get(key);
        if (v == null) {
            v = loadFromDb(key);
            l2.opsForValue().set(key, v, Duration.ofMinutes(10));
        }
        return v;
    }

    public Object get(String key) {
        return l1.get(key);  // 自动回源
    }
}
```

**加分项**

多级缓存的一致性挑战在于 L1 各 JVM 独立，需要**短 TTL + 主动失效**（Redis Pub/Sub 广播失效消息）。

---

### Q17. Redis 集群下 Pipeline 还能用吗？

**参考答案**

**可以用，但有限制**：

1. **同一槽**：Pipeline 内所有 key 必须在同一节点（同一槽），否则收到 `CROSSSLOT` 错误。
2. **Hash Tag**：用 `{}` 强制 key 落到同一槽，如 `{user:123}:name` 和 `{user:123}:age`。

```java
// 正确：同一 hash tag
pipeline.set("{user:1}:name", "Alice");
pipeline.set("{user:1}:age", "30");

// 错误：跨槽
pipeline.set("user:1", "Alice");
pipeline.set("order:1", "ORDER-001");
```

**追问**

如果必须跨槽呢？只能拆成多次 Pipeline 或用 `MSET`（要求所有 key 同槽）。集群场景下也可用客户端 SDK 的分布式批量工具。

---

### Q18. Redis 集群如何实现事务？

**参考答案**

Cluster 模式下 MULTI/EXEC 仍然可用，但**所有 key 必须在同一槽**，否则报错：

```text
(error) CROSSSLOT Keys in request don't hash to the same slot
```

**解决方案**

1. **Hash Tag**：用 `{}` 把相关 key 绑定到同一槽。
2. **应用层补偿**：放弃 Redis 事务，改在业务层用分布式事务框架（Seata / TCC）。
3. **Lua 脚本**：把所有操作封装到 Lua，配合 hash tag 保证同槽原子。

**代码示例**

```java
// Jedis Cluster 下用 hash tag
JedisCluster cluster = new JedisCluster(nodes);
String script =
    "redis.call('SET', KEYS[1], ARGV[1]);" +
    "redis.call('SET', KEYS[2], ARGV[2]);" +
    "return 'OK'";
Object result = cluster.eval(script,
    Arrays.asList("{order:100}:status", "{order:100}:amount"),
    Arrays.asList("PAID", "99.00"));
```

---

### Q19. Redis 集群下 Lua 脚本限制？

**参考答案**

Cluster 模式下执行 Lua 脚本的所有 key 必须能确定映射到**同一槽**，否则无法路由到具体节点。

**两种方式**

1. **显式传 KEYS**：脚本所有 key 通过 `KEYS` 数组传入，Redis 用第一个 key 计算 slot。
2. **隐式 key 报错**：脚本中通过 `redis.call('GET', 'unknown_key')` 引用未声明的 key，集群返回 `CROSSSLOT` 错误。

**Node ID 绑定**

Cluster 中所有节点需要执行同一份脚本时，用 `EVALSHA` 缓存脚本：

```bash
SCRIPT LOAD "return redis.call('GET', KEYS[1])"
# 返回 sha1 哈希

# 集群各节点独立维护 script cache，
# 第一次 EVAL 时脚本被广播到所有节点（Redis 7.0 前）
```

**Redis 7 改进**

Functions 通过 `FUNCTION LOAD` 把脚本持久化到每个节点，AOF / RDB 重启后自动加载，避免重复广播。

---

### Q20. Redis 7 Functions 相比 Lua 优势？

**参考答案**

Functions 是 Redis 7 新引入的脚本管理机制，弥补 EVAL 的几个缺陷：

| 维度 | EVAL Lua | Functions |
|------|----------|-----------|
| 持久化 | 不持久化，重启丢失 | 持久化到 RDB / AOF |
| 命名空间 | 无 | 有（library 隔离） |
| 调试 | 无 | 支持 `FUNCTION STATS` / `FUNCTION KILL` |
| 跨实例同步 | 需手动 SCRIPT LOAD | 自动同步 |
| 性能 | 每次传完整脚本 | 传函数名 + 参数 |

**使用示例**

```bash
# 1. 创建 library
FUNCTION LOAD "#!lua name=mylib
redis.register_function('add_user', function(keys, args)
    redis.call('SET', keys[1], args[1])
    return 'OK'
end)"

# 2. 调用
FCALL add_user 1 user:1 "Alice"

# 3. 查看
FUNCTION LIST
```

**加分项**

Functions 还支持异步函数（`redis.register_function` 配合 `redis.fcall_ro` 只读标记），未来会支持更多语言（WASM）。

---

## 下一步

到这里 20 道进阶题结束。下一篇进入真正的**手撕代码**环节：从分布式锁到 LRU，从跳表到缓存三大问题。

**下一步：** [🔒 分布式锁手撕](/08-interview/lock-coding)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
