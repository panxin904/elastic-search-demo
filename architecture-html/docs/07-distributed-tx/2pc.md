---
title: 2PC / 3PC
date: 2026-08-15  # date-auto-injected
---
# 2PC / 3PC 分布式事务

## 1. 为什么需要分布式事务

```
单体：本地 ACID 事务
  - transfer account A: balance -= 100
  - transfer account B: balance += 100
  - COMMIT → 一起成功 / ROLLBACK → 一起回滚

分布式：跨服务 / 跨数据库
  A 服务扣款 → B 服务加款
  - 网络可能失败
  - 节点可能宕机
  - 怎么保证原子性？
```

## 2. 2PC（Two-Phase Commit）

```
                Coordinator
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
     Service A   Service B   Service C
```

**Phase 1（Prepare）**：
- Coordinator：你们能 commit 吗？
- A / B / C：执行但不提交，记 redo/undo log → 返回 "ready"
- 任意一个返回 "no" → 中止

**Phase 2（Commit / Rollback）**：
- 全部 ready → Coordinator 发 commit
- A / B / C：真正提交 → 返回 "done"

## 3. 2PC 的致命问题

### 同步阻塞

Prepare 阶段后，所有节点持有锁等协调者命令。**协调者宕机 → 所有节点永远等待**。

### 单点故障

协调者是 SPOF。**协调者恢复前所有事务卡住**。

### 数据不一致

```
1. Coordinator 收到全部 ready
2. Coordinator 发 commit
3. Coordinator 崩了
4. A 收到 commit，commit 成功
5. B 没收到 commit（网络问题）
→ A 扣款，B 没加款 → 钱丢了！
```

## 4. 3PC（Three-Phase Commit）

2PC 之上加 **PreCommit** 中间状态，try-fix 同步阻塞：

```
Phase 1 (CanCommit)   → 协调者问"能不能 commit"
Phase 2 (PreCommit)    → 协调者说"准备提交"，所有节点 ack
Phase 3 (doCommit)     → 真正提交
```

**改进**：协调者崩了 → 节点超时自动 commit（PreCommit 已 ack）。
**问题**：网络分区时可能脑裂（部分 commit / 部分 rollback）。

## 5. 为什么生产不用 2PC / 3PC

```
❌ 同步阻塞 = 长事务 = 锁持有 = 性能差
❌ SPOF = 可用性差
❌ 协调者 = 性能瓶颈
✅ 实际上只有 DB 内部用（XA 事务）
✅ 微服务用 BASE 替代（最终一致 + 补偿）
```

**现代分布式事务 = Saga / TCC / 本地消息表 / 事件驱动**。

## 6. XA 事务（数据库层 2PC）

```sql
-- MySQL XA
XA START 'transfer-001';
UPDATE account SET balance = balance - 100 WHERE id = 1;
UPDATE account SET balance = balance + 100 WHERE id = 2;
XA END 'transfer-001';
XA PREPARE 'transfer-001';  -- phase 1
XA COMMIT 'transfer-001';  -- phase 2
```

DB 层 2PC 适用单机多库场景，但跨服务不适用。

## 7. 分布式事务选型矩阵

| 场景 | 方案 |
|------|------|
| 单 DB 多表 | 传统 ACID |
| 单服务多 DB | 2PC / XA |
| 微服务强一致 | **TCC** / Saga |
| 微服务最终一致 | Saga + 补偿 / 本地消息表 |
| 跨服务异步 | MQ + 幂等 |

## 8. 从 2PC 思维学到的

1. **两阶段**：prepare 预提交 + commit 真正提交
2. **幂等**：commit 操作必须可重入
3. **超时**：每个阶段必须有超时
4. **补偿**：commit 后必须能补偿

## 🔗 下一步
- [TCC 模式](/07-distributed-tx/tcc)
- [Saga 模式](/07-distributed-tx/saga)
- [本地消息表](/07-distributed-tx/local-table)
- [BASE / 最终一致性](/03-ha-theory/base)
