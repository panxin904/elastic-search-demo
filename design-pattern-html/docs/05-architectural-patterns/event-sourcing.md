---
title: Event Sourcing 事件溯源
date: 2026-08-15  # date-auto-injected
description: 用事件序列保存状态 + Axon / EventStoreDB + 优势与挑战
---

# Event Sourcing 事件溯源

## 核心问题

传统 CRUD 只保留对象当前状态，丢失历史：
- 无法审计（不知道谁改了什么）
- 无法回放（出错难以复现）
- 无法时间旅行（不能查询任意时间点的状态）
- 业务分析困难（缺少历史数据）

## 核心思想

不保存对象的当前状态，而是保存**导致状态变化的全部事件**。当前状态 = replay 所有事件。

```sql
-- 传统：只保留最新状态
UPDATE accounts SET balance = 100 WHERE id = 'alice';
-- 历史丢失

-- Event Sourcing：保留事件流
-- 1. AccountOpened{alice, 0}
-- 2. MoneyDeposited{alice, +1000}
-- 3. MoneyWithdrawn{alice, -500}
-- 4. MoneyDeposited{alice, +200}
-- replay 后: balance = 700
```

## 实战：Axon Event Sourcing

```java
// 聚合根只产生事件，不直接修改字段
@Aggregate
public class BankAccount {
    @AggregateIdentifier
    private String accountId;
    private BigDecimal balance;

    // 命令处理：校验 + 产生事件
    @CommandHandler
    public BankAccount(OpenAccountCommand cmd) {
        apply(new AccountOpenedEvent(cmd.getAccountId(), cmd.getInitialBalance()));
    }

    @CommandHandler
    public void handle(DepositMoneyCommand cmd) {
        if (cmd.getAmount().signum() <= 0) {
            throw new IllegalArgumentException("Deposit must be positive");
        }
        apply(new MoneyDepositedEvent(cmd.getAccountId(), cmd.getAmount()));
    }

    @CommandHandler
    public void handle(WithdrawMoneyCommand cmd) {
        if (balance.compareTo(cmd.getAmount()) < 0) {
            throw new IllegalStateException("Insufficient balance");
        }
        apply(new MoneyWithdrawnEvent(cmd.getAccountId(), cmd.getAmount()));
    }

    // 事件溯源：修改字段
    @EventSourcingHandler
    public void on(AccountOpenedEvent event) {
        this.accountId = event.getAccountId();
        this.balance = event.getInitialBalance();
    }

    @EventSourcingHandler
    public void on(MoneyDepositedEvent event) {
        this.balance = this.balance.add(event.getAmount());
    }

    @EventSourcingHandler
    public void on(MoneyWithdrawnEvent event) {
        this.balance = this.balance.subtract(event.getAmount());
    }
}

// 仓库：自动 replay 事件加载聚合
@Repository
public class BankAccountRepository {
    @Autowired private EventStore eventStore;

    public BankAccount findById(String id) {
        // 加载所有事件，replay 出当前状态
        DomainEventStream stream = eventStore.readEvents(id);
        BankAccount account = new BankAccount();  // 空状态
        while (stream.hasNext()) {
            AccountEvent event = (AccountEvent) stream.next();
            account.on(event);  // 应用事件，修改字段
        }
        return account;
    }
}
```

## Snapshots 优化

replay 100 万个事件太慢，**Snapshot（快照）** 优化：

```java
// 每 100 个事件做一次快照
public class BankAccountSnapshot {
    private String accountId;
    private BigDecimal balance;
    private long eventVersion;

    @EventSourcingHandler
    public void on(AccountOpenedEvent event) { /* ... */ }
}

// 加载流程：
// 1. 加载最近的快照（假设是 version 1000）
// 2. 加载 version 1001 之后的所有事件
// 3. 应用这些事件到快照状态

public BankAccount loadWithSnapshot(String id) {
    // 1. 加载快照
    BankAccountSnapshot snapshot = snapshotRepo.findLatest(id);

    // 2. 从快照版本之后加载事件
    DomainEventStream stream = eventStore.readEvents(id, snapshot.getEventVersion() + 1);

    // 3. 应用事件
    BankAccount account = new BankAccount(snapshot);
    while (stream.hasNext()) {
        account.on((AccountEvent) stream.next());
    }
    return account;
}
```

**Snapshot 策略**：
- 每 N 个事件（如 100 / 500）
- 或每 T 时间（如每天一次）
- 或聚合 size 超过阈值时

## 实战：Git 内部

Git 是 Event Sourcing 的经典案例：

```bash
# 每次 commit 是一个事件
git log --oneline
# a3f2c8 (HEAD -> main) feat: add login
# 8d7e1b fix: handle null
# 6c5d9a initial commit

# 任意版本的状态 = checkout 对应 commit
git checkout a3f2c8  # 时间旅行到 a3f2c8

# git reset = 删除某些事件
git reset HEAD~1  # 撤销最后一次事件
```

## 数据库 binlog

MySQL / PostgreSQL / Oracle 的 binlog / WAL 也是 Event Sourcing：

```bash
# MySQL binlog
mysqlbinlog --start-datetime='2024-01-01' binlog.000001

# Debezium 监听 binlog 生成事件流
```

## Kafka 提交日志

Kafka topic 本身就是不可变的事件流：

```java
// Kafka topic：order-events
// 每个消息是一个领域事件
@KafkaListener(topics = "order-events")
public void process(String eventJson) {
    OrderEvent event = parse(eventJson);
    // 处理事件
}
```

## 优势与挑战

## 优势

1. **完整审计**：所有状态变化可追溯
2. **时间旅行**：可以查询任意时间点的状态
3. **事件驱动**：天然适合 Event-Driven Architecture
4. **调试容易**：测试时 replay 真实事件
5. **业务洞察**：事件流可分析（用户行为 / 业务流程）

## 挑战

1. **复杂查询困难**：要算当前状态必须 replay 全部事件（用 snapshot 缓解）
2. **schema 演进**：事件结构变了要兼容老事件
3. **存储成本**：事件不断增长，需要冷热分离
4. **调试复杂**：业务方不熟悉事件模型
5. **查询能力受限**：需要 CQRS + 读模型补充

## 适用边界

✅ **使用场景**：
- 金融 / 支付（必须审计）
- 业务规则复杂（订单状态机）
- 需要事件分析（用户行为）
- 跨服务集成（事件驱动）

❌ **避免场景**：
- 简单 CRUD（直接读写数据库）
- 团队无 Event Sourcing 经验
- 业务规则经常变（事件 schema 难维护）

🔄 **与 CQRS 关系**：
- Event Sourcing 是 CQRS 的**写端实现**
- CQRS 是 Event Sourcing 的**读端优化**
- 两者经常一起使用

💡 **最佳实践**：
- Event Schema 用 Avro / Protobuf（强 schema + 演进兼容）
- Snapshot 策略选择（每 N 事件 / 每 T 时间）
- 事件不可变（避免修改历史）
- 事件版本号管理（upcasting 处理 schema 演进）


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
<!-- auto-enrich:do-not-edit -->
