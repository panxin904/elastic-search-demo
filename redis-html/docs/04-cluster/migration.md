---
title: 数据迁移
date: 2026-08-15  # date-auto-injected
---

# 🚚 数据迁移

> Redis Cluster 支持**在线迁移槽位（slot）**，不影响服务运行。理解迁移原理对扩容、缩容、负载均衡至关重要。

## 🎯 什么是数据迁移？

```
场景：
  Master A 有 5461 个槽位（0-5460）
  Master B 有 5462 个槽位（5461-10922）
  Master C 有 5461 个槽位（10923-16383）
  
  添加新节点 Master D 后：
    需要从 A/B/C 各迁出部分槽位给 D
    让 4 个 Master 平均分配 16384 个槽位
```

**数据迁移 = 槽位迁移 = 把指定 slot 的 key 从源节点搬到目标节点**。

## 🔄 迁移流程

```
┌──────────────────────────────────────────────┐
│                  客户端                       │
└──────────────┬───────────────────────────────┘
               │ SET key1 value
               ▼
        ┌──────────────┐
        │  源 Master A │ slot 5258 在 A
        └──────┬───────┘
               │ 1. A 标记 slot 5258 为 MIGRATING
               ▼
        ┌──────────────┐
        │ 目标 Master D│ D 标记 slot 5258 为 IMPORTING
        └──────┬───────┘
               │ 2. A 逐个 key 迁移到 D
               ▼
        ┌──────────────┐
        │  D 接收 keys  │
        └──────┬───────┘
               │ 3. 迁移完成
               ▼
        两个节点都设置：
        CLUSTER SETSLOT 5258 NODE <D-id>
```

## 📋 迁移命令详解

### 1. 标记状态

```bash
# 在源节点（接收者）执行
CLUSTER SETSLOT <slot> IMPORTING <source-node-id>
# 标记为 IMPORTING：准备接收该 slot 的 key

# 在目标节点（迁出者）执行
CLUSTER SETSLOT <slot> MIGRATING <target-node-id>
# 标记为 MIGRATING：正在迁出该 slot 的 key
```

### 2. 实际迁移

```bash
# 在源节点执行
MIGRATE <target-ip> <target-port> "" 0 <timeout> KEYS <key>

# 内部流程：
# 1. 源节点建立到目标的连接（R-Channel）
# 2. 序列化 key 的数据
# 3. 发送到目标节点
# 4. 目标节点接收并存入
# 5. 源节点删除该 key
# 6. 整个流程是同步阻塞
```

### 3. 完成迁移

```bash
# 两个节点都执行
CLUSTER SETSLOT <slot> NODE <new-master-id>

# 通知全集群更新
CLUSTER SETSLOT <slot> NODE <new-master-id>
# 其他节点通过 Gossip 自动收到更新
```

## 🛠️ 自动化工具

### redis-cli 自动 reshard

```bash
redis-cli --cluster reshard 192.168.1.10:7001

# 交互式问答：
# How many slots do you want to move? 1365
# What is the receiving node ID? <D-id>
# Source node #1: <A-id>
# Source node #2: <B-id>
# Source node #3: <C-id>
# Do you want to proceed? yes
```

### 一次性脚本

```bash
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-from <A-id> \
    --cluster-to <D-id> \
    --cluster-slots 1365 \
    --cluster-yes
```

## 📊 迁移期间客户端行为

```
迁移过程中客户端请求：

1. 客户端请求 slot 5258 到 Master A
2. Master A 已迁移部分 key，剩余 key 还在 A
3. Master A 返回：
   - 命中已迁移的 key：
     - A 没这个 key → 返回 ASK 重定向到 D
     - 客户端下次访问 slot 5258 → 临时发到 D
   - 命中未迁移的 key：
     - 正常返回数据

4. 迁移完成：
   - slot 5258 全部归属 D
   - A 返回 MOVED 重定向到 D
   - 客户端永久更新路由表
```

## ⚙️ 迁移性能优化

### 批量迁移

```bash
# 每次 MIGRATE 一个 key 太慢
# redis-cli 自动按批迁移（默认 10 个 key 一批）

# 调整批大小
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-pipeline 100      # 每批 100 个 key
    --cluster-slots 1365
```

### 限制迁移速度

```bash
# 使用 redis-cli throttling
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-timeout 5000      # 每批间隔 5 秒
```

## 🛠️ 实战：扩缩容迁移

### 扩容流程

```bash
# 1. 启动新节点（无数据）
redis-server /redis-cluster/7007/redis.conf

# 2. 加入集群
redis-cli --cluster add-node 192.168.1.10:7007 192.168.1.10:7001

# 3. 添加 Replica（如 7008）
redis-cli --cluster add-node 192.168.1.10:7008 192.168.1.10:7001 \
    --cluster-slave \
    --cluster-master-id <7007-id>

# 4. 重新分片（迁移部分槽位到新节点）
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-from all \
    --cluster-to <7007-id> \
    --cluster-slots 4096 \
    --cluster-yes

# 5. 观察迁移进度
redis-cli -h 192.168.1.10 -p 7007 CLUSTER INFO
```

### 缩容流程

```bash
# 1. 把要删除的 Master 槽位迁到其他节点
redis-cli --cluster reshard 192.168.1.10:7001 \
    --cluster-from <to-delete-id> \
    --cluster-to <other-master-id> \
    --cluster-slots 5461 \
    --cluster-yes

# 2. 等所有 slot 迁移完成
redis-cli -h 192.168.1.10 -p <to-delete-port> CLUSTER INFO
# cluster_known_nodes: 6（确认所有 key 已迁移）

# 3. 删除 Replica
redis-cli --cluster del-node 192.168.1.10:7001 <replica-id>

# 4. 删除 Master
redis-cli --cluster del-node 192.168.1.10:7001 <master-id>

# 5. 停止 Redis
redis-cli -h 192.168.1.10 -p <port> SHUTDOWN
```

## ⚠️ 迁移期间注意事项

```bash
# 1. 避免大 Key 阻塞迁移
#    大 Key 同步阻塞 MIGRATE，影响源节点性能
#    推荐：先拆分大 Key

# 2. 低峰期迁移
#    业务高峰期迁移会导致客户端 ASK 重定向增多
#    推荐：凌晨或低 QPS 时段

# 3. 监控客户端错误率
#    迁移期间 MOVED/ASK 增加属于正常现象
#    但错误率超过 1% 需要排查

# 4. 不要在迁移时重启节点
#    节点重启会重置 cluster-epoch，影响选举

# 5. 网络带宽
#    跨机房迁移会占用大量带宽
#    推荐：同机房迁移，或限制速度
```

## 📊 迁移速度参考

```
场景：1 个 slot，5000 个 key，平均每个 100 字节

迁移耗时：
  - 单 key 模式：~50 秒
  - 批量 100 个：~5 秒
  - 批量 1000 个：~1 秒

网络占用（批量模式）：
  - 100 key/批 ≈ 100KB
  - 10 批/秒 ≈ 1MB/秒
```

## 🐛 故障案例

### 案例 1：迁移卡住

```
现象：reshard 一直不完成
原因：某个 key 太大，迁移阻塞
解决：
  1. 查看 INFO 命令统计：migrate_cached_sockets
  2. 删除大 Key 或拆分
  3. 重启 reshard 流程
```

### 案例 2：迁移后 slot 状态不对

```
现象：CLUSTER SLOTS 显示 slot 归属错误
原因：SETSLOT NODE 命令未在所有节点执行
解决：
  1. 手动 CLUSTER SETSLOT <slot> NODE <correct-id>
  2. 在所有节点执行
```

### 案例 3：客户端大量 ASK 重定向

```
现象：迁移期间错误率飙升
原因：客户端未实现 ASK 处理逻辑
解决：
  1. 升级客户端 SDK（Lettuce 6+ 已支持）
  2. 降低迁移速度（--cluster-pipeline 调小）
  3. 在低峰期迁移
```

## 🎯 总结

**数据迁移核心要点**：
- ✅ 在线迁移不中断服务
- ✅ MIGRATING + IMPORTING 两阶段
- ✅ redis-cli --cluster reshard 自动化
- ✅ 客户端需支持 MOVED 和 ASK
- ⚠️ 大 Key 会阻塞迁移
- ⚠️ 低峰期迁移更安全

**下一步：** [📈 集群扩容](/04-cluster/scale) — 加节点、负载均衡、缩容实战


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
