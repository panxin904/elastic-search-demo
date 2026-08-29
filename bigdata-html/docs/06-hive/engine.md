---
title: Hive on Spark / Tez
date: 2026-08-15  # date-auto-injected
---
# Hive 执行引擎

## 1. 三种执行引擎

| 引擎 | 推出 | 模型 | 速度 | 适用 |
|------|------|------|------|------|
| **MapReduce** | 2007 | 磁盘迭代 | 慢 | 极老（基本不用） |
| **Tez** | 2014 | DAG | 较快 | Hive 主流 |
| **Spark** | 2014 | 内存迭代 | 快 | Hive 3.x 默认推荐 |
| **LLAP** | 2016 | 常驻进程 + 缓存 | 最快 | 实时查询 |

## 2. Tez

Tez = DAG 执行引擎（Hive / Pig 通用）。

```
SQL → Tez DAG
        ↓
  Vertices（Hive Map / Reduce 任务）
        ↓
  Edges（shuffle / broadcast）
        ↓
  Container（YARN）
```

**优势**：
- DAG 优化（合并相邻 task）
- Container 重用（-1 不释放）
- 启动快（不需要 JVM 启动）

## 3. Spark

Hive on Spark = Hive 走 Spark 执行（Spark SQL）。

```sql
SET hive.execution.engine=spark;
```

**优势**：
- 内存计算（迭代快）
- 与 Spark 生态整合（DataFrame / MLlib）
- Catalyst 优化（谓词下推 + 列裁剪）

## 4. LLAP

LLAP（Live Long And Process）= 常驻 daemon + 内存缓存。

```
HS2
  ↓
LLAP daemon × N（常驻）
  - 内存缓存（列裁剪 / 谓词下推）
  - 共享内存
  - 快速查询（亚秒级）
```

**优势**：
- 启动快（避免每次 query 起 JVM）
- 内存缓存（多次查询提速）
- 实时查询友好

## 5. 选型建议

```
默认：Spark（Hive 3.x 推荐）
  - 性能好
  - 生态成熟
  - 与 Spark 整合

实时查询：LLAP
  - 亚秒级响应
  - 内存缓存

历史原因：Tez
  - 稳定
  - 兼容好
```

## 6. 实战配置

```sql
-- 引擎选择
SET hive.execution.engine=spark;
-- 或 tez
-- 或 llap

-- 内存（Spark / Tez 容器）
SET hive.tez.container.size=8192;  -- 8 GB
SET hive.tez.java.opts=-Xmx6g -XX:+UseG1GC;
```

## 7. Spark vs Tez vs LLAP 性能

| 操作 | MR | Tez | Spark | LLAP |
|------|------|-----|-------|------|
| 全表扫描 | 10 min | 1 min | 30 s | 10 s |
| 聚合查询 | 5 min | 30 s | 10 s | 5 s |
| Join | 10 min | 1 min | 30 s | 15 s |
| 重复查询 | 同 | 同 | 同 | 缓存加速（10 倍） |

## 8. 实战案例：Hive 切换 Spark

```sql
-- 老 Hive on MR：30 分钟
SET hive.execution.engine=mr;
SELECT ...;  -- 30 min

-- 切到 Spark：3 分钟
SET hive.execution.engine=spark;
SELECT ...;  -- 3 min

-- 进一步优化
SET hive.vectorized.execution.enabled=true;  -- 向量化
SET hive.tez.container.size=8192;  -- 大内存
ANALYZE TABLE ... COMPUTE STATISTICS;  -- 收集统计
```

## 9. 实战 checklist

- [ ] 引擎选择（Spark 推荐）
- [ ] 内存调优（4-8 GB）
- [ ] 启用 CBO
- [ ] 启用向量化
- [ ] 收集统计（ANALYZE）
- [ ] 监控（HS2 / Tez / Spark 指标）

## 🔗 下一步
- [Hive 架构](/06-hive/architecture)
- [Hive 优化](/06-hive/optimize)
- [数据建模 OLAP vs OLTP](/08-modeling/olap-oltp)
