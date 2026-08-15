---
title: ProxySQL 中间件
---

# 🚦 MySQL ProxySQL 中间件

> ProxySQL 是高性能的 MySQL 代理，提供查询路由、读写分离、连接池、查询缓存等功能，是 MySQL 架构中常用的中间件。

## 🎯 ProxySQL 是什么？

ProxySQL 是一个 **高性能的 MySQL 代理**，位于应用和 MySQL 之间：

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│   App    │ ────→ │   ProxySQL    │ ────→ │  MySQL   │
│          │       │  (代理层)     │       │  Servers │
└──────────┘       └──────────────┘       └──────────┘
                     ↓
              ┌──────────────┐
              │  智能路由     │
              │  连接池       │
              │  查询缓存     │
              │  限流熔断     │
              └──────────────┘
```

## 🏆 ProxySQL 的核心特性

### 1. 读写分离

```sql
-- 自动将 SELECT 路由到从库
-- 自动将 INSERT/UPDATE/DELETE 路由到主库
```

### 2. 连接池

```
应用端连接 → ProxySQL（复用连接）→ MySQL
- 应用端维持 100 个连接
- ProxySQL 维持 50 个到 MySQL 的连接
- 节省 MySQL 连接资源
```

### 3. 查询缓存

```sql
-- ProxySQL 缓存 SELECT 结果
-- 相同查询直接返回缓存（不查 MySQL）
-- 大幅降低 MySQL 压力
```

### 4. 限流熔断

```sql
-- 慢查询自动路由到其他从库
-- 故障节点自动摘除
-- 查询超时自动重试
```

## ⚙️ ProxySQL 安装

```bash
# Ubuntu/Debian
wget https://repo.proxysql.com/ProxySQL/repo_pub_key
apt-key add repo_pub_key
echo "deb https://repo.proxysql.com/ProxySQL/proxysql-2.7.x/$(lsb_release -sc)/ ./" \
  | tee /etc/apt/sources.list.d/proxysql.list
apt-get update
apt-get install proxysql mysql-client

# 启动
systemctl start proxysql
```

## 🔧 ProxySQL 配置

### 1. 添加 MySQL 服务器

```sql
-- 登录 ProxySQL 管理界面（默认端口 6032）
mysql -u admin -padmin -h 127.0.0.1 -P 6032

-- 添加主库（hostgroup 0 = 写）
INSERT INTO mysql_servers (hostgroup_id, hostname, port, weight, max_connections)
VALUES (0, '192.168.1.10', 3306, 100, 1000);

-- 添加从库（hostgroup 1 = 读）
INSERT INTO mysql_servers (hostgroup_id, hostname, port, weight, max_connections)
VALUES
  (1, '192.168.1.11', 3306, 100, 1000),
  (1, '192.168.1.12', 3306, 100, 1000);

-- 应用配置
LOAD MYSQL SERVERS TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
```

### 2. 配置读写分离规则

```sql
-- 写操作路由到 hostgroup 0（主库）
INSERT INTO mysql_query_rules (rule_id, active, match_digest, destination_hostgroup)
VALUES
  (1, 1, '^SELECT.*FOR UPDATE$', 0),
  (2, 1, '^SELECT.*LOCK IN SHARE MODE$', 0),
  (3, 1, '^SELECT', 1);  -- 其他 SELECT → 从库

-- 应用配置
LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL QUERY RULES TO DISK;
```

### 3. 配置复制用户

```sql
-- ProxySQL 监控主从复制延迟的用户
INSERT INTO mysql_users (username, password, default_hostgroup)
VALUES ('proxysql_monitor', 'monitor_pwd', 0);

-- 应用用户
INSERT INTO mysql_users (username, password, default_hostgroup, max_connections)
VALUES ('app_user', 'app_pwd', 1, 200);

-- 应用配置
LOAD MYSQL USERS TO RUNTIME;
SAVE MYSQL USERS TO DISK;
```

## 📊 ProxySQL 监控

### 查看统计信息

```sql
-- 查看查询统计
SELECT
  digest_text,
  count_star AS exec_count,
  sum_time AS total_ms,
  hostgroup
FROM stats_mysql_query_digest
ORDER BY sum_time DESC
LIMIT 20;

-- 查看连接池状态
SELECT
  srv_host,
  srv_port,
  status,
  Connections_used,
  Connections_free
FROM stats_mysql_connection_pool;

-- 查看慢查询
SELECT
  digest_text,
  count_star,
  sum_time / 1000 AS total_seconds
FROM stats_mysql_query_digest
WHERE sum_time > 1000000  -- 超过 1 秒
ORDER BY sum_time DESC;
```

## 🛠️ 高级配置

### 1. 查询路由（基于规则）

```sql
-- 复杂查询路由到专用从库
INSERT INTO mysql_query_rules
  (rule_id, active, match_digest, destination_hostgroup, comment)
VALUES
  -- 大表查询路由到 SSD 从库
  (10, 1, 'SELECT.*FROM huge_table', 2, '大表查询到 SSD 从库'),

  -- 报表查询路由到专用从库
  (11, 1, '^SELECT.*FROM reports', 3, '报表查询到专用从库'),

  -- 应用层查询带 hint
  (12, 1, '/* FOR_MASTER \*/.*', 0, '强制走主库');
```

### 2. 限流

```sql
-- 限制某个用户的查询频率
UPDATE mysql_users
SET max_connections = 100
WHERE username = 'app_user';

-- 配置查询超时
SET mysql-default_query_timeout = 30000;  -- 30 秒
```

### 3. 熔断

```sql
-- 慢查询自动路由
INSERT INTO mysql_query_rules
  (rule_id, active, match_digest, destination_hostgroup, apply)
VALUES
  (20, 1, 'SELECT.*FROM slow_table', 1, 0);

-- 标记节点为 SHUNNED（暂时不路由）
UPDATE mysql_servers
SET status = 'SHUNNED'
WHERE hostname = 'slow_slave';
```

## 📈 性能提升数据

```
优化前（应用直连 MySQL）：
- 应用连接数：500
- MySQL 连接数：500
- 平均响应：15ms
- QPS 上限：~3000

使用 ProxySQL 后：
- 应用连接数：500
- MySQL 连接数：50（连接池复用）
- 平均响应：8ms
- QPS 上限：~15000

提升：5x 性能，10x QPS
```

## 🎯 总结

**ProxySQL 核心：**
- ✅ 读写分离（自动路由）
- ✅ 连接池（节省 MySQL 资源）
- ✅ 查询缓存（提升性能）
- ✅ 限流熔断（保护 MySQL）

**适用场景：**
- 大量应用连接
- 需要读写分离
- 需要查询缓存
- 生产环境 MySQL 代理

**配置要点：**
- hostgroup 0 = 主（写）
- hostgroup 1+ = 从（读）
- 规则匹配顺序很重要

**下一步：** [📦 mysqldump 逻辑备份](../08-backup/mysqldump) — 备份恢复系列