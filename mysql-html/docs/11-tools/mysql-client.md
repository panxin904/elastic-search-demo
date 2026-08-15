---
title: mysql client 命令
---

# 💻 MySQL mysql client 命令

> mysql client 是 MySQL 自带的命令行工具，DBA 必备。掌握这些命令能让你**高效完成 90% 的日常运维**。

## 🚀 连接 MySQL

### 基本连接

```bash
# 本地连接
mysql -u root -p

# 指定主机和端口
mysql -h 192.168.1.10 -P 3306 -u root -p

# 指定数据库
mysql -h 192.168.1.10 -P 3306 -u root -p mydb

# 执行单条命令
mysql -u root -p -e "SELECT VERSION();"

# 执行 SQL 文件
mysql -u root -p mydb < backup.sql

# 静默模式（不显示列名）
mysql -u root -p -ss -e "SELECT * FROM users LIMIT 5;"
```

### 连接选项

```bash
# 指定字符集
mysql --default-character-set=utf8mb4

# 压缩传输
mysql --compress

# 超时
mysql --connect-timeout=10

# 启用自动提交
mysql --skip-auto-rehash  # 关闭自动补全（启动更快）
```

## ⌨️ 常用命令

### 数据库操作

```sql
-- 查看所有数据库
SHOW DATABASES;

-- 切换数据库
USE mydb;

-- 查看当前数据库
SELECT DATABASE();

-- 创建数据库
CREATE DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 删除数据库
DROP DATABASE mydb;

-- 修改数据库字符集
ALTER DATABASE mydb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 表操作

```sql
-- 查看所有表
SHOW TABLES;

-- 查看表结构
DESC users;
DESCRIBE users;
EXPLAIN users;  -- 三者效果一样

-- 查看建表 SQL
SHOW CREATE TABLE users\G

-- 查看表状态
SHOW TABLE STATUS LIKE 'users'\G

-- 查看表的索引
SHOW INDEX FROM users;
SHOW KEYS FROM users;
```

### 数据操作

```sql
-- 查询
SELECT * FROM users LIMIT 10;

-- 插入
INSERT INTO users (name, email) VALUES ('张三', 'zhangsan@x.com');

-- 更新
UPDATE users SET name = '李四' WHERE id = 1;

-- 删除
DELETE FROM users WHERE id = 1;
```

## 🔧 运维必备命令

### 1. 查看进程

```sql
-- 查看所有连接
SHOW PROCESSLIST;

-- 查看完整 SQL
SHOW FULL PROCESSLIST;

-- 过滤活跃查询
SELECT * FROM information_schema.PROCESSLIST
WHERE COMMAND != 'Sleep'
ORDER BY TIME DESC;
```

### 2. 杀死慢查询

```sql
-- 查找慢查询
SELECT id, user, host, db, command, time, state, LEFT(info, 100) AS query
FROM information_schema.PROCESSLIST
WHERE COMMAND != 'Sleep' AND TIME > 5
ORDER BY TIME DESC;

-- 杀死进程
KILL 12345;

-- 杀查询（不断连接）
KILL QUERY 12345;

-- 杀连接
KILL CONNECTION 12345;
```

### 3. 查看变量和状态

```sql
-- 查看所有变量
SHOW VARIABLES;

-- 查看特定变量
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'innodb%';

-- 查看所有状态
SHOW STATUS;

-- 查看特定状态
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Innodb%';
```

### 4. 查看权限

```sql
-- 查看当前用户
SELECT CURRENT_USER(), USER();

-- 查看当前用户权限
SHOW GRANTS;

-- 查看其他用户权限
SHOW GRANTS FOR 'app_user'@'%';

-- 创建用户
CREATE USER 'app_user'@'%' IDENTIFIED BY 'StrongP@ss!';

-- 授权
GRANT SELECT, INSERT, UPDATE ON mydb.* TO 'app_user'@'%';
GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost' WITH GRANT OPTION;

-- 刷新权限
FLUSH PRIVILEGES;
```

### 5. 锁和事务

```sql
-- 查看当前锁等待
SELECT * FROM performance_schema.data_lock_waits\G

-- 查看长事务
SELECT * FROM information_schema.innodb_trx
WHERE TIMESTAMPDIFF(SECOND, trx_started, NOW()) > 60;
```

### 6. 备份恢复

```bash
# 备份整个数据库
mysqldump -u root -p mydb > backup.sql

# 备份表结构
mysqldump -u root -p --no-data mydb > schema.sql

# 恢复
mysql -u root -p mydb < backup.sql
```

## 🎯 实用技巧

### 1. 格式化输出

```bash
# 表格格式（默认）
mysql -u root -p -e "SELECT * FROM users LIMIT 5;"

# 垂直格式（字段多时更好看）
mysql -u root -p -e "SELECT * FROM users LIMIT 5\G"

# HTML 格式
mysql -u root -p -H -e "SELECT * FROM users LIMIT 5;"

# XML 格式
mysql -u root -p -X -e "SELECT * FROM users LIMIT 5;"
```

### 2. 批量执行

```bash
# 从文件读 SQL
mysql -u root -p < script.sql

# 执行多条 SQL
mysql -u root -p -e "
  SELECT COUNT(*) FROM users;
  SELECT COUNT(*) FROM orders;
  SHOW TABLES;
"

# 从管道读 SQL
echo "SELECT VERSION();" | mysql -u root -p
```

### 3. 安全模式

```bash
# 开启 safe-updates（防止误操作）
mysql --safe-updates -u root -p

# 效果：
# - UPDATE/DELETE 必须带 WHERE
# - WHERE 必须用主键或唯一索引
# - LIMIT 自动设为 1000
```

### 4. 配置快捷方式

```bash
# ~/.my.cnf（免密码登录）
[client]
user=root
password=StrongP@ss!
host=192.168.1.10

# 设置后直接 mysql 即可连接
```

### 5. 常用快捷键（在 mysql 交互界面中）

```
Ctrl + A    # 跳到行首
Ctrl + E    # 跳到行尾
Ctrl + W    # 删除前一个单词
Ctrl + U    # 删除整行
Ctrl + L    # 清屏
Ctrl + C    # 取消当前命令
Ctrl + D    # 退出 mysql
\G          # 垂直显示结果
\q          # 退出
\h 或 ?     # 帮助
\c          # 取消当前输入
```

## 📊 监控脚本

### 1. 实时 QPS

```bash
# 监控 QPS（每秒查询数）
watch -n 1 "mysql -u root -p -e 'SHOW STATUS LIKE \"Questions\";' | awk 'NR==2{print \$2}'"
```

### 2. 实时连接数

```bash
watch -n 1 "mysql -u root -p -e 'SHOW STATUS LIKE \"Threads_connected\";'"
```

### 3. 实时慢查询

```bash
# 每 5 秒刷新一次慢查询
watch -n 5 "mysql -u root -p -e 'SHOW FULL PROCESSLIST;' | grep -v Sleep"
```

## 🛠️ 高级用法

### 1. pager 分页

```bash
# 启动时用 pager
mysql --pager='less -S' -u root -p

# 大结果集自动分页
```

### 2. 导入导出

```bash
# 导出 CSV
mysql -u root -p -e "SELECT * FROM users" --batch --raw > users.csv

# 导入 CSV
mysqlimport -u root -p --local mydb users.csv
```

### 3. 主从复制检查

```sql
-- 主库
SHOW MASTER STATUS;

-- 从库
SHOW SLAVE STATUS\G

-- 关键指标：
-- Seconds_Behind_Master: 延迟秒数
-- Slave_IO_Running: IO 线程
-- Slave_SQL_Running: SQL 线程
```

### 4. 性能快速诊断

```sql
-- 5 个 SQL 看性能
-- 1. 慢查询数量
SHOW STATUS LIKE 'Slow_queries';

-- 2. 连接使用率
SHOW STATUS LIKE 'Threads_connected';
SHOW VARIABLES LIKE 'max_connections';

-- 3. 缓冲池命中率
SHOW STATUS LIKE 'Innodb_buffer_pool_read%';

-- 4. 主从延迟
SHOW SLAVE STATUS\G

-- 5. 表大小
SELECT table_name, ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables WHERE table_schema = DATABASE();
```

## 🎯 总结

**mysql client 核心命令：**

| 场景 | 命令 |
|---|---|
| 连接 | `mysql -h host -u user -p db` |
| 查看表结构 | `DESC table` / `SHOW CREATE TABLE table\G` |
| 查看进程 | `SHOW PROCESSLIST` |
| 杀进程 | `KILL id` |
| 查看变量 | `SHOW VARIABLES LIKE 'xxx'` |
| 查看状态 | `SHOW STATUS LIKE 'xxx'` |
| 权限 | `SHOW GRANTS` / `GRANT ...` |
| 备份 | `mysqldump` |
| 监控 | `SHOW SLAVE STATUS\G` |

**效率技巧：**
- 配置 `~/.my.cnf` 免密码
- 用 `\G` 垂直显示
- 用 `watch` 实时监控
- 用 `--safe-updates` 防止误操作

**下一步：** [🔧 pt-toolkit 工具集](../11-tools/pt-toolkit) — Percona 神器工具集