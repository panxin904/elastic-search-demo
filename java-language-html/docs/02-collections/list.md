---
title: ArrayList / LinkedList
date: 2026-08-15  # date-auto-injected
---
# ArrayList / LinkedList
- ArrayList: dynamic array, O(1) get, O(n) insert/remove, grows 1.5x
- LinkedList: doubly-linked, O(1) insert/remove at ends, O(n) get
- fail-fast: ConcurrentModificationException when iterating while modifying
- Use ArrayList for random access, LinkedList for queue/deque
```java
var list = new ArrayList<String>();
list.add("a");
list.get(0);        // O(1)
var it = list.iterator();
while (it.hasNext()) System.out.println(it.next());
```