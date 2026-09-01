---
layout: home
title: System Design 知识图谱
date: 2026-08-27  # date-auto-injected
hero:
  name: System Design 知识图谱
  text: 从理论到经典设计题
  tagline: CAP / Paxos / Raft · 一致性哈希 · 分布式事务 · 短链 / 秒杀 / Feed
  actions:
    - theme: brand
      text: 📖 理论基础
      link: /01-theory/overview
    - theme: alt
      text: 🏛️ 分布式协调
      link: /03-coordination/raft
    - theme: alt
      text: 🎯 经典设计题
      link: /10-cases/short-url
features:
  - icon: 📖
    title: 理论基础
    details: CAP / PACELC / FLP / 一致性模型 / 共识问题
    link: /01-theory/overview
    linkText: 看理论 →
  - icon: 💾
    title: 分布式存储
    details: 分片策略 / 一致性哈希 / 副本 / Quorum NWR
    link: /02-storage/consistent-hash
    linkText: 看存储 →
  - icon: 🤝
    title: 分布式协调
    details: Paxos / Raft / ZAB / 分布式锁 / Leader 选举
    link: /03-coordination/raft
    linkText: 看协调 →
  - icon: 🔄
    title: 分布式事务
    details: 2PC / 3PC / TCC / Saga / 本地消息表
    link: /04-transaction/saga
    linkText: 看事务 →
  - icon: 🧩
    title: 微服务模式
    details: 服务发现 / 配置中心 / API 网关 / 熔断 / 限流 / 追踪
    link: /05-patterns/service-discovery
    linkText: 看模式 →
  - icon: ⚡
    title: 缓存体系
    details: 多级缓存 / 缓存模式 / 一致性 / 雪崩穿透击穿
    link: /06-cache/three-problems
    linkText: 看缓存 →
  - icon: 📨
    title: 消息可靠性
    details: 不丢 / 幂等 / 顺序 / 堆积处理
    link: /07-messaging/not-lost
    linkText: 看 MQ →
  - icon: 🏢
    title: 高可用设计
    details: 主备 / 集群 / 多活 / 容灾演练
    link: /08-availability/multi-idc
    linkText: 看 HA →
  - icon: 🆔
    title: 分布式 ID
    details: Snowflake / Leaf / UUID 对比
    link: /09-id/snowflake
    linkText: 看 ID →
  - icon: 🎯
    title: 经典设计题
    details: 短链 / Feed / 秒杀 / 抢红包 / 排行 / LBS / 推送
    link: /10-cases/short-url
    linkText: 看案例 →
---


<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "会写 CRUD 却讲不清 CAP",
      "调过 Redis 却说不出 cache-aside 的失效边界",
      "用过 Kafka 但说不清「不丢消息」需要哪几道防线",
      "设计过系统但写不出「短链」的短码生成选型",
      "读过 Raft 论文但没自己推导过选举超时"
    ]
const goals = [
      "一致性模型谱 + CAP + PACELC + FLP：分布式理论的根",
      "短链 / Feed / 秒杀 / 抢红包 / LBS：系统设计面试与实战",
      "每章给出：问题 → 经典方案 → 工程取舍 → 代码骨架"
    ]
const relatedSites = [
      { site: "architecture", path: "/01-distributed/cap", label: "CAP 定理" },
      { site: "java-language", path: "/04-jvm/overview", label: "JVM 原理" },
      { site: "java", path: "/04-tech/jvm", label: "Java Web JVM" },
      { site: "kafka", path: "/01-basics/architecture", label: "Kafka 架构" },
      { site: "redis", path: "/01-basics/intro", label: "Redis 基础" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>

## 📖 学习路径（推荐顺序）

```
📖 理论  →  CAP / PACELC / FLP / 一致性级别谱
         ↓
💾 存储  →  分片 / 一致性哈希 / Quorum
         ↓
🤝 协调  →  Raft 选举与日志复制 / 分布式锁
         ↓
🔄 事务  →  2PC / TCC / Saga 适用场景
         ↓
🧩 模式  →  服务发现 / 网关 / 熔断 / 限流
         ↓
⚡ 缓存  →  三大问题 + 多级缓存 + 一致性
         ↓
📨 消息  →  不丢 / 幂等 / 顺序 / 堆积
         ↓
🎯 案例  →  短链 / Feed / 秒杀 / 抢红包
```

## 💡 与「企业级架构」站的关系

```
🔄 互补关系，不重叠：
  enterprise architecture 站  →  高并发 / 微服务 / DDD / 企业案例（偏工程师视角）
  system design 站          →  分布式理论 / 经典设计题（偏架构师视角）

📌 推荐路径：
  看 kafka 的"消息可靠性" → 跳到这里看"不丢/幂等/顺序"
  看 redis 的"集群"      → 跳到这里看"一致性哈希 + Quorum"
  看 mysql 的"主从复制"   → 跳到这里看"Paxos/Raft + 2PC"
```

## 🎯 适用读者

| 角色 | 推荐章节 |
|---|---|
| 后端工程师 | 理论基础 + 缓存 + 消息可靠性 + 案例 |
| 架构师 | CAP / Raft / Saga / 微服务模式 / 多活 |
| 面试候选人 | CAP + 一致性哈希 + 短链 + 秒杀 + 抢红包 |
| SRE | 高可用设计 + 多活 / 单元化 + 容灾演练 |

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [architecture](https://java-px.bot.cd/architecture/)：企业架构
- [java](https://java-px.bot.cd/java-web-manual/)：Java 实现
- [kafka](https://java-px.bot.cd/kafka/)：消息
- [redis](https://java-px.bot.cd/redis/)：缓存
- [mysql](https://java-px.bot.cd/mysql/)：数据库
- [design-pattern](https://java-px.bot.cd/design-pattern/)：设计模式


## 💬 评论与反馈

有问题或建议？欢迎在下方评论。

<ClientOnly>
  <GiscusComment />
</ClientOnly>
