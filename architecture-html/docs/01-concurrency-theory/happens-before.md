---
title: happens-before
date: 2026-08-15  # date-auto-injected
---
# happens-before 原则

## 1. 核心问题

**没有 happens-before 关系，JVM 可任意重排序，前一个线程的写对后一个线程不可见。**

happens-before 是 JMM 的**核心概念**：A happens-before B 表示 A 的结果对 B 可见。

## 2. 8 大天然 happens-before 规则

1. **程序顺序规则**：同线程内，按代码顺序，前面的操作 happens-before 后面。
2. **volatile 规则**：volatile 写 happens-before 后续 volatile 读。
3. **传递性**：A hb B，B hb C → A hb C。
4. **start() 规则**：Thread.start() 之前 happens-before 该线程的每个动作。
5. **join() 规则**：线程所有动作 happens-before 其他线程 join() 返回。
6. **中断规则**：interrupt() happens-before 被中断线程检测到中断。
7. **终结规则**：构造器结束 happens-before finalize()。
8. **monitor 规则**：unlock happens-before 后续同一 monitor 的 lock。

## 3. 一个反例

```java
// Thread 1
context.start();
doWork();  // 写共享变量

// Thread 2
while (!ready) ;  // 死循环
use(sharedVar);   // 可能看不到 doWork 的写！
```

**为什么？** Thread 2 与 Thread 1 没有 happens-before 关系（除非用 volatile/join/lock）。

## 4. happens-before 与可见性

| 关系 | 可见？ |
|------|--------|
| 同一线程内顺序 | ✅ |
| synchronized 块退出 → 下个 synchronized 块进入 | ✅ |
| volatile 写 → 后续 volatile 读 | ✅ |
| Thread.start() → 子线程操作 | ✅ |
| Thread.join() 返回 → 主线程后续操作 | ✅ |
| 无任何同步 | ❌ 可能看不到 |

## 5. 实战原则

```java
// 1. 读最新值：用 volatile 或 Atomic* 或锁
private volatile boolean ready = false;

// 2. 跨线程传递：用 join、Future、Exchanger、CyclicBarrier

// 3. 写后读：必须有 happens-before（synchronized、volatile、Atomic、Lock、ConcurrentHashMap）
```

## 🔗 下一步
- [JMM 内存模型](/01-concurrency-theory/jmm)
- [volatile / final](/01-concurrency-theory/volatile)
- [CAS / Lock-Free](/01-concurrency-theory/cas)
