---
title: Cluster 集群
date: 2026-08-15  # date-auto-injected
---

# 🌐 Cluster 集群

> **Redis Cluster**是 Redis 官方提供的**分布式解决方案**，用于解决单机内存瓶颈和主从复制无法水平扩展的问题。

## 🎯 为什么需要 Cluster？

```
单机 Redis 的痛点：
  ❌ 单机内存有限（最大几百 GB，受限于硬件）
  ❌ 主从复制只能扩展读，不能扩展写
  ❌ Sentinel 仍然只有一个 Master 处理写
  ❌ QPS 上限受单机 CPU 限制

Cluster 的解决方案：
  ✅ 多 Master 分片：写负载分散
  ✅ 每 Master 多个 Replica：高可用
  ✅ 水平扩展：增加节点即可提升容量和性能
  ✅ 自动故障转移：Master 宕机 Replica 自动晋升
```

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Redis Cluster Slot 路由</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">CRC16(key) % 16384 → MOVED / ASK 跳转</text>

  <!-- 客户端 -->
  <rect class="at-hover-card" x="230" y="90" width="140" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
  <text x="300" y="113" text-anchor="middle" font-size="12" font-weight="700" fill="#1e40af">Client</text>
  <text x="300" y="132" text-anchor="middle" font-size="10" fill="#475569">SET user:42 "abc"</text>

  <!-- 3 个 Master 节点 -->
  <rect class="at-hover-card" x="40" y="180" width="140" height="100" rx="8" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="110" y="205" text-anchor="middle" font-size="12" font-weight="700" fill="#047857">Master A</text>
  <text x="110" y="225" text-anchor="middle" font-size="10" fill="#475569">slots 0-5460</text>
  <text x="110" y="245" text-anchor="middle" font-size="9" fill="#475569">(33% 数据)</text>
  <text x="110" y="265" text-anchor="middle" font-size="9" fill="#475569" font-style="italic">CRC16("user:42")=1234</text>

  <rect class="at-hover-card" x="220" y="180" width="160" height="100" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="300" y="205" text-anchor="middle" font-size="12" font-weight="700" fill="#92400e">Master B (目标)</text>
  <text x="300" y="225" text-anchor="middle" font-size="10" fill="#475569">slots 5461-10922</text>
  <text x="300" y="245" text-anchor="middle" font-size="9" fill="#475569">(33% 数据)</text>
  <text x="300" y="265" text-anchor="middle" font-size="9" fill="#92400e" font-weight="700">1234 % 16384 = 1234</text>
  <text x="300" y="278" text-anchor="middle" font-size="9" fill="#92400e" font-weight="700">→ slot 1234 ∈ [0,5460]</text>

  <rect class="at-hover-card" x="420" y="180" width="140" height="100" rx="8" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="490" y="205" text-anchor="middle" font-size="12" font-weight="700" fill="#047857">Master C</text>
  <text x="490" y="225" text-anchor="middle" font-size="10" fill="#475569">slots 10923-16383</text>
  <text x="490" y="245" text-anchor="middle" font-size="9" fill="#475569">(34% 数据)</text>

  <!-- Replica -->
  <rect class="at-hover-card" x="40" y="305" width="140" height="40" rx="4" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="110" y="329" text-anchor="middle" font-size="10" font-weight="600" fill="#475569">Replica A1/A2</text>

  <rect class="at-hover-card" x="220" y="305" width="160" height="40" rx="4" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="300" y="329" text-anchor="middle" font-size="10" font-weight="600" fill="#475569">Replica B1/B2</text>

  <rect class="at-hover-card" x="420" y="305" width="140" height="40" rx="4" fill="#f1f5f9" stroke="#94a3b8"/>
  <text x="490" y="329" text-anchor="middle" font-size="10" font-weight="600" fill="#475569">Replica C1/C2</text>

  <!-- Client 路由箭头 -->
  <line x1="270" y1="140" x2="110" y2="180" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="170" y="160" font-size="9" fill="#1e40af">① 路由到任意节点</text>

  <line x1="110" y1="220" x2="270" y2="220" stroke="#dc2626" stroke-width="2" marker-end="url(#arr)"/>
  <text x="180" y="213" font-size="10" font-weight="700" fill="#dc2626">② MOVED 1234 MasterB:6380</text>

  <line x1="300" y1="140" x2="300" y2="180" stroke="#3b82f6" stroke-width="2" marker-end="url(#arr)"/>
  <text x="320" y="160" font-size="9" fill="#1e40af">③ 直接执行</text>

  <!-- 关键点 -->
  <rect x="30" y="365" width="540" height="100" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="388" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">关键设计</text>
  <text x="50" y="410" font-size="11" fill="#334155">· 客户端缓存 slot map（启动时 CLUSTER SLOTS 一次性拉取）</text>
  <text x="50" y="428" font-size="11" fill="#334155">· MOVED（永久迁移）vs ASK（临时跳转，如 reshard 中）</text>
  <text x="50" y="446" font-size="11" fill="#334155">· 16384 = 2^14（不是 65536）：压缩位图，控制心跳包大小</text>
  <text x="320" y="410" font-size="11" fill="#334155">· hash tags：{user}:42 与 {user}:100 保证同 slot</text>
  <text x="320" y="428" font-size="11" fill="#334155">· Reshard：slot 在线迁移，从 source → target</text>
  <text x="320" y="446" font-size="11" fill="#334155">· 不支持多 key 跨 slot 操作（除非用 hash tag）</text>
</svg>

## 🏗️ Cluster 架构

```
                 Redis Cluster（6 节点）
┌─────────────────────────────────────────────┐
│                                              │
│   Master A          Master B          Master C │
│   Slots 0-5460      Slots 5461-10922  10923-16383 │
│   ↕ Replica A1      ↕ Replica B1      ↕ Replica C1 │
│                                              │
│   客户端通过 CRC16(key) % 16384 找到对应槽位    │
└─────────────────────────────────────────────┘

- 3 个 Master 节点 + 3 个 Replica 节点（推荐）
- 每个 Master 处理一部分槽位（slot）
- 数据自动分片到不同 Master
```

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
    <marker id="arrR" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#dc2626"/>
    </marker>
    <marker id="arrG" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#10b981"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis Cluster 故障转移</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">PFAIL → FAIL → Replica Election → Slots 接管 · 多数派投票</text>

  <!-- 时间线 -->
  <g>
    <text x="60" y="95" font-size="13" font-weight="700" fill="#1e293b">故障转移时序（6 节点 · M1宕机）</text>

    <!-- Master 1 -->
    <rect class="at-hover-card" x="40" y="120" width="80" height="30" rx="4" fill="#fee2e2" stroke="#dc2626" stroke-dasharray="4"/>
    <text x="80" y="140" text-anchor="middle" font-size="11" font-weight="700" fill="#7f1d1d">M1 ✗</text>

    <!-- Replica 1 -->
    <rect class="at-hover-card" x="160" y="120" width="80" height="30" rx="4" fill="#d1fae5" stroke="#10b981"/>
    <text x="200" y="140" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">R1 (候选)</text>

    <!-- M2 -->
    <rect class="at-hover-card" x="280" y="120" width="80" height="30" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="320" y="140" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">M2</text>

    <!-- M3 -->
    <rect class="at-hover-card" x="400" y="120" width="80" height="30" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="440" y="140" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">M3</text>

    <!-- R2 -->
    <rect class="at-hover-card" x="520" y="120" width="50" height="30" rx="4" fill="#f1f5f9" stroke="#94a3b8"/>
    <text x="545" y="140" text-anchor="middle" font-size="10" fill="#475569">R2</text>
  </g>

  <!-- 流程步骤 -->
  <g>
    <line x1="60" y1="170" x2="540" y2="170" stroke="#94a3b8" stroke-width="2"/>

    <!-- t1: PFAIL -->
    <circle cx="80" cy="170" r="8" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="80" y="195" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">t=0</text>
    <text x="80" y="208" text-anchor="middle" font-size="9" fill="#475569">M1 宕机</text>

    <!-- t2: gossip PFAIL -->
    <circle cx="160" cy="170" r="8" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="160" y="195" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">t=1s</text>
    <text x="160" y="208" text-anchor="middle" font-size="9" fill="#475569">R1 PFAIL</text>

    <line x1="88" y1="170" x2="152" y2="170" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>

    <!-- t3: gossip 扩散 -->
    <circle cx="280" cy="170" r="8" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="280" y="195" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">t=2s</text>
    <text x="280" y="208" text-anchor="middle" font-size="9" fill="#475569">M2 收到 PFAIL</text>

    <line x1="168" y1="170" x2="272" y2="170" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>

    <!-- t4: 多数派确认 -->
    <circle cx="440" cy="170" r="8" fill="#dc2626"/>
    <text x="440" y="195" text-anchor="middle" font-size="10" font-weight="700" fill="#7f1d1d">t=5s</text>
    <text x="440" y="208" text-anchor="middle" font-size="9" fill="#475569">M2/M3 确认 FAIL</text>

    <line x1="288" y1="170" x2="432" y2="170" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>

    <!-- t5: 选举 -->
    <circle cx="80" cy="260" r="8" fill="#10b981"/>
    <text x="80" y="285" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">t=6s</text>
    <text x="80" y="298" text-anchor="middle" font-size="9" fill="#475569">R1 发起选举</text>

    <line x1="448" y1="170" x2="88" y2="252" stroke="#10b981" stroke-width="1.5" stroke-dasharray="3" marker-end="url(#arrG)"/>

    <!-- t6: 投票 -->
    <circle cx="200" cy="260" r="8" fill="#10b981"/>
    <text x="200" y="285" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">t=7s</text>
    <text x="200" y="298" text-anchor="middle" font-size="9" fill="#475569">M2 投票赞成</text>

    <line x1="88" y1="270" x2="192" y2="270" stroke="#10b981" stroke-width="1.5" marker-end="url(#arrG)"/>

    <!-- t7: 升 Master -->
    <circle cx="320" cy="260" r="8" fill="#10b981"/>
    <text x="320" y="285" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">t=8s</text>
    <text x="320" y="298" text-anchor="middle" font-size="9" fill="#475569">多数票达成</text>

    <line x1="208" y1="270" x2="312" y2="270" stroke="#10b981" stroke-width="1.5" marker-end="url(#arrG)"/>

    <!-- t8: 接管 slot -->
    <circle cx="440" cy="260" r="8" fill="#10b981"/>
    <text x="440" y="285" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">t=9s</text>
    <text x="440" y="298" text-anchor="middle" font-size="9" fill="#475569">R1 升 M + 接管 slot</text>

    <line x1="328" y1="270" x2="432" y2="270" stroke="#10b981" stroke-width="1.5" marker-end="url(#arrG)"/>
  </g>

  <!-- 关键参数 -->
  <g>
    <rect class="at-hover-card" x="40" y="345" width="525" height="100" rx="6" fill="#fef9c3" stroke="#facc15"/>
    <text x="60" y="367" font-size="11" font-weight="700" fill="#854d0e">关键参数：</text>
    <text x="60" y="385" font-size="10" font-family="monospace" fill="#1e2937">cluster-node-timeout=15000          # 15s 未响应 → PFAIL</text>
    <text x="60" y="402" font-size="10" font-family="monospace" fill="#1e2937">cluster-replica-validity-factor=10  # replica 数据落后不超过 10 倍</text>
    <text x="60" y="419" font-size="10" font-family="monospace" fill="#1e2937">cluster-migration-barrier=1         # 接管时至少 1 个客户端</text>
    <text x="60" y="436" font-size="11" fill="#854d0e" font-weight="700">⚠️ M1 复活后：自动成为 R1 的 Replica，不会双 Master 脑裂</text>
  </g>
</svg>
## 🆚 Cluster vs 主从 + 哨兵

| 维度 | 主从复制 | Sentinel | Cluster |
|------|---------|----------|---------|
| **数据分片** | ❌ | ❌ | ✅ |
| **水平扩展** | ❌ | ❌ | ✅ |
| **自动故障转移** | ❌ | ✅ | ✅ |
| **写性能** | 单机 | 单机 | 多机 |
| **适合规模** | 10 GB | 100 GB | 10 TB+ |
| **客户端复杂度** | 低 | 低 | 中（需支持 MOVED） |

## ⚙️ 集群配置

### 启动配置

```properties
# redis.conf
cluster-enabled yes                  # 开启集群模式
cluster-config-file nodes-6379.conf  # 集群配置文件（自动生成）
cluster-node-timeout 15000          # 节点超时时间（毫秒）
cluster-migration-barrier 1         # Replica 迁移屏障
cluster-require-full-coverage yes   # 槽位全覆盖才提供服务
cluster-replica-validity-factor 10  # Replica 失效因子
cluster-announce-ip 192.168.1.10    # 节点 IP（多网卡需指定）
cluster-announce-port 6379          # 节点端口
```

### 创建集群（6 节点）

```bash
# 1. 准备 6 个 Redis 实例（监听不同端口）
mkdir -p /redis-cluster/{7001,7002,7003,7004,7005,7006}

for port in 7001 7002 7003 7004 7005 7006; do
    cat > /redis-cluster/$port/redis.conf << EOF
port $port
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
daemonize yes
pidfile /var/run/redis-$port.pid
logfile /var/log/redis-$port.log
dir /redis-cluster/$port
EOF
    redis-server /redis-cluster/$port/redis.conf
done

# 2. 使用 redis-cli 创建集群（自动分配槽位）
redis-cli --cluster create \
    192.168.1.10:7001 192.168.1.10:7002 192.168.1.10:7003 \
    192.168.1.10:7004 192.168.1.10:7005 192.168.1.10:7006 \
    --cluster-replicas 1

# 输出：
# [OK] All 16384 slots covered
```

## 📊 客户端路由

```
客户端 SET user:1 "Alice"

  1. 计算槽位：slot = CRC16("user:1") % 16384 = 5258
  2. 查找槽位对应的 Master
  3. 发送请求到该 Master

如果连接的不是该 Master：
  - Master 返回 MOVED 5258 192.168.1.10:7002
  - 客户端更新路由表，重新发送请求
```

### MOVED vs ASK

```
MOVED 5258 192.168.1.10:7002
  含义：槽位 5258 在 7002 节点
  行为：客户端应永久更新路由表

ASK 5258 192.168.1.10:7002
  含义：槽位 5258 正在迁移中，下一个槽位在 7002
  行为：客户端下次请求应发送到 7002，但不更新路由表
  触发：迁移过程中的临时状态
```

## 🔍 集群命令

```bash
# 查看集群节点
redis-cli -c -h 192.168.1.10 -p 7001 CLUSTER NODES

# 查看槽位分配
redis-cli -c -h 192.168.1.10 -p 7001 CLUSTER SLOTS

# 查看某 key 的槽位
redis-cli -c CLUSTER KEYSLOT "user:1"
# → 5258

# 查看集群信息
redis-cli -c CLUSTER INFO

# 健康检查
redis-cli -c CLUSTER HEALTH

# 添加节点
redis-cli --cluster add-node 192.168.1.10:7007 192.168.1.10:7001

# 添加 Replica
redis-cli --cluster add-node 192.168.1.10:7008 192.168.1.10:7001 \
    --cluster-slave --cluster-master-id <master-node-id>
```

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis 多 Key 事务与 Lua 脚本</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">MULTI/EXEC · WATCH · EVAL 原子性 · Cluster 下 hash tag</text>

  <!-- MULTI/EXEC 事务 -->
  <g>
    <text x="60" y="90" font-size="13" font-weight="700" fill="#1e293b">① MULTI/EXEC 事务（非原子）</text>

    <rect class="at-hover-card" x="40" y="105" width="520" height="125" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="60" y="120" width="110" height="32" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="115" y="140" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">MULTI</text>

    <rect class="at-hover-card" x="60" y="160" width="110" height="32" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="115" y="180" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">SET k1 v1</text>

    <rect class="at-hover-card" x="190" y="160" width="110" height="32" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="245" y="180" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">INCR k2</text>

    <rect class="at-hover-card" x="320" y="160" width="110" height="32" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="375" y="180" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">LPUSH k3 x</text>

    <rect class="at-hover-card" x="60" y="200" width="110" height="32" rx="3" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="115" y="220" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">EXEC</text>

    <text x="450" y="140" font-size="10" font-weight="700" fill="#1e293b">特性</text>
    <text x="450" y="160" font-size="9" fill="#475569">• 串行执行，不被打断</text>
    <text x="450" y="178" font-size="9" fill="#475569">• 不支持回滚（失败继续）</text>
    <text x="450" y="196" font-size="9" fill="#475569">• 乐观锁：WATCH + CAS</text>
    <text x="450" y="214" font-size="9" fill="#dc2626">⚠️ Cluster: 多 key 必须</text>
  </g>

  <!-- Lua 脚本 -->
  <g>
    <text x="60" y="252" font-size="13" font-weight="700" fill="#1e293b">② EVAL Lua 脚本（真正原子）</text>

    <rect class="at-hover-card" x="40" y="265" width="520" height="115" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="60" y="278" width="480" height="55" rx="3" fill="#1e293b"/>
    <text x="75" y="296" font-size="10" font-family="monospace" fill="#a7f3d0">EVAL "local v = redis.call('GET', KEYS[1])</text>
    <text x="75" y="312" font-size="10" font-family="monospace" fill="#a7f3d0">       if v == ARGV[1] then</text>
    <text x="75" y="328" font-size="10" font-family="monospace" fill="#a7f3d0">         return redis.call('SET', KEYS[1], ARGV[2]) end"</text>

    <text x="60" y="350" font-size="10" font-weight="700" fill="#10b981">✅ 优势</text>
    <text x="60" y="368" font-size="9" fill="#475569">• 整段脚本在 server 端原子执行</text>
    <text x="60" y="383" font-size="9" fill="#475569">• 减少网络 RTT（一次往返）</text>
  </g>

  <!-- Cluster 下 hash tag -->
  <g>
    <text x="60" y="402" font-size="13" font-weight="700" fill="#1e293b">③ Cluster 下多 Key：Hash Tag</text>

    <rect class="at-hover-card" x="40" y="415" width="170" height="50" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="125" y="433" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">{user}:profile</text>
    <text x="125" y="447" text-anchor="middle" font-size="9" fill="#475569">{} 内只算 hash</text>
    <text x="125" y="461" text-anchor="middle" font-size="9" fill="#475569">→ 同一 slot</text>

    <path d="M 210 440 L 240 440" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="240" y="415" width="160" height="50" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="320" y="433" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">{user}:orders</text>
    <text x="320" y="447" text-anchor="middle" font-size="9" fill="#475569">同 user 哈希</text>
    <text x="320" y="461" text-anchor="middle" font-size="9" fill="#475569">→ 同一 slot</text>

    <path d="M 400 440 L 430 440" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="430" y="415" width="130" height="50" rx="4" fill="#dcfce7" stroke="#10b981"/>
    <text x="495" y="433" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">同节点</text>
    <text x="495" y="447" text-anchor="middle" font-size="9" fill="#475569">保证原子性</text>
    <text x="495" y="461" text-anchor="middle" font-size="9" fill="#475569">支持事务</text>
  </g>
</svg>
## ⚠️ 集群限制

```bash
# 1. 多 key 操作必须保证在同一个槽
❌ MSET user:1:name "Alice" user:2:name "Bob"
   # user:1 和 user:2 在不同槽位，跨槽位不支持

✅ MSET user:{1001}:name "Alice" user:{1001}:age 28
   # 用 {tag} 强制路由到同一槽

# 2. 不支持事务跨槽
❌ MULTI ... EXEC（跨多个 key 在不同槽）

# 3. Lua 脚本限制
❌ 跨槽位 key 操作（Redis 7 改善，但仍有限制）

# 4. Pipeline 限制
❌ Pipeline 内跨多个槽（需要按槽分组）

# 5. 不支持 SELECT
❌ SELECT 1（只有 db 0）
```

### Hash Tag 解决方案

```bash
# 使用 {} 强制路由
SET user:{1001}:name "Alice"   # 槽位 = CRC16("1001") % 16384
SET user:{1001}:age 28          # 槽位 = CRC16("1001") % 16384
# 两个 key 在同一槽位！

# 实战：购物车按用户分片
HSET cart:{user:1001} item1 1
HSET cart:{user:1001} item2 2
HGETALL cart:{user:1001}       # 一个 HGETALL 就能拿到完整购物车
```

## 📊 故障转移流程

```
1. Master A 宕机
   ↓
2. Replica A1 探测到心跳超时
   ↓
3. 其他 Master 通过 Gossip 协议标记 A 失联
   ↓
4. Replica A1 触发选举（Raft 思路）
   ↓
5. 多数 Master 投票同意 A1 晋升
   ↓
6. A1 切换为 Master，接管槽位
   ↓
7. 客户端路由表更新（MOVED 重定向）
```

## 🛠️ 实战：Spring Boot 集成 Cluster

```yaml
# application.yml
spring:
  redis:
    cluster:
      nodes:
        - 192.168.1.10:7001
        - 192.168.1.10:7002
        - 192.168.1.10:7003
        - 192.168.1.10:7004
        - 192.168.1.10:7005
        - 192.168.1.10:7006
      max-redirects: 3          # MOVED 重定向最大次数
      timeout: 5000ms
    lettuce:
      pool:
        max-active: 100
        max-idle: 20
        min-idle: 5
```

```java
@Configuration
public class RedisClusterConfig {

    @Bean
    public RedisClusterConfiguration redisClusterConfiguration() {
        RedisClusterConfiguration config = new RedisClusterConfiguration();
        List<String> nodes = Arrays.asList(
            "192.168.1.10:7001", "192.168.1.10:7002", "192.168.1.10:7003",
            "192.168.1.10:7004", "192.168.1.10:7005", "192.168.1.10:7006"
        );
        for (String node : nodes) {
            String[] parts = node.split(":");
            config.addClusterNode(new RedisNode(parts[0], Integer.parseInt(parts[1])));
        }
        config.setMaxRedirects(3);
        return config;
    }
}
```

## 🎯 总结

**Cluster 核心要点**：
- ✅ 官方分布式方案，水平扩展
- ✅ 16384 个槽位，自动分片
- ✅ 自动故障转移，高可用
- ✅ 多 Master 写负载均衡
- ⚠️ 客户端需支持 MOVED 重定向
- ⚠️ 跨槽位操作受限（用 hash tag 解决）

**下一步：** [🎰 哈希槽分片](/04-cluster/slots) — 深入理解 CRC16 与槽位分配

<!-- svg-injected:do-not-edit -->

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
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis Cluster 哈希槽</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">16384 slot · CRC16(key) % 16384</text>

  <!-- 顶部：客户端 -->
  <rect class="at-hover-card" x="240" y="90" width="120" height="40" rx="8" fill="#3b82f6" opacity="0.9"/>
  <text x="300" y="115" text-anchor="middle" font-size="13" font-weight="700" fill="white">Client</text>
  <text x="300" y="130" text-anchor="middle" font-size="10" fill="#dbeafe">任意节点</text>

  <!-- 3 个主节点 -->
  <g font-size="12" font-weight="700">
    <rect class="at-hover-card" x="60" y="180" width="120" height="50" rx="8" fill="#10b981" opacity="0.9"/>
    <text x="120" y="202" text-anchor="middle" fill="white">Master A</text>
    <text x="120" y="220" text-anchor="middle" font-size="10" fill="#d1fae5">slot 0-5460</text>

    <rect class="at-hover-card" x="240" y="180" width="120" height="50" rx="8" fill="#10b981" opacity="0.9"/>
    <text x="300" y="202" text-anchor="middle" fill="white">Master B</text>
    <text x="300" y="220" text-anchor="middle" font-size="10" fill="#d1fae5">slot 5461-10922</text>

    <rect class="at-hover-card" x="420" y="180" width="120" height="50" rx="8" fill="#10b981" opacity="0.9"/>
    <text x="480" y="202" text-anchor="middle" fill="white">Master C</text>
    <text x="480" y="220" text-anchor="middle" font-size="10" fill="#d1fae5">slot 10923-16383</text>
  </g>

  <!-- 箭头 -->
  <g stroke="#94a3b8" stroke-width="2" fill="none" marker-end="url(#arrow)">
    <line x1="180" y1="130" x2="120" y2="178"/>
    <line x1="300" y1="130" x2="300" y2="178"/>
    <line x1="420" y1="130" x2="480" y2="178"/>
  </g>

  <!-- 3 个从节点 -->
  <g font-size="12" font-weight="700">
    <rect class="at-hover-card" x="60" y="270" width="120" height="50" rx="8" fill="#94a3b8" opacity="0.85"/>
    <text x="120" y="292" text-anchor="middle" fill="white">Replica A'</text>
    <text x="120" y="310" text-anchor="middle" font-size="10" fill="#f1f5f9">复制 A</text>

    <rect class="at-hover-card" x="240" y="270" width="120" height="50" rx="8" fill="#94a3b8" opacity="0.85"/>
    <text x="300" y="292" text-anchor="middle" fill="white">Replica B'</text>
    <text x="300" y="310" text-anchor="middle" font-size="10" fill="#f1f5f9">复制 B</text>

    <rect class="at-hover-card" x="420" y="270" width="120" height="50" rx="8" fill="#94a3b8" opacity="0.85"/>
    <text x="480" y="292" text-anchor="middle" fill="white">Replica C'</text>
    <text x="480" y="310" text-anchor="middle" font-size="10" fill="#f1f5f9">复制 C</text>
  </g>

  <!-- 复制箭头 -->
  <g stroke="#ec4899" stroke-width="2" fill="none" stroke-dasharray="4 3" marker-end="url(#arrow)">
    <line x1="120" y1="230" x2="120" y2="268"/>
    <line x1="300" y1="230" x2="300" y2="268"/>
    <line x1="480" y1="230" x2="480" y2="268"/>
  </g>

  <!-- 关键概念 -->
  <g font-size="11">
    <rect class="at-hover-card" x="50" y="345" width="160" height="100" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>
    <text x="130" y="365" text-anchor="middle" font-weight="700" fill="#1e3a8a">哈希槽算法</text>
    <text x="130" y="383" text-anchor="middle" fill="#1e40af">HASH_SLOT =</text>
    <text x="130" y="398" text-anchor="middle" fill="#1e40af">CRC16(key) % 16384</text>
    <text x="130" y="418" text-anchor="middle" fill="#1e40af">#{}  #{}  #{}</text>
    <text x="130" y="435" text-anchor="middle" fill="#1e40af">key 含 {} 取 {} 内</text>

    <rect class="at-hover-card" x="230" y="345" width="160" height="100" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1"/>
    <text x="310" y="365" text-anchor="middle" font-weight="700" fill="#92400e">MOVED 重定向</text>
    <text x="310" y="383" text-anchor="middle" fill="#78350f">-MOVED slot ip:port</text>
    <text x="310" y="400" text-anchor="middle" fill="#78350f">客户端更新路由表</text>
    <text x="310" y="418" text-anchor="middle" fill="#78350f">ASK 临时重定向</text>
    <text x="310" y="435" text-anchor="middle" fill="#78350f">（迁移中）</text>

    <rect class="at-hover-card" x="410" y="345" width="160" height="100" rx="6" fill="#d1fae5" stroke="#10b981" stroke-width="1"/>
    <text x="490" y="365" text-anchor="middle" font-weight="700" fill="#064e3b">故障转移</text>
    <text x="490" y="383" text-anchor="middle" fill="#065f46">主节点 ping pong</text>
    <text x="490" y="400" text-anchor="middle" fill="#065f46">半数投票 → 升级</text>
    <text x="490" y="418" text-anchor="middle" fill="#065f46">从节点接管 slot</text>
    <text x="490" y="435" text-anchor="middle" fill="#065f46">CLUSTER FAILOVER</text>
  </g>
</svg>
<!-- svg-injected:do-not-edit -->

## 图示：Redis Cluster Gossip 协议与故障检测

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Redis Cluster Gossip 协议</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">去中心化集群 · ping/pong 消息 · 16384 slot · 故障检测</text>

  <!-- 6 节点 -->
  <g>
    <circle cx="120" cy="160" r="35" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="120" y="158" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Master 1</text>
    <text x="120" y="172" text-anchor="middle" font-size="9" fill="#475569">slots 0-5460</text>

    <circle cx="300" cy="100" r="35" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="300" y="98" text-anchor="middle" font-size="11" font-weight="700" fill="#065f46">Master 2</text>
    <text x="300" y="112" text-anchor="middle" font-size="9" fill="#475569">slots 5461-10922</text>

    <circle cx="480" cy="160" r="35" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
    <text x="480" y="158" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">Master 3</text>
    <text x="480" y="172" text-anchor="middle" font-size="9" fill="#475569">slots 10923-16383</text>

    <circle cx="120" cy="280" r="30" fill="#fce7f3" stroke="#ec4899" stroke-width="1.5" stroke-dasharray="3"/>
    <text x="120" y="280" text-anchor="middle" font-size="10" font-weight="700" fill="#9d174d">Replica</text>
    <text x="120" y="293" text-anchor="middle" font-size="9" fill="#475569">M1 副本</text>

    <circle cx="300" cy="340" r="30" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5" stroke-dasharray="3"/>
    <text x="300" y="340" text-anchor="middle" font-size="10" font-weight="700" fill="#5b21b6">Replica</text>
    <text x="300" y="353" text-anchor="middle" font-size="9" fill="#475569">M2 副本</text>

    <circle cx="480" cy="280" r="30" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="3"/>
    <text x="480" y="280" text-anchor="middle" font-size="10" font-weight="700" fill="#475569">Replica</text>
    <text x="480" y="293" text-anchor="middle" font-size="9" fill="#475569">M3 副本</text>
  </g>

  <!-- Gossip 连线（双向 ping/pong） -->
  <g stroke="#64748b" stroke-width="1.2" fill="none" stroke-dasharray="4">
    <path d="M155,160 L265,100" marker-end="url(#arr)" marker-start="url(#arr)"/>
    <path d="M335,100 L445,160" marker-end="url(#arr)" marker-start="url(#arr)"/>
    <path d="M120,195 L120,250" marker-end="url(#arr)" marker-start="url(#arr)"/>
    <path d="M300,135 L300,310" marker-end="url(#arr)" marker-start="url(#arr)"/>
    <path d="M480,195 L480,250" marker-end="url(#arr)" marker-start="url(#arr)"/>
    <path d="M150,280 L270,340" marker-end="url(#arr)" marker-start="url(#arr)"/>
    <path d="M450,280 L330,340" marker-end="url(#arr)" marker-start="url(#arr)"/>
  </g>
  <text x="300" y="80" text-anchor="middle" font-size="9" fill="#64748b">ping / pong（每 100ms）</text>

  <!-- Gossip 消息内容 -->
  <g>
    <rect class="at-hover-card" x="20" y="395" width="560" height="75" rx="6" fill="#f1f5f9" stroke="#cbd5e1" stroke-width="1.5"/>
    <text x="40" y="418" font-size="11" font-weight="700" fill="#1e293b">⚡ Gossip 消息字段（ping/pong 共享）</text>
    <text x="40" y="438" font-size="10" fill="#475569">node.id · node.ip:port · node.flags（PFAIL/FAIL）· hash slot（cluster slots 16384）</text>
    <text x="40" y="455" font-size="10" fill="#475569">⚡ PFAIL → FAIL：半数以上 master 在 gossip 超时内（cluster-node-timeout）确认某节点不可达</text>
    <text x="40" y="467" font-size="10" font-style="italic" fill="#94a3b8">⚡ 故障转移：master FAIL 后，其副本之一被晋升；其他 master 通过 gossip 感知新拓扑</text>
  </g>
</svg>
