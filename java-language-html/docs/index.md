---
layout: home

hero:
  name: Java 语言全栈 知识图谱
  text: 系统化学习 Java
  tagline: 从基础语法到 JVM 调优，从集合到并发，从 Spring 到微服务
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 🧠 思维导图
      link: /mindmap
    - theme: alt
      text: 📋 命令速查
      link: /cheatsheet

features:
  - icon: 📐
    title: 基础语法
    details: OOP · 数据类型 · 异常 · 泛型 · 注解 · 反射 · JDK 新特性
    link: /01-basics/oop
    linkText: 开始 →
  - icon: 📚
    title: 集合框架
    details: List/Map/Set 原理 · Stream API · 并发集合
    link: /02-collections/list
    linkText: 看集合 →
  - icon: 🧵
    title: 并发编程
    details: 线程池 · 锁/AQS · JUC · CompletableFuture · 虚拟线程
    link: /03-concurrency/thread-pool
    linkText: 看并发 →
  - icon: ⚙️
    title: JVM 内存模型
    details: 运行时数据区 · 类加载 · 字节码 · OOM 排查
    link: /04-jvm/runtime
    linkText: 看 JVM →
  - icon: 🗑️
    title: GC 垃圾回收
    details: GC 算法 · G1/ZGC/Shenandoah · GC 日志 · 调优
    link: /05-gc/algorithms
    linkText: 看 GC →
  - icon: 🌱
    title: Spring 核心
    details: IoC/DI/AOP · Spring Boot · MVC · 声明式事务
    link: /06-spring/ioc-aop
    linkText: 看 Spring →
  - icon: ☁️
    title: Spring Cloud
    details: Nacos · Gateway · Sentinel · Seata
    link: /07-spring-cloud/nacos
    linkText: 看微服务 →
  - icon: 🗄️
    title: DB / ORM
    details: JDBC · HikariCP · MyBatis/Plus · JPA/Hibernate
    link: /08-database/jdbc
    linkText: 看 DB →
  - icon: 📡
    title: IO / NIO
    details: BIO/NIO/AIO · Netty · 序列化
    link: /09-io/nio
    linkText: 看 IO →
  - icon: ⚡
    title: 性能调优
    details: JVM 调优 · Arthas · jstack/jmap/jstat
    link: /10-performance/jvm-tuning
    linkText: 看性能 →
  - icon: 🏛️
    title: 设计模式
    details: 创建型 · 结构型 · 行为型 · 23 种经典
    link: /11-design/creational
    linkText: 看模式 →
  - icon: 🛠️
    title: 工具 / 构建
    details: Maven/Gradle · Lombok · 常用命令
    link: /12-tools/build
    linkText: 看工具 →
  - icon: 🧪
    title: 测试
    details: JUnit5 · Mockito · Spring Boot Test
    link: /13-testing/junit5
    linkText: 看测试 →
  - icon: 🎯
    title: 面试 / 进阶
    details: 高频面试题 · 手写代码 · 学习路径
    link: /14-interview/questions
    linkText: 看面试 →
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "会用 HashMap 但不理解红黑树和 Hash 冲突",
      "写了 Spring 但不理解 IoC 容器如何工作",
      "遇到 GC 停顿只会调 Xmx",
      "用了线程池但不理解核心参数",
      "面试问 JVM 只知道「堆栈方法区」"
    ]
const goals = [
      "系统化讲清 Java 基础 → 集合 → 并发 → JVM → GC",
      "Spring IoC/AOP/事务/自动配置原理",
      "微服务：Nacos/Gateway/Sentinel/Seata",
      "性能调优：Arthas/jstack/jmap/jstat",
      "设计模式 + 测试 + 工具",
      "面试高频题 + 手写代码"
    ]
const relatedSites = [
      { site: "architecture", path: "/02-thread-pool/executor", label: "并发架构" },
      { site: "system-design", path: "/09-id/snowflake", label: "ID 生成实战" },
      { site: "cloud", path: "/01-springboot/quickstart", label: "Spring Boot 微服务" },
      { site: "kafka", path: "/02-sdks/java", label: "Java 客户端 SDK" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>
## 🎯 学习路径

```
📐 基础    →  OOP / 数据类型 / 异常 / 泛型
📚 集合    →  List/Map/Set / Stream API
🧵 并发    →  线程池 / 锁 / JUC / 虚拟线程
⚙️ JVM   →  运行时数据区 / 类加载 / 字节码
🗑️ GC     →  算法 / G1/ZGC / 调优
🌱 Spring  →  IoC/AOP / Boot / MVC / 事务
☁️ 微服务 →  Nacos / Gateway / Seata
🎯 进阶    →  性能调优 / 设计模式 / 测试 / 面试
```

完整路径请看 [📖 学习路径](/path)。

## 💡 学习建议

```
1. 初学者   →  从"基础语法"和"集合框架"开始
2. 中级     →  加上"并发""JVM""GC"
3. 框架     →  深入 Spring / Spring Cloud
4. 性能     →  性能调优 + Arthas
5. 求职     →  面试高频题 + 手写代码
```