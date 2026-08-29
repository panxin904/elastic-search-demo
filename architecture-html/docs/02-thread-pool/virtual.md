---
title: JDK 21 虚拟线程
date: 2026-08-15  # date-auto-injected
---
# JDK 21 虚拟线程（Virtual Threads / Loom）

## 1. 解决什么问题

**平台线程 = OS 线程，1:1 映射**，每线程约 1MB 栈。
**虚拟线程 = JVM 线程**，约 1KB 栈，**百万级**并发。

```
平台线程 1:1 OS 线程：
  - 创建/上下文切换昂贵
  - 阻塞 I/O 时 OS 线程空转
  - 1000 并发 = 1GB+ 内存

虚拟线程（协程+M:N 调度）：
  - 创建快（数 ns）
  - 阻塞 I/O 时挂起，不占 OS 线程
  - 100 万并发 ≈ 100MB 内存
```

## 2. 三大优势

1. **高吞吐**：单进程支持百万级并发连接
2. **简化代码**：无需回调 / Future / ReactiveX
3. **兼容现有 API**：所有 `synchronized` / `BlockingQueue` / JDBC / NIO **无需修改**

## 3. 实战

```java
// 方式 1：直接启动
Thread.startVirtualThread(() -> {
  System.out.println("virtual");
});

// 方式 2：ExecutorService（推荐长任务）
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
  for (int i = 0; i < 100_000; i++) {
    executor.submit(() -> callRemote(i));
  }
}  // 自动关闭 + 等待

// 方式 3：ThreadFactory 给现有 ExecutorService
var factory = Thread.ofVirtual().name("worker-").factory();
var executor = Executors.newFixedThreadPool(100, factory);
```

## 4. 关键机制

- **M:N 调度**：100 万虚拟线程 → N 个 OS 线程（carrier thread）
- **M:N 调度器**：`ForkJoinPool`（默认 1-1 映射时）→ JDK 21+ `Thread.ofVirtual()`
- **挂起（mount）/ 恢复（unmount）**：阻塞 I/O 时挂起，不占 OS 线程

## 5. pinning 问题

`synchronized` 块 + JNI 调用会**pin** 到 carrier thread（避免 OS 线程切换出问题）：

```java
// 解决：拆分同步块
synchronized (lock) { counter++; }  // 整块 pin
// 改为：
int v = counter.incrementAndGet();  // AtomicInteger 不 pin
synchronized (lock) { /* do other */ }
```

## 6. 与 reactive 框架对比

| | 虚拟线程 | Reactive（Reactor/Project Reactor） |
|--|----------|--------------------------------------|
| 编程模型 | 命令式 / 阻塞写法 | 响应式 / 链式 / Mono Flux |
| 学习曲线 | 低 | 高（操作符 + 背压） |
| 性能 | 等同 / 略胜 | 同等 |
| 调试 | 简单 | 难（堆栈深） |
| 现有代码 | 0 改动 | 需重写 |

**推荐**：新项目用虚拟线程；老阻塞 API 直接受益。

## 7. 限制

- 不适合 CPU 密集任务（无加速）
- synchronized 块要短（pinning）
- JNI 兼容性需测试

## 8. 实战：HTTP 服务

```java
// 之前：1000 并发连接 → 1000 个 OS 线程 → 1GB 内存
var server = HttpServer.create(new InetSocketAddress(8080), backlog);
// 之后：100 万虚拟线程，每请求一个虚拟线程
var executor = Executors.newVirtualThreadPerTaskExecutor();
server.setExecutor(executor);
server.createContext("/api", new Handler());
server.start();
```

## 🔗 下一步
- [ThreadPoolExecutor](/02-thread-pool/executor)
- [ForkJoinPool](/02-thread-pool/forkjoin)
