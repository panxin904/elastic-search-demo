---
title: 锁机制
description: PostgreSQL 行级锁、表锁、咨询锁
---

# 锁机制

> **TL;DR**：PG 默认用 **MVCC 实现读写不冲突**，但**写写、读写 + 写**仍需要锁。生产最常见的两个锁问题：**行锁等待**（业务卡顿）和 **死锁**（自动检测 + 回滚）。**理解 pg_locks + pg_stat_activity 是定位锁问题的关键**。

## 一句话定义

```
PG 锁 = 控制并发修改的机制，分 3 类：
  - 行级锁（最细粒度，最常用）
  - 表级锁（DDL / 批量操作）
  - 咨询锁（应用层自定义锁）
```

## 行级锁（最常用）

### 4 种行锁模式

```sql
-- 1. FOR UPDATE：最强，阻塞所有其他锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;
UPDATE users SET name = 'xxx' WHERE id = 1;
DELETE FROM users WHERE id = 1;

-- 2. FOR NO KEY UPDATE：与 FOR UPDATE 类似，但允许其他 FOR KEY SHARE
--    （区别在于是否保护外键）
SELECT * FROM users WHERE id = 1 FOR NO KEY UPDATE;

-- 3. FOR SHARE：共享锁，允许多个读，但阻塞写
SELECT * FROM users WHERE id = 1 FOR SHARE;

-- 4. FOR KEY SHARE：最弱，保护外键引用
SELECT * FROM users WHERE id = 1 FOR KEY SHARE;
```

**冲突矩阵**：

| | FOR UPDATE | FOR NO KEY UPDATE | FOR SHARE | FOR KEY SHARE |
|---|---|---|---|---|
| FOR UPDATE | 冲突 | 冲突 | 冲突 | 冲突 |
| FOR NO KEY UPDATE | 冲突 | 冲突 | 冲突 | ✓ |
| FOR SHARE | 冲突 | 冲突 | ✓ | ✓ |
| FOR KEY SHARE | 冲突 | ✓ | ✓ | ✓ |

### NOWAIT 和 SKIP LOCKED

```sql
-- NOWAIT：拿不到锁立即报错
SELECT * FROM users WHERE id = 1 FOR UPDATE NOWAIT;
-- ERROR: could not obtain lock on row in relation "users"

-- SKIP LOCKED：跳过已锁定的行（任务队列神器）
SELECT * FROM jobs 
WHERE status = 'pending'
LIMIT 10
FOR UPDATE SKIP LOCKED;
-- 多个 worker 并发取任务，互不阻塞
```

## 表级锁

| 模式 | 冲突 | 用途 |
|---|---|---|
| ACCESS SHARE | 只与 ACCESS EXCLUSIVE 冲突 | SELECT |
| ROW SHARE | 与 EXCLUSIVE 冲突 | SELECT FOR UPDATE |
| ROW EXCLUSIVE | 与 SHARE 冲突 | INSERT/UPDATE/DELETE |
| SHARE UPDATE EXCLUSIVE | 与多数冲突 | VACUUM / ANALYZE |
| SHARE | 与 ROW EXCLUSIVE 冲突 | CREATE INDEX |
| ACCESS EXCLUSIVE | 与**所有**锁冲突 | DROP / ALTER / VACUUM FULL |

```sql
-- 查看表锁
SELECT locktype, mode, granted, pid
FROM pg_locks
WHERE relation = 'users'::regclass;

-- 查看谁在锁
SELECT
  pg_class.relname,
  pg_locks.mode,
  pg_stat_activity.usename,
  pg_stat_activity.query
FROM pg_locks
JOIN pg_class ON pg_locks.relation = pg_class.oid
JOIN pg_stat_activity ON pg_locks.pid = pg_stat_activity.pid
WHERE pg_class.relname = 'users';
```

## 死锁

**PG 自动检测死锁**：

```
两个事务相互等待 → PG 检测到死锁 → 自动回滚其中一个（牺牲品）
```

**应用端要 retry**：

```java
// Java retry
@Transactional
public void transferMoney(Long fromId, Long toId, BigDecimal amount) {
    try {
        // 业务逻辑（扣款 + 加款）
    } catch (DataAccessException e) {
        if (e.getMessage().contains("deadlock detected")) {
            // 重试
        } else throw e;
    }
}
```

**避免死锁的 4 个原则**：

```
1. 固定顺序访问资源
   - 所有业务先按 id 升序加锁，再按 id 降序

2. 缩短事务
   - 事务内只做必要操作
   - 不要在事务里调用外部 HTTP

3. 用更细粒度锁
   - 行锁 > 表锁
   - SELECT FOR UPDATE 限定 WHERE

4. 避免长事务
   - 设置 statement_timeout
   - 监控 idle_in_transaction
```

## 咨询锁（应用层锁）

```sql
-- 1. 获取会话级锁
SELECT pg_advisory_lock(123);

-- 2. 获取事务级锁（事务结束自动释放）
SELECT pg_advisory_xact_lock(123);

-- 3. 非阻塞版本
SELECT pg_try_advisory_lock(123);  -- 返回 boolean

-- 4. 释放
SELECT pg_advisory_unlock(123);
```

**实战：分布式锁**

```sql
-- Worker 想执行任务
SELECT pg_try_advisory_lock(789);
-- true = 拿到锁，执行任务
-- false = 别人在跑，跳过

-- 任务完成
SELECT pg_advisory_unlock(789);
```

**应用场景**：
- 定时任务（防止多实例并发）
- 分布式系统协调
- 全局配置更新

## 实战案例

### 案例 1：行锁等待导致接口超时

**现象**：订单创建接口超时。

**定位**：

```sql
-- 看阻塞链
SELECT
  blocked.pid AS blocked_pid,
  blocking.pid AS blocking_pid,
  blocked.query AS blocked_query,
  blocking.query AS blocking_query,
  now() - blocked.query_start AS blocked_duration
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid
JOIN pg_locks kl ON kl.locktype = bl.locktype
  AND kl.pid != bl.pid
  AND kl.granted
JOIN pg_stat_activity blocking ON blocking.pid = kl.pid
WHERE NOT bl.granted;
```

**根因**：事务 A 长事务持有行锁不释放，B 等待。

**修复**：

```ini
# postgresql.conf
# 1. 限制单语句执行时间
statement_timeout = '30s'

# 2. 限制空闲事务（防止忘了 commit）
idle_in_transaction_session_timeout = '60s'
```

```sql
-- 杀长事务
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '5 minutes';
```

### 案例 2：批量更新导致全表锁

**现象**：批量 UPDATE 100 万行，30 分钟，期间该表所有读都被阻塞。

**修复**：分批更新

```sql
-- ❌ 一次更新全表
UPDATE users SET status = 'inactive' WHERE last_login < '2020-01-01';

-- ✅ 分批更新
DO $$
DECLARE
  affected INT;
BEGIN
  LOOP
    UPDATE users 
    SET status = 'inactive' 
    WHERE id IN (
      SELECT id FROM users 
      WHERE status = 'active' AND last_login < '2020-01-01'
      LIMIT 10000
      FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS affected = ROW_COUNT;
    EXIT WHEN affected = 0;
    COMMIT;  -- 每批提交
    RAISE NOTICE 'Updated % rows', affected;
    PERFORM pg_sleep(0.1);
  END LOOP;
END $$;
```

### 案例 3：死锁频发

**现象**：转账业务每天死锁 100+ 次。

**根因**：两个账户互相转账时顺序不一致。

**修复**：

```java
// 统一按 id 升序加锁
@Transactional
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    // 关键：先锁 id 小的，再锁 id 大的
    Long first = Math.min(fromId, toId);
    Long second = Math.max(fromId, toId);
    
    // 第一步：扣款（先锁 first）
    accountDao.updateBalance(first, -amount);
    
    // 第二步：加款（再锁 second）
    accountDao.updateBalance(second, amount);
}
```

## 监控告警

### 关键指标

```sql
-- 1. 等待中的锁数
SELECT count(*) FROM pg_locks WHERE NOT granted;

-- 2. 死锁次数
SELECT datname, deadlocks FROM pg_stat_database;

-- 3. 长事务
SELECT count(*), max(now() - xact_start)
FROM pg_stat_activity
WHERE xact_start IS NOT NULL AND state != 'idle';
```

### Prometheus 告警

```yaml
groups:
- name: pg_locks
  rules:
  - alert: PGLongTransaction
    expr: pg_stat_activity_max_tx_duration{state="active"} > 300
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "PG 长事务超过 5 分钟"

  - alert: PGIdleInTransaction
    expr: pg_stat_activity_count{state="idle in transaction"} > 5
    for: 10m
    labels:
      severity: warning
    annotations:
      summary: "PG 有 5+ idle in transaction 连接"

  - alert: PGLockWait
    expr: pg_locks_count{granted="false"} > 10
    for: 1m
    labels:
      severity: page
    annotations:
      summary: "PG 有 10+ 锁等待"
```

## 一句话总结

> **PG 锁 = MVCC + 行锁为主**：默认读不阻塞读、写不阻塞读（MVCC），**写阻塞写**（行锁）。生产最常见 3 个问题：行锁等待（长事务导致）、死锁（应用层 retry）、全表锁（批量操作分批）。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
