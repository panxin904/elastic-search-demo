---
title: 学习路径
date: 2026-08-15  # date-auto-injected
---

# 📖 Kafka 学习路径

> 根据你的角色选择对应路径，每条路径推荐了核心阅读顺序。

## 🛤️ 路径 1：入门（1 周）

适合**刚接触 Kafka**的开发者。

1. [❓ Kafka 是什么](/01-basics/intro) - 5 分钟了解 Kafka
2. [📥 安装部署](/01-basics/install) - 5 分钟跑起来
3. [🧩 核心概念](/01-basics/concepts) - Broker / Topic / Partition / Producer / Consumer
4. [📂 Topic & Partition](/01-basics/topic-partition) - 消息存储模型
5. [💬 消息模型](/01-basics/message-model) - 点对点 vs 发布订阅
6. [📋 命令速查](/cheatsheet) - 速查命令

**目标**：能搭建 Kafka 集群，能用命令行工具生产消费消息。

## 🛤️ 路径 2：进阶（2-3 周）

适合**想深入底层**的开发者。

- 完成"入门"路径
- [🎯 整体架构](/02-architecture/overview) - Kafka 集群拓扑
- [🎮 Controller 控制器](/02-architecture/controller) - 集群大脑
- [🗂️ 分区副本机制](/02-architecture/replica) - 数据可靠性
- [👑 Leader 选举](/02-architecture/leader-election) - 高可用核心
- [📜 日志存储](/02-architecture/log-storage) - 顺序写盘
- [🚀 零拷贝原理](/02-architecture/zero-copy) - 高吞吐核心
- [✍️ 生产者原理](/04-producer/principle) - 发送机制
- [📥 消费者原理](/05-consumer/principle) - 拉取机制

**目标**：能在面试中讲清 Kafka 架构、副本同步、零拷贝等核心原理。

## 🛤️ 路径 3：Java 实战（3-4 周）

适合**Java 后端工程师**。

- 完成"入门"路径
- [✍️ 生产者原理](/04-producer/principle) - Producer API
- [🔁 幂等性](/04-producer/idempotent) - 不重复发送
- [🔐 事务](/04-producer/transaction) - 精确一次语义
- [👥 消费者组](/05-consumer/group) - Consumer Group
- [📍 偏移量提交](/05-consumer/offset) - Offset 管理
- [🔄 再平衡](/05-consumer/rebalance) - 重新分配
- [🌱 Spring Kafka 入门](/07-spring/intro) - Spring 集成
- [📤 KafkaTemplate](/07-spring/kafka-template) - 消息发送
- [🎧 @KafkaListener](/07-spring/listener) - 消息监听

**目标**：能在 Spring Boot 项目中集成 Kafka，能用 Spring KafkaTemplate 生产消费消息。

## 🛤️ 路径 4：架构师（5 周+）

适合**架构师 / 高级开发**。

- 完成所有前置路径
- [🔁 消息幂等性](/08-enterprise/idempotent) - 实战幂等方案
- [📊 顺序消费](/08-enterprise/order-consume) - 顺序保证实战
- [⏰ 延迟消息](/08-enterprise/delay) - 延迟队列实现
- [☠️ 死信队列](/08-enterprise/dead-letter) - 异常处理
- [📦 消息积压](/08-enterprise/backlog) - 积压监控与处理
- [📐 集群规划](/09-ops/capacity) - 容量评估
- [⚡ 性能压测](/09-ops/benchmark) - 性能基线
- [💾 JVM 调优](/09-ops/jvm) - GC 优化
- [📊 监控告警](/08-enterprise/monitoring) - Prometheus + Grafana
- [📝 高频面试题（上）](/10-interview/basic) - 面试必备

**目标**：能独立设计 Kafka 高可用方案，能解决生产环境的各种消息问题。

## 🎯 速查卡片

| 我想 | 推荐先看 |
|------|---------|
| 学命令 | [📋 命令速查](/cheatsheet) |
| 做项目 | [🌱 Spring Kafka 入门](/07-spring/intro) → [🎧 @KafkaListener](/07-spring/listener) |
| 找工作 | [📝 高频面试题（上）](/10-interview/basic) → [📝 高频面试题（下）](/10-interview/advanced) |
| 解 Bug | [📦 消息积压](/08-enterprise/backlog) → [☠️ 死信队列](/08-enterprise/dead-letter) |
| 写方案 | [🏗️ 整体架构](/02-architecture/overview) → [📐 集群规划](/09-ops/capacity) |
| 深入原理 | [🏗️ 架构原理](/02-architecture/overview) → [👑 Leader 选举](/02-architecture/leader-election) |

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
