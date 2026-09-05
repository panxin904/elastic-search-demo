---
title: Sentinel 哨兵
date: 2026-08-15  # date-auto-injected
---

# 🛡️ Sentinel 哨兵

> Sentinel 是 Redis 官方的高可用方案。它在主从复制的基础上，部署一组独立的"哨兵进程"，持续监控 Master/Replica 状态，自动完成故障检测与故障转移。理解 Sentinel，就是理解"分布式共识 + 自动化运维"如何落地。

<ClientOnly>
  <DataStructureViz />
</ClientOnly>

## 一、Sentinel 的诞生

主从复制解决不了一个关键问题：**Master 挂了怎么办**？如果只能人工介入，凌晨 3 点的告警电话基本是每个 Redis 运维的噩梦。Sentinel 把这件事自动化——监控、选主、通知、配置更新，全部由 Sentinel 集群自己完成。

```text
   ┌──────────────────────────────────────────────────┐
   │               Sentinel Cluster                    │
   │                                                  │
   │   ┌─────────┐  ┌─────────┐  ┌─────────┐          │
   │   │Sentnel-1│  │Sentnel-2│  │Sentnel-3│  (奇数) │
   │   │ :26379  │  │ :26379  │  │ :26379  │          │
   │   └────┬────┘  └────┬────┘  └────┬────┘          │
   │        │ pub/sub     │ pub/sub    │ pub/sub       │
   └────────┼─────────────┼───────────┼───────────────┘
            │             │           │
   ─────────┼─────────────┼───────────┼───────────────
            ▼             ▼           ▼
        ┌───────────────────────────────┐
        │      Data Nodes               │
        │                               │
        │  Master ◀───── Replica1       │
        │  6379          6380           │
        │       ◀───── Replica2        │
        │                6381           │
        └───────────────────────────────┘
```

**为什么至少 3 个**？因为 Sentinel 用类似 Raft 的多数派协议判断"Master 是否真的下线"，少数服从多数能容忍 1 台 Sentinel 故障。3 节点可容忍 1 节点故障，5 节点可容忍 2 节点故障。

## 二、SDOWN 与 ODOWN

Sentinel 区分两个层级的主观判断与客观判断，这是分布式系统经典的"最终一致"思想：

```text
   Sentinel-1                         Sentinel-2   Sentinel-3
       │                                  │            │
   ping Master ──┐                        │            │
       │        │ no response             │            │
       │        ▼                         │            │
   标记 SDOWN   │                  ping   │   ping     │
   (主观下线)   │                  正常    │   正常     │
                │                        │            │
                └──── "is-master-down-by-addr" ──────▶│
                         询问：Master 真的挂了吗？
                         
   ┌─────────────────────────────────────────────┐
   │ 当 ≥ quorum 个 Sentinel 都报告 SDOWN        │
   │ 才升级为 ODOWN（客观下线），开始故障转移     │
   └─────────────────────────────────────────────┘
```

| 概念 | 含义 | 触发者 | 持久态？ |
|------|------|--------|---------|
| **SDOWN** | 单个 Sentinel 认为 Master 不可达 | 单个 Sentinel | 否，本地状态 |
| **ODOWN** | 多数 Sentinel 都认为 Master 不可达 | 多数派共识 | 是，触发 failover |

这种设计避免了"网络抖动导致误判"——只有多数 Sentinel 都看不到 Master 响应，才认定真的挂了。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Redis Sentinel 故障转移流程</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">SDOWN/ODOWN · Leader 选举 · 故障切换</text>

  <!-- 主从 -->
  <rect class="at-hover-card" x="30" y="100" width="120" height="50" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="90" y="123" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">Master (旧)</text>
  <text x="90" y="140" text-anchor="middle" font-size="9" fill="#475569">宕机 ↓</text>

  <rect class="at-hover-card" x="30" y="170" width="120" height="50" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="90" y="193" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">Replica A</text>
  <text x="90" y="210" text-anchor="middle" font-size="9" fill="#475569">candidate</text>

  <rect class="at-hover-card" x="30" y="240" width="120" height="50" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="90" y="263" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">Replica B</text>
  <text x="90" y="280" text-anchor="middle" font-size="9" fill="#475569">candidate</text>

  <!-- Sentinel 三节点 -->
  <rect class="at-hover-card" x="220" y="100" width="160" height="60" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="300" y="125" text-anchor="middle" font-size="12" font-weight="700" fill="#5b21b6">Sentinel-1</text>
  <text x="300" y="143" text-anchor="middle" font-size="10" fill="#475569">PING / 10s 心跳</text>

  <rect class="at-hover-card" x="220" y="170" width="160" height="60" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="300" y="195" text-anchor="middle" font-size="12" font-weight="700" fill="#5b21b6">Sentinel-2 (Leader)</text>
  <text x="300" y="213" text-anchor="middle" font-size="10" fill="#475569">RAFT 多数派选出</text>

  <rect class="at-hover-card" x="220" y="240" width="160" height="60" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="300" y="265" text-anchor="middle" font-size="12" font-weight="700" fill="#5b21b6">Sentinel-3</text>
  <text x="300" y="283" text-anchor="middle" font-size="10" fill="#475569">投票给 S-2</text>

  <!-- 客户端 -->
  <rect class="at-hover-card" x="440" y="170" width="130" height="60" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="505" y="195" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Client</text>
  <text x="505" y="213" text-anchor="middle" font-size="9" fill="#475569">订阅 +switch-master</text>

  <!-- 箭头 -->
  <line x1="150" y1="125" x2="220" y2="125" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arr)" stroke-dasharray="3,2"/>
  <text x="155" y="115" font-size="9" fill="#dc2626">PONG 缺失</text>
  <line x1="150" y1="195" x2="220" y2="195" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)" stroke-dasharray="3,2"/>
  <line x1="150" y1="265" x2="220" y2="265" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)" stroke-dasharray="3,2"/>

  <line x1="380" y1="200" x2="440" y2="200" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>
  <text x="385" y="190" font-size="9" fill="#10b981">+switch-master</text>

  <!-- 流程步骤 -->
  <text x="300" y="335" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">4 阶段故障转移</text>

  <rect class="at-hover-card" x="30" y="350" width="125" height="55" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="92" y="373" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">① SDOWN</text>
  <text x="92" y="393" text-anchor="middle" font-size="9" fill="#475569">单 sentinel</text>

  <rect class="at-hover-card" x="165" y="350" width="125" height="55" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="227" y="373" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">② ODOWN</text>
  <text x="227" y="393" text-anchor="middle" font-size="9" fill="#475569">quorum 多数</text>

  <rect class="at-hover-card" x="300" y="350" width="125" height="55" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="362" y="373" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">③ 选 Leader</text>
  <text x="362" y="393" text-anchor="middle" font-size="9" fill="#475569">RAFT 一轮</text>

  <rect class="at-hover-card" x="435" y="350" width="135" height="55" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="502" y="373" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">④ failover</text>
  <text x="502" y="393" text-anchor="middle" font-size="9" fill="#475569">slaveof no one</text>

  <line x1="155" y1="377" x2="165" y2="377" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="290" y1="377" x2="300" y2="377" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="425" y1="377" x2="435" y2="377" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- 关键点 -->
  <text x="300" y="430" text-anchor="middle" font-size="11" font-weight="700" fill="#1e293b">quorum 配置</text>
  <text x="300" y="448" text-anchor="middle" font-size="10" fill="#475569">quorum=N / M 个 sentinel：至少 N 个判定 SDOWN 后 ODOWN 触发 failover</text>
  <text x="300" y="465" text-anchor="middle" font-size="10" fill="#475569">推荐：3 节点 sentinel + quorum=2（容忍 1 节点宕机，避免脑裂）</text>
</svg>

## 三、Leader 选举（Raft 思想）

ODOWN 触发后，多个 Sentinel 不会同时执行 failover，而是先选出一个 Leader Sentinel，由它主导整个故障转移过程。

```text
   S1              S2              S3
    │               │               │
    │ vote-for S1   │               │
    ├──────────────▶│               │
    │               │ vote-for S1   │
    │               ├──────────────▶│
    │               │               │
    │◀──────────────┤               │
    │  同意票        │               │
    │               │               │
    │      T1 (election epoch = 1)   │
    │                               │
    │      S1 收到 2 票 (quorum=2)  │
    │      赢得选举，成为 Leader     │
    ▼                               ▼
   开始 failover
```

选举细节（参考 `src/sentinel.c`）：
- 每个 Sentinel 有随机超时（1500-3000ms），先到期的先发起投票。
- 每个 epoch 内只能投一票，先到先得。
- 获得 `>= quorum` 票数的 Sentinel 立即成为 Leader。
- 若一轮选举超时无人获多数派，进入下一 epoch 重选。

这与 Raft 一致：任期（epoch）+ 多数派 + 随机超时三件套。

## 四、故障转移完整流程

Leader Sentinel 选出后，按以下步骤执行故障转移（耗时通常 10-30 秒）：

```text
  步骤 1：选主
    从 Replica 列表中按规则打分，选出"最合适的"新 Master
       │
       ▼
  步骤 2：晋升
    对选中的 Replica 发送 SLAVEOF NO ONE（REPLICAOF NO ONE）
    让它停止复制、晋升为 Master
       │
       ▼
  步骤 3：通知其他 Replica
    对其余 Replica 发送 REPLICAOF <new_master> <port>
    让它们切换复制目标到新 Master
       │
       ▼
  步骤 4：更新配置纪元
    在新 Master 上执行 CONFIG SET cluster-announce-ip ...
    让所有 Sentinel 感知到新拓扑
       │
       ▼
  步骤 5：老 Master 复活后
    老 Master 重新加入，自动成为新 Master 的 Replica
```

**选主打分规则**（源码 `getMaxConnectionScore` 等函数）：
1. 排除 `down-after-milliseconds * 10` 毫秒内断连过的 Replica。
2. 优先选 `replica-priority` 最低的（默认 100，可手动调）。
3. 相同优先级选 `replication offset` 最大的（数据最新）。
4. 仍相同选 `runid` 字典序最小的。

## 五、Sentinel 配置详解

最小可用配置（`sentinel.conf`）：

```conf
# Sentinel 端口
port 26379

# 后台运行
daemonize yes

# 日志
logfile "/var/log/redis/sentinel.log"

# 监控一个名为 mymaster 的 Master
# 格式：sentinel monitor <name> <ip> <port> <quorum>
sentinel monitor mymaster 192.168.1.10 6379 2

# Master 多少毫秒无响应判定为 SDOWN
sentinel down-after-milliseconds mymaster 30000

# 多少毫秒后仍未恢复则视为故障，开始 failover
sentinel failover-timeout mymaster 180000

# failover 时同时同步新数据的 Replica 数（控制雪崩）
sentinel parallel-syncs mymaster 1

# 鉴权（如果 Master 设置了 requirepass）
sentinel auth-pass mymaster your-strong-password

# 通知脚本（Master 切换时触发）
sentinel notification-script mymaster /opt/notify.sh
```

启动 Sentinel：

```bash
# 命令行启动
redis-sentinel /path/to/sentinel.conf

# 或者 redis-server 加 --sentinel 参数
redis-server /path/to/sentinel.conf --sentinel
```

## 六、核心参数详解

| 参数 | 默认值 | 作用 | 调优建议 |
|------|--------|------|----------|
| `down-after-milliseconds` | 30000 | 判定 SDOWN 的超时阈值 | 网络稳定可调小到 5000；网络抖动大调大到 60000 |
| `parallel-syncs` | 1 | failover 时同时同步的 Replica 数 | 设为 1 避免新 Master IO 雪崩；网络强可调大 |
| `failover-timeout` | 180000 | 整个 failover 的最长耗时 | 必须大于 `down-after-milliseconds` × 3 |
| `quorum` | (无默认) | 判定 ODOWN 需要的票数 | 通常 `(Sentinel 个数 / 2) + 1` |
| `notification-script` | 无 | 故障切换时触发的脚本 | 用于发钉钉/企微告警 |

`parallel-syncs` 是生产中非常容易踩坑的参数：如果设为 N，failover 时 N 个 Replica 会**同时**从新 Master 拉全量 RDB，把新 Master 打挂。保守起见通常设为 1。

## 七、生产案例

**案例：Sentinel 误切导致业务抖动**

某金融系统部署 3 个 Sentinel，`down-after-milliseconds` 设为 5000（5 秒）。某次主库做 1 次慢查询 GC 暂停了 7 秒，Sentinel 集体判定 ODOWN，触发 failover，业务中断 20 秒。

**根因**：GC 暂停 > `down-after-milliseconds` 阈值，被误判为下线。

**解决方案**：
1. 把 `down-after-milliseconds` 调到 30000（30 秒），容忍偶发 GC。
2. 关键业务设双 Sentinel 集群，互相独立判断。
3. 上游接入层加熔断，failover 期间不立刻切流量，等 30 秒观察新 Master 稳定后再切换。

## 八、Sentinel 客户端接入

Java 客户端通过 `JedisSentinelPool` 连接：

```java
Set<String> sentinels = new HashSet<>();
sentinels.add("192.168.1.10:26379");
sentinels.add("192.168.1.11:26379");
sentinels.add("192.168.1.12:26379");

JedisPoolConfig poolConfig = new JedisPoolConfig();
poolConfig.setMaxTotal(200);
poolConfig.setMaxIdle(50);

JedisSentinelPool pool = new JedisSentinelPool(
    "mymaster",   // Master 名称
    sentinels,    // Sentinel 节点列表
    poolConfig,
    3000          // 连接超时
);

try (Jedis jedis = pool.getResource()) {
    jedis.set("key", "value");
}
```

客户端通过订阅 Sentinel 的 `+switch-master` 频道感知 Master 切换，无需重启即可自动连接新 Master。

![Redis Sentinel Vs Cluster](/redis-sentinel-vs-cluster.svg)

## 九、Sentinel vs Cluster

| 维度 | Sentinel | Cluster |
|------|----------|---------|
| 数据分片 | ❌ 单一 Master | ✅ 16384 槽位分散到多 Master |
| 写入扩展 | ❌ 仍是单点写入 | ✅ 多 Master 并行写入 |
| 内存上限 | 受单 Master 内存限制 | 整体 = N × 单机内存 |
| 部署复杂度 | 低 | 中（需要 ruby 脚本或 redis-cli 集群模式） |
| 适用场景 | 数据量 < 10GB | 数据量 > 10GB 或写并发极高 |

如果你的业务数据能装进单台机器（内存够大），Sentinel 是首选；如果数据量膨胀到单机装不下，就必须上 Cluster。

**下一步：** [🌐 Cluster 集群](/04-cluster/cluster)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）

<!-- svg-injected:do-not-edit -->

## 图示：Redis Sentinel 高可用

![Redis Sentinel 高可用](/redis-sentinel.svg)
