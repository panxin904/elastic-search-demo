---
title: Gossip 协议
date: 2026-08-15  # date-auto-injected
---

# 💬 Gossip 协议

> Redis Cluster 节点之间通过 **Gossip 协议**通信，用于**节点发现、故障检测、状态传播**。每个节点每秒向随机几个节点发送 ping 消息，最终全集群状态达成**最终一致**。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis Cluster Gossip 协议</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">ping/pong 消息 · MEET/PFAIL/FAIL · cluster_bus_port · gossip 扩散</text>

  <!-- 6 节点环 -->
  <g>
    <text x="60" y="95" font-size="13" font-weight="700" fill="#1e293b">Gossip 节点选择（每节点维护随机 N 个 peer）</text>

    <!-- 中心节点 -->
    <circle cx="300" cy="220" r="40" fill="#dbeafe" stroke="#3b82f6" stroke-width="3"/>
    <text x="300" y="218" text-anchor="middle" font-size="12" font-weight="700" fill="#1e40af">节点 A</text>
    <text x="300" y="234" text-anchor="middle" font-size="9" fill="#475569">发起 ping</text>

    <!-- 周围节点 -->
    <circle cx="120" cy="160" r="28" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="120" y="163" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">B</text>

    <circle cx="480" cy="160" r="28" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="480" y="163" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">C</text>

    <circle cx="120" cy="300" r="28" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="120" y="303" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">D</text>

    <circle cx="480" cy="300" r="28" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="480" y="303" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">E</text>

    <circle cx="300" cy="380" r="28" fill="#f1f5f9" stroke="#94a3b8" stroke-width="2" stroke-dasharray="3"/>
    <text x="300" y="383" text-anchor="middle" font-size="10" font-weight="700" fill="#475569">F</text>

    <!-- ping 路径 -->
    <line x1="280" y1="195" x2="148" y2="172" stroke="#3b82f6" stroke-width="2" marker-end="url(#arr)"/>
    <text x="210" y="180" text-anchor="middle" font-size="9" fill="#1e40af" font-weight="700">ping 1</text>

    <line x1="320" y1="195" x2="452" y2="172" stroke="#3b82f6" stroke-width="2" marker-end="url(#arr)"/>
    <text x="385" y="180" text-anchor="middle" font-size="9" fill="#1e40af" font-weight="700">ping 2</text>

    <line x1="280" y1="245" x2="148" y2="288" stroke="#3b82f6" stroke-width="2" marker-end="url(#arr)"/>
    <text x="210" y="270" text-anchor="middle" font-size="9" fill="#1e40af" font-weight="700">ping 3</text>

    <!-- pong 返回 -->
    <line x1="148" y1="178" x2="280" y2="205" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3" marker-end="url(#arr)"/>
    <line x1="452" y1="178" x2="320" y2="205" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3" marker-end="url(#arr)"/>

    <!-- 二次 gossip（带节点列表） -->
    <text x="300" y="430" text-anchor="middle" font-size="11" fill="#475569">ping 消息携带：节点 B 的已知节点列表 → A 收到 → A 也认识这些节点</text>
    <text x="300" y="447" text-anchor="middle" font-size="11" fill="#475569">→ gossip 二次扩散（指数级传播）</text>
  </g>

  <!-- 故障检测时序 -->
  <g>
    <text x="60" y="468" font-size="11" font-weight="700" fill="#1e293b">故障检测：</text>
    <text x="170" y="468" font-size="11" fill="#475569">PFAIL（本地判定）→ gossip 扩散 → 多数节点确认 → FAIL（全局确认）</text>
  </g>
</svg>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis Cluster 总线协议</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Gossip 消息传播 · 4 类消息 · 槽指派一致性</text>

  <!-- 总线连接拓扑 -->
  <g>
    <text x="60" y="90" font-size="13" font-weight="700" fill="#1e293b">① Cluster 总线连接（端口 16379）</text>

    <!-- 6 节点 -->
    <rect class="at-hover-card" x="80" y="115" width="90" height="65" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="125" y="138" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">N1 (6379)</text>
    <text x="125" y="158" text-anchor="middle" font-size="9" fill="#475569">slots 0-5460</text>
    <text x="125" y="172" text-anchor="middle" font-size="9" fill="#475569">master</text>

    <rect class="at-hover-card" x="200" y="115" width="90" height="65" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="245" y="138" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">N2 (6379)</text>
    <text x="245" y="158" text-anchor="middle" font-size="9" fill="#475569">slots 5461-10922</text>
    <text x="245" y="172" text-anchor="middle" font-size="9" fill="#475569">master</text>

    <rect class="at-hover-card" x="320" y="115" width="90" height="65" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="365" y="138" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">N3 (6379)</text>
    <text x="365" y="158" text-anchor="middle" font-size="9" fill="#475569">slots 10923-16383</text>
    <text x="365" y="172" text-anchor="middle" font-size="9" fill="#475569">master</text>

    <rect class="at-hover-card" x="440" y="115" width="90" height="65" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="2"/>
    <text x="485" y="138" text-anchor="middle" font-size="11" font-weight="700" fill="#065f46">N4 (6379)</text>
    <text x="485" y="158" text-anchor="middle" font-size="9" fill="#475569">N1 replica</text>
    <text x="485" y="172" text-anchor="middle" font-size="9" fill="#475569">replica</text>

    <!-- 双向连接线 -->
    <path d="M 170 140 L 200 140" fill="none" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>
    <path d="M 290 140 L 320 140" fill="none" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>
    <path d="M 410 140 L 440 140" fill="none" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>

    <!-- 节点间连接 (全部对) -->
    <path d="M 125 180 L 245 195" fill="none" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="2,2"/>
    <path d="M 245 195 L 365 180" fill="none" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="2,2"/>
    <path d="M 365 195 L 125 195" fill="none" stroke="#94a3b8" stroke-width="0.8" stroke-dasharray="2,2"/>

    <text x="300" y="207" text-anchor="middle" font-size="9" fill="#475569">每节点每秒随机 ping 3 个其他节点</text>
  </g>

  <!-- 4 类消息 -->
  <g>
    <text x="60" y="240" font-size="13" font-weight="700" fill="#1e293b">② 4 类 Gossip 消息</text>

    <rect class="at-hover-card" x="40" y="255" width="125" height="42" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="102" y="273" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">MEET</text>
    <text x="102" y="287" text-anchor="middle" font-size="9" fill="#475569">握手 / 加入</text>

    <rect class="at-hover-card" x="175" y="255" width="125" height="42" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="237" y="273" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">PING</text>
    <text x="237" y="287" text-anchor="middle" font-size="9" fill="#475569">心跳 + 元数据</text>

    <rect class="at-hover-card" x="310" y="255" width="125" height="42" rx="4" fill="#dcfce7" stroke="#10b981"/>
    <text x="372" y="273" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">PONG</text>
    <text x="372" y="287" text-anchor="middle" font-size="9" fill="#475569">响应 + 自状态</text>

    <rect class="at-hover-card" x="445" y="255" width="125" height="42" rx="4" fill="#fee2e2" stroke="#dc2626"/>
    <text x="507" y="273" text-anchor="middle" font-size="10" font-weight="700" fill="#991b1b">FAIL</text>
    <text x="507" y="287" text-anchor="middle" font-size="9" fill="#475569">节点下线广播</text>
  </g>

  <!-- 槽指派一致性 -->
  <g>
    <text x="60" y="325" font-size="13" font-weight="700" fill="#1e293b">③ 槽指派一致性（epoch 机制）</text>

    <rect class="at-hover-card" x="40" y="340" width="520" height="100" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <!-- epoch 时间线 -->
    <line x1="80" y1="380" x2="520" y2="380" stroke="#64748b" stroke-width="1.5"/>

    <circle cx="120" cy="380" r="6" fill="#3b82f6"/>
    <text x="120" y="365" font-size="9" text-anchor="middle" fill="#1e40af">epoch=1</text>
    <text x="120" y="402" font-size="9" text-anchor="middle" fill="#475569">初始槽分配</text>

    <circle cx="220" cy="380" r="6" fill="#f59e0b"/>
    <text x="220" y="365" font-size="9" text-anchor="middle" fill="#92400e">epoch=2</text>
    <text x="220" y="402" font-size="9" text-anchor="middle" fill="#475569">N4 接管 N1 槽位</text>

    <circle cx="320" cy="380" r="6" fill="#dc2626"/>
    <text x="320" y="365" font-size="9" text-anchor="middle" fill="#991b1b">epoch=3</text>
    <text x="320" y="402" font-size="9" text-anchor="middle" fill="#475569">N1 重新加入</text>

    <circle cx="420" cy="380" r="6" fill="#10b981"/>
    <text x="420" y="365" font-size="9" text-anchor="middle" fill="#065f46">当前</text>
    <text x="420" y="402" font-size="9" text-anchor="middle" fill="#475569">cluster-epoch++</text>

    <text x="300" y="425" font-size="10" fill="#475569" text-anchor="middle">Gossip 携带 currentEpoch + configEpoch，接收方丢弃旧 epoch 消息</text>
  </g>
</svg>
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
