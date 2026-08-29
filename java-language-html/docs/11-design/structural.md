---
title: 结构型设计模式
date: 2026-08-15  # date-auto-injected
---
# 结构型模式
- Proxy: static (compile-time), dynamic (JDK Proxy), CGLIB (subclass)
- Decorator: wrap object to add behavior (InputStream hierarchy)
- Adapter: convert interface (class adapter vs object adapter)
- Facade: simplified interface to complex subsystem
- Bridge: decouple abstraction from implementation
```java
// JDK dynamic proxy
InvocationHandler handler = (proxy, method, args) -> {
  System.out.println("before " + method.getName());
  return method.invoke(target, args);
};
MyInterface proxy = (MyInterface) Proxy.newProxyInstance(
  MyInterface.class.getClassLoader(),
  new Class[]{MyInterface.class}, handler
);
```