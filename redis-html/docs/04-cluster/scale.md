---
title: 集群扩容
date: 2026-08-15  # date-auto-injected
---

# 📈 集群扩容

> 业务增长导致单机容量/性能不够时，需要**水平扩容**——增加 Master 节点，重新分片。

## 🎯 扩容场景

```
场景 1：单机内存满了
  现有 3 Master × 16GB = 48GB
  业务需要 80GB
  → 扩容到 5 Master × 16GB = 80GB

场景 2：写 QPS 上限
  现有 3 Master，每节点写 QPS 上限 ~8 万
  业务 QPS 达到 25 万
  → 扩容到 4 Master，QPS 上限提升到 ~32 万

场景 3：容灾要求更高
  现有 3 Master 3 Replica（1 副本）
  业务要求 2 副本
  → 增加 3 个 Replica

场景 4：机房迁移
  单机房 → 双机房（同城主备）
  → 增加新机房节点，数据迁移
```

## ⚖️ 扩容 vs 缩容

| 维度 | 扩容 | 缩容 |
|------|------|------|
| 操作 | 添加 Master/Replica | 删除 Master/Replica |
| 风险 | 中（数据迁移） | 高（数据丢失风险） |
| 影响 | 迁移期间客户端 ASK | 误删可能导致数据丢失 |
| 推荐时机 | 低峰期 | 极低峰期或停服窗口 |

## 🔄 Slot 重分配流程

![Redis Cluster Slot 重分配](/redis-cluster-slot-reshard.svg)

## 📋 扩容步骤（3 → 4 Master）

### 1. 启动新节点

```bash
# 新 Master 节点（端口 7007）
cat > /redis-cluster/7007/redis.conf << EOF
port 7007
cluster-enabled yes
cluster-config-file nodes.conf
cluster-node-timeout 5000
appendonly yes
daemonize yes
dir /redis-cluster/7007
EOF

redis-server /redis-cluster/7007/redis.conf
```

### 2. 加入集群

```bash
# 让新节点加入集群（meet 任意现有节点）
redis-cli --cluster add-node 192.168.1.10:7007 192.168.1.10:7001

# 输出：
# [OK] New node added correctly.
```

**此时**：新节点没有分配任何槽位（slots: []），不承担流量。

### 3. 添加 Replica（如需要）

```bash
# 启动新 Replica（端口 7008）
redis-server /redis-cluster/7008/redis.conf

# 加入集群并指定其 Master 为 7007
redis-cli --cluster add-node 192.168.1.10:7008 192.168.1.10:7001 \
    --cluster-slave \
    --cluster-master-id <7007-node-id>
```

### 4. 重新分片

```bash
# 从现有 3 个 Master 各迁 1365 个槽位给新节点（共 4096）
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-from all \
    --cluster-to <7007-id> \
    --cluster-slots 4096 \
    --cluster-yes

# 输出示例：
# Moving slot 0 from 192.168.1.10:7001 to 192.168.1.10:7007:
# Moving slot 1 from 192.168.1.10:7001 to 192.168.1.10:7007:
# ...
# [OK] All 16384 slots covered
```

### 5. 验证扩容结果

```bash
# 检查集群状态
redis-cli -h 192.168.1.10 -p 7001 CLUSTER INFO

# 输出：
# cluster_known_nodes:8       # 4 Master + 4 Replica
# cluster_slots_assigned:16384

# 查看节点角色
redis-cli -h 192.168.1.10 -p 7001 CLUSTER NODES
```

## 🛠️ 扩容脚本（自动化）

```bash
#!/bin/bash
# expand_cluster.sh
# 从 3 Master 扩到 5 Master

set -e

NEW_NODES=("192.168.1.10:7007" "192.168.1.10:7009")
EXISTING_NODE="192.168.1.10:7001"
SLOTS_PER_NEW=2048   # 2×2048 = 4096，新增给 2 个 Master

echo "=== 添加新 Master 节点 ==="
for node in "${NEW_NODES[@]}"; do
    IFS=':' read -r ip port <<< "$node"
    redis-cli --cluster add-node $node $EXISTING_NODE
done

echo "=== 重新分片 ==="
sleep 5
for node in "${NEW_NODES[@]}"; do
    IFS=':' read -r ip port <<< "$node"
    node_id=$(redis-cli -h $ip -p $port CLUSTER MYID)
    redis-cli --cluster reshard $EXISTING_NODE \
        --cluster-from all \
        --cluster-to $node_id \
        --cluster-slots $SLOTS_PER_NEW \
        --cluster-yes
done

echo "=== 验证 ==="
redis-cli -h 192.168.1.10 -p 7001 CLUSTER INFO
echo "✅ 扩容完成"
```

## ⚠️ 扩容期间的影响

### 1. 客户端行为

```
扩容期间（约几分钟到几小时）：
  - 部分 key 触发 ASK 重定向（临时）
  - 客户端会自动重试
  - 业务延迟略有增加
  - 错误率短暂上升（但客户端 SDK 应自动处理）

扩容完成后：
  - 所有 key 触发 MOVED 重定向（永久）
  - 客户端更新路由表
  - 业务恢复正常
```

### 2. 性能影响

```
对源 Master：
  - 迁移期间需响应 MIGRATE 请求
  - 发送 key 数据占用网络带宽
  - 同步阻塞 MIGRATE 命令

对目标 Master：
  - 接收 key 数据并存储
  - 持续写入压力

对集群整体：
  - 网络流量增加
  - 客户端延迟增加
```

### 3. 减少扩容影响

```bash
# 1. 低峰期扩容
#    凌晨 2-5 点最佳

# 2. 限制迁移速度
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-pipeline 50       # 每批 50 个 key（默认 10）
    --cluster-timeout 3000      # 每批间隔 3 秒

# 3. 分批扩容（每次只扩一个 Master）
#    不要一次加 5 个 Master 同时 reshard

# 4. 避免大 Key
#    提前清理大 Key
```

## 📋 缩容步骤

```bash
# 1. 把要删除的 Master 槽位迁到其他节点
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-from <to-delete-id> \
    --cluster-to <keep-master-id> \
    --cluster-slots 4096 \
    --cluster-yes

# 2. 等所有 slot 迁移完成
while true; do
    assigned=$(redis-cli -h <to-delete-ip> -p <to-delete-port> CLUSTER INFO | grep cluster_slots_assigned | awk -F: '{print $2}' | tr -d '\r')
    if [ "$assigned" = "0" ]; then
        echo "All slots migrated"
        break
    fi
    sleep 5
done

# 3. 先删除 Replica
redis-cli --cluster del-node 192.168.1.10:7001 <replica-id>

# 4. 再删除 Master
redis-cli --cluster del-node 192.168.1.10:7001 <master-id>

# 5. 停止 Redis
redis-cli -h <ip> -p <port> SHUTDOWN
```

## 🎯 最佳实践

```
扩容前准备：
  ✅ 评估容量和性能需求
  ✅ 选择扩容时机（低峰期）
  ✅ 提前清理大 Key
  ✅ 测试客户端 ASK 重定向

扩容过程：
  ✅ 监控源 Master CPU、网络带宽
  ✅ 监控目标 Master 写入 QPS
  ✅ 监控客户端错误率（应 < 1%）
  ✅ 准备回滚方案

扩容后验证：
  ✅ CLUSTER INFO 确认所有 slot 已分配
  ✅ 客户端路由表已更新
  ✅ 业务延迟恢复正常
  ✅ 备份新集群配置
```

## 📊 扩容性能参考

```
场景：4 GB 数据，500 万 key，从 3 Master 扩到 5 Master

时间：
  - 启动新节点：~1 分钟
  - 加入集群：~10 秒
  - 重新分片：~30 分钟（取决于网络和 key 大小）
  - 客户端路由表更新：~1 分钟

网络占用：
  - 4GB 数据在 ~30 分钟内传输 ≈ 2.3 MB/秒

对业务影响：
  - 短暂延迟增加 5-10ms
  - ASK 重定向期间错误率 < 0.5%
  - 完成后完全恢复
```

## 🎯 总结

**扩容核心要点**：
- ✅ 加节点 → 加入集群 → 重新分片
- ✅ redis-cli --cluster reshard 自动化
- ✅ 低峰期扩容 + 限制速度
- ⚠️ 缩容风险更高，需确认所有 slot 已迁移
- ⚠️ 大 Key 阻塞迁移

**下一步：** [🔧 Jedis](/05-jdk/jedis) — Java 客户端基础
