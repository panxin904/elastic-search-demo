---
title: 创建型设计模式
---
# 创建型模式
- Singleton: DCL + volatile, enum, static inner class holder
- Factory Method: define interface, subclasses decide class
- Builder: fluent API for complex object construction (Lombok @Builder)
- Prototype: clone existing object
```java
// Singleton: static inner class (recommended)
public class Singleton {
  private Singleton() {}
  private static class Holder { static final Singleton INSTANCE = new Singleton(); }
  public static Singleton getInstance() { return Holder.INSTANCE; }
}
// Builder with Lombok
@Builder record User(String name, int age, String email) {}
```