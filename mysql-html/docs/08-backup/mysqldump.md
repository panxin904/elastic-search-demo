---
title: mysqldump 逻辑备份
---

# 📦 MySQL mysqldump 逻辑备份

> mysqldump 是 MySQL 自带的逻辑备份工具，适合中小数据量备份（< 100GB），是 DBA 必备技能。

## 🎯 mysqldump 是什么？

mysqldump 生成 **SQL 脚本**，包含建表语句和 INSERT 数据，可以用来恢复数据库。

```bash
# 生成 SQL 备份文件
mysqldump mydb > mydb.sql

# 恢复
mysql mydb < mydb.sql
```

## 🚀 基本用法

### 备份整个数据库

```bash
# 备份一个库
mysqldump mydb > /backup/mydb_$(date +%Y%m%d).sql

# 备份多个库
mysqldump --databases db1 db2 > /backup/multi.sql

# 备份所有库
mysqldump --all-databases > /backup/all.sql
```

### 备份特定表

```bash
# 备份指定表
mysqldump mydb users orders > /backup/tables.sql

# 备份匹配通配符的表
mysqldump mydb 'user_*' > /backup/user_tables.sql
```

## ⚙️ 常用参数

### 关键参数

```bash
# 最重要：单事务（保证一致性）
mysqldump --single-transaction mydb > backup.sql

# 包含存储过程、函数、触发器
mysqldump --routines --triggers --events mydb > backup.sql

# 完整 INSERT（每行一条 INSERT，便于排查）
mysqldump --complete-insert mydb > backup.sql

# 压缩
mysqldump mydb | gzip > backup.sql.gz

# 不锁表（需要 InnoDB）
mysqldump --single-transaction --quick --lock-tables=false mydb > backup.sql
```

### 完整推荐参数（生产环境）

```bash
mysqldump \
  --single-transaction \
  --quick \
  --routines \
  --triggers \
  --events \
  --hex-blob \
  --default-character-set=utf8mb4 \
  --master-data=2 \
  --set-gtid-purged=OFF \
  mydb > /backup/mydb_$(date +%Y%m%d_%H%M%S).sql
```

**参数说明：**
- `--single-transaction`：单事务，保证一致性（InnoDB）
- `--quick`：不缓存查询，逐行读取
- `--master-data=2`：记录 binlog position（用于搭建从库）
- `--set-gtid-purged=OFF`：不记录 GTID 信息（用于恢复到不同环境）

## 📊 备份恢复实战

### 1. 完整备份恢复

```bash
# 备份
mysqldump --single-transaction mydb > /backup/mydb_full.sql

# 恢复（先创建数据库）
mysql -e "CREATE DATABASE mydb;"
mysql mydb < /backup/mydb_full.sql
```

### 2. 备份 + binlog 恢复（恢复到指定时间点）

```bash
# 步骤 1: 完整备份
mysqldump --single-transaction --master-data=2 mydb > /backup/mydb_full.sql

# 步骤 2: 查看备份时的 binlog 位置
grep "CHANGE MASTER" /backup/mydb_full.sql
# CHANGE MASTER TO MASTER_LOG_FILE='mysql-bin.000003', MASTER_LOG_POS=456789;

# 步骤 3: 恢复完整备份
mysql mydb < /backup/mydb_full.sql

# 步骤 4: 应用 binlog（恢复到指定时间点）
mysqlbinlog --start-position=456789 \
           --stop-datetime="2025-07-18 15:30:00" \
           /var/log/mysql/mysql-bin.000003 | mysql mydb
```

### 3. 备份特定表

```bash
# 备份
mysqldump mydb users orders > /backup/tables.sql

# 恢复（不需要先建库）
mysql mydb < /backup/tables.sql
```

## 📋 备份策略

### 完整备份 + binlog 增量

```bash
# 每天凌晨 3 点完整备份
0 3 * * * /usr/bin/mysqldump --single-transaction --master-data=2 \
    --routines --triggers mydb | gzip > /backup/mydb_$(date +\%Y\%m\%d).sql.gz

# 保留 7 天
find /backup -name "mydb_*.sql.gz" -mtime +7 -delete
```

### 备份到远程

```bash
# 备份到远程服务器
mysqldump mydb | gzip | ssh user@backup-server \
  "cat > /backup/remote/mydb_$(date +%Y%m%d).sql.gz"

# 备份到 S3
mysqldump mydb | gzip | aws s3 cp - s3://my-bucket/mysql/mydb.sql.gz
```

## ⚠️ mysqldump 的局限性

### 1. 备份大数据量慢

```
数据量 100GB：
- 备份时间：30 分钟 ~ 2 小时
- 备份文件：20-50GB
- 恢复时间：1-3 小时

不推荐 mysqldump 备份 > 100GB 的库
```

### 2. 锁表风险（MyISAM）

```bash
# ❌ MyISAM 表会被锁（影响业务）
mysqldump mydb > backup.sql

# ✅ 改用 xtrabackup（热备）
xtrabackup --backup --target-dir=/backup/full
```

### 3. 内存占用

```bash
# 大量数据时，mysqldump 会占用内存
# 加 --quick 参数逐行读取
mysqldump --quick mydb > backup.sql
```

## 🛠️ 高级用法

### 1. 排除特定表

```bash
# 排除日志表
mysqldump --ignore-table=mydb.logs \
         --ignore-table=mydb.audit_logs \
         mydb > backup.sql
```

### 2. 条件导出

```bash
# 只导出特定条件的数据
mysqldump mydb users --where="created_at >= '2025-01-01'" > users_2025.sql
```

### 3. 跨服务器备份

```bash
# 从远程服务器备份
mysqldump -h remote-host -u user -p mydb > backup.sql

# 直接备份到远程
mysqldump mydb | mysql -h remote-host remote_db
```

### 4. 加密备份

```bash
# 用 openssl 加密
mysqldump mydb | gzip | openssl enc -aes-256-cbc -salt -pbkdf2 \
  -out /backup/mydb_$(date +%Y%m%d).sql.gz.enc

# 解密
openssl enc -d -aes-256-cbc -in backup.sql.gz.enc | gunzip | mysql mydb
```

## 📊 性能优化

```bash
# 1. 启用并行备份（mysqldump 本身单线程）
# 用 mydumper 实现并行备份
mydumper --threads=4 --outputdir=/backup/mydumper mydb

# 2. 增加网络带宽
# 备份时用专用网络

# 3. 排除大字段
mysqldump --skip-lock-tables mydb users \
  --where="id < 10000" > small_backup.sql
```

## 🛠️ 备份验证

```bash
# 1. 检查备份文件大小
ls -lh /backup/mydb_*.sql

# 2. 检查备份内容
head -50 /backup/mydb_full.sql

# 3. 验证备份可恢复（定期演练）
mysql -e "CREATE DATABASE test_restore;"
mysql test_restore < /backup/mydb_full.sql
# 验证数据
mysql -e "SELECT COUNT(*) FROM test_restore.users;"

# 4. 用 pt-table-checksum 验证一致性
pt-table-checksum --host=master_host
```

## 🎯 总结

**mysqldump 核心：**
- ✅ MySQL 自带，零成本
- ✅ 适合中小数据量（< 100GB）
- ✅ 单事务保证一致性
- ✅ 输出 SQL，可读性好

**最佳实践：**
- InnoDB 表用 `--single-transaction`（不锁表）
- 加上 `--quick`（不缓存，逐行读取）
- 包含存储过程、函数、触发器
- 定期演练恢复

**局限性：**
- 大数据量慢
- MyISAM 会锁表
- 单线程

**下一步：** [⚡ xtrabackup 热备](../08-backup/xtrabackup) — TB 级数据热备方案


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
