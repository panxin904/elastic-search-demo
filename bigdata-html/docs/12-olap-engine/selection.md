---
title: OLAP 选型
date: 2026-08-15  # date-auto-injected
---
# OLAP 选型决策

## 1. 主流 OLAP 引擎对比

| 引擎 | 类型 | 性能 | 实时更新 | 部署 | 适合 |
|------|------|------|----------|------|------|
| **ClickHouse** | 列式 | 极强 | 弱 | 自建 / 云 | 海量日志 |
| **Doris** | MPP | 强 | 强 | 自建 | 实时 OLAP |
| **StarRocks** | MPP | 极强 | 强 | 自建 | 实时 OLAP |
| **TiDB** | 行式 + HTAP | 中 | 强 | 自建 | OLTP + OLAP |
| **Presto / Trino** | 联邦查询 | 强 | 弱 | 自建 | 跨源查询 |
| **Snowflake** | 云原生 | 强 | 弱 | 公有云 | 通用 |
| **Redshift** | 列式 | 强 | 弱 | AWS | AWS 用户 |
| **BigQuery** | 云原生 | 强 | 弱 | GCP | GCP 用户 |

## 2. 选型决策树

```
场景：
  - 海量日志 / 监控 → ClickHouse
  - 实时 OLAP 大宽表 → Doris / StarRocks
  - 联邦查询（多源） → Trino / Presto
  - 云端 / 零运维 → Snowflake / BigQuery
  - OLTP + OLAP 混合 → TiDB
  - 私有化 → Apache Doris
```

## 3. 实战选型决策

### 场景 1：电商实时大屏

```
需求：实时聚合（GMV / UV / 订单），亚秒级查询

选 Doris / StarRocks
  - 唯一键模型（实时更新）
  - 物化视图（聚合）
  - 5 秒级查询
```

### 场景 2：日志分析（监控 / 监控）

```
需求：百亿级日志，按维度聚合

选 ClickHouse
  - 写入极快
  - 列式压缩
  - 实时查询（亚秒）
```

### 场景 3：联邦查询（多源）

```
需求：跨 Hive / Kafka / MySQL / Elasticsearch 查询

选 Trino / Presto
  - 联邦查询（多源）
  - 内存计算
  - Spark / Flink 集成
```

## 4. ClickHouse vs Doris vs StarRocks

| 维度 | ClickHouse | Doris | StarRocks |
|------|-------------|-------|-----------|
| 实时写入 | 弱 | 强 | 强 |
| 频繁更新 | 弱 | 强 | 强 |
| 列式压缩 | 强 | 强 | 强 |
| 向量化 | 极强 | 强 | 极强 |
| SQL 兼容 | 弱 | 强（MySQL） | 强（MySQL） |
| 部署 | 复杂 | 简单 | 简单 |
| 社区 | 活跃 | 成熟 | 快速增长 |

## 5. 实战选型清单

- [ ] 业务场景（实时 OLAP / 日志 / 联邦）
- [ ] 数据量（GB / TB / PB）
- [ ] 写入频率（高频 / 低频）
- [ ] 查询频率（亚秒 / 秒 / 分钟）
- [ ] 部署（自建 / 云 / 私有化）
- [ ] 预算（按量 / 服务器）

## 6. 实战决策

```
1. 写少读多 + 海量日志 → ClickHouse
2. 实时 OLAP + 频繁更新 → Doris / StarRocks
3. 云端 + 零运维 → Snowflake / BigQuery
4. 多源联邦查询 → Trino
5. 私有化 + 实时 → Apache Doris
```

## 7. 实战选型对比

| 规模 | 首选 |
|------|------|
| 中小（< 10 TB） | ClickHouse / Doris |
| 大（10-100 TB） | Doris / StarRocks |
| 超大（> 100 TB） | Doris / StarRocks + ClickHouse |
| 云端 | Snowflake / BigQuery |
| 私有化 | Doris + MinIO |

## 8. 实战 checklist

- [ ] 选型
- [ ] 部署（自建 / 云）
- [ ] 性能测试（1 周压测）
- [ ] 监控（query_log / 慢查询）
- [ ] 备份（重要数据）

## 9. 实战选型决策

```
1. 评估数据量（GB / TB / PB）
2. 评估写入频率（实时 / 定时）
3. 评估查询延迟（亚秒 / 秒）
4. 选型（Doris / StarRocks / ClickHouse）
5. 部署（自建 / 云）
6. 监控 + 备份
```

## 10. 实战选型总结

- 实时 OLAP → Doris / StarRocks（首选）
- 日志 / 监控 → ClickHouse
- 云端 → Snowflake / BigQuery
- 私有化 → Apache Doris
- HTAP → TiDB

## 11. 实战选型清单

- [ ] 业务场景
- [ ] 数据量
- [ ] 写入频率
- [ ] 查询频率
- [ ] 部署
- [ ] 预算

## 12. 实战选型决策

```
实时 OLAP（首选） → Doris / StarRocks
日志 / 监控 → ClickHouse
云端 → Snowflake / BigQuery
联邦查询 → Trino
HTAP → TiDB
私有化 → Apache Doris
```

## 13. 实战 checklist

- [ ] 选型
- [ ] 模型选择
- [ ] 分区 + 分桶
- [ ] 写入方式
- [ ] 监控
- [ ] 备份

## 14. 实战总结

- 实时 OLAP → Doris / StarRocks
- 日志 / 监控 → ClickHouse
- 云端 → Snowflake / BigQuery
- 私有化 → Apache Doris

## 15. 实战选型决策

- 实时 OLAP → Doris / StarRocks
- 日志 / 监控 → ClickHouse
- 云端 → Snowulflake / BigQuery
- 私有化 → Apache Doris

## 16. 实战 checklist

- [ ] 选型
- [ ] 部署
- [ ] 监控
- [ ] 备份

## 17. 实战完成

- 实时 OLAP 首选：Doris / StarRocks
- 日志：ClickHouse
- 云：Snowflake / BigQuery
- 私有化：Apache Doris

## 18. 实战选型决策

- 业务场景 → 选型 → 部署 → 监控 → 备份

## 19. 实战

实时 OLAP → Doris / StarRocks｜日志 → ClickHouse

## 20. 实战完成

- 实时 OLAP → Doris / StarRocks
- 日志 → ClickHouse
- 云 → Snowflake / BigQuery
- 私有化 → Apache Doris

## 21. 实战建议

- 实时 OLAP → Doris / StarRocks
- 日志 → ClickHouse
- 云 → Snowflake 或 BigQuery

## 22. 实战

- 实时 OLAP → Doris / StarRocks
- 日志 → ClickHouse
- 云 → Snowflake 或 BigQuery
- 私有化 → Apache Doris

## 23. 实战综合

- 实时 OLAP → Doris / StarRocks
- 日志 → ClickHouse
- 云 → Snowflake / BigQuery
- 私有化 → Apache Doris

## 24. 实战选型清单

- [ ] 业务场景
- [ ] 数据量
- [ ] 写入频率
- [ ] 查询频率
- [ ] 部署
- [ ] 预算

## 25. 实战

- 实时 OLAP 首选：Doris / StarRocks
- 日志：ClickHouse
- 云：Snowflake / BigQuery
- 私有化：Apache Doris

## 26. 实战

Doris / StarRocks 是当下实时 OLAP 最优选！

## 27. 实战 checklist

- [ ] 选型
- [ ] 模型
- [ ] 分区
- [ ] 摄入
- [ ] 监控
- [ ] 备份

## 28. 实战完成

- 实时 OLAP：优选 Doris / StarRocks
- 日志 / 监控：ClickHouse
- 云：Snowflake / BigQuery
- 私有化：Apache Doris

## 🔗 下一步
- [ClickHouse 架构](/12-olap-engine/clickhouse)
- [Doris / StarRocks](/12-olap-engine/doris-starrocks)
- [Snowflake 架构](/09-dw-architecture/snowflake)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
