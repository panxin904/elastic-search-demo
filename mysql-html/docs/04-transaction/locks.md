---
title: InnoDB 锁机制
---

# 🔐 InnoDB 锁机制

> 理解 InnoDB 的锁机制，是排查并发问题和性能调优的基础。

## 🎯 锁的分类

### 按粒度分类

```
InnoDB 锁粒度
├── 表锁
│   ├── 意向锁 (IS / IX)
│   └── 自增锁 (AUTO-INC)
└── 行锁 (InnoDB 的核心)
    ├── 共享锁 (S Lock)
    ├── 排他锁 (X Lock)
    └── 间隙锁 / 临键锁 (Gap / Next-Key)
```

### 按模式分类

- **共享锁（S Lock）**：允许多个事务同时持有（读读兼容）
- **排他锁（X Lock）**：只允许一个事务持有（其他事务阻塞）

### 兼容性矩阵

| | S Lock | X Lock |
|---|---|---|
| **S Lock** | ✅ 兼容 | ❌ 阻塞 |
| **X Lock** | ❌ 阻塞 | ❌ 阻塞 |

## 🔒 行锁（Record Lock）

### 共享锁（S Lock）

```sql
-- 加共享锁
SELECT * FROM users WHERE id = 1 LOCK IN SHARE MODE;
-- 8.0+ 推荐写法
SELECT * FROM users WHERE id = 1 FOR SHARE;

-- 特点：
-- ✅ 多个事务可同时加 S 锁（读读不阻塞）
-- ❌ 加 S 锁后不能修改（UPDATE/DELETE 会阻塞）
-- ❌ S 锁与 X 锁互斥
```

### 排他锁（X Lock）

```sql
-- 加排他锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;
-- 等价于：UPDATE users SET name = 'x' WHERE id = 1;

-- 特点：
-- ✅ 加 X 锁后可以安全修改
-- ❌ 其他事务的 S/X 锁都被阻塞
```

### 实战对比

```sql
-- 时间线：
-- T1: SELECT * FROM users WHERE id = 1 FOR SHARE;  -- S 锁
-- T2: SELECT * FROM users WHERE id = 1 FOR SHARE;  -- ✅ 不阻塞（S+S 兼容）
-- T3: UPDATE users SET name = 'x' WHERE id = 1;    -- ❌ 阻塞（S+X 冲突）

-- T1: SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- X 锁
-- T2: SELECT * FROM users WHERE id = 1 FOR SHARE;  -- ❌ 阻塞（X+S 冲突）
-- T3: UPDATE users SET name = 'y' WHERE id = 1;    -- ❌ 阻塞（X+X 冲突）
```

## 🌌 间隙锁（Gap Lock）与临键锁（Next-Key Lock）

### 为什么需要间隙锁？

```sql
-- 表 data 只有 3 条记录：id = 10, 20, 30
SELECT * FROM data WHERE id BETWEEN 10 AND 20;

-- 没有间隙锁时，并发插入会导致幻读：
-- T1: SELECT id BETWEEN 10 AND 20  → 返回 10, 20
-- T2: INSERT id = 15                → 成功
-- T1: SELECT id BETWEEN 10 AND 20  → 多了 15（幻读！）
```

### 间隙锁的工作原理

```sql
-- REPEATABLE READ + 范围查询时，InnoDB 会加间隙锁
-- 锁住"记录之间的间隙"，防止插入

-- 表 data: id = 10, 20, 30
-- 查询 WHERE id BETWEEN 15 AND 25
-- 间隙锁范围：(10, 20] (20, 30)
-- 即：id 在 10-20 之间、20-30 之间的所有插入都被阻塞
```

### 临键锁（Next-Key Lock）

```sql
-- 临键锁 = 记录锁 + 间隙锁
-- 锁住当前记录 + 前面的间隙

-- 表 data: id = 10, 20, 30
-- 查询 WHERE id = 20
-- 临键锁：(10, 20]
-- 即：id=20 的记录 + (10, 20) 之间的间隙
```

### 间隙锁可能导致的问题

```sql
-- ❌ 业务上不需要间隙锁，但 InnoDB 默认会加

-- 例如：插入新数据可能被阻塞
-- T1: SELECT * FROM data WHERE id < 20 FOR UPDATE;
-- T2: INSERT INTO data (id) VALUES (15);  -- 被 T1 的间隙锁阻塞！
```

### 关闭间隙锁

```sql
-- READ COMMITTED 隔离级别下没有间隙锁
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- 或启用 innodb_locks_unsafe_for_binlog（已废弃）
```

## 🎯 意向锁（Intention Lock）

### 为什么需要意向锁？

```sql
-- 表 users 有 100 万行
-- T1: SELECT * FROM users WHERE id = 1 FOR UPDATE;  -- 加 X 行锁
-- T2: ALTER TABLE users ADD COLUMN new_col INT;     -- 需要表锁

-- 问题：T2 在加表锁前，需要检查是否有行锁
-- 但遍历 100 万行检查行锁太慢了！

-- 解决：意向锁（表级锁）
-- 事务加行锁前，先加一个表级意向锁
-- T2 看到意向锁就知道有行锁存在，直接阻塞
```

### 意向锁类型

| 锁 | 用途 | 兼容性 |
|---|---|---|
| IS（意向共享锁） | 事务打算加 S 行锁 | 与 S 兼容，与 IX 阻塞 |
| IX（意向排他锁） | 事务打算加 X 行锁 | 与所有意向锁兼容 |

## 🔍 锁的监控

### 查看当前锁

```sql
-- 8.0+ 推荐：performance_schema
SELECT * FROM performance_schema.data_locks LIMIT 10;
SELECT * FROM performance_schema.data_lock_waits LIMIT 10;

-- 查看谁在阻塞谁
SELECT
  blocking_pid AS '阻塞者线程',
  waiting_pid  AS '等待者线程',
  waiting_query AS '等待 SQL'
FROM performance_schema.events_statements_history
WHERE waiting_pid IS NOT NULL;
```

### 锁等待超时

```sql
-- 设置锁等待超时（默认 50 秒）
SET SESSION innodb_lock_wait_timeout = 10;

-- 超时后报错
-- ERROR 1205 (HY000): Lock wait timeout exceeded; try restarting transaction
```

### 查看锁争用

```sql
-- 查看行锁等待统计
SHOW STATUS LIKE 'Innodb_row_lock%';
-- Innodb_row_lock_current_waits  = 当前等待数
-- Innodb_row_lock_time           = 总等待时间（毫秒）
-- Innodb_row_lock_waits          = 等待总次数

-- 查看表锁争用
SHOW STATUS LIKE 'Table_locks%';
```

## 🔒 SELECT ... FOR UPDATE 加锁规则

### 唯一索引等值查询

```sql
-- 主键等值（记录存在）
SELECT * FROM users WHERE id = 1 FOR UPDATE;
-- 加 X 记录锁（只锁 id=1 这一行）

-- 主键等值（记录不存在）
SELECT * FROM users WHERE id = 999 FOR UPDATE;
-- 加间隙锁（防止幻读）
```

### 唯一索引范围查询

```sql
-- 主键范围
SELECT * FROM users WHERE id BETWEEN 10 AND 20 FOR UPDATE;
-- 加临键锁：(负无穷, 10] (10, 20] (20, +无穷)

-- 防止范围内插入新数据
INSERT INTO users (id) VALUES (15);  -- 被阻塞
```

### 非唯一索引

```sql
-- 非唯一索引等值
CREATE INDEX idx_age ON users(age);
SELECT * FROM users WHERE age = 25 FOR UPDATE;
-- 加临键锁：(20, 25] (25, 30)
-- 即：所有 age=25 的记录 + 前后间隙

-- 非唯一索引范围
SELECT * FROM users WHERE age > 20 FOR UPDATE;
-- 加临键锁：(最大 age, +无穷)
```

### 普通字段（无索引）

```sql
-- 全表扫描
SELECT * FROM users WHERE name = '张三' FOR UPDATE;
-- ⚠️ 没有索引！会全表扫描 + 全表加锁
-- 等价于表锁

-- ✅ 加索引
CREATE INDEX idx_name ON users(name);
```

## 🔐 INSERT 加锁机制

```sql
-- INSERT 加隐式锁（行锁的变种）
INSERT INTO users (name) VALUES ('张三');

-- 特点：
-- 1. 加的是隐式 X 锁（不被 performance_schema 显示）
-- 2. INSERT 前会设置插入意向锁
-- 3. 可能等待间隙锁（如果目标位置被锁）
```

### INSERT 阻塞场景

```sql
-- T1: SELECT * FROM users WHERE id BETWEEN 10 AND 20 FOR UPDATE;
-- T2: INSERT INTO users (id) VALUES (15);
-- T2 会被阻塞（T1 的间隙锁阻止插入）

-- T2 等待直到 T1 提交或回滚
```

## 🛠️ 锁优化实战

### 1. 避免无索引导致的锁升级

```sql
-- ❌ 无索引：行锁变表锁
UPDATE users SET name = 'x' WHERE name = '张三';
-- 全表扫描 + 全表锁

-- ✅ 加索引：精确锁
CREATE INDEX idx_name ON users(name);
UPDATE users SET name = 'x' WHERE name = '张三';
-- 只锁 name='张三' 的行
```

### 2. 控制事务大小

```sql
-- ❌ 大事务
START TRANSACTION;
UPDATE t1 SET ... WHERE ...;  -- 100 万行
UPDATE t2 SET ... WHERE ...;  -- 100 万行
UPDATE t3 SET ... WHERE ...;  -- 100 万行
COMMIT;

-- ✅ 分批小事务
UPDATE t1 SET ... WHERE id BETWEEN 1 AND 1000;
UPDATE t1 SET ... WHERE id BETWEEN 1001 AND 2000;
```

### 3. 固定访问顺序避免死锁

```sql
-- ❌ 反向访问可能死锁
-- T1: UPDATE a WHERE id = 1; UPDATE b WHERE id = 1;
-- T2: UPDATE b WHERE id = 1; UPDATE a WHERE id = 1;  -- 死锁！

-- ✅ 固定顺序
-- 总是先 id 小的，再 id 大的
START TRANSACTION;
UPDATE a WHERE id = 1;
UPDATE b WHERE id = 1;
COMMIT;
```

### 4. 用 SKIP LOCKED 处理队列

```sql
-- MySQL 8.0+: SKIP LOCKED 跳过已锁定的行
-- 任务队列场景：多个 worker 并发处理任务

-- 创建任务表
CREATE TABLE task_queue (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  status TINYINT DEFAULT 0,  -- 0=待处理, 1=处理中, 2=完成
  payload JSON
);

-- Worker 处理任务（跳过别人正在处理的）
START TRANSACTION;
SELECT * FROM task_queue
WHERE status = 0
ORDER BY id
LIMIT 1
FOR UPDATE SKIP LOCKED;
-- 拿到一个没人处理的任务

UPDATE task_queue SET status = 1 WHERE id = ?;
COMMIT;
```

## 🎯 总结

**InnoDB 锁核心：**
- 行锁：S 锁（共享）、X 锁（排他）
- 表锁：意向锁（IS/IX）、自增锁
- 间隙锁 + 临键锁：解决幻读

**加锁规则：**
- 唯一索引等值：精确行锁
- 唯一索引范围：临键锁
- 非唯一索引：临键锁（更大范围）
- 全表扫描：全表锁（最差）

**优化原则：**
- ✅ 索引避免锁升级
- ✅ 事务尽量小
- ✅ 固定访问顺序避免死锁
- ✅ READ COMMITTED 减少间隙锁
- ✅ SKIP LOCKED 处理队列

**下一步：** [💀 死锁分析与排查](../04-transaction/deadlock) — 实战死锁日志解读