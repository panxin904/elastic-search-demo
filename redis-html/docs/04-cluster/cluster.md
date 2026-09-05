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

![Redis Cluster 故障转移](/redis-cluster-failover.svg)

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

![Redis Multi Key Tx](/redis-multi-key-tx.svg)

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

![cluster slot](/cluster-slot.svg)

<!-- svg-injected:do-not-edit -->

## 图示：Redis Cluster Gossip 协议与故障检测

![Redis Cluster Gossip 协议与故障检测](/redis-cluster-gossip.svg)
