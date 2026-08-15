---
title: PgBouncer 连接池
description: 轻量级 PostgreSQL 连接池实战
---

# PgBouncer 连接池

> **TL;DR**：PgBouncer 是 PG 生态最流行的**轻量级连接池**。PostgreSQL 每连接占用 5-10 MB，每秒创建连接的 fork 开销巨大。**1000 并发的应用 + 100 个真实 DB 连接 = PgBouncer**。

## 一句话定义

```
PgBouncer = PG 前端的连接代理，池化客户端连接，复用后端连接
```

## 为什么需要连接池

### PostgreSQL 连接的代价

```
1 个连接 = 5-10 MB 内存（PG 进程 + 私有上下文）
1000 并发 = 5-10 GB 内存
连接 fork 开销 ≈ 1-3 ms（每秒 1000 fork = 100% CPU）
```

### 连接池的效果

```
应用 1000 并发 → PgBouncer 池化 100 个真实连接 → PG 后端
              ↑                                  ↑
         内存节省 90%                      后端压力 1/10
```

## 三种池化模式

| 模式 | 行为 | 适用场景 |
|---|---|---|
| **Session** | 客户端断开才释放连接 | 简单，但复用率低 |
| **Transaction** | 事务结束释放连接 | **90% 场景**，最常用 |
| **Statement** | 每个 SQL 后释放 | 极端场景（不建议） |

```ini
# pgbouncer.ini
pool_mode = transaction   # ← 推荐
```

### Transaction 模式注意事项

```
⚠️ Transaction 模式下，跨事务的功能不可用：
- PREPARE / DEALLOCATE（prepared statements）
- SET（会话级参数）
- LISTEN / NOTIFY
- 临时表
- 锁的会话级保持
```

## 安装与配置

### 安装

```bash
# Debian/Ubuntu
apt install pgbouncer

# CentOS
yum install pgbouncer
```

### 关键配置

```ini
# /etc/pgbouncer/pgbouncer.ini

[databases]
# 数据库连接配置
mydb = host=127.0.0.1 port=5432 dbname=mydb
mydb_ro = host=127.0.0.1 port=5432 dbname=mydb pool_size=20  # 只读副本

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432

# 认证
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

# 池化模式
pool_mode = transaction

# 连接数（关键）
default_pool_size = 20       # 每 (user, db) 对的最大连接数
max_client_conn = 1000       # 客户端最大连接
min_pool_size = 5            # 最小保持连接
reserve_pool_size = 5        # 突发连接
reserve_pool_timeout = 3     # 3s 后释放突发连接

# 超时
server_idle_timeout = 600
client_idle_timeout = 0      # 0 = 客户端永不超时
query_timeout = 0            # 0 = 不限
client_login_timeout = 60

# 日志
log_connections = on
log_disconnections = on
log_pooler_errors = on
stats_period = 60
```

### 用户文件

```bash
# /etc/pgbouncer/userlist.txt
# 格式："user" "password"
"appuser" "md5abc123def456..."
"readonly" "md5..."

# 或者用 scram-sha-256
"appuser" "SCRAM-SHA-256$4096:..."
```

> **生产建议**：appuser 用 SCRAM-SHA-256（PG 14+ 默认）。

## 应用侧配置

### Java (JDBC)

```yaml
# application.yml
spring:
  datasource:
    # 直连 PG
    # url: jdbc:postgresql://127.0.0.1:5432/mydb
    # 经 PgBouncer
    url: jdbc:postgresql://127.0.0.1:6432/mydb
    hikari:
      maximum-pool-size: 50          # 应用层池，叠加在 PgBouncer 上
      minimum-idle: 10
      connection-timeout: 30000
```

### 注意事项

```java
// ⚠️ PgBouncer transaction 模式下，prepared statements 默认关闭
// HikariCP 默认会缓存 prepared statements
// 解决方案 1: 禁用 prepared statements
dataSource.setPreparedStatementCacheQueries(0);
dataSource.setPreparedStatementCacheSize(0);

// 解决方案 2: 用 PgBouncer prepared statements（PG 14+ + PgBouncer 1.21+）
// 在 JDBC URL 加 &prepareThreshold=0&preparedStatementCacheQueries=0
```

## 监控与运维

### pgBouncer 控制台

```bash
# 连接 PgBouncer 管理接口
psql -h 127.0.0.1 -p 6432 -U pgbouncer pgbouncer

# 查看池状态
SHOW POOLS;

# 返回：
# database | user | cl_active | cl_waiting | sv_active | sv_idle | pool_mode
# mydb     | app  | 50        | 0          | 18        | 2       | transaction

# 关键指标：
# - cl_waiting: 客户端等待数（> 0 表示池不够大）
# - sv_active: 后端活跃连接
# - sv_idle: 后端空闲连接
```

### 关键监控指标

```sql
-- 1. 客户端等待（> 0 持续 = 池不够）
SHOW STATS;

-- 2. 总查询数
SHOW TOTALS;

-- 3. 实时活动
SHOW ACTIVITY;
```

### Prometheus 监控

```yaml
# pgbouncer_exporter 启动
pgbouncer_exporter --pgbouncer.connection-string="postgres://stats:stats@127.0.0.1:6432/pgbouncer"

# 暴露指标：
# pgbouncer_pools_client_active
# pgbouncer_pools_client_waiting
# pgbouncer_pools_server_active
# pgbouncer_pools_server_idle
```

### Grafana 告警规则

```promql
# 客户端等待连接超过 10 个持续 5 分钟
pgbouncer_pools_client_waiting > 10

# 后端连接数用满
pgbouncer_pools_server_active / pgbouncer_pools_max_client_conn > 0.9
```

## 高可用部署

### 模式 1：PgBouncer + 单 PG

```
App → PgBouncer (单点) → PG
```

**问题**：PgBouncer 单点故障。

### 模式 2：PgBouncer + Patroni

```
App → PgBouncer (HAProxy VIP 漂移) → Patroni 管理 PG 集群
        ↑
   keepalived 接管 VIP
```

```ini
# pgbouncer.ini - 经 HAProxy
mydb = host=patroni-vip port=5001 dbname=mydb
```

### 模式 3：PgBouncer Sidecar

```
Pod (PgBouncer sidecar) → PG
   ↑                      ↑
  App Container          K8s Service
```

```yaml
# k8s deployment
spec:
  containers:
  - name: app
    env:
    - name: DB_HOST
      value: "localhost"
    - name: DB_PORT
      value: "6432"
  - name: pgbouncer
    image: bitnami/pgbouncer
    config:
      databases: |
        mydb = host=pg-primary port=5432 dbname=mydb
```

## 常见错误

### 错误 1：prepared statements 失败

```
ERROR: prepared statement "S_1" does not exist
```

**原因**：Transaction 模式下，prepared statement 跨事务失效。

**修复**：
```java
// JDBC 关闭 prepared statement cache
dataSource.setPreparedStatementCacheQueries(0);
```

### 错误 2：临时表跨事务丢失

```sql
BEGIN;
CREATE TEMP TABLE tmp_data (...);
-- 事务结束后表消失（transaction 模式）
```

**修复**：用普通表 + truncate，或换 session 模式。

### 错误 3：连接数设置过大

```
default_pool_size = 200 + db 数 × user 数 = 实际后端连接
可能超过 PG max_connections
```

**修复**：
```sql
-- PG 端：max_connections = 200
-- PgBouncer：default_pool_size × db × user ≤ 200
-- 1 db × 5 users × 20 = 100 ✓
```

### 错误 4：密码错误

```
ERROR: password authentication failed for user "app"
```

**修复**：
```bash
# 1. PG 端确认用户存在
psql -c "SELECT usename FROM pg_user WHERE usename='app';"

# 2. PgBouncer 用户文件里密码格式
#   md5 格式："user" "md5" + md5(password + user)
#   SCRAM:    "user" "SCRAM-SHA-256$..."
```

## 一句话总结

> **PgBouncer 是 PG 接入层标配**：1000 并发应用 + 100 后端连接 = 10x 资源节约 + 10x 性能提升。**Transaction 模式 + 默认池大小 20 + 配合应用层池（HikariCP）= 最佳实践**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>