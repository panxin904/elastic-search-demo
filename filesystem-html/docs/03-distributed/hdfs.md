---
title: HDFS 大数据基石
date: 2026-08-15  # date-auto-injected
---

# HDFS 大数据基石

<span class="kg-badge kg-badge-distributed">分布式</span>

Hadoop Distributed File System——PB 级顺序写优化的经典分布式 FS。

## 架构

HDFS 采用**主从架构**：

```
            NameNode（主，元数据）
                ↓
   ┌────────────┼────────────┐
   ↓            ↓            ↓
DataNode 1  DataNode 2  DataNode 3
   ↓            ↓            ↓
  block1      block2       block3
  block2      block3       block1
  block3      block1       block2
```

### NameNode

- **内存中维护整个 FS 树**：文件名 → block → DataNode 列表
- 接收客户端元数据操作（mkdir、ls、rm）
- 接收 DataNode 心跳和 block 报告
- 单点！早期版本是 SPOF（后来用 HA + Zookeeper 解决）

### DataNode

- 存储实际数据块（默认 128 MB）
- 定期向 NameNode 发送**心跳**（3 秒）
- 定期发送 **block 报告**（6 小时）
- 客户端读写数据**直接和 DataNode 通信**

## 副本策略

HDFS 默认 **3 副本**：

```
写入文件 /data/foo.txt
  → 拆成 block1、block2、block3
  → block1 副本分布：
    副本1：本地机架的某 DataNode
    副本2：同机架另一 DataNode
    副本3：不同机架某 DataNode
```

**副本 1 和 2 同机架**：保证写带宽（机架内带宽高）。
**副本 3 跨机架**：保证机架故障时的可用性。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">HDFS 写流程剖析</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">客户端-NameNode-DataNode 三方协同 · Pipeline 流水线</text>

  <!-- 写流程 -->
  <g>
    <text x="50" y="90" font-size="13" font-weight="700" fill="#1e293b">① HDFS 写流程（8 步）</text>

    <rect class="at-hover-card" x="40" y="105" width="100" height="60" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="90" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Client</text>
    <text x="90" y="145" text-anchor="middle" font-size="9" fill="#475569">发起写请求</text>

    <rect class="at-hover-card" x="240" y="105" width="120" height="60" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="300" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">NameNode</text>
    <text x="300" y="145" text-anchor="middle" font-size="9" fill="#475569">元数据 + 副本选址</text>

    <rect class="at-hover-card" x="460" y="105" width="100" height="60" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="510" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">DataNodes</text>
    <text x="510" y="145" text-anchor="middle" font-size="9" fill="#475569">DN1 / DN2 / DN3</text>

    <path d="M140,135 L240,135" stroke="#3b82f6" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="190" y="128" text-anchor="middle" font-size="9" fill="#3b82f6">① create 请求</text>

    <path d="M240,150 L140,150" stroke="#f59e0b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="190" y="178" text-anchor="middle" font-size="9" fill="#f59e0b">② 返回 DN 列表</text>

    <path d="M140,180 L240,180" stroke="#3b82f6" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="190" y="195" text-anchor="middle" font-size="9" fill="#3b82f6">③ write</text>

    <path d="M240,210 L460,210" stroke="#3b82f6" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="350" y="200" text-anchor="middle" font-size="9" fill="#3b82f6">④ 建立 pipeline</text>

    <path d="M460,230 L520,230 L520,260 L100,260 L100,245" stroke="#10b981" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="300" y="252" text-anchor="middle" font-size="9" fill="#10b981">⑤ 流水线写入（packets 沿 DN1→DN2→DN3）</text>

    <path d="M140,280 L240,280" stroke="#10b981" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="190" y="295" text-anchor="middle" font-size="9" fill="#10b981">⑥ ack 确认</text>

    <path d="M140,310 L240,310" stroke="#3b82f6" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="190" y="325" text-anchor="middle" font-size="9" fill="#3b82f6">⑦ close</text>

    <path d="M240,340 L140,340" stroke="#f59e0b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>
    <text x="190" y="358" text-anchor="middle" font-size="9" fill="#f59e0b">⑧ 元数据持久化</text>
  </g>

  <!-- Pipeline 复制 -->
  <g>
    <text x="50" y="380" font-size="13" font-weight="700" fill="#1e293b">② 副本策略 + Pipeline 流水线</text>

    <rect class="at-hover-card" x="40" y="390" width="510" height="40" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="55" y="412" font-size="11" font-weight="700" fill="#047857">副本数（默认 3）</text>
    <text x="180" y="412" font-size="10" fill="#475569">Client → DN1（同 Rack）→ DN2（同 Rack）→ DN3（异 Rack）</text>

    <rect class="at-hover-card" x="40" y="438" width="510" height="32" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="55" y="458" font-size="11" font-weight="700" fill="#92400e">⭐ Pipeline 优势</text>
    <text x="195" y="458" font-size="10" fill="#475569">数据同时流向 3 个 DN（不是串行复制）→ 写带宽 = 单 DN 带宽</text>
  </g>
</svg>

## 写流程

```java
FSDataOutputStream out = fs.create(new Path("/data/foo.txt"));
out.write("hello".getBytes());
out.close();
```

```
1. Client → NameNode: create /data/foo.txt
2. NameNode → Client: 成功（写入 FS tree）
3. Client → NameNode: addBlock for block1
4. NameNode → Client: DataNode 列表（3 个）
5. Client → DataNode1: write block1
6. DataNode1 → DataNode2: 转发（pipeline）
7. DataNode2 → DataNode3: 转发
8. DataNode3 → ack → DataNode2 → DataNode1 → Client
9. Client: 写完成，关闭 block
```

**Pipeline 机制**：副本像管道一样写入，所有 DataNode 串行 ack。

## 读流程

```
1. Client → NameNode: getBlockLocations for /data/foo.txt
2. NameNode → Client: block 位置列表（含每个副本的 DataNode）
3. Client → 最近 DataNode: read block
4. DataNode → Client: 数据流
```

**就近读取**：Client 优先读最近的 DataNode（同节点 → 同机架 → 跨机架）。

## HDFS 的特性

### 适合

- ✅ **大文件顺序读写**：GB ~ TB 级
- ✅ **写一次读多次**：日志、数据仓库
- ✅ **流式访问**：Hadoop MapReduce / Spark
- ✅ **容错**：副本机制 + 心跳检测

### 不适合

- ❌ **小文件**：每个文件都要在 NameNode 内存登记，万级文件就崩溃
- ❌ **低延迟访问**：ms ~ s 级延迟
- ❌ **频繁修改**：HDFS 文件一旦写入基本不修改（append 有限支持）
- ❌ **强一致性**：最终一致

## 容错机制

### DataNode 故障

```
NameNode 10 分钟没收到 DataNode 心跳
  → 标记为 dead
  → 查找该 DataNode 上的 block
  → 触发副本复制（补足到 3 副本）
```

### Block 损坏

```
Client 读 block 时 checksum 错误
  → 报告 NameNode
  → NameNode 标记该副本为 corrupt
  → 触发复制
```

### NameNode 故障（HDFS HA）

```
Active NameNode ← ZKFC ← Zookeeper
  ↓ 故障
Standby NameNode 接管（通过 Zookeeper 选举）
  ↓
共享 EditLog（JournalNode 集群）
```

## Federation（联邦）

HDFS 单 NameNode 内存受限（~100M 文件上限）。HDFS Federation 允许**多 NameNode**：

```
ns1 (Nameservice 1) → /data/foo
ns2 (Nameservice 2) → /user/bar
ns3 (Nameservice 3) → /logs/baz
```

不同 namespace 独立扩展，共享 DataNode 集群。

## 实战

```bash
# HDFS 命令
hdfs dfs -ls /
hdfs dfs -mkdir /user/alice
hdfs dfs -put local.txt /data/foo.txt
hdfs dfs -cat /data/foo.txt
hdfs dfs -du -h /data
hdfs dfs -df -h /

# 看 block 信息
hdfs fsck /data/foo.txt -files -blocks

# 平衡器（新加 DataNode 后）
hdfs balancer -threshold 10

# Namenode 安全模式（只读）
hdfs dfsadmin -safemode enter
hdfs dfsadmin -safemode leave

# 报告
hdfs dfsadmin -report
```

## 配置关键参数（hdfs-site.xml）

```xml
<!-- block 大小 -->
<property>
  <name>dfs.blocksize</name>
  <value>134217728</value>  <!-- 128 MB -->
</property>

<!-- 副本数 -->
<property>
  <name>dfs.replication</name>
  <value>3</value>
</property>

<!-- NameNode 心跳 -->
<property>
  <name>dfs.heartbeat.interval</name>
  <value>3</value>  <!-- 秒 -->
</property>

<!-- 块报告间隔 -->
<property>
  <name>dfs.blockreport.intervalMsec</name>
  <value>21600000</value>  <!-- 6 小时 -->
</property>
```

## 替代品：HDFS 是不是过时了？

HDFS 仍在用，但对象存储（S3）正在取代它：

| 维度 | HDFS | S3 / 对象存储 |
|------|------|--------------|
| 计算分离 | ❌（紧耦合）| ✅ |
| 成本 | 高（专用集群） | 低（按量） |
| 扩展性 | 受 NameNode 限 | 无限 |
| 延迟 | ms ~ s | 30-200 ms |
| 协议 | HDFS RPC | HTTP REST |
| 生态 | Hadoop | 全云生态 |

**云原生时代**：越来越多 Hadoop 部署在 S3 上跑（Spark on S3），HDFS 主要在自建机房场景。

## 关键 takeaway

| 优势 | 劣势 |
|------|------|
| 成熟稳定 | NameNode 单点（HA 后缓解） |
| 顺序写性能强 | 不适合小文件 |
| Hadoop 生态原生 | 不适合低延迟 |
| 副本容错 | 与计算耦合 |
| 简单（仅追加） | 难以替代对象存储 |