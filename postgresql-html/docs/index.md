---
layout: home
title: PostgreSQL 知识图谱
date: 2026-08-27  # date-auto-injected
hero:
  name: PostgreSQL 知识图谱
  text: 现代关系型数据库的纵深
  tagline: JSONB · PostGIS · pgvector · MVCC · CTE · 11 大类 60+ 节点
  actions:
    - theme: brand
      text: 📖 基础入门
      link: /01-basics/overview
    - theme: alt
      text: 🧩 JSONB
      link: /02-data-types/jsonb
    - theme: alt
      text: 🤖 pgvector
      link: /10-extensions/pgvector
features:
  - icon: 📖
    title: 基础入门
    details: 安装 / 进程架构 / postgresql.conf / psql / pgAdmin
    link: /01-basics/overview
    linkText: 看基础 →
  - icon: 🔢
    title: 数据类型
    details: JSONB · array · range · 自定义类型 · domain
    link: /02-data-types/jsonb
    linkText: 看类型 →
  - icon: 📊
    title: 表与索引
    details: B-Tree · Hash · GIN · GiST · BRIN · SP-GiST
    link: /03-tables-and-indexes/table
    linkText: 看索引 →
  - icon: 🔍
    title: 查询优化
    details: EXPLAIN · CTE · 窗口函数 · 全文检索
    link: /04-query/explain
    linkText: 看查询 →
  - icon: 🔄
    title: 事务与并发
    details: MVCC · 隔离级别 · 锁机制 · 死锁排查
    link: /05-transaction/mvcc
    linkText: 看事务 →
  - icon: ⚙️
    title: 高级特性
    details: 视图 / 触发器 / 存储过程 / UPSERT / 生成列
    link: /06-advanced/view
    linkText: 看高级 →
  - icon: 🛠️
    title: 运维管理
    details: vacuum · 备份 · 升级 · pg_stat 视图
    link: /07-operations/vacuum
    linkText: 看运维 →
  - icon: 📡
    title: 复制与高可用
    details: 流复制 · 逻辑复制 · 热备 · Patroni
    link: /08-replication/streaming
    linkText: 看复制 →
  - icon: 🔌
    title: 客户端连接
    details: PgBouncer · libpq · psycopg · JDBC
    link: /09-connection/pgbouncer
    linkText: 看连接 →
  - icon: 🧩
    title: 扩展生态
    details: PostGIS · pgvector · TimescaleDB · Citus
    link: /10-extensions/postgis
    linkText: 看扩展 →
  - icon: ⚖️
    title: 横向对比
    details: MySQL vs PostgreSQL 全方位对比
    link: /11-compare/mysql-vs-postgresql
    linkText: 看对比 →
  - icon: 🏛️
    title: AI 时代的关键
    details: pgvector + PG = AI 时代关系型数据库的事实标准
    link: /10-extensions/pgvector
    linkText: 看 pgvector →
---


<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "MVCC 原理：为什么 PG 的读不阻塞写？",
      "事务隔离级别（RC / RR / Serializable）选哪个？",
      "索引类型（B-tree / Hash / GIN / BRIN / GiST）怎么选？",
      "主从复制延迟、逻辑复制、FDW 怎么用？",
      "慢查询、锁等待、checkpoint 怎么监控？"
    ]
const goals = [
      "SQL 基础（DDL / DML / 查询 / 聚合 / CTE / Window）",
      "事务与并发控制（MVCC / 隔离级别 / 锁）",
      "索引体系（B-tree / Hash / GIN / BRIN / GiST）",
      "复制与高可用（流复制 / 逻辑复制 / Patroni / PgBouncer）",
      "性能调优（EXPLAIN / pg_stat_statements / 参数调优）",
      "扩展生态（PostGIS / pgvector / TimescaleDB）"
    ]
const relatedSites = [
      { site: "mysql", path: "/11-compare/mysql-vs-postgresql", label: "MySQL vs PostgreSQL" },
      { site: "clickhouse", path: "/06-compare/clickhouse", label: "PG → ClickHouse HTAP" },
      { site: "redis", path: "/09-connection/cache-pattern", label: "PG + Redis 缓存层" },
      { site: "observability", path: "/07-operations/monitor", label: "PG 慢查询监控" },
      { site: "architecture", path: "/04-transaction/overview", label: "分布式事务" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>

## 学习路径建议

| 阶段 | 时长 | 路径 |
|------|------|------|
| 入门 | 1-2 周 | 01-basics → 02-data-types → 03-tables-and-indexes |
| 进阶 | 2-3 周 | 04-query → 05-transaction → 06-advanced |
| 高级 | 2-3 周 | 07-operations → 08-replication → 09-connection |
| 实战 | 持续 | 10-extensions（PostGIS/pgvector/TimescaleDB）→ 11-compare |

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [mysql](https://java-px.bot.cd/mysql/)：MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/)：ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/)：数据库选型
- [architecture](https://java-px.bot.cd/architecture/)：数据一致性
- [linux](https://java-px.bot.cd/linux/)：Linux 服务端调优


## 💬 评论与反馈

有问题或建议？欢迎在下方评论。

<ClientOnly>
  <GiscusComment />
</ClientOnly>
