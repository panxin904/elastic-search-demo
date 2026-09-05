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

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis Sentinel vs Cluster</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">两种高可用方案对比 · 容量上限 · 数据分片 · 选型决策</text>

  <!-- Sentinel 方案 -->
  <g>
    <text x="60" y="95" font-size="13" font-weight="700" fill="#1e293b">① Sentinel 模式（主从 + 故障转移）</text>

    <rect class="at-hover-card" x="40" y="115" width="250" height="220" rx="8" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="165" y="138" text-anchor="middle" font-size="12" font-weight="700" fill="#1e40af">Sentinel 集群</text>

    <!-- 3 sentinels -->
    <rect class="at-hover-card" x="60" y="155" width="60" height="40" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="90" y="178" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">S1</text>

    <rect class="at-hover-card" x="125" y="155" width="60" height="40" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="155" y="178" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">S2</text>

    <rect class="at-hover-card" x="190" y="155" width="60" height="40" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="220" y="178" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">S3</text>

    <!-- Master -->
    <rect class="at-hover-card" x="60" y="215" width="80" height="40" rx="4" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="100" y="238" text-anchor="middle" font-size="11" font-weight="700" fill="#065f46">Master</text>

    <!-- Replicas -->
    <rect class="at-hover-card" x="145" y="215" width="60" height="40" rx="4" fill="#f1f5f9" stroke="#94a3b8"/>
    <text x="175" y="238" text-anchor="middle" font-size="10" fill="#475569">R1</text>

    <rect class="at-hover-card" x="210" y="215" width="60" height="40" rx="4" fill="#f1f5f9" stroke="#94a3b8"/>
    <text x="240" y="238" text-anchor="middle" font-size="10" fill="#475569">R2</text>

    <!-- 连接 -->
    <line x1="100" y1="255" x2="175" y2="255" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>
    <line x1="100" y1="255" x2="240" y2="255" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>

    <!-- 文字说明 -->
    <text x="60" y="275" font-size="10" fill="#475569">✓ 部署简单 · 客户端 SDK 友好</text>
    <text x="60" y="290" font-size="10" fill="#475569">✗ 单 Master 容量瓶颈</text>
    <text x="60" y="305" font-size="10" fill="#475569">✗ 写无法水平扩展</text>
    <text x="60" y="320" font-size="10" fill="#dc2626" font-weight="700">容量：受限于单机内存</text>
  </g>

  <!-- Cluster 方案 -->
  <g>
    <text x="320" y="95" font-size="13" font-weight="700" fill="#1e293b">② Cluster 模式（数据分片）</text>

    <rect class="at-hover-card" x="310" y="115" width="250" height="220" rx="8" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="435" y="138" text-anchor="middle" font-size="12" font-weight="700" fill="#065f46">Cluster 集群</text>

    <!-- 3 master + 3 replica -->
    <rect class="at-hover-card" x="325" y="155" width="60" height="40" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="355" y="178" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">M1</text>

    <rect class="at-hover-card" x="390" y="155" width="60" height="40" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="420" y="178" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">M2</text>

    <rect class="at-hover-card" x="455" y="155" width="60" height="40" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="485" y="178" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">M3</text>

    <rect class="at-hover-card" x="325" y="215" width="60" height="40" rx="4" fill="#f1f5f9" stroke="#94a3b8"/>
    <text x="355" y="238" text-anchor="middle" font-size="10" fill="#475569">R1</text>

    <rect class="at-hover-card" x="390" y="215" width="60" height="40" rx="4" fill="#f1f5f9" stroke="#94a3b8"/>
    <text x="420" y="238" text-anchor="middle" font-size="10" fill="#475569">R2</text>

    <rect class="at-hover-card" x="455" y="215" width="60" height="40" rx="4" fill="#f1f5f9" stroke="#94a3b8"/>
    <text x="485" y="238" text-anchor="middle" font-size="10" fill="#475569">R3</text>

    <!-- Gossip -->
    <line x1="355" y1="195" x2="420" y2="195" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)" stroke-dasharray="3"/>
    <line x1="420" y1="195" x2="485" y2="195" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)" stroke-dasharray="3"/>

    <!-- 文字说明 -->
    <text x="325" y="275" font-size="10" fill="#475569">✓ 数据分片 16384 slot</text>
    <text x="325" y="290" font-size="10" fill="#475569">✓ 写水平扩展（多个 Master）</text>
    <text x="325" y="305" font-size="10" fill="#475569">✗ 多 key 操作受限于同一 slot</text>
    <text x="325" y="320" font-size="10" fill="#dc2626" font-weight="700">容量：N × 单机内存</text>
  </g>

  <!-- 选型决策 -->
  <g>
    <rect class="at-hover-card" x="40" y="350" width="525" height="100" rx="8" fill="#fef9c3" stroke="#facc15" stroke-width="2"/>

    <text x="60" y="372" font-size="13" font-weight="700" fill="#854d0e">选型决策</text>

    <text x="60" y="392" font-size="10" fill="#854d0e">• 数据量 &lt; 10GB + 简单 → <tspan font-weight="700" fill="#1e40af">Sentinel</tspan></text>
    <text x="60" y="407" font-size="10" fill="#854d0e">• 数据量 &gt; 50GB + 高写吞吐 → <tspan font-weight="700" fill="#065f46">Cluster</tspan></text>
    <text x="60" y="422" font-size="10" fill="#854d0e">• 业务要求 Lua/Multi 原子多 key → <tspan font-weight="700" fill="#1e40af">Sentinel</tspan>（hash tag 强制同 slot 复杂）</text>
    <text x="60" y="437" font-size="10" fill="#854d0e">• 大公司 / 缓存 + 数据库分离 → <tspan font-weight="700" fill="#065f46">Cluster</tspan></text>
  </g>
</svg>
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

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis Sentinel 高可用</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Sentinel 集群 · 自动故障转移</text>

  <!-- 客户端 -->
  <rect class="at-hover-card" x="40" y="220" width="100" height="40" rx="6" fill="#3b82f6" opacity="0.9"/>
  <text x="90" y="245" text-anchor="middle" font-size="12" font-weight="700" fill="white">客户端</text>

  <!-- Sentinel 集群 -->
  <g font-size="11" font-weight="700">
    <rect class="at-hover-card" x="200" y="100" width="160" height="40" rx="6" fill="#ec4899" opacity="0.95"/>
    <text x="280" y="118" text-anchor="middle" fill="white">Sentinel 1</text>
    <text x="280" y="132" text-anchor="middle" font-size="9" fill="#fce7f3">主观/客观下线</text>

    <rect class="at-hover-card" x="200" y="150" width="160" height="40" rx="6" fill="#ec4899" opacity="0.95"/>
    <text x="280" y="168" text-anchor="middle" fill="white">Sentinel 2</text>
    <text x="280" y="182" text-anchor="middle" font-size="9" fill="#fce7f3">投票选举</text>

    <rect class="at-hover-card" x="200" y="200" width="160" height="40" rx="6" fill="#ec4899" opacity="0.95"/>
    <text x="280" y="218" text-anchor="middle" fill="white">Sentinel 3</text>
    <text x="280" y="232" text-anchor="middle" font-size="9" fill="#fce7f3">配置下发</text>
  </g>

  <!-- 主从节点 -->
  <g font-size="11" font-weight="700">
    <rect class="at-hover-card" x="430" y="100" width="130" height="60" rx="6" fill="#10b981" opacity="0.9"/>
    <text x="495" y="125" text-anchor="middle" fill="white">Redis Master</text>
    <text x="495" y="140" text-anchor="middle" font-size="9" fill="#d1fae5">读写</text>
    <text x="495" y="153" text-anchor="middle" font-size="9" fill="#d1fae5">写操作</text>

    <rect class="at-hover-card" x="430" y="180" width="120" height="40" rx="6" fill="#94a3b8" opacity="0.85"/>
    <text x="490" y="203" text-anchor="middle" fill="white">Replica 1</text>
    <text x="490" y="215" text-anchor="middle" font-size="9" fill="#f1f5f9">读</text>

    <rect class="at-hover-card" x="430" y="230" width="120" height="40" rx="6" fill="#94a3b8" opacity="0.85"/>
    <text x="490" y="253" text-anchor="middle" fill="white">Replica 2</text>
    <text x="490" y="265" text-anchor="middle" font-size="9" fill="#f1f5f9">读</text>
  </g>

  <!-- 心跳箭头 -->
  <g stroke="#ec4899" stroke-width="1.5" fill="none" stroke-dasharray="4 3" marker-end="url(#arrow)">
    <line x1="360" y1="120" x2="430" y2="120"/>
    <line x1="360" y1="170" x2="430" y2="130"/>
    <line x1="360" y1="220" x2="430" y2="135"/>
  </g>

  <!-- Sentinel 相互通信 -->
  <g stroke="#ec4899" stroke-width="1" fill="none" stroke-dasharray="2 2">
    <line x1="280" y1="140" x2="280" y2="150"/>
    <line x1="280" y1="190" x2="280" y2="200"/>
  </g>

  <!-- 客户端连接 -->
  <g stroke="#3b82f6" stroke-width="2" fill="none" marker-end="url(#arrow)">
    <line x1="140" y1="240" x2="200" y2="170"/>
  </g>

  <!-- 主从复制 -->
  <g stroke="#10b981" stroke-width="2" fill="none" marker-end="url(#arrow)">
    <line x1="495" y1="160" x2="490" y2="180"/>
    <line x1="495" y1="160" x2="490" y2="230"/>
  </g>

  <!-- 故障转移流程 -->
  <g font-size="11">
    <rect class="at-hover-card" x="40" y="320" width="520" height="135" rx="8" fill="#f1f5f9" stroke="#64748b" stroke-width="1"/>
    <text x="300" y="340" text-anchor="middle" font-weight="700" fill="#1e293b">故障转移流程</text>

    <g font-size="10" font-weight="700">
      <rect class="at-hover-card" x="55" y="355" width="100" height="40" rx="4" fill="#fef3c7" stroke="#f59e0b" stroke-width="1"/>
      <text x="105" y="372" text-anchor="middle" fill="#92400e">① 主观下线</text>
      <text x="105" y="386" text-anchor="middle" font-size="9" fill="#78350f">PING 失败</text>

      <rect class="at-hover-card" x="170" y="355" width="100" height="40" rx="4" fill="#fce7f3" stroke="#ec4899" stroke-width="1"/>
      <text x="220" y="372" text-anchor="middle" fill="#9f1239">② 客观下线</text>
      <text x="220" y="386" text-anchor="middle" font-size="9" fill="#9d174d">半数同意</text>

      <rect class="at-hover-card" x="285" y="355" width="100" height="40" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>
      <text x="335" y="372" text-anchor="middle" fill="#1e3a8a">③ 选举 leader</text>
      <text x="335" y="386" text-anchor="middle" font-size="9" fill="#1e40af">Raft 简化</text>

      <rect class="at-hover-card" x="400" y="355" width="100" height="40" rx="4" fill="#d1fae5" stroke="#10b981" stroke-width="1"/>
      <text x="450" y="372" text-anchor="middle" fill="#064e3b">④ failover</text>
      <text x="450" y="386" text-anchor="middle" font-size="9" fill="#065f46">提升从为主</text>

      <text x="105" y="412" font-weight="600" fill="#475569">配置传播</text>
      <text x="220" y="412" font-weight="600" fill="#475569">客户端订阅</text>
      <text x="335" y="412" font-weight="600" fill="#475569">通知 +VIP 切换</text>
      <text x="450" y="412" font-weight="600" fill="#475569">CONFIG REWRITE</text>
    </g>

    <text x="300" y="438" font-size="10" fill="#475569" text-anchor="middle">⚠ 脑裂：min-replicas-to-write/ max-lag 防止</text>
    <text x="300" y="451" font-size="10" fill="#475569" text-anchor="middle">vs Cluster：Sentinel 仅高可用 · Cluster 同时做水平扩展</text>
  </g>
</svg>
