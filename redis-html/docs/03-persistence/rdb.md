---
title: RDB 快照
date: 2026-08-15  # date-auto-injected
---

# 📸 RDB 快照

> **RDB（Redis Database）**是 Redis 默认的持久化方式：通过**内存快照**把某个时刻的全量数据保存到二进制文件。

## 🎯 RDB 原理

```
┌─────────────────────┐
│   Redis 内存数据      │
│   dict / skiplist   │
└──────────┬──────────┘
           │ 触发 BGSAVE
           ▼
┌─────────────────────┐
│  fork 子进程（COW）   │
│  - 复制父进程页表     │
│  - 不复制实际数据     │
└──────────┬──────────┘
           │ 序列化写入
           ▼
┌─────────────────────┐
│   dump.rdb 文件      │
│   二进制压缩          │
└─────────────────────┘
```

**COW（Copy On Write）**：fork 时不复制实际内存数据，只复制页表。子进程写入新文件时，父进程修改的页才真正复制。

## ⚡ 触发方式

### 1. SAVE（同步）

```bash
SAVE
# 主线程同步执行，会阻塞所有客户端请求
# 不推荐用于生产环境！
```

### 2. BGSAVE（异步，推荐）

```bash
BGSAVE
# 主线程 fork 子进程
# 子进程负责写入 RDB
# 主线程继续服务客户端
```

### 3. 自动触发（save 规则）

```properties
# redis.conf
save 3600 1       # 3600 秒内至少 1 次修改
save 300 100      # 300 秒内至少 100 次修改
save 60 10000     # 60 秒内至少 10000 次修改

# 三条规则同时存在，任一满足即触发 BGSAVE
```

### 4. 其他触发

```bash
SHUTDOWN          # 正常关闭时自动持久化
FLUSHALL          # 清空后生成空 RDB
Replica 连接       # 首次连接时 master 自动 BGSAVE
```

## 📂 RDB 文件结构

```
┌──────────────────────────────────────────────┐
│ REDIS + 4 字节版本号                            │
├──────────────────────────────────────────────┤
│ 0xFA + 9 字节长度 + 数据库编号                 │
├──────────────────────────────────────────────┤
│ selectdb: 0                                   │
│ dict size: N                                  │
│ expires size: M                               │
├──────────────────────────────────────────────┤
│ Key-Value 1 (type + key + value + expire)     │
│ Key-Value 2                                   │
│ ...                                           │
├──────────────────────────────────────────────┤
│ 0xFF + 8 字节 CRC64 校验                       │
└──────────────────────────────────────────────┘
```

**查看 RDB 文件**：
```bash
# 使用工具查看
od -c dump.rdb | head -20

# 使用 redis-check-rdb 检查
redis-check-rdb dump.rdb
```

## ⚙️ 关键配置

```properties
# redis.conf RDB 相关

# 保存规则（满足任一即触发 BGSAVE）
save 3600 1
save 300 100
save 60 10000

# 禁用自动 RDB（仅手动触发）
# save ""

# RDB 文件名
dbfilename dump.rdb

# RDB 文件路径
dir /var/lib/redis

# 是否压缩（开启可减小文件，但消耗 CPU）
rdbcompression yes

# 是否校验（开启可检测损坏，但有 10% 性能损耗）
rdbchecksum yes

# BGSAVE 失败时是否停止写
stop-writes-on-bgsave-error yes

# 子进程 RDB 写入磁盘方式
rdb-save-incremental-fsync yes    # 增量 fsync，减少 IO 抖动
```

## ⚠️ fork 阻塞问题

```
BGSAVE = fork + 写入 RDB
        ↑
        fork 这一步会阻塞主线程

fork 耗时与内存大小成正比：
  - 1GB 内存 → fork 约 20ms
  - 10GB 内存 → fork 约 200ms
  - 100GB 内存 → fork 约 2 秒

阻塞期间所有客户端请求都会被卡住！
```

**优化方案**：
- 避免巨型 Key 减少内存碎片
- 启用 `rdb-save-incremental-fsync yes` 减少 IO 抖动
- 高配置机器：增大 `repl-backlog-size` 减少 fork 次数

## 📊 RDB 优缺点

| 优点 | 缺点 |
|------|------|
| ✅ 文件紧凑（二进制压缩） | ❌ 可能丢失最后一次快照后的数据 |
| ✅ 恢复速度极快（直接加载） | ❌ fork 时阻塞主线程 |
| ✅ 适合备份（每天一份 RDB 异地存储） | ❌ 大内存时 fork 慢 |
| ✅ 对主线程几乎无影响 | ❌ 实时性差（分钟级） |

## 🛠️ 实战：RDB 备份与恢复

### 自动备份脚本

```bash
#!/bin/bash
# backup_redis.sh
# 每日凌晨 2 点执行

REDIS_DIR=/var/lib/redis
BACKUP_DIR=/backup/redis
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 触发 BGSAVE
redis-cli BGSAVE

# 等待 BGSAVE 完成（最多 60 秒）
for i in {1..60}; do
    status=$(redis-cli INFO Persistence | grep rdb_bgsave_in_progress | awk -F: '{print $2}' | tr -d '\r')
    if [ "$status" = "0" ]; then
        echo "BGSAVE completed"
        break
    fi
    sleep 1
done

# 复制 RDB 到备份目录
cp $REDIS_DIR/dump.rdb $BACKUP_DIR/dump_$DATE.rdb

# 压缩
gzip $BACKUP_DIR/dump_$DATE.rdb

# 保留最近 30 天的备份
find $BACKUP_DIR -name "dump_*.rdb.gz" -mtime +30 -delete

# 同步到异地存储（rsync / s3 / oss）
# rsync -av $BACKUP_DIR/ backup-server:/backup/redis/
```

### RDB 恢复

```bash
# 1. 停止 Redis
redis-cli SHUTDOWN

# 2. 备份当前 RDB 文件
cp /var/lib/redis/dump.rdb /var/lib/redis/dump.rdb.bak

# 3. 拷贝备份的 RDB 文件
cp /backup/redis/dump_20240701_020000.rdb /var/lib/redis/dump.rdb
chown redis:redis /var/lib/redis/dump.rdb

# 4. 启动 Redis
redis-server /etc/redis/redis.conf

# 5. 验证数据
redis-cli DBSIZE
redis-cli KEYS "*"
```

## 🐛 故障案例

### 案例 1：RDB 文件损坏

```
报错：Bad file format reading the append only file
原因：磁盘空间满、RDB 写入未完成时宕机
解决：
  1. redis-check-rdb --fix dump.rdb  # 尝试修复
  2. 从最近的备份恢复
  3. 启用 AOF（更安全）
```

### 案例 2：磁盘写满导致 BGSAVE 失败

```
报错：Background save failed
原因：磁盘空间不足
解决：
  1. INFO Persistence 查看 last bgsave status
  2. df -h 检查磁盘
  3. 清理磁盘空间或扩容
  4. 临时禁用 stop-writes-on-bgsave-error
```

### 案例 3：fork 阻塞导致请求超时

```
现象：BGSAVE 期间客户端大量超时
原因：内存太大（50GB+），fork 耗时几秒
解决：
  1. 升级到 SSD（fork 后台 IO 不阻塞）
  2. 降低单实例内存（多实例集群）
  3. 减少 Key 数量（合并小 Key）
```

## 🎯 最佳实践

```
生产环境 RDB 建议配置：
  save 3600 1
  save 300 100
  save 60 10000
  rdbcompression yes
  rdbchecksum yes
  stop-writes-on-bgsave-error yes

+ 每天 1 次异地备份
+ 保留 30 天历史
+ 定期演练恢复流程
```

## 📋 RDB vs AOF 选型

| 场景 | 推荐 |
|------|------|
| 缓存（可丢） | 仅 RDB |
| 业务数据 | RDB + AOF |
| 极致性能 | 关闭持久化 |
| 灾备备份 | RDB（每天一份） |
| 金融级 | AOF always（不丢） |

## 🎯 总结

**RDB 核心要点**：
- ✅ 内存全量快照，二进制压缩
- ✅ 通过 fork + COW 几乎不影响主线程
- ✅ 适合备份、灾备、主从同步
- ⚠️ 可能丢失最后一次快照后的数据
- ⚠️ 大内存 fork 阻塞主线程

**下一步：** [📜 AOF 日志](/03-persistence/aof) — 详解 AOF 原理与配置
