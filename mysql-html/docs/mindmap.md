---
title: 思维导图
---

# 🧭 MySQL 思维导图

> 按 **11 大主题** 分类的结构化导图，支持展开/收起，点击叶子节点跳转对应文档。

<MindMap :height="720" />

## 📚 主题地图

### 🏛️ 基础层（必须先学）

- [体系结构](01-foundation/architecture) - MySQL 是怎么运行的
- [存储引擎](01-foundation/storage-engine) - InnoDB vs MyISAM vs MEMORY
- [数据类型](01-foundation/data-types) - 整数 / 字符串 / 时间 / JSON
- [字符集与排序规则](01-foundation/charset) - utf8mb4 与 collation

### 🌲 索引（性能核心）

- [B+Tree 原理](02-index/btree) - 为什么索引这么快
- [聚簇索引 vs 二级索引](02-index/clustered) - InnoDB 的特殊设计
- [覆盖索引与最左前缀](02-index/covering) - 索引优化的两大利器
- [索引下推 ICP](02-index/icp) - 减少回表次数

### 📝 SQL 实战

- [CRUD 与 DDL](03-sql/crud) - 日常 80% 的 SQL
- [JOIN 七种用法](03-sql/join) - 图解各种 JOIN
- [窗口函数](03-sql/window-functions) - MySQL 8.0 强大功能
- [常用函数与 CTE](03-sql/functions) - 函数速查 + CTE 递归

### 🔒 事务与锁（并发控制）

- [ACID 与隔离级别](04-transaction/isolation) - 4 种隔离级别的影响
- [InnoDB 锁机制](04-transaction/locks) - 共享锁 / 排他锁 / 意向锁
- [死锁分析与排查](04-transaction/deadlock) - 死锁日志怎么读
- [MVCC 多版本并发](04-transaction/mvcc) - 不加锁的读是怎么实现的

### 🚀 性能优化

- [EXPLAIN 解读](05-optimization/explain) - 12 个字段含义
- [慢查询定位](05-optimization/slow-query) - 找到系统的瓶颈
- [索引优化实战](05-optimization/index-tuning) - 索引选型的艺术
- [SQL 改写 12 招](05-optimization/sql-rewrite) - 常见慢 SQL 改造

### 🔁 主从复制

- [binlog 与 relay log](06-replication/binlog) - 复制的基石
- [主从同步原理](06-replication/replication) - 从库是怎么追上主库的
- [主从延迟排查](06-replication/lag) - 延迟过大怎么办
- [读写分离实战](06-replication/read-write-split) - 扩展读的标准方案

### 🛡️ 高可用

- [MHA 故障切换](07-ha/mha) - 30 秒自动切换
- [MGR 组复制](07-ha/mgr) - MySQL 官方高可用方案
- [ProxySQL 中间件](07-ha/proxysql) - 读写分离 + 负载均衡

### 💾 备份恢复

- [mysqldump 逻辑备份](08-backup/mysqldump) - 小数据量备份
- [xtrabackup 热备](08-backup/xtrabackup) - TB 级热备方案
- [binlog 时间点恢复](08-backup/binlog-recovery) - 误删数据救命稻草

### 📈 监控诊断

- [慢查询日志](09-monitoring/slow-log) - 性能瓶颈的第一道防线
- [performance_schema](09-monitoring/performance-schema) - MySQL 内部观测台
- [Prometheus + mysqld_exporter](09-monitoring/prometheus) - 生产级监控

### 🧩 分库分表

- [垂直拆分 vs 水平拆分](10-sharding/strategy) - 何时该拆
- [ShardingSphere 实战](10-sharding/shardingsphere) - 国产优秀中间件
- [MyCat 中间件](10-sharding/mycat) - 老牌分库分表
- [一致性 Hash 与分片键](10-sharding/sharding-key) - 拆分的关键决策

### 🛠️ 工具速查

- [mysql client 命令](11-tools/mysql-client) - 最常用运维命令
- [pt-toolkit 工具集](11-tools/pt-toolkit) - Percona 神器
- [SQL 速查表](11-tools/cheatsheet) - 30+ SQL 模板