---
title: GC 算法
---
# GC 算法
- Mark-Sweep: mark reachable, sweep unreachable → fragmentation
- Copying: Eden → Survivor, compact → used in Young Gen
- Mark-Compact: mark then compact → Old Gen
- Generational: weak generational hypothesis (most objects die young)
- Card Table: tracks references from Old to Young (Remembered Set)
```java
// Young GC (Minor GC): Eden full → copy to Survivor
// Old GC (Major GC): Old Gen full
// Full GC: entire heap + Metaspace
```