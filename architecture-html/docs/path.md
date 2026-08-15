---
title: 学习路径
---
# 📖 企业级架构 学习路径

## 🛤️ 路径 1：架构入门（1 周）
1. [JMM 内存模型](/01-concurrency-theory/jmm) — 并发编程的根
2. [CAP 定理](/03-ha-theory/cap) — 分布式系统设计的基础
3. [限流令牌桶算法](/04-rate-limit/token-bucket) — 高可用三件套之 1
4. [熔断器三态](/05-circuit-breaker/states) — 高可用三件套之 2
5. [微服务拆分原则](/06-microservice/split) — 微服务怎么拆

**目标**：能讲清"为什么这么设计"，不只是会用框架。

## 🛤️ 路径 2：分布式后端（2-3 周）
- 完成"入门"路径
- [happens-before](/01-concurrency-theory/happens-before) — 并发可见性
- [ThreadPoolExecutor](/02-thread-pool/executor) — 线程池原理
- [BASE / 最终一致性](/03-ha-theory/base) — 大多数系统选 AP
- [Raft 共识](/03-ha-theory/raft) — etcd/k8s/Consul 都用它
- [幂等性设计](/03-ha-theory/idempotency) — 分布式系统的"万金油"
- [分布式限流](/04-rate-limit/distributed) — Redis + Lua 方案
- [Kafka vs RabbitMQ](/08-message-queue/compare) — MQ 选型
- [秒杀系统](/14-enterprise-cases/flash-sale) — 经典案例

**目标**：能设计一个高可用的分布式系统。

## 🛤️ 路径 3：架构师（3-4 周）
- 完成"分布式后端"路径
- [CAS / Lock-Free](/01-concurrency-theory/cas) — 并发性能优化
- [JDK 21 虚拟线程](/02-thread-pool/virtual) — 性能飞跃
- [Raft 共识](/03-ha-theory/raft) — 深入了解 leader election
- [TCC 模式](/07-distributed-tx/tcc) — 高一致性业务
- [Saga 模式](/07-distributed-tx/saga) — 长事务补偿
- [多级缓存架构](/09-cache/architecture) — 缓存分层
- [水平/垂直拆分](/10-database-sharding/strategy) — 数据扩展
- [DDD 聚合 / 实体 / 值对象](/11-ddd/basics) — 领域建模
- [Service Mesh](/12-microservice-patterns/service-mesh) — 微服务基础设施
- [Metrics/Tracing/Logging](/13-observability/three-pillars) — 可观测三大支柱
- [异地多活](/14-enterprise-cases/multi-region) — 终极容灾

**目标**：能设计跨数据中心的高可用架构。

## 🛤️ 路径 4：面试冲刺（2 周）
- 复习 [CAP 定理](/03-ha-theory/cap) + [BASE](/03-ha-theory/base)
- 复习 [2PC / TCC / Saga](/07-distributed-tx/saga)
- 复习 [缓存三大问题](/09-cache/breakdown) — 击穿 / 穿透 / 雪崩
- 复习 [Token Bucket](/04-rate-limit/token-bucket) 算法
- 复习 [Raft 共识](/03-ha-theory/raft)
- 复习 [秒杀系统](/14-enterprise-cases/flash-sale) — 经典白板题
- 复习 [DDD 限界上下文](/11-ddd/bounded-context)
- 复习 [Service Mesh](/12-microservice-patterns/service-mesh) vs SDK 治理

## 🎯 速查卡片
| 我想 | 推荐先看 |
|------|---------|
| 学并发编程原理 | [JMM 内存模型](/01-concurrency-theory/jmm) → [happens-before](/01-concurrency-theory/happens-before) |
| 学分布式系统 | [CAP 定理](/03-ha-theory/cap) → [BASE](/03-ha-theory/base) → [Raft 共识](/03-ha-theory/raft) |
| 学高可用三件套 | [限流](/04-rate-limit/token-bucket) → [熔断](/05-circuit-breaker/states) |
| 学分布式事务 | [2PC / 3PC](/07-distributed-tx/2pc) → [TCC](/07-distributed-tx/tcc) → [Saga](/07-distributed-tx/saga) |
| 学 DDD | [聚合 / 实体 / 值对象](/11-ddd/basics) → [限界上下文](/11-ddd/bounded-context) |
| 面试准备 | [秒杀系统](/14-enterprise-cases/flash-sale) + [CAP 定理](/03-ha-theory/cap) + [缓存三大问题](/09-cache/breakdown) |