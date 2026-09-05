---
title: Kafka 是什么
date: 2026-08-15  # date-auto-injected
---

# ❓ Kafka 是什么


<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 460" font-family="--apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <rect class="at-svg-bg" width="600" height="460"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Kafka 集群拓扑</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Broker 集群 + 分区副本 + Consumer Group</text>

  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
    <marker id="arrow-kafka" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>

  <!-- 3 个 Broker -->
  <rect class="at-hover-card" x="50" y="100" width="160" height="220" rx="6" fill="#fef3c7" stroke="#f59e0b"/>
  <text x="130" y="125" text-anchor="middle" font-size="14" font-weight="700" fill="#92400e">Broker 1</text>
  <!-- partitions of broker 1 -->
  <rect class="at-hover-card" x="65" y="145" width="60" height="20" rx="2" fill="#f59e0b"/>
  <text x="95" y="159" text-anchor="middle" font-size="10" font-weight="600" fill="white">P0 (L)</text>
  <rect class="at-hover-card" x="135" y="145" width="60" height="20" rx="2" fill="#fbbf24"/>
  <text x="165" y="159" text-anchor="middle" font-size="10" font-weight="600" fill="white">P1 (F)</text>
  <rect class="at-hover-card" x="65" y="175" width="60" height="20" rx="2" fill="#fbbf24"/>
  <text x="95" y="189" text-anchor="middle" font-size="10" font-weight="600" fill="white">P1 (F)</text>
  <rect class="at-hover-card" x="135" y="175" width="60" height="20" rx="2" fill="#f59e0b"/>
  <text x="165" y="189" text-anchor="middle" font-size="10" font-weight="600" fill="white">P2 (L)</text>
  <rect class="at-hover-card" x="65" y="205" width="60" height="20" rx="2" fill="#f59e0b"/>
  <text x="95" y="219" text-anchor="middle" font-size="10" font-weight="600" fill="white">P2 (L)</text>
  <rect class="at-hover-card" x="135" y="205" width="60" height="20" rx="2" fill="#fbbf24"/>
  <text x="165" y="219" text-anchor="middle" font-size="10" font-weight="600" fill="white">P0 (F)</text>

  <rect class="at-hover-card" x="220" y="100" width="160" height="220" rx="6" fill="#fef3c7" stroke="#f59e0b"/>
  <text x="300" y="125" text-anchor="middle" font-size="14" font-weight="700" fill="#92400e">Broker 2</text>
  <rect class="at-hover-card" x="235" y="145" width="60" height="20" rx="2" fill="#fbbf24"/>
  <text x="265" y="159" text-anchor="middle" font-size="10" font-weight="600" fill="white">P0 (F)</text>
  <rect class="at-hover-card" x="305" y="145" width="60" height="20" rx="2" fill="#f59e0b"/>
  <text x="335" y="159" text-anchor="middle" font-size="10" font-weight="600" fill="white">P1 (L)</text>
  <rect class="at-hover-card" x="235" y="175" width="60" height="20" rx="2" fill="#f59e0b"/>
  <text x="265" y="189" text-anchor="middle" font-size="10" font-weight="600" fill="white">P1 (L)</text>
  <rect class="at-hover-card" x="305" y="175" width="60" height="20" rx="2" fill="#fbbf24"/>
  <text x="335" y="189" text-anchor="middle" font-size="10" font-weight="600" fill="white">P2 (F)</text>
  <rect class="at-hover-card" x="235" y="205" width="60" height="20" rx="2" fill="#fbbf24"/>
  <text x="265" y="219" text-anchor="middle" font-size="10" font-weight="600" fill="white">P2 (F)</text>
  <rect class="at-hover-card" x="305" y="205" width="60" height="20" rx="2" fill="#f59e0b"/>
  <text x="335" y="219" text-anchor="middle" font-size="10" font-weight="600" fill="white">P0 (L)</text>

  <rect class="at-hover-card" x="390" y="100" width="160" height="220" rx="6" fill="#fef3c7" stroke="#f59e0b"/>
  <text x="470" y="125" text-anchor="middle" font-size="14" font-weight="700" fill="#92400e">Broker 3</text>
  <rect class="at-hover-card" x="405" y="145" width="60" height="20" rx="2" fill="#fbbf24"/>
  <text x="435" y="159" text-anchor="middle" font-size="10" font-weight="600" fill="white">P0 (F)</text>
  <rect class="at-hover-card" x="475" y="145" width="60" height="20" rx="2" fill="#fbbf24"/>
  <text x="505" y="159" text-anchor="middle" font-size="10" font-weight="600" fill="white">P1 (F)</text>
  <rect class="at-hover-card" x="405" y="175" width="60" height="20" rx="2" fill="#fbbf24"/>
  <text x="435" y="189" text-anchor="middle" font-size="10" font-weight="600" fill="white">P2 (F)</text>
  <rect class="at-hover-card" x="475" y="175" width="60" height="20" rx="2" fill="#f59e0b"/>
  <text x="505" y="189" text-anchor="middle" font-size="10" font-weight="600" fill="white">P0 (L)</text>
  <rect class="at-hover-card" x="405" y="205" width="60" height="20" rx="2" fill="#f59e0b"/>
  <text x="435" y="219" text-anchor="middle" font-size="10" font-weight="600" fill="white">P1 (L)</text>
  <rect class="at-hover-card" x="475" y="205" width="60" height="20" rx="2" fill="#f59e0b"/>
  <text x="505" y="219" text-anchor="middle" font-size="10" font-weight="600" fill="white">P2 (L)</text>

  <!-- Consumer Group -->
  <rect class="at-hover-card" x="100" y="370" width="400" height="60" rx="6" fill="#dbeafe" stroke="#3b82f6"/>
  <text x="300" y="392" text-anchor="middle" font-size="13" font-weight="700" fill="#1e40af">Consumer Group "order-service"</text>
  <text x="300" y="410" text-anchor="middle" font-size="11" fill="#475569">3 个 Consumer 实例分别消费 P0 / P1 / P2</text>
  <text x="300" y="425" text-anchor="middle" font-size="10" fill="#64748b">组内每个分区只被一个 Consumer 消费 · 扩容时自动 rebalance</text>

  <line x1="300" y1="320" x2="300" y2="365" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arrow-kafka)"/>

  <!-- 图例 -->
  <rect x="50" y="445" width="14" height="14" fill="#f59e0b"/>
  <text x="70" y="457" font-size="11" fill="#475569">Leader</text>
  <rect x="160" y="445" width="14" height="14" fill="#fbbf24"/>
  <text x="180" y="457" font-size="11" fill="#475569">Follower</text>
  <text x="280" y="457" font-size="11" fill="#94a3b8">ISR = Leader + 所有 Follower</text>
</svg>
> **Apache Kafka** 最初是由 LinkedIn 开发，后捐赠给 Apache 基金会的**分布式发布订阅消息系统**。现已成为大数据、实时计算、微服务领域的事实标准。

## 🎯 Kafka 核心定位

```
Kafka = 分布式 + 高吞吐 + 持久化 + 发布订阅的消息系统
```

| 维度 | Kafka 的特点 |
|------|-------------|
| **吞吐** | 单机 100w+ msg/s（顺序写盘 + 零拷贝） |
| **持久化** | 消息持久化到磁盘，可保留 N 天 |
| **水平扩展** | 增加 Broker 即可提升容量和吞吐 |
| **高可用** | 多副本机制，单点故障不影响服务 |
| **生态** | Connect / Streams / ksqlDB 完整生态 |

## 🆚 Kafka vs 其他消息中间件

| 维度 | Kafka | RabbitMQ | RocketMQ |
|------|-------|----------|----------|
| **吞吐** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **延迟** | ms 级 | μs 级 | ms 级 |
| **消息保留** | N 天（磁盘） | 不保留 | N 天 |
| **消息回溯** | ✅ 支持 | ❌ | ⚠️ 有限 |
| **顺序消费** | ✅ 分区内 | ⚠️ 弱 | ✅ |
| **生态** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **适用场景** | 日志、流计算、事件溯源 | 业务消息 | 业务消息、金融 |

## 🎯 Kafka 典型应用场景

```
✅ 日志聚合（ELK + Kafka）
✅ 用户行为埋点（点击、浏览、停留时长）
✅ 微服务异步通信（订单 ↔ 库存 ↔ 支付）
✅ 事件溯源（Event Sourcing）
✅ CDC（Change Data Capture，数据库变更同步）
✅ 流式计算（Kafka Streams / Flink / Spark Streaming）
✅ 消息推送（WebSocket 广播）
✅ 削峰填谷（秒杀、下单）
```

## 🏗️ Kafka 核心特性

```
✅ 发布订阅模型
   - 多个 Producer 写入，多个 Consumer 订阅
   - Consumer 各自维护消费位置（offset）

✅ 持久化存储
   - 消息持久化到磁盘
   - 可配置保留策略（时间 / 大小）

✅ 流处理
   - 不是简单的 Queue
   - 可重放历史消息（Kafka Streams）

✅ 高可用
   - 分区多副本（replication）
   - Leader 故障自动选举

✅ 高吞吐
   - 顺序写盘（顺序 IO）
   - 零拷贝（sendfile 系统调用）
   - Page Cache（OS 文件缓存）
```

## 🆚 Kafka 与传统 MQ 的本质区别

```
传统 MQ（如 RabbitMQ）：
  - 消息消费后即删除
  - 不支持回放
  - 适合业务消息

Kafka：
  - 消息保留 N 天（即使已消费）
  - 支持回放历史消息
  - 更像「分布式日志」而不是「消息队列」
  - 适合大数据 + 事件流
```

## 📊 Kafka 在生态中的位置

```
数据源 → Kafka → 多个消费者
  - DB
  - 日志
  - 微服务
        ├── Elasticsearch（日志搜索）
        ├── Flink / Spark（实时计算）
        ├── HDFS / S3（离线分析）
        ├── 微服务 1（订单）
        ├── 微服务 2（库存）
        └── Dashboard（实时大屏）
```

## 🔑 Kafka 核心概念速览

```
Broker          Kafka 服务器节点
Topic           消息主题（逻辑分类）
Partition       Topic 的分区（物理分片）
Producer        消息生产者
Consumer        消息消费者
Consumer Group  消费者组（多 Consumer 协作）
Offset          消息在分区中的偏移量
Replica         分区副本（高可用保障）
ISR             In-Sync Replicas（同步副本列表）
Controller      集群控制器（管理元数据）
ZooKeeper       早期版本依赖（KRaft 已移除）
```

## 🎯 Kafka 版本演进

```
0.x  - LinkedIn 内部
2011 - 开源
0.9  - 增加副本、Consumer Group（2015）
0.10 - 增加 Kafka Streams（2016）
0.11 - 增加事务、幂等性（2017）
1.0  - 第一个稳定版本（2017）
2.0  - KRaft 取代 ZooKeeper（2020）
3.0  - 全面拥抱 KRaft（2021）
3.x  - 当前主流版本（2022+）
```

## 🎯 总结

**Kafka 核心要点**：
- ✅ 分布式发布订阅消息系统
- ✅ 高吞吐（100w+ msg/s）
- ✅ 持久化 + 多副本高可用
- ✅ 不仅是 MQ，更是分布式日志
- ✅ 大数据、微服务、实时计算的标配

**下一步：** [📥 安装部署](/01-basics/install) — 5 分钟跑起来

<!-- svg-injected:do-not-edit -->

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Kafka Topic 与 Partition</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">水平扩展单元 · 顺序写 · 副本机制</text>

  <!-- Topic -->
  <rect class="at-hover-card" x="50" y="100" width="500" height="280" rx="10" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4 3"/>
  <text x="60" y="125" font-size="14" font-weight="700" fill="#1e293b">Topic: orders</text>

  <!-- 3 个 Partition -->
  <g font-size="11" font-weight="700">
    <!-- P0 -->
    <rect class="at-hover-card" x="70" y="140" width="155" height="220" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="147" y="160" text-anchor="middle" fill="#1e3a8a">Partition 0</text>
    <rect class="at-hover-card" x="80" y="170" width="135" height="22" rx="3" fill="#3b82f6" opacity="0.9"/>
    <text x="90" y="185" fill="white">off=0  msg=1</text>
    <rect class="at-hover-card" x="80" y="195" width="135" height="22" rx="3" fill="#3b82f6" opacity="0.9"/>
    <text x="90" y="210" fill="white">off=1  msg=2</text>
    <rect class="at-hover-card" x="80" y="220" width="135" height="22" rx="3" fill="#3b82f6" opacity="0.9"/>
    <text x="90" y="235" fill="white">off=2  msg=3</text>
    <text x="147" y="270" text-anchor="middle" font-size="10" fill="#3b82f6">leader</text>
    <text x="147" y="285" text-anchor="middle" font-size="10" fill="#3b82f6">replica: 2</text>
    <text x="147" y="305" text-anchor="middle" font-size="10" fill="#3b82f6">顺序写 · 不可变</text>
    <text x="147" y="325" text-anchor="middle" font-size="10" fill="#3b82f6">retention 7d</text>

    <!-- P1 -->
    <rect class="at-hover-card" x="240" y="140" width="155" height="220" rx="6" fill="#d1fae5" stroke="#10b981" stroke-width="1.5"/>
    <text x="317" y="160" text-anchor="middle" fill="#064e3b">Partition 1</text>
    <rect class="at-hover-card" x="250" y="170" width="135" height="22" rx="3" fill="#10b981" opacity="0.9"/>
    <text x="260" y="185" fill="white">off=0  msg=1</text>
    <rect class="at-hover-card" x="250" y="195" width="135" height="22" rx="3" fill="#10b981" opacity="0.9"/>
    <text x="260" y="210" fill="white">off=1  msg=2</text>
    <rect class="at-hover-card" x="250" y="220" width="135" height="22" rx="3" fill="#10b981" opacity="0.9"/>
    <text x="260" y="235" fill="white">off=2  msg=3</text>
    <text x="317" y="270" text-anchor="middle" font-size="10" fill="#10b981">leader</text>
    <text x="317" y="285" text-anchor="middle" font-size="10" fill="#10b981">replica: 2</text>

    <!-- P2 -->
    <rect class="at-hover-card" x="410" y="140" width="130" height="220" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="475" y="160" text-anchor="middle" fill="#92400e">Partition 2</text>
    <rect class="at-hover-card" x="420" y="170" width="110" height="22" rx="3" fill="#f59e0b" opacity="0.9"/>
    <text x="430" y="185" fill="white">off=0  m=1</text>
    <rect class="at-hover-card" x="420" y="195" width="110" height="22" rx="3" fill="#f59e0b" opacity="0.9"/>
    <text x="430" y="210" fill="white">off=1  m=2</text>
    <text x="475" y="270" text-anchor="middle" font-size="10" fill="#f59e0b">leader</text>
    <text x="475" y="285" text-anchor="middle" font-size="10" fill="#f59e0b">replica: 2</text>
  </g>

  <!-- 关键事实 -->
  <g font-size="11">
    <rect class="at-hover-card" x="50" y="400" width="500" height="60" rx="8" fill="#f1f5f9" stroke="#64748b" stroke-width="1"/>
    <text x="60" y="420" font-weight="700" fill="#1e293b">核心特性</text>
    <text x="60" y="438" fill="#475569">✓ 分区内有序 · 全局无序 · Key 哈希保证相同 key 进同分区</text>
    <text x="60" y="455" fill="#475569">✓ 副本机制：replica.factor=3 · leader 读写 · follower 同步</text>
  </g>
</svg>
