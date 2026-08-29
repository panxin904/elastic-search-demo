---
title: volatile / final
date: 2026-08-15  # date-auto-injected
---
# volatile 与 final

## 1. volatile 三大特性

```java
private volatile boolean flag;
```

| 特性 | 含义 |
|------|------|
| **可见性** | 写立刻刷主内存，读从主内存读 |
| **禁止重排** | 写前后加 StoreLoad 屏障 |
| **不保证原子性** | `count++` 仍是三步操作，非原子 |

> volatile 是**轻量级同步**：性能优于 synchronized（无 monitorenter/exit）。

## 2. volatile 内存语义

```
写 volatile:
  1. StoreStore 屏障（禁止前面的普通写与 volatile 写重排）
  2. 写入主内存
  3. StoreLoad 屏障（禁止 volatile 写与后面的读重排）

读 volatile:
  1. LoadLoad 屏障
  2. 从主内存读
  3. LoadStore 屏障
```

**JMM 底层用 lock addl 指令实现**（x86）。

## 3. volatile 适用场景

```java
// 1. 状态标志
private volatile boolean shutdownRequested = true;

// 2. 一次性安全发布（double-checked locking）
private volatile Singleton instance;

// 3. 配合 CAS（Atomic*）
AtomicLong counter = new AtomicLong();

// 4. 与 happens-before 配合（双重检查锁）
public class DCL {
  private volatile static DCL instance;
  public static DCL get() {
    if (instance == null) {
      synchronized (DCL.class) {
        if (instance == null) instance = new DCL();
      }
    }
    return instance;
  }
}
```

## 4. 不适用 volatile 的场景

- `count++`（复合操作）
- 对象引用非原子赋值（实际引用赋值是原子的，但配合其他操作时不一定）
- 多变量一致性

## 5. final 关键字

```java
// final 字段：构造完成前必须赋值；JMM 保证构造对象的 final 字段对其他线程可见（正确发布）
public class User {
  private final String name;  // 安全发布
  private static final int MAX = 100;
}
```

**final 语义**（JMM）：
- 构造器中 this 逸出会破坏 final 安全发布
- final 引用（不能改引用本身，但引用对象可变）

## 6. 实战

```java
// 典型 DCL
class Config {
  private volatile static Config INSTANCE;
  public static Config getInstance() {
    Config c = INSTANCE;  // 读 volatile，普通读
    if (c == null) {
      synchronized (Config.class) {
        c = INSTANCE;
        if (c == null) c = new Config();
        INSTANCE = c;  // 写 volatile，普通写
      }
    }
    return c;
  }
}
```

## 🔗 下一步
- [JMM 内存模型](/01-concurrency-theory/jmm)
- [happens-before](/01-concurrency-theory/happens-before)
- [synchronized / AQS](/02-thread-pool/executor)
