---
title: 字符集与排序规则
date: 2026-08-15  # date-auto-injected
---

# 🌐 字符集与排序规则

> 一个 `utf8` 字符集的选择，藏着 **表情符号存不进**、**索引失效**、**性能差 3 倍** 的坑。

## 📚 基础概念

### 字符集（Charset）

字符集定义了**字符到二进制字节的映射规则**。

```sql
-- 查看 MySQL 支持的字符集
SHOW CHARACTER SET;
-- 常用：utf8mb4、utf8、latin1、binary、ascii
```

### 排序规则（Collation）

排序规则定义了**字符如何比较和排序**。

```sql
-- 查看每种字符集的排序规则
SHOW COLLATION LIKE 'utf8mb4%';
-- utf8mb4_0900_ai_ci    - MySQL 8.0 默认（推荐）
-- utf8mb4_unicode_ci    - Unicode 标准
-- utf8mb4_bin           - 区分大小写（二进制比较）
-- utf8mb4_general_ci    - 旧版，不推荐
```

**命名规则：**
- `_ci`：case-insensitive（不区分大小写）
- `_cs`：case-sensitive（区分大小写）
- `_bin`：binary（二进制比较）
- `_ai`：accent-insensitive（不区分重音）
- `_0900`：基于 Unicode 9.0

## ⚠️ utf8 ≠ utf8mb4：最大的坑

MySQL 的 `utf8` **不是真正的 UTF-8**！

| 字符集 | 最大字节 | 支持字符 |
|---|---|---|
| `utf8`（MySQL "假 utf8"） | **3 字节** | BMP 平面（基本多文种平面） |
| `utf8mb4`（真 UTF-8） | **4 字节** | 所有 Unicode，包括 emoji 😀 |

```sql
-- ❌ 用 utf8 存 emoji 会报错
CREATE TABLE wrong (
  name VARCHAR(50) CHARACTER SET utf8
);
INSERT INTO wrong VALUES ('😀 你好');
-- ERROR 1366 (HY000): Incorrect string value

-- ✅ 用 utf8mb4
CREATE TABLE correct (
  name VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci
);
INSERT INTO correct VALUES ('😀 你好 🎉');
-- 成功
```

**为什么 MySQL "假 utf8"只支持 3 字节？**
因为 MySQL 早期作者误以为 UTF-8 最多 3 字节（实际是 1-6 字节）。后来加了 `utf8mb4`（most bytes 4）作为补充，但不敢改 `utf8` 名字以免破坏兼容性。

## 🎯 字符集和排序规则的选择

### 数据库级

```sql
-- 创建数据库时指定
CREATE DATABASE mydb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

-- 修改已存在数据库
ALTER DATABASE mydb
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
```

### 表级

```sql
CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(100)
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

### 列级

```sql
CREATE TABLE mixed (
  id INT,
  username VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin,  -- 二进制比较（区分大小写）
  email VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci  -- 不区分大小写
);
```

### 服务端级（推荐）

```ini
# my.cnf
[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_0900_ai_ci

[mysql]
default-character-set = utf8mb4

[client]
default-character-set = utf8mb4
```

```sql
-- 查看当前设置
SHOW VARIABLES LIKE 'character%';
SHOW VARIABLES LIKE 'collation%';
```

## 📊 各排序规则对比

### utf8mb4_0900_ai_ci（MySQL 8.0 默认）

```sql
-- 特点
-- 不区分大小写（ci）
-- 不区分重音符号（ai）：a = á = À
-- 性能好（有 Unicode 9.0 优化）
-- 适合：大部分业务
```

### utf8mb4_unicode_ci

```sql
-- 特点
-- 不区分大小写（ci）
-- 不区分重音（但比 0900 更复杂的 Unicode 算法）
-- 准确度更高（符合 Unicode 标准）
-- 性能略低于 0900
-- 适合：需要更准确排序的多语言场景
```

### utf8mb4_bin

```sql
-- 特点
-- 区分大小写（A ≠ a）
-- 区分重音（á ≠ a）
-- 二进制比较，速度最快
-- 适合：密码、token、哈希存储
```

### utf8mb4_general_ci（不推荐）

```sql
-- 特点
-- MySQL 5.7 之前的默认
-- 不是基于 Unicode 标准，排序可能不符合预期
-- 某些字符排序不正确（如 ä = a 在某些场景）
-- ❌ 已过时，新项目不要用
```

## 🔍 字符集与排序规则的继承

```
服务器级（character-set-server）
  ↓ 继承
数据库级（创建时指定）
  ↓ 继承
表级（创建时指定）
  ↓ 继承
列级（创建时指定）

客户端连接字符集（character_set_client）
  ↓ 影响
实际查询和写入
```

```sql
-- 查看某列的字符集和排序规则
SHOW FULL COLUMNS FROM users;
-- Field | Type | Collation | Null | Key | Default | Extra | Privileges | Comment
-- name  | varchar(100) | utf8mb4_unicode_ci | YES | | NULL | | | 

-- 查看表的创建语句（能看到所有继承）
SHOW CREATE TABLE users\G
```

## ⚠️ 字符集不匹配导致的索引失效

```sql
-- 表用 utf8mb4_unicode_ci（不区分大小写）
CREATE TABLE users (
  name VARCHAR(50) COLLATE utf8mb4_unicode_ci
);

-- 查询时用了 utf8mb4_bin（区分大小写）
SELECT * FROM users WHERE name = 'ZhangSan' COLLATE utf8mb4_bin;
-- 索引失效！全表扫描

-- ✅ 使用相同的排序规则
SELECT * FROM users WHERE name = 'ZhangSan';
```

## 🔧 字符集相关的常见问题

### 1. 客户端连接字符集

```sql
-- 查看当前连接的字符集
SHOW VARIABLES LIKE 'character_set_client';
SHOW VARIABLES LIKE 'character_set_results';

-- 设置当前连接的字符集
SET NAMES utf8mb4;
-- 等价于：
SET character_set_client = utf8mb4;
SET character_set_results = utf8mb4;
SET character_set_connection = utf8mb4;
```

### 2. JDBC 连接字符串

```properties
# application.properties（Spring Boot）
spring.datasource.url=jdbc:mysql://localhost:3306/mydb?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai
# characterEncoding=utf8 实际就是 utf8mb4（MySQL Connector/J 做了兼容）
```

### 3. 数据迁移时的字符集问题

```bash
# mysqldump 导出
mysqldump --default-character-set=utf8mb4 mydb > dump.sql

# 导入
mysql --default-character-set=utf8mb4 mydb < dump.sql
```

### 4. 不同字符集的 JOIN

```sql
-- 两个表不同字符集
CREATE TABLE t1 (name VARCHAR(50) CHARACTER SET utf8mb4) ENGINE=InnoDB;
CREATE TABLE t2 (name VARCHAR(50) CHARACTER SET gbk) ENGINE=InnoDB;

-- JOIN 会报错或隐式转换
SELECT * FROM t1 JOIN t2 ON t1.name = t2.name;
-- ERROR 1267 (HY000): Illegal mix of collations

-- ✅ 统一字符集
SELECT * FROM t1 JOIN t2 ON t1.name = t2.name COLLATE utf8mb4_unicode_ci;
```

## 📋 排序规则的性能影响

```sql
-- 查看表的排序规则
SELECT
  table_name,
  table_collation
FROM information_schema.tables
WHERE table_schema = DATABASE();

-- 查看每列的排序规则
SELECT
  table_name,
  column_name,
  collation_name
FROM information_schema.columns
WHERE table_schema = DATABASE()
  AND collation_name IS NOT NULL;
```

**性能对比（一般情况）：**
- `utf8mb4_bin` > `utf8mb4_0900_ai_ci` > `utf8mb4_unicode_ci` > `utf8mb4_general_ci`
- 但 `_bin` 会区分大小写，业务上要确认需求

## 🎯 推荐配置

### 服务端配置（my.cnf）

```ini
[mysqld]
character-set-server = utf8mb4
collation-server = utf8mb4_0900_ai_ci
init-connect = 'SET NAMES utf8mb4'

[client]
default-character-set = utf8mb4

[mysql]
default-character-set = utf8mb4
```

### 数据库 / 表

```sql
-- 创建数据库
CREATE DATABASE mydb
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

-- 创建表（明确指定，养成习惯）
CREATE TABLE users (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  password_hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin,  -- 密码哈希用 ascii
  bio VARCHAR(500),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;
```

### 特殊字段

```sql
-- 用户名、邮箱：区分大小写（推荐 bin）
username VARCHAR(50) COLLATE utf8mb4_bin,

-- 昵称、标题：不区分大小写
nickname VARCHAR(50) COLLATE utf8mb4_unicode_ci,

-- 密码哈希、token：ASCII
api_token CHAR(32) CHARACTER SET ascii COLLATE ascii_bin,

-- URL：ASCII
url VARCHAR(2000) CHARACTER SET ascii COLLATE ascii_bin,
```

## ✅ 验证字符集正确

```sql
-- 1. 查看最终生效的字符集
SHOW VARIABLES LIKE 'character_set_server';
SHOW VARIABLES LIKE 'collation_server';

-- 2. 测试中文 / emoji
CREATE TABLE charset_test (
  id INT PRIMARY KEY,
  emoji VARCHAR(50)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

INSERT INTO charset_test VALUES
(1, '🎉 中文测试 emoji 😀'),
(2, '日本語テスト'),
(3, '한국어 테스트');

SELECT * FROM charset_test;
-- 应该能正确显示所有字符

-- 3. 测试排序
SELECT * FROM charset_test ORDER BY emoji;
```

## 🎯 总结

| 场景 | 推荐 |
|---|---|
| **默认配置** | `utf8mb4` + `utf8mb4_0900_ai_ci` |
| **用户名/邮箱** | `utf8mb4_bin`（区分大小写） |
| **密码/token** | `ascii` + `ascii_bin` |
| **昵称/标题** | `utf8mb4_unicode_ci` |
| **emoji 必须支持** | 必须用 `utf8mb4`（不能用 `utf8`） |

**下一步：** [🌲 B+Tree 索引原理](../02-index/btree) — 进入索引的世界，理解为什么索引这么快