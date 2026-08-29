---
title: 对比选型总览
description: ClickHouse vs MySQL vs PostgreSQL vs Doris vs StarRocks vs TiDB 选型决策树
---

# 对比选型总览

> OLAP 选型没有银弹。本章给出一张可执行的决策图，把 ClickHouse 放到 MySQL/PG/Doris/StarRocks/TiDB 的坐标里，让你在 5 分钟内判断「这个项目该不该用 ClickHouse」。

## 1. 六大数据库定位矩阵

```text
                写吞吐       单查询性能    SQL 完整度    JOIN 能力    生态成熟度
                (rows/s)     (列扫亿级)    (CTE/窗口)    (大表 JOIN)   (运维/BI)
MySQL/PG         ★★★          ★            ★★★★★        ★★★★         ★★★★★
Doris            ★★★★         ★★★★         ★★★★         ★★★★★       ★★★
StarRocks        ★★★★         ★★★★★       ★★★★         ★★★★★       ★★★
TiDB             ★★★          ★★★          ★★★★★        ★★★★★       ★★★★
ClickHouse       ★★★★★        ★★★★★       ★★★          ★★           ★★★★
```

关键观察：
- **ClickHouse**：写吞吐和单查询性能双冠，但 JOIN 弱（≤ 8 张表的本地 JOIN，过大易 OOM），SQL 完整度中（无完整事务、UPDATE/DELETE 弱）。
- **MySQL/PG**：万金油，OLTP 首选，做 OLAP 只能算勉强（PG 强一些，有 pg_analytics、duckdb_fdw；MySQL 适合跑简单聚合，复杂分析直接卡死）。
- **Doris / StarRocks**：MPP 架构，JOIN 强于 ClickHouse（向量化 + CBO + 数据 shuffle 优化），适合大宽表 JOIN（事实表 + 多维表星型/雪花模型）。StarRocks 在多表关联场景普遍比 ClickHouse 快 2-5x。
- **TiDB**：HTAP 卖点，OLTP+OLAP 一套系统，但 OLAP 性能比前三者弱一档（行存 + TiFlash 列存混合架构），适合中小规模实时分析。

## 2. 选型决策树（直接 copy 决策）

```text
                        你的场景是？
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
    OLTP 为主           OLAP 为主           OLTP + OLAP 一套
    （行级事务）         （列扫聚合）           （HTAP）
        │                   │                   │
   MySQL / PG         Q1: 单表列扫?         TiDB / PolarDB
   (按团队熟悉度)      Q2: 大宽表 JOIN?      (中小规模)
                      Q3: 高吞吐写入?
                            │
                  ┌─────────┼─────────┐
                  ▼         ▼         ▼
                Q1=Yes    Q2=Yes    Q3=Yes
                Q2=No     Q1=Yes    Q2=No
                Q3=Yes    Q3=Yes    (≥10万 rows/s)
                  │         │         │
                  ▼         ▼         ▼
              ClickHouse  StarRocks  ClickHouse
              (默认 OLAP)  / Doris   (Kafka 引擎)
```

**三条黄金法则**：

1. **数据量 ≥ 1 亿行 + 查询模式以聚合/扫描为主** → ClickHouse 是默认选择（GitHub、Cloudflare、Uber、字节、京东、B 站都在用）。
2. **多张大表 JOIN（星型/雪花模型）+ 实时更新** → StarRocks / Doris 更合适（ClickHouse JOIN 超过 4 张表会显著退化）。
3. **强事务 + 偶尔分析** → MySQL/PG 或 TiDB，不要为了「顺便分析」把 OLAP 系统扛在 OLTP 上。

## 3. ClickHouse vs MySQL / PostgreSQL

| 维度 | ClickHouse | MySQL / PostgreSQL |
|---|---|---|
| **数据模型** | 列式（按列压缩、按列向量化） | 行式（按行存储） |
| **写吞吐** | 100w rows/s 单分片 | MySQL 1-5w/s；PG 5-10w/s |
| **单查询** | 亿级聚合 < 1s | 亿级聚合 > 30s 或 OOM |
| **JOIN** | 弱（≤ 8 表，否则 SHUFFLE 退化） | 强（优化器成熟） |
| **事务** | 无（K/V 写入无原子性保证） | 完整 ACID |
| **UPDATE/DELETE** | 弱（ALTER TABLE ... DELETE/MUTATION 异步） | 强 |
| **索引** | 主键稀疏索引 + Skip 索引 | B+Tree / GIN / BRIN |
| **生态** | Grafana / dbt / Airbyte / Kafka | 任何 BI / ORM |
| **运维** | Zookeeper（老版）/ ClickHouse Keeper（新版） | 主从 / MGR / Patroni |

**适用边界**：

- 同步链路：**MySQL/PG → ClickHouse** 是常规做法（CDC + MaterializedPostgreSQL/CDC 或 canal/debezium + Kafka 引擎）。
- 反向链路（CK → MySQL）：少见，只在「ClickHouse 计算后回写 MySQL 提供 OLTP 读取」时用。
- 共同存在：CK 做实时大宽表分析，MySQL/PG 做事务，两者用 Kafka/CDC 同步。

## 4. ClickHouse vs Doris

[Doris](https://doris.apache.org/)（原 Palo）是百度开源的 MPP 分析库，2020 年进 Apache。ClickHouse 和 Doris 都是「单查询极快」的 OLAP 引擎，但实现路径不同。

| 维度 | ClickHouse | Doris |
|---|---|---|
| **架构** | Shared-nothing + 本地存储 | Frontend + Backend，BE 存数据 |
| **存储** | MergeTree（LSM 风格） | 列存 + Segment + 索引 |
| **JOIN** | 弱（Hash Join 仅本地） | 强（Runtime Filter + shuffle 优化） |
| **数据更新** | ReplacingMergeTree / VersionedCollapsingMergeTree | 默认支持 UPSERT（Unique Key 表） |
| **实时写入** | Kafka 引擎 + 物化视图 | Stream Load / Routine Load（Kafka 消费内置） |
| **运维** | 复杂（多分片 + 副本 + Zookeeper） | 简单（FE + BE，Zookeeper 可选） |
| **生态** | ClickHouse Cloud / Altinity / ch-go | SelectDB / Apache Doris 社区 |
| **典型用户** | Uber、Cloudflare、字节 | 百度、美团、小米、京东 |

**如何选**：

- **ClickHouse 赢面**：极简单表扫描 + 极高高吞吐写入（埋点/日志）+ 二次开发定制（ch-go 客户端 + 自定义函数）。
- **Doris 赢面**：大宽表 JOIN 复杂查询 + 实时 UPDATE 需求 + 运维团队不想维护 Zookeeper。
- **结论**：除非你明确需要 Doris 的 JOIN 能力或 UPDATE 友好，否则 ClickHouse 是更主流的选择（Yandex 血统 + 大厂案例更多）。

## 5. ClickHouse vs StarRocks

[StarRocks](https://www.starrocks.io/)（原 DorisDB）从 Doris 0.13 fork 出来后专注 CBO 优化器和向量化执行。在多表 JOIN 和高并发点查（高 QPS 小查询）场景，StarRocks 通常比 ClickHouse 快 2-5x。

| 维度 | ClickHouse | StarRocks |
|---|---|---|
| **CBO 优化器** | 弱（无统计信息收集） | 强（基于 HyperLogLog/Cardinality 统计 + CBO） |
| **向量化** | 完整（SSE/AVX） | 完整 |
| **JOIN 优化** | Hash Join 简单实现 | Runtime Filter + Adaptive Multi-Agg Join |
| **高并发** | 中（每查询单线程/少线程） | 强（每 BE 数百并发查询） |
| **数据湖** | Iceberg/Hudi/Delta 通过外部引擎 | 原生 Iceberg/Hudi/Hive Catalog |
| **实时数仓** | Kafka 引擎 + 物化视图 | Routine Load + 主键模型 |
| **运维** | 中（Keeper 集群） | 简单（FE 高可用 + BE 弹性） |
| **典型用户** | Cloudflare、Uber、字节、京东 | 滴滴、网易、米哈游、小红书 |

**如何选**：

- **ClickHouse 赢面**：写入吞吐 > 100w rows/s 的场景（日志/埋点），CK 的批量写入仍是行业标杆。
- **StarRocks 赢面**：高并发（> 100 QPS）+ 复杂 JOIN + 数据湖联邦查询。
- **结论**：StarRocks 在 2024-2026 年的增长更快（新版本 3.x 引入了存算分离 + 数据湖），CK 在写入吞吐和历史沉淀占优。

## 6. ClickHouse vs TiDB

[TiDB](https://tidb.io/) 是 PingCAP 开源的 HTAP 分布式数据库。TiKV（行存）+ TiFlash（列存副本）实现一份数据两种引擎。

| 维度 | ClickHouse | TiDB |
|---|---|---|
| **定位** | 纯 OLAP | HTAP（OLTP + OLAP） |
| **OLTP 性能** | 不支持 | 与 MySQL 持平或略优 |
| **OLAP 性能** | 极强 | 中（TiFlash 列副本，比 CK 慢 5-10x） |
| **事务** | 无 | 完整分布式事务（Percolator） |
| **写入延迟** | 异步（无强一致） | 同步（P99 < 50ms） |
| **生态** | BI / Kafka / 各种 ETL | MySQL 协议完全兼容 |
| **典型用户** | 上述 | B 站（早期）、小米、平安 |

**如何选**：

- **ClickHouse 赢面**：只做 OLAP，不要 OLTP 拖累。
- **TiDB 赢面**：中小规模（< 10 亿行）实时 HTAP，不想维护两套系统。
- **结论**：如果你的主库已经是 MySQL/PG 且分析负载不大，TiDB 是不错的轻量化选择；如果分析负载明确 > 100 QPS 或 > 1 亿行，老老实实用 ClickHouse + CDC。

## 7. 与传统数仓对比（Snowflake / BigQuery / Redshift）

```text
                自建 ClickHouse 集群     云数仓 (Snowflake/BQ/RS)
成本              中（机器 + 运维人力）    高（按扫描字节计费）
性能              极快（本地存储）          极快（云端弹算）
扩展性            中（手动加节点）          极强（秒级扩缩容）
运维              团队自己搞              云厂商搞定
数据量 ≤ 1TB      不划算                 划算
数据量 1-100TB     划算                   看折扣
数据量 ≥ 100TB     划算（私有部署）         贵（按扫描付费）
数据合规          本地化                  跨境风险
```

**结论**：

- **小团队 / 早期项目**：直接用 Snowflake / BigQuery，省运维。
- **中大规模 / 数据本地化**：ClickHouse 自建集群，案例成熟（Cloudflare 日处理 50PB）。
- **混合方案**：云数仓做临时查询 + ClickHouse 做实时看板（参考 Uber 早期架构）。

## 8. 选型 checklist（决策前自检）

用这张表对照你的项目：

| 问题 | Yes → 选 CK | No → 别选 CK |
|---|---|---|
| 数据量 ≥ 1 亿行？ | ✅ | ❌（用 PG/MySQL 足够） |
| 查询以聚合/扫描为主？ | ✅ | ❌（用 StarRocks） |
| 写吞吐 ≥ 10w rows/s？ | ✅ | ❌（用 MySQL/PG 即可） |
| 不需要强事务？ | ✅ | ❌（用 MySQL/PG/TiDB） |
| 团队能运维 Zookeeper/多副本？ | ✅ | ❌（用 Doris/StarRocks） |
| 主要场景是日志/埋点/指标？ | ✅ | ❌（看具体场景） |

**满足 4/6 个 Yes** → ClickHouse 是合理选择。
**满足 5-6 个 Yes** → ClickHouse 是强烈推荐。

## 9. 大厂案例（一句话定位）

- **Uber**：用 ClickHouse 替代 Elasticsearch 做日志分析，成本降 10x，查询快 10x。
- **Cloudflare**：处理 DNS / CDN 日志，单集群 50+ PB，自研 ch-go 客户端。
- **GitHub**：events / audit log 分析，替换 Elasticsearch。
- **字节**：抖音埋点、广告指标全链路用 CK。
- **京东**：订单履约实时监控 + 商品分析，PB 级。
- **B 站**：用户行为分析 + 弹幕反垃圾。
- **美团**：外卖订单实时监控 + 商户经营分析。
- **网易**：游戏埋点 + 反作弊。
- **滴滴**：行程数据实时分析（与 StarRocks 共存）。

## 10. 后续章节导航

- **实战经验**：见 [04-olap-scenarios](../04-olap-scenarios/overview.md) 的 6 大场景（埋点/日志/指标/数仓/去重/业务 OLAP）。
- **生态工具**：见 [05-ecosystem](../05-ecosystem/overview.md) 的 Kafka/Grafana/Prometheus/dbt/Airbyte 集成。
- **大厂案例**：见 [case-study](../case-study.md) 12 个真实生产案例的深度剖析。

> 一句话总结：**默认选 ClickHouse，除非你的场景命中 Doris/StarRocks/TiDB 的赢面。**

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [es](https://java-px.bot.cd/es/):ES 对比
- [bigdata](https://java-px.bot.cd/bigdata/):大数据生态
- [postgresql](https://java-px.bot.cd/postgresql/):PostgreSQL 对比
