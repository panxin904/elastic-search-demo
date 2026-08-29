---
title: 并发集合
date: 2026-08-15  # date-auto-injected
---
# 并发集合
- ConcurrentHashMap: segment lock (Java 7) → CAS + synchronized (Java 8+)
- CopyOnWriteArrayList: copy entire array on write, read-only snapshot
- BlockingQueue: ArrayBlockingQueue (bounded), LinkedBlockingQueue (unbounded), SynchronousQueue
- ConcurrentSkipListMap: concurrent TreeMap
```java
var map = new ConcurrentHashMap<String, Integer>();
map.put("a", 1);
var queue = new LinkedBlockingQueue<String>(100);
queue.offer("task");    // non-blocking
queue.take();           // blocking
```