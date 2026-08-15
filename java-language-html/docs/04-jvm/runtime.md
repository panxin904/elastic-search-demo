---
title: JVM 运行时数据区
---
# JVM 运行时数据区
- Heap: Young (Eden+S0+S1), Old, shared by all threads
- Method Area / Metaspace: class metadata, constants, static vars (Java 8+ Metaspace in native memory)
- VM Stack: each thread has one, stores stack frames (local vars, operand stack, return address)
- Native Method Stack: for native methods
- PC Register: current bytecode instruction address
```java
// Adjust memory sizes
// -Xms512m -Xmx2g  (heap)
// -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=256m
```