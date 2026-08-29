---
title: CAS / Lock-Free
date: 2026-08-15  # date-auto-injected
---
# CAS 与无锁编程

## 1. CAS 定义

**Compare-And-Swap**（比较并交换），CPU 硬件原语：

```
CAS(V, E, N):
  if V == E:
    V = N
    return true
  else:
    return false
```

**乐观锁**：不断重试直到成功。

## 2. CAS 的三大问题

### ABA 问题

```
Thread 1: read A = 1, CAS(A, 1, 2)  准备写 2
Thread 2: A 1→2→1  （改了又改回）
Thread 1: CAS 成功！但 A 已经被中间状态污染
```

**解决**：版本号（AtomicStampedReference）或加锁。

### 自旋开销

高竞争下 CAS 反复失败 → CPU 空转。**解决**：自适应自旋 / Exponential Backoff / 让出 CPU。

### 单变量原子性

CAS 只能保护**一个**变量。多变量一致性需要**事务 / 锁**。

## 3. Java 中的 CAS 应用

| 类 | 实现 |
|----|------|
| `AtomicInteger` / `AtomicLong` | `compareAndSet(expect, update)` |
| `AtomicReference` | 引用原子操作 |
| `AtomicStampedReference` | 带版本号，**解决 ABA** |
| `AtomicIntegerArray` | 数组 CAS |
| `AtomicReferenceFieldUpdater` | 对象字段原子更新 |
| `LongAdder` / `DoubleAdder` | JDK 8+，**高并发性能优于 AtomicLong** |

## 4. 无锁队列 / 栈

```java
// ConcurrentLinkedQueue (Michael & Scott 算法)
// 1. 入队：CAS tail
// 2. 出队：从 head 往后找到第一个真实节点，CAS next
// 特点：lock-free，wait-free
// 缺点：内存回收靠 GC

// ConcurrentLinkedDeque 类似
```

## 5. AQS（AbstractQueuedSynchronizer）

Java 并发包基石，**ReentrantLock / Semaphore / CountDownLatch / CyclicBarrier** 都基于 AQS：

```
state (volatile int)
   ↓ CAS 成功 → 获得锁
   ↓ CAS 失败 → 入等待队列 park/unpark
```

AQS 模板方法模式：子类只实现 `tryAcquire / tryRelease`。

## 6. 实战：LongAdder vs AtomicLong

```java
// 高并发下 AtomicLong 大量 CAS 失败
LongAdder adder = new LongAdder();
adder.add(1L);          // 分段累加（Cell[]）
long sum = adder.sum();  // 汇总所有 Cell
```

- AtomicLong：所有线程竞争一个变量
- LongAdder：分散到 Cell[]，高并发下写竞争少

## 🔗 下一步
- [JMM 内存模型](/01-concurrency-theory/jmm)
- [ThreadPoolExecutor](/02-thread-pool/executor)
- [synchronized / AQS](/02-thread-pool/executor)
