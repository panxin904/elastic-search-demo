---
title: 备份与恢复
description: pg_dump / pg_basebackup / PITR
---

# 备份与恢复

> **TL;DR**：PG 备份 = **逻辑备份（pg_dump）+ 物理备份（pg_basebackup）+ WAL archive**。**RPO < 1 分钟、PITR 任意时间点恢复**是 PG 备份的标准能力。

## 一句话定义

```
备份策略 = 全量 + 增量 + WAL archive
        = RPO 取决于 WAL 归档频率
        = RTO 取决于恢复速度
```

## 三种备份方式对比

| 维度 | 逻辑（pg_dump） | 物理（pg_basebackup） | 流复制 |
|---|---|---|---|
| 备份对象 | 逻辑 SQL | 物理文件 | 持续 WAL |
| 恢复速度 | 慢（重建索引） | 快（拷贝文件） | 极快（promote） |
| 跨版本 | ✓ | ✗ | ✗ |
| 跨平台 | ✓ | ✗ | ✗ |
| 粒度 | 单表 / 全库 | 全实例 | 持续 |
| 适用 | 迁移 / 备份 | HA / 容灾 | DR / 读写分离 |

## 1. pg_dump 逻辑备份

```bash
# 全库
pg_dump -h localhost -U postgres -d mydb > backup.sql

# 压缩
pg_dump -h localhost -U postgres -d mydb | gzip > backup.sql.gz

# 自定义格式（并行恢复）
pg_dump -h localhost -U postgres -d mydb -Fc > backup.dump

# 目录格式（并行恢复）
pg_dump -h localhost -U postgres -d mydb -Fd -j 4 -f backup_dir/

# 单表
pg_dump -h localhost -U postgres -d mydb -t users > users.sql

# 仅 schema
pg_dump -h localhost -U postgres -d mydb --schema-only > schema.sql
```

**恢复**：

```bash
# SQL 格式
psql -h localhost -U postgres -d newdb < backup.sql

# 自定义格式
pg_restore -h localhost -U postgres -d newdb backup.dump

# 并行恢复
pg_restore -h localhost -U postgres -d newdb -j 4 backup.dump
```

## 2. pg_basebackup 物理备份

```bash
# 全量备份
pg_basebackup -h localhost -U postgres -D /backup/base -Ft -Xs -P -c fast

# 参数：
# -Ft：tar 格式
# -Xs：流式 WAL
# -P：进度显示
# -c fast：快速 checkpoint
```

**恢复**：

```bash
# 1. 停 PG
pg_ctl stop

# 2. 清空数据目录
rm -rf /var/lib/postgresql/data/*

# 3. 解压备份
tar -xf /backup/base/base.tar -C /var/lib/postgresql/data/
tar -xf /backup/base/wal.tar -C /var/lib/postgresql/wal/

# 4. 启动
pg_ctl start
```

## 3. WAL archive（增量 + PITR）

**配置归档**：

```ini
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'
# 或用 WAL-G / pgbackrest
```

**手动归档**：

```sql
SELECT pg_switch_wal();
-- 强制切换 WAL，立即归档
```

**PITR（Point-in-Time Recovery）**：

```bash
# 1. 恢复基础备份
rm -rf /var/lib/postgresql/data/*
pg_basebackup -h ... -D /var/lib/postgresql/data -Ft -Xs

# 2. 创建恢复配置文件
cat > /var/lib/postgresql/data/recovery.signal << EOF
EOF

cat >> /var/lib/postgresql/data/postgresql.conf << EOF
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2026-08-09 10:00:00'
recovery_target_action = 'pause'
EOF

# 3. 启动
pg_ctl start

# 4. 验证
SELECT pg_is_in_recovery();  -- true 表示在恢复中
SELECT pg_wal_replay_resume();  -- 恢复完成
```

## 4. 工具推荐

### pgBackrest

```bash
# 配置文件
/etc/pgbackrest.conf

[global]
repo1-path=/var/lib/pgbackrest
repo1-cipher-type=aes-256-cbc
repo1-cipher-pass=secret

[mycluster]
pg1-path=/var/lib/postgresql/data

# 全量 + 增量 + WAL
pgbackrest backup --type=full --compress
pgbackrest backup --type=incr --compress

# 恢复
pgbackrest restore --type=time --target="2026-08-09 10:00:00"
```

### Barman

```bash
# barman backup
barman backup mycluster
barman recover mycluster 20260809T100000 /var/lib/postgresql/data
```

### WAL-G

```bash
# 推送 WAL 到 S3
archive_command = 'wal-g wal-push %p --config /etc/walg.json'

# 备份
wal-g backup-push /var/lib/postgresql/data

# 恢复
wal-g backup-fetch /var/lib/postgresql/data BACKUP_NAME
```

## 5. 备份策略

```
生产环境推荐：
  1. 每日全量（pgBackrest full）
  2. 每小时增量（pgBackrest incr）
  3. WAL 持续归档（S3 / NFS）
  4. RPO < 1 分钟
  5. RTO 取决于恢复速度
```

## 实战案例

### 案例 1：误删除整张表

```bash
# 1. 停业务
pg_ctl pause  # 暂停写入

# 2. 从最近的备份恢复到一个新实例
pg_restore -h localhost -d testdb users.dump

# 3. 提取丢失的表
pg_dump -h localhost -d testdb -t users > recovered_users.sql

# 4. 加载到生产
psql -h localhost -d productiondb -f recovered_users.sql
```

### 案例 2：PITR 到误操作前 1 分钟

```bash
# 误操作：DELETE FROM users  -- 删错了

# 1. 找到误操作时间
# 14:30:00 执行 DELETE

# 2. PITR 到 14:29:00
recovery_target_time = '2026-08-09 14:29:00'
```

## 一句话总结

> **PG 备份 = pg_dump（逻辑）+ pg_basebackup（物理）+ WAL archive（PITR）**。**生产推荐 pgBackrest 全量+增量+WAL 到 S3**，**RPO < 1 分钟**。**跨版本迁移用 pg_dump，HA/容灾用 pg_basebackup**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
