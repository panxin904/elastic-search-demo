---
title: Seata 分布式事务
date: 2026-08-15  # date-auto-injected
---
# Seata
- AT mode: auto, undo_log table for rollback, global lock
- TCC mode: Try/Confirm/Cancel, manual implementation
- Saga mode: forward + backward compensation
```java
@GlobalTransactional
public void transfer(String from, String to, BigDecimal amount) {
  accountService.debit(from, amount);
  accountService.credit(to, amount);
}
```