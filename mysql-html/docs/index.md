---
layout: home
title: MySQL 知识图谱
hero:
  name: MySQL
  text: 系统化学习
  tagline: 用知识图谱串联 MySQL 概念与使用方式
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 📊 思维导图
      link: /mindmap
features:
  - icon: 🏛️
    title: 基础层
    details: 体系结构 / InnoDB / 数据类型 / 字符集 — 理解 MySQL 的底层基石
    link: /01-foundation/architecture
    linkText: 查看基础层
  - icon: 🌲
    title: 索引
    details: B+Tree / 聚簇索引 / 覆盖索引 / 最左前缀 — 性能优化的核心
    link: /02-index/btree
    linkText: 深入索引原理
  - icon: 📝
    title: SQL 实战
    details: CRUD / JOIN / 窗口函数 / CTE — 写出高效可读的 SQL
    link: /03-sql/crud
    linkText: 实战 SQL
  - icon: 🔒
    title: 事务与锁
    details: ACID / 隔离级别 / InnoDB 锁 / 死锁 / MVCC — 并发控制的基石
    link: /04-transaction/isolation
    linkText: 掌握事务锁
  - icon: 🚀
    title: 性能优化
    details: EXPLAIN / 慢查询 / 索引优化 / SQL 改写 — 系统化的性能调优方法
    link: /05-optimization/explain
    linkText: 性能调优实战
  - icon: 🔁
    title: 主从复制
    details: binlog / 主从同步 / 读写分离 — 扩展读能力的标准方案
    link: /06-replication/binlog
    linkText: 掌握主从复制
  - icon: 🛡️
    title: 高可用
    details: MHA / MGR / ProxySQL — 保障数据库持续可用的方案
    link: /07-ha/mha
    linkText: HA 方案
  - icon: 💾
    title: 备份恢复
    details: mysqldump / xtrabackup / binlog 恢复 — 数据安全的最后防线
    link: /08-backup/mysqldump
    linkText: 备份恢复方案
  - icon: 📈
    title: 监控诊断
    details: 慢查询日志 / performance_schema / Prometheus — 主动发现问题
    link: /09-monitoring/slow-log
    linkText: 监控实战
  - icon: 🧩
    title: 分库分表
    details: 拆分策略 / ShardingSphere / MyCat / 一致性 Hash — 突破单机瓶颈
    link: /10-sharding/strategy
    linkText: 分库分表方案
---

<ClientOnly>
  <WhyThisGraph
    :pain-points="[
      "知识点碎片化，不知道先后顺序（11 大主题怎么学？）",
      "InnoDB 引擎原理（MVCC / Buffer Pool / Redo Log）讲不清？",
      "索引（B+Tree / Hash / 全文）怎么建才高效？",
      "SQL 优化（EXPLAIN / 慢查询 / 索引失效）？",
      "主从复制 / 读写分离 / 分库分表 / 分布式事务怎么落地？"
    ]"
    :goals="[
      "体系结构 + 存储引擎 + 数据类型 + 字符集",
      "索引 + SQL + 事务锁（日常开发 90% 场景）",
      "性能优化 + 复制 + 高可用 + 备份 + 监控",
      "分库分表 + 工具速查",
      "SQL Playground + 思维导图 + 知识图谱"
    ]"
    :related-sites="[
      { site: "postgresql", path: "/01-basics/intro", label: "PostgreSQL 对比" },
      { site: "clickhouse", path: "/01-storage/index-design", label: "ClickHouse 索引" },
      { site: "redis", path: "/01-basics/intro", label: "Redis 缓存" },
      { site: "architecture", path: "/09-cases/sharding", label: "分库分表实战" },
      { site: "observability", path: "/07-operations/monitor", label: "MySQL 监控" }
    ]"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>


<span class="kg-badge kg-badge-foundation">MySQL</span>

# MySQL 知识图谱

> **11 个核心主题** + **50 个关键概念节点** + **知识图谱** + **思维导图** + **SQL Playground**
> 系统化学习 MySQL 的知识体系

## 🎯 为什么需要知识图谱？

| 层次 | 主题 | 学习目标 |
|---|---|---|
| **基础** | 体系结构 / 存储引擎 / 数据类型 / 字符集 | 理解 MySQL 底层原理 |
| **核心** | 索引 / SQL / 事务锁 | 掌握日常开发 90% 场景 |
| **进阶** | 性能优化 / 复制 / 高可用 / 备份 / 监控 | 生产环境调优与运维 |
| **扩展** | 分库分表 / 工具速查 | 应对大数据量与日常速查 |

## 🚀 快速开始

- 📖 **[学习路径](path)** — 不知道从哪开始？看这里！
- 🌐 **[知识图谱](graph)** — 50 个概念的全局关系图
- 🧭 **[思维导图](mindmap)** — 按主题分类的结构化展示
- 🛢️ **[SQL Playground](11-tools/cheatsheet)** — 在线写 SQL + EXPLAIN 解读
- 📋 **[SQL 速查表](11-tools/cheatsheet)** — 30+ 常用 SQL 模板，一键复制

## 🎓 学习建议

1. **入门 (1-2 周)**：基础层 + 索引 + SQL 实战 + SQL Playground
2. **进阶 (2-4 周)**：事务锁 + 性能优化 + 慢查询排查
3. **高级 (1-2 月)**：复制 + 高可用 + 备份恢复 + 监控
4. **架构 (持续)**：分库分表 + ShardingSphere + 大厂案例

## 🛠️ 交互组件

| 组件 | 说明 |
|---|---|
| 🌐 知识图谱 | 50 个概念节点 + 80 条关系边的力导向图 |
| 🧭 思维导图 | 11 大主题的树状展示，可展开/收起 |
| 🛢️ SQL Playground | 在线写 SQL，模拟执行 + EXPLAIN 解读 |
| 🔒 锁演示 | 4 种并发场景的交互式动画演示 |
| 📋 SQL 速查表 | 30+ 模板，可搜索 + 一键复制 |
| 🧮 性能计算器 | B+Tree 高度 / Buffer Pool / QPS 容量估算 |
| ☕ **MyBatis/MyBatis-Plus** | 10 页从入门到高级实战的 ORM 教程 |