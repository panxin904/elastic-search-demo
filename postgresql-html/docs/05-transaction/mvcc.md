---
title: MVCC 多版本并发控制
date: 2026-08-15  # date-auto-injected
---

# MVCC 多版本并发控制

> PostgreSQL 的灵魂：让读不阻塞写、写不阻塞读。**xmin / xmax 是 PG 的版本号系统**。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">PostgreSQL MVCC 版本链</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">多版本并发控制 · xmin/xmax · 元组可见性</text>

  <!-- 行级版本链 -->
  <text x="50" y="100" font-size="12" font-weight="700" fill="#1e293b">同一行的多个版本（按 xmin 排序）</text>

  <!-- Tuple v1 -->
  <rect class="at-hover-card" x="50" y="115" width="160" height="120" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="130" y="138" text-anchor="middle" font-size="12" font-weight="700" fill="#1e40af">Tuple v1</text>
  <text x="60" y="160" font-size="10" fill="#334155">xmin = 100</text>
  <text x="60" y="178" font-size="10" fill="#334155">xmax = 200</text>
  <text x="60" y="196" font-size="10" fill="#334155">data = {a:1}</text>
  <text x="60" y="214" font-size="10" fill="#64748b">t_xmin: T1</text>
  <text x="60" y="230" font-size="10" fill="#64748b">t_xmax: T2</text>

  <!-- Tuple v2 -->
  <rect class="at-hover-card" x="220" y="115" width="160" height="120" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="300" y="138" text-anchor="middle" font-size="12" font-weight="700" fill="#047857">Tuple v2 (current)</text>
  <text x="230" y="160" font-size="10" fill="#334155">xmin = 200</text>
  <text x="230" y="178" font-size="10" fill="#334155">xmax = 0 (活跃)</text>
  <text x="230" y="196" font-size="10" fill="#334155">data = {a:2}</text>
  <text x="230" y="214" font-size="10" fill="#64748b">t_xmin: T2</text>
  <text x="230" y="230" font-size="10" fill="#64748b">ctid = (0,1)</text>

  <!-- Tuple v3 -->
  <rect class="at-hover-card" x="390" y="115" width="160" height="120" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="470" y="138" text-anchor="middle" font-size="12" font-weight="700" fill="#92400e">Tuple v3 (in-flight)</text>
  <text x="400" y="160" font-size="10" fill="#334155">xmin = 300</text>
  <text x="400" y="178" font-size="10" fill="#334155">xmax = 0</text>
  <text x="400" y="196" font-size="10" fill="#334155">data = {a:3}</text>
  <text x="400" y="214" font-size="10" fill="#64748b">t_xmin: T3</text>
  <text x="400" y="230" font-size="10" fill="#64748b">uncommitted</text>

  <!-- 箭头 -->
  <line x1="210" y1="175" x2="220" y2="175" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>
  <line x1="380" y1="175" x2="390" y2="175" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

  <!-- 可见性规则 -->
  <rect x="40" y="260" width="520" height="120" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="285" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">可见性判定规则（简化版）</text>
  <text x="60" y="310" font-size="11" fill="#334155">事务 T 在快照 S 下看到元组 v 当且仅当：</text>
  <text x="60" y="332" font-size="11" font-weight="600" fill="#1e40af">① v.xmin 已提交  AND  v.xmin &lt; S.xmax</text>
  <text x="60" y="354" font-size="11" font-weight="600" fill="#dc2626">② v.xmax = 0  OR  v.xmax 未提交  OR  v.xmax &gt; S.xmin</text>
  <text x="60" y="372" font-size="10" fill="#475569" font-style="italic">即：插入事务先于快照完成，且删除事务尚未影响快照</text>

  <!-- 底部 -->
  <text x="300" y="410" text-anchor="middle" font-size="11" font-weight="600" fill="#1e293b">VACUUM 回收死亡元组</text>
  <text x="300" y="430" text-anchor="middle" font-size="10" fill="#64748b">UPDATE 不改原行，而是插入新版本（append-only） → 膨胀 → 需 VACUUM / autovacuum</text>
  <text x="300" y="450" text-anchor="middle" font-size="10" fill="#64748b">HOT update：同页内更新可避免索引膨胀（fillfactor 触发）</text>
</svg>

## 1. 什么是 MVCC？

```
MVCC（Multi-Version Concurrency Control）：
  - 同一行数据保留多个版本
  - 读看到的是某个时刻的快照
  - 写创建新版本，旧版本保留
  - 读不阻塞写，写不阻塞读

vs 锁并发：
  - MySQL InnoDB：行锁，读写互斥
  - PG MVCC：读写不互斥，并发更高

代价：
  - 多版本需要清理（vacuum）
  - 表会膨胀（需定期 vacuum）
  - 索引也会膨胀

📌 MVCC 是 PG 高并发的核心机制
   没有 MVCC，PG 的并发性能会大幅下降
```

## 2. 实现原理

### 2.1 行版本结构

```
PG 每行有 3 个隐藏列：
  - xmin：插入此版本的事务 ID
  - xmax：删除此版本的事务 ID（NULL 表示未删除）
  - cmin/cmax：命令 ID（同一事务内多命令）

📌 这 3 列默认不可见
```

```sql
-- 查看隐藏列
SELECT xmin, xmax, * FROM users LIMIT 1;

-- 创建表时显式包含
CREATE TABLE user_with_xmin (
  id    BIGSERIAL PRIMARY KEY,
  name  TEXT,
  xmin  XID,
  xmax  XID
);
```

### 2.2 插入流程

```
事务 T1 (xid=100) INSERT INTO users (name) VALUES ('Tom');

行版本：
  ┌──────┬─────────────┬──────┐
  │ id=1 │ name='Tom'  │      │
  │xmin=100│            │xmax=0│  ← NULL 表示有效
  └──────┴─────────────┴──────┘

T1 提交 → xmin=100 永远有效（除非被删除）
```

### 2.3 更新流程

```
事务 T2 (xid=200) UPDATE users SET name='Jerry' WHERE id=1;

PG 不直接修改，而是：
  1. 创建新版本（xmin=200）
  2. 旧版本 xmax 设为 200（标记删除）

  ┌─────────────────────────────┐
  │ id=1 │ name='Jerry'         │
  │ xmin=200 │                    │ xmax=0  ← 新版本
  ├─────────────────────────────┤
  │ id=1 │ name='Tom'           │
  │ xmin=100 │                    │ xmax=200  ← 旧版本被删除
  └─────────────────────────────┘
```

### 2.4 删除流程

```
事务 T3 (xid=300) DELETE FROM users WHERE id=1;

  ┌─────────────────────────────┐
  │ id=1 │ name='Jerry'         │
  │ xmin=200 │                    │ xmax=300  ← 标记删除
  └─────────────────────────────┘
  
行还在，只是 xmax=300
VACUUM 后才真正清理
```

### 2.5 可见性判断

```
事务 T4 (xid=400) SELECT * FROM users WHERE id=1;

判断行版本是否可见：
  1. 当前事务快照（snapshot）
     - 包含：已提交事务的 xid + 当前事务 xid
     - 不包含：未提交事务的 xid

  2. 行版本可见条件：
     - 行 xmin 在快照中（已提交）且 xmin < 当前 xid
     - 行 xmax 不在快照中（未删除或回滚）

📌 这是 MVCC 的核心算法
```

## 3. 事务快照

### 3.1 快照结构

```
快照包含：
  - xmin：创建快照时，仍活跃的最小 xid
  - xmax：创建快照时，下一个将被分配的 xid
  - xip_list：当前活跃事务的 xid 列表

例：
  活跃事务：100, 105, 110
  xmin=100, xmax=115
  xip_list=[100, 105, 110]

可见事务：
  - < 100（已提交）✓
  - 100, 105, 110（活跃）✗
  - >= 115（未开始）✗
```

### 3.2 快照获取时机

```
READ COMMITTED（默认）：
  - 每条 SQL 都获取新快照
  - 例：同一事务内两次 SELECT 可能看到不同数据

REPEATABLE READ：
  - 事务开始时获取快照，整个事务用同一个
  - 例：同一事务内两次 SELECT 看到相同数据

SERIALIZABLE：
  - 同 REPEATABLE READ + SSI 串行化检测
```

### 3.3 实际例子

```sql
-- 事务 A
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM users WHERE id = 1;  -- name='Tom'

-- 此时事务 B UPDATE 并提交
-- 事务 A 再次查询：
SELECT * FROM users WHERE id = 1;  -- 还是 'Tom'（快照不变）

COMMIT;
-- 事务 A 结束后，新事务才能看到 'Jerry'
```

## 4. Vacuum 机制

### 4.1 为什么需要 Vacuum？

```
MVCC 副作用：
  - 大量"死元组"（dead tuples）：被标记删除但还在表中
  - 表膨胀：占用空间，但不参与查询
  - 索引膨胀：索引也指向死元组
  - 性能下降：扫描更多死元组

Vacuum 任务：
  - 清理死元组
  - 释放空间给 PG 复用（不归还 OS）
  - 更新统计信息
  - 防止事务 ID 回卷（freeze）
```

### 4.2 Vacuum 流程

```sql
-- 手动 Vacuum
VACUUM users;
VACUUM;  -- 全库

-- Vacuum + 统计信息
VACUUM ANALYZE users;

-- 完整 Vacuum（锁表，仅离线维护用）
VACUUM FULL users;
-- ⚠️ 锁表、生成新文件、不复用空间

-- autovacuum（自动）
SHOW autovacuum;  -- 默认 on
```

### 4.3 autovacuum 调优

```sql
-- 查看 autovacuum 配置
SELECT name, setting FROM pg_settings WHERE name LIKE 'autovacuum%';

-- 关键参数
-- autovacuum_vacuum_threshold: 触发 vacuum 的死元组数（默认 50）
-- autovacuum_vacuum_scale_factor: 触发比例（默认 0.2 = 20%）
-- autovacuum_analyze_scale_factor: analyze 触发比例（默认 0.1）
-- autovacuum_naptime: 检查间隔（默认 60s）
-- autovacuum_max_workers: 最大 worker 数（默认 3）

-- 大表单独配置
ALTER TABLE big_events SET (
  autovacuum_vacuum_scale_factor = 0.05,  -- 5% 死元组就触发
  autovacuum_vacuum_threshold = 1000
);
```

### 4.4 Freeze

```
事务 ID 是 32 bit，循环使用：
  - 总共 2^32 = 4 billion 个事务
  - 假设 1000 QPS INSERT → 49 天用完
  - 必须定期 freeze，标记"永久可见"

Freeze 过程：
  - vacuum 时将 xmin 标记为 frozen（特殊 xid=2）
  - 不再比较 xmin < xmax，直接可见
  - 防止 transaction ID wraparound（回卷）
```

## 5. MVCC vs 其他数据库

| 数据库 | 实现 | 优点 | 缺点 |
|---|---|---|---|
| PostgreSQL | 行级 MVCC | 读写不阻塞 | 表膨胀 |
| MySQL InnoDB | 行级 MVCC（undo log） | 读写不阻塞 | undo 膨胀 |
| Oracle | 段级 MVCC | 空间可重用 | 段级锁 |
| SQL Server | 快照隔离（tempdb） | 简单 | tempdb 压力 |
| MongoDB | 文档级 MVCC | 灵活 | 仅文档级 |

## 6. 监控与调优

### 6.1 监控指标

```sql
-- 死元组数
SELECT relname, n_live_tup, n_dead_tup,
       ROUND(n_dead_tup::NUMERIC / NULLIF(n_live_tup, 0) * 100, 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;

-- 表膨胀
SELECT
  schemaname || '.' || relname AS table_name,
  pg_size_pretty(pg_relation_size(schemaname || '.' || relname)) AS size,
  ROUND(100 * pg_relation_size(schemaname || '.' || relname) /
        NULLIF(pg_total_relation_size(schemaname || '.' || relname), 0), 2) AS table_pct
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname || '.' || relname) DESC
LIMIT 10;

-- 长事务（最容易引起膨胀）
SELECT pid, usename, state, xact_start, NOW() - xact_start AS duration
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY xact_start;
```

### 6.2 调优建议

```
1. 启用 autovacuum（默认开）
2. 大表调低 autovacuum_vacuum_scale_factor
3. 监控长事务（> 1h 应报警）
4. 监控死元组率（> 20% 应处理）
5. 频繁 UPDATE/DELETE 的表调低 fillfactor
   ALTER TABLE hot_table SET (fillfactor = 70);
   -- 留 30% 空间给 HOT update（页内更新）
6. 考虑分区表（按时间），分区级 vacuum
```

## 7. MVCC 与索引

### 7.1 索引指向所有版本

```
PG 索引特点：
  - 索引项指向行的所有版本（不只是最新的）
  - 即使死元组，索引项还存在
  - VACUUM 后才清理索引项

代价：
  - 索引体积可能 > 表体积
  - VACUUM 同时清理索引

优化：
  - autovacuum 频率
  - 索引维护
```

### 7.2 HOT（Heap-Only Tuples）

```
HOT 优化：
  - 如果 UPDATE 不修改索引列，新版本在原页面内
  - 不更新索引项（减少索引膨胀）
  - 配合 fillfactor < 100

开启：
  - 默认开
  - 通过 fillfactor 调优页面空闲空间
```

## 8. 一句话总结

```
📌 MVCC = 每行多版本 + xmin/xmax 版本号 + 读快照
📌 优势：读写不阻塞，并发极高
📌 代价：死元组 + 表膨胀 + 需要 vacuum
📌 快照：READ COMMITTED 每条 SQL 一新，REPEATABLE READ 事务一快照
📌 Vacuum：autovacuum 默认开，大表要调低 scale_factor
📌 Freeze：防事务 ID 回卷，必须定期执行
📌 长事务是 MVCC 杀手：监控 + 报警 + 杀进程
📌 PG vs MySQL：都是行级 MVCC，但 PG 死元组在表内，MySQL 在 undo log
```

## 9. 参考资料

- PostgreSQL MVCC 官方文档 Chapter 13
- "PostgreSQL 修炼之道" MVCC 章节
- "PostgreSQL 14 Internals"（EGMONT）
- "PostgreSQL 9.0 MVCC 实现"
- pg_stat_user_tables 视图
- "Database Internals"（Alex Petrov）


<!-- auto-enrich:do-not-edit -->

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
