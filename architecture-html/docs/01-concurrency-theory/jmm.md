---
title: JMM 内存模型
---
# JMM（Java Memory Model）内存模型

## 1. JMM 解决了什么问题？

JMM 定义了线程如何与内存交互，**解决了"可见性"和"指令重排"**两大核心问题：

- **可见性**：一个线程修改了共享变量，另一个线程能立即看到。
- **原子性**：操作要么全部完成，要么全部不完成。
- **有序性**：程序执行的顺序看起来是按代码顺序的（实际 JIT/CPU 可能重排）。

> 没有 JMM 之前，多线程程序的行为依赖物理硬件，Java 是跨平台的——必须定义一个**与硬件无关的内存模型**。

## 2. JMM 抽象结构

```
┌──── Java Memory Model ────┐
│                           │
│  Main Memory (堆)         │  ← 共享（所有线程可见）
│   - 共享变量              │
│                           │
│  ┌─ Thread 1 ─┐ ┌─ Thread 2 ─┐
│  │ Working     │ │ Working     │  ← 线程私有
│  │ Memory      │ │ Memory      │
│  │ (副本)     │ │ (副本)     │
│  └────────────┘ └────────────┘
│                           │
│  CPU Registers ←→ Cache  │  ← 硬件层
└───────────────────────────┘
```

- **主内存**：堆上的共享变量（实例字段、静态字段、数组元素）
- **工作内存**：线程私有的栈帧副本（CPU 寄存器 / 缓存的抽象）

线程对共享变量的所有操作都在工作内存中，必须写回主内存才生效。

## 3. 八大原子操作

JMM 定义了 8 个内存间交互操作（lock / unlock / read / load / use / assign / store / write），规定了它们的执行规则。

```
use ← read  (从主内存读)
         ↓
    load
         ↓
   工作内存
         ↓
   线程执行操作
         ↓
   assign
         ↓
   store
         ↓
   write → 主内存
```

## 4. 三大特性

| 特性 | 含义 | Java 实现 |
|------|------|------------|
| **原子性** | 一个操作不可中断 | synchronized, Lock, Atomic* |
| **可见性** | 一个线程的写，其他线程立即看到 | volatile, synchronized, final |
| **有序性** | 操作按代码顺序执行（无重排时） | happens-before 规则 |

## 5. 关键原理

- **lock / unlock**：作用于主内存的变量
- **volatile**：保证可见性（每次读都从主内存读，每次写都立即刷回）
- **synchronized**：保证可见性 + 原子性（monitorenter / monitorexit 屏障）
- **final**：构造对象时正确发布（无 this 逸出）

## 6. 重排序（Reordering）

编译器 + CPU 都会重排指令，**单线程不改变语义，多线程可能出错**：

```java
int a = 0, b = 0;
// Thread 1
a = 1;  // 1. 写 a
b = 1;  // 2. 写 b
// 可能重排为：b=1, a=1

// Thread 2
if (b == 1) {  // 3. 读 b
  a = a + 1;    // 4. 读 a + 1
  // 可能看到 a=0（被重排，a=1 还没刷回）
}
```

`volatile`、`synchronized` 等建立**内存屏障**，禁止特定重排。

## 7. 经典例子：双重检查锁（DCL）

```java
class Singleton {
  private volatile static Singleton instance;
  private Singleton() {}
  public static Singleton getInstance() {
    if (instance == null) {
      synchronized (Singleton.class) {
        if (instance == null) {
          instance = new Singleton();  // 1.分配 2.初始化 3.赋值
        }
      }
    }
    return instance;
  }
}
```

**为什么必须 volatile**？防止重排为 1→3→2，其他线程看到 instance 非 null 但未初始化。

## 🔗 下一步
- [happens-before](/01-concurrency-theory/happens-before)
- [volatile / final](/01-concurrency-theory/volatile)
- [CAS / Lock-Free](/01-concurrency-theory/cas)
- [ThreadPoolExecutor](/02-thread-pool/executor)
