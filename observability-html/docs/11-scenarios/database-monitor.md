---
title: 数据库可观测性
description: MySQL / PostgreSQL / Redis 监控实践
---

# 数据库可观测性

> **TL;DR**：**数据库监控 = 连接池 + 慢查询 + 复制延迟 + 锁等待 + 缓存命中率**。**MySQL：mysqld_exporter + performance_schema**。**PostgreSQL：postgres_exporter + pg_stat_statements**。**Redis：redis_exporter + INFO 命令**。**SRE 三件套：Exporter + 慢查询日志 + EXPLAIN 分析**。

## 一句话定义

```
数据库可观测性 = 4 个维度
             = 1. 资源（CPU/内存/磁盘/连接池）
             = 2. 查询（QPS / 慢查询 / 锁）
             = 3. 复制（主从延迟 / binlog）
             = 4. 缓存（命中率 / 淘汰率）
```

## MySQL 监控

```yaml
# Prometheus mysqld_exporter
scrape_configs:
  - job_name: mysql
    static_configs:
      - targets: [mysql-exporter:9104]
    metrics_path: /metrics
```

```promql
# 1. 连接池使用率
mysql_global_status_threads_connected / mysql_global_variables_max_connections

# 2. QPS / TPS
rate(mysql_global_status_questions[5m])     # QPS
rate(mysql_global_status_com_insert[5m])    # INSERT/s
rate(mysql_global_status_com_update[5m])    # UPDATE/s

# 3. 慢查询
rate(mysql_global_status_slow_queries[5m])

# 4. InnoDB 缓冲池命中率
1 - rate(mysql_global_status_innodb_buffer_pool_reads[5m])
  / rate(mysql_global_status_innodb_buffer_pool_read_requests[5m])

# 5. 主从延迟
mysql_slave_status_seconds_behind_master

# 6. 表锁等待
mysql_global_status_table_locks_waited
```

```sql
-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 1 秒
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- 查询最慢的 SQL（performance_schema）
SELECT * FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC LIMIT 10;
```

## PostgreSQL 监控

```yaml
# Prometheus postgres_exporter
scrape_configs:
  - job_name: postgres
    static_configs:
      - targets: [postgres-exporter:9187]
```

```promql
# 1. 连接池使用率
pg_stat_activity_count / pg_settings_max_connections

# 2. QPS
rate(pg_stat_database_tup_fetched[5m])    # 读
rate(pg_stat_database_tup_inserted[5m])   # 写

# 3. 慢查询（pg_stat_statements）
# 需要先 CREATE EXTENSION pg_stat_statements
# 然后用 postgres_exporter 暴露

# 4. 锁等待
pg_locks_count{mode="waiting"}

# 5. 复制延迟
pg_replication_lag_seconds

# 6. 缓存命中率
pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)
```

```sql
-- 启用 pg_stat_statements
-- postgresql.conf
shared_preload_libraries = 'pg_stat_statements'

-- CREATE EXTENSION
CREATE EXTENSION pg_stat_statements;

-- 查询最慢的 SQL
SELECT round((100 * total_time / sum(total_time) over ())::numeric, 2) AS percent,
       calls, round(total_time::numeric, 2) AS total_ms,
       round(mean_time::numeric, 2) AS mean_ms,
       substring(query, 1, 80)
FROM pg_stat_statements
ORDER BY total_time DESC LIMIT 10;
```

## Redis 监控

```yaml
# Prometheus redis_exporter
scrape_configs:
  - job_name: redis
    static_configs:
      - targets: [redis-exporter:9121]
```

```promql
# 1. QPS
rate(redis_commands_processed_total[5m])

# 2. 命中率
1 - rate(redis_keyspace_misses_total[5m])
  / rate(redis_keyspace_hits_total[5m])

# 3. 连接数
redis_connected_clients

# 4. 内存使用
redis_memory_used_bytes / redis_memory_max_bytes

# 5. 淘汰率（重要：频繁淘汰 = 容量不足）
rate(redis_evicted_keys_total[5m])

# 6. 主从延迟（master_repl_offset vs slave offset）
# redis_exporter 自动暴露
```

## 数据库告警

```yaml
# Prometheus rules
groups:
  - name: db-alerts
    rules:
      # MySQL 连接池即将耗尽
      - alert: MySQLConnectionsHigh
        expr: |
          mysql_global_status_threads_connected
          / mysql_global_variables_max_connections > 0.8
        for: 5m
        labels: {severity: warning}

      # PostgreSQL 复制延迟
      - alert: PostgresReplicationLag
        expr: pg_replication_lag_seconds > 30
        for: 2m
        labels: {severity: critical}

      # Redis 命中率低
      - alert: RedisHitRateLow
        expr: |
          1 - rate(redis_keyspace_misses_total[5m])
          / rate(redis_keyspace_hits_total[5m])
          < 0.8   # 命中率 < 80%
        for: 10m
        labels: {severity: warning}

      # Redis 频繁淘汰
      - alert: RedisEvictionRate
        expr: rate(redis_evicted_keys_total[5m]) > 100
        for: 5m
        labels: {severity: warning}
        annotations:
          summary: "Redis 频繁淘汰 key（容量不足）"

      # 慢查询 spike
      - alert: MySQLSlowQuerySpike
        expr: |
          rate(mysql_global_status_slow_queries[5m])
          > rate(mysql_global_status_slow_queries[1h] offset 1d) * 3
        for: 10m
        labels: {severity: warning}
```

## 慢查询分析流程

```
1. 触发慢查询告警
   ↓
2. 拉 slow query log
   mysqldumpslow -s t /var/log/mysql/slow.log | head
   ↓
3. 找到慢 SQL → 拿 schema
   ↓
4. EXPLAIN ANALYZE 看执行计划
   - 看是否走索引（全表扫描 = 缺索引）
   - 看 join 顺序
   - 看 rows 估算
   ↓
5. 优化：
   - 加索引
   - 改写 SQL（避免 SELECT * / 避免子查询）
   - 拆表 / 分区
   ↓
6. 验证：slow query 指标下降
```

## 一句话总结

> **DB 监控 = Exporter + 慢查询 + EXPLAIN**。**MySQL / PG / Redis 都有官方 exporter**。**关键指标：连接池 / 慢查询 / 复制延迟 / 命中率 / 淘汰率**。

---

## 关联章节

- [Exporter](../03-prometheus/exporter.md)
- [K8s 监控](./k8s-monitor.md)
- [RED 方法](../09-app-instrumentation/red-method.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
