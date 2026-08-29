---
title: SQL 速查表
date: 2026-08-15  # date-auto-injected
---

# 📋 MySQL SQL 速查表

> 30+ 常用 SQL 模板，**支持搜索 + 一键复制**。覆盖 CRUD / DDL / 查询 / 聚合 / JOIN / 索引 / 事务 / 性能 / 运维 9 大类。

<SqlCheatsheet />

## 🎯 常用 SQL 速查（直接复制使用）

### 创建数据库

```sql
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mydb;
```

### 用户权限

```sql
-- 创建用户
CREATE USER 'appuser'@'%' IDENTIFIED BY 'StrongPassword!';

-- 授权
GRANT SELECT, INSERT, UPDATE, DELETE ON mydb.* TO 'appuser'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' WITH GRANT OPTION;

-- 刷新权限
FLUSH PRIVILEGES;

-- 查看权限
SHOW GRANTS FOR 'appuser'@'%';
```

### 查看数据库状态

```sql
-- 查看所有数据库
SHOW DATABASES;

-- 查看所有表
SHOW TABLES;

-- 查看表结构
DESC table_name;
SHOW CREATE TABLE table_name;

-- 查看表大小
SELECT
  table_name,
  ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = DATABASE();
```

### 日期时间函数

```sql
SELECT
  NOW(),                  -- 当前时间
  CURDATE(),              -- 当前日期
  CURTIME(),              -- 当前时间
  DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s'),
  DATE_ADD(NOW(), INTERVAL 7 DAY),
  DATEDIFF('2025-12-31', '2025-01-01'),
  UNIX_TIMESTAMP(),       -- 时间戳
  FROM_UNIXTIME(1700000000),
  YEAR(NOW()), MONTH(NOW()), DAY(NOW()),
  DATE(created_at),        -- 取日期部分
  TIME(created_at)         -- 取时间部分
;
```

### 字符串函数

```sql
SELECT
  CONCAT('a', '-', 'b'),         -- 拼接
  SUBSTRING('hello', 2, 3),     -- 截取 'ell'
  LENGTH('hello'),                -- 字节长度
  CHAR_LENGTH('hello'),          -- 字符长度
  UPPER('hello'), LOWER('HELLO'),
  TRIM('  hello  '),              -- 去空格
  REPLACE('hello', 'l', 'L'),
  REVERSE('hello'),
  LOCATE('world', 'hello world'), -- 查找位置
  LPAD('1', 3, '0'),             -- 左填充 → '001'
  RPAD('1', 3, '0')              -- 右填充 → '100'
;
```

## 🛢️ 在线 SQL Playground

打开 [🛢️ SQL Playground](../cheatsheet) 直接写 SQL，模拟执行结果 + EXPLAIN 解读。

## 🔗 关联工具

- **[💻 mysql client](../11-tools/mysql-client)** — 命令行运维
- **[🔧 pt-toolkit](../11-tools/pt-toolkit)** — Percona 神器