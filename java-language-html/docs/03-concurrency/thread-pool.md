---
title: 线程 / 线程池
---
# 线程 / 线程池
- ThreadPoolExecutor params: corePoolSize, maxPoolSize, keepAliveTime, workQueue, threadFactory, rejectHandler
- 4 reject policies: AbortPolicy(default), CallerRunsPolicy, DiscardPolicy, DiscardOldestPolicy
- Executors factory: newFixedThreadPool, newCachedThreadPool, newSingleThreadExecutor
- ForkJoinPool: work-stealing, used by parallel streams and CompletableFuture
```java
var pool = new ThreadPoolExecutor(
  2, 4, 60, TimeUnit.SECONDS,
  new LinkedBlockingQueue<>(100),
  new ThreadPoolExecutor.CallerRunsPolicy()
);
pool.execute(() -> System.out.println("hi"));
pool.shutdown();
```