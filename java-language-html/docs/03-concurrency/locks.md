---
title: synchronized / AQS
date: 2026-08-15  # date-auto-injected
---
# synchronized / AQS
- synchronized upgrades: biased → lightweight → heavyweight (irreversible)
- ReentrantLock: tryLock(timeout), lockInterruptibly, fair mode
- AQS (AbstractQueuedSynchronizer): CLH queue, CAS state, template pattern
- StampedLock: optimistic read (no lock), tryOptimisticRead → validate
```java
var lock = new ReentrantLock();
lock.lock();
try { /* critical section */ }
finally { lock.unlock(); }

synchronized (obj) { /* JVM monitors */ }
```