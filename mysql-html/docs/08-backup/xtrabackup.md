---
title: xtrabackup 热备
date: 2026-08-15  # date-auto-injected
---

# ⚡ MySQL xtrabackup 热备

> Percona XtraBackup 是业界标准的 MySQL 热备工具，支持 **TB 级数据在线热备**，是生产环境的首选备份方案。

## 🎯 xtrabackup 是什么？

xtrabackup 是 Percona 开发的 **物理热备工具**，可以**在不锁表的情况下**备份整个数据库。

```
mysqldump：
- 逻辑备份（生成 SQL）
- 锁表 / 慢
- 适合 < 100GB

xtrabackup：
- 物理备份（复制数据文件）
- 热备（不锁表）
- 适合 TB 级数据
- 备份速度：1-2GB/秒
```

## 🚀 xtrabackup 安装

```bash
# Ubuntu/Debian
wget https://repo.percona.com/apt/percona-release_latest.$(lsb_release -sc)_all.deb
dpkg -i percona-release_latest.$(lsb_release -sc)_all.deb
apt-get update
apt-get install percona-xtrabackup-80

# CentOS/RHEL
yum install https://repo.percona.com/yum/percona-release-latest.noarch.rpm
yum install percona-xtrabackup-80
```

## 🔧 完整备份

### 1. 执行备份

```bash
# 基础备份
xtrabackup --backup \
  --target-dir=/backup/full_20250718 \
  --user=root --password=xxx

# 推荐参数（生产环境）
xtrabackup --backup \
  --target-dir=/backup/full_20250718 \
  --user=root \
  --password=xxx \
  --parallel=4 \
  --compress \
  --compress-threads=4 \
  --slave-info \
  --safe-slave-backup
```

**参数说明：**
- `--parallel=4`：并行备份（4 线程）
- `--compress`：压缩备份
- `--slave-info`：记录从库信息（用于搭建新从库）
- `--safe-slave-backup`：在从库上安全备份（不影响复制线程）

### 2. 准备备份

```bash
# 备份完成后，需要 prepare（应用 redo log）
xtrabackup --prepare --target-dir=/backup/full_20250718
```

### 3. 恢复备份

```bash
# 步骤 1: 停止 MySQL
systemctl stop mysql

# 步骤 2: 清空数据目录（或备份现有数据）
mv /var/lib/mysql /var/lib/mysql.bak

# 步骤 3: 恢复
xtrabackup --copy-back --target-dir=/backup/full_20250718 \
  --datadir=/var/lib/mysql

# 步骤 4: 修复权限
chown -R mysql:mysql /var/lib/mysql

# 步骤 5: 启动 MySQL
systemctl start mysql
```

## 📊 增量备份

### 增量备份原理

```
完整备份 (周日)        增量 (周一)     增量 (周二)
   ↓                    ↓               ↓
   ├────────────── 增量1 ──┴── 增量2 ────┘
   │
   └── 基础（所有增量的合并点）
```

### 执行增量备份

```bash
# 1. 完整备份
xtrabackup --backup --target-dir=/backup/full

# 2. 基于完整备份的增量备份（周一）
xtrabackup --backup --target-dir=/backup/inc1 \
  --incremental-basedir=/backup/full

# 3. 基于最近增量的增量备份（周二）
xtrabackup --backup --target-dir=/backup/inc2 \
  --incremental-basedir=/backup/inc1
```

### 恢复增量备份

```bash
# 步骤 1: 准备完整备份
xtrabackup --prepare --target-dir=/backup/full

# 步骤 2: 应用增量备份（按顺序）
xtrabackup --prepare --target-dir=/backup/full \
  --incremental-dir=/backup/inc1

xtrabackup --prepare --target-dir=/backup/full \
  --incremental-dir=/backup/inc2

# 步骤 3: 恢复（同完整备份）
xtrabackup --copy-back --target-dir=/backup/full
```

## ⏰ 定时备份策略

### 完整备份 + 增量备份

```bash
#!/bin/bash
# /usr/local/bin/mysql-backup.sh

BACKUP_DIR=/backup/mysql
DATE=$(date +%Y%m%d)
WEEKDAY=$(date +%u)

# 周日：完整备份
if [ $WEEKDAY -eq 7 ]; then
  rm -rf $BACKUP_DIR/full
  xtrabackup --backup --target-dir=$BACKUP_DIR/full \
    --user=root --password=xxx --parallel=4
fi

# 每天：增量备份
xtrabackup --backup --target-dir=$BACKUP_DIR/inc_$DATE \
  --incremental-basedir=$BACKUP_DIR/full

# 清理 7 天前的增量备份
find $BACKUP_DIR -name "inc_*" -mtime +7 -exec rm -rf {} \;

# 上传到远程
rsync -avz $BACKUP_DIR/ backup@backup-server:/backup/
```

```bash
# crontab -e
0 2 * * * /usr/local/bin/mysql-backup.sh
```

## 🛠️ 实战案例

### 案例 1：TB 级数据库备份

```bash
# 1TB 数据备份
# 完整备份时间：~30-60 分钟
# 增量备份时间：~5-10 分钟
# 恢复时间：~1-2 小时

# 完整备份
xtrabackup --backup --target-dir=/backup/full \
  --parallel=8 --compress --compress-threads=8

# 恢复
xtrabackup --prepare --target-dir=/backup/full
xtrabackup --copy-back --target-dir=/backup/full --parallel=8
```

### 案例 2：从库备份（不影响主库）

```bash
# 在从库上备份
xtrabackup --backup --target-dir=/backup/slave_backup \
  --user=root --password=xxx \
  --slave-info \
  --safe-slave-backup
```

### 案例 3：搭建新从库

```bash
# 1. 在主库执行完整备份
xtrabackup --backup --target-dir=/backup/full --slave-info

# 2. 恢复到新从库
xtrabackup --prepare --target-dir=/backup/full
xtrabackup --copy-back --target-dir=/backup/full --datadir=/var/lib/mysql
systemctl start mysql

# 3. 配置复制（从备份中获取 binlog position）
cat /var/lib/mysql/xtrabackup_binlog_info
# mysql-bin.000003 456789
mysql -e "
  CHANGE MASTER TO
    MASTER_HOST='192.168.1.10',
    MASTER_USER='repl_user',
    MASTER_PASSWORD='xxx',
    MASTER_LOG_FILE='mysql-bin.000003',
    MASTER_LOG_POS=456789;
  START SLAVE;
"
```

## 📊 性能对比

| 数据量 | mysqldump | xtrabackup |
|---|---|---|
| 10GB | 5 分钟 | 30 秒 |
| 100GB | 1 小时 | 5 分钟 |
| 1TB | 10+ 小时 | 30-60 分钟 |
| 10TB | 不推荐 | 5-10 小时 |

## ⚠️ 注意事项

### 1. 磁盘空间

```bash
# 备份目录需要足够空间
# 完整备份 = 数据库大小（压缩后约 30-50%）

df -h /backup
# 确保至少 2x 数据库大小的可用空间
```

### 2. 版本兼容

```
xtrabackup 版本需与 MySQL 版本匹配：
- xtrabackup 8.0 → MySQL 8.0
- xtrabackup 2.4 → MySQL 5.7
- xtrabackup 2.3 → MySQL 5.6
```

### 3. 加密备份

```bash
# 备份时加密
xtrabackup --backup --target-dir=/backup/full \
  --encrypt=AES256 \
  --encrypt-key-file=/root/backup.key

# 准备时解密
xtrabackup --prepare --target-dir=/backup/full \
  --encrypt-key-file=/root/backup.key
```

## 🛠️ 备份验证

```bash
# 1. 定期恢复演练
mysql -e "DROP DATABASE test_restore;"
mysql -e "CREATE DATABASE test_restore;"
xtrabackup --prepare --target-dir=/backup/full
xtrabackup --copy-back --target-dir=/backup/full --datadir=/var/lib/mysql_test
systemctl start mysql
# 验证数据
mysql -e "SELECT COUNT(*) FROM test_restore.users;"

# 2. 验证备份一致性
xtrabackup --prepare --target-dir=/backup/full --check
```

## 🎯 总结

**xtrabackup 核心：**
- ✅ 物理热备（不锁表）
- ✅ 支持 TB 级数据
- ✅ 增量备份节省空间
- ✅ 业界标准方案

**vs mysqldump：**
- mysqldump：小数据量、逻辑备份
- xtrabackup：大数据量、物理热备

**最佳实践：**
- 周日完整备份 + 每天增量
- 备份到远程存储
- 定期演练恢复
- 加密敏感数据

**下一步：** [🔙 binlog 时间点恢复](../08-backup/binlog-recovery) — 误删数据救命稻草