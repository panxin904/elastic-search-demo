---
title: 泛型 / 注解 / 反射
date: 2026-08-15  # date-auto-injected
---
# 泛型 / 注解 / 反射
- Type erasure: generics exist only at compile time, `&#60;T>` becomes Object at runtime
- PECS principle: Producer Extends, Consumer Super
- @Override, @FunctionalInterface, @Deprecated, @SuppressWarnings
- Reflection: Class.forName, getDeclaredMethods, getDeclaredFields, setAccessible (Java 9+ restricted)
```java
// Producer Extends (read)  Consumer Super (write)
void copy(List<? extends Number> src, List<? super Number> dst) {
  for (Number n : src) dst.add(n);
}
```