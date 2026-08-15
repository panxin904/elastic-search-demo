---
title: 混合持久化
---

# 混合持久化

Redis 4.0 开始支持混合持久化，用来同时解决 RDB 与 AOF 的典型痛点。RDB 文件紧凑、恢复速度快，但两次快照之间的数据可能丢失；纯 AOF 可以把数据丢失窗口缩小到秒级，却会产生更大的文件，并且在重启时逐条回放命令，数据量越大，恢复越慢。混合持久化保留两者的优点：用 RDB 快速恢复存量数据，再用 AOF 补齐最近的变化。

## 工作原理

执行 AOF 重写时，Redis 不再把当前数据集全部转换为写命令。子进程先以 RDB 二进制格式写入某一时刻的完整数据集；重写期间发生的写操作会记录为 AOF 增量，最后追加到文件尾部。因此从逻辑上看，AOF 文件前半部分是 **RDB 全量快照**，后半部分是 **AOF 增量命令**。

```text
appendonly.aof
├── RDB preamble：T0 时刻的完整数据
└── AOF tail：T0 之后的 SET、DEL、EXPIRE 等命令
```

Redis 7 使用多部件 AOF 时，RDB 基础文件和 AOF 增量文件可能分开保存并由 manifest 管理，但“全量基线 + 命令增量”的恢复思想不变。

## redis.conf 配置

生产环境应同时开启 AOF 和 RDB 前导格式，并按可接受的数据丢失窗口选择刷盘策略：

```ini
appendonly yes
appendfilename "appendonly.aof"
aof-use-rdb-preamble yes
appendfsync everysec

auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

`aof-use-rdb-preamble yes` 会在下一次 AOF 重写时生效。修改配置后可以主动触发重写，并检查运行状态：

```bash
redis-cli CONFIG GET appendonly
redis-cli CONFIG GET aof-use-rdb-preamble
redis-cli BGREWRITEAOF
redis-cli INFO persistence
```

如果使用 `CONFIG SET` 在线修改，还应同步更新 `redis.conf`，或在确认配置文件允许重写时执行 `CONFIG REWRITE`，避免重启后丢失设置。

## 启动加载流程

当 AOF 已开启且文件存在时，Redis 先识别文件头。发现 RDB preamble 后，加载器按 RDB 格式一次性恢复大量键；读到 RDB 结束标记后，再按 AOF 协议顺序回放增量命令，最终还原到最近一次成功刷盘的状态。与纯 AOF 从第一条历史命令开始回放相比，这个过程通常明显更快。

## 三种方案对比

| 方案 | 文件体积 | 启动恢复 | 数据完整性 | 主要代价 |
|---|---:|---|---|---|
| 纯 RDB | 最小 | 最快 | 可能丢失一个快照周期 | 实时性较弱 |
| 纯 AOF | 较大 | 较慢 | `everysec` 下通常最多丢约 1 秒 | 重写与回放成本高 |
| 混合持久化 | 较小 | 接近 RDB | 接近 AOF | 文件不再是纯文本，人工可读性降低 |

## 何时开启

推荐所有需要数据可靠性的生产环境开启混合持久化，尤其是数据量大、重启时间敏感，又希望把故障丢失窗口控制在秒级的实例。即使已经部署主从复制，也不能把复制当作持久化备份：错误命令同样会传播到副本。开启后仍需监控 AOF 重写耗时、磁盘空间、`aof_last_bgrewrite_status` 与刷盘延迟，并定期验证备份能否恢复。

**下一步：** [🔙 数据恢复策略](/03-persistence/recovery)
