---
title: HDFS 副本机制
---
# HDFS 副本机制

## 1. 副本策略

```
默认：3 副本（dfs.replication = 3）
写：客户端 → 最近 DataNode → 链式复制到其他节点
读：选最近的副本
```

**优点**：高可用（挂 2 个 DataNode 仍有 1 个副本）
**缺点**：3 倍存储开销

## 2. 副本放置策略（Rack Awareness）

```
默认 3 副本放置：
  1 个本地（同 DN）
  1 个同 rack（不同 DN）
  1 个不同 rack

为什么？
  - 同 rack：网络近，复制快
  - 跨 rack：1 个 rack 挂了数据还在
```

```
  Rack 1           Rack 2
  DN1   DN2        DN3   DN4
   ●     ●          ●
   block 副本 1, 2, 3
```

## 3. 写流程详解

```
1. Client 调 create → NameNode
2. NN 返：block A → [DN1, DN3, DN4]（pipeline）
3. Client → DN1 → DN3 → DN4 串行复制
4. DN1 收到 + DN3 收到 + DN4 收到 = 全部成功
5. DN1 ack Client → Client 关闭文件
6. Client 异步通知 NN 关闭文件（合并 edit log）
```

**关键**：写本地 DN = "first replica" = "close pipe"。

## 4. 副本数调整

```bash
# 单个文件
hdfs dfs -setrep 3 /data/important

# 整个目录
hdfs dfs -setrep -R 3 /data/

# 查看副本数
hdfs dfs -stat %r /data/file    # 3
```

## 5. 副本完整性

```
HDFS 写时检查：所有副本接收完成 + checksum 校验
读时检查：每次读 + 周期校验
后台：DataNode 周期性校验（BlockScanner）
```

不一致 → 标记 corrupt 副本 → 删 + 从其他副本复制

## 6. 副本数 vs 性能

| 副本数 | 写吞吐 | 读吞吐 | 容错 |
|--------|--------|--------|------|
| 1 | 100% | 100% | 无（挂 = 丢）|
| 2 | 50% | 100% | 1 副本故障 |
| 3（默认）| 33% | 100% | 2 副本故障 |
| 5 | 20% | 100% | 4 副本故障 |

**3 副本是 sweet spot**：足够容错 + 不浪费。

## 7. 实战：调整副本

```bash
# 重要数据 → 5 副本
hdfs dfs -setrep 5 /data/critical

# 临时数据 → 2 副本
hdfs dfs -setrep 2 /tmp/staging

# 监控副本
hdfs dfs -ls /data/important  # replication 5
```

## 🔗 下一步
- [HDFS 架构](/02-hdfs/architecture)
- [NameNode HA](/02-hdfs/ha)
