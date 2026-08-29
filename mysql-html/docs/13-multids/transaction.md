---
title: 分布式事务
date: 2026-08-15  # date-auto-injected
---

# 🔄 分布式事务

> 当业务涉及**多个数据源**或**多个服务**时，传统单库事务（ACID）无法保证一致性。分布式事务是微服务架构的核心难题之一。

## 🎯 为什么需要分布式事务？

```
传统单库事务：
- BEGIN
- UPDATE accounts SET balance = balance - 100 WHERE id = 1  # 扣款
- UPDATE accounts SET balance = balance + 100 WHERE id = 2  # 加款
- COMMIT
# ✅ 原子性：要么都成功，要么都失败

跨库 / 跨服务场景：
- 订单服务：写 orders 库
- 库存服务：扣减 inventory 库
- 账户服务：扣款 accounts 库
# ❌ 单库事务无法保证多库一致性！
```

## 📊 4 种解决方案对比

| 方案 | 一致性 | 性能 | 复杂度 | 适用场景 |
|---|---|---|---|---|
| 2PC（两阶段提交） | 强一致 | 差 | 中 | 数据库支持时 |
| 3PC（三阶段提交） | 强一致 | 差 | 高 | 理论，很少用 |
| **TCC** | 最终一致 | 好 | 高 | 金融、电商 |
| **Saga** | 最终一致 | 好 | 中 | 长事务、跨服务 |
| **本地消息表** | 最终一致 | 好 | 中 | 异步场景 |
| **Seata（阿里）** | 强/最终一致 | 好 | 低 | **推荐** |
| **最大努力通知** | 弱一致 | 最好 | 低 | 通知场景 |

## 🚀 方案 1：Seata（强烈推荐）

### Seata 是什么？

```
Seata = Simple Extensible Autonomous Transaction Architecture
阿里开源的分布式事务解决方案
```

```
Seata 三大角色：
┌──────────────────────────────────────┐
│  TC (Transaction Coordinator) 事务协调器 │
│  - 全局事务管理                          │
│  - 协调各分支事务的提交 / 回滚            │
└──────────────────────────────────────┘
              ↑
    ┌─────────┼─────────┐
    │         │         │
┌───▼──┐  ┌──▼───┐  ┌──▼───┐
│ RM 1 │  │ RM 2 │  │ RM 3 │  ← Resource Manager（各微服务）
└──────┘  └──────┘  └──────┘
   订单       库存      账户
```

### 1. 部署 Seata Server

```bash
# 下载
wget https://github.com/seata/seata/releases/download/v1.7.0/seata-server-1.7.0.zip
unzip seata-server-1.7.0.zip

# 启动
cd seata/bin
./seata-server.sh -p 8091 -m file
```

### 2. 微服务集成 Seata

```xml
<dependency>
    <groupId>io.seata</groupId>
    <artifactId>seata-spring-boot-starter</artifactId>
    <version>1.7.0</version>
</dependency>
```

```yaml
seata:
  application-id: order-service
  tx-service-group: my_tx_group
  registry:
    type: file
    file:
      name: file.conf
  config:
    type: file
    file:
      name: file.conf
```

### 3. Seata 三种模式

#### AT 模式（推荐，零侵入）

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private InventoryClient inventoryClient;  // 远程调用库存服务
    
    @Autowired
    private AccountClient accountClient;  // 远程调用账户服务
    
    @GlobalTransactional  // ✅ Seata 关键注解
    public boolean createOrder(OrderDTO dto) {
        // 1. 创建订单（写本服务库）
        orderMapper.insert(dto);
        
        // 2. 扣减库存（远程调用）
        inventoryClient.decrease(dto.getProductId(), dto.getQuantity());
        
        // 3. 扣款（远程调用）
        accountClient.debit(dto.getUserId(), dto.getAmount());
        
        return true;
        // ✅ 任何一个失败，Seata 自动回滚所有分支
    }
}
```

**AT 模式原理：**
- TC 给每个分支事务生成 undo log
- 任何分支失败 → TC 通知所有分支执行 undo log
- 自动保证一致性

#### TCC 模式（高性能）

```java
@LocalTCC
public interface OrderTccService {
    
    @TwoPhaseBusinessAction(
        name = "createOrder",
        commitMethod = "commit",
        rollbackMethod = "rollback"
    )
    boolean tryCreate(OrderDTO dto);
    
    boolean commit(BusinessActionContext context);
    
    boolean rollback(BusinessActionContext context);
}

@Service
public class OrderTccServiceImpl implements OrderTccService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    public boolean tryCreate(OrderDTO dto) {
        // 1. Try：预占资源
        orderMapper.insertPending(dto);
        return true;
    }
    
    public boolean commit(BusinessActionContext context) {
        // 2. Confirm：确认
        orderMapper.confirmPending(...);
        return true;
    }
    
    public boolean rollback(BusinessActionContext context) {
        // 3. Cancel：取消
        orderMapper.cancelPending(...);
        return true;
    }
}
```

**TCC 三个阶段：**
- **Try**：预占资源（不真正扣款，只冻结）
- **Confirm**：确认（真正扣款）
- **Cancel**：取消（解冻资源）

#### Saga 模式（长事务）

```java
@SagaStart  // Saga 起点
public void createOrderSaga(OrderDTO dto) {
    // 步骤 1：创建订单
    orderMapper.insert(dto);
    
    // 步骤 2：扣库存（带补偿）
    decreaseInventorySaga(dto);
    
    // 步骤 3：扣款（带补偿）
    debitAccountSaga(dto);
}

@Compensable  // 补偿方法
public void decreaseInventorySaga(OrderDTO dto) {
    try {
        inventoryClient.decrease(dto);
    } catch (Exception e) {
        // 自动触发补偿
        inventoryClient.rollback(dto);
    }
}
```

## 🚀 方案 2：本地消息表（最终一致性）

### 原理

```
1. 业务操作 + 消息插入 在同一个数据库事务里
2. 后台任务扫描消息表
3. 发送消息到 MQ
4. 消费者处理业务

✅ 不用 Seata
✅ 适合异步场景
⚠️ 有少量延迟
```

### 实现

```sql
-- 本地消息表
CREATE TABLE local_message (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  topic VARCHAR(100),
  content TEXT,
  status TINYINT,  -- 0=待发送 1=已发送 2=失败
  retry_count INT DEFAULT 0,
  created_at DATETIME,
  sent_at DATETIME
);
```

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private LocalMessageMapper messageMapper;
    
    @Transactional
    public boolean createOrder(Order order) {
        // 1. 业务操作
        orderMapper.insert(order);
        
        // 2. 写本地消息（同事务）
        LocalMessage msg = new LocalMessage();
        msg.setTopic("inventory.decrease");
        msg.setContent(JSON.toJSONString(order));
        msg.setStatus(0);
        messageMapper.insert(msg);
        
        return true;
    }
}

// 后台任务：扫描并发送
@Scheduled(fixedRate = 5000)
public void scanMessages() {
    List<LocalMessage> msgs = messageMapper.selectList(
        Wrappers.<LocalMessage>lambdaQuery()
            .eq(LocalMessage::getStatus, 0)
            .lt(LocalMessage::getRetryCount, 5)
            .last("LIMIT 100")
    );
    
    for (LocalMessage msg : msgs) {
        try {
            // 发送到 MQ
            mqProducer.send(msg.getTopic(), msg.getContent());
            
            // 标记已发送
            msg.setStatus(1);
            msg.setSentAt(new Date());
            messageMapper.updateById(msg);
        } catch (Exception e) {
            msg.setRetryCount(msg.getRetryCount() + 1);
            messageMapper.updateById(msg);
        }
    }
}
```

## 🚀 方案 3：TCC（Try-Confirm-Cancel）

### 适用场景

```
✅ 强一致性要求（金融、支付）
✅ 性能要求高
✅ 业务相对简单
```

### 完整示例

```java
@LocalTCC
public interface InventoryTccService {
    
    @TwoPhaseBusinessAction(
        name = "decreaseInventory",
        commitMethod = "commit",
        rollbackMethod = "rollback"
    )
    boolean tryDecrease(@BusinessActionContextParameter("productId") Long productId,
                        @BusinessActionContextParameter("quantity") Integer quantity);
    
    boolean commit(BusinessActionContext context);
    
    boolean rollback(BusinessActionContext context);
}

@Service
@Slf4j
public class InventoryTccServiceImpl implements InventoryTccService {
    
    @Autowired
    private InventoryMapper inventoryMapper;
    
    @Autowired
    private InventoryFreezeMapper freezeMapper;
    
    @Override
    public boolean tryDecrease(Long productId, Integer quantity) {
        // Try：冻结库存（不真正扣减）
        InventoryFreeze freeze = new InventoryFreeze();
        freeze.setProductId(productId);
        freeze.setQuantity(quantity);
        freeze.setStatus(0);  // 0=冻结
        freezeMapper.insert(freeze);
        return true;
    }
    
    @Override
    public boolean commit(BusinessActionContext context) {
        // Confirm：真正扣减库存
        Long productId = (Long) context.getActionContext("productId");
        Integer quantity = (Integer) context.getActionContext("quantity");
        
        inventoryMapper.decrease(productId, quantity);
        return true;
    }
    
    @Override
    public boolean rollback(BusinessActionContext context) {
        // Cancel：解冻库存
        // 删除冻结记录即可
        return freezeMapper.deleteByBusinessId(
            context.getXid(), "decreaseInventory"
        ) > 0;
    }
}
```

### TCC 实战注意事项

```java
// ⚠️ Try 阶段必须保证幂等性
// 因为网络可能重试 Try 请求

@Override
public boolean tryDecrease(Long productId, Integer quantity) {
    // 1. 检查是否已经 Try 过（幂等性）
    String xid = RootContext.getXID();
    InventoryFreeze freeze = freezeMapper.selectByXidAndBiz(xid, ...);
    if (freeze != null) {
        return true;  // 已 Try 过，直接返回成功
    }
    
    // 2. 真正的 Try 逻辑
    // ...
}

// ⚠️ Confirm / Cancel 也要保证幂等性
```

## 🚀 方案 4：最大努力通知

### 适用场景

```
- 通知类业务（短信、邮件、推送）
- 对最终一致性要求高
- 允许少量丢失
```

### 实现

```java
@Service
public class NotificationService {
    
    @Autowired
    private NotificationMapper notificationMapper;
    
    // 1. 写消息到本地表（业务事务内）
    @Transactional
    public void onOrderPaid(Order order) {
        // 业务逻辑...
        
        // 写消息
        Notification msg = new Notification();
        msg.setType("order_paid");
        msg.setContent(JSON.toJSONString(order));
        msg.setStatus(0);
        notificationMapper.insert(msg);
    }
    
    // 2. 定时任务发送
    @Scheduled(fixedRate = 60000)
    public void sendNotifications() {
        List<Notification> msgs = notificationMapper.selectList(
            Wrappers.<Notification>lambdaQuery()
                .eq(Notification::getStatus, 0)
                .last("LIMIT 100")
        );
        
        for (Notification msg : msgs) {
            try {
                sendToMQ(msg);
                msg.setStatus(1);
                notificationMapper.updateById(msg);
            } catch (Exception e) {
                msg.setRetryCount(msg.getRetryCount() + 1);
                if (msg.getRetryCount() >= 5) {
                    msg.setStatus(2);  // 标记失败
                }
                notificationMapper.updateById(msg);
            }
        }
    }
}
```

## 📊 方案选型

| 业务场景 | 推荐方案 | 理由 |
|---|---|---|
| 金融支付（强一致） | **Seata AT / TCC** | 强一致 |
| 电商订单（最终一致可接受） | **本地消息表 / Seata Saga** | 高性能 |
| 库存扣减（强一致） | **Seata AT / TCC** | 不能超卖 |
| 跨服务长事务 | **Seata Saga** | 适合长流程 |
| 简单通知 | **最大努力通知** | 实现简单 |
| 实时性要求高 | **Seata AT** | 性能好 |

## 🎯 实战：电商下单完整方案

### 业务流

```
1. 订单服务：创建订单（写 order_db）
2. 库存服务：扣减库存（写 inventory_db）
3. 账户服务：扣款（写 account_db）
4. 物流服务：创建物流单（写 logistics_db）
5. 通知服务：发短信（写 notification_db + MQ）
```

### Seata 方案

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private InventoryClient inventoryClient;
    
    @Autowired
    private AccountClient accountClient;
    
    @GlobalTransactional(name = "create-order", timeoutMills = 30000)
    public Order createOrder(OrderDTO dto) {
        // 1. 写本服务库（order_db）
        orderMapper.insert(dto);
        
        // 2. 远程调用库存（inventory_db）
        inventoryClient.tryDecrease(dto.getProductId(), dto.getQuantity());
        
        // 3. 远程调用账户（account_db）
        accountClient.tryDebit(dto.getUserId(), dto.getAmount());
        
        return dto;
        // ✅ 任何失败自动回滚
    }
}
```

### 注意事项

```java
// ⚠️ 1. 避免长事务（影响性能）
@GlobalTransactional(timeoutMills = 30000)  // 设置超时

// ⚠️ 2. 避免在事务内做远程调用阻塞
@GlobalTransactional
public void slowMethod() {
    orderMapper.insert(order);
    httpClient.post();  // ⚠️ 慢！
    Thread.sleep(5000);  // ⚠️ 更慢！
}

// ✅ 3. 幂等性（防止重复提交）
@GlobalTransactional
public boolean createOrder(OrderDTO dto) {
    // 用业务单号去重
    Order exist = orderMapper.selectByOrderNo(dto.getOrderNo());
    if (exist != null) return true;  // 已创建过
    return orderMapper.insert(dto) > 0;
}
```

## 🎯 总结

**分布式事务选型：**
- ✅ **简单 + 推荐**：Seata AT 模式
- ✅ **金融级**：TCC（业务需要改造）
- ✅ **长事务**：Saga
- ✅ **不想引入中间件**：本地消息表
- ✅ **通知类**：最大努力通知

**Seata 三种模式对比：**
- AT：零侵入，自动回滚
- TCC：性能高，需业务改造
- Saga：长事务，复杂业务

**关键原则：**
- ✅ 优先用 Seata（阿里出品，最成熟）
- ✅ 避免长事务
- ✅ 保证幂等性
- ✅ 设置超时
- ✅ 监控异常

**下一步：** [☕ 微服务数据库模式](/14-microservice/db-pattern) — 每个服务一个数据库的实践