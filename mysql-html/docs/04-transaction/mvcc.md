---
title: MVCC 多版本并发
date: 2026-08-15  # date-auto-injected
---

# 🔄 MVCC 多版本并发控制

> MVCC（Multi-Version Concurrency Control）是 InnoDB 实现**非阻塞读**的核心机制，让读不阻塞写、写不阻塞读。

## 🤔 为什么需要 MVCC？

### 传统锁读的问题

```sql
-- 没有 MVCC 时，读需要加 S 锁
START TRANSACTION;
SELECT * FROM users WHERE id = 1 LOCK IN SHARE MODE;
-- ❌ 读期间其他事务不能修改这一行
-- ❌ 大并发读时严重影响写入性能
```

### MVCC 的解决方案

```
事务 A（读）：                    事务 B（写）：
                                  
START TRANSACTION;                START TRANSACTION;
                                  
SELECT * FROM users WHERE id = 1; 
-- ✅ 读快照，不加锁                UPDATE users SET name='x' WHERE id = 1;
-- 立即返回结果                    -- ✅ 创建新版本
                                  
COMMIT;                           COMMIT;
```

**MVCC 的精髓：读快照（不加锁）+ 写新版本（不阻塞读）**

## 🎯 MVCC 的核心组件

```
InnoDB 存储结构

┌──────────────────────────────────────┐
│           数据行（聚簇索引）           │
│                                      │
│  ┌────────┐  ┌────────┐  ┌────────┐ │
│  │ 行 1   │  │ 行 2   │  │ 行 3   │ │
│  │        │  │ Undo   │  │ Undo   │ │
│  │ DB_TRX_ID│ │ Ptr   │  │ Ptr   │ │
│  │ DB_ROLL_PTR→│ │       │  │       │ │
│  └────────┘  └────────┘  └────────┘ │
└──────────────────────────────────────┘
       │              │           │
       ▼              ▼           ▼
┌──────────────────────────────────────┐
│           Undo Log（回滚日志）         │
│                                      │
│  v1 (初始值)                         │
│   ↑                                  │
│  v2 (第一次修改)                      │
│   ↑                                  │
│  v3 (当前值)                          │
└──────────────────────────────────────┘
```

### 关键字段

每行数据有两个隐藏列：

- `DB_TRX_ID`：最后修改该行的事务 ID
- `DB_ROLL_PTR`：指向 Undo Log 中该行的上一版本

```sql
-- 查看隐藏列（伪行格式：infimum/supremum）
SELECT * FROM information_schema.INNODB_SYS_COLUMNS
WHERE TABLE_ID = (
  SELECT TABLE_ID FROM information_schema.INNODB_SYS_TABLES
  WHERE NAME = 'mydb/users'
);
```

![MySQL MVCC 与 Undo Log 原理](/mysql-mvcc-undo-log.svg)

## 🔄 Undo Log 版本链

每次 UPDATE/DELETE 都生成一个 Undo Log 记录，形成版本链：

```
初始状态：name='张三'
   │
   ▼ UPDATE by T1 (TRX_ID=10)
name='张三' (old) → Undo Log v1: name='李四'
   │
   ▼ UPDATE by T2 (TRX_ID=20)
name='李四' (old) → Undo Log v2: name='王五'
   │
   ▼ 当前行：name='王五', DB_TRX_ID=20
```

```
Undo Log 链：
v2 ← v1 ← 初始
```

## 📸 Read View（读视图）

### 什么是 Read View？

事务启动时，InnoDB 为它生成一个**一致性快照（Read View）**，记录：
- `m_ids`：当前活跃的事务 ID 列表
- `min_trx_id`：最小活跃事务 ID
- `max_trx_id`：下一个要分配的事务 ID
- `creator_trx_id`：创建该 Read View 的事务 ID

```sql
-- 查看当前活跃事务
SELECT * FROM information_schema.innodb_trx;
```

### Read View 判断规则

对于一行数据（`DB_TRX_ID`）：

```
if (DB_TRX_ID == creator_trx_id)
  → 是自己改的，可见 ✅
else if (DB_TRX_ID < min_trx_id)
  → 修改已提交，可见 ✅
else if (DB_TRX_ID in m_ids)
  → 修改未提交，不可见 ❌（读 Undo Log 旧版本）
else
  → 修改已提交（在 Read View 创建之后），可见 ✅
```

### 流程图

```
读取一行数据：
1. 获取该行的 DB_TRX_ID
2. 与 Read View 比较
3. 如果可见 → 返回当前值
4. 如果不可见 → 沿着 Undo Log 链找上一版本，重复比较
5. 直到找到可见的版本，或到 Undo Log 起点
```

## 🎯 不同隔离级别的 MVCC 行为

### READ COMMITTED（每次读都创建 Read View）

```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

START TRANSACTION;
-- 第 1 次读：创建 Read View v1
SELECT * FROM users WHERE id = 1;  -- 读快照 v1

-- 此时其他事务提交了修改
COMMIT;  -- T2 提交修改 name='x'

-- 第 2 次读：创建新的 Read View v2（看到 T2 的提交）
SELECT * FROM users WHERE id = 1;  -- 读最新值 'x'（不可重复读）

COMMIT;
```

### REPEATABLE READ（事务开始时创建 Read View）

```sql
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;

START TRANSACTION;
-- 创建 Read View（事务级，整个事务复用）

-- 第 1 次读
SELECT * FROM users WHERE id = 1;  -- 读快照

-- T2 提交修改（不影响 T1 的 Read View）

-- 第 2 次读：还是用同一个 Read View
SELECT * FROM users WHERE id = 1;  -- 读快照（值不变，可重复读）

COMMIT;
```

## 🔍 实战：MVCC 是如何工作的？

### 场景：可重复读（MySQL 默认）

```sql
-- 数据：users.id=1, name='张三'
-- 当前活跃事务：T1 (本事务), T2 (其他事务，TRX_ID=100)

-- 时间线：
-- 1. T1 START TRANSACTION;  -- 创建 Read View: m_ids=[T1, T2], min=100, max=102

-- 2. T2: UPDATE users SET name = '李四' WHERE id = 1;
--    行变为 name='李四', DB_TRX_ID=100, Undo: name='张三'

-- 3. T1: SELECT * FROM users WHERE id = 1;
--    DB_TRX_ID=100 在 m_ids 中（未提交）→ 不可见
--    沿 Undo Log 找上一版本 → name='张三'（可见）

-- 4. T2: COMMIT;  -- T2 从 m_ids 中移除

-- 5. T1: SELECT * FROM users WHERE id = 1;
--    仍然是同一个 Read View（m_ids 还是创建时的）
--    T2 仍然在 m_ids 中（Read View 创建时 T2 在）→ 不可见
--    返回 name='张三'（可重复读！）

-- 6. T1: COMMIT;
```

**关键点：Read View 在第一次读时创建，整个事务复用。**

## 🎯 MVCC 解决了哪些问题？

| 问题 | MVCC 解决方案 |
|---|---|
| 脏读 | 不可见未提交的版本 |
| 不可重复读 | REPEATABLE READ 下 Read View 不变 |
| 幻读（快照读） | REPEATABLE READ 下范围读也是快照 |
| 读阻塞写 | 读不加锁，写不阻塞 |

**注意：** 幻读在**当前读**（FOR UPDATE）下仍可能发生，需要临键锁解决。

## 🔄 当前读 vs 快照读

### 快照读（普通 SELECT）

```sql
-- 快照读：读 MVCC 快照，不加锁
SELECT * FROM users WHERE id = 1;
```

### 当前读（加锁 SELECT / INSERT / UPDATE / DELETE）

```sql
-- 当前读：读最新版本，加锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;
SELECT * FROM users WHERE id = 1 LOCK IN SHARE MODE;
SELECT * FROM users WHERE id = 1 FOR SHARE;  -- 8.0

-- DML 都是当前读
INSERT INTO users ...;     -- 加 X 锁 + 插入意向锁
UPDATE users SET ...;       -- 加 X 锁
DELETE FROM users WHERE ...; -- 加 X 锁
```

### 当前读 + MVCC

```sql
-- 当前读：忽略 Read View，直接读最新版本
START TRANSACTION;
SELECT * FROM users WHERE id = 1;       -- 快照读：用 Read View
SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- 当前读：读最新值
```

## 🔍 Undo Log 的清理

### Undo Log 会无限增长吗？

不会！InnoDB 有自动清理机制：

```sql
-- 控制 Undo 保留时间（默认 0 = 不强制）
SHOW VARIABLES LIKE 'innodb_max_undo_log_size';

-- 控制清理线程数量
SHOW VARIABLES LIKE 'innodb_purge_threads';
-- 默认 4，并行清理

-- 何时清理？
-- 当没有事务需要这个 Undo Log 时（所有 Read View 都已经结束）
```

### Undo Log 类型

```sql
-- 查看 Undo Log 配置
SHOW VARIABLES LIKE 'innodb_undo%';
-- innodb_undo_tablespaces: Undo 表空间数量
-- innodb_undo_directory: Undo 文件目录
-- innodb_rollback_segments: 回滚段数量
```

## 🎯 MVCC 在不同操作中的作用

```sql
-- 1. SELECT（快照读）
-- 读 MVCC 快照，不加锁
SELECT * FROM users WHERE id = 1;

-- 2. SELECT ... FOR UPDATE（当前读）
-- 读最新版本 + 加 X 锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;

-- 3. UPDATE
-- 先当前读找到最新数据
-- 然后：
--   a) 加 X 锁
--   b) 生成 Undo Log（旧版本）
--   c) 写入新数据（DB_TRX_ID = 当前事务）
UPDATE users SET name = 'x' WHERE id = 1;

-- 4. INSERT
-- 加 X 锁
-- 直接插入（没有旧版本，无需 Undo Log）
INSERT INTO users (id, name) VALUES (2, '李四');

-- 5. DELETE
-- 当前读 + 加 X 锁
-- 不立即删除，而是标记为删除（"墓碑"标记）
-- 由 purge 线程后续清理
DELETE FROM users WHERE id = 1;
```

## 📊 MVCC 的局限性

```sql
-- MVCC 不能解决：
-- 1. 当前读的幻读 → 需要临键锁
-- 2. 死锁 → 需要应用层处理
-- 3. 大事务导致的 Undo Log 膨胀 → 需要拆分事务
-- 4. 长事务导致的历史版本保留 → 需要避免长事务
```

## 🎯 总结

**MVCC 三要素：**
- **Undo Log**：保存数据的历史版本
- **DB_TRX_ID**：标记行最后被哪个事务修改
- **Read View**：事务的快照，决定能看到哪些版本

**MVCC 工作流程：**
- 读时：对比 DB_TRX_ID 与 Read View，可见则返回，否则沿 Undo Log 找旧版本
- 写时：加 X 锁 + 生成 Undo Log + 写入新版本

**MVCC 解决的并发问题：**
- ✅ 脏读
- ✅ 不可重复读
- ✅ 幻读（快照读）
- ✅ 读不阻塞写

**下一步：** [📊 EXPLAIN 解读](../05-optimization/explain) — 进入性能调优的世界

<!-- svg-injected:do-not-edit -->

![mvcc flow](/mvcc-flow.svg)
