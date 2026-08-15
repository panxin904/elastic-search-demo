---
title: 哈希槽分片
---

# 🎰 哈希槽分片

> Redis Cluster 用 **16384 个哈希槽（hash slot）**做数据分片，每个 key 通过 **CRC16 算法**映射到固定槽位。

## 🎯 为什么是 16384 个槽？

```
候选值：65536（2^16）

为什么不用 65536：
  ❌ 节点间心跳包包含所有槽位信息（65536 bit = 8KB/包）
  ❌ 网络带宽压力大
  ❌ 心跳包解析慢

为什么用 16384（2^14）：
  ✅ 16384 bit = 2KB/包，压缩到 65536 的 1/4
  ✅ 带宽压力小
  ✅ Redis 作者 antirez 解释：16384 是性能和分布均匀性的最优平衡

16384 的分布：
  集群规模      每 Master 槽位
  3 Master      ~5461
  4 Master      ~4096
  8 Master      ~2048
  16 Master     ~1024
  100 Master    ~164
```

## 🔢 CRC16 算法

```
slot = CRC16(key) % 16384

Redis 使用 CRC16-CCITT 多项式：
  G(x) = x^16 + x^12 + x^5 + 1 (0x1021)

示例：
  CRC16("user:1")   = 12345
  12345 % 16384     = 12345

  CRC16("order:100") = 30000
  30000 % 16384     = 13616
```

### 计算 key 槽位

```bash
redis-cli CLUSTER KEYSLOT "user:1"
# → 5258

redis-cli CLUSTER KEYSLOT "{user:1001}.name"
# → 只计算 {tag} 部分 = CRC16("user:1001") % 16384
```

## 📊 槽位分配

```
Cluster 拓扑（3 Master）：
  Master A: slots 0-5460      (5461 个槽位)
  Master B: slots 5461-10922  (5462 个槽位)
  Master C: slots 10923-16383  (5461 个槽位)

查看当前分配：
  CLUSTER SLOTS
  CLUSTER NODES
```

### 手动分配槽位

```bash
# 把 slot 0 添加到当前节点
CLUSTER ADDSLOTS 0 1 2 3 4 5 6 7 8 9

# 或从其他节点迁入（接收）
CLUSTER SETSLOT 1000 IMPORTING <source-node-id>

# 批量分配（自动均分）
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-from all \
    --cluster-to <new-node-id> \
    --cluster-slots 4096 \
    --cluster-yes
```

## 🔀 重定向机制

### MOVED（永久）

```
客户端 SET "user:1" "Alice" → 连接到 Master B
实际槽位 5258 在 Master A
Master B 返回：
  MOVED 5258 192.168.1.10:7001

客户端行为：
  1. 更新本地路由表：slot 5258 → Master A
  2. 重新发送请求到 Master A
```

**MOVED 是永久重定向**，表示槽位稳定在某个 Master。

### ASK（临时，迁移中）

```
迁移过程中：
  - 源 Master：slot 5258 importing
  - 目标 Master：slot 5258 migrating

客户端请求 slot 5258 到源 Master：
  源 Master 返回：
    ASK 5258 192.168.1.10:7003  # 下一个请求请去这里

  客户端行为：
    1. 不更新路由表
    2. 临时发送请求到目标 Master（带 ASKING 前缀）
    3. 下次还是查路由表
```

**ASK 是临时重定向**，表示槽位正在迁移中。

### MOVED vs ASK 对比

| 维度 | MOVED | ASK |
|------|-------|-----|
| 时机 | 槽位稳定后 | 槽位迁移中 |
| 是否更新路由表 | ✅ 是 | ❌ 否 |
| 客户端行为 | 永久转向新节点 | 临时查询，下次回路由 |
| 含义 | 槽位在哪 | 槽位迁移过程中临时在哪 |

## 🔒 Hash Tag（标签路由）

> **问题**：想对关联数据（user:1, user:2, order:100）做事务/Multi-key 操作，但它们在不同的 slot。

**解决**：用 `{tag}` 强制路由到同一 slot。

```bash
# 普通 key
SET user:1 "Alice"             # slot = CRC16("user:1") % 16384
SET user:2 "Bob"               # slot = CRC16("user:2") % 16384
# 两个 slot 不同！

# Hash Tag
SET {user:1}.name "Alice"      # slot = CRC16("user:1") % 16384（只看花括号内）
SET {user:1}.age 28            # slot = CRC16("user:1") % 16384
# 两个 slot 相同！

# 实战：按用户分组
HSET user:{1001} name "Alice" age 28
HGET user:{1001} name
# 所有 user:1001 相关数据都在同一槽位

# 实战：购物车
HSET cart:{user:1001} item1 1
HGETALL cart:{user:1001}
```

## 🎯 slot 路由策略

### 一致性 vs 简单性

```
Hash Tag 路由：
  - 同一 tag 的所有 key 在同一节点
  - 方便事务、批量操作
  - 数据倾斜风险（某 tag 太大）

CRC16 路由：
  - 默认均匀分布
  - 不支持跨槽事务
  - 适合无关联的散列数据
```

### 多 key 操作技巧

```java
// Spring Data Redis 中，按 slot 分组 Pipeline
// 1. 计算每个 key 的 slot
Map<Integer, List<String>> keysBySlot = keys.stream()
    .collect(Collectors.groupingBy(k -> CRC16.crc16(k.getBytes()) % 16384));

// 2. 按 slot 发送 Pipeline
keysBySlot.forEach((slot, keysForSlot) -> {
    // 向该 slot 对应的 Master 发送 Pipeline
    redisTemplate.executePipelined((RedisCallback) connection -> {
        keysForSlot.forEach(k -> connection.stringCommands().set(k.getBytes(), value.getBytes()));
        return null;
    });
});
```

## 📊 槽位迁移

### 迁移流程

```
1. 在目标节点执行：
   CLUSTER SETSLOT 5258 IMPORTING <source-node-id>

2. 在源节点执行：
   CLUSTER SETSLOT 5258 MIGRATING <target-node-id>

3. 源节点返回 ASK 5258 target-ip:port 给客户端

4. 源节点迁移 key 到目标节点：
   MIGRATE target-ip target-port "" 0 5258 <timeout> KEYS key1 key2

5. 迁移完成后：
   CLUSTER SETSLOT 5258 NODE <new-master-id>
   （两个节点都执行）
```

### 迁移命令

```bash
# redis-cli 自动迁移工具
redis-cli --cluster reshard 192.168.1.10:7001

# 手动迁移单个 slot
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-from <source-id> \
    --cluster-to <target-id> \
    --cluster-slots 1 \
    --cluster-yes
```

## 🎯 总结

**哈希槽分片核心要点**：
- ✅ 16384 个槽位（不是 65536）
- ✅ CRC16(key) % 16384 计算槽位
- ✅ MOVED 永久重定向 / ASK 临时重定向
- ✅ Hash Tag 强制同一槽位（事务友好）
- ✅ 槽位迁移：IMPORTING + MIGRATING 两阶段

**下一步：** [💬 Gossip 协议](/04-cluster/gossip) — 节点间如何发现和通信
