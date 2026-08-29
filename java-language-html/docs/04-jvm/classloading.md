---
title: 类加载机制
date: 2026-08-15  # date-auto-injected
---
# 类加载机制
- Bootstrap ClassLoader (JVM built-in, loads rt.jar)
- Extension/Platform ClassLoader (jre/lib/ext, Java 9+ Platform)
- Application ClassLoader (classpath)
- Parent delegation: child asks parent first, parent can't load then child loads
- Breaking delegation: Tomcat WebappClassLoader, OSGi, JDBC SPI (Thread Context ClassLoader)
```java
ClassLoader cl = String.class.getClassLoader();  // null = Bootstrap
ClassLoader app = MyClass.class.getClassLoader(); // AppClassLoader
```