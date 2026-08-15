---
title: 领域驱动设计 DDD
---

# 领域驱动设计（DDD）

DDD 适用于复杂业务场景，通过领域建模让代码结构与业务逻辑一致。

## 核心概念

| 概念 | 说明 | 示例 |
|---|---|---|
| 实体 Entity | 有唯一标识、可变 | User (有 userId) |
| 值对象 VO | 无唯一标识、不可变 | Address, Money |
| 聚合根 | 聚合的入口，保证一致性 | Order（聚合根，管理 OrderItem） |
| 领域服务 | 不属于单个实体的业务逻辑 | TransferService（转账） |
| 仓储 Repository | 聚合的持久化 | OrderRepository |

## 分层结构

```
├── interfaces/        # 接口层（Controller, MQ Listener）
├── application/       # 应用层（编排、事务）
├── domain/            # 领域层（核心）
│   ├── entity/        # 实体
│   ├── valueobject/   # 值对象
│   ├── service/       # 领域服务
│   └── repository/    # 仓储接口
└── infrastructure/    # 基础设施层（Repository 实现、外部调用）
```

## DDD vs 传统三层

| | 传统三层 | DDD |
|---|---|---|
| 组织方式 | 按技术职责分层 | 按业务领域分包 |
| 业务逻辑 | 集中在 Service | 分散在实体、值对象、领域服务 |
| 适合 | 简单 CRUD | 复杂业务规则 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="ddd" :height="400" />
