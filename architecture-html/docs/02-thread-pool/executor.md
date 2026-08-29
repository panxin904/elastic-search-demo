---
title: ThreadPoolExecutor
date: 2026-08-15  # date-auto-injected
---
# ThreadPoolExecutor 原理

## 1. 为什么需要线程池

```
new Thread().start()  // 每次创建/销毁线程代价大
   频繁创建：内存 + CPU 抖动
   无限创建：OOM

线程池 = 预创建 + 复用 + 队列缓冲
```

**降低资源消耗 + 提高响应速度 + 提高线程可管理性**。

## 2. 七个核心参数

```java
new ThreadPoolExecutor(
  int corePoolSize,                    // 常驻线程数
  int maximumPoolSize,                 // 最大线程数
  long keepAliveTime,                  // 空闲存活时间
  TimeUnit unit,
  BlockingQueue<Runnable> workQueue,    // 任务队列
  ThreadFactory threadFactory,          // 线程创建
  RejectedExecutionHandler handler     // 拒绝策略
);
```

## 3. 任务处理流程（关键！）

```
提交任务
   ↓
1. 当前线程数 < corePoolSize？
   YES → 创建新线程执行
   NO  ↓
2. 任务入队（workQueue.offer）
   ↓
3. 队列未满？
   YES → 入队等待
   NO  ↓
4. 当前线程数 < maximumPoolSize？
   YES → 创建非核心线程（keepAliveTime 后回收）
   NO  ↓
5. 触发 RejectedExecutionHandler（拒绝）
```

## 4. 队列选择

| 队列 | 行为 | 适用 |
|------|------|------|
| `SynchronousQueue` | 不存储，直接 hand-off | 大池子 + 高吞吐 |
| `LinkedBlockingQueue` | 无界（Integer.MAX_VALUE） | 慎用：可能 OOM |
| `ArrayBlockingQueue` | 有界 | **推荐**（指定 capacity） |
| `PriorityBlockingQueue` | 带优先级 | 任务有优先级 |
| `SynchronousQueue` | 0 容量 | 必触发 maxPoolSize |

**坑**：`Executors.newFixedThreadPool` 内部用无界 LinkedBlockingQueue → 任务堆积 → OOM。

## 5. 四种拒绝策略

```java
ThreadPoolExecutor.AbortPolicy      // 默认，抛 RejectedExecutionException
ThreadPoolExecutor.CallerRunsPolicy // 调用者线程执行任务（降级）
ThreadPoolExecutor.DiscardPolicy    // 静默丢弃
ThreadPoolExecutor.DiscardOldestPolicy // 丢弃队列头 + 入队新任务
```

生产推荐 `CallerRunsPolicy`（保证不丢任务）。

## 6. 核心线程数配置

**CPU 密集型**：`corePoolSize = CPU 核数 + 1`
**IO 密集型**：`corePoolSize = 2 * CPU 核数`（线程经常在等 IO）
**混合型**：`corePoolSize = CPU 核数 * (1 + W/C)`，W=等待时间，C=计算时间

**公式来源**：Brian Goetz《Java Concurrency in Practice》。

## 7. 监控线程池

```java
ThreadPoolExecutor tp = (ThreadPoolExecutor) executor;
System.out.println("active: " + tp.getActiveCount());
System.out.println("queue: " + tp.getQueue().size());
System.out.println("coreSize: " + tp.getCorePoolSize());
```

**重要监控指标**：
- `tp_queue_size`：队列堆积（> 0 表示有积压）
- `tp_active_count`：活跃线程（接近 maxPoolSize 表示已饱和）

## 8. 实战：动态调参

```java
// 监控 + 调优
if (monitor.queueSize() > threshold) {
  tp.setCorePoolSize(newSize);  // 动态调整
  tp.setMaximumPoolSize(newMax);
}
```

## 9. ForkJoinPool 简述

分治算法：递归拆任务，子任务 fork() 异步执行，结果 join() 合并。**工作窃取**（work-stealing）：空闲线程从其他队列偷任务。

**使用场景**：并行流（parallelStream）、CompletableFuture、ForkJoinTask 递归。

## 🔗 下一步
- [JMM 内存模型](/01-concurrency-theory/jmm)
- [ForkJoinPool](/02-thread-pool/forkjoin)
- [JDK 21 虚拟线程](/02-thread-pool/virtual)
