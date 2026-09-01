---
title: 学习路径
date: 2026-08-15  # date-auto-injected
---

# 📖 MySQL 学习路径

> 不知道从哪里开始？按照这个路径，**4 阶段从入门到精通**，每阶段 1-2 周时间。

## 🛤️ 阶段一：入门基础（1-2 周）

### 🎯 目标
理解 MySQL 是什么，能写出基本的 CRUD SQL。

### 📚 学习内容

1. **[🏛️ 体系结构](01-foundation/architecture.md)** — MySQL 是怎么运行的（连接器 / 查询缓存 / 分析器 / 优化器 / 执行器）
2. **[🔧 存储引擎](01-foundation/storage-engine.md)** — InnoDB 是默认引擎，了解 MyISAM / MEMORY 的区别
3. **[📊 数据类型](01-foundation/data-types.md)** — 整数 / 浮点 / 字符串 / 时间 / JSON 怎么选
4. **[🌐 字符集](01-foundation/charset.md)** — utf8mb4 是为什么（不是 utf8）
5. **[📝 CRUD 与 DDL](03-sql/crud.md)** — SELECT / INSERT / UPDATE / DELETE / CREATE TABLE

### ✅ 检验标准

- 能独立设计一张用户表的 schema
- 能熟练写出 CRUD SQL
- 理解主键 / 外键 / 索引的基本概念

### 🛠️ 实践

- [SQL Playground](cheatsheet) — 在线练习 SQL

---

## ⚡ 阶段二：性能核心（2-3 周）

### 🎯 目标
能通过索引优化慢查询，理解事务的 ACID 特性。

### 📚 学习内容

1. **[🌳 B+Tree 原理](02-index/btree.md)** — 为什么索引这么快（树高度 = 磁盘 IO 次数）
2. **[📑 聚簇索引](02-index/clustered.md)** — InnoDB 的特殊设计：数据即索引
3. **[✅ 覆盖索引与最左前缀](02-index/covering.md)** — 索引优化的两大利器
4. **[🔗 JOIN 七种用法](03-sql/join.md)** — 图解 INNER / LEFT / RIGHT / FULL JOIN
5. **[🪟 窗口函数](03-sql/window-functions.md)** — ROW_NUMBER / RANK / LAG / LEAD
6. **[⚖️ ACID 与隔离级别](04-transaction/isolation.md)** — 4 种隔离级别的影响
7. **[🔐 InnoDB 锁机制](04-transaction/locks.md)** — 共享锁 / 排他锁 / 意向锁
8. **[🔒 锁演示](#)** — 4 种并发场景的交互式动画（[本页下方](#)）

### ✅ 检验标准

- 给一条慢 SQL，能分析是否用到索引
- 能解释脏读 / 不可重复读 / 幻读的区别
- 能设计合适的复合索引（字段顺序）

### 🛠️ 实践

- [🛢️ SQL Playground](cheatsheet) — 写 SQL + EXPLAIN
- [🔒 锁演示](#) — 互动学习并发场景

---

## 🚀 阶段三：性能调优（2-3 周）

### 🎯 目标
能系统性地定位和解决生产环境的性能问题。

### 📚 学习内容

1. **[📊 EXPLAIN 解读](05-optimization/explain.md)** — 12 个字段含义（type / key / rows / Extra）
2. **[🐌 慢查询定位](05-optimization/slow-query.md)** — slow_query_log 配置 + pt-query-digest 分析
3. **[🎯 索引优化实战](05-optimization/index-tuning.md)** — 索引选型的艺术（覆盖索引 / 前缀索引 / 函数索引）
4. **[✍️ SQL 改写 12 招](05-optimization/sql-rewrite.md)** — 常见慢 SQL 改造（避免 SELECT * / OR 改 UNION / IN 优化等）
5. **[🔄 MVCC 多版本并发](04-transaction/mvcc.md)** — 读不阻塞写的实现原理

### ✅ 检验标准

- 能用 EXPLAIN 分析任意 SQL 并给出优化建议
- 能配置和解读慢查询日志
- 能识别常见的反模式 SQL 并改写

### 🛠️ 实践

- [🧮 性能计算器](#) — 估算 B+Tree 高度、Buffer Pool 大小、QPS 容量

---

## 🏗️ 阶段四：生产运维（2-4 周）

### 🎯 目标
能搭建生产级 MySQL 集群，处理故障，保障 SLA。

### 📚 学习内容

1. **[📜 binlog 与 relay log](06-replication/binlog.md)** — 主从复制的基石
2. **[🔄 主从同步原理](06-replication/replication.md)** — 从库是怎么追上主库的
3. **[⏱️ 主从延迟排查](06-replication/lag.md)** — 延迟过大怎么办
4. **[📖 读写分离实战](06-replication/read-write-split.md)** — 扩展读的标准方案
5. **[🏗️ MHA 故障切换](07-ha/mha.md)** — 30 秒自动切换
6. **[🌐 MGR 组复制](07-ha/mgr.md)** — MySQL 官方高可用方案
7. **[🚦 ProxySQL 中间件](07-ha/proxysql.md)** — 读写分离 + 负载均衡
8. **[📦 mysqldump 逻辑备份](08-backup/mysqldump.md)** — 小数据量备份
9. **[⚡ xtrabackup 热备](08-backup/xtrabackup.md)** — TB 级热备方案
10. **[🔙 binlog 时间点恢复](08-backup/binlog-recovery.md)** — 误删数据救命稻草
11. **[🐢 慢查询日志](09-monitoring/slow-log.md)** — 性能瓶颈的第一道防线
12. **[🔬 performance_schema](09-monitoring/performance-schema.md)** — MySQL 内部观测台

### ✅ 检验标准

- 能搭建 1 主 2 从 + MHA 的高可用集群
- 能用 xtrabackup 做 TB 级热备并恢复
- 能用 Prometheus + Grafana 监控 MySQL

---

## 🌟 阶段五：架构进阶（持续）

### 🎯 目标
能设计支撑千万级 QPS 的数据库架构。

### 📚 学习内容

1. **[📐 垂直拆分 vs 水平拆分](10-sharding/strategy.md)** — 何时该拆
2. **[🌊 ShardingSphere 实战](10-sharding/shardingsphere.md)** — 国产优秀中间件
3. **[🐱 MyCat 中间件](10-sharding/mycat.md)** — 老牌分库分表
4. **[🔑 一致性 Hash 与分片键](10-sharding/sharding-key.md)** — 拆分的关键决策
5. **大厂案例** — 阿里 / 字节 / 美团 的 MySQL 实践

### ✅ 检验标准

- 能设计千万级用户的分库分表方案
- 能选型合适的分片键和拆分策略
- 能处理分布式事务和数据迁移

---

## 📊 学习进度自测

| 阶段 | 预计耗时 | 关键里程碑 |
|---|---|---|
| 一、入门基础 | 1-2 周 | 能独立设计 schema + CRUD |
| 二、性能核心 | 2-3 周 | 能分析索引使用 + 解释隔离级别 |
| 三、性能调优 | 2-3 周 | 能定位 + 优化生产慢查询 |
| 四、生产运维 | 2-4 周 | 能搭建高可用集群 + 备份恢复 |
| 五、架构进阶 | 持续 | 能设计分库分表方案 |

## 🎓 推荐资源

- 📚 官方文档：[dev.mysql.com/doc](https://dev.mysql.com/doc/)
- 📖 经典书籍：《高性能 MySQL》《MySQL 是怎么运行的》《MySQL 实战 45 讲》
- 🎬 视频课程：B 站搜「MySQL 实战 45 讲」「尚硅谷 MySQL」
- 🛠️ 工具：Percona Toolkit / MySQL Workbench / DBeaver / Navicat


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
