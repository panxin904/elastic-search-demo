---
title: HDFS 架构
date: 2026-08-15  # date-auto-injected
---
# HDFS 架构

## 1. 整体架构

```
        NameNode (Master)
        - 元数据（fsimage + edit log）
        - 内存中维护文件系统树
        - 单点（HA 用 Standby）

        DataNode (Slave, N 个)
        - 存数据块
        - 定期向 NameNode 发送心跳
        - 存副本（默认 3 份）

        Client
        - 写：先写本地 → 复制到其他节点
        - 读：先到 NameNode 拿位置 → 到对应 DataNode 读
```

## 2. 核心概念

### 块（Block）

```
默认 128 MB（Hadoop 3.x 可配 256 MB）
大文件被切块：
  1 GB 文件 → 8 块（每块 128 MB）
  100 MB 文件 → 1 块
```

**优点**：大块减少 NameNode 寻址开销
**缺点**：小文件浪费（一个块只放一个小文件）

### 副本（Replication）

```
默认 3 副本：dfs.replication = 3
写：客户端 → 1 个 DataNode → 链式复制到其他 2 个
读：NameNode 告诉客户端最近副本
```

**rack awareness**：副本跨机架（默认）

```
        rack1          rack2
        DN1   DN2   DN3   DN4
   block1  1/2/3  block1 block1   (1个主 + 2个副本在不同 rack)
```

### NameNode 元数据

```
1. fsimage：文件系统元数据快照（定期 merge）
2. edit log：所有修改操作（append）
3. 启动时：load fsimage + replay edit log

元数据 = 整个文件系统的 inode 表
- 目录树
- 文件名 → 块映射
- 块 → DataNode 列表
```

**NameNode 单点风险**：所有元数据在内存，挂了 = 数据丢失。
**解决**：Secondary NameNode → NameNode HA（JournalNode + ZooKeeper / ZKFC）

## 3. NameNode HA

### QJM（Quorum Journal Manager）

```
NameNode-1  ←──→  JournalNode  ←──→  NameNode-2
   (Active)        (Journal)         (Standby)
```

写 edit log → JournalNode（多数写成功）
Active 挂了 → Standby 从 JournalNode 拉 log → 接管

### ZKFC（ZK Failover Controller）

```
NameNode 通过 ZK 选主：
  - 健康检查（fencing）
  - 选举（避免脑裂）
  - 切换
```

## 4. 数据写入流程

```
1. Client 调 create("/data/a.txt", data)
2. Client 问 NameNode：要写哪些块？
   NN 返：block1 → [DN1, DN3, DN4]（距离近）
3. Client → DN1（最近的）
4. DN1 → DN3 → DN4 链式复制
5. DN1 ack → Client
6. Client 异步通知 NN 关闭文件
```

**强一致**（一次写成功 = 3 个副本都成功）。

## 5. 数据读取流程

```
1. Client 调 read("/data/a.txt")
2. Client 问 NameNode：a.txt 在哪些块？
   NN 返：block1 → [DN1, DN2, DN3]
3. Client 选最近的 DN（按网络拓扑）
4. Client 直连 DN 读 block1
5. DN 返数据
```

**就近读取**，减少跨 rack 流量。

## 6. 容错机制

| 故障 | 处理 |
|------|------|
| DataNode 挂 | NameNode 收不到心跳（10 min）→ 标记 dead → 副本复制 |
| NameNode 挂 | Standby 接管（fencing + ZK 选举）|
| 副本不一致 | 后台 Reconciliation 线程修复 |
| 写入一半失败 | 重新选副本完成 |
| 读失败 | 自动重试另一个副本 |

## 7. HDFS Federation

```
NameNode 单点 → 内存有限（10亿文件）
→ Federation：多 NameNode，各管一部分命名空间

/cluster1 (NameNode 1)
/cluster2 (NameNode 2)
/cluster3 (NameNode 3)
```

Router 路由到对应 NameNode。

## 8. 实战命令

```bash
hdfs dfs -ls /                          # 列出
hdfs dfs -put local.txt /data/in/      # 上传
hdfs dfs -get /data/out/ ./          # 下载
hdfs dfs -cat /data/file             # 看内容
hdfs dfs -du -h /data/              # 看大小
hdfs dfs -chown alice:alice /data   # 改属主
hdfs dfs -chmod 755 /data           # 改权限
hdfs dfs -df -h                    # 看使用
hdfs dfsadmin -report               # 集群报告
hdfs dfsadmin -safemode get         # 安全模式
hdfs haadmin -getServiceState nn1   # NN HA 状态
hdfs fsck /                          # 检查
hdfs balancer -threshold 10        # 平衡
hdfs dfs -setrep 3 /data/important  # 设副本数
hdfs dfs -getfacl /data/file        # 看 ACL
hdfs dfs -put -p /dir1 /dir2 /       # 创建父目录
hdfs dfs -getmerge /data/*.csv out.csv  # 合并下载
```

## 9. 性能调优

| 场景 | 调优 |
|------|------|
| 小文件多 | 合并 + HFile / ORC + HAR |
| 大文件 | 增大 block size（Hadoop 3.x: 256 MB） |
| 写少读多 | 启用 Short-Circuit Read |
| 远程读 | 启用 Hedged Reads |
| DataNode 磁盘满 | 启用 Balancer / DiskBalancer |

## 10. 现代数据栈的 HDFS 现状

```
HDFS → 仍是主流分布式存储
但：对象存储（S3 / OSS）崛起
  - HDFS 优势：本地 + 强一致 + 大数据生态
  - S3 优势：无限扩展 + 成本低 + 云原生
  - 趋势：HDFS 落本地 + S3 落云端（混合云）

HDFS → 对象存储迁移是趋势
但 Hadoop 生态（Hive / Spark）仍大量使用 HDFS
```

## 🔗 下一步
- [副本机制](/02-hdfs/replication)
- [NameNode HA](/02-hdfs/ha)
- [HDFS 命令](/02-hdfs/commands)

<!-- svg-injected:do-not-edit -->

## 图示：HDFS NameNode/DataNode 副本策略

![HDFS NameNode/DataNode 副本策略](/hdfs-architecture.svg)
