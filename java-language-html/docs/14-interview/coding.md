---
title: 手写代码
date: 2026-08-15  # date-auto-injected
---
# 手写代码题
1. 线程安全单例（DCL+volatile, static inner class, enum）
2. 生产者-消费者（BlockingQueue, wait/notify, Lock+Condition）
3. 死锁（两线程互相等待对方锁）
4. LRU缓存（LinkedHashMap accessOrder，或 HashMap+双向链表）
5. 两个线程交替打印奇偶数
6. 限流器（令牌桶/滑动窗口）
```java
// LRU Cache with LinkedHashMap
class LRU`<K,V>` extends LinkedHashMap`<K,V>` {
  private final int capacity;
  LRU(int cap) { super(cap, 0.75f, true); this.capacity = cap; }
  protected boolean removeEldestEntry(Map.Entry`<K,V>` e) { return size() > capacity; }
}
// Producer-Consumer with BlockingQueue
var q = new LinkedBlockingQueue<Integer>(10);
new Thread(() -> { while(true) q.put(produce()); }).start();
new Thread(() -> { while(true) consume(q.take()); }).start();
```