---
title: MySQL vs PostgreSQL
---

# MySQL vs PostgreSQL

> 关系型数据库两大巨头，各有所长。**没有最好，只有最适合**。

## 1. 总体对比

```
MySQL：
  - 起源：1995 年，瑞典 MySQL AB
  - 现状：Oracle 旗下
  - 哲学：易用、性能优先、开箱即用
  - 主流版本：8.0+（InnoDB）
  - 主要用户：互联网公司（淘宝 / 美团 / Twitter）

PostgreSQL：
  - 起源：1986 年，加州伯克利分校 POSTGRES 项目
  - 现状：开源社区，全球贡献者
  - 哲学：严谨、标准、可扩展
  - 主流版本：17.x
  - 主要用户：技术深度公司（GitHub / Reddit / Instagram）

📌 不是"非此即彼"
   - 大量公司两个都用
   - 不同业务不同选型
```

## 2. SQL 标准支持

| 标准 | PostgreSQL | MySQL |
|---|---|---|
| SQL:2016 核心 | 100% | ~70% |
| 窗口函数 | ✅ | ✅ 8.0+ |
| CTE | ✅ 8.4+ | ✅ 8.0+ |
| 递归 CTE | ✅ | ✅ |
| UPSERT | ✅ ON CONFLICT | ✅ ON DUPLICATE KEY |
| MERGE | ✅ 15+ | ✅ 8.0+ |
| JSON 路径 | ✅ 12+ | ⚠️ 有限 |
| 物化视图 | ✅ | ❌ |
| 生成列 | ✅ | ✅ |
| 全文检索 | ✅ 内置 | ⚠️ 有限 |
| CHECK 约束 | ✅ | ✅ 8.0+ |

📌 PG 是 SQL 标准的事实遵循者
   MySQL 早期大量偏离标准（已逐步修复）

## 3. 数据类型

| 类型 | PostgreSQL | MySQL |
|---|---|---|
| 内置数量 | ~40 | ~30 |
| 数组 | ✅ | ❌ |
| JSONB | ✅（索引） | ✅ JSON（无索引） |
| Range | ✅ | ❌ |
| UUID | ✅ 原生 | ✅ |
| 几何 | ✅ | ✅ 基础 |
| 自定义类型 | ✅ CREATE TYPE | ❌ |
| Domain | ✅ | ❌ |
| 货币 | ✅ money | ✅ DECIMAL |

📌 PG 类型丰富度远超 MySQL
   PG 是"可扩展"的（CREATE TYPE / CREATE OPERATOR）

## 4. 索引

| 索引 | PostgreSQL | MySQL |
|---|---|---|
| B-Tree | ✅ | ✅ |
| Hash | ✅ 10+ | ✅ 8.0+ |
| GIN | ✅（JSONB / 全文 / 数组） | ❌ |
| GiST | ✅（空间 / 全文 / 范围） | ❌（SPATIAL 有限） |
| BRIN | ✅（大表） | ❌ |
| SP-GiST | ✅（IP / 电话） | ❌ |
| 表达式索引 | ✅ | ✅ |
| 部分索引 | ✅ WHERE | ❌ |
| 覆盖索引 | ✅ INCLUDE | ✅ |

📌 PG 索引类型是 MySQL 的 3-5 倍
   GIN 让 PG 索引 JSONB / 全文成为可能

## 5. 高级 SQL 特性

### 5.1 窗口函数

```sql
-- 两者都支持，但 PG 更早、更完整

-- PG 8.4+（2010 年）
SELECT user_id, amount,
       ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rk,
       LAG(amount) OVER (PARTITION BY user_id ORDER BY created_at) AS prev_amount
FROM orders;

-- MySQL 8.0+（2018 年）才支持
-- 之前用子查询模拟
```

### 5.2 CTE

```sql
-- PG 8.4+
WITH regional_sales AS (
  SELECT region, SUM(amount) AS total
  FROM orders
  GROUP BY region
)
SELECT * FROM regional_sales WHERE total > 10000;

-- PG 12+：可控制 CTE 物化（NOT MATERIALIZED）
-- MySQL 8.0+ 支持 CTE，但一直内联（无法选择物化）
```

### 5.3 JSONB vs JSON

```sql
-- PG JSONB + GIN 索引
CREATE TABLE products (data JSONB);
CREATE INDEX idx ON products USING GIN (data);
SELECT * FROM products WHERE data @> '{"tags": ["phone"]}';
-- 毫秒级

-- MySQL JSON（文本存储 + 函数索引）
CREATE TABLE products (data JSON);
CREATE INDEX idx ON products ((JSON_EXTRACT(data, '$.brand')));
SELECT * FROM products WHERE JSON_EXTRACT(data, '$.brand') = 'Apple';
-- 索引只对特定路径有效
```

### 5.4 UPSERT

```sql
-- PG：ON CONFLICT
INSERT INTO users (id, name) VALUES (1, 'Tom')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- MySQL：ON DUPLICATE KEY
INSERT INTO users (id, name) VALUES (1, 'Tom')
ON DUPLICATE KEY UPDATE name = VALUES(name);
```

### 5.5 物化视图

```sql
-- PG：原生物化视图
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT DATE_TRUNC('month', created_at) AS month, SUM(amount)
FROM orders GROUP BY 1;

REFRESH MATERIALIZED VIEW monthly_sales;

-- MySQL：无物化视图（用汇总表 / 触发器模拟）
```

## 6. 事务与并发

| 维度 | PostgreSQL | MySQL InnoDB |
|---|---|---|
| 隔离级别 | 4 种 | 4 种 |
| MVCC | ✅ 行级 | ✅ 行级 |
| 死元组位置 | 表内（vacuum 清理） | undo log |
| 表膨胀 | 需要 vacuum | 不明显（undo 循环） |
| 长事务 | 影响大（阻塞 vacuum） | 影响较小 |
| 串行化 | SSI（14+） | 无（仅 REPEATABLE READ） |

📌 PG MVCC 优势：读写不阻塞
   PG MVCC 劣势：长事务会让表膨胀（MySQL 没这问题）

## 7. 性能

### 7.1 OLTP（在线事务）

```
简单查询 / 写入：
  - MySQL InnoDB 略胜（5-15%）
  - PG 写入略慢（每行版本号 + xmin/xmax）

复杂查询：
  - PG 完胜（优化器更强）
  - 大表 JOIN / 子查询 / CTE 性能差距明显

📌 MySQL 适合：高并发简单查询（电商 / 社交）
   PG 适合：复杂分析 + 业务逻辑
```

### 7.2 OLAP（在线分析）

```
PG 完胜：
  - 窗口函数强大
  - CTE 优化
  - 并行查询（10x 提升）
  - JOIN 优化

📌 MySQL 不擅长 OLAP
   MySQL 用户用 ClickHouse / Doris 做 OLAP
   PG 用户直接用 PG 做中小型 OLAP
```

### 7.3 基准测试

```
Sysbench OLTP 100万行：
  - MySQL 8.0：~50000 TPS
  - PG 16：~35000 TPS  ← 简单场景略慢

TPC-H 22 查询：
  - MySQL 8.0：很多查询需要优化
  - PG 16：直接跑通，优化器自动选择最佳计划
```

## 8. 扩展生态

| 扩展 | MySQL | PostgreSQL |
|---|---|---|
| 空间数据库 | ⚠️ MySQL Spatial | ✅ PostGIS |
| 向量数据库 | ❌ | ✅ pgvector |
| 时序数据库 | ⚠️ MySQL TS | ✅ TimescaleDB |
| 分布式 | ⚠️ MySQL Cluster / Vitess | ✅ Citus |
| 模糊匹配 | ⚠️ LIKE | ✅ pg_trgm |
| 时序 | ⚠️ TIMESTAMP 索引 | ✅ BRIN |
| JSON 增强 | ✅ JSON 函数 | ✅ JSONB + 索引 |
| 队列 | ❌ | ✅ pgmq / SKIP LOCKED |

📌 PG 扩展生态完胜
   这是 AI 时代 PG 越来越火的关键

## 9. 运维管理

### 9.1 备份

```
MySQL：
  - mysqldump（逻辑）
  - XtraBackup（物理，Percona）
  - mysqlbinlog（binlog）

PostgreSQL：
  - pg_dump（逻辑）
  - pg_basebackup（物理）
  - pgBackRest（高级工具）
  - WAL 归档（PITR）
```

### 9.2 主从复制

```
MySQL：
  - 异步复制（默认）
  - 半同步复制
  - 组复制（MGR）
  - binlog + canal（CDC）

PostgreSQL：
  - 流复制（同步 / 异步）
  - 逻辑复制（PG 10+）
  - Patroni HA
  - BDR（多主）
```

### 9.3 监控工具

```
MySQL：Prometheus + mysqld_exporter、Percona PMM
PG：Prometheus + postgres_exporter、pgwatch2、pgAdmin
```

## 10. 许可与生态

```
MySQL：
  - GPL（社区版）
  - 商业授权（企业版）
  - Oracle 主导
  - 生态：MySQL Cluster / MariaDB / Percona

PostgreSQL：
  - BSD-like（PostgreSQL License）
  - 完全开源
  - 社区驱动（PG 大会）
  - 生态：PG 衍生（Greenplum / Redshift / Aurora PG）
```

## 11. 迁移成本

```
MySQL → PG：
  - 数据类型映射（有些不一致）
  - SQL 差异（GROUP BY 严格性）
  - 自增主键：AUTO_INCREMENT → SERIAL / GENERATED
  - 字符集：utf8mb4 直接兼容
  - 应用代码：少量调整
  - 工具：pgloader、AWS DMS、阿里云 DTS

PG → MySQL：
  - 大量 PG 特性无对应（JSONB / CTE MATERIALIZED / 数组）
  - 通常需要应用代码改造
  - 复杂查询可能性能下降
```

## 12. 选型决策树

```
新项目，怎么选？
│
├─ 业务简单（CRUD + 报表）
│  ├─ 已有 DBA 熟悉 MySQL → MySQL
│  └─ 团队技术深度 → PG
│
├─ 复杂查询 / 数据分析
│  └─ → PG（优化器 + 窗口函数 + CTE）
│
├─ JSON / 半结构化数据
│  ├─ 不需要复杂索引 → MySQL
│  └─ 需要索引查询 → PG（JSONB + GIN）
│
├─ GIS 应用
│  └─ → PG + PostGIS（行业标准）
│
├─ AI / 向量搜索
│  └─ → PG + pgvector（AI 时代标配）
│
├─ 时序数据
│  └─ → PG + TimescaleDB（一个数据库）
│
└─ 极高并发简单写入
   └─ → MySQL（写性能略好 + 运维简单）
```

## 13. 何时选谁？

```
✅ 选 MySQL：
  - 业务简单（CRUD）
  - 高并发写入（电商 / 社交）
  - 团队熟悉 MySQL
  - 运维简单
  - 已有大量 MySQL 积累

✅ 选 PostgreSQL：
  - 复杂查询 / 分析
  - JSON / 半结构化
  - GIS 应用
  - AI / 向量搜索
  - 时序数据
  - 数据一致性要求高（金融 / 医疗）
  - 想要"可扩展"的数据库

❌ 谁也别选：
  - 业务量极小（SQLite / H2）
  - 业务量极大（专用数据库）
```

## 14. 真实案例

```
- 阿里巴巴：早期 MySQL 为主，现在 ADB PG（分析）+ PolarDB（MySQL 衍生）
- 字节跳动：双用（MySQL OLTP + PG OLAP）
- 腾讯：MySQL + TDSQL（MySQL 衍生）
- 美团：MySQL 为主，CRUD 性能
- GitHub：PostgreSQL（早期）
- Reddit：PostgreSQL（评论）
- Stripe：PostgreSQL（金融）
- Instagram：PostgreSQL（早期）
- Shopify：PostgreSQL（电商）
- Notion：PostgreSQL
```

## 15. 一句话总结

```
📌 MySQL = 易用 + 写性能 + 互联网主流
📌 PostgreSQL = 严谨 + 可扩展 + 复杂场景
📌 SQL 标准：PG 完胜（170+ vs 100+ 标准）
📌 数据类型：PG 完胜（40 vs 30，多 1/3）
📌 索引：PG 完胜（6 种 vs 3 种）
📌 扩展：PG 完胜（PostGIS / pgvector / TimescaleDB）
📌 性能：MySQL 略胜简单写，PG 完胜复杂查询
📌 选型：业务复杂 → PG，业务简单 → MySQL
📌 AI 时代：PG 越来越火（pgvector + JSONB）
📌 现实：99% 公司两者都用，按业务选型
```

## 16. 参考资料

- PostgreSQL vs MySQL 性能基准（2024）
- "High Performance MySQL"（O'Reilly）
- "PostgreSQL 修炼之道"
- Stack Overflow 开发者调查
- DB-Engines Ranking
- Hacker News 历年讨论
- 各公司技术博客（GitHub / Reddit / Stripe）