---
title: 刷盘机制
---

# 📜 刷盘机制

> Kafka 通过 **fsync 系统调用**将 Page Cache 中的数据持久化到磁盘。本章详解刷盘机制对**数据安全**与**性能**的影响。

## 🎯 什么是刷盘？

```
刷盘 = Page Cache（内存）→ 磁盘（持久化）

写入流程：
  消息 → Page Cache（内存）→ 立即返回 ack
                              ↓
                          后台线程异步 fsync

fsync：
  - 系统调用
  - 强制将 Page Cache 写入磁盘
  - 确保数据持久化（宕机不丢失）
```

## 📊 写入与刷盘的时序

```
时间线：
  T0   Producer 发送 msg
  T1   Leader 写入 Page Cache
  T2   Leader 返回 ack
  T3   Page Cache 仍在内存（未刷盘）
  T4   后台线程 fsync 到磁盘
  T5   数据完全持久化

⚠️ 关键：
  - T2 后即使 Broker 宕机，msg 丢失（Page Cache 没刷盘）
  - 只有 T5 后，宕机才不丢数据
```

## ⚙️ 刷盘配置

```properties
# ==== Kafka 主动刷盘 ====
log.flush.interval.messages=10000   # 每 10000 条消息 fsync
log.flush.interval.ms=1000          # 每 1 秒 fsync

# ==== OS 后台刷盘（默认行为） ====
# Kafka 不主动 fsync 时，依赖 OS 后台 flush
# 一般 30 秒左右自动 flush

# ==== 数据安全性配置 ====
replication.factor=3              # 3 副本冗余
min.insync.replicas=2             # 至少 2 个副本写入
acks=all                           # 等所有 ISR 写入
```

## 📊 刷盘策略对比

### 不主动 fsync（默认）

```
✅ 优点：
  - 写延迟最低（不阻塞主线程）
  - 吞吐最高（无 fsync 开销）

❌ 缺点：
  - 宕机可能丢失 Page Cache 中数据（最多丢失几秒）
  - 需要靠副本机制（acks=all + min.insync.replicas）保证不丢
```

### 主动 fsync（配置刷盘）

```
✅ 优点：
  - 数据更安全（立即持久化）
  - 减少丢失窗口

❌ 缺点：
  - 写延迟增加（10-100ms）
  - 吞吐降低（fsync 是阻塞 IO）
```

### 推荐配置

```properties
# ⚠️ 生产环境推荐：
# 不主动 fsync（依赖 OS 后台）
log.flush.interval.messages=9223372036854775807  # 不主动 fsync
log.flush.interval.ms=9223372036854775807          # 不主动 fsync

# 数据安全靠：
acks=all + min.insync.replicas=2 + replication.factor=3
```

## 📊 数据丢失窗口分析

### 场景 1：不主动 fsync + 单副本

```
时间线：
  T0   Producer 发送 msg
  T1   Leader 写入 Page Cache
  T2   Leader 返回 ack
  T3   Broker 宕机（Page Cache 丢失）
  T4   Broker 重启
  T5   msg 丢失！

丢失窗口：从 T2 到 T3（通常几秒）
丢失率：100%（Page Cache 中数据全部丢失）
```

### 场景 2：不主动 fsync + 3 副本 + min.insync.replicas=2

```
时间线：
  T0   Producer 发送 msg（acks=all）
  T1   Leader 写入 Page Cache
  T2   Follower 1 写入 Page Cache（同步）
  T3   Follower 2 写入 Page Cache（同步）
  T4   Leader 返回 ack（min.insync.replicas 满足）
  T5   Broker 1 宕机
  T6   Follower 2 晋升为 Leader
  T7   msg 在新 Leader 上（不丢）

丢失窗口：从 T4 到 T5（< 几秒）
丢失率：0%（多副本冗余）
```

### 场景 3：主动 fsync + 单副本

```
时间线：
  T0   Producer 发送 msg
  T1   Leader 写入 Page Cache
  T2   Leader fsync 到磁盘（阻塞）
  T3   Leader 返回 ack
  T4   Broker 宕机
  T5   Broker 重启（msg 在磁盘）
  T6   msg 不丢！

丢失率：0%（fsync 保证）
性能：写延迟 10-100ms（fsync 开销）
```

## 📊 fsync 性能影响

```
测试场景：NVMe SSD，单 Broker

配置                          吞吐        P99 延迟
不主动 fsync                  200 MB/s    < 5 ms
fsync 10000 条               150 MB/s    < 20 ms
fsync 1 条（每次都 fsync）    20 MB/s     50-100 ms

推荐：
  - 依赖 OS 后台 fsync
  - 副本机制保证可靠性
  - 避免主动 fsync
```

## 🛠️ OS 后台 fsync 调优

```bash
# 查看 OS 脏页刷新策略
cat /proc/sys/vm/dirty_ratio
cat /proc/sys/vm/dirty_background_ratio

# 调整（SSD 环境）
sysctl -w vm.dirty_ratio=10
sysctl -w vm.dirty_background_ratio=5

# 强制刷新（紧急情况）
sync  # 同步所有挂起的写入
```

## 📊 监控刷盘

### 关键指标

```bash
# 查看 Kafka 刷盘状态
iostat -x 1
# 看 wKB/s 和 %util

# 查看 OS Page Cache
free -h
cat /proc/meminfo | grep -i "cache\|dirty"
```

### 监控告警

```yaml
- alert: KafkaDiskWriteHigh
  expr: rate(node_disk_written_bytes_total[5m]) > 100 * 1024 * 1024  # 100 MB/s
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Kafka 磁盘写入速率过高"
```

## 🎯 总结

**刷盘机制核心要点**：
- ✅ Kafka 默认不主动 fsync（依赖 OS 后台）
- ✅ 推荐：acks=all + 多副本保证安全
- ✅ 主动 fsync 影响性能（不推荐）
- ⚠️ 单副本 + 不 fsync = 必丢数据
- ⚠️ 副本机制是数据安全的核心

**下一步：** [🗑️ 数据恢复策略](/03-persistence/recovery) — 灾难恢复