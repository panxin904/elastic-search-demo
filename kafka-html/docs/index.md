---
layout: home

hero:
  name: Kafka 知识图谱
  text: 系统化学习
  tagline: 用知识图谱串联 Kafka 底层原理、生产消费、企业实战
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
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "分区副本机制、Leader 选举讲不清？",
      "Exactly-Once 语义怎么实现？",
      "消费者组位移提交策略选哪个？",
      "Kafka 性能调优参数（broker / producer / consumer）？",
      "Kafka + Flink / Spark 流处理集成怎么做？"
    ]
const goals = [
      "核心概念（Topic / Partition / Offset / Broker）",
      "架构原理（Controller / 副本机制 / 零拷贝）",
      "命令行工具（kafka-topics / kafka-console-*）",
      "生产消费实战（Java / Go / Python 客户端）",
      "企业级应用（监控 / 调优 / 安全 / 多集群）"
    ]
const relatedSites = [
      { site: "bigdata", path: "/03-streaming/kafka", label: "大数据 Kafka" },
      { site: "observability", path: "/05-sre/overview", label: "SRE 实践" },
      { site: "architecture", path: "/01-distributed/cap", label: "分布式理论" },
      { site: "clickhouse", path: "/05-ecosystem/kafka-engine", label: "Kafka → ClickHouse" },
      { site: "system-design", path: "/01-theory/cap-theorem", label: "系统设计基础" }
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

features:
  - icon: 🚀
    title: Kafka 入门
    details: Kafka 是什么、安装部署、核心概念、Topic & Partition、消息模型
    link: /01-basics/intro
    linkText: 开始学习 →
  - icon: 🏗️
    title: 架构原理
    details: 整体架构、Controller 控制器、分区副本机制、Leader 选举、日志存储、零拷贝原理
    link: /02-architecture/overview
    linkText: 深入原理 →
  - icon: 🛠️
    title: 命令行工具
    details: kafka-topics、kafka-console-producer、kafka-console-consumer、消费者组管理
    link: /03-cli/overview
    linkText: 常用命令 →
  - icon: ✍️
    title: 生产者 Producer
    details: 生产者原理、消息发送流程、幂等性、事务、顺序保证、性能调优
    link: /04-producer/principle
    linkText: 生产者详解 →
  - icon: 📥
    title: 消费者 Consumer
    details: 消费者原理、消费者组、偏移量提交、再平衡、手动提交、多线程消费
    link: /05-consumer/principle
    linkText: 消费者详解 →
  - icon: ☕
    title: Java SDK
    details: Producer API、Consumer API、AdminClient、序列化与反序列化、自定义分区器、异常处理
    link: /06-jdk/producer-api
    linkText: Java 实战 →
  - icon: 🌱
    title: Spring 集成
    details: Spring for Apache Kafka、KafkaTemplate、@KafkaListener、Spring 事务、Spring Boot 集成
    link: /07-spring/intro
    linkText: Spring 集成 →
  - icon: 💼
    title: 企业实战
    details: 消息幂等性、顺序消费、延迟消息、死信队列、消息积压、Kafka Connect、Kafka Streams
    link: /08-enterprise/idempotent
    linkText: 实战案例 →
  - icon: 🛠️
    title: 运维调优
    details: 集群规划、性能压测、JVM 调优、日志清理、监控指标、故障恢复
    link: /09-ops/capacity
    linkText: 性能调优 →
  - icon: 🎯
    title: 面试手撕题
    details: 高频面试题、副本同步机制、消息丢失解决方案、Kafka vs RocketMQ、Exactly Once
    link: /10-interview/basic
    linkText: 挑战面试 →

---

## 🎯 为什么写这个知识图谱？

```
Kafka 是分布式消息中间件的标杆，但绝大多数人：
  ❌ 只会用 kafka-console-producer，不知道 Partition 怎么分区
  ❌ 不懂 Leader 选举、ISR 副本同步原理
  ❌ 用了 Spring Kafka 但不知道 ack 模式含义
  ❌ 踩过消息丢失、重复消费的坑但不知道为什么

本图谱的目标：
  ✅ 系统化讲解 Kafka 底层原理（架构、选举、日志、零拷贝）
  ✅ 深入 Producer/Consumer 核心机制（幂等性、事务、顺序）
  ✅ Java SDK + Spring Boot 集成全场景
  ✅ 企业实战（顺序消费、死信队列、延迟消息、消息积压）
  ✅ 面试手撕题 + 性能调优
```

## 🎯 学习路径

```
🆕 入门     →  🚀 Kafka 入门 →  🧩 核心概念 →  💬 消息模型
🏗️ 原理     →  🏗️ 架构原理 →  👑 Leader 选举 →  📜 日志存储 →  🚀 零拷贝
✍️ 实战     →  ✍️ 生产者 →  📥 消费者 →  ☕ Java SDK →  🌱 Spring 集成
💼 进阶     →  💼 企业实战 →  🛠️ 运维调优
🎯 面试     →  🎯 面试手撕题
```

完整路径请看 [📖 学习路径](/path)。

## 🆕 推荐先看

- [🚀 Kafka 是什么](/01-basics/intro) - 5 分钟搞懂 Kafka 价值
- [🌐 全局知识图谱](/graph) - 看完整节点关系
- [🧭 思维导图](/mindmap) - 树形结构总览
- [📋 命令速查](/cheatsheet) - 30+ 命令可搜索

## 🛠️ 技术栈

- [VitePress 1.x](https://vitepress.dev/) - 静态站点生成器
- [Vue 3](https://vuejs.org/) - 组件化
- [ECharts 5.x](https://echarts.apache.org/) - 图谱、思维导图
- 6 个自研交互组件（命令 Playground / 集群拓扑 / 消费者模拟器 / 命令速查 / 知识图谱 / 思维导图）
