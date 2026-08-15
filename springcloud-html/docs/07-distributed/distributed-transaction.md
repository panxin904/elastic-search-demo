---
title: 分布式事务
---

# 💰 分布式事务

> 在分布式环境下保证**多个数据源的操作要么全部成功要么全部失败**。

## 🎯 为什么需要分布式事务？

**单体应用**：单个数据库，本地事务（ACID）即可

```
BEGIN
  INSERT INTO orders ...
  UPDATE inventory SET stock = stock - 1 ...
COMMIT;
```

**分布式场景**：订单服务写 MySQL-orders，库存服务写 MySQL-inventory，本地事务无法跨库

```
订单服务 ─→ MySQL-orders      ─→ 提交成功
库存服务 ─→ MySQL-inventory   ─→ 提交失败 → 数据不一致！
```

## 📜 ACID 与 CAP

| 维度 | 单机 DB（ACID）| 分布式事务 |
|---|---|---|
| **原子性** | 全部成功或全部回滚 | 跨服务全部成功或全部回滚 |
| **一致性** | 强一致 | 最终一致（BASE）|
| **隔离性** | 多种隔离级别 | 业务自己保证 |
| **持久性** | 同步刷盘 | 多副本存储 |

## 🛠️ 主流分布式事务方案

### 1. 两阶段提交（2PC）

**流程：**
```
        协调者（TM）
        /    │    \
       ↓     ↓     ↓
    参与者A  参与者B  参与者C

阶段 1：投票（prepare）
  TM → A: prepare
  TM → B: prepare
  TM → C: prepare
  A → TM: ready / no
  B → TM: ready / no
  C → TM: ready / no

阶段 2：提交（commit）
  TM → A: commit (若全部 ready)
  TM → B: commit
  TM → C: commit
  TM → A: rollback (若有 no)
```

| 优点 | 缺点 |
|---|---|
| 强一致 | 同步阻塞（持有锁直到第二阶段） |
| 简单 | 协调者单点故障 |
| 标准化（XA 协议）| 数据不一致风险（第二阶段网络故障）|

**实现**：MySQL XA、Atomikos、Seata AT（部分 2PC）

### 2. 三阶段提交（3PC）

**改进点：** 在 2PC 的 prepare 和 commit 之间加 `preCommit`，降低阻塞范围

```
CanCommit → PreCommit → DoCommit
```

| 优点 | 缺点 |
|---|---|
| 降低阻塞 | 实现复杂 |
| 引入超时机制 | 仍可能数据不一致 |

### 3. TCC（Try-Confirm-Cancel）

**核心思想：** 把每个分支事务拆成三个操作

| 阶段 | 操作 |
|---|---|
| **Try** | 资源检查 + 预留（冻结库存）|
| **Confirm** | 真正执行业务（扣减冻结的库存）|
| **Cancel** | 释放预留（解冻库存）|

**示例：转账 A → B**

```java
// Try 阶段
try {
    // 冻结 A 账户 100 元
    accountA.freeze(100);
    // 冻结 B 账户入账 100 元（待入账）
    accountB.freezeCredit(100);
} catch (Exception e) {
    // Cancel
}

// Confirm 阶段（全部 Try 成功后）
try {
    accountA.confirmDebit();  // A 实际扣款
    accountB.confirmCredit(); // B 实际入账
} catch (Exception e) {
    // 重试 / 人工介入
}

// Cancel 阶段（任一失败）
cancelA(); cancelB();
```

| 优点 | 缺点 |
|---|---|
| 最终一致 / 高性能 | 业务侵入性强 |
| 灵活 | 需要实现 Try/Confirm/Cancel 三套接口 |

**框架**：Seata TCC、阿里 Dragonfly

### 4. AT 模式（Auto Transaction）

**原理：** 基于**本地事务 + 快照**自动实现 2PC，Seata 默认模式

```
阶段 1：解析 SQL → 生成 before/after 镜像 → 执行业务 SQL → 提交本地事务 → 上报 RM
阶段 2：TM 根据各 RM 上报结果 → 全成功则异步删除快照 / 任一失败则根据镜像回滚
```

| 优点 | 缺点 |
|---|---|
| 业务零侵入 | 有全局锁（性能损耗） |
| 自动生成回滚 SQL | 表必须有主键 / 需要 undolog |
| 简单 | 部分场景需要手动补偿 |

### 5. Saga 模式

**原理：** 把长事务拆为多个**本地事务 + 补偿动作**

```
T1 → T2 → T3（成功路径）
     ↓
     C2 → C1（补偿路径）
```

| 实现方式 | 含义 |
|---|---|
| **Orchestration** | 中心化的协调器（Orchestrator）调度各步骤 |
| **Choreography** | 各服务通过事件自行决策，无中心 |

| 优点 | 缺点 |
|---|---|
| 适合长事务 / 跨多服务 | 不保证隔离性 |
| 无锁 | 需要业务写补偿逻辑 |

**框架**：Seata Saga、Cadence、Apache ServiceComb Saga

### 6. 本地消息表

**原理：** 业务写本地消息表 + 定时扫描投递

```
1. 订单服务：写订单 + 写本地消息表（同事务）
2. 定时任务：扫描未发送的消息 → 投递到 MQ
3. 库存服务：消费 MQ → 扣减库存
4. 库存服务：扣减成功 → ack / 失败 → 重试
```

| 优点 | 缺点 |
|---|---|
| 最终一致性 | 消息可能重复（需幂等） |
| 简单可靠 | 不适合高实时场景 |

### 7. 事务消息（RocketMQ）

```
1. 发送 Half 消息（对消费者不可见）
2. 本地事务执行（更新订单）
3. 根据本地事务结果 commit / rollback MQ 消息
4. 若 MQ 未收到 ack → 回查本地事务状态
```

| 优点 | 缺点 |
|---|---|
| 业务友好 | 依赖特定 MQ |
| 不丢失消息 | 需要回查机制 |

## 📊 方案对比

| 方案 | 一致性 | 性能 | 业务侵入 | 适用场景 |
|---|---|---|---|---|
| **2PC / XA** | 强一致 | 低 | 无 | 短事务、DB 内部 |
| **3PC** | 强一致 | 低 | 无 | 几乎不用 |
| **TCC** | 最终一致 | 高 | **高** | 高并发、核心金融 |
| **AT** | 最终一致 | 中 | 低 | 通用微服务（推荐）|
| **Saga** | 最终一致 | 高 | 中 | 长事务 / 跨多服务 |
| **本地消息表** | 最终一致 | 中 | 中 | 异步场景（最常用）|
| **事务消息** | 最终一致 | 中 | 中 | MQ 场景（推荐）|

## 🎯 选型决策树

```
                    强一致要求？
                         │
              ┌──────────┴──────────┐
              是                    否（可最终一致）
              │                            │
         性能要求？                  业务侵入容忍？
              │                            │
        ┌─────┴─────┐              ┌───────┴───────┐
       高           低              高             低
        │            │              │               │
       TCC          2PC/XA         Saga/         本地消息表
        │                         TCC             / 事务消息
   Seata TCC                       │
                                  AT 模式
                                  (Seata 推荐)
```

## 🔧 Seata AT 实战

### Server 部署

```yaml
# registry.conf
registry {
  type = "nacos"
  nacos {
    serverAddr = "127.0.0.1:8848"
    namespace = "public"
    group = "SEATA_GROUP"
  }
}
config {
  type = "nacos"
  nacos {
    serverAddr = "127.0.0.1:8848"
    group = "SEATA_GROUP"
  }
}
```

### 业务使用

```java
// 1. 加注解
@GlobalTransactional(name = "create-order", rollbackFor = Exception.class)
public Order createOrder(OrderDTO dto) {
    // 1. 订单服务：创建订单
    Order order = orderMapper.insert(dto);

    // 2. 远程调用库存服务
    inventoryFeign.deduct(dto.getSkuId(), dto.getCount());

    // 3. 远程调用账户服务
    accountFeign.debit(dto.getUserId(), dto.getAmount());

    return order;
}
```

**Seata 三大角色：**
- **TC（Transaction Coordinator）**：事务协调器（Server）
- **TM（Transaction Manager）**：事务管理器（标注 `@GlobalTransactional` 的方法入口）
- **RM（Resource Manager）**：资源管理器（各微服务数据库代理）

## ⚠️ 分布式事务的常见问题

### 1. 空回滚

TCC 中 Try 未执行（网络问题）→ Cancel 被调用 → 业务异常

**解决：** Cancel 中检查 Try 是否执行过

### 2. 幂等性

重试 / 网络抖动导致同一操作多次执行

**解决：** 唯一业务键 + 数据库唯一索引 / Redis SETNX

### 3. 悬挂

Cancel 先执行 → Try 后执行 → Try 占用了不应占用的资源

**解决：** Try 中检查 Cancel 是否已执行

### 4. 脑裂

协调者发 commit，但部分节点收到，部分未收到

**解决：** 引入超时机制 + 自动恢复

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| 分布式事务方案？| 2PC / 3PC / TCC / AT / Saga / 本地消息表 / 事务消息 |
| Seata AT 原理？| 本地事务 + 快照 + 异步回滚 |
| TCC 三阶段？| Try 预留 → Confirm 确认 → Cancel 取消 |
| 如何保证幂等？| 唯一键 + 状态机 + 乐观锁 |

---

- 上一章：[🔐 分布式锁](/07-distributed/distributed-lock)
- 下一章：[🆔 分布式 ID](/07-distributed/distributed-id)