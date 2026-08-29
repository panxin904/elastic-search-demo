---
title: 数据类型 / 包装类
date: 2026-08-15  # date-auto-injected
---
# 数据类型 / 包装类

## 📊 8 种基本类型

| 类型 | 字节 | 范围 | 包装类 |
|------|------|------|--------|
| byte | 1 | -128~127 | Byte |
| short | 2 | -32k~32k | Short |
| int | 4 | -2B~2B | Integer |
| long | 8 | -9e18~9e18 | Long |
| float | 4 | 6-7 位 | Float |
| double | 8 | 15-16 位 | Double |
| char | 2 | 0~65535 | Character |
| boolean | 1 (JVM dependent) | true/false | Boolean |

## 🔄 Autoboxing / Unboxing

```java
Integer i = 10;         // autoboxing: int → Integer
int j = i;              // unboxing: Integer → int
Integer a = 100, b = 100;
System.out.println(a == b);      // true（缓存池 -128~127）
Integer c = 200, d = 200;
System.out.println(c == d);      // false（超出缓存）
```

**IntegerCache**：默认缓存 -128~127，可调 `-XX:AutoBoxCacheMax=1024`。

## 📝 String

```java
String s1 = "hello";              // 字面量 → 字符串常量池
String s2 = new String("hello");  // 堆上新对象
System.out.println(s1 == s2.intern());  // true

StringBuilder sb = new StringBuilder();
sb.append("a").append("b");      // 非线程安全，快
StringBuffer sbf = new StringBuffer();
sbf.append("a");                  // 线程安全（synchronized）
```

## 💰 BigDecimal

```java
BigDecimal a = new BigDecimal("0.1");
BigDecimal b = new BigDecimal("0.2");
BigDecimal c = a.add(b);         // 0.3
// ❌ never: new BigDecimal(0.1) → 0.100000000000000005551115123...
```

## 🔗 下一步

- [OOP / 类与对象](/01-basics/oop)
- [异常处理](/01-basics/exceptions)
- [泛型 / 注解 / 反射](/01-basics/generics)

<!-- svg-injected:do-not-edit -->

## 图示：JDK 平台架构（开发工具 + JRE + JPMS + JVM）

![JDK 平台架构（开发工具 + JRE + JPMS + JVM）](/jdk-architecture.svg)
