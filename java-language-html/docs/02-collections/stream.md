---
title: Stream API
---
# Stream API
- Intermediate: filter, map, flatMap, distinct, sorted, peek, limit, skip
- Terminal: collect, forEach, reduce, count, findFirst, anyMatch, allMatch
- collect(Collectors.toList/toMap/toSet/groupingBy/partitioningBy/joining)
- Parallel stream: .parallelStream(), use only for CPU-bound large data
```java
var result = users.stream()
  .filter(u -> u.getAge() > 18)
  .map(User::getName)
  .sorted()
  .collect(Collectors.toList());
```