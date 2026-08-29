---
date: 2026-08-27  # date-auto-injected
layout: home

hero:
  name: Redis 知识图谱
  text: 系统化学习 Redis
  tagline: 用知识图谱串联 Redis 底层原理、5 大基础类型、持久化、集群、Java SDK 与企业实战
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 🧠 思维导图
      link: /mindmap
    - theme: alt
      text: 📋 命令速查
      link: /cheatsheet

features:
  - icon: 🚀
    title: 基础入门
    details: Redis 是什么 · 安装部署 · 5 大基础类型 · Key 通用操作 · 过期策略
    link: /01-basics/intro
    linkText: 开始学习 →
  - icon: 🧬
    title: 数据结构原理
    details: SDS / Dict / SkipList / Listpack / QuickList / Stream 7 篇深度剖析
    link: /02-datastruct/object
    linkText: 深入原理 →
  - icon: 💾
    title: 持久化机制
    details: RDB 快照 · AOF 日志 · 混合持久化 · 恢复策略
    link: /03-persistence/overview
    linkText: 掌握持久化 →
  - icon: 🔗
    title: 高可用集群
    details: 主从复制 · Sentinel 哨兵 · Cluster 集群 · 哈希槽 · Gossip
    link: /04-cluster/replication
    linkText: 精通集群 →
  - icon: ☕
    title: Java SDK
    details: Jedis / Lettuce / Redisson / Spring Data Redis / 连接池
    link: /05-jdk/jedis
    linkText: Java 实战 →
  - icon: 💼
    title: 企业实战
    details: 分布式锁 · Session · 限流 · Stream MQ · 延迟队列 · 排行榜 · 缓存一致性
    link: /06-practice/distributed-lock
    linkText: 实战案例 →
  - icon: 🛠️
    title: 运维调优
    details: 内存淘汰 · 大 Key 热 Key · 慢查询 · 监控告警 · Redis 7 新特性
    link: /07-ops/eviction
    linkText: 性能调优 →
  - icon: 🎯
    title: 面试手撕题
    details: 高频面试题 · 分布式锁手撕 · LRU 算法 · 跳表 · 缓存三大问题
    link: /08-interview/basic
    linkText: 挑战面试 →
---


<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "只会简单 SET / GET，不懂底层数据结构（SDS / Dict / SkipList）",
      "不了解 RDB / AOF 的差异与混合持久化",
      "集群模式分不清主从 / 哨兵 / Cluster / Gossip",
      "用过 Jedis 但不知道 Lettuce 是怎么 NIO 异步的",
      "做过分布式锁但不清楚「看门狗」续期原理"
    ]
const goals = [
      "系统化讲解 Redis 底层原理",
      "覆盖 5 大基础类型（String / Hash / List / Set / ZSet） + Stream",
      "Java SDK 全场景（Jedis / Lettuce / Redisson / Spring Data Redis）",
      "企业实战（分布式锁 / 限流 / Session / 消息队列 / 排行榜）",
      "面试手撕题 + 性能调优"
    ]
const relatedSites = [
      { site: "java", path: "/03-practice/jedis", label: "Jedis / Lettuce" },
      { site: "architecture", path: "/04-cache/redis", label: "架构中的 Redis" },
      { site: "system-design", path: "/01-theory/cap-theorem", label: "CAP 与一致性" },
      { site: "observability", path: "/05-sre/redis-monitor", label: "Redis 监控" },
      { site: "mysql", path: "/09-connection/cache-pattern", label: "MySQL + Redis 缓存" }
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

## 🎯 学习路径

```
🆕 入门     →  🚀 基础入门 →  📦 5 大基础类型 →  ⏱️ 过期策略
🔧 进阶     →  🧬 数据结构 →  💾 持久化 →  🔗 集群
☕ 实战     →  ☕ Java SDK →  💼 企业实战
🔨 高阶     →  🛠️ 运维调优 →  🎯 面试手撕题
```

完整路径请看 [📖 学习路径](/path)。

## 🆕 推荐先看

- [🚀 Redis 是什么](/01-basics/intro) - 5 分钟搞懂 Redis 价值
- [🌐 全局知识图谱](/graph) - 看完整节点关系
- [🧭 思维导图](/mindmap) - 树形结构总览
- [📋 命令速查](/cheatsheet) - 60+ 命令可搜索

## 🛠️ 技术栈

- [VitePress 1.x](https://vitepress.dev/) - 静态站点生成器
- [Vue 3](https://vuejs.org/) - 组件化
- [ECharts 5.x](https://echarts.apache.org/) - 图谱、思维导图
- 5 个自研交互组件（命令 Playground / 数据结构可视化 / 集群拓扑 / 分布式锁 / 命令速查）

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [mysql](https://java-px.bot.cd/mysql/)：MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/)：Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/)：Java 客户端（Redisson / Jedis）
- [system-design](https://java-px.bot.cd/system-design/)：分布式锁 / 缓存架构
- [architecture](https://java-px.bot.cd/architecture/)：微服务缓存层
- [linux](https://java-px.bot.cd/linux/)：Linux 内核参数调优
