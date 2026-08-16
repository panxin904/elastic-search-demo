---
layout: home
title: 企业级架构知识图谱
hero:
  name: 企业级架构知识图谱
  text: 从理论到实战
  tagline: 并发 · 高可用 · 微服务 · 分布式事务 · DDD · 企业案例
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
  - icon: 🧠
    title: 并发理论
    details: JMM · happens-before · CAS · volatile · AQS
    link: /01-concurrency-theory/jmm
    linkText: 看理论 →
  - icon: 🧵
    title: 线程池原理
    details: ThreadPoolExecutor · ForkJoinPool · JDK 21 虚拟线程
    link: /02-thread-pool/executor
    linkText: 看线程池 →
  - icon: 🏛️
    title: 高可用理论
    details: CAP · BASE · Raft 共识 · Quorum · 幂等性
    link: /03-ha-theory/cap
    linkText: 看 HA →
  - icon: 🚦
    title: 限流
    details: 令牌桶 / 漏桶 / 滑动窗口 / 分布式限流
    link: /04-rate-limit/token-bucket
    linkText: 看限流 →
  - icon: ⚡
    title: 熔断降级
    details: 熔断器三态 · Sentinel / Hystrix · Fallback
    link: /05-circuit-breaker/states
    linkText: 看熔断 →
  - icon: 🧩
    title: 微服务
    details: 服务拆分 / 服务发现 / API 网关 / 配置中心
    link: /06-microservice/split
    linkText: 看微服务 →
  - icon: 🔄
    title: 分布式事务
    details: 2PC / TCC / Saga / 本地消息表
    link: /07-distributed-tx/2pc
    linkText: 看事务 →
  - icon: 📨
    title: 消息队列
    details: Kafka · RabbitMQ · 顺序保证 · 幂等 · 死信
    link: /08-message-queue/compare
    linkText: 看 MQ →
  - icon: 💾
    title: 缓存
    details: 多级缓存 · 缓存击穿 / 穿透 / 雪崩 · 一致性
    link: /09-cache/architecture
    linkText: 看缓存 →
  - icon: 🗄️
    title: 分库分表
    details: 水平 / 垂直拆分 · 路由 · 扩容 · 分布式 ID
    link: /10-database-sharding/strategy
    linkText: 看分库 →
  - icon: 🧠
    title: DDD 领域驱动
    details: 聚合 / 实体 / 值对象 · 限界上下文 · 事件风暴
    link: /11-ddd/basics
    linkText: 看 DDD →
  - icon: 🧱
    title: 微服务模式
    details: Service Mesh · Sidecar · Saga · Bulkhead
    link: /12-microservice-patterns/service-mesh
    linkText: 看模式 →
  - icon: 🔭
    title: 可观测
    details: Metrics / Tracing / Logging · OpenTelemetry
    link: /13-observability/three-pillars
    linkText: 看可观测 →
  - icon: 🏢
    title: 企业案例
    details: 秒杀系统 · 短链 · 异地多活
    link: /14-enterprise-cases/flash-sale
    linkText: 看案例 →
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "会写 CRUD 却讲不清 CAP 定理",
      "知道消息队列但说不清幂等性设计",
      "调过限流却不懂令牌桶 vs 滑动窗口的区别",
      "用了 Seata 却不知道 AT 模式的 undo_log 怎么工作",
      "部署过微服务但没读过 DDD"
    ]
const goals = [
      "JMM / happens-before / CAS：并发编程的根",
      "CAP / BASE / Raft：分布式系统的根",
      "限流 / 熔断 / 降级：高可用三大法宝",
      "2PC / TCC / Saga：分布式事务选型",
      "DDD：微服务拆分的理论",
      "短链 / 秒杀 / 异地多活：真实案例分析"
    ]
const relatedSites = [
      { site: "system-design", path: "/cap-theorem", label: "系统设计的 CAP" },
      { site: "cloud", path: "/01-overview/microservices", label: "Spring Cloud 落地" },
      { site: "bigdata", path: "/06-warehouse/overview", label: "大数据架构" },
      { site: "kafka", path: "/01-basics/architecture", label: "消息架构" },
      { site: "system-design", path: "/short-url", label: "短链架构案例" }
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
🧠 并发理论  →  JMM / happens-before / CAS
🧵 线程池   →  ThreadPoolExecutor / 虚拟线程
🏛️ HA 理论  →  CAP / BASE / Raft / 幂等
🚦 限流    →  令牌桶 / 滑动窗口
⚡ 熔断    →  三态机 / Sentinel
🧩 微服务  →  拆分 / 服务发现 / 网关
🔄 分布式事务→  2PC / TCC / Saga
📨 消息队列  →  Kafka / 幂等 / 死信
💾 缓存    →  多级缓存 / 三大问题
🗄️ 分库分表  →  水平拆分 / 路由 / 分布式 ID
🧠 DDD     →  聚合 / 限界上下文 / 事件风暴
🧱 微服务模式→  Service Mesh / Sidecar
🔭 可观测   →  Metrics / Tracing / Logging
🏢 案例   →  秒杀 / 短链 / 异地多活
```

完整路径请看 [📖 学习路径](/path)。

## 💡 学习建议

```
1. 后端工程师  →  并发理论 + 限流 + 熔断 + 案例
2. 架构师    →  CAP / BASE / Saga / DDD / 微服务
3. 面试      →  CAP + 缓存三大问题 + 秒杀设计
4. SRE      →  限流 / 熔断 / 可观测 / 异地多活
```