---
title: AOF 日志
date: 2026-08-15  # date-auto-injected
---

# 📜 AOF 日志

> **AOF（Append Only File）**通过记录**所有写命令**到文件，实现**增量持久化**。Redis 默认关闭，需手动开启。

## 🎯 AOF 原理

```
┌──────────────────────────────────────────┐
│ 客户端 SET user:1 "Alice"                │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│ 1. 命令执行                                 │
│ 2. 将 RESP 协议格式的命令追加到 AOF buffer  │
│ 3. 根据策略（always/everysec/no）刷盘      │
└──────────────┬───────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────┐
│         appendonly.aof                    │
│ *3\r\n$3\r\nSET\r\n$6\r\nuser:1\r\n      │
│ $5\r\nAlice\r\n                           │
└──────────────────────────────────────────┘

Redis 启动时：回放 AOF 中所有命令，恢复数据
```

**AOF 是命令日志**，记录每个写操作。重启时按顺序回放所有命令即可恢复数据。

## ⚡ 三种写回策略

```properties
# redis.conf
appendfsync always      # 每次写都 fsync（最安全但 IO 极慢）
appendfsync everysec    # 每秒 fsync 一次（推荐，默认）
appendfsync no          # 让 OS 决定（最快但不安全）
```

| 策略 | 含义 | 数据丢失 | 性能 |
|------|------|---------|------|
| **always** | 每次写都刷盘 | **不丢失** | 差（IO 瓶颈） |
| **everysec** | 每秒刷盘一次 | **最多 1 秒** | 好（默认） |
| **no** | OS 决定 | **可能丢失** | 最好 |

**everysec 是经典折衷**：最多丢失 1 秒数据，IO 影响可接受。

## 📂 AOF 文件结构

```
┌──────────────────────────────────────────────┐
│ *3\r\n                                       │
│ $3\r\nSET\r\n                                │
│ $6\r\nuser:1\r\n                             │
│ $5\r\nAlice\r\n                              │
│ ---------------------------------- ← SELECTDB │
│ *1\r\n                                       │
│ $4\r\nkey1\r\n                               │
│ ---------------------------------- ← EXPIRE   │
│ *3\r\n                                       │
│ $3\r\nDEL\r\n                                │
│ $7\r\nuser:2\r\n                             │
└──────────────────────────────────────────────┘
```

**AOF 重写时**：只保留能恢复当前数据集的命令（合并冗余命令）。

## 🔄 AOF 重写（BGREWRITEAOF）

> **问题**：AOF 文件会无限膨胀。比如对同一个 key 修改 1000 次，AOF 会记录 1000 条命令，但实际只需要 SET 1 次。

### 重写原理

```
原始 AOF：
  SET counter 0
  INCR counter
  INCR counter
  INCR counter
  INCR counter
  INCR counter
  ... 1000 次 INCR
  
AOF 重写后：
  SET counter 1000           # 只保留最终结果
```

### 重写流程（fork 子进程）

```
┌──────────────────┐         ┌──────────────────┐
│   Redis 主进程    │         │   子进程           │
│                  │ fork    │                   │
│  - 服务客户端     ├────────►│  - 扫描内存数据     │
│  - 写入 aof_buf  │         │  - 生成最小命令集   │
│  - 写入 aof_     │         │  - 写入新 AOF 文件 │
│    rewrite_buf   │         │                   │
└──────────────────┘         └──────────────────┘
        │
        │  子进程完成后
        ▼
   主进程：
   1. 将 aof_rewrite_buf 追加到新 AOF
   2. 原子替换旧 AOF
   3. 完成重写
```

**COW 应用**：子进程扫描内存生成新 AOF 时，父进程修改的页才真正复制。

### 自动触发配置

```properties
# redis.conf
auto-aof-rewrite-percentage 100   # AOF 文件比上次重写增长 100% 触发
auto-aof-rewrite-min-size 64mb   # AOF 文件至少 64MB 才触发

# 例子：
# 上次重写后 AOF = 64MB
# 当前 AOF = 128MB  → 增长 100%  → 触发重写
# 当前 AOF = 100MB  → 增长 56%   → 不触发（因为没达到 100%）
```

### 手动触发

```bash
BGREWRITEAOF    # 异步重写 AOF（推荐）
```

## ⚙️ 关键配置

```properties
# redis.conf AOF 相关

# 开启 AOF（默认关闭）
appendonly yes

# AOF 文件名
appendfilename "appendonly.aof"

# 文件路径
dir /var/lib/redis

# 写回策略（默认 everysec）
appendfsync everysec

# 自动重写配置
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Redis 7+ 多文件 AOF（推荐启用）
# 自动启用，配置简单
# manifest 文件记录各 AOF 片段信息

# AOF 加载时遇到错误处理
aof-load-truncated yes    # 加载截断的 AOF（默认开启）
```

## 📊 AOF 优缺点

| 优点 | 缺点 |
|------|------|
| ✅ 数据更完整（最多丢 1 秒） | ❌ 文件大（命令文本） |
| ✅ 实时性好（每秒刷盘） | ❌ 恢复慢（要回放命令） |
| ✅ 可读性好（RESP 文本） | ❌ 持续占用 IO 带宽 |
| ✅ 自动重写控制文件大小 | ❌ 大量写场景下 IO 压力大 |

## 🔬 AOF 与 RDB 对比

| 维度 | RDB | AOF |
|------|-----|-----|
| 数据完整性 | 分钟级丢失 | 最多丢 1 秒 |
| 文件大小 | 小 | 大 |
| 恢复速度 | **快** | 慢 |
| IO 影响 | 间歇性大块 IO | 持续性小块 IO |
| 适用场景 | 备份、灾备 | 数据安全 |

## 🛠️ 实战：AOF 备份与恢复

### 手动备份

```bash
# 触发 BGSAVE 或 BGREWRITEAOF 创建一个干净的状态
redis-cli BGREWRITEAOF

# 等待重写完成（最多 60 秒）
for i in {1..60}; do
    status=$(redis-cli INFO Persistence | grep aof_rewrite_in_progress | awk -F: '{print $2}' | tr -d '\r')
    if [ "$status" = "0" ]; then
        echo "AOF rewrite completed"
        break
    fi
    sleep 1
done

# 备份 AOF 文件
cp /var/lib/redis/appendonly.aof /backup/redis/aof_$(date +%Y%m%d).aof
gzip /backup/redis/aof_*.aof
```

### AOF 修复（文件损坏时）

```bash
# 使用工具检查并修复
redis-check-aof --fix /var/lib/redis/appendonly.aof

# 如果无法修复，从备份恢复
```

### 切回 RDB-only

```bash
# 1. 停止 Redis
redis-cli SHUTDOWN

# 2. 修改配置
sed -i 's/^appendonly yes/appendonly no/' /etc/redis/redis.conf

# 3. 删除 AOF 文件（或保留为备份）
mv /var/lib/redis/appendonly.aof /backup/

# 4. 启动 Redis（加载 RDB）
redis-server /etc/redis/redis.conf
```

## 🐛 故障案例

### 案例 1：AOF 文件无限膨胀

```
现象：appendonly.aof 文件达到 100GB+
原因：写入量大，auto-aof-rewrite-percentage 设置不合理
解决：
  1. 调小 percentage（如 50%）
  2. 调小 min-size（如 32mb）
  3. 手动 BGREWRITEAOF
```

### 案例 2：AOF 加载失败

```
报错：Bad file format reading the append only file
原因：AOF 文件损坏或截断
解决：
  1. redis-check-aof --fix appendonly.aof  # 尝试修复
  2. aof-load-truncated yes  # 配置允许加载截断文件（默认开启）
  3. 从备份恢复
```

### 案例 3：everysec 数据丢失

```
现象：每 1 秒（每秒）有一次刷盘窗口，可能丢 1 秒数据
解决：
  - 关键业务改用 appendfsync always
  - 但 everysec IO 影响小，性能好
  - 权衡：99% 场景 everysec 足够
```

## 🎯 最佳实践

```
生产环境 AOF 建议配置：
  appendonly yes
  appendfsync everysec
  auto-aof-rewrite-percentage 100
  auto-aof-rewrite-min-size 64mb
  aof-use-rdb-preamble yes   # 混合持久化（Redis 4.0+）

+ 监控 AOF 文件大小
+ 监控 aof_rewrite_in_progress 状态
+ 每天备份 AOF
+ 演练 AOF 恢复
```

## 🎯 总结

**AOF 核心要点**：
- ✅ 记录所有写命令到日志
- ✅ 三种策略：always / everysec / no（推荐 everysec）
- ✅ 自动重写控制文件大小
- ✅ 数据完整性优于 RDB（最多丢 1 秒）
- ⚠️ 恢复速度比 RDB 慢
- ⚠️ 文件比 RDB 大

**下一步：** [🔀 混合持久化](/03-persistence/mixed) — Redis 7 默认推荐的方案

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
