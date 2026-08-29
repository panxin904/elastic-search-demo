---
title: Set / TreeSet
date: 2026-08-15  # date-auto-injected
---
# HashSet / TreeSet
- HashSet backed by HashMap (value is a dummy PRESENT object)
- TreeSet: Red-Black Tree, sorted order, O(log n)
- LinkedHashSet: insertion order, doubly-linked list + HashSet
```java
var set = new HashSet<String>();
set.add("a");
set.contains("a");
var tree = new TreeSet<String>();
tree.add("z"); tree.add("a");  // [a, z]
```