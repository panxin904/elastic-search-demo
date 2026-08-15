---
title: TCC 模式
---
# TCC（Try-Confirm-Cancel）

## 1. 核心思想

TCC = **Try + Confirm + Cancel** 三阶段，把 2PC 的数据库层 prepare/commit 提到业务层。

```
     Try            Confirm         Cancel
      │                │                │
  预留资源         真正执行业务     释放预留资源
  (冻结库存)       (扣款 + 加款)   (解冻库存)
```

## 2. 转账例子

### Try 阶段

```
A 服务：
  1. 余额充足检查 → 通过
  2. 冻结金额 100 元（写入 freeze 表）
  3. 返回 "try ok"

B 服务：
  1. 余额充足检查 → 通过
  2. 冻结金额 100 元
  3. 返回 "try ok"
```

### Confirm 阶段

协调者收到 A / B 都 "try ok" → 调 A / B 的 confirm

```
A.confirm: 把 freeze 表的 100 元 → 实际扣款
B.confirm: 把 freeze 表的 100 元 → 实际加款
```

### Cancel 阶段

任何 try 失败 → 调 A / B 的 cancel

```
A.cancel: 删 freeze 表的 100 元
B.cancel: 删 freeze 表的 100 元
```

## 3. TCC 关键点

### Try 阶段：预留资源

不是直接扣款，是"冻结" → 失败时可逆。

### Confirm 必须能幂等

confirm 可能因网络重试 → 必须幂等（用业务 ID 去重）。

### Cancel 必须能幂等

同样原因，cancel 重试也要幂等。

### 隔离性

TCC 不保证全局 ACID 隔离，但保证最终一致。

## 4. 实战：阿里 TCC 框架

```xml
<dependency>
  <groupId>org.springframework.cloud</groupId>
  <artifactId>spring-cloud-alibaba-seata</artifactId>
</dependency>
```

```java
@LocalTCC
public interface TransferService {
  @TwoPhaseBusinessAction(name = "transfer", commitMethod = "confirm", rollbackMethod = "cancel")
  boolean tryTransfer(TransferDTO dto);

  boolean confirm(TransferDTO dto);

  boolean cancel(TransferDTO dto);
}

@Service
public class TransferServiceImpl implements TransferService {
  @Autowired AccountMapper accountMapper;

  public boolean tryTransfer(TransferDTO dto) {
    // Try: 冻结金额
    accountMapper.freeze(dto.getFrom(), dto.getAmount());
    return true;
  }
  public boolean confirm(TransferDTO dto) {
    // Confirm: 真正扣款 + 加款
    accountMapper.confirmTransfer(dto.getFrom(), dto.getTo(), dto.getAmount());
    return true;
  }
  public boolean cancel(TransferDTO dto) {
    // Cancel: 解冻
    accountMapper.unfreeze(dto.getFrom(), dto.getAmount());
    return true;
  }
}
```

## 5. Seata TCC 模式

Seata（阿里）将 TCC 标准化为框架：
- `@TwoPhaseBusinessAction` 注解
- 自动调用 confirm / cancel
- 异常时自动 cancel
- 与 AT 模式可混用

## 6. TCC vs 2PC

| | 2PC | TCC |
|--|-----|-----|
| 在哪层 | 数据库 | 业务 |
| 阻塞 | 全程锁 | 只在 Try 阶段锁 |
| 协调者 | DB | 业务 / Seata |
| 性能 | 差 | 中 |
| 适用 | 单机多库 | 微服务强一致 |
| 隔离性 | 强 | 弱（取决于业务） |

## 7. TCC 适用 vs 不适用

✅ **适用**：
- 转账 / 支付（强一致 + 性能）
- 库存冻结（电商秒杀）
- 票务预订（强一致）

❌ **不适用**：
- 高并发写（每单都要 Try 锁资源）
- 业务状态机复杂（写 Try 接口难）
- 长事务（TCC Try 阶段同步阻塞）

## 8. TCC 最佳实践

1. **Try 阶段必须幂等**：用 biz_id 去重
2. **Confirm 必须成功**：失败则人工介入
3. **超时自动 cancel**：防止悬挂
4. **幂等 + 监控 + 告警**：必备
5. **空回滚**：cancel 不需要补偿（因为 Try 没真做）

## 9. TCC vs Saga

| | TCC | Saga |
|--|-----|------|
| 一致性 | 强 | 弱（最终） |
| Try 锁 | 是 | 否 |
| 适用 | 短事务 | 长事务 / 多服务 |
| 实现复杂度 | 高 | 中 |

**选型**：短事务 → TCC；长事务 / 多服务 → Saga。

## 🔗 下一步
- [2PC / 3PC](/07-distributed-tx/2pc)
- [Saga 模式](/07-distributed-tx/saga)
- [本地消息表](/07-distributed-tx/local-table)
