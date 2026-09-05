---
title: 分区副本机制
date: 2026-08-15  # date-auto-injected
---

# 🗂️ 分区副本机制

> **副本（Replica）**是 Kafka 高可用的基石。每个 Partition 有多个副本，分布在不同 Broker，Leader 故障时自动选举新 Leader。

## 🎯 副本机制基础

### 副本结构

```
Topic: orders (replication-factor=3)
├── Partition 0
│   ├── Replica 0 (Leader) on Broker 1    ← 处理读写
│   ├── Replica 1 (Follower) on Broker 2  ← 同步数据
│   └── Replica 2 (Follower) on Broker 3  ← 同步数据
├── Partition 1
│   ├── Replica 0 (Leader) on Broker 2
│   ├── Replica 1 (Follower) on Broker 3
│   └── Replica 2 (Follower) on Broker 1
└── Partition 2
    ├── Replica 0 (Leader) on Broker 3
    ├── Replica 1 (Follower) on Broker 1
    └── Replica 2 (Follower) on Broker 2
```

### 关键术语

```
AR（Assigned Replicas）
  - 分区所有副本的集合
  - 由副本分配策略决定

ISR（In-Sync Replicas）
  - 与 Leader 保持同步的副本
  - 故障转移时只从 ISR 选 Leader

OSR（Out-of-Sync Replicas）
  - 落后 Leader 太多的副本
  - 不在 ISR 列表中

Leader Replica
  - 处理读写请求
  - 由 Controller 选举

Follower Replica
  - 从 Leader 拉取数据
  - 备用 Leader
```

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
    <marker id="arrG" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#10b981"/>
    </marker>
    <marker id="arrR" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#dc2626"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Kafka ISR 与副本同步机制</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">In-Sync Replicas · Leader Epoch · HW/LEO · replica.lag.time.max.ms</text>

  <!-- ISR 集合 -->
  <g>
    <text x="60" y="95" font-size="13" font-weight="700" fill="#1e293b">partition-0 副本集（replication.factor=3）</text>

    <!-- Leader -->
    <rect class="at-hover-card" x="60" y="115" width="120" height="60" rx="8" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="120" y="138" text-anchor="middle" font-size="13" font-weight="700" fill="#1e40af">Leader (B1)</text>
    <text x="120" y="155" text-anchor="middle" font-size="10" fill="#475569">offset: 100</text>
    <text x="120" y="170" text-anchor="middle" font-size="10" fill="#065f46" font-weight="700">★ ISR</text>

    <!-- Follower 1 -->
    <rect class="at-hover-card" x="220" y="115" width="120" height="60" rx="8" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="280" y="138" text-anchor="middle" font-size="13" font-weight="700" fill="#065f46">Follower (B2)</text>
    <text x="280" y="155" text-anchor="middle" font-size="10" fill="#475569">offset: 100</text>
    <text x="280" y="170" text-anchor="middle" font-size="10" fill="#065f46" font-weight="700">★ ISR</text>

    <!-- Follower 2 (lagging) -->
    <rect class="at-hover-card" x="380" y="115" width="120" height="60" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4"/>
    <text x="440" y="138" text-anchor="middle" font-size="13" font-weight="700" fill="#92400e">Follower (B3)</text>
    <text x="440" y="155" text-anchor="middle" font-size="10" fill="#475569">offset: 95 (落后 5)</text>
    <text x="440" y="170" text-anchor="middle" font-size="10" fill="#dc2626" font-weight="700">× OUT of ISR</text>

    <!-- 同步箭头 -->
    <line x1="180" y1="135" x2="220" y2="135" stroke="#10b981" stroke-width="1.5" marker-end="url(#arrG)"/>
    <text x="200" y="128" text-anchor="middle" font-size="9" fill="#065f46">fetch</text>
    <line x1="180" y1="155" x2="380" y2="155" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arrR)" stroke-dasharray="3"/>
    <text x="280" y="148" text-anchor="middle" font-size="9" fill="#dc2626">慢 → 被踢出 ISR</text>
  </g>

  <!-- HW/LEO -->
  <g>
    <text x="60" y="205" font-size="13" font-weight="700" fill="#1e293b">HW（High Watermark）与 LEO</text>

    <rect class="at-hover-card" x="60" y="225" width="480" height="70" rx="6" fill="#f1f5f9" stroke="#94a3b8"/>
    <text x="80" y="248" font-size="11" fill="#475569">Log segments（offset 90 → 100）</text>

    <!-- 9 个格子 -->
    <g font-family="monospace" font-size="9">
      <rect x="80" y="258" width="48" height="28" fill="#ffffff" stroke="#cbd5e1"/>
      <text x="104" y="276" text-anchor="middle" fill="#64748b">90</text>
      <rect x="130" y="258" width="48" height="28" fill="#dbeafe" stroke="#3b82f6"/>
      <text x="154" y="276" text-anchor="middle" fill="#1e40af">91</text>
      <rect x="180" y="258" width="48" height="28" fill="#dbeafe" stroke="#3b82f6"/>
      <text x="204" y="276" text-anchor="middle" fill="#1e40af">92</text>
      <rect x="230" y="258" width="48" height="28" fill="#dbeafe" stroke="#3b82f6"/>
      <text x="254" y="276" text-anchor="middle" fill="#1e40af">93</text>
      <rect x="280" y="258" width="48" height="28" fill="#dbeafe" stroke="#3b82f6"/>
      <text x="304" y="276" text-anchor="middle" fill="#1e40af">94</text>
      <rect x="330" y="258" width="48" height="28" fill="#fef3c7" stroke="#f59e0b"/>
      <text x="354" y="276" text-anchor="middle" fill="#92400e">95</text>
      <rect x="380" y="258" width="48" height="28" fill="#fef3c7" stroke="#f59e0b"/>
      <text x="404" y="276" text-anchor="middle" fill="#92400e">96</text>
      <rect x="430" y="258" width="48" height="28" fill="#fef3c7" stroke="#f59e0b"/>
      <text x="454" y="276" text-anchor="middle" fill="#92400e">97</text>
      <rect x="480" y="258" width="48" height="28" fill="#f1f5f9" stroke="#cbd5e1" stroke-dasharray="3"/>
      <text x="504" y="276" text-anchor="middle" fill="#94a3b8">98-100</text>
    </g>

    <!-- HW 线 -->
    <line x1="475" y1="248" x2="475" y2="295" stroke="#dc2626" stroke-width="2" stroke-dasharray="4"/>
    <text x="475" y="245" text-anchor="middle" font-size="10" font-weight="700" fill="#dc2626">HW=95</text>
    <text x="475" y="307" text-anchor="middle" font-size="9" fill="#dc2626">Consumer 可见上限</text>
  </g>

  <!-- Leader Epoch 防脑裂 -->
  <g>
    <text x="60" y="325" font-size="13" font-weight="700" fill="#1e293b">Leader Epoch 防脑裂（旧 Leader 复活场景）</text>

    <rect class="at-hover-card" x="60" y="345" width="480" height="100" rx="6" fill="#f8fafc" stroke="#cbd5e1"/>

    <text x="80" y="367" font-size="11" fill="#475569">t=0  L=B1, epoch=1, HW=100</text>
    <text x="80" y="385" font-size="11" fill="#dc2626">t=10  B1 宕机</text>
    <text x="80" y="403" font-size="11" fill="#475569">t=15  B2 晋升 Leader, epoch=2, HW=100</text>
    <text x="80" y="421" font-size="11" fill="#475569">t=20  B1 复活 → 携带 epoch=1 请求写入</text>
    <text x="80" y="439" font-size="11" fill="#10b981" font-weight="700">     B2 拒绝（epoch=2 &gt; 1）→ 自动 step down → 重新加入 ISR</text>
  </g>

  <!-- 关键配置 -->
  <g>
    <rect class="at-hover-card" x="40" y="455" width="520" height="20" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="60" y="470" font-size="11" font-weight="700" fill="#1e40af">关键配置：acks=all · min.insync.replicas=2 · replica.lag.time.max.ms=30000 · unclean.leader.election.enable=false</text>
  </g>
</svg>
## 🔄 副本同步流程

### Follower 拉取同步

```
时间线：
  T0   Leader 写入 msg(offset=100)
  T1   Leader 更新 LEO（Log End Offset）= 101
  T2   Follower 发送 FetchRequest(startOffset=99)
  T3   Leader 返回 msg + 元数据
  T4   Follower 写入本地 log
  T5   Follower 更新 LEO = 100
  T6   Follower 发送 FetchRequest(startOffset=100)
  T7   Leader 返回 msg + 元数据
  T8   Follower 写入本地 log
  T9   Follower 更新 LEO = 101
```

### 关键概念

```
LEO（Log End Offset）
  - 日志末端偏移量
  - 表示副本写入到哪里

HW（High Watermark）
  - 已提交偏移量（消费者可见的边界）
  - HW = min(所有 ISR 的 LEO)
  - 消费者只能读到 HW 之前的数据

LSO（Log Start Offset）
  - 日志起始偏移量（默认 0）
  - 因消息删除可能大于 0
```

```
Partition (Leader):  [m0 m1 m2 m3 m4 m5]    LEO=6, HW=4
Partition (Follower A): [m0 m1 m2 m3]    LEO=4   ← 同步
Partition (Follower B): [m0 m1 m2 m3 m4]  LEO=5   ← 稍慢

HW = min(LEO_A, LEO_B, LEO_Leader) = 4
Consumer 只能看到 offset 0-3
m4、m5 已写入 Leader，但还未被所有 Follower 同步
```

## ⚙️ 副本同步配置

```properties
# ==== 副本相关配置 ====
default.replication.factor=3        # Topic 默认副本数
min.insync.replicas=2               # 最小同步副本数（影响 acks=all 行为）
replica.fetch.min.bytes=1           # 拉取最小字节（减少小请求）
replica.fetch.max.bytes=1048576     # 拉取最大字节（默认 1MB）
replica.fetch.wait.max.ms=500       # 长轮询等待时间

# ==== ISR 管理 ====
replica.lag.time.max.ms=30000       # Follower 超时时间（默认 30s）
# 超过这个时间被踢出 ISR

# ==== 落后副本处理 ====
unclean.leader.election.enable=false # 是否允许 OSR 当 Leader（关闭更安全）
```

## 📊 副本与生产者关系

### acks 配置（生产者端）

```java
Properties props = new Properties();
props.put(ProducerConfig.ACKS_CONFIG, "all");
```

| acks 值 | 行为 | 可靠性 | 性能 |
|---------|------|--------|------|
| **0** | 不等响应 | ❌ 可能丢失 | ⭐⭐⭐⭐⭐ |
| **1** | 等 Leader 写入 | ⚠️ Leader 故障可能丢失 | ⭐⭐⭐⭐ |
| **all** (或 -1) | 等所有 ISR 写入 | ✅ 强保证 | ⭐⭐ |

```
acks=all + min.insync.replicas=2：
  - Leader 写入 + ISR 中至少 1 个 Follower 写入 = 才返回成功
  - 即使 Leader 故障，剩余 ISR 中有完整数据
  - 最安全的配置
```

## 📊 副本与消费者关系

```
Consumer 只能读取 HW 之前的数据：

Producer 发送 m5 → Leader 写入 → Follower 同步
                                              ↓
                                          HW=5（所有 ISR 同步完成）
                                          ↓
Consumer.poll() 读取 → 看到 m0~m4 + m5

Producer 发送 m6 → Leader 写入 → Follower 未同步
                                              ↓
                                          HW=5（Follower 还没追上）
                                          ↓
Consumer.poll() 读取 → 只看到 m0~m4（HW 边界）
```

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Kafka Unclean Leader Election</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">可用性 vs 一致性 · 丢数据 vs 不可服务</text>

  <!-- 概念 -->
  <g>
    <text x="60" y="90" font-size="13" font-weight="700" fill="#1e293b">① ISR / OSR / Leader 关系</text>

    <rect class="at-hover-card" x="40" y="105" width="520" height="100" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="55" y="120" width="160" height="70" rx="4" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="135" y="140" text-anchor="middle" font-size="11" font-weight="700" fill="#065f46">ISR (in-sync)</text>
    <text x="135" y="158" text-anchor="middle" font-size="9" fill="#475569">同步副本集</text>
    <text x="135" y="175" text-anchor="middle" font-size="9" fill="#475569">可被选为 Leader</text>
    <text x="135" y="187" text-anchor="middle" font-size="9" font-weight="700" fill="#065f46">推荐 ✅</text>

    <rect class="at-hover-card" x="225" y="120" width="160" height="70" rx="4" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="305" y="140" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">OSR (out-of-sync)</text>
    <text x="305" y="158" text-anchor="middle" font-size="9" fill="#475569">落后副本</text>
    <text x="305" y="175" text-anchor="middle" font-size="9" fill="#475569">默认不可被选</text>
    <text x="305" y="187" text-anchor="middle" font-size="9" font-weight="700" fill="#92400e">需 unclean 开启</text>

    <rect class="at-hover-card" x="395" y="120" width="160" height="70" rx="4" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="475" y="140" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">unclean 开启</text>
    <text x="475" y="158" text-anchor="middle" font-size="9" fill="#475569">允许 OSR 选 Leader</text>
    <text x="475" y="175" text-anchor="middle" font-size="9" fill="#475569">→ 高可用</text>
    <text x="475" y="187" text-anchor="middle" font-size="9" font-weight="700" fill="#dc2626">⚠️ 丢数据风险</text>
  </g>

  <!-- 故障场景 -->
  <g>
    <text x="60" y="225" font-size="13" font-weight="700" fill="#1e293b">② 场景：Leader 宕机 + ISR 全挂</text>

    <rect class="at-hover-card" x="40" y="240" width="520" height="100" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="60" y="255" width="60" height="35" rx="3" fill="#fee2e2" stroke="#dc2626"/>
    <text x="90" y="270" text-anchor="middle" font-size="9" font-weight="700" fill="#991b1b">L0</text>
    <text x="90" y="285" text-anchor="middle" font-size="8" fill="#475569">Leader</text>
    <text x="90" y="297" text-anchor="middle" font-size="8" fill="#475569">宕</text>

    <rect class="at-hover-card" x="140" y="255" width="60" height="35" rx="3" fill="#fee2e2" stroke="#dc2626"/>
    <text x="170" y="270" text-anchor="middle" font-size="9" font-weight="700" fill="#991b1b">F1</text>
    <text x="170" y="285" text-anchor="middle" font-size="8" fill="#475569">Follower</text>
    <text x="170" y="297" text-anchor="middle" font-size="8" fill="#475569">宕</text>

    <rect class="at-hover-card" x="220" y="255" width="60" height="35" rx="3" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="250" y="270" text-anchor="middle" font-size="9" font-weight="700" fill="#92400e">F2</text>
    <text x="250" y="285" text-anchor="middle" font-size="8" fill="#475569">Follower</text>
    <text x="250" y="297" text-anchor="middle" font-size="8" fill="#475569">OSR</text>

    <rect class="at-hover-card" x="300" y="255" width="60" height="35" rx="3" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="330" y="270" text-anchor="middle" font-size="9" font-weight="700" fill="#92400e">F3</text>
    <text x="330" y="285" text-anchor="middle" font-size="8" fill="#475569">Follower</text>
    <text x="330" y="297" text-anchor="middle" font-size="8" fill="#475569">OSR</text>

    <text x="380" y="270" font-size="10" font-weight="700" fill="#1e293b">ISR = {}</text>
    <text x="380" y="290" font-size="9" fill="#475569">所有 in-sync 副本都不可用</text>

    <text x="60" y="320" font-size="10" fill="#475569">⚠️ 此时若不允许 unclean：partition 不可用，等待 OSR 追上</text>
  </g>

  <!-- 决策 -->
  <g>
    <text x="60" y="358" font-size="13" font-weight="700" fill="#1e293b">③ 两种策略对比</text>

    <rect class="at-hover-card" x="40" y="373" width="250" height="90" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="165" y="393" text-anchor="middle" font-size="12" font-weight="700" fill="#065f46">unclean.leader.election.enable=false（默认）</text>
    <text x="55" y="413" font-size="10" font-weight="700" fill="#1e293b">✅ 强一致</text>
    <text x="55" y="430" font-size="9" fill="#475569">ISR 全挂时拒绝选主</text>
    <text x="55" y="445" font-size="9" fill="#475569">→ partition 不可用</text>
    <text x="55" y="458" font-size="9" fill="#475569">→ 等待 F2/F3 追上</text>

    <rect class="at-hover-card" x="310" y="373" width="250" height="90" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="435" y="393" text-anchor="middle" font-size="12" font-weight="700" fill="#991b1b">unclean.leader.election.enable=true</text>
    <text x="325" y="413" font-size="10" font-weight="700" fill="#1e293b">✅ 高可用</text>
    <text x="325" y="430" font-size="9" fill="#475569">F2/F3 直接被选为 Leader</text>
    <text x="325" y="445" font-size="9" fill="#dc2626">⚠️ 丢失 L0/F1 未同步消息</text>
    <text x="325" y="458" font-size="9" fill="#475569">→ 适合：日志可重建</text>
  </g>
</svg>
## ⚠️ 副本同步异常场景

### 场景 1：Follower 落后

```
原因：Follower GC、网络故障、磁盘慢
处理：
  1. 超过 replica.lag.time.max.ms（30s）被踢出 ISR
  2. OSR 不参与 Leader 选举
  3. Follower 恢复后，重新追上 Leader，加入 ISR

影响：
  - Leader 选举时，OSR 不可选
  - acks=all 时不等待 OSR（只等 ISR）
```

### 场景 2：Leader 故障

```
原因：Leader Broker 宕机
处理流程：
  1. Controller 检测到 Leader 失联（超时）
  2. 从 ISR 中选新 Leader
  3. Producer 收到 MetadataResponse，更新到新 Leader
  4. Consumer 收到 FetchResponse，自动重连新 Leader

Producer 处理：
  - 自动重试（retries 配置）
  - 幂等性保证（enable.idempotence=true）
```

### 场景 3：所有 ISR 不可用

```
现象：Leader 故障，且 ISR 中所有 Follower 都不可用
处理：
  - 如果 unclean.leader.election.enable=false
    → 等待旧 Leader 恢复（分区不可用）
  - 如果 unclean.leader.election.enable=true
    → 从 OSR 中选新 Leader（可能数据丢失，但分区可用）
```

## 🔧 副本分配策略

### 默认分配策略

```java
// Kafka 0.11+ 默认分配策略
// 目标：均匀分配副本到所有 Broker
// 规则：
//   1. 副本因子 ≤ Broker 数量
//   2. 第一个副本随机选择
//   3. 其他副本选择不同机架（如果配置）
//   4. 所有副本分布在不同 Broker
```

### 手动重新分配

```bash
# 1. 生成 reassignment.json
cat > reassign.json << EOF
{
  "version": 1,
  "partitions": [
    {"topic": "orders", "partition": 0, "replicas": [1, 2]},
    {"topic": "orders", "partition": 1, "replicas": [2, 3]},
    {"topic": "orders", "partition": 2, "replicas": [3, 1]}
  ]
}
EOF

# 2. 执行重新分配
bin/kafka-reassign-partitions.sh \
    --bootstrap-server localhost:9092 \
    --reassignment-json-file reassign.json \
    --execute

# 3. 验证进度
bin/kafka-reassign-partitions.sh \
    --bootstrap-server localhost:9092 \
    --reassignment-json-file reassign.json \
    --verify
```

## 🛠️ 副本数选择建议

```
小集群（3 节点）：
  - replication.factor=3（满副本）
  - min.insync.replicas=2（容忍 1 节点故障）

中集群（5-10 节点）：
  - replication.factor=3（多数派）
  - min.insync.replicas=2

大集群（10+ 节点）：
  - replication.factor=3（成本与可靠性平衡）
  - 重要数据可设为 5
  - min.insync.replicas=2

⚠️ 副本数不是越多越好：
  - 副本数 = 3 时，磁盘空间 3 倍
  - 副本数 = 5 时，写入延迟增加
  - 一般 3 副本足够
```

## 🎯 总结

**副本机制核心要点**：
- ✅ 每个 Partition 有 N 个副本（默认 3）
- ✅ Leader 处理读写，Follower 同步数据
- ✅ ISR（同步副本）是故障转移的候选
- ✅ acks=all + min.insync.replicas=2 最强保证
- ✅ Controller 选举新 Leader（从 ISR 选）
- ⚠️ unclean.election 关闭可避免数据丢失
- ⚠️ 副本数影响磁盘空间和写入延迟

**下一步：** [👑 Leader 选举](/02-architecture/leader-election) — 故障转移详解
