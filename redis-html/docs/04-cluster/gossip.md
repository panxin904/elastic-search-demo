---
title: Gossip 协议
---

# 💬 Gossip 协议

> Redis Cluster 节点之间通过 **Gossip 协议**通信，用于**节点发现、故障检测、状态传播**。每个节点每秒向随机几个节点发送 ping 消息，最终全集群状态达成**最终一致**。

## 🎯 为什么用 Gossip？

```
Redis Cluster 的需求：
  - 1000+ 节点集群
  - 节点随时上下线
  - 不能有中心节点（Raft 算法中心化）

Gossip 协议的优势：
  ✅ 去中心化，无单点
  ✅ 可扩展到上千节点
  ✅ 最终一致性（O(log N) 收敛）
  ✅ 容错性强（部分节点失联不影响）
```

## 📡 4 种消息类型

```c
// Redis 集群消息定义（cluster.h）
#define CLUSTERMSG_TYPE_PING    0    // ping：本节点状态
#define CLUSTERMSG_TYPE_PONG    1    // pong：响应 ping
#define CLUSTERMSG_TYPE_MEET    2    // meet：让新节点加入集群
#define CLUSTERMSG_TYPE_FAIL    3    // fail：标记节点下线
#define CLUSTERMSG_TYPE_PUBLISH 4    // publish：发布订阅（Pub/Sub）
#define CLUSTERMSG_TYPE_FAILOVER_AUTH_REQUEST 5
#define CLUSTERMSG_TYPE_FAILOVER_AUTH_ACK 6
#define CLUSTERMSG_TYPE_UPDATE 7     // 增量配置更新
#define CLUSTERMSG_TYPE_MFSTART 8    // 手动故障转移
```

### ping / pong（心跳）

```bash
# 默认每秒发送一次 ping
# 每次向 3 个随机节点发送
cluster-node-timeout 15000          # 节点超时时间（毫秒）
```

**ping 消息包含**：
- 本节点 ID
- 当前 epoch
- 槽位映射关系
- 已知的其他节点状态

**pong 消息包含**：
- 与 ping 相同内容
- 用于响应 ping 和 meet

### meet（加入集群）

```bash
# 让新节点加入集群
CLUSTER MEET 192.168.1.10 7007

# 内部流程：
# 1. 客户端发送 MEET 给 A
# 2. A 向 7007 发送 PING
# 3. 7007 收到后向 A 发送 PONG
# 4. 通过 Gossip 协议扩散，集群所有节点认识 7007
```

### fail（标记下线）

```bash
# 节点 A 长时间未响应 B 的 ping
# B 将 A 标记为 PFAIL（疑似下线）
# B 通过 Gossip 扩散 PFAIL 给其他节点
# 多数节点认为 A 下线 → A 标记为 FAIL（确认下线）

# 然后触发故障转移流程（Replica 晋升）
```

## 🕐 故障检测流程

```
时间线：
  T0    A 宕机
  T1    B 的 ping 失败
  T2    B 标记 A 为 PFAIL（本地状态）
  T3    B 通过 Gossip 告诉 C、D、E
  T4    C、D、E 也标记 A 为 PFAIL
  T5    多数节点认为 A 下线 → 标记为 FAIL
  T6    触发故障转移流程
  T7    Replica 晋升为新 Master

总耗时：通常 1-3 秒
```

**配置项**：
```properties
# 节点超时时间（毫秒）
cluster-node-timeout 15000

# 多少秒未收到 pong 视为 PFAIL
# 默认 = cluster-node-timeout
```

## 📊 消息格式

```c
typedef struct {
    uint32_t totlen;        // 总长度
    uint16_t type;          // 消息类型
    uint16_t count;         // Gossip 节点数量
    uint64_t currentEpoch;  // 当前 epoch
    uint64_t configEpoch;   // 配置 epoch
    uint64_t serverId;      // 发送者 ID
    char sender[CLUSTER_NAMELEN];  // 发送者名字
    uint16_t port;          // 端口
    uint16_t flags;         // 标志位
    char state;             // 集群状态
    union clusterMsgData data;  // 数据
} clusterMsg;
```

**节点间一次 ping 的大小**：
- 每个 ping 包含当前节点信息 + 最多 3 个其他节点信息
- 默认每个节点约 150 字节
- ping 包总大小：约 2KB（16384 bit 槽位映射）

## 🔄 Gossip 传播规律

```
每秒一次 ping：
  - 选 3 个随机节点
  - 发送本节点状态 + 已知节点状态
  - 收到 pong 后更新本地视图

收敛时间：
  - 100 节点集群 → 几秒收敛
  - 1000 节点集群 → 几十秒收敛
  - 10000 节点集群 → 分钟级收敛
```

## 🛠️ 实战：Gossip 调优

```properties
# redis.conf
cluster-node-timeout 15000          # 节点超时（毫秒）
# 太小：误判下线（网络抖动就误报）
# 太大：故障检测慢
# 推荐：15000ms

# Replica 选举超时
cluster-replica-validity-factor 10  # 失效 factor

# 心跳间隔（默认 100ms）
# 不可配，由 cluster-node-timeout 决定

# 控制 Gossip 频率
# cluster_busy_disable_pings  # 进入 OOM 时停止 ping
```

## 🐛 故障案例

### 案例 1：网络分区脑裂

```
现象：集群分成 A、B 两个分区，各自独立工作
原因：网络抖动导致心跳失败
解决：
  1. 多数节点分区才提供服务
  2. 少数派分区拒绝写入（cluster-require-full-coverage yes）
  3. 网络恢复后自动合并
```

### 案例 2：节点频繁 PFAIL

```
现象：节点偶发 PFAIL 告警
原因：
  1. 网络延迟高
  2. 节点 CPU 繁忙（响应慢）
  3. 磁盘 IO 抖动
解决：
  1. 调大 cluster-node-timeout
  2. 监控集群延迟
  3. 优化磁盘性能
```

### 案例 3：大集群 Gossip 风暴

```
现象：1000 节点集群 Gossip 消息占满带宽
原因：每秒 1000 节点 × 3 ping = 3000 个消息
解决：
  1. 拆分多个集群（业务隔离）
  2. 调整 cluster-node-timeout（减少心跳频率）
  3. 监控 gossip 流量
```

## 📊 Gossip vs Raft 对比

| 维度 | Gossip | Raft |
|------|--------|------|
| **一致性** | 最终一致 | 强一致 |
| **中心化** | 无中心 | 有 Leader |
| **故障检测** | O(log N) | O(1)（Leader 检测） |
| **选举** | 多数派投票 | 多数派投票 |
| **实现复杂度** | 简单 | 中等 |
| **适用规模** | 1000+ 节点 | 5-7 节点 |

## 🎯 总结

**Gossip 核心要点**：
- ✅ 4 种消息：ping / pong / meet / fail
- ✅ 每秒向 3 个随机节点发送 ping
- ✅ PFAIL → FAIL 两阶段故障判定
- ✅ 去中心化，可扩展到 1000+ 节点
- ⚠️ 最终一致性（非强一致）
- ⚠️ 大集群有 Gossip 风暴风险

**下一步：** [🚚 数据迁移](/04-cluster/migration) — 在线迁移不中断服务
