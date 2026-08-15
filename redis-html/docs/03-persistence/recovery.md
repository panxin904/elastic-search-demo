---
title: 数据恢复策略
---

# 数据恢复策略

持久化文件只有经过验证并能成功恢复，才算真正的备份。生产环境应先明确 Redis 的启动选择、文件修复边界和异地备份流程，再定期演练，而不是等故障发生后临时研究命令。

## 启动时的数据加载顺序

Redis 并不会把 RDB 和 AOF 各加载一遍。当 `appendonly yes` 且有效 AOF 存在时，启动过程 **优先加载 AOF**，因为它通常比 RDB 更新；只有 AOF 未启用或文件不存在时，才回退加载 RDB。若启用了混合持久化，AOF 内部会先按 RDB 格式恢复全量数据，再回放尾部的 AOF 增量命令。

```ini
# redis.conf
dir /var/lib/redis
dbfilename dump.rdb
appendonly yes
appenddirname "appendonlydir"
aof-use-rdb-preamble yes
appendfsync everysec

save 900 1
save 300 10
save 60 10000
```

因此，故障处理时不要只替换 `dump.rdb` 就直接启动：只要旧 AOF 仍然存在且 AOF 已开启，Redis 仍会优先读取 AOF，新放入的 RDB 可能完全不会被采用。

## 检查与修复持久化文件

`redis-check-rdb` 用于检查 RDB 结构，`redis-check-aof` 用于检查 AOF，并可通过 `--fix` 截断损坏尾部。修复会丢弃最后一个有效偏移之后的内容，操作前必须停止 Redis，并保留原始文件副本。

```bash
sudo systemctl stop redis
cp /var/lib/redis/dump.rdb /recovery/dump.rdb.broken
cp -a /var/lib/redis/appendonlydir /recovery/appendonlydir.broken

redis-check-rdb /var/lib/redis/dump.rdb
redis-check-aof /var/lib/redis/appendonly.aof
redis-check-aof --fix /var/lib/redis/appendonly.aof
```

Redis 7 的多部件 AOF 由 manifest、base 和 incr 文件组成，应根据报错检查 manifest 指向的实际文件，不要随意改名或拼接。完成修复后，先在隔离实例上启动，核对键数量、关键业务数据和日志，再替换生产文件。

## 灾难恢复场景

| 场景 | 首要动作 | 恢复路径 | 注意事项 |
|---|---|---|---|
| RDB、AOF 都损坏 | 停止实例并复制现场 | 从最近一次异地备份恢复，再补业务日志 | 原文件不可覆盖 |
| 数据盘损坏 | 隔离故障盘并更换磁盘 | 在新节点恢复备份，校验后切流 | 不要反复写入故障盘 |
| 误执行 `FLUSHALL` | 立即阻断写入与复制 | 恢复操作前备份，必要时重放后续业务事件 | 删除命令可能已传播到副本和 AOF |

若 `FLUSHALL` 已进入 AOF、RDB 也已重新生成，并且没有历史备份或上游业务日志，Redis 自身无法找回被删除的数据。副本提供高可用，但不能替代独立备份。

## 定时备份与异地同步

可以使用 `redis-cli --rdb` 生成一致性快照，校验后再通过 `rsync` 发送到异地存储。凭据应通过受限配置文件或密钥管理系统提供，不要硬编码在脚本中。

```bash
#!/usr/bin/env bash
set -euo pipefail
STAMP=$(date +%Y%m%d-%H%M%S)
DEST="/backup/redis/${STAMP}"
mkdir -p "$DEST"

redis-cli --rdb "$DEST/dump.rdb"
redis-check-rdb "$DEST/dump.rdb"
sha256sum "$DEST/dump.rdb" > "$DEST/SHA256SUMS"
rsync -a --partial "$DEST/" backup@10.0.20.15:"/data/redis/${STAMP}/"
```

## 生产最佳实践

遵循 **3-2-1 原则**：至少保留 3 份数据，使用 2 种不同介质，其中 1 份位于异地或不可变存储。生产实例开启混合持久化，监控最近一次 RDB/AOF 操作状态与磁盘余量；备份按小时、天、周设置不同保留周期，并校验哈希。至少每季度做一次从空节点开始的恢复演练，记录恢复点目标（RPO）、恢复时间目标（RTO）及实际耗时，确保值班人员能按手册完成操作。

**下一步：** [🔁 主从复制](/04-cluster/replication)
