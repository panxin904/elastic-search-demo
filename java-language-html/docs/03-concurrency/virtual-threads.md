---
title: 虚拟线程 (Loom)
---
# 虚拟线程
- JDK 21: java.lang.VirtualThread, lightweight threads managed by JVM
- Platform thread: OS thread (1:1), expensive
- Virtual thread: JVM-managed, cheap (millions possible), works with synchronized (pinning)
- For IO-bound tasks, don't pool virtual threads
```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
  executor.submit(() -> { Thread.sleep(1000); return "done"; });
}
Thread.startVirtualThread(() -> System.out.println("virtual"));
```