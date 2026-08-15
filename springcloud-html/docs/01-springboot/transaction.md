---
title: 事务管理
---

# 🔄 Spring Boot 事务管理

> 理解 `@Transactional` 的传播机制、隔离级别、回滚规则，是处理并发数据问题的关键。

## 🎯 基础事务

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private InventoryService inventoryService;
    
    @Transactional  // 🎯 开启事务
    public boolean createOrder(OrderDTO dto) {
        // 1. 写订单
        orderMapper.insert(dto);
        
        // 2. 扣库存
        inventoryService.decrease(dto);
        
        // 3. 异常自动回滚
        return true;
    }
}
```

## 📊 7 种传播行为

```java
@Transactional(propagation = Propagation.REQUIRED)  // 默认
public void method() { ... }
```

| 传播行为 | 说明 |
|---|---|
| **REQUIRED**（默认） | 存在事务则加入，不存在则新建 |
| SUPPORTS | 存在事务则加入，不存在则非事务执行 |
| MANDATORY | 必须在事务中调用，否则抛异常 |
| REQUIRES_NEW | 总是新建事务，挂起当前事务 |
| NOT_SUPPORTED | 非事务执行，挂起当前事务 |
| NEVER | 非事务执行，存事务则抛异常 |
| NESTED | 嵌套事务（外层回滚 → 全回滚；内层回滚 → 仅内层） |

### 实战场景

```java
@Service
public class OrderService {
    
    // 场景 1：日志必须记录（即使主业务失败）
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void logOperation(String action) {
        logMapper.insert(new Log(action));  // 独立事务
    }
    
    public void createOrder(OrderDTO dto) {
        try {
            // 主业务（REQUIRED）
            doCreateOrder(dto);
        } catch (Exception e) {
            // 记录失败日志（独立事务，不受主业务回滚影响）
            logOperation("create_order_failed");
        }
    }
    
    // 场景 2：批量操作，每批独立
    public void batchProcess(List<Order> orders) {
        for (Order order : orders) {
            processOne(order);  // 每次独立事务
        }
    }
    
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void processOne(Order order) {
        orderMapper.insert(order);
    }
}
```

## 🔒 4 种隔离级别

```java
@Transactional(isolation = Isolation.READ_COMMITTED)
public void method() { ... }
```

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---|---|---|---|---|
| READ_UNCOMMITTED | ✅ | ✅ | ✅ | 最高 |
| **READ_COMMITTED**（Oracle 默认） | ❌ | ✅ | ✅ | 高 |
| **REPEATABLE_READ**（MySQL 默认） | ❌ | ❌ | ✅ | 中 |
| SERIALIZABLE | ❌ | ❌ | ❌ | 低 |

### MySQL InnoDB 的特殊点

```sql
-- MySQL 默认是 REPEATABLE READ
-- 但 InnoDB 通过 MVCC + next-key lock 解决了大部分幻读

-- 查看当前隔离级别
SELECT @@transaction_isolation;
```

## ⚠️ @Transactional 失效场景（最常踩的坑）

### 坑 1：同类方法调用（最常见！）

```java
@Service
public class OrderService {
    
    public void createOrder(OrderDTO dto) {
        // ❌ 直接调用同类方法，事务不生效！
        this.saveOrder(dto);  // 绕过代理，@Transactional 失效
    }
    
    @Transactional
    public void saveOrder(OrderDTO dto) {
        orderMapper.insert(dto);
    }
}
```

**解决：**
```java
// ✅ 方案 1：注入自己（通过 Spring 代理）
@Service
public class OrderService {
    
    @Autowired
    @Lazy  // 解决循环依赖
    private OrderService self;
    
    public void createOrder(OrderDTO dto) {
        self.saveOrder(dto);  // 通过代理调用，事务生效
    }
    
    @Transactional
    public void saveOrder(OrderDTO dto) {
        orderMapper.insert(dto);
    }
}

// ✅ 方案 2：拆到两个 Service
@Service
public class OrderService {
    @Autowired
    private OrderInternalService internal;
    
    public void createOrder(OrderDTO dto) {
        internal.saveOrder(dto);
    }
}

@Service
public class OrderInternalService {
    @Transactional
    public void saveOrder(OrderDTO dto) {
        // ...
    }
}
```

### 坑 2：私有方法

```java
@Service
public class OrderService {
    
    public void createOrder(OrderDTO dto) {
        // ❌ 私有方法调用，事务不生效
        save(dto);
    }
    
    @Transactional
    private void save(OrderDTO dto) {  // ❌ private 方法
        orderMapper.insert(dto);
    }
}
```

### 坑 3：异常被 try-catch 吃掉

```java
@Transactional
public void createOrder(OrderDTO dto) {
    try {
        orderMapper.insert(dto);
        inventoryService.decrease(dto);  // 抛异常
    } catch (Exception e) {
        // ❌ 异常被 catch，事务不会回滚！
        log.error("失败", e);
    }
}
```

**解决：**
```java
// 方案 1：抛出异常
@Transactional
public void createOrder(OrderDTO dto) {
    try {
        orderMapper.insert(dto);
        inventoryService.decrease(dto);
    } catch (Exception e) {
        log.error("失败", e);
        throw e;  // 重新抛出
    }
}

// 方案 2：手动回滚
@Transactional
public void createOrder(OrderDTO dto) {
    try {
        orderMapper.insert(dto);
    } catch (Exception e) {
        TransactionAspectSupport.currentTransactionStatus()
            .setRollbackOnly();  // 手动回滚
        log.error("失败", e);
    }
}
```

### 坑 4：rollbackFor 默认只回滚 RuntimeException

```java
@Transactional  // 默认只回滚 RuntimeException
public void createOrder() throws Exception {
    orderMapper.insert(dto);
    throw new Exception("IO 错误");  // ❌ checked 异常不回滚！
}
```

**解决：**
```java
@Transactional(rollbackFor = Exception.class)  // 任何异常都回滚
public void createOrder() throws Exception {
    orderMapper.insert(dto);
    throw new Exception("IO 错误");  // ✅ 回滚
}
```

### 坑 5：跨线程调用

```java
@Transactional
public void createOrder() {
    orderMapper.insert(dto);
    
    new Thread(() -> {
        // ❌ 异步线程，不在事务中
        orderMapper.update(dto);
    }).start();
}
```

## 🔧 编程式事务（高级）

```java
@Service
public class OrderService {
    
    @Autowired
    private TransactionTemplate transactionTemplate;
    
    public void createOrder(OrderDTO dto) {
        // 编程式事务
        transactionTemplate.execute(status -> {
            orderMapper.insert(dto);
            inventoryService.decrease(dto);
            return true;
        });
    }
}
```

## 📊 事务传播实战

```java
@Service
public class OrderService {
    
    @Autowired
    private InventoryService inventoryService;
    
    @Autowired
    private AccountService accountService;
    
    @Transactional(propagation = Propagation.REQUIRED)
    public void createOrder(OrderDTO dto) {
        // 主事务
        orderMapper.insert(dto);
        
        // 加入主事务（REQUIRED）
        inventoryService.decrease(dto);
        
        // 新建独立事务（REQUIRES_NEW）
        accountService.debit(dto);
        // 即使这里失败，主事务也不会回滚
    }
}

@Service
public class AccountService {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void debit(OrderDTO dto) {
        accountMapper.debit(dto.getUserId(), dto.getAmount());
    }
}
```

## 🔍 事务调试

```yaml
# 开启事务调试日志
logging:
  level:
    org.springframework.transaction: DEBUG
    org.springframework.jdbc.datasource.DataSourceTransactionManager: DEBUG
```

输出可以看到：
- 事务开始
- 事务提交 / 回滚
- 隔离级别

## 🎯 总结

**事务核心：**
- ✅ `@Transactional` 默认 `REQUIRED` 传播
- ✅ 默认只回滚 `RuntimeException`
- ✅ 必须通过 Spring 代理调用（同类方法调用失效）

**7 种传播行为：**
- 常用：`REQUIRED`（默认）、`REQUIRES_NEW`（独立）、`NESTED`（嵌套）

**4 种隔离级别：**
- MySQL 默认：`REPEATABLE READ`
- 推荐：`READ COMMITTED`（性能好）

**失效场景：**
- ❌ 同类方法调用
- ❌ private 方法
- ❌ 异常被 catch 吃掉
- ❌ checked exception 默认不回滚
- ❌ 跨线程调用

**下一步：** [📚 Spring Cloud Alibaba 总览](/02-overview/intro) — 微服务生态与版本对应