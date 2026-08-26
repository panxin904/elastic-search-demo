---
title: 两阶段提交（2PC）
---

# 两阶段提交（2PC）

> Two-Phase Commit。最经典的分布式事务协议，也是最被诟病的协议。

## 1. 什么是分布式事务？

```
单体应用：
  BEGIN
    UPDATE account SET balance = balance - 100 WHERE id = 1
    UPDATE account SET balance = balance + 100 WHERE id = 2
  COMMIT
  → 数据库保证原子性

分布式场景：
  - 账户服务扣款
  - 订单服务下单
  - 库存服务扣库存
  - 三个数据库在三个机器
  → 单一数据库的 ACID 不够用了
  → 需要分布式事务协调
```

## 2. 2PC 的角色

```
Coordinator（协调者）：
  - 整个事务的"指挥官"
  - 决定 commit 或 abort

Participants（参与者）：
  - 实际执行本地事务的节点
  - 每个参与者有自己的本地事务
```

## 3. 两阶段流程

### 3.1 阶段 1：Prepare（投票）

```
Coordinator:
  1. 写本地事务日志（begin）
  2. 发 PREPARE 给所有 Participants
  3. 进入"等待"状态

Participants:
  1. 收到 PREPARE
  2. 执行本地事务（写 undo log + redo log）
  3. 锁定相关资源
  4. 返回 VOTE_COMMIT 或 VOTE_ABORT

Coordinator:
  - 收到所有 VOTE_COMMIT → 进入阶段 2 COMMIT
  - 任一 VOTE_ABORT 或超时 → 进入阶段 2 ABORT
```

### 3.2 阶段 2：Commit（决定）

```
COMMIT 路径：
  Coordinator:
    1. 写本地日志（commit）
    2. 发 COMMIT 给所有 Participants
    3. 等待所有 ACK
  Participants:
    1. 收到 COMMIT
    2. 真正提交本地事务
    3. 释放锁
    4. 返回 ACK
  Coordinator:
    1. 收到所有 ACK
    2. 写日志（end）
    3. 事务完成

ABORT 路径：
  Coordinator:
    1. 写本地日志（abort）
    2. 发 ABORT 给所有 Participants
  Participants:
    1. 收到 ABORT
    2. 回滚本地事务（用 undo log）
    3. 释放锁
    4. 返回 ACK
  Coordinator:
    1. 收到所有 ACK
    2. 写日志（end）
    3. 事务完成
```

## 4. 直觉

```
类比：结婚
  - 主持人（Coordinator）问新郎新娘（Participants）
  - "你愿意吗？"（PREPARE）
  - 双方都说"我愿意"（VOTE_COMMIT）
  - 主持人宣布"礼成"（COMMIT）
  - 任何一方说"不愿意"（VOTE_ABORT）
  - 主持人宣布"婚礼取消"（ABORT）
```

## 5. 致命缺陷

### 5.1 同步阻塞

```
Prepare 阶段：
  Participants 必须**锁定资源**等 Coordinator 决定
  → 其他事务要访问这些资源 → 等待
  → 系统吞吐大幅下降

📌 高并发场景下：
  - 锁等待时间长
  - 大量事务堆积
  - 系统响应慢
```

### 5.2 Coordinator 单点

```
Coordinator 故障场景：

1. Coordinator 在 COMMIT 前挂了
   - Participants 不知道要 commit 还是 abort
   - 资源永久锁定
   - 必须人工介入

2. Coordinator 在发 COMMIT 后挂了
   - Participants 可能没收到
   - 资源锁定等待
   - 重启后靠日志恢复

📌 协调者是最脆弱的点
```

### 5.3 数据不一致

```
最坏情况：
  - Coordinator 收到多数 ACK
  - 决定 COMMIT
  - 发 COMMIT 给 Participants
  - 发给 P1 的 COMMIT 成功，P1 commit
  - 发给 P2 的 COMMIT 网络丢包
  - P2 仍在等（资源锁定）
  - P3 没收到，P3 abort（因为超时）
  → P1 commit, P2 锁定, P3 abort
  → 状态不一致
```

### 5.4 脑裂

```
Coordinator 与 Participants 网络分区：
  - Coordinator 认为多数 P 都在（多数派 ACK）
  - 但实际只有少数派能联系
  - 发 COMMIT 给少数派
  - 多数派等不到，等超时后 abort
  → 不同节点状态不一致
```

## 6. 工程改进

### 6.1 同步转异步

```
传统 2PC：
  - Prepare → 等所有回应 → Commit → 等所有 ACK
  - 同步阻塞

改进：
  - Prepare 后立即返回给客户端（不等所有 ACK）
  - 后台异步收集 ACK
  - 达到多数派后 commit
  → 客户端延迟降低

📌 但仍然有"不确定状态"
```

### 6.2 预写日志（WAL）

```
Coordinator 持久化日志：
  - begin 标记
  - commit/abort 决定
  - end 标记
  → 故障后能恢复决定

Participants 持久化日志：
  - 本地事务状态
  - 收到的 commit/abort
  → 故障后能恢复本地状态
```

### 6.3 超时机制

```
Coordinator 等待 Participants 超时：
  - 默认 abort（保守策略）

Participants 等待 Coordinator 超时：
  - 询问其他 Participants
  - 或直接 abort
  → 减少永久阻塞

📌 但仍可能误判
```

## 7. XA 协议

```
XA = eXtended Architecture
  - 2PC 的工业标准实现
  - 数据库驱动层支持
  - 全局事务管理器 + 局部资源管理器

支持：Oracle / MySQL / PostgreSQL / DB2
框架：Atomikos / Bitronix / Narayana
```

### 7.1 XA 接口

```
资源管理器（RM）接口：
  - xa_start：开启事务分支
  - xa_end：结束事务分支
  - xa_prepare：准备提交
  - xa_commit：提交
  - xa_rollback：回滚

事务管理器（TM）接口：
  - xa_open / xa_close：连接管理
  - xa_start / xa_end：管理全局事务

📌 实际应用通过 ODBC / JDBC 暴露
```

### 7.2 XA 的使用

```java
// 示例：Java + Atomikos
UserTransactionManager tm = new UserTransactionManager();
tm.begin();

// 多个数据源
dataSource1.execute("UPDATE ...");
dataSource2.execute("INSERT ...");

// 两阶段提交
tm.commit();  // 内部走 2PC
```

### 7.3 XA 的局限

```
1. 同步阻塞（同 2PC）
2. 协调者单点
3. 数据库必须支持 XA
4. 全局锁，影响性能
5. 不适合长事务

📌 现代微服务架构基本不用 XA
```

## 8. 实际工程怎么选？

```
📌 优先：避免分布式事务
   - 设计上避免跨服务事务
   - 用最终一致性替代
   - 单服务用本地事务

真要分布式事务：
  - 强一致 + 短事务 + 低并发：2PC / XA
  - 高并发 + 可补偿：TCC
  - 长事务 + 业务可拆分：Saga
  - 异步可靠消息：本地消息表 / 事务消息
```

## 9. 案例分析：转账

```
需求：A 转账给 B（跨账户服务）

2PC 方案：
  1. Coordinator 开始全局事务
  2. Account Service A：扣款（Prepare → 锁定）
  3. Account Service B：加款（Prepare → 锁定）
  4. 都成功 → Coordinator 发 COMMIT
  5. 两边真正提交

📌 问题：
   - 整个过程 A 和 B 资源锁定
   - 任何环节失败都要回滚
   - 高并发下性能差

替代方案：本地消息表 + 异步
  1. A 扣款成功 + 写本地消息表
  2. 后台 worker 把消息发给 MQ
  3. B 消费消息 + 加款
  → 见 saga.md 与本地消息表章节
```

## 10. 一句话总结

```
📌 2PC 是分布式事务的"老古董"，理论简单但工程缺陷严重
📌 同步阻塞 + 协调者单点 + 数据不一致是三大致命问题
📌 XA 是 2PC 的工业标准，但现代微服务基本不用
📌 工程上能用本地事务就别用分布式事务
📌 真要用：短事务 + 低并发 + 强一致场景
📌 高并发场景用 TCC / Saga / 异步消息替代
```

## 11. 参考资料

- Transaction Recovery in Distributed Database Systems (Gray, 1978)
- Distributed Recovery (Skeen, 1981)
- XA Specification (X/Open)
- Atomikos Documentation
- Seata 文档
- DDIA 第 9 章


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
