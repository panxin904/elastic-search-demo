---
title: Kafka 是什么
---

# ❓ Kafka 是什么


![Kafka 集群拓扑 — Broker / Partition / Consumer Group](/kafka-topology.svg)

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
