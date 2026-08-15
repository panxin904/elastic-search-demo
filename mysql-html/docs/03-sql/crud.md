---
title: CRUD 与 DDL
---

# ✏️ MySQL CRUD 与 DDL

> 日常开发 80% 的 SQL：增删改查、建表改表。看似基础，却藏着无数坑。

## 📝 SELECT 查询

### 基础查询

```sql
-- 全表查询（慎用）
SELECT * FROM users;

-- 指定列（推荐）
SELECT id, name, email FROM users;

-- 条件查询
SELECT * FROM users WHERE age > 18;

-- 多条件
SELECT * FROM users
WHERE age > 18 AND status = 1;

-- IN 查询
SELECT * FROM users WHERE id IN (1, 2, 3, 100);

-- BETWEEN 范围
SELECT * FROM users WHERE age BETWEEN 18 AND 30;

-- LIKE 模糊查询
SELECT * FROM users WHERE name LIKE '张%';        -- 前缀匹配（能用索引）
SELECT * FROM users WHERE name LIKE '%张%';       -- 中间包含（不能用索引 ❌）
```

### ⚠️ 避免 SELECT *

```sql
-- ❌ SELECT * 的危害：
-- 1. 查询不需要的列，浪费 IO
-- 2. 失去覆盖索引优化的机会
-- 3. 表结构变更时代码可能出错

-- ✅ 明确指定需要的列
SELECT id, name, email FROM users WHERE id = 100;
```

### 排序（ORDER BY）

```sql
-- 单字段排序
SELECT * FROM products ORDER BY created_at DESC;

-- 多字段排序（先按 price，再按 id）
SELECT * FROM products ORDER BY price DESC, id ASC;

-- ⚠️ filesort：当排序字段不是索引时，性能差
EXPLAIN SELECT * FROM products ORDER BY name LIMIT 100;
-- Extra: Using filesort ❌

-- ✅ 利用索引排序
SELECT * FROM products ORDER BY created_at DESC LIMIT 100;
-- Extra: NULL 或 Backward index scan ✅
```

### 分页（LIMIT）

```sql
-- 基础分页（深分页性能差）
SELECT id, name FROM products
ORDER BY id LIMIT 20 OFFSET 100;
-- OFFSET 1000000 时扫描 100 万行，丢弃前 100 万

-- ✅ 推荐：基于主键的"游标分页"
SELECT id, name FROM products
WHERE id > 100  -- 上次最后一条的 id
ORDER BY id LIMIT 20;
-- 不管翻多少页，性能都稳定

-- ✅ 推荐：延迟关联（先取 id，再 JOIN 取数据）
SELECT *
FROM products p
INNER JOIN (
  SELECT id FROM products
  WHERE category_id = 1
  ORDER BY created_at DESC
  LIMIT 100000, 20
) AS t ON p.id = t.id;
```

## ✏️ INSERT 插入

```sql
-- 单条插入
INSERT INTO users (name, email, age) VALUES ('张三', 'zhangsan@example.com', 25);

-- 批量插入（性能远高于循环单条）
INSERT INTO users (name, email, age) VALUES
  ('李四', 'lisi@example.com', 30),
  ('王五', 'wangwu@example.com', 28),
  ('赵六', 'zhaoliu@example.com', 35);

-- ⚠️ 批量大小建议：每批 1000-5000 行
-- 过大：单次事务太长，binlog 暴涨
-- 过小：网络往返次数多

-- INSERT IGNORE：忽略冲突（不报错）
INSERT IGNORE INTO users (id, name) VALUES (1, '张三');
-- id=1 已存在时，不报错也不插入

-- ON DUPLICATE KEY UPDATE：存在则更新
INSERT INTO users (id, name, age) VALUES (1, '张三', 26)
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  age = VALUES(age),
  updated_at = NOW();

-- REPLACE INTO：存在则替换（删除 + 插入）
REPLACE INTO users (id, name, age) VALUES (1, '张三', 26);
-- ⚠️ 自增 ID 会变化，可能影响外键
```

### ⚠️ INSERT 性能优化

```sql
-- ✅ 1. 批量插入（不要循环单条）
INSERT INTO t (a, b) VALUES (1, 'x'), (2, 'y'), (3, 'z');

-- ✅ 2. 按主键顺序插入（避免页分裂）
-- 如果主键是自增，顺序就是自增顺序 ✅

-- ✅ 3. 关闭自动提交（大批量时）
SET autocommit = 0;
INSERT INTO t VALUES (...), (...), (...);
COMMIT;
SET autocommit = 1;

-- ✅ 4. 用 LOAD DATA 导入大量数据（最快）
LOAD DATA INFILE '/path/to/data.csv'
INTO TABLE users
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n';

-- ❌ 5. 避免使用触发器（在 INSERT 时触发其他操作）
-- 触发器严重拖慢写入
```

## ✏️ UPDATE 更新

```sql
-- 基础更新
UPDATE users SET name = '张三丰', updated_at = NOW()
WHERE id = 100;

-- ⚠️ UPDATE 必须带 WHERE！否则更新全表
-- ❌ UPDATE users SET status = 1;  -- 危险！

-- 多字段更新
UPDATE products
SET price = price * 0.9,
    updated_at = NOW()
WHERE category_id = 1 AND stock > 0;

-- UPDATE JOIN（关联更新）
UPDATE products p
INNER JOIN categories c ON p.category_id = c.id
SET p.status = 0  -- 下架
WHERE c.name = '已淘汰分类';

-- UPDATE 排序（MySQL 不支持 LIMIT OFFSET，但支持 LIMIT）
UPDATE products SET status = 0
ORDER BY created_at ASC
LIMIT 100;  -- 只下架最早的 100 个
```

### ⚠️ UPDATE 性能陷阱

```sql
-- ❌ 1. 修改了索引字段（导致索引重建）
UPDATE users SET email = 'new@x.com' WHERE id = 100;
-- 二级索引 idx_email 需要更新

-- ✅ 只更新需要的字段

-- ❌ 2. 大批量 UPDATE（产生大量 binlog + 行锁）
UPDATE users SET status = 1;

-- ✅ 分批更新（每批 1000-10000）
UPDATE users SET status = 1 WHERE id BETWEEN 1 AND 1000;
UPDATE users SET status = 1 WHERE id BETWEEN 1001 AND 2000;
-- ...

-- ❌ 3. 锁竞争
-- UPDATE 会加 X 锁，并发 UPDATE 同一行会等待
-- ✅ 尽量按主键更新，避免范围更新
```

## ✏️ DELETE 删除

```sql
-- 基础删除
DELETE FROM users WHERE id = 100;

-- ⚠️ DELETE 必须带 WHERE！
-- ❌ DELETE FROM users;  -- 删全表（用 TRUNCATE 更快）

-- TRUNCATE：清空整表（更快，不可回滚）
TRUNCATE TABLE users;
-- vs DELETE FROM users;
-- TRUNCATE 不写 binlog（部分版本），不触发触发器，速度极快
-- 但无法带 WHERE 条件

-- 软删除（推荐）：加 deleted_at 字段
UPDATE users SET deleted_at = NOW() WHERE id = 100;
-- 查询时加 WHERE deleted_at IS NULL

-- DELETE JOIN（关联删除）
DELETE o
FROM orders o
INNER JOIN users u ON o.user_id = u.id
WHERE u.status = 0;  -- 删除已注销用户的所有订单

-- DELETE LIMIT（防止误删大量数据）
DELETE FROM logs WHERE created_at < '2024-01-01' LIMIT 10000;
```

## 🏗️ DDL：建表改表

### CREATE TABLE

```sql
CREATE TABLE users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  username VARCHAR(50) NOT NULL COMMENT '用户名',
  email VARCHAR(100) NOT NULL COMMENT '邮箱',
  password_hash CHAR(64) CHARACTER SET ascii NOT NULL COMMENT '密码哈希',
  age TINYINT UNSIGNED DEFAULT 0 COMMENT '年龄',
  status TINYINT NOT NULL DEFAULT 1 COMMENT '1=正常 0=禁用',
  bio TEXT COMMENT '个人简介',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (id),
  UNIQUE KEY uk_username (username),
  UNIQUE KEY uk_email (email),
  KEY idx_created (created_at),
  KEY idx_status_created (status, created_at)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET=utf8mb4
  DEFAULT COLLATE=utf8mb4_0900_ai_ci
  COMMENT='用户表';
```

### ALTER TABLE

```sql
-- 添加列
ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER email;

-- 修改列
ALTER TABLE users MODIFY COLUMN phone VARCHAR(30) NOT NULL;

-- 重命名列（MySQL 8.0+）
ALTER TABLE users RENAME COLUMN phone TO mobile;

-- 删除列（⚠️ 不可恢复，会丢失数据）
ALTER TABLE users DROP COLUMN phone;

-- 添加索引
ALTER TABLE users ADD INDEX idx_phone (phone);
ALTER TABLE users ADD UNIQUE INDEX uk_phone (phone);
ALTER TABLE users ADD PRIMARY KEY (id);  -- ⚠️ 如果已有数据可能失败

-- 删除索引
ALTER TABLE users DROP INDEX idx_phone;
-- 或
DROP INDEX idx_phone ON users;

-- 修改表名
ALTER TABLE old_users RENAME TO users;
-- 或
RENAME TABLE old_users TO users;

-- 修改字符集
ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### ⚠️ 大表 ALTER TABLE 的风险

```sql
-- ❌ 直接 ALTER 大表
ALTER TABLE huge_table ADD COLUMN new_col VARCHAR(100);
-- 问题：
-- 1. 锁表（MySQL 5.6 之前）
-- 2. 重建整张表（耗 IO、耗时）
-- 3. 可能撑爆磁盘（需要额外空间）

-- ✅ MySQL 5.6+ 在线 DDL（默认 ALGORITHM=INPLACE）
ALTER TABLE huge_table ADD COLUMN new_col VARCHAR(100), ALGORITHM=INPLACE, LOCK=NONE;
-- ALGORITHM=INPLACE: 不重建表
-- LOCK=NONE: 不阻塞 DML
```

### CREATE INDEX / DROP INDEX

```sql
-- 创建索引
CREATE INDEX idx_phone ON users(phone);
CREATE UNIQUE INDEX uk_phone ON users(phone);
CREATE INDEX idx_combo ON users(status, created_at);

-- 在线创建索引（不锁表）
CREATE INDEX idx_phone ON users(phone) ALGORITHM=INPLACE, LOCK=NONE;

-- 删除索引
DROP INDEX idx_phone ON users;

-- 重建索引（清理碎片）
ALTER TABLE users ENGINE=InnoDB;
-- 或
OPTIMIZE TABLE users;
```

## 🛡️ 事务中的 DDL

```sql
-- ⚠️ MySQL DDL 不会回滚！
BEGIN;
INSERT INTO users (name) VALUES ('test');
ALTER TABLE users ADD COLUMN age INT;  -- ⚠️ 自动提交之前的所有事务！
ROLLBACK;  -- INSERT 回滚了，但 ALTER 已经生效
```

**正确做法：**
- 大 DDL 单独执行，不要放在事务里
- 用 `pt-online-schema-change` 或 `gh-ost` 工具

## 🎯 SQL 编写最佳实践

### ✅ 必须遵守

1. **明确列名**（不用 SELECT *）
2. **UPDATE/DELETE 必须带 WHERE**
3. **批量操作分批次**（1000-5000 行/批）
4. **使用占位符**（Prepared Statement，防止 SQL 注入）
5. **大表 ALTER 用 INPLACE/NONE**

### ❌ 必须避免

1. SELECT *
2. WHERE 中使用函数（破坏索引）
3. ORDER BY RAND()（全表扫描 + 排序）
4. 大 LIMIT OFFSET（深分页慢）
5. 隐式类型转换（破坏索引）
6. 循环单条 INSERT（改用批量）

## 🎯 总结

**CRUD 核心原则：**
- ✅ SELECT 只查需要的列
- ✅ WHERE 一定要带，避免全表操作
- ✅ 批量操作分批次
- ✅ 排序/分页尽量用索引
- ✅ UPDATE 频繁字段需谨慎（索引重建）
- ✅ DELETE 优先考虑软删除
- ✅ DDL 用在线模式（ALGORITHM=INPLACE）

**下一步：** [🔗 JOIN 七种用法](../03-sql/join) — 图解各种 JOIN，写出高效的多表查询