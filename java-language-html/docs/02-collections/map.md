---
title: HashMap 原理
date: 2026-08-15  # date-auto-injected
---
# HashMap 原理
- Array + linked list + red-black tree (Java 8+)
- Default capacity 16, load factor 0.75 (resize when size > capacity * loadFactor)
- Hash collision: linked list, convert to red-black tree when list length >= 8
- Resize: capacity doubles, rehash all entries
- Thread-unsafe: use ConcurrentHashMap for concurrent access
```java
var map = new HashMap<String, Integer>();
map.put("a", 1);
map.get("a");
// JDK 8+ computeIfAbsent
map.computeIfAbsent("b", k -> map.size() + 1);
```