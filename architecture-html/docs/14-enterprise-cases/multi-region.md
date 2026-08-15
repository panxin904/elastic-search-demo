---
title: 异地多活
---
# 异地多活设计

## 1. 为什么异地多活

单机房：
  简单、低成本
  单点故障：地震 / 火灾 / 电力 → 全站停
  容量天花板（一个机房）
  延迟：异地用户访问慢

异地多活：多机房同时服务
  容灾（任一机房挂了其他接管）
  就近访问（用户走最近机房）
  容量扩展（横向）
  复杂（数据同步 / 流量调度 / 一致性）

## 2. 三种部署模式

### 同城双活

机房 A 和 B 在同一城市，RTT < 2ms。

适用：金融 / 支付 / 关键业务。
成本：高（机房 + 专线）。

### 异地灾备

主机房 + 异地备机房，平时备机房不服务，灾备时切换。

适用：大多数传统企业。
问题：RTO（恢复时间）= 数小时。

### 异地多活（真正的）

所有机房同时服务，任一机房挂了不影响其他。

适用：互联网大型应用。
挑战：最大（数据冲突 / 流量切分）。

## 3. 异地多活三大挑战

### 3.1 数据同步

机房 A 写入 → 同步到机房 B
  同步延迟：50-200ms
  同步故障：丢数据
  冲突：两机房同时改同一条数据

解决：
- 单向同步（主 → 备）
- 双向同步 + 冲突解决策略（最后写胜 / 业务时间戳）
- CRDT（Conflict-free Replicated Data Types）

### 3.2 流量调度

用户请求 → DNS 解析 → 就近机房

DNS GeoDNS：
  - 北京用户 → 解析为 A 机房 IP
  - 上海用户 → 解析为 B 机房 IP
  - 广州用户 → 解析为 C 机房 IP

GSLB (Global Server Load Balancing)：
  - 阿里云 DNS / 腾讯云 GSLB
  - 智能解析 + 健康检查
  - 故障自动切换

### 3.3 数据冲突

场景：
  A 机房用户下单 → 写入 A 机房
  B 机房用户改同一单 → 写入 B 机房
  → 同步冲突，谁胜？

解决：
- 业务路由：按 userId hash → 固定机房（A 用户只在 A 写）
- 乐观锁 + 时间戳胜
- CRDT / 事件溯源

## 4. 经典模式

### 4.1 同城双活（最常见）

   ┌──── 上海机房 A ────┐    ┌──── 上海机房 B ────┐
   │  应用 + DB 主      │ ←→ │  应用 + DB 备      │
   │  用户（主）         │    │  用户（备/对读）     │
   └─────────────────────┘    └─────────────────────┘
              ↑ 同步（实时，双向）

特点：
- RTT < 2ms → 同步实时
- 故障切换快（秒级）
- 成本高（同城市双机房 + 万兆专线）

### 4.2 单元化异地多活

按 userId hash 分片：
  userId % 4 == 0 → 单元 0（北京）
  userId % 4 == 1 → 单元 1（上海）
  userId % 4 == 2 → 单元 2（广州）
  userId % 4 == 3 → 单元 3（深圳）

特点：
- 每个用户只在一个机房
- 单机房故障只影响 1/4 用户
- 故障切换：把对应单元的 userId 切到其他机房（重新 hash）

代表：阿里 / 字节 / 美团的单元化架构。

### 4.3 主备异地

机房 A（主）  ←异地专线  机房 B（备，平时不服务）
  ↑
只读镜像

特点：成本低，简单。
缺点：RTO 数小时，不算"多活"。

## 5. 实战：阿里单元化

userId 路由层（GSLB / DNS）
  ↓
  unit = userId % N
  ↓
  路由到单元 N 的机房
  ↓
  本地机房 Redis + DB
  写操作只发生在本地
  读操作：本地优先 → 跨单元读 fallback

## 6. 数据同步

### 6.1 同步中间件

- Otter（阿里）：MySQL binlog 同步
- Canal / Maxwell：MySQL → MQ
- DRC：阿里自研

### 6.2 同步原则

1. 写主机房 → 同步备机房（异步）
2. 最终一致（不等同步完成才返回）
3. 同步失败 → 重试 + 告警 + 人工
4. 冲突解决：业务时间戳胜 + 业务路由

### 6.3 同步设计

```java
@EventListener
public void onOrderCreated(OrderCreatedEvent e) {
  // 本地写
  orderRepo.save(e);
  // 异步同步到其他单元
  kafkaTemplate.send("order-sync", e);
  // 消费者：在远端机房重建数据
}
```

## 7. 流量调度

### DNS GeoDNS

阿里云 DNS 配置
- 北京：返回 A 机房 IP
- 上海：返回 B 机房 IP
- 广州：返回 C 机房 IP

### 应用层路由

```java
// 智能 DNS 解析
public String resolveServer(String userId) {
  int unit = userId.hashCode() % 4;
  return switch (unit) {
    case 0 -> "unit0.api.example.com";
    case 1 -> "unit1.api.example.com";
    case 2 -> "unit2.api.example.com";
    default -> "unit3.api.example.com";
  };
}
```

## 8. 故障切换

### 主动切换（planned）

1. 流量切到其他机房
2. 等待完成（max 5min）
3. 机房维护
4. 流量切回

### 故障切换（unplanned）

1. GSLB 健康检查发现机房故障
2. 自动剔除该机房 IP
3. 流量全部切到其他机房
4. 触发告警
5. 工程师介入修复

## 9. 实战 checklist

- 单元化拆分（按 userId hash）
- GSLB + DNS GeoDNS
- 数据双向同步 + 冲突解决
- 故障自动切换 + 告警
- 演练（每季度一次）
- 监控覆盖各机房
- 文档完整（RTO / RPO 明确）

## 10. 实战选型

| 规模 | 方案 |
|------|------|
| 传统企业 | 双活 + Otter 同步 |
| 互联网中大型 | 单元化（阿里 / 美团） |
| 巨型 | 单元化 + 全球 GSLB（字节 / Google） |
| 创业 | 异地灾备 + DNS |

## 11. 关键指标

- RTO（Recovery Time Objective）：恢复时间目标
- RPO（Recovery Point Objective）：可丢失数据时间

| 等级 | RTO | RPO |
|------|------|------|
| 单机房 | ∞ | 全丢 |
| 同城双活 | 分钟 | 0 |
| 异地灾备 | 小时 | 分钟-小时 |
| 异地多活 | 秒-分钟 | 0-秒 |

## 12. 实战案例

阿里双 11：
- 单元化（按 userId hash 分片）
- 实时同步（Otter + MQ）
- GSLB 流量调度
- 单机房故障秒级切流

## 🔗 下一步
- [BASE / 最终一致性](/03-ha-theory/base)
- [Raft 共识](/03-ha-theory/raft)
- [Saga 模式](/07-distributed-tx/saga)