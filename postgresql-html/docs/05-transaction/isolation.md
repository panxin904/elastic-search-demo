---
title: 事务隔离级别
date: 2026-08-15  # date-auto-injected
description: PostgreSQL 4 个隔离级别与异常现象
---

# 事务隔离级别

> **TL;DR**：SQL 标准定义了 4 个隔离级别（读未提交、读已提交、可重复读、可串行化）。**PG 默认 Read Committed**，但实际表现比 MySQL 强。**生产 95% 用 Read Committed，需要强一致时用 Serializable**。

## 一句话定义

| 级别 | 简称 | PG 支持 | 脏读 | 不可重复读 | 幻读 | 序列化异常 |
|---|---|---|---|---|---|---|
| Read Uncommitted | RU | ❌ 视作 RC | ❌ | ❌ | ❌ | ❌ |
| **Read Committed** | **RC** | ✅ 默认 | ❌ | ✅ | ✅ | ✅ |
| Repeatable Read | RR | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Serializable** | **SER** | ✅ | ❌ | ❌ | ❌ | ❌ |

> **关键点**：PG 的 RR 实际**不出现幻读**（快照隔离），但**可能出现 serialization failure**（40001 错误）。PG 的 SER 通过 SSI 实现真串行化。

## 三种异常现象

### 1. 脏读（Dirty Read）

读到其他事务**未提交**的数据。

```sql
-- 会话 A
BEGIN;
UPDATE accounts SET balance = 0 WHERE id = 1;

-- 会话 B（在 A 提交前读）
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- 看到 0（脏读）

-- 会话 A
ROLLBACK;  -- 撤销 update
```

**PG 行为**：Read Committed 都不会脏读，脏读只发生在 Read Uncommitted 级别（PG 不支持）。

### 2. 不可重复读（Non-repeatable Read）

同一事务内两次读同一行，结果不同（被其他事务 UPDATE）。

```sql
-- 会话 A
BEGIN;
SELECT balance FROM accounts WHERE id = 1;  -- 100

-- 会话 B
BEGIN;
UPDATE accounts SET balance = 200 WHERE id = 1;
COMMIT;

-- 会话 A 再次读
SELECT balance FROM accounts WHERE id = 1;  -- 200（不可重复读）
COMMIT;
```

**PG 行为**：
- Read Committed：出现
- Repeatable Read：**不出现**（快照固定）

### 3. 幻读（Phantom Read）

同一事务内两次范围查询，结果集行数不同（被其他事务 INSERT/DELETE）。

```sql
-- 会话 A
BEGIN;
SELECT count(*) FROM accounts WHERE balance > 100;  -- 100 行

-- 会话 B
BEGIN;
INSERT INTO accounts (balance) VALUES (500);
COMMIT;

-- 会话 A 再次查
SELECT count(*) FROM accounts WHERE balance > 100;  -- 101 行（幻读）
COMMIT;
```

**PG 行为**：
- Read Committed：出现
- Repeatable Read：**不出现**（快照固定）
- Serializable：**不出现**（SSI 检测）

## PG 默认 Read Committed 的特殊行为

PG 的 RC 跟其他数据库不同：

### 语句级快照（不是事务级）

```
RC 级别下，每个 SQL 语句都获取新快照
```

**例子**：

```sql
-- 会话 A
BEGIN;
SELECT count(*) FROM accounts WHERE balance > 100;  -- 100

-- 会话 B
INSERT INTO accounts (balance) VALUES (500);
COMMIT;

-- 会话 A 同一事务内
SELECT count(*) FROM accounts WHERE balance > 100;  -- 101（看到 B 的提交）

UPDATE accounts SET balance = balance + 1 WHERE balance > 100;
-- 这条 UPDATE 会更新 101 行（包括刚 INSERT 的行）

SELECT count(*) FROM accounts WHERE balance > 100;  -- 101
COMMIT;
```

> **核心**：PG RC 下 SELECT 看到新数据，但 UPDATE 会**修改"在快照里"和"实际存在"的数据**——这是 RC 的特殊语义，**用于减少 serialization failure**。

### 读 + 写冲突的等待

PG RC 下，如果两个事务同时 UPDATE 同一行：

```
会话 A: UPDATE row WHERE id = 1  -- 拿锁
会话 B: UPDATE row WHERE id = 1  -- 等待 A 提交/回滚
A COMMIT
B 拿到锁 → 看到 A 修改后的值（不是 B 事务开始时的值）
```

## 设置隔离级别

```sql
-- 1. 事务级
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT ... ;
COMMIT;

-- 2. 会话级（之后所有事务）
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- 3. 单事务级
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

```ini
# postgresql.conf
default_transaction_isolation = 'read committed'
```

## Serializable + SSI

**SSI**（Serializable Snapshot Isolation）= PG 9.1 引入，用乐观并发实现真串行化。

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;

-- 检查库存
SELECT stock FROM products WHERE id = 1;  -- 5

-- 扣库存
UPDATE products SET stock = stock - 1 WHERE id = 1;

INSERT INTO orders (product_id, qty) VALUES (1, 1);
COMMIT;

-- 如果两个事务同时扣，第二个会得到：
-- ERROR: could not serialize access due to read/write dependencies among transactions
```

**应用处理**：

```java
// Java 端 retry 逻辑
int maxRetries = 3;
for (int i = 0; i < maxRetries; i++) {
    try {
        // 业务逻辑（Serializable 事务）
        doBusinessLogic();
        break;
    } catch (SQLException e) {
        if (e.getSQLState().equals("40001")) {  // serialization_failure
            Thread.sleep(50 * (i + 1));  // backoff
            continue;
        }
        throw e;
    }
}
```

> **何时用 Serializable**：库存扣减、转账、票务抢购（不能超卖）等**金融级一致**场景。

## 实战选型

### 选 Read Committed（默认，95% 场景）

```sql
-- 大多数业务不需要 Serializable
-- READ COMMITTED + 业务层幂等足够
```

### 选 Repeatable Read

```sql
-- 长事务（如数据迁移、报表统计）
-- 同一事务内多次读必须一致
```

### 选 Serializable

```sql
-- 金融交易
-- 库存扣减（防超卖）
-- 票务系统
-- 抢购
-- 任何"读 + 写"组合容易冲突的场景
```

## 实战案例

### 案例 1：库存超卖

**问题**：商品库存 1 个，两个用户同时下单，都成功（超卖）。

**修复 1**：Serializable + 应用层 retry

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT stock FROM products WHERE id = 1;  -- 1
UPDATE products SET stock = stock - 1 WHERE id = 1;
-- 第二个事务会 serialization failure，应用重试
COMMIT;
```

**修复 2**：行级锁 + Read Committed

```sql
-- 用 SELECT FOR UPDATE 显式加锁
BEGIN;
SELECT stock FROM products WHERE id = 1 FOR UPDATE;  -- 拿锁
UPDATE products SET stock = stock - 1 WHERE id = 1;
INSERT INTO orders (...) VALUES (...);
COMMIT;  -- 释放锁
```

**修复 3**：原子 UPDATE

```sql
-- 单条原子 SQL
UPDATE products SET stock = stock - 1 
WHERE id = 1 AND stock > 0;
-- 返回 1 行 = 成功，0 行 = 失败（无库存）
```

### 案例 2：报表统计一致性

**问题**：每天 0 点跑报表，10 分钟，期间持续有交易，统计结果不准。

**修复**：Repeatable Read 整个报表

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT ...   -- 全程看到同一个快照
COMMIT;
```

## 监控隔离级别

```sql
-- 1. 看数据库默认
SHOW default_transaction_isolation;

-- 2. 看当前事务
SHOW transaction_isolation;

-- 3. 看是否出现 serialization failure
SELECT datname, conflicts 
FROM pg_stat_database
WHERE datname = current_database();
```

## 一句话总结

> **PG 默认 RC 满足 95% 场景**，RC 不出现脏读但有不可重复读和幻读。**RR 用快照避免不可重复读和幻读**（PG 实际行为）。**金融级强一致用 Serializable + 应用层 retry**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>