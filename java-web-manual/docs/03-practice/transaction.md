---
title: 事务管理
---

# 事务管理

事务保证一组数据库操作要么全部成功，要么全部回滚。

## @Transactional 使用

```java
@Service
public class OrderServiceImpl implements OrderService {

    @Transactional(rollbackFor = Exception.class)  // 任何异常都回滚
    public void createOrder(OrderCreateDTO dto) {
        // 1. 扣减库存
        productMapper.decreaseStock(dto.getProductId(), dto.getQuantity());
        // 2. 创建订单
        orderMapper.insert(order);
        // 3. 创建订单明细
        orderItemMapper.insertBatch(items);
        // 任何一步失败，前面操作全部回滚
    }
}
```

## 传播行为

| 传播行为 | 说明 |
|---|---|
| REQUIRED（默认） | 有事务则加入，无则新建 |
| REQUIRES_NEW | 总是新建事务，挂起当前事务 |
| NESTED | 嵌套事务，内层回滚不影响外层 |
| SUPPORTS | 有事务则加入，无则以非事务运行 |
| NOT_SUPPORTED | 以非事务运行，挂起当前事务 |

## 事务失效场景

<div class="kg-note kg-note-warning">
以下场景 @Transactional 会失效，需要特别注意！
</div>

```java
// 1. 方法非 public（最常见）
@Transactional
private void doSomething() {}  // ❌ 失效！必须是 public

// 2. 自调用（同类方法调用）
public void methodA() {
    this.methodB();  // ❌ methodB 上的 @Transactional 失效
}
// 解决：注入自己
@Autowired
private OrderService self;
self.methodB();  // ✅ 通过代理调用生效

// 3. 异常被 catch 吞掉
@Transactional
public void doSomething() {
    try { riskyOperation(); }
    catch (Exception e) { /* 吞了异常 */ }  // ❌ 不回滚
}

// 4. 非运行时异常（需要 rollbackFor）
@Transactional  // ❌ checked 异常不会回滚
@Transactional(rollbackFor = Exception.class)  // ✅ 所有异常都回滚
```

## 事务隔离级别

| 级别 | 解决的问题 | 并发性能 |
|---|---|---|
| READ_UNCOMMITTED | 无 | 最高 |
| READ_COMMITTED | 脏读 | 高 |
| REPEATABLE_READ（MySQL默认） | 脏读、不可重复读 | 中 |
| SERIALIZABLE | 全部（含幻读） | 最低 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="transaction" :height="400" />
