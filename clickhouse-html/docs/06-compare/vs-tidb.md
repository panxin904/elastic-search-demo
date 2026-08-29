---
title: vs TiDB
date: 2026-08-15  # date-auto-injected
description: ClickHouse vs TiDB HTAP：OLAP 专精 vs OLTP + OLAP 一体化
---

# ClickHouse vs TiDB

[TiDB](https://tidb.io/) 是 PingCAP 开源的分布式 HTAP 数据库，TiKV（行存）+ TiFlash（列存副本）实现一份数据两种引擎。本章对比 ClickHouse 和 TiDB 的 OLAP 能力。

## 核心差异

| 维度 | ClickHouse | TiDB |
|---|---|---|
| **定位** | 纯 OLAP | HTAP（OLTP + OLAP） |
| **架构** | Shared-nothing + 本地存储 | TiKV（行存）+ TiFlash（列存副本） |
| **OLTP** | ❌ 不支持 | ✅ 强（MySQL 兼容） |
| **OLAP** | 极强（专用引擎） | 中（TiFlash 列副本） |
| **事务** | 无 | 完整分布式事务（Percolator） |
| **写入延迟** | 异步（无强一致） | 同步（P99 < 50ms） |
| **生态** | BI / Kafka / 各种 ETL | MySQL 协议完全兼容 |
| **运维** | 中（Keeper 集群） | 中（TiKV + TiFlash） |
| **典型用户** | 上述 | B 站（早期）/ 小米 / 平安 |

## OLAP 性能对比（10 亿行）

```sql
-- 测试查询：单表聚合
SELECT
  order_date,
  count() AS order_count,
  sum(amount) AS gmv,
  uniq(user_id) AS buyers
FROM orders
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY order_date

-- ClickHouse: 200ms
-- TiDB（TiFlash）: 2-5s（列副本未优化好）
```

**结论**：**OLAP 性能** ClickHouse 比 TiDB（TiFlash）快 5-10x。

## OLTP 能力对比

```sql
-- OLTP 事务
BEGIN;
UPDATE users SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET total = total - 100 WHERE user_id = 1;
COMMIT;

-- ClickHouse: ❌ 不支持事务
-- TiDB: ✅ 完整 ACID
```

**结论**：**OLTP 能力** TiDB 完胜（ClickHouse 根本没 OLTP）。

## HTAP 适用性

```text
TiDB HTAP 架构：
┌──────────┐    ┌──────────┐    ┌──────────┐
│ TiKV     │    │ TiFlash  │    │ TiSpark  │
│ (行存)   │    │ (列副本) │    │ (Spark)  │
│ OLTP     │    │ OLAP     │    │ 复杂分析 │
└──────────┘    └──────────┘    └──────────┘
     ▲                ▲                ▲
     └────────────────┼────────────────┘
                      │
              Raft 同步 + 异步复制
```

**优势**：
- 一套系统搞定 OLTP + OLAP
- 数据强一致（TiKV 主写入，TiFlash 异步复制）

**劣势**：
- TiFlash OLAP 性能不如 ClickHouse
- 资源隔离差（OLTP 负载影响 OLAP）

## 选型决策

### 选 TiDB

✅ **需要 HTAP**（OLTP + OLAP 一套系统）
✅ **MySQL 协议兼容**（迁移成本低）
✅ **数据量 < 10 亿行**（TiFlash 列副本规模上限）
✅ **团队倾向 MySQL 生态**

### 选 ClickHouse

✅ **纯 OLAP**（不需要 OLTP 拖累）
✅ **数据量 > 10 亿行**（ClickHouse 横向扩展更成熟）
✅ **极致 OLAP 性能**（CK 比 TiFlash 快 5-10x）
✅ **团队有能力运维 Keeper 集群**

## 典型混合架构

```text
MySQL/PG → CDC → Kafka → ClickHouse（专用 OLAP）
                            │
                            └── 复杂报表 / 实时看板
```

如果不想维护两套系统，TiDB HTAP 是合理选择。

## 实战对比

### 场景 1：电商（HTAP 需求）

```text
订单创建：    OLTP（强事务）→ TiDB
订单分析：    OLAP（聚合查询）→ ClickHouse（更快）

混合架构：
  应用 → TiDB（事务）
       → CDC → Kafka → ClickHouse（分析）
```

### 场景 2：金融（HTAP 强需求）

```text
账户余额：    OLTP（强事务）→ TiDB
账户分析：    OLAP（聚合查询）→ TiDB TiFlash（一致性优先）

纯 TiDB HTAP。
```

### 场景 3：日志分析（CK 主场）

```text
日志采集：    Kafka → ClickHouse
日志分析：    ClickHouse

无需 TiDB（无 OLTP 需求）。
```

## 大厂案例

### TiDB 案例

- **B 站**（早期）：HTAP 实践
- **小米**：用户中心 + 业务分析
- **平安**：金融业务 HTAP

### ClickHouse 案例

- **字节跳动**：抖音埋点（CK 专用 OLAP）
- **京东**：订单分析（CK 专用 OLAP）
- **Uber**：日志分析（CK 专用 OLAP）

## TiDB vs Doris / StarRocks 对比

| 维度 | TiDB | Doris / StarRocks |
|---|---|---|
| **OLTP** | 极强 | 弱（不建议） |
| **OLAP** | 中 | 强（CBO 优化） |
| **HTAP** | 强 | 弱 |
| **生态** | MySQL 协议 | 自有生态 |
| **典型场景** | 强 HTAP 需求 | 纯 OLAP 复杂 JOIN |

## 工具对比

| 维度 | TiDB | ClickHouse |
|---|---|---|
| **客户端** | MySQL 客户端 | DBeaver / DataGrip / ch-go |
| **BI** | Metabase / Superset | Grafana / Superset |
| **CDC** | TiCDC | Debezium / MaterializedPostgreSQL |
| **云服务** | TiDB Cloud | ClickHouse Cloud |

## 实际案例：选择思考

### 案例 A：互联网业务（中小规模）

```text
Q: 数据量 1 亿行 + OLTP + OLAP 都要
A: TiDB（HTAP，省运维）
```

### 案例 B：互联网业务（大规模）

```text
Q: 数据量 10 亿+ + 强 OLAP
A: MySQL + ClickHouse（专机专用）
```

### 案例 C：传统企业（金融）

```text
Q: 强事务 + 数据一致性 + OLAP
A: TiDB HTAP（一致性优先）
```

### 案例 D：日志平台

```text
Q: 日志 PB 级 + 聚合查询
A: ClickHouse（专用 OLAP）
```

## 结论

- **HTAP 需求 + 数据量适中** → TiDB
- **大规模 OLAP** → ClickHouse
- **两者结合** → MySQL/PG + ClickHouse 混合架构

## 大厂混合实践

- **小米**：TiDB + ClickHouse（OLTP + OLAP 分工）
- **美团**：MySQL + ClickHouse
- **字节**：MySQL + ClickHouse

详见 [../case-study.md](../case-study.md)。

## 下一步

- 学习 OLAP 实战：见 [04-olap-scenarios/overview.md](../04-olap-scenarios/overview.md)
- 学习生态集成：见 [05-ecosystem/overview.md](../05-ecosystem/overview.md)
