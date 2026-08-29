---
title: ForkJoinPool
date: 2026-08-15  # date-auto-injected
---
# ForkJoinPool 工作窃取

## 1. 核心思想

**分治（divide and conquer）+ 工作窃取（work-stealing）**：

```
        task (100万条数据)
            ↓ fork
        ┌───┴───┐
      subtask subtask ... subtask
        ↓ join
      result（合并）
```

- **每个线程有自己 deque**（双端队列）
- **空闲线程从别人的 deque 尾部偷任务**（work-stealing）
- **自己的 deque LIFO（FILO）** 拿最新任务（hot cache）

## 2. 三大优势

1. **充分利用多核**：递归拆任务并行
2. **负载均衡**：自动从繁忙线程偷任务
3. **减少线程切换**：每个线程独立 deque

## 3. 实战

```java
ForkJoinPool pool = new ForkJoinPool(Runtime.availableProcessors());
Long sum = pool.invoke(new SumTask(arr, 0, arr.length));

class SumTask extends RecursiveTask<Long> {
  int lo, hi;
  SumTask(int lo, int hi) { this.lo = lo; this.hi = hi; }
  protected Long compute() {
    if (hi - lo < 1000) return seqSum();
    int mid = (lo + hi) >>> 1;
    SumTask left = new SumTask(lo, mid);
    SumTask right = new SumTask(mid, hi);
    left.fork();              // 异步执行
    return right.compute() + left.join();  // 阻塞拿左结果
  }
}
```

## 4. 适用 vs 不适用

✅ **适用**：可分解 + 各子任务独立 + 合并结果有定义
  - 并行排序 / 归并
  - 大数据 map-reduce
  - 矩阵运算
  - 树遍历 / 图算法

❌ **不适用**：任务小（< 1ms，fork 成本高于收益）+ 强依赖链

## 5. 与 ExecutorService 区别

| | ThreadPoolExecutor | ForkJoinPool |
|--|---------------------|---------------|
| 任务类型 | 独立任务 | 递归/分治任务 |
| 队列 | 共享 BlockingQueue | 每线程独立 deque |
| 调度 | FIFO | LIFO + work-stealing |
| 阻塞 | 工作线程阻塞 | 父 join 阻塞子任务 |

## 6. 常见应用

- `Arrays.parallelSort()`：并行归并排序
- `parallelStream()`：底层用 common ForkJoinPool
- `CompletableFuture`：forkJoinPool 调度
- CompletableFuture 编排 DAG：fork 出去的子任务在公共池里执行

## 7. 公共池

```java
ForkJoinPool.commonPool()  // 全局单例，处理 parallelStream
// 大小 = availableProcessors() - 1
// 默认异步异常处理 = 打印到 stderr
```

## 🔗 下一步
- [ThreadPoolExecutor](/02-thread-pool/executor)
- [JDK 21 虚拟线程](/02-thread-pool/virtual)
- [CompletableFuture](/02-thread-pool/executor)
