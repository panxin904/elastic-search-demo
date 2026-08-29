---
title: 高频面试题（上）
date: 2026-08-15  # date-auto-injected
---

# 📝 高频面试题（上）

> 20 道 Redis 高频面试题，按主题归类：基础概念、底层原理、持久化、集群、运维实战。每题覆盖核心答案 + 加分项 + 面试官追问。

## 一、基础概念篇

### Q1. Redis 是什么？为什么快？

**参考答案**

Redis（Remote Dictionary Server）是一个基于内存的键值数据库，支持多种数据结构（String、Hash、List、Set、ZSet、Stream 等），常用于缓存、排行榜、计数器、分布式锁、消息队列等场景。

快的核心原因：

1. **内存读写**：数据主要驻留在内存中，避免磁盘 I/O 瓶颈。
2. **单线程模型**：避免线程切换和锁竞争开销（命令执行层面）。
3. **IO 多路复用**：基于 epoll/kqueue/select，单线程同时处理上万连接。
4. **高效数据结构**：SDS、dict、ziplist、skiplist 等底层结构针对场景高度优化。
5. **C 语言实现**：贴近底层，代码经过多年性能调优。

**加分项**

能答出 Redis 6/7 在网络 I/O 层引入多线程（io-threads），但命令执行依然单线程，体现对版本演进的认知。

**追问**

QPS 多少算正常？单节点 Redis 一般 8~10 万 QPS（GET/SET），集群可达百万级。

---

### Q2. Redis 为什么用单线程？

**参考答案**

Redis 的"单线程"特指**命令执行**层面，4.0 之前连异步任务（如 AOF 刷盘）都是单线程。单线程设计带来三个好处：

1. **无锁竞争**：避免多线程修改共享数据结构的加锁开销，简化数据结构实现。
2. **可预测性**：每条命令的执行时间确定，无线程切换带来的延迟毛刺。
3. **内存高效**：不需要为每个连接维护独立的栈和上下文，节省内存。

**追问**

那为什么不用多线程分摊 CPU？根本原因是 Redis 的性能瓶颈不在 CPU，而在网络 I/O 和内存带宽。单线程足够把单核跑满，加多线程反而引入同步复杂度。

---

### Q3. Redis 和 Memcached 的区别？

| 维度 | Redis | Memcached |
|------|-------|-----------|
| 数据结构 | 5 大基础 + Stream / Geo / HyperLogLog | 仅 String |
| 持久化 | RDB + AOF | 不支持 |
| 集群 | Cluster + Sentinel | 客户端分片 / mcrouter |
| 线程模型 | 单线程命令 + 多线程 I/O（Redis 6+） | 完全多线程 |
| 内存管理 | 多种淘汰策略 | 仅 LRU |
| 事务 | MULTI/EXEC + Lua | 不支持 |
| 典型场景 | 缓存 + 数据库 + MQ | 纯缓存 |

**加分项**

Memcached 用 Slab Allocation，固定大小 chunk 减少碎片，但无法存储变长对象；Redis 用 jemalloc，更通用。

---

### Q4. Redis 5 大基础类型？

```text
┌─────────┬────────────────┬─────────────────────────────┐
│ 类型    │ 底层编码        │ 典型命令                     │
├─────────┼────────────────┼─────────────────────────────┤
│ String  │ int / embstr / raw │ SET / GET / INCR / SETNX│
│ Hash    │ listpack / HT      │ HSET / HGET / HMSET      │
│ List    │ quicklist（Redis 7）│ LPUSH / RPUSH / LRANGE  │
│ Set     │ intset / HT       │ SADD / SMEMBERS / SINTER  │
│ ZSet    │ listpack / skiplist│ ZADD / ZRANGE / ZRANK    │
└─────────┴────────────────┴─────────────────────────────┘
```

**加分项**

能补充 Redis 7 的 `listpack` 已经替代 `ziplist` 作为小对象编码，并解释 quicklist = 双向链表 + listpack 的混合结构。

---

### Q5. Redis 是单线程还是多线程？

**参考答案**

Redis 整体是**多线程**，但**命令执行**保持单线程：

- **主线程**：接收连接、解析命令、执行命令、返回结果、写 AOF、生成 RDB。
- **后台线程**（Redis 4+）：`bio_close_file`、`bio_aof_fsync`、`bio_lazy_free` 等异步任务。
- **IO 线程**（Redis 6+）：通过 `io-threads` 配置多线程处理**网络读写**，但命令解析和执行仍在主线程。

**为什么 IO 多线程但不命令多线程？**

多线程读写能分摊大流量场景的网络 I/O 开销，而命令执行多线程需要复杂同步（如 BLPOP 阻塞唤醒），收益远小于复杂度代价。

---

## 二、底层原理篇

### Q6. 什么是 Redis 持久化？RDB 和 AOF 区别？

**参考答案**

持久化就是把内存数据写到磁盘，保证 Redis 重启后数据不丢。两种方式：

- **RDB（Redis Database）**：定时快照全量数据。`bgsave` 用 fork + COW 实现，对性能影响小，但可能丢失最后一次快照到宕机之间的数据。
- **AOF（Append Only File）**：记录每条写命令到日志。`always / everysec / no` 三种刷盘策略，可配合 `bgrewriteaof` 做 AOF 重写压缩。

**对比**

| 维度 | RDB | AOF |
|------|-----|-----|
| 恢复速度 | 快 | 慢 |
| 数据安全 | 可能丢失几分钟 | 最多丢 1 秒（everysec） |
| 文件大小 | 小（压缩二进制） | 大（文本命令） |
| 性能影响 | fork 时阻塞 | always 模式 IO 密集 |

**加分项**

Redis 4 引入**混合持久化**（aof-use-rdb-preamble），AOF 文件前半段是 RDB 格式、后半段是增量 AOF，兼顾恢复速度和数据安全。

---

### Q7. Redis 过期键删除策略？

**参考答案**

Redis 同时使用两种策略：

1. **惰性删除（Lazy Expiration）**：访问 key 时才检查是否过期，对 CPU 友好但可能堆积大量过期 key 占内存。
2. **定期删除（Periodic Expiration）**：每秒执行 `activeExpireCycle`，按 expire 字典分批抽样删除，限制单次时长避免阻塞。

**追问**

为什么不用定时器（TTL 到点删除）？因为 key 数量大时，定时器会消耗大量 CPU 资源，且大多数 key 根本不会被访问。

**底层实现**

过期字典 `expires` 存的是"key → 过期时间戳"，结构复用 dict。`EXPIRE key 60` 实际写入 `expires[key] = now + 60s`。

---

### Q8. Redis 内存淘汰策略有哪些？

`maxmemory-policy` 配置项，可选 8 种：

```text
noeviction          # 默认，写命令返回错误
allkeys-lru         # 所有 key 中淘汰最久未用
allkeys-lfu         # 所有 key 中淘汰最不常用（Redis 4+）
allkeys-random      # 所有 key 中随机淘汰
volatile-lru        # 仅在过期 key 中 LRU
volatile-lfu        # 仅在过期 key 中 LFU
volatile-random     # 仅在过期 key 中随机
volatile-ttl        # 优先淘汰剩余 TTL 最短的
```

**选择建议**

- 纯缓存场景：`allkeys-lru` 或 `allkeys-lfu`。
- 数据不能丢：`noeviction` + 监控内存。
- 有明显冷热分层：`volatile-lru` 配合 expire 字段。

---

### Q9. 缓存穿透、击穿、雪崩区别？

| 问题 | 描述 | 典型方案 |
|------|------|----------|
| **穿透** | 查询不存在的 key，每次都打到 DB | 布隆过滤器 / 空值缓存 |
| **击穿** | 热点 key 过期瞬间高并发打到 DB | 互斥锁 / 逻辑过期 |
| **雪崩** | 大量 key 同时过期 | 随机过期时间 / 多级缓存 / 熔断降级 |

**加分项**

穿透和击穿经常被混淆，区分点在于"key 是否真实存在"。穿透的 key 在 DB 也不存在，击穿的 key 真实存在但 Redis 没命中。详见 [❄️ 缓存三大问题](/08-interview/avalanche)。

---

## 三、分布式篇

### Q10. Redis 分布式锁如何实现？

**参考答案**

最简实现基于 `SET key value NX PX 30000`：

```bash
SET lock:order:123 "uuid-abc" NX PX 30000
```

- `NX`：仅当 key 不存在时设置。
- `PX 30000`：30 秒后自动过期，防止持锁进程崩溃后死锁。
- value 用 UUID：释放锁时通过 Lua 脚本校验，避免误删别人的锁。

**释放锁的 Lua 脚本**

```lua
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

**追问**

单机锁有什么风险？Redis 主从切换时锁可能丢失，需要 **Redlock** 多实例多数派算法。详见 [🔒 分布式锁手撕](/08-interview/lock-coding)。

---

### Q11. Redis 集群方案有哪些？

**参考答案**

三种主流方案：

1. **主从复制（Master-Slave）**：读写分离，一主多从，从节点异步复制。无法自动故障转移。
2. **Sentinel 哨兵**：在主从基础上加 Sentinel 进程监控，自动选主并切换。但仍是主从架构，存储受单机内存限制。
3. **Cluster 集群**：16384 个哈希槽分布在多主节点上，每节点处理一部分槽，自带故障转移和水平扩展能力。

**选择建议**

- 数据量小（< 10G）：Sentinel 足够。
- 数据量大（> 10G）：Cluster。
- 强一致性：不用 Redis，改用 Zookeeper / etcd。

---

### Q12. Redis 主从复制原理？

**参考答案**

主从复制分两个阶段：

1. **全量同步（Full Sync）**：从节点首次连主节点时，主执行 `bgsave` 生成 RDB 发给从，从加载后主再发送缓冲期间的写命令。
2. **增量同步（Partial Resync）**：网络抖动恢复时，从发 `PSYNC offset`，主从 `repl_backlog` 环形缓冲区中拷贝 offset 之后的命令。

**核心数据结构**

- `replication_id`：主节点唯一标识，重启或切换后会变。
- `repl_backlog`：主节点维护的环形缓冲区，默认 1MB，断连后只要 offset 还在就能增量同步。

**追问**

主从延迟怎么解决？`WAIT numreplicas timeout` 强制等待指定副本确认，但会降低可用性。

---

### Q13. Redis Sentinel 哨兵工作原理？

**参考答案**

Sentinel 是 Redis 的高可用方案，通常部署 3~5 个 Sentinel 节点形成集群。核心职责：

1. **监控（Monitor）**：每秒 PING 所有主从节点，超过 `down-after-milliseconds` 未响应则标记为主观下线（SDOWN）。
2. **选主（Leader Election）**：多数 Sentinel 认为某主客观下线（ODOWN）后，Raft-like 协议选举一个 Sentinel Leader。
3. **故障转移（Failover）**：Leader Sentinel 选一个数据最新的从升级为主，让其他从切换复制新主，并通知客户端。

**加分项**

能说出 Sentinel 至少需要 3 个节点（多数派需要 ≥ 2 票），且配置 `quorum` 影响客观下线判定。

---

### Q14. Redis Cluster 哈希槽？

**参考答案**

Cluster 把整个 key 空间划分成 **16384 个哈希槽**（CRC16 mod 16384），每个主节点负责一部分槽。Key 通过 `CRC16(key) % 16384` 映射到槽。

**为什么是 16384？**

- 16384 = 2^14，集群间通过 gossip 协议同步槽位映射时，每个节点的槽位图用 2KB bitmap 就能存下（16384 bit = 2048 byte）。
- 槽数太多会增加心跳包大小和网络开销，太少又不利于均匀分片。

**Key 定位流程**

```text
client → cluster → 计算 CRC16(key) % 16384 → 查槽位映射表
                                    │
                            若槽不在本节点
                                    │
                            返回 MOVED 重定向
                                    │
                            client 重新连接目标节点
```

---

### Q15. Redis 事务支持 ACID 吗？

**参考答案**

Redis 事务通过 `MULTI / EXEC / DISCARD / WATCH` 实现，但**只满足部分 ACID**：

| 特性 | 是否满足 | 说明 |
|------|----------|------|
| **Atomicity** | 部分 | 队列中的命令要么都执行要么都不执行，但单条命令失败不回滚 |
| **Consistency** | 满足 | 约束由 Redis 内部维护 |
| **Isolation** | 满足 | 单线程串行执行，无并发 |
| **Durability** | 取决于持久化 | 仅当 AOF always 时才真正持久 |

**追问**

Redis 事务 vs Lua 脚本？Lua 脚本里多条命令是原子执行（期间不会被其他命令插入），且能基于前面命令的结果做逻辑判断，更强大。

---

## 四、运维实战篇

### Q16. Redis 持久化如何选择？

**场景化建议**

- **纯缓存，可容忍丢数据**：关闭持久化，节省 IO。
- **缓存 + 数据库，丢少量数据可接受**：RDB（定时快照）。
- **数据不能丢**：AOF `everysec` + 混合持久化 + 主从复制 + 定期备份 RDB。

**生产配置**

```conf
# RDB
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes

# AOF
appendonly yes
appendfsync everysec
aof-use-rdb-preamble yes
```

---

### Q17. Redis 数据类型底层实现？

| 类型 | 底层结构 | 关键操作复杂度 |
|------|----------|----------------|
| String | int / embstr / raw SDS | O(1) |
| Hash | listpack（≤128 field）/ HT | O(1) ~ O(N) |
| List | quicklist（listpack 链表） | 头尾 O(1)，中间 O(N) |
| Set | intset（纯整数）/ HT | O(1) |
| ZSet | listpack + skiplist + dict | O(log N) |

**核心考点**

- ZSet 用了两个结构：跳表做范围查询，dict 提供 O(1) 查 score。
- listpack 替代了 ziplist，解决了级联更新问题。
- Redis 7 的 List 统一 quicklist，不再在 linkedlist 和 ziplist 间切换。

---

### Q18. Redis 跳表原理？

**参考答案**

跳表（SkipList）是有序集合 ZSet 的核心数据结构（Redis 7 之前）。多层索引 + 链表，查找从顶层往下，跨度逐层缩小，类似二分查找。

**时间复杂度**

- 查找 / 插入 / 删除：平均 O(log N)，最坏 O(N)。
- 范围查询：`ZREVRANGEBYSCORE` 通过跳表头尾指针 O(log N + M) 拿到。

**层数生成**

每个节点晋升到上一层的概率是 0.25（Redis 默认），层数上限 32。`Math.random() < 0.25` 控制随机晋升。

**加分项**

为什么不用红黑树？Redis 作者 antirez 说过跳表实现更简单，调试更容易，范围操作不需要中序遍历回溯。详见 [🦘 跳表手撕](/08-interview/skiplist-coding)。

---

### Q19. Redis 单线程为什么快？

**核心原因汇总**

1. **纯内存访问**：纳秒级响应，比磁盘 IO 快 10 万倍。
2. **非阻塞 IO + epoll**：单线程处理上万连接，避免 select 轮询开销。
3. **单线程避免锁竞争**：数据结构无需加锁，无上下文切换。
4. **C 语言 + jemalloc**：连续内存分配，CPU 缓存命中率高。
5. **协议简单**：RESP 协议文本/二进制混合，解析开销小。

**误区澄清**

"单线程"≠ "慢"。Redis 性能瓶颈是网络和内存带宽，不是 CPU。多线程反而会引入同步开销，得不偿失。

---

### Q20. Redis IO 多路复用？

**参考答案**

IO 多路复用（Multiplexing）让单个线程同时监听多个文件描述符，一旦某个 FD 就绪就通知线程处理。Redis 用 `aeEventLoop` 抽象层封装系统调用：

```text
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   epoll     │     │   kqueue    │     │   select    │
│  (Linux)    │     │  (BSD/macOS)│     │  (Windows)  │
└─────────────┘     └─────────────┘     └─────────────┘
       ↓                   ↓                   ↓
       └──────────────┬────┴───────────────────┘
                      ↓
              aeEventLoop (事件循环)
                      ↓
         ┌────────────┼────────────┐
         ↓            ↓            ↓
      时间事件     IO事件      beforeSleep
```

**epoll 优势**

- 无连接数限制（select 受 FD_SETSIZE 1024 限制）。
- 回调通知，无需遍历所有 FD。
- O(1) 复杂度，百万连接下依然高效。

---

## 下一步

到这里你已经掌握 20 道高频基础题。下一篇进入**进阶题**，覆盖集群脑裂、Redlock、Tracking、新特性等深度话题。

**下一步：** [📝 高频面试题（下）](/08-interview/advanced)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
