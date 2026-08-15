---
title: ClickHouse 总览
---

# ClickHouse 总览

**ClickHouse = Yandex 开源的高性能列式 OLAP 数据库**——亿级数据秒级聚合，被 Uber / Cloudflare / GitHub 用来做实时数仓。

## 一句话总结

> **ClickHouse = 列式存储 + MergeTree 引擎 + 向量化执行 + 分布式 MPP**。**OLAP 场景的事实标准（2020 年后）**。

---

## 一、为什么需要 ClickHouse

传统 OLTP 数据库（MySQL / PG）在以下场景捉襟见肘：

| 场景 | MySQL/PG 痛点 | ClickHouse 解法 |
|---|---|---|
| 亿级日志聚合 | 几小时 | 几秒 |
| 用户行为分析 | 多表 JOIN 慢 | 列存 + 索引 |
| 指标存储（TSDB） | 不擅长 | 稀疏索引 + 高压缩 |
| 实时数仓 | 需数仓 + ETL | 直接消费 Kafka |

**OLAP 场景** = 读多写少 + 大宽表 + 聚合查询 + 时间序列。

## 二、ClickHouse 的核心特点

### 1. 列式存储

**OLTP 行存 vs OLAP 列存**：

```
行存（MySQL）:
┌────┬──────┬─────┐
│ id │ name │ age │
├────┼──────┼─────┤
│ 1  │ A    │ 20  │  ← 一行连续
│ 2  │ B    │ 21  │
└────┴──────┴─────┘
查询 `SELECT age, AVG(age)` → 读所有 name（浪费）

列存（ClickHouse）:
┌────┬────┐
│ id │    │
├────┤    │
│ 1  │    │
│ 2  │    │
└────┘    │
┌───────┐ │
│ name  │ │  ← 一列连续
├───────┤ │
│ A     │ │
│ B     │ │
└───────┘ │
┌─────┐  │  ← 只读 age 列
│ age │  │
├─────┤  │
│ 20  │  │
│ 21  │  │
└─────┘──┘
查询 `SELECT age, AVG(age)` → 只读 age 列（10-100x 快）
```

### 2. MergeTree 引擎族

**核心引擎**：
- **MergeTree**：基础引擎，主键索引 + 分区 + 排序键
- **ReplacingMergeTree**：去重，保留最新版本
- **AggregatingMergeTree**：预聚合
- **CollapsingMergeTree**：折叠相反状态
- **VersionedCollapsingMergeTree**：版本化折叠
- **SummingMergeTree**：同主键求和

### 3. 向量化执行

**SIMD 指令**（SSE / AVX）一次处理 1024 个数据，而非传统一次一个。

### 4. 数据分区 + 主键索引

- **PARTITION BY**：按时间分目录，删除时秒级
- **ORDER BY**：稀疏索引（每 8192 行一个）
- **PRIMARY KEY**：默认与 ORDER BY 相同，可不同

### 5. 高压缩比

| 数据 | MySQL | ClickHouse |
|---|---|---|
| 日志（1 亿行） | 50GB | 5GB（10x 压缩）|
| 用户行为 | 30GB | 3GB（10x）|

**压缩算法**：LZ4（默认）+ ZSTD（高压缩率）。

## 三、ClickHouse vs 传统数仓

| 维度 | Hadoop/Hive | ClickHouse |
|---|---|---|
| 延迟 | 分钟-小时 | 秒-毫秒 |
| 数据量 | PB 级 | TB-PB |
| 部署 | 需 HDFS/YARN | 单机/集群均可 |
| SQL 兼容 | HQL（类 SQL） | 标准 SQL + 扩展 |
| 成本 | 高（10+ 节点） | 中（3-5 节点起）|
| 实时性 | 批处理 | 实时 |

**ClickHouse 优势**：
- 实时：无需预聚合，物化视图自动维护
- 简单：单二进制，5 分钟启动
- 兼容 SQL：MySQL/PG 工程师无学习成本
- 压缩高：节省 5-10x 存储

## 四、ClickHouse 适用场景

✅ **适合**：
- 实时数仓（替代 Hive / Druid）
- 指标存储（Prometheus remote_write 目标）
- 日志分析（替代 ELK 聚合部分）
- 用户行为分析（埋点 + 漏斗 + 留存）
- 业务 OLAP（订单分析、GMV、用户画像）
- 时序数据（IoT / 服务器监控）

❌ **不适合**：
- OLTP（事务、写多读少）
- 全文搜索（用 ES）
- 简单 KV 缓存（用 Redis）
- 强事务 + 关系建模（用 MySQL/PG）
- 单行 UPDATE/DELETE（不支持高频）

## 五、ClickHouse 性能基准

**官方 benchmark**（1 亿行单表）：

| 查询 | 响应时间 |
|---|---|
| `SELECT count()` | 0.001s |
| `SELECT uniq(user_id)` | 0.2s |
| `SELECT sum(amount) WHERE date=...` | 0.05s |
| `SELECT top 10 user ORDER BY sum DESC` | 0.3s |
| `SELECT ... GROUP BY date, country` | 0.5s |

**单服务器 100MB/s 吞吐**，集群线性扩展。

## 六、ClickHouse 生态

```
┌──────────┐     ┌────────────┐     ┌──────────────┐
│  Kafka   │────▶│ ClickHouse │────▶│  Grafana     │
└──────────┘     │            │     └──────────────┘
                 │            │
┌──────────┐     │            │     ┌──────────────┐
│  Logs    │────▶│  Cluster   │────▶│ Prometheus   │
└──────────┘     │            │     └──────────────┘
                 │            │
┌──────────┐     │            │     ┌──────────────┐
│ MySQL/PG │────▶│            │────▶│  BI / Tabix  │
└──────────┘     └────────────┘     └──────────────┘
```

## 七、ClickHouse 历史

- **2008**：Yandex 开发，用于 Metrica（全球第二大网站分析平台）
- **2016**：开源（Apache 2.0）
- **2017**：商业化 ClickHouse Inc.（俄裔创始人）
- **2018-2020**：Uber / Cloudflare 公开案例，GitHub 切换
- **2021**：ClickHouse Cloud 上线（云原生托管）
- **2024-2025**：24.x LTS / Keeper 独立 / 物化视图增强

## 八、与其他站的关系

| 站 | 关系 |
|---|---|
| **mysql** | OLTP 业务库 → CDC 同步 → ClickHouse 做分析 |
| **postgresql** | OLTP 多模 → 同上 |
| **bigdata** | Spark/Hive 离线 → ClickHouse 实时 |
| **es** | ES 全文检索 + ClickHouse 数值聚合 |
| **kafka** | ClickHouse Kafka engine 直接消费 |
| **observability** | Prometheus remote_write 存 ClickHouse |
| **cloud-native** | ClickHouse Operator 部署在 K8s |
| **go** | ch-go 客户端 / go-clickhouse 生态 |
| **system-design** | 列存 / 向量化 / MPP 架构理论 |

## 关联章节

- **01-basics/history**：历史与版本
- **01-basics/installation**：安装部署
- **01-basics/data-types**：数据类型
- **06-compare/overview**：对比选型

## 一句话总结

> **ClickHouse = Yandex 开源的高性能列式 OLAP**。**亿级数据秒级聚合，是现代数据栈的实时数仓首选**。
