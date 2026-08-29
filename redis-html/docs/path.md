---
title: 学习路径
date: 2026-08-15  # date-auto-injected
---

# 📖 Redis 学习路径

> 根据你的角色选择对应路径，每条路径推荐了核心阅读顺序。

## 🛤️ 路径 1：入门（1 周）

适合**刚接触 Redis**的开发者。

1. [❓ Redis 是什么](/01-basics/intro) - 5 分钟了解 Redis
2. [📥 安装部署](/01-basics/install) - 5 分钟跑起来
3. [📦 5 大基础类型](/01-basics/datatypes) - 核心概念
4. [🔑 Key 通用操作](/01-basics/keys) - 常用命令
5. [⏱️ 过期策略](/01-basics/expiration) - TTL / 过期删除
6. [📋 命令速查](/cheatsheet) - 速查命令

**目标**：能熟练使用 5 大基础类型，能用 Redis 做基本缓存。

## 🛤️ 路径 2：进阶（2-3 周）

适合**想深入底层**的开发者。

- 完成"入门"路径
- [🎯 RedisObject](/02-datastruct/object) - 一切对象的基类
- [📝 SDS 简单动态字符串](/02-datastruct/sds) - Redis 字符串实现
- [🗂️ Dict 哈希表](/02-datastruct/dict) - 哈希结构 + 渐进式 rehash
- [🦘 SkipList 跳表](/02-datastruct/skiplist) - ZSet 底层
- [💾 RDB 快照](/03-persistence/rdb) - 持久化机制 1
- [📜 AOF 日志](/03-persistence/aof) - 持久化机制 2
- [🔁 主从复制](/04-cluster/replication) - 高可用基础
- [🛡️ Sentinel 哨兵](/04-cluster/sentinel) - 故障自动切换
- [🌐 Cluster 集群](/04-cluster/cluster) - 分布式方案

**目标**：能在面试中讲清 SDS、跳跃表、RDB、AOF、主从复制原理。

## 🛤️ 路径 3：Java 实战（3-4 周）

适合**Java 后端工程师**。

- 完成"入门"路径
- [🔧 Jedis](/05-jdk/jedis) - 最简单的 Java 客户端
- [🥬 Lettuce](/05-jdk/lettuce) - 基于 Netty 的异步客户端
- [🔴 Redisson](/05-jdk/redisson) - 分布式工具集
- [🌱 Spring Data Redis](/05-jdk/spring-data-redis) - Spring 集成
- [🔒 分布式锁](/06-practice/distributed-lock) - 企业实战 1
- [🚦 限流](/06-practice/ratelimit) - 企业实战 2
- [📨 Stream 消息队列](/06-practice/stream-mq) - 企业实战 3
- [⚖️ 缓存一致性](/06-practice/cache-consistency) - 企业实战 4

**目标**：能在 Spring Boot 项目中集成 Redis，能用 Redisson 做分布式锁。

## 🛤️ 路径 4：架构师（5 周+）

适合**架构师 / 高级开发**。

- 完成所有前置路径
- [🎰 哈希槽分片](/04-cluster/slots) - Cluster 核心
- [💬 Gossip 协议](/04-cluster/gossip) - 节点发现
- [🚚 数据迁移](/04-cluster/migration) - 扩容实战
- [🗑️ 内存淘汰策略](/07-ops/eviction) - 8 大淘汰算法
- [🔑 大 Key 热 Key](/07-ops/bigkey-hotkey) - 生产调优
- [🐢 慢查询分析](/07-ops/slowlog) - 性能诊断
- [📊 监控告警](/07-ops/monitoring) - Prometheus + Grafana
- [📝 高频面试题（上）](/08-interview/basic) - 面试必备

**目标**：能独立设计 Redis 高可用方案，能解决生产性能问题。

## 🎯 速查卡片

| 我想 | 推荐先看 |
|------|---------|
| 学命令 | [📋 命令速查](/cheatsheet) |
| 做项目 | [🔧 Jedis](/05-jdk/jedis) → [🔴 Redisson](/05-jdk/redisson) |
| 找工作 | [📝 高频面试题（上）](/08-interview/basic) → [📝 高频面试题（下）](/08-interview/advanced) |
| 解 Bug | [🐢 慢查询分析](/07-ops/slowlog) → [🔑 大 Key 热 Key](/07-ops/bigkey-hotkey) |
| 写方案 | [🌐 Cluster 集群](/04-cluster/cluster) → [🗑️ 内存淘汰策略](/07-ops/eviction) |
