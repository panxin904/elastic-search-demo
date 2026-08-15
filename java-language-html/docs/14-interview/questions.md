---
title: 高频面试题
---
# Java 高频面试题
1. HashMap 原理？数组+链表/红黑树，hash冲突，扩容，loadFactor 0.75
2. ConcurrentHashMap 怎么保证线程安全？Java 7 Segment锁，Java 8 CAS+synchronized
3. synchronized vs Lock？JVM内置 vs API，自动释放 vs finally unlock，condition等待通知
4. volatile 作用？可见性+禁止指令重排+不保证原子性
5. ThreadLocal 原理与内存泄漏？ThreadLocalMap，Key弱引用，remove()
6. JVM 内存模型？堆/栈/方法区/程序计数器/本地方法栈
7. CMS vs G1？CMS标记清除碎片，G1 Region+MixedGC+可预期暂停
8. Spring IoC/AOP？Bean容器，动态代理/CGLIB切面
9. @Transactional 传播机制？REQUIRED/REQUIRES_NEW/NESTED
10. N+1 问题？LAZY加载+循环=1+N条SQL，用@Query JOIN FETCH或@EntityGraph
