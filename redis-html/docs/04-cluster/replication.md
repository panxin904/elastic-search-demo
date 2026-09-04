---
title: 主从复制
date: 2026-08-15  # date-auto-injected
---

# 🔁 主从复制 Replication

> 主从复制是 Redis 高可用的基石。一台 Master 负责处理写请求，多台 Replica 自动同步数据并提供只读服务，既分担读压力，又为故障转移提供数据副本。理解主从复制，是理解 Sentinel 与 Cluster 的前置条件。

<ClientOnly>
  <DataStructureViz />
</ClientOnly>

![Redis Replication Psync](/redis-replication-psync.svg)

## 一、为什么需要主从复制

单机 Redis 存在三个致命问题：**单点故障**（进程挂了就停服）、**读压力无法分担**（所有读都打到同一台机器）、**容量瓶颈**（单实例内存再大也有上限）。主从复制直接解决前两个，第三个留给 Cluster。

```text
                  写请求
                   │
                   ▼
        ┌─────────────────────┐
        │       Master        │
        │   6379 (读写)       │
        └──────────┬──────────┘
                   │ 异步同步 RDB + 命令流
        ┌──────────┼──────────┐
        ▼          ▼          ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ Replica1 │ │ Replica2 │ │ Replica3 │
  │ 6380只读 │ │ 6381只读 │ │ 6382只读 │
  └──────────┘ └──────────┘ └──────────┘
       ▲          ▲          ▲
       └────────读请求───────┘
```

默认配置下 Replica 只接受 `READONLY` 连接，写命令会被拒绝。这种"读写分离"模式让主库专心写、副库专心读，读吞吐可以随 Replica 数量线性扩展。

## 二、全量同步（首次连接）

当 Replica 第一次连上 Master、或者断开太久导致 offset 差距过大时，会触发**全量同步（Full Resync）**。这是最重的同步路径，需要 Master 把整个数据集传给 Replica。

```text
   Replica                      Master
      │                            │
      │── PSYNC ? -1 ─────────────▶│  1. 报告自己不知道 runid
      │                            │     也不知道 offset
      │                            │
      │◀── +FULLRESYNC runid 1000 ─│  2. 分配 runid 并告知当前 offset
      │                            │
      │                            │  3. fork 子进程 bgsave 生成 RDB
      │                            │     同时写入 replication buffer
      │◀───── RDB 文件传输 ───────│  4. 通过 socket 传 RDB
      │                            │
      │   5. 清空旧数据 + 加载 RDB  │
      │◀──── replication buffer ──│  6. 把 bgsave 期间新增的命令重放
      │                            │
      │── +CONTINUE offset=1050 ──▶│  7. 进入命令传播阶段
```

四个关键点：
- **`bgsave` 阻塞**：Master `fork` 子进程生成 RDB 时，父进程仍可服务，但 `fork` 本身会阻塞（内存越大阻塞越久，业内经验值是 10GB 内存 `fork` 约 20-50ms）。
- **replication buffer**：bgsave 期间所有新写命令会被同时写入这个临时 buffer，RDB 传完后立刻重放，保证最终一致。
- **磁盘 vs 无盘**：默认 Replica 先把 RDB 落盘再加载；可以配置 `repl-diskless-sync yes` 让 Master 直接把 RDB 通过 socket 喂给 Replica，省一次磁盘 IO。
- **无盘复制适用场景**：磁盘慢但网卡快（如云主机），且 Replica 距离 Master 很近（避免网络成为瓶颈）。

## 三、增量同步（PSYNC）

绝大多数时候网络抖动后 Replica 重连，只需要补齐断开期间丢失的命令，而不是全量重传。这就是 **PSYNC 增量同步**。

Redis 在 Master 端维护两个关键结构：

```text
   ┌─────────────────────────────────┐
   │   repl_backlog (环形缓冲区)     │
   │   默认 1MB，可配置              │
   │                                 │
   │   ┌───┬───┬───┬───┬───┬───┬───┐ │
   │   │ A │ B │ C │ D │ E │ F │ G │ │
   │   └───┴───┴───┴───┴───┴───┴───┘ │
   │       ▲                       ▲ │
   │    写指针                  读指针 │
   └─────────────────────────────────┘

   ┌──────────────────────────────┐
   │   replica offset 映射表      │
   │   记录每个 Replica 当前 offset│
   └──────────────────────────────┘
```

Replica 重连时发送 `PSYNC <runid> <offset>`：
- 如果 `runid` 匹配且 offset 还在 backlog 内 → 返回 `+CONTINUE`，只传缺失的命令。
- 否则返回 `+FULLRESYNC`，退化到全量同步。

`repl-backlog-size` 决定了能容忍多长的网络断连。经验公式：`backlog_size = (平均写速率 byte/s) × (最长可接受断连秒数)`。生产环境通常配到 100MB-1GB，避免断连后回退到全量。

## 四、复制风暴与树形结构

如果一个 Master 挂了 N 个 Replica，Master 重启后所有 Replica 同时发起全量同步，会把 Master 的网卡和 CPU 打爆——这就是**复制风暴**。

```text
   ❌ 星形结构（复制风暴）
              Master
       ┌─────┬─────┬─────┐
       ▼     ▼     ▼     ▼
      R1    R2    R3    R4      同时全量同步

   ✅ 树形结构（错峰同步）
              Master
                │
              R1 (主副本)
        ┌─────┬─────┬─────┐
        ▼     ▼     ▼     ▼
       R2    R3    R4    R5      只有 R1 在同步 Master
```

在云厂商的 Redis 服务中（如阿里云 Redis 社区版高可用架构），往往采用树形复制——主副本从 Master 同步，其他副本从主副本同步，错峰 + 分流。

## 五、心跳机制与超时判定

Master 和 Replica 之间通过周期性 PING/PONG 维持心跳：

```conf
# Master 每 10 秒向 Replica 发送 PING
repl-ping-replica-period 10

# Replica 超过 60 秒没收到 PING 视为下线
repl-timeout 60
```

判断逻辑（简化）：

```text
Master 端：
  for each replica:
      last_ping_time = 上次收到 PONG 的时间
      if now - last_ping_time > repl-timeout:
          mark replica as offline
          释放 client 连接

Replica 端：
  for each master:
      last_pong_time = 上次收到 PING/PONG 的时间
      if now - last_pong_time > repl-timeout:
          disconnect and try to reconnect
```

⚠️ **生产踩坑**：`repl-timeout` 必须大于 `repl-ping-replica-period`，否则会出现"误判下线-重连-误判"的抖动循环。安全起见把 `repl-timeout` 设为 ping 间隔的 5-10 倍。

## 六、配置示例

完整 `redis.conf` 主从配置（Master 端）：

```conf
# 绑定地址
bind 0.0.0.0
port 6379

# 开启 AOF（保证 repl buffer 期间不丢数据）
appendonly yes
appendfsync everysec

# 复制 backlog 大小
repl-backlog-size 256mb
repl-backlog-ttl 3600

# 心跳间隔（秒）
repl-ping-replica-period 10
repl-timeout 60

# Master 写入时是否阻塞 N 个 Replica 同步后才返回
# 用于强一致场景，慎用
min-replicas-to-write 1
min-replicas-max-lag 10
```

Replica 端配置（两种方式）：

```conf
# 方式 1：配置文件（旧版本用 slaveof）
replicaof 192.168.1.10 6379
replica-serve-stale-data yes    # 同步完成前是否响应旧数据
replica-read-only yes           # 是否只读

# 方式 2：运行时命令
redis-cli -p 6380 REPLICAOF 192.168.1.10 6379

# 取消复制（晋升为 Master）
redis-cli -p 6380 REPLICAOF NO ONE
```

`replica-serve-stale-data yes` 是个容易被忽视的关键配置：设为 `yes` 时，Replica 在同步完成前仍能用旧数据响应读请求，避免全量同步期间读流量打到 Master 造成雪崩。

## 七、生产案例

**案例：电商大促期间主从延迟导致超卖**

某电商在大促开始瞬间，主库写入并发冲到 10w QPS，但 Replica 同步有 2-3 秒延迟。用户在主库下单后立刻查询订单列表（路由到 Replica），看不到刚才的订单，重复点击导致超卖。

**解决方案**：
1. 关键读写强制走 Master（`@Transactional` 内查写同源）。
2. 缓存预热 + 写入后短暂 TTL 延长，让 Replica 有时间追上。
3. `min-replicas-max-lag 10` 配置兜底——延迟超过 10 秒 Master 拒绝写入。

## 八、主从复制的局限

主从复制解决了"读写扩展"和"数据冗余"，但**没有自动故障转移**——Master 挂了需要运维手动把某个 Replica 提升为新 Master，然后改其他 Replica 的复制目标。这就是下一节 **Sentinel** 要解决的问题。

| 维度 | 单机 | 主从复制 | Sentinel |
|------|------|----------|----------|
| 读扩展 | ❌ | ✅ | ✅ |
| 写扩展 | ❌ | ❌ | ❌ |
| 数据冗余 | ❌ | ✅ | ✅ |
| 自动故障转移 | ❌ | ❌ | ✅ |
| 水平分片 | ❌ | ❌ | ❌ |

**下一步：** [🛡️ Sentinel 哨兵](/04-cluster/sentinel)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
