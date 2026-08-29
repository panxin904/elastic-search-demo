---
title: 学习路径
date: 2026-08-15  # date-auto-injected
---
# 📖 Java 学习路径

## 🛤️ 路径 1：Java 入门（1-2 周）
1. [OOP / 类与对象](/01-basics/oop) — 封装继承多态
2. [数据类型 / 包装类](/01-basics/datatypes) — 基本类型 vs 引用
3. [异常处理](/01-basics/exceptions) — try-catch-finally
4. [泛型 / 注解 / 反射](/01-basics/generics) — Java 高级特性
5. [JDK 17-21 新特性](/01-basics/new-features) — record/sealed/pattern
**目标**：能写健壮的 Java 类。

## 🛤️ 路径 2：集合 + 并发（2-3 周）
- 完成"入门"路径
- [List/ArrayList/LinkedList](/02-collections/list)
- [HashMap 原理](/02-collections/map) — hash/红黑树/扩容
- [Stream API](/02-collections/stream) — filter/map/reduce
- [线程/线程池](/03-concurrency/thread-pool)
- [synchronized/AQS](/03-concurrency/locks) — 锁底层
- [CompletableFuture](/03-concurrency/future) — 异步编排
- [虚拟线程](/03-concurrency/virtual-threads) — JDK 21 Loom
**目标**：能写出线程安全的集合操作。

## 🛤️ 路径 3：JVM + GC（2 周）
- [JVM 运行时数据区](/04-jvm/runtime)
- [类加载机制](/04-jvm/classloading)
- [GC 算法](/05-gc/algorithms)
- [G1/ZGC/Shenandoah](/05-gc/collectors)
- [GC 调优](/05-gc/tuning)
- [OOM 排查](/04-jvm/oom)
- [JVM 调优参数](/10-performance/jvm-tuning)
**目标**：能看懂 GC 日志，调 JVM 参数。

## 🛤️ 路径 4：Spring 全栈（3 周）
- [IoC/DI/AOP](/06-spring/ioc-aop)
- [Spring Boot 自动配置](/06-spring/boot)
- [Spring MVC](/06-spring/mvc)
- [声明式事务](/06-spring/transaction)
- [MyBatis/Plus](/08-database/mybatis)
- [Nacos 注册/配置中心](/07-spring-cloud/nacos)
- [Gateway/Sentinel](/07-spring-cloud/gateway)
**目标**：能搭建 Spring Boot + Cloud 微服务。

## 🛤️ 路径 5：性能调优（1 周）
- [JVM 调优参数](/10-performance/jvm-tuning)
- [Arthas 诊断](/10-performance/arthas)
- [jstack/jmap/jstat](/10-performance/jvm-tools)
- [BIO/NIO/AIO](/09-io/nio)
**目标**：能用 Arthas 排查线上问题。

## 🛤️ 路径 6：面试冲刺（2 周）
- 复习 [HashMap 原理](/02-collections/map)
- 复习 [synchronized/AQS](/03-concurrency/locks)
- 复习 [JVM 运行时数据区](/04-jvm/runtime)
- 复习 [GC 算法](/05-gc/algorithms)
- [高频面试题](/14-interview/questions)
- [手写代码](/14-interview/coding)

## 🎯 速查卡片
| 我想 | 推荐先看 |
|------|---------|
| 入门 | [OOP 类与对象](/01-basics/oop) → [集合](/02-collections/list) |
| 学并发 | [线程池](/03-concurrency/thread-pool) → [锁](/03-concurrency/locks) |
| 学 JVM | [运行时数据区](/04-jvm/runtime) → [GC](/05-gc/algorithms) |
| 学 Spring | [IoC/AOP](/06-spring/ioc-aop) → [Boot](/06-spring/boot) |
| 调优 | [JVM 调优](/10-performance/jvm-tuning) → [Arthas](/10-performance/arthas) |
| 找工作 | [面试题](/14-interview/questions) → [手写代码](/14-interview/coding) |