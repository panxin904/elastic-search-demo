---
title: JDK 17-21 新特性
date: 2026-08-15  # date-auto-injected
---
# JDK 17-21 新特性
- JDK 17 (LTS): Sealed classes, Pattern matching for switch, Text blocks finalized, Records
- JDK 21 (LTS): Virtual Threads, Record Patterns, Pattern Matching for switch finalized, String Templates (preview), Sequenced Collections
```java
// Record (JDK 14 final 16)
record Point(int x, int y) {}
// Sealed class (JDK 17)
sealed interface Shape permits Circle, Rectangle {}
// Pattern matching switch (JDK 21)
switch (obj) {
  case String s -> System.out.println(s);
  case Integer i -> System.out.println(i);
  default -> System.out.println("other");
}
// Virtual Thread (JDK 21)
Thread.startVirtualThread(() -> System.out.println("virtual"));
```