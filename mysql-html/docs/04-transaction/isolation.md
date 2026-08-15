---
title: ACID 与隔离级别
---

# ⚖️ MySQL ACID 与隔离级别

> 事务是数据库的核心概念。理解 ACID 和四种隔离级别，是处理并发问题的基础。

## 🎯 什么是事务？

**事务（Transaction）** 是一组 SQL 操作的逻辑单元，要么全部成功，要么全部失败。

```sql
-- 经典例子：转账
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- A 减 100
UPDATE accounts SET balance = balance + 100 WHERE id = 2;  -- B 加 100
COMMIT;
-- 两步必须都成功；任一失败，全部回滚
```

## ⚖️ ACID 四大特性

### A - Atomicity（原子性）

**事务是最小执行单元，不可分割。**

```sql
-- ✅ 原子性体现
START TRANSACTION;
INSERT INTO orders (user_id, amount) VALUES (1, 100);
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
COMMIT;
-- 要么都成功，要么都失败

-- ❌ 违反原子性的场景（开启自动提交时）
INSERT INTO orders (user_id, amount) VALUES (1, 100);
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
-- 如果第一条成功、第二条失败，数据不一致！
```

**实现机制：** `undo log`（回滚日志）
- 事务执行时，记录每条 SQL 的反向操作
- ROLLBACK 时执行反向操作恢复数据

### C - Consistency（一致性）

**事务前后，数据库从一个一致状态转换到另一个一致状态。**

```sql
-- ✅ 一致性体现
-- 转账前：A 有 1000，B 有 500，总和 1500
-- 转账后：A 有 900，B 有 600，总和还是 1500
-- 总金额不变 ✓
```

**实现机制：** AID 三者共同保证 C
- 原子性 → 不会部分成功
- 隔离性 → 不会互相干扰
- 持久性 → 不会丢失

### I - Isolation（隔离性）

**多个事务并发执行时，一个事务的执行不应影响其他事务。**

```sql
-- 隔离性的"理想"状态：事务串行执行
-- 但串行性能差，所以需要"隔离级别"在性能和一致性间权衡
```

### D - Durability（持久性）

**事务提交后，对数据的修改是永久的，即使系统崩溃也不会丢失。**

```sql
-- 事务提交后
COMMIT;
-- 即使立刻断电，数据也已持久化（写入 redo log 和数据文件）
```

**实现机制：** `redo log`（重做日志）
- 修改数据前，先写 redo log
- 系统恢复时，从 redo log 重放已提交的事务

## 📊 四种隔离级别

### 概览

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---|---|---|---|---|
| READ UNCOMMITTED（读未提交） | ✅ | ✅ | ✅ | 最高 |
| READ COMMITTED（读已提交） | ❌ | ✅ | ✅ | 高 |
| **REPEATABLE READ（可重复读，MySQL 默认）** | ❌ | ❌ | ✅ | 中 |
| SERIALIZABLE（可串行化） | ❌ | ❌ | ❌ | 最低 |

### 设置隔离级别

```sql
-- 全局设置（影响所有新连接）
SET GLOBAL TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- 当前会话设置
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 查看当前隔离级别
SELECT @@global.transaction_isolation;
SELECT @@session.transaction_isolation;
SHOW VARIABLES LIKE 'transaction_isolation';
```

### 配置（my.cnf）

```ini
[mysqld]
transaction-isolation = REPEATABLE-READ
```

## 🔬 三种并发问题详解

### 问题 1：脏读（Dirty Read）

**一个事务读到另一个事务未提交的数据。**

```sql
-- 时间线：
-- T1: BEGIN; UPDATE accounts SET balance = 999 WHERE id = 1;  -- 修改未提交
-- T2: SELECT balance FROM accounts WHERE id = 1;  -- 读到 999
-- T1: ROLLBACK;  -- 撤销修改，实际 balance 还是原来的值
-- T2: 用 999 计算 → 数据错误！

-- 脏读危害：T2 读到了根本不存在的数据（被 T1 回滚了）
```

### 问题 2：不可重复读（Non-Repeatable Read）

**同一事务内，两次读同一行，结果不同。**

```sql
-- T1: BEGIN;
-- T1: SELECT balance FROM accounts WHERE id = 1;  -- 读到 1000
-- T2: UPDATE accounts SET balance = 2000 WHERE id = 1;
-- T2: COMMIT;
-- T1: SELECT balance FROM accounts WHERE id = 1;  -- 读到 2000（不同！）
-- T1: COMMIT;

-- 不可重复读：同一行被修改了
```

### 问题 3：幻读（Phantom Read）

**同一事务内，两次查同一范围，记录数不同。**

```sql
-- T1: BEGIN;
-- T1: SELECT COUNT(*) FROM accounts WHERE balance > 1000;  -- 5 行
-- T2: INSERT INTO accounts (balance) VALUES (2000);  -- 插入新行
-- T2: COMMIT;
-- T1: SELECT COUNT(*) FROM accounts WHERE balance > 1000;  -- 6 行（多了 1 行！）
-- T1: COMMIT;

-- 幻读：范围查询时，新插入了符合范围的行
```

## 🎯 MySQL InnoDB 的特殊之处

### REPEATABLE READ 解决了幻读（部分）

```sql
-- MySQL 8.0 的 REPEATABLE READ 通过 MVCC 解决了大部分幻读

-- T1: BEGIN;
-- T1: SELECT * FROM t WHERE age > 20;  -- 读快照，建立 ReadView
-- T2: INSERT INTO t (age) VALUES (30);
-- T2: COMMIT;
-- T1: SELECT * FROM t WHERE age > 20;  -- 还是原来的快照（看不到 T2 插入）
-- T1: COMMIT;

-- 但当前读（FOR UPDATE）仍可能幻读
-- T1: SELECT * FROM t WHERE age > 20 FOR UPDATE;  -- 读最新数据，可能幻读
```

## 🔬 实战：四种隔离级别演示

```sql
-- 创建测试表
CREATE TABLE isolation_test (
  id INT PRIMARY KEY,
  val INT
) ENGINE=InnoDB;

-- 演示脏读（READ UNCOMMITTED）
SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;

-- 会话 1：
START TRANSACTION;
UPDATE isolation_test SET val = 999 WHERE id = 1;
-- 不 COMMIT

-- 会话 2：
SELECT * FROM isolation_test WHERE id = 1;  -- 读到 999（脏读！）

-- 会话 1：ROLLBACK;
-- 会话 2：用 999 是错的

-- ✅ 用 READ COMMITTED 就避免了脏读
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- 重复上面的步骤，会话 2 不会读到未提交的 999
```

## 🎯 如何选择隔离级别？

### MySQL 默认 REPEATABLE READ 是最佳选择

| 场景 | 推荐隔离级别 |
|---|---|
| **大多数业务** | REPEATABLE READ（MySQL 默认） |
| 需要看其他事务提交的实时数据 | READ COMMITTED |
| 金融、库存等强一致性要求 | SERIALIZABLE |
| 高并发 + 最终一致性可接受 | READ COMMITTED |

### 为什么 REPEATABLE READ 是 MySQL 的最佳选择？

- ✅ 解决了脏读、不可重复读
- ✅ 在 InnoDB 中通过 MVCC 解决了大部分幻读
- ✅ 性能比 SERIALIZABLE 好很多
- ✅ 比 READ COMMITTED 提供更强的一致性保证

## 🛠️ 实战技巧

### 1. 减少锁竞争

```sql
-- ❌ 长事务 = 长时间持锁 = 阻塞其他事务
START TRANSACTION;
SELECT * FROM huge_table WHERE ...;  -- 耗时 10 秒
UPDATE ...;
COMMIT;

-- ✅ 拆分事务
START TRANSACTION;
UPDATE small_table SET ...;
COMMIT;

-- 独立的查询不要放在事务里
SELECT * FROM huge_table;  -- 不用事务
```

### 2. 避免死锁

```sql
-- 死锁的常见原因：两个事务以相反的顺序加锁
-- T1: UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- T2: UPDATE accounts SET balance = balance - 100 WHERE id = 2;
-- T1: UPDATE accounts SET balance = balance - 100 WHERE id = 2;  -- 阻塞
-- T2: UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 死锁！

-- ✅ 解决方案：固定访问顺序
START TRANSACTION;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;  -- 总是先小后大
UPDATE accounts SET balance = balance - 100 WHERE id = 2;
COMMIT;
```

### 3. 监控长事务

```sql
-- 查看运行超过 60 秒的事务
SELECT * FROM information_schema.innodb_trx
WHERE TIME_TO_SEC(TIMEDIFF(NOW(), trx_started)) > 60;

-- 查看锁等待
SELECT * FROM performance_schema.data_lock_waits;
```

## 🎯 总结

**ACID 四性：**
- **A**tomicity：原子性（undo log）
- **C**onsistency：一致性（AID 共同保证）
- **I**solation：隔离性（隔离级别）
- **D**urability：持久性（redo log）

**四种隔离级别：**
- READ UNCOMMITTED：脏读、不可重复读、幻读（基本不用）
- READ COMMITTED：避免脏读（Oracle 默认）
- **REPEATABLE READ**：避免脏读、不可重复读（**MySQL 默认**）
- SERIALIZABLE：全部避免（性能差）

**下一步：** [🔐 InnoDB 锁机制](../04-transaction/locks) — 深入理解行锁、表锁、意向锁