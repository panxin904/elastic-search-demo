---
title: 声明式事务
---
# @Transactional
- Propagation: REQUIRED (default), REQUIRES_NEW, NESTED
- Isolation: DEFAULT, READ_COMMITTED, REPEATABLE_READ, SERIALIZABLE
- rollbackFor: default only RuntimeException, add Exception.class for checked
- Self-invocation bypasses proxy: call through ApplicationContext.getBean() or @Autowired self
```java
@Service
public class OrderService {
  @Transactional(rollbackFor = Exception.class)
  public void place(Order order) {
    orderRepo.save(order);
    inventoryRepo.deduct(order.getItems());
  }
}
```