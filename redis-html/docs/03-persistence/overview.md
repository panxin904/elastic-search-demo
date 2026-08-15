---
title: 持久化总览
---

# 📚 持久化总览

> Redis 是**内存数据库**，数据默认存在内存中。**一旦宕机，数据全部丢失**。持久化机制就是把内存数据保存到磁盘，让数据不丢。

## 🎯 为什么需要持久化？

```bash
# 没有持久化时
redis-server &
SET user:1 "alice"
kill -9 redis-server             # 模拟宕机
redis-server &                    # 启动后
GET user:1                        # → (nil) 数据丢失！
```

```
业务对持久化的需求：
  缓存（可丢） → 可以不开持久化
  业务数据（不可丢） → 必须开持久化
  混合场景（部分可丢） → 部分 Key 开启 AOF
```

## 🔄 两种持久化方案对比

| 维度 | RDB（快照） | AOF（日志） |
|------|-------------|------------|
| **原理** | 定时把内存全量快照到 RDB 文件 | 每次写命令追加到 AOF 文件 |
| **持久化方式** | 全量（某个时刻的完整数据） | 增量（所有写命令历史） |
| **文件大小** | 小（二进制压缩） | 大（命令文本，未压缩） |
| **恢复速度** | **快**（直接加载） | 慢（要回放命令） |
| **数据安全性** | 可能丢失最后一次快照后的数据 | 可配置为不丢失（always） |
| **IO 消耗** | 一次性大 IO | 持续小 IO |
| **对主进程影响** | fork 子进程，几乎无影响 | always 策略会阻塞 IO |
| **文件格式** | 二进制 | RESP 协议文本 |
| **默认状态** | ✅ 开启 | ❌ 默认关闭（需手动开启） |

## ⏰ 持久化触发时机

```
┌──────────────────────────────────────────┐
│         Redis 内存数据                     │
└──────────────────────────────────────────┘
     │              │              │
     ▼              ▼              ▼
  自动触发         手动触发        主从同步触发
     │              │              │
   save 规则      SAVE（同步）   Replica 连接
   shutdown       BGSAVE（异步）  Master 自动 BGSAVE
   flushall
```

### 1. 自动触发（默认配置）

```bash
# redis.conf 默认规则
save 3600 1    # 3600 秒内至少 1 次修改
save 300 100   # 300 秒内至少 100 次修改
save 60 10000  # 60 秒内至少 10000 次修改

# 满足任一规则即触发 BGSAVE
# 三条规则同时存在，任一满足都会触发
```

### 2. 手动触发

```bash
SAVE          # 同步阻塞（不推荐，主线程不能服务）
BGSAVE        # 异步 fork 子进程（推荐）
```

### 3. 其他触发

```bash
# 主从同步触发（Replica 首次连接）
# 自动执行 BGSAVE 生成 RDB 传输给 Replica

# flushall 命令触发（清空 + 生成空 RDB）
FLUSHALL

# shutdown 命令触发（正常关闭前持久化）
SHUTDOWN
```

## 📂 持久化文件结构

```
/var/lib/redis/
├── dump.rdb            # RDB 文件
├── appendonly.aof      # AOF 文件
└── appendonly.aof.manifest   # Redis 7 多文件 AOF
```

## 🎯 业务场景如何选择？

```
✅ 允许分钟级数据丢失（如会话缓存）
   → 仅用 RDB
   → save 60 1000  # 1 分钟兜底

✅ 不允许丢失数据（如交易、订单）
   → RDB + AOF
   → appendonly yes
   → appendfsync everysec

✅ 混合持久化（Redis 7 推荐）
   → aof-use-rdb-preamble yes
   → 默认开启（Redis 4.0+）

✅ 极致性能（可丢数据）
   → 关闭持久化
   → save ""  +  appendonly no
   → 用 Replica 兜底
```

## ⚖️ RDB + AOF 共存时的加载顺序

```
Redis 启动时：
  1. 检查 AOF 文件是否存在
     ├─ 存在 → 优先加载 AOF（数据更完整）
     └─ 不存在 → 检查 RDB 文件
              ├─ 存在 → 加载 RDB
              └─ 不存在 → 直接启动（空数据）
  2. 加载完成后对外提供服务
```

**为什么优先 AOF？** 因为 AOF 一般比 RDB 数据更完整。

## 🛡️ 性能影响对比

| 操作 | RDB | AOF (everysec) |
|------|-----|----------------|
| **写入性能** | fork 时短暂阻塞（ms 级） | 几乎无影响 |
| **磁盘 IO** | 间歇性大块 IO | 持续性小块 IO |
| **CPU 消耗** | fork 子进程 + 压缩 | 持续写入 |
| **内存占用** | fork 时翻倍（COW） | AOF 重写时翻倍 |
| **网络影响** | 主从同步时占用带宽 | 同 RDB |

## 🧰 实战配置模板

### 高性能缓存场景

```properties
# redis.conf
save 3600 1 300 100 60 10000
appendonly no
rdbcompression yes
rdbchecksum yes
```

### 数据安全场景

```properties
save 3600 1 300 100 60 10000
appendonly yes
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-use-rdb-preamble yes    # 混合持久化
```

### 极致性能（允许丢失）

```properties
save ""
appendonly no
# 关闭所有持久化，纯内存模式
```

## 📊 监控持久化状态

```bash
# 查看 RDB 信息
INFO Persistence

# 输出：
# loading:0
# rdb_changes_since_last_save:0        # 自上次 save 后修改次数
# rdb_bgsave_in_progress:0              # BGSAVE 是否在执行
# rdb_last_save_time:1730000000         # 上次保存时间
# rdb_last_bgsave_status:ok             # 上次保存状态
# rdb_last_bgsave_time_sec:0            # 上次保存耗时

# AOF 状态
# aof_enabled:1
# aof_rewrite_in_progress:0
# aof_rewrite_scheduled:0
# aof_last_rewrite_time_sec:0
# aof_current_size:1024                # 当前 AOF 大小
# aof_base_size:1024                    # 上次启动时 AOF 大小
```

## 🎯 总结

**持久化核心要点**：
- ✅ RDB：定时全量快照，恢复快，可能丢数据
- ✅ AOF：增量日志，最多丢 1 秒（everysec），恢复慢
- ✅ 混合持久化：RDB 全量 + AOF 增量（Redis 7 推荐）
- ✅ 启动优先加载 AOF
- ✅ 生产环境推荐：RDB + AOF everysec + 混合持久化

**下一步：** [📸 RDB 快照](/03-persistence/rdb) — 详解 RDB 原理与配置
