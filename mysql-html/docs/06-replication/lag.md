---
title: 主从延迟排查
date: 2026-08-15  # date-auto-injected
---

# ⏱️ MySQL 主从延迟排查

> 主从延迟是主从复制最常见的问题。延迟过大会导致读到"过时"的数据，影响业务。

## 🎯 什么是主从延迟？

主库执行完事务后，从库需要时间应用这些变更。这个时间差就是延迟。

```sql
-- 查看延迟
SHOW SLAVE STATUS\G
-- Seconds_Behind_Master: 30  （延迟 30 秒）
```

```
Master: T=0 写入订单 #100
Slave:  T=30 才写入订单 #100  （延迟 30 秒）

后果：用户在主库下完单，去从库查时找不到！
```

## 📊 延迟的常见原因

### 1. 主库大事务

```sql
-- ❌ 一次性更新 100 万行
UPDATE orders SET status = 'paid' WHERE created_at < '2025-01-01';

-- binlog 内容：100 万条行变更
-- 从库需要全部重放 → 延迟

-- ✅ 分批小事务
UPDATE orders SET status = 'paid'
WHERE created_at < '2025-01-01' LIMIT 10000;
-- 每批 1 万行，分 100 次执行
```

### 2. 从库单线程复制（旧版本）

```
MySQL 5.6 之前：单线程重放 SQL
- 主库并发写 100 个事务
- 从库串行重放，可能延迟很大

MySQL 5.7+：多线程复制（基于组提交）
- 多个 SQL 线程并发重放
- 大幅降低延迟
```

### 3. 从库性能不足

```sql
-- 从库的硬件配置应该 >= 主库 70%
-- 从库通常只承担读，但写重放也是写 IO

-- ⚠️ 在从库上跑大查询 → 阻塞 SQL 线程
SELECT * FROM huge_table WHERE ...;
-- 这个查询会持有锁，阻塞复制重放
```

### 4. 网络慢

```
主库 → 从库的网络延迟
- 同机房：< 1ms
- 跨机房：1-10ms
- 跨地域：10-100ms

binlog 大小 × 网络延迟 = 同步延迟
```

### 5. 锁等待

```sql
-- 从库上有人跑长时间查询，持有锁
SELECT * FROM orders FOR UPDATE;  -- 长时间持有 X 锁
-- 复制线程需要加 X 锁重放 SQL，但被阻塞
```

## 🔍 排查延迟

### 步骤 1：确认延迟大小

```sql
SHOW SLAVE STATUS\G
-- Seconds_Behind_Master: 30
```

### 步骤 2：查看主从状态

```sql
-- 主库：查看 binlog 写入位置
SHOW MASTER STATUS;

-- 从库：查看读取位置
SHOW SLAVE STATUS\G
-- Master_Log_File: 实际读到的 binlog 文件
-- Read_Master_Log_Pos: 实际读到的 position
-- Relay_Master_Log_File: 已应用的 binlog 文件
-- Exec_Master_Log_Pos: 已应用的 position
```

### 步骤 3：分析延迟原因

```sql
-- 查看从库的负载
SHOW PROCESSLIST;
-- 是否有大查询在跑？

-- 查看从库的 IO
SHOW ENGINE INNODB STATUS\G
-- FILE I/O 部分的统计

-- 查看复制线程状态
SHOW SLAVE STATUS\G
-- Slave_IO_Running: Yes
-- Slave_SQL_Running: Yes
```

## 🛠️ 优化延迟的方案

### 1. 启用多线程复制（MySQL 5.7+）

```ini
[mysqld]
# 从库配置
slave_parallel_workers = 8           # 8 个 SQL 线程并发
slave_parallel_type = LOGICAL_CLOCK # 基于组提交（推荐）
slave_preserve_commit_order = ON     # 保持事务顺序
```

```sql
-- 动态启用
SET GLOBAL slave_parallel_workers = 8;
SET GLOBAL slave_parallel_type = 'LOGICAL_CLOCK';
SET GLOBAL slave_preserve_commit_order = ON;
```

### 2. 拆分大事务

```sql
-- ❌ 大事务
DELETE FROM logs WHERE created_at < '2024-01-01';
-- 一次删除 1 亿行，binlog 暴涨

-- ✅ 分批删除
DELETE FROM logs WHERE created_at < '2024-01-01' LIMIT 10000;
-- 循环执行，每批 commit
```

### 3. 升级 MySQL 版本

| 版本 | 复制性能 |
|---|---|
| 5.5 及之前 | 单线程，慢 |
| 5.6 | 单线程，但支持 GTID |
| 5.7 | **多线程复制，性能 10x** |
| 8.0 | 更智能的多线程 + 写入集优化 |

### 4. 改善网络

```
- 使用万兆网络（10Gbps）
- 主从同机房部署
- 避免跨地域复制（除非用 GTID + 半同步）
```

### 5. 提升从库硬件

```ini
# 从库配置应该足够
innodb_buffer_pool_size = 16G  # 足够大的缓冲池
innodb_io_capacity = 2000      # SSD 配置
innodb_flush_neighbors = 0     # SSD 关闭邻页刷新
```

### 6. 监控慢查询

```sql
-- 从库开启慢查询日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;
-- 找出阻塞复制的慢查询
```

### 7. 控制主库的写压力

```sql
-- 在应用层做批量插入（避免高频小事务）
INSERT INTO logs (data) VALUES (...), (...), (...), ...;
-- 而非循环单条 INSERT
```

## 🎯 应用层处理延迟

### 强制读主库（关键业务）

```java
// Java 示例
@Service
public class OrderService {

    @Autowired
    @Qualifier("masterDataSource")
    private DataSource masterDataSource;

    @Autowired
    @Qualifier("slaveDataSource")
    private DataSource slaveDataSource;

    // 创建订单：读主库（保证读到刚写入的数据）
    public Order createOrder(OrderDTO dto) {
        // 强制读主库
        return executeWithMaster(masterDataSource, () -> {
            return orderMapper.insert(dto);
        });
    }

    // 查询订单列表：读从库（性能更好）
    public List<Order> listOrders(Long userId) {
        return executeWithSlave(slaveDataSource, () -> {
            return orderMapper.selectByUserId(userId);
        });
    }
}
```

### 等延迟追上

```java
// 写入主库后，等待从库同步
public void createOrder(OrderDTO dto) {
    // 1. 写入主库
    Long orderId = orderMapper.insert(dto);

    // 2. 等待从库同步（最多等 5 秒）
    for (int i = 0; i < 50; i++) {
        Long count = jdbcTemplate.queryForObject(
            "SELECT COUNT(*) FROM orders WHERE id = ? AND status = 'created'", Long.class, orderId
        );
        if (count != null && count > 0) break;
        Thread.sleep(100);
    }

    // 3. 现在从从库读，能读到
    return orderMapper.selectById(orderId);
}
```

## 📊 监控告警

```yaml
# Prometheus 告警
groups:
- name: mysql_replication_lag
  rules:
  - alert: MySQLReplicationLag
    expr: mysql_slave_status_seconds_behind_master > 30
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "主从延迟超过 30 秒"
      description: "实例 {{ $labels.instance }} 延迟 {{ $value }} 秒"

  - alert: MySQLReplicationLagCritical
    expr: mysql_slave_status_seconds_behind_master > 300
    for: 1m
    labels:
      severity: critical
```

## 🎯 总结

**延迟优化优先级：**
1. ✅ 启用多线程复制（MySQL 5.7+）
2. ✅ 拆分大事务
3. ✅ 避免在从库跑大查询
4. ✅ 改善网络（同机房部署）
5. ✅ 提升从库硬件（SSD）
6. ✅ 应用层处理（强制读主库）

**典型延迟水平：**
- 健康：< 1 秒
- 可接受：1-5 秒
- 需要优化：5-30 秒
- 严重：> 30 秒

**下一步：** [📖 读写分离实战](../06-replication/read-write-split) — 应用层如何利用主从架构

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
