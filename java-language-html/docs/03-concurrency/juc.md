---
title: JUC 工具
---
# JUC 工具
- CountDownLatch: wait for N tasks to complete
- CyclicBarrier: N threads wait for each other at barrier
- Semaphore: permits counter, acquire/release
- Phaser: flexible barrier for phases
- Exchanger: two threads swap data
```java
var latch = new CountDownLatch(3);
for (int i = 0; i < 3; i++)
  new Thread(() -> { doWork(); latch.countDown(); }).start();
latch.await();  // wait all 3 done
```