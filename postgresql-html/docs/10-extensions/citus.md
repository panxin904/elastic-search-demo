---
title: Citus 分布式
date: 2026-08-15  # date-auto-injected
description: PG 水平扩展方案
---

# Citus 分布式

> **TL;DR**：Citus = PG 的**水平分片扩展**。**10 亿行表拆到 N 个 worker 节点**，**查询自动并行**。**适用**：实时分析、SaaS 多租户、IoT 时序。

## 一句话定义

```
Citus = PG 的分片扩展
     = 1 个协调节点（coordinator）+ N 个工作节点（worker）
     = 自动分片、并行查询
```

## 适用场景

```
✓ SaaS 多租户（每租户独立分片）
✓ 实时分析（千万级实时聚合）
✓ IoT 时序数据
✓ 大表（> 1 亿行）
✓ 高 QPS（> 10 万 QPS）

✗ 强 OLTP（事务一致性受限）
✗ 跨节点 JOIN（性能差）
```

## 安装

```bash
# Ubuntu/Debian
apt install postgresql-15-citus

# 或从源码
# https://github.com/citusdata/citus
```

```sql
-- 所有节点启用扩展
CREATE EXTENSION citus;
```

## 集群部署

```
节点：
  - coordinator（1 个）：接收查询、分发
  - worker（N 个）：存储数据、执行子查询

端口：
  - coordinator: 5432
  - worker: 5432（不同机器）

最小配置：1 coordinator + 2 workers（生产推荐）
```

```sql
-- 1. coordinator 上加 worker 节点
SELECT citus_add_node('worker1.db', 5432);
SELECT citus_add_node('worker2.db', 5432);

-- 2. 看节点列表
SELECT * FROM citus_get_active_worker_nodes();

-- 3. 看集群健康
SELECT * FROM citus_check_cluster_health();
```

## 创建分布式表

```sql
-- 1. 选分布列（高基数 / 高频 JOIN 列）
--    user_id / tenant_id / sensor_id

-- 2. 分布表
SELECT create_distributed_table('events', 'user_id');
-- 自动按 user_id hash 分布到 worker 节点
```

**分布列选择**：

```
✓ user_id（高基数，每行不同）
✓ tenant_id（多租户）
✗ status（低基数，所有行分布不均）
✗ created_at（数据倾斜，老数据集中）
```

## 表类型

### 1. 分布式表

```sql
SELECT create_distributed_table('events', 'user_id');
-- 数据分布到所有 worker
```

### 2. 引用表（Reference Table）

```sql
SELECT create_reference_table('countries');
-- 每个 worker 都有完整副本（小表，用于 JOIN）
```

### 3. 本地表（Local Table）

```sql
-- 只在 coordinator（不分布）
-- 用于管理数据
```

## 实战案例

### 案例 1：SaaS 多租户

```sql
-- 用户表（参考表）
CREATE TABLE tenants (
  id BIGINT PRIMARY KEY,
  name TEXT
);
SELECT create_reference_table('tenants');

-- 订单表（按 tenant_id 分布）
CREATE TABLE orders (
  id BIGSERIAL,
  tenant_id BIGINT NOT NULL,
  amount NUMERIC(10,2),
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (id, tenant_id)
);
SELECT create_distributed_table('orders', 'tenant_id');

-- 索引自动在每个 worker 上创建
CREATE INDEX idx_orders_tenant_created ON orders (tenant_id, created_at);

-- 查询
-- 自动推到对应 worker（shard pruning）
SELECT * FROM orders WHERE tenant_id = 123;
```

### 案例 2：实时分析

```sql
CREATE TABLE events (
  id BIGSERIAL,
  user_id BIGINT,
  event_type TEXT,
  ts TIMESTAMPTZ DEFAULT now()
);
SELECT create_distributed_table('events', 'user_id');

-- 实时聚合（推到 worker 并行执行）
SELECT
  date_trunc('hour', ts) AS hour,
  count(*) AS cnt
FROM events
WHERE ts >= now() - interval '1 day'
GROUP BY hour;
```

### 案例 3：迁移单 PG 到 Citus

```sql
-- 1. 单 PG 实例（已有大表）
-- 2. 部署 Citus 集群
-- 3. 在线迁移
--    a. create_distributed_table（自动分布）
--    b. 数据自动迁移到 worker
--    c. 切换应用到 coordinator
```

## 性能优化

```sql
-- 1. 选好分布列（最重要）
--    避免热点 user_id

-- 2. 用 co-location（关联表用同一分布列）
SELECT create_distributed_table('users', 'user_id');
SELECT create_distributed_table('orders', 'user_id');
-- JOIN 不跨节点

-- 3. 用 reference table（小表）
SELECT create_reference_table('products');

-- 4. 分区大表（组合 Citus + 时间分区）
SELECT create_distributed_table('events', 'user_id');
-- events 按 user_id 分布，按 ts 分区
```

## 监控

```sql
-- 1. 节点状态
SELECT * FROM citus_get_active_worker_nodes();

-- 2. 表分布信息
SELECT
  logical_relid,
  partmethod,
  partkey
FROM pg_dist_partition;

-- 3. 分片位置
SELECT
  shardid,
  shardstate,
  nodename,
  nodeport,
  size
FROM pg_dist_shard_placement
JOIN pg_dist_shard USING (shardid)
LIMIT 10;

-- 4. 集群健康
SELECT * FROM citus_check_cluster_health();
```

## 限制

```
✗ 不支持跨节点事务（Citus 10 之前）
✗ 不支持 cross-shard JOIN（除非 colocation）
✗ 不支持视图（PG 视图可以，但 Citus 不优化）
✗ 节点增减需要 rebalance
```

## 一句话总结

> **Citus = PG 水平扩展方案**：**多租户、实时分析、大表**首选。**colocation（同分布列）让 JOIN 不跨节点**。**生产推荐 1 coordinator + 4-8 workers + sh 2**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
