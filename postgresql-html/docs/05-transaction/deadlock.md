---
title: 死锁排查
description: deadlock_detected 错误处理
---

# 死锁排查

> **TL;DR**：PG 自动检测死锁 + 回滚较小事务。**应用层需要 retry**。**避免策略**：固定锁顺序、缩短事务、行锁替代表锁。

## 一句话定义

```
死锁 = 两个事务互相等待对方释放锁
     = PG 自动检测
     = 自动回滚代价较小的事务
     = 应用层需要 retry
```

## 死锁检测

```
PG 启动后每 1s 检查一次 wait_queue
如果发现循环依赖 → 选代价小的事务回滚 → 另一事务继续执行
```

## 错误码

```sql
-- 死锁错误
ERROR: deadlock detected
DETAIL: Process 1234 waits for ShareLock on transaction 5678; blocked by process 5678.
HINT: See server log for query details.
CONTEXT: SQL statement "..."
SQLSTATE: 40P01
```

## 应用层 Retry

```java
@Transactional
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    int maxRetries = 3;
    for (int attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            // 业务代码
            accountDao.updateBalance(fromId, amount.negate());
            accountDao.updateBalance(toId, amount);
            return;  // 成功
        } catch (DataAccessException e) {
            if (isDeadlock(e) && attempt < maxRetries) {
                Thread.sleep(50L * attempt);  // 指数 backoff
                continue;  // 重试
            }
            throw e;
        }
    }
}

private boolean isDeadlock(Exception e) {
    return e.getMessage().contains("deadlock detected") 
        || (e.getCause() instanceof SQLException 
            && "40P01".equals(((SQLException) e.getCause()).getSQLState()));
}
```

## 排查死锁

### 启用详细日志

```ini
# postgresql.conf
log_lock_waits = on          # 记录所有锁等待
deadlock_timeout = '1s'      # 死锁检测间隔（默认 1s）
```

### 看死锁日志

```
ERROR:  deadlock detected at 2026-08-09 10:00:00
DETAIL: Process 1234 waits for ShareLock on transaction 5678; 
        blocked by process 5678.
        Process 5678 waits for ShareLock on transaction 1234; 
        blocked by process 1234.
HINT:   See server log for query details.
QUERY:  UPDATE accounts SET balance = balance - 100 WHERE id = 1
```

### pg_stat_activity 查锁等待

```sql
SELECT
  blocked.pid AS blocked_pid,
  blocking.pid AS blocking_pid,
  now() - blocked.query_start AS blocked_duration,
  blocked.query AS blocked_query,
  blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid
JOIN pg_locks kl ON kl.locktype = bl.locktype
  AND kl.pid != bl.pid
  AND kl.granted
  AND kl.relation IS NOT DISTINCT FROM bl.relation
  AND kl.tuple IS NOT DISTINCT FROM bl.tuple
JOIN pg_stat_activity blocking ON blocking.pid = kl.pid
WHERE NOT bl.granted;
```

## 避免死锁的 4 个原则

### 1. 固定锁顺序

```java
// ❌ 错误：顺序不一致
void transfer(Long a, Long b, BigDecimal amount) {
    accountDao.updateBalance(a, amount.negate());  // 先 a
    accountDao.updateBalance(b, amount);          // 后 b
}

// A 转 B 顺序：a, b
// B 转 A 顺序：b, a
// 可能死锁

// ✅ 修复：固定按 id 升序
void transfer(Long a, Long b, BigDecimal amount) {
    Long first = Math.min(a, b);
    Long second = Math.max(a, b);
    accountDao.updateBalance(first, ...);  // 小 id 先
    accountDao.updateBalance(second, ...); // 大 id 后
}
```

### 2. 缩短事务

```java
// ❌ 错误：长事务
@Transactional
public void processOrder(Order order) {
    // 业务逻辑
    orderDao.save(order);
    paymentService.charge(order);  // ← HTTP 调用，10s+
    inventoryService.reduce(order); // ← 又一个 HTTP 调用
    notificationService.send(order); // ← 又一个
}

// ✅ 修复：事务只做 DB 操作
public void processOrder(Order order) {
    saveOrder(order);  // 短事务
    // 事务外做副作用
    asyncExecutor.submit(() -> {
        paymentService.charge(order);
        // ...
    });
}
```

### 3. 行锁替代表锁

```sql
-- ❌ 表锁
LOCK TABLE users IN EXCLUSIVE MODE;

-- ✅ 行锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;
```

### 4. 监控长事务

```ini
# postgresql.conf
idle_in_transaction_session_timeout = '60s'
statement_timeout = '30s'
```

## 实战案例

### 案例 1：转账并发死锁

**场景**：用户 A → B 和 B → A 同时转账

**修复**：

```java
// 固定顺序：先小 id
@Transactional
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    if (fromId > toId) {
        // 调换顺序
        Long tmp = fromId; fromId = toId; toId = tmp;
        amount = amount.negate();
    }
    accountDao.updateBalance(fromId, amount.negate());
    accountDao.updateBalance(toId, amount);
}
```

### 案例 2：批量更新死锁

**场景**：批量 UPDATE 同一表的不同行

**修复**：分批 + SKIP LOCKED

```sql
DO $$
DECLARE
  affected INT;
BEGIN
  LOOP
    UPDATE large_table
    SET status = 'processed'
    WHERE id IN (
      SELECT id FROM large_table
      WHERE status = 'pending'
      LIMIT 1000
      FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS affected = ROW_COUNT;
    EXIT WHEN affected = 0;
    COMMIT;
    PERFORM pg_sleep(0.1);
  END LOOP;
END $$;
```

## 一句话总结

> **死锁 = 必然会发生，应用必须 retry**。**避免策略**：**固定锁顺序 + 缩短事务 + 行锁替代表锁 + 监控长事务**。**PG 1s 检测一次** + 自动回滚较小事务 + SQLSTATE `40P01`。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
