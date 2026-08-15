---
title: Hot Standby 从库查询
description: PostgreSQL 从库只读查询
---

# Hot Standby 从库查询

> **TL;DR**：Hot Standby = **从库应用 WAL 时同时提供只读查询**。**读写分离、查询报表** = 标配能力。

## 一句话定义

```
Hot Standby = 流复制 + 从库可读
            = 实时跟随主库
            = 提供 SELECT（不提供 INSERT/UPDATE）
```

## 启用

```ini
# postgresql.conf（主库）
wal_level = replica
max_wal_senders = 10

# postgresql.conf（从库）
hot_standby = on
hot_standby_feedback = on       # 防止查询冲突
max_standby_streaming_delay = 30s  # 取消冲突查询的最大延迟
```

## 实战配置

```bash
# 1. 主库配置（如前）
wal_level = replica
max_wal_senders = 10
wal_keep_size = '1GB'

# 2. 从库用 pg_basebackup 初始化
pg_basebackup -h primary.db -D /data -U replicator -P -Xs -c fast

# 3. 从库 standby.signal
touch /data/standby.signal

# 4. 从库 postgresql.conf
cat >> /data/postgresql.conf << EOF
primary_conninfo = 'host=primary.db port=5432 user=replicator password=xxx'
hot_standby = on
hot_standby_feedback = on
EOF

# 5. 启动从库
pg_ctl start -D /data

# 6. 验证
psql -c "SELECT pg_is_in_recovery();"
-- t（true 表示在 recovery 模式，只读）
```

## 应用读写分离

```yaml
# Spring Boot 多数据源
spring:
  datasource:
    primary:
      url: jdbc:postgresql://primary.db:6432/mydb
      driver-class-name: org.postgresql.Driver
    replica:
      url: jdbc:postgresql://replica.db:6432/mydb
      driver-class-name: org.postgresql.Driver
```

```java
@Service
public class OrderService {
  @Autowired
  @Qualifier("primaryDataSource")
  private DataSource primaryDs;

  @Autowired
  @Qualifier("replicaDataSource")
  private DataSource replicaDs;

  @Transactional("primaryTransactionManager")
  public void createOrder(Order order) {
    // 写主库
  }

  public List<Order> getOrders(Long userId) {
    // 读从库
    return jdbcTemplate.query(
      "SELECT * FROM orders WHERE user_id = ?", 
      userId
    );
  }
}
```

## 冲突处理

**查询冲突场景**：

```
1. 主库：VACUUM 清理了 dead tuple
2. 从库：还有长查询读到这些 dead tuple
3. 冲突！从库要么取消查询，要么延迟 vacuum
```

**解决策略**：

```ini
# 1. 延迟取消查询
max_standby_streaming_delay = 30s
# 主库 vacuum 延迟 30s 等从库查询完成

# 2. 从库反馈（推荐）
hot_standby_feedback = on
# 从库告诉主库："我这里有长查询，请暂缓 vacuum"

# 3. 监控冲突
SELECT * FROM pg_stat_database_conflicts;
-- conflict_tablespace / conflict_lock / conflict_snapshot
```

## 同步 vs 异步 + Hot Standby

```
异步复制 + Hot Standby：
  - 从库最多滞后几秒
  - 适合读写分离、报表

同步复制 + Hot Standby：
  - 强一致读（理论上）
  - 实际：从库可能还没应用最新的 WAL
  - 需要 synchronous_commit = on（等从库 fsync）
```

## 监控

```sql
-- 主库：看从库延迟
SELECT
  client_addr,
  sent_lsn - replay_lsn AS byte_lag,
  EXTRACT(EPOCH FROM now() - reply_time) AS seconds_lag
FROM pg_stat_replication;

-- 从库：看 replay 进度
SELECT
  pg_last_wal_receive_lsn(),  -- 接收位置
  pg_last_wal_replay_lsn(),   -- replay 位置
  pg_last_xact_replay_timestamp();
```

## 一句话总结

> **Hot Standby = 流复制 + 从库只读查询**。**读写分离必备**。**冲突用 hot_standby_feedback 解决**，**延迟用 max_standby_streaming_delay 控制**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
