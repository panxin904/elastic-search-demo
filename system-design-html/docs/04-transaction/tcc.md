---
title: TCC 补偿事务
---

# TCC 补偿事务

> Try-Confirm-Cancel，把分布式事务拆成 3 个阶段，业务自己写补偿逻辑。**性能高，代码侵入大**。

## 1. 什么是 TCC？

```
TCC = Try + Confirm + Cancel
  - Try：预留资源（业务检查 + 锁定）
  - Confirm：真正执行业务（使用 Try 预留的资源）
  - Cancel：释放 Try 预留的资源

📌 区别于 2PC：
   2PC = 协议层，由 DB 驱动
   TCC = 业务层，由应用代码驱动
   TCC 性能高（无锁），但要写 3 个方法
```

## 2. 三阶段详解

### 2.1 Try 阶段

```
作用：
  - 完成业务检查（一致性）
  - 预留必需业务资源（准隔离性）

例：转账 A → B 100 元
  A.Try：
    - 检查 A 余额 ≥ 100
    - A 余额冻结 100
  B.Try：
    - 检查 B 账户存在
    - B 账户余额加 100（先标记"待入账"）

📌 Try 要满足幂等
   Try 不能真正修改业务数据，只预留
```

### 2.2 Confirm 阶段

```
作用：
  - 真正执行业务
  - 使用 Try 阶段预留的资源
  - 必须成功

例：转账 Confirm
  A.Confirm：
    - A 余额扣 100（把冻结的 100 扣掉）
  B.Confirm：
    - B 余额加 100（标记为已入账）

📌 Confirm 要满足幂等
   Confirm 不能报错回滚（资源已用）
   如果失败 → 人工介入
```

### 2.3 Cancel 阶段

```
作用：
  - 释放 Try 阶段预留的资源
  - 业务回滚

例：转账 Cancel
  A.Cancel：
    - A 余额解冻 100
  B.Cancel：
    - B 余额减 100（取消待入账）

📌 Cancel 要满足幂等
   允许空回滚（Try 未执行就收到 Cancel）
   允许防悬挂（Cancel 之后才到 Try）
```

## 3. 与 2PC 对比

| 维度 | 2PC | TCC |
|---|---|---|
| 协议层 | DB 驱动 | 业务驱动 |
| 锁 | 持锁到结束 | 几乎无锁 |
| 性能 | 低（长事务） | 高（短事务） |
| 代码侵入 | 小 | 大（3 个方法）|
| 适用 | 强一致 | 高并发 |

## 4. 工程实现

### 4.1 Seata TCC 模式

```java
// 1. 定义接口
@LocalTCC
public interface TransferService {
    @TwoPhaseBusinessAction(name = "transfer", commitMethod = "confirm", rollbackMethod = "cancel")
    boolean tryTransfer(@BusinessActionContextParameter(paramName = "from") String from,
                        @BusinessActionContextParameter(paramName = "to") String to,
                        @BusinessActionContextParameter(paramName = "amount") int amount);

    boolean confirmTransfer(BusinessActionContext context);
    boolean cancelTransfer(BusinessActionContext context);
}

// 2. 实现
@Service
public class TransferServiceImpl implements TransferService {
    @Autowired
    private AccountDao accountDao;

    @Transactional
    public boolean tryTransfer(String from, String to, int amount) {
        // 1. 检查余额
        Account fromAccount = accountDao.findById(from);
        if (fromAccount.getBalance() < amount) return false;

        // 2. 冻结
        accountDao.freeze(from, amount);
        return true;
    }

    public boolean confirmTransfer(BusinessActionContext ctx) {
        // 1. 扣减冻结
        accountDao.deductFrozen(ctx.getActionContext("from"), (int) ctx.getActionContext("amount"));
        // 2. 增加余额
        accountDao.add(ctx.getActionContext("to"), (int) ctx.getActionContext("amount"));
        return true;
    }

    public boolean cancelTransfer(BusinessActionContext ctx) {
        // 解冻
        accountDao.unfreeze(ctx.getActionContext("from"), (int) ctx.getActionContext("amount"));
        return true;
    }
}
```

### 4.2 ByteTCC / Hmily

```
TCC 框架对比：
  - Seata：阿里出品，生态最全
  - Hmily：基于 Java Agent，零侵入
  - ByteTCC：基于拦截器
  - tcc-transaction：华为

📌 主流用 Seata
   简单场景用 Hmily 零侵入
```

## 5. 关键问题

### 5.1 空回滚

```
场景：
  1. Try 请求因网络问题未到达
  2. 全局事务已发起 Cancel
  3. Cancel 到达 → 没有 Try 记录可回滚

解决：
  - Cancel 时检查是否执行过 Try
  - 加 Try 状态表（主键 = 业务 ID）
  - 没 Try 过 → 直接返回成功
```

### 5.2 幂等

```
问题：
  - 网络重试导致重复 Try / Confirm / Cancel
  - 重复扣款 / 重复冻结

解决：
  - 主键去重
  - 状态机：只有"待 Try"才能 Try，"待 Confirm"才能 Confirm
  - 唯一索引兜底
```

### 5.3 防悬挂

```
场景：
  1. Cancel 先到，Try 后到
  2. Try 执行成功 → 业务被错误处理

解决：
  - Cancel 成功 → 标记"已 Cancel"
  - Try 到达 → 检查是否已 Cancel
  - 已 Cancel → 不执行 Try
```

### 5.4 资源预留性能

```
问题：
  - Try 阶段冻结资金，Confirm/Cancel 才用/释放
  - 资源长期占用 → 用户体验差

优化：
  - 短事务：Try + Confirm 在毫秒级完成
  - 超时自动 Cancel（资源释放）
  - 资源预留轻量化（只锁必要的）
```

## 6. 经典案例

### 6.1 电商下单

```
流程：
  1. Try 订单：检查商品库存 → 冻结
  2. Try 支付：检查用户余额 → 冻结
  3. Try 库存：扣减（标记预占）
  4. Try 优惠券：标记使用

  全部 Try 成功 → Confirm 全提交
  任一失败 → Cancel 全回滚

📌 6 个参与者，全部要写 TCC 接口
   工程量很大，但性能高
```

### 6.2 银行转账

```
跨行转账场景：
  A 行 → B 行
  - A 行 Try：冻结 A 账户 100
  - B 行 Try：标记 B 账户 +100
  - 双方 Confirm：A 扣 100，B 加 100
  - 任一失败 → 双方 Cancel

📌 实时性要求不高时用 Saga
   实时性要求高时用 TCC
```

## 7. 何时用 TCC？

```
✅ 适合：
  - 业务能拆 Try / Confirm / Cancel
  - 高并发（不能用 2PC 锁）
  - 强一致（不能用 Saga 最终一致）

❌ 不适合：
  - 业务接口不能改（用 Saga 异步补偿）
  - 简单业务（用本地事务 + MQ 异步）
  - 实时性不强（用 Saga）
```

## 8. 一句话总结

```
📌 TCC = Try（预留）+ Confirm（提交）+ Cancel（回滚），三段业务代码
📌 优势：性能高（无锁）、可控制（业务自己写）
📌 劣势：代码侵入大（每个分支 3 个方法）、要解决空回滚/幂等/防悬挂
📌 框架：Seata（主流）/ Hmily（零侵入）/ ByteTCC
📌 与 2PC 区别：TCC 是业务层，2PC 是 DB 层
📌 与 Saga 区别：TCC 是同步强一致，Saga 是异步最终一致
📌 适用：高并发、强一致业务（转账 / 支付 / 抢单）
```

## 9. 参考资料

- "Life beyond Distributed Transactions" (Pat Helland, 2007)
- Seata TCC 模式官方文档
- Hmily 分布式事务框架
- "Patterns of Distributed Systems" (Unmesh Joshi)
- 阿里 Seata 演进史
