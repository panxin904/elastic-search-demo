---
layout: home
title: PostgreSQL 知识图谱
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

## 关联站点

PostgreSQL 在企业架构中常与 OLTP、OLAP、缓存、可观测性深度协同：

- **mysql/** → MySQL vs PostgreSQL 全方位对比（事务 / 复制 / 扩展性 / 生态）→ 链到 `11-compare/mysql-vs-postgresql`
- **clickhouse/** → HTAP 架构：PG 处理 OLTP、ClickHouse 处理 OLAP，Binlog/CDC 同步 → 链到 `06-compare/clickhouse`
- **redis/** → PG + Redis 缓存层：缓存击穿 / 雪崩 / 一致性保障 → 链到 `09-connection/cache-pattern`
- **observability/** → PG 慢查询 / 锁等待 / checkpoint 监控 / pg_stat_statements → 链到 `07-operations/monitoring`
- **architecture/** → 分布式数据库架构：读写分离 / 分库分表 / 分布式事务 → 链到 `04-transaction/overview`

## 学习路径建议

| 阶段 | 时长 | 路径 |
|------|------|------|
| 入门 | 1-2 周 | 01-basics → 02-data-types → 03-tables-and-indexes |
| 进阶 | 2-3 周 | 04-query → 05-transaction → 06-advanced |
| 高级 | 2-3 周 | 07-operations → 08-replication → 09-connection |
| 实战 | 持续 | 10-extensions（PostGIS/pgvector/TimescaleDB）→ 11-compare |