---
title: 死锁分析与排查
date: 2026-08-15  # date-auto-injected
---

# 💀 MySQL 死锁分析与排查

> 死锁是并发系统的常见问题。InnoDB 自动检测死锁并回滚一个事务，但应用层必须妥善处理。

## 🤔 什么是死锁？

**两个或多个事务互相等待对方持有的锁，导致都无法继续执行。**

```
事务 A                    事务 B
├─ 锁 id=1                ├─ 锁 id=2
│                         │
├─ 等待 id=2 ─────────────┤─ 等待 id=1
│  (阻塞)                  │  (阻塞)
│                         │
└─ 死锁！                └─ 死锁！
```

## 🎯 死锁的四个必要条件（Coffman 条件）

1. **互斥**：锁只能被一个事务持有
2. **持有并等待**：事务持有锁的同时等待其他锁
3. **不可抢占**：锁不能被强制剥夺
4. **循环等待**：事务之间形成等待环路

**打破任一条件即可避免死锁**。

## 🔍 经典死锁场景

### 场景 1：转账死锁

```sql
-- 经典场景：转账导致死锁
-- T1: 转账 A → B
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 锁 id=1
UPDATE accounts SET balance = balance + 100 WHERE id = 2;  -- 等待 id=2

-- T2: 转账 B → A
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 2;  -- 锁 id=2
UPDATE accounts SET balance = balance + 100 WHERE id = 1;  -- 等待 id=1

-- 💀 死锁！InnoDB 检测后回滚其中一个事务
```

### 场景 2：间隙锁死锁

```sql
-- 表 data: id = 1, 5, 10
-- T1: 范围查询
START TRANSACTION;
SELECT * FROM data WHERE id BETWEEN 3 AND 7 FOR UPDATE;
-- 间隙锁：(1, 5) 和 (5, 10)

-- T2: 插入
START TRANSACTION;
INSERT INTO data (id) VALUES (6);  -- 等待 T1 的间隙锁

-- T1: 插入
INSERT INTO data (id) VALUES (8);  -- 等待 T2 的插入意向锁
-- 💀 死锁！
```

### 场景 3：共享锁升级死锁

```sql
-- T1: 共享锁
START TRANSACTION;
SELECT * FROM users WHERE id = 1 FOR SHARE;

-- T2: 共享锁
START TRANSACTION;
SELECT * FROM users WHERE id = 2 FOR SHARE;

-- T1: 想升级为排他锁
UPDATE users SET name = 'x' WHERE id = 2;  -- 等待 T2 的 S 锁

-- T2: 想升级为排他锁
UPDATE users SET name = 'y' WHERE id = 1;  -- 等待 T1 的 S 锁

-- 💀 死锁！
```

## 🔧 InnoDB 死锁检测

### 检测机制

```sql
-- 查看是否开启死锁检测（默认 ON）
SHOW VARIABLES LIKE 'innodb_deadlock_detect';
-- ON: 检测到死锁立即回滚（推荐）
-- OFF: 等待 innodb_lock_wait_timeout 才回滚

-- 死锁等待超时（默认 50 秒）
SHOW VARIABLES LIKE 'innodb_lock_wait_timeout';
```

### 自动回滚策略

```
InnoDB 检测到死锁后：
1. 选择"代价最小"的事务回滚（undo log 数量最少）
2. 返回错误 ER_LOCK_DEADLOCK (1213)
3. 另一个事务继续执行
```

## 📊 实战：查看死锁日志

### 启用死锁日志

```sql
-- 启用详细死锁日志
SET GLOBAL innodb_print_all_deadlocks = ON;

-- 或在 my.cnf 中
[mysqld]
innodb_print_all_deadlocks = ON
```

### 死锁日志示例

```
=====================================
2025-07-18 10:23:45 0x7f1234567890 INNODB MONITOR OUTPUT
=====================================
LATEST DETECTED DEADLOCK
------------------------
2025-07-18 10:23:45 1*** TRANSACTION 12345, ACTIVE 2 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 3 lock struct(s), heap size 1136, 2 row lock(s)
MySQL thread id 100, query id 1234, OS thread handle 0x7f1234567890

-- 事务 1 正在等待的锁
*** (1) WAITING FOR THIS LOCK TO BE GRANTED:
RECORD LOCKS space id 100 page no 4 n bits 72 index PRIMARY of table `test`.`accounts`
Record lock, heap no 5 PHYSICAL RECORD: n_fields 4; compact format; info bits 0
 0: len 4; hex 80000002; asc     2;;
 1: len 6; hex 000000000234; asc       ;;
 2: len 7; hex 810000012d0110; asc       ;;
 3: len 4; hex 8000012c; asc     ,;;

-- 事务 1 持有的锁
*** (1) HOLDS THE LOCK(S):
RECORD LOCKS space id 100 page no 4 n bits 72 index PRIMARY of table `test`.`accounts`
Record lock, heap no 3 PHYSICAL RECORD: n_fields 4
 0: len 4; hex 80000001; asc     1;;
-- ...

*** (2) TRANSACTION:
-- 事务 2 等待的锁 + 持有的锁
...

*** WE ROLL BACK TRANSACTION (2)
-- InnoDB 选择了事务 2 回滚
```

## 🛠️ 应用层处理死锁

### 1. 捕获死锁错误并重试

```java
// Java 示例（Spring Boot）
@Service
public class TransferService {
    
    @Autowired
    private JdbcTemplate jdbcTemplate;
    
    @Transactional
    public void transfer(int fromId, int toId, BigDecimal amount) {
        try {
            // 转账逻辑
            jdbcTemplate.update("UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, fromId);
            jdbcTemplate.update("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, toId);
        } catch (DataIntegrityViolationException e) {
            // 1213 = ER_LOCK_DEADLOCK
            // 抛出此异常让外层重试
            throw e;
        }
    }
}

@Service
public class TransferRetryService {
    private static final int MAX_RETRIES = 3;
    
    public void transferWithRetry(int fromId, int toId, BigDecimal amount) {
        for (int i = 0; i < MAX_RETRIES; i++) {
            try {
                transferService.transfer(fromId, toId, amount);
                return;  // 成功
            } catch (DataIntegrityViolationException e) {
                if (i == MAX_RETRIES - 1) throw e;  // 最后一次重试失败
                try {
                    Thread.sleep(100L * (i + 1));  // 退避
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            }
        }
    }
}
```

### 2. Python 处理死锁

```python
import time
import pymysql
from pymysql.err import OperationalError

def transfer_with_retry(conn, from_id, to_id, amount, max_retries=3):
    for attempt in range(max_retries):
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                cur.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, from_id))
                cur.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, to_id))
                cur.execute("COMMIT")
            return  # 成功
        except OperationalError as e:
            if e.args[0] == 1213:  # 死锁错误码
                conn.rollback()
                if attempt < max_retries - 1:
                    time.sleep(0.1 * (attempt + 1))
                    continue
            raise
```

## 🛡️ 死锁预防策略

### 1. 固定访问顺序

```sql
-- ❌ 不同事务用不同顺序访问
-- T1: UPDATE a WHERE id = 1; UPDATE b WHERE id = 1;
-- T2: UPDATE b WHERE id = 1; UPDATE a WHERE id = 1;
-- 💀 死锁风险

-- ✅ 统一从小到大访问
START TRANSACTION;
UPDATE a WHERE id = 1;
UPDATE b WHERE id = 1;
COMMIT;
```

### 2. 减少事务范围

```sql
-- ❌ 大事务
START TRANSACTION;
UPDATE users SET status = 1 WHERE id BETWEEN 1 AND 100000;
UPDATE orders SET status = 'paid' WHERE user_id BETWEEN 1 AND 10000;
UPDATE accounts SET balance = balance + 100 WHERE user_id BETWEEN 1 AND 10000;
COMMIT;

-- ✅ 分批小事务
UPDATE users SET status = 1 WHERE id BETWEEN 1 AND 1000;
COMMIT;
UPDATE users SET status = 1 WHERE id BETWEEN 1001 AND 2000;
COMMIT;
```

### 3. 用更粗粒度的锁

```sql
-- ❌ 细粒度锁容易死锁
START TRANSACTION;
SELECT * FROM orders WHERE id = 1 FOR UPDATE;
SELECT * FROM orders WHERE id = 2 FOR UPDATE;  -- 可能与别的事务冲突
COMMIT;

-- ✅ 用排序后批量加锁
START TRANSACTION;
SELECT * FROM orders WHERE id IN (1, 2) ORDER BY id FOR UPDATE;
COMMIT;
```

### 4. 避免长时间持有锁

```sql
-- ❌ 事务里做耗时操作
START TRANSACTION;
SELECT * FROM users WHERE id = 1 FOR UPDATE;
-- 调用外部 HTTP 接口（5 秒）
-- 调用 Redis（1 秒）
UPDATE users SET last_login = NOW() WHERE id = 1;
COMMIT;

-- ✅ 事务只包含数据库操作
result = SELECT * FROM users WHERE id = 1 FOR UPDATE;
-- 外部操作（无锁）
callExternalApi(result);
-- 新的短事务更新
START TRANSACTION;
UPDATE users SET last_login = NOW() WHERE id = 1;
COMMIT;
```

### 5. 使用 NOWAIT 或 SKIP LOCKED

```sql
-- MySQL 8.0+: NOWAIT 立即失败（不等锁）
START TRANSACTION;
SELECT * FROM users WHERE id = 1 FOR UPDATE NOWAIT;
-- 如果锁被占用，立即报错（不等 50 秒）

-- SKIP LOCKED 跳过已锁的行（适合队列）
SELECT * FROM task_queue
WHERE status = 0
LIMIT 1
FOR UPDATE SKIP LOCKED;
-- 跳过别人正在处理的，拿到一个空闲的
```

## 🔍 监控死锁

### 查看死锁统计

```sql
-- 查看总死锁次数
SHOW STATUS LIKE 'Innodb_deadlocks';

-- 或
SHOW ENGINE INNODB STATUS\G
-- 在输出中查找 "LATEST DETECTED DEADLOCK"
```

### 实时监控

```sql
-- 8.0+: 查看当前锁等待
SELECT
  t.trx_id,
  t.trx_state,
  t.trx_started,
  TIMESTAMPDIFF(SECOND, t.trx_started, NOW()) AS duration_sec,
  t.trx_query,
  GROUP_CONCAT(DISTINCT lw.blocking_trx_id) AS blocking_trx_ids
FROM information_schema.innodb_trx t
LEFT JOIN performance_schema.data_lock_waits lw
  ON t.trx_id = lw.waiting_trx_id
GROUP BY t.trx_id;
```

## 📋 死锁排查清单

发现死锁时，按以下顺序排查：

1. ✅ 启用 `innodb_print_all_deadlocks = ON`
2. ✅ 查看 `SHOW ENGINE INNODB STATUS\G` 输出
3. ✅ 分析死锁日志中的两个事务
4. ✅ 找到循环等待的锁
5. ✅ 应用层是否捕获 ER_LOCK_DEADLOCK 并重试
6. ✅ 是否能统一访问顺序
7. ✅ 是否能减小事务粒度

## 🎯 总结

**死锁核心：**
- 4 个必要条件（互斥、持有等待、不可抢占、循环等待）
- 打破任一即可预防
- InnoDB 自动检测 + 回滚代价最小的事务
- 应用层必须捕获 1213 错误并重试

**预防策略：**
- ✅ 固定访问顺序
- ✅ 减少事务范围
- ✅ 用 NOWAIT / SKIP LOCKED
- ✅ 避免事务内做耗时操作

**下一步：** [🔄 MVCC 多版本并发](../04-transaction/mvcc) — InnoDB 不加锁读的实现原理


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
