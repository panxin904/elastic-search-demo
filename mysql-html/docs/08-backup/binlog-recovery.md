---
title: binlog 时间点恢复
---

# 🔙 MySQL binlog 时间点恢复

> 误删数据、误更新表？binlog 是救命稻草。学会从 binlog 恢复数据，是 DBA 的核心技能。

## 🎯 什么是 binlog 恢复？

binlog 记录了**所有数据变更**，通过应用 binlog，可以把数据库恢复到**任意时间点**。

```
场景：下午 3 点误删了订单表

时间线：
14:00 - 正常
15:00 - 误删 orders 表
15:30 - 发现错误

恢复：
1. 停止写入
2. 找到 15:00 之前的完整备份
3. 应用 binlog 到 14:59:59
4. 恢复完成！
```

## 🚀 恢复流程

### 步骤 1：定位问题

```bash
# 1. 确认误操作时间
# 通过慢查询日志、应用日志、binlog 找到时间点

# 2. 找到误操作前的完整备份
ls -la /backup/mysql/
# full_20250717/    ← 7 月 17 日完整备份
# full_20250718/    ← 7 月 18 日完整备份（误删前）

# 3. 查看备份时的 binlog 位置
cat /backup/mysql/full_20250718/xtrabackup_binlog_info
# mysql-bin.000003 456789
```

### 步骤 2：恢复完整备份

```bash
# 1. 停止 MySQL
systemctl stop mysql

# 2. 备份当前数据（防止二次破坏）
mv /var/lib/mysql /var/lib/mysql_broken

# 3. 恢复 7 月 18 日的完整备份
xtrabackup --prepare --target-dir=/backup/mysql/full_20250718
xtrabackup --copy-back --target-dir=/backup/mysql/full_20250718 \
  --datadir=/var/lib/mysql

# 4. 启动 MySQL
systemctl start mysql
```

### 步骤 3：应用 binlog 到指定时间点

```bash
# 1. 查看 binlog 文件
ls /var/log/mysql/mysql-bin.*

# 2. 找到误操作的具体 binlog
mysqlbinlog /var/log/mysql/mysql-bin.000005 | grep "DROP TABLE"

# 3. 应用 binlog（恢复到误操作前）
mysqlbinlog --start-position=456789 \
           --stop-datetime="2025-07-18 14:59:59" \
           /var/log/mysql/mysql-bin.000005 | mysql

# 或跳过具体的误操作语句
mysqlbinlog --start-position=456789 \
           --stop-position=789012 \
           /var/log/mysql/mysql-bin.000005 | mysql
```

### 步骤 4：验证恢复

```bash
# 检查数据是否恢复
mysql -e "SELECT COUNT(*) FROM mydb.orders;"
mysql -e "SELECT * FROM mydb.orders ORDER BY id DESC LIMIT 10;"
```

## 🎯 精确恢复技巧

### 1. 跳过单个误操作

```bash
# 场景：误删了某个表，但其他表正常
# 找到 DROP TABLE 的 position

# 1. 查看具体语句
mysqlbinlog --start-datetime="2025-07-18 15:00:00" \
           --stop-datetime="2025-07-18 15:30:00" \
           /var/log/mysql/mysql-bin.000005 | less

# 2. 找到 DROP TABLE 的 position（假设 123456）
# # at 123456

# 3. 应用到 DROP TABLE 之前
mysqlbinlog --start-position=456789 \
           --stop-position=123456 \
           /var/log/mysql/mysql-bin.000005 | mysql
```

### 2. 恢复单条误删数据

```bash
# 场景：误 UPDATE 了一条数据
# 1. 找到 UPDATE 的位置
mysqlbinlog --start-datetime="2025-07-18 14:00:00" \
           --stop-datetime="2025-07-18 15:00:00" \
           /var/log/mysql/mysql-bin.000005 | grep "UPDATE"

# 2. 找到具体的 UPDATE 语句和 position
# # at 234567
# UPDATE users SET name='xxx' WHERE id=100;

# 3. 恢复（先记录当前值，再恢复）
# 建议：直接用 SQL 反向操作
UPDATE users SET name = '原值' WHERE id = 100;
```

### 3. 恢复误删的库

```bash
# 场景：误 DROP DATABASE
# 1. 找到 DROP DATABASE 的 position

# 2. 应用 binlog 到 DROP DATABASE 之前
mysqlbinlog --start-position=456789 \
           --stop-position=999999 \
           /var/log/mysql/mysql-bin.000005 | mysql

# 3. 验证
mysql -e "SHOW DATABASES;"
```

## 🔧 高级恢复：定点跳过

### 场景：binlog 中包含多个事务，需要跳过中间的某些事务

```bash
# 1. 解析 binlog 找到关键 position
mysqlbinlog /var/log/mysql/mysql-bin.000005 > /tmp/binlog.sql
grep -n "^# at" /tmp/binlog.sql

# 2. 选择要恢复的区间
# 比如恢复 position 456789 到 123456，跳过 234567 开始的误操作

mysqlbinlog --start-position=456789 \
           --stop-position=123456 \
           /var/log/mysql/mysql-bin.000005 > /tmp/recover.sql

# 跳过误操作，应用后续的
mysqlbinlog --start-position=345678 \
           /var/log/mysql/mysql-bin.000005 >> /tmp/recover.sql

# 3. 一次性应用
mysql < /tmp/recover.sql
```

## 📊 ROW 格式 binlog 恢复（推荐）

```bash
# ROW 格式 binlog 默认不可读，需要 -v 参数
mysqlbinlog -v /var/log/mysql/mysql-bin.000005

# 转换为可读的 SQL
mysqlbinlog -v --base64-output=decode-rows \
  /var/log/mysql/mysql-bin.000005 > /tmp/binlog_readable.sql

# 查看具体行变更
less /tmp/binlog_readable.sql
```

## 🛠️ 自动化恢复脚本

```bash
#!/bin/bash
# /usr/local/bin/point-in-time-recovery.sh
# 用法: ./point-in-time-recovery.sh "2025-07-18 14:59:59"

STOP_DATETIME=$1
BACKUP_DIR=/backup/mysql/latest
BINLOG_DIR=/var/log/mysql

# 1. 准备备份
echo "准备备份..."
xtrabackup --prepare --target-dir=$BACKUP_DIR

# 2. 恢复数据
echo "恢复数据..."
systemctl stop mysql
rm -rf /var/lib/mysql/*
xtrabackup --copy-back --target-dir=$BACKUP_DIR --datadir=/var/lib/mysql
chown -R mysql:mysql /var/lib/mysql
systemctl start mysql

# 3. 应用 binlog
echo "应用 binlog 到 $STOP_DATETIME..."
LATEST_BINLOG=$(ls -t $BINLOG_DIR/mysql-bin.* | head -1)
mysqlbinlog --stop-datetime="$STOP_DATETIME" $BINLOG_DIR/mysql-bin.0* | mysql

echo "恢复完成！请验证数据..."
```

## ⚠️ 重要注意事项

### 1. 立即停止写入

```bash
# 发现误操作后，第一时间：
mysql -e "SET GLOBAL read_only = ON;"
# 或直接停止应用
# 防止更多数据写入，恢复时数据不一致
```

### 2. 保留现场

```bash
# 1. 备份当前数据目录
mv /var/lib/mysql /var/lib/mysql_broken_$(date +%Y%m%d_%H%M%S)

# 2. 保留当前 binlog
cp -p /var/log/mysql/mysql-bin.* /backup/binlog_emergency/
```

### 3. 测试恢复

```bash
# ⚠️ 不要在生产环境直接恢复
# 先在测试环境验证

# 复制数据到测试服务器
rsync -avz /var/lib/mysql_broken_20250718_150000/ test-server:/tmp/test_data/
# 在测试环境恢复
```

### 4. 恢复后验证

```sql
-- 1. 检查数据完整性
SELECT COUNT(*) FROM orders;  -- 对比业务系统

-- 2. 检查 binlog 是否一致
SHOW MASTER STATUS;
SHOW BINARY LOGS;

-- 3. 检查复制状态（如果是主库）
SHOW SLAVE STATUS\G
```

## 🛡️ 预防误操作

### 1. 开启 safe-updates

```bash
# mysql client 默认开启（防止 UPDATE/DELETE 没有 WHERE）
mysql --safe-updates

# 或在配置文件中
[mysql]
safe-updates
```

### 2. 开启审计日志

```sql
-- 开启 audit log
INSTALL PLUGIN audit_log SONAME 'audit_log.so';
SET GLOBAL audit_log_policy = 'ALL';

-- 记录所有 SQL
-- 可以追溯谁在什么时候执行了什么
```

### 3. 危险操作前先备份

```sql
-- 删表前先备份
CREATE TABLE orders_backup_20250718 AS SELECT * FROM orders;
DROP TABLE orders;

-- 删库前先备份
mysqldump mydb > /tmp/mydb_backup_before_drop.sql
DROP DATABASE mydb;
```

### 4. 设置延迟复制从库

```sql
-- 搭建一个延迟 1 小时的从库
CHANGE MASTER TO MASTER_DELAY = 3600;

-- 即使误操作，从库还有 1 小时前的数据
STOP SLAVE;
START SLAVE UNTIL MASTER_LOG_FILE='mysql-bin.000005', MASTER_LOG_POS=123456;
# 跳过误操作的 position
```

## 🎯 总结

**binlog 恢复核心：**
- ✅ 找到误操作前的完整备份
- ✅ 定位误操作的 binlog position
- ✅ 应用 binlog 到误操作前
- ✅ 验证数据完整性

**恢复流程：**
1. 立即停止写入（read_only）
2. 备份现场
3. 恢复完整备份
4. 应用 binlog 到指定时间点
5. 验证数据

**预防措施：**
- 开启 safe-updates
- 延迟复制从库
- 审计日志
- 危险操作前备份

**下一步：** [🐢 慢查询日志](../09-monitoring/slow-log) — 监控系列


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
