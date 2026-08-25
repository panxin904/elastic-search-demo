---
title: 设计模式 / GoF 23 式 / 反模式
layout: home

hero:
  name: "设计模式"
  text: "GoF 23 模式 + 现代架构模式 + 反模式自查表"
  tagline: "创建型 · 结构型 · 行为型 · 现代模式 · 架构模式 · 反模式 · Java + Go + TypeScript 多语言对照"
  image:
    src: /favicon.svg
    alt: 设计模式
  actions:
    - theme: brand
      text: 开始学习
      link: /01-gof-creational/overview
    - theme: alt
      text: 反模式自查
      link: /06-anti-patterns/overview

features:
  - title: 🏗️ 创建型模式
    details: 5 种创建型模式：Singleton 单例 / Factory Method 工厂方法 / Abstract Factory 抽象工厂 / Builder 建造者 / Prototype 原型。每种模式给 Java + Go + TypeScript 三语言实现，对比单线程/分布式场景下的线程安全与生命周期管理。
    link: /01-gof-creational/overview
    linkText: 创建型总览
  - title: 🧩 结构型模式
    details: 7 种结构型模式：Adapter / Bridge / Composite / Decorator / Facade / Flyweight / Proxy。重点是类与对象的组合方式：装饰器在 Java IO/Go middleware/TS Nest 中如何演进，代理模式与 RPC 框架的天然契合。
    link: /02-gof-structural/overview
    linkText: 结构型总览
  - title: 🎭 行为型模式
    details: 11 种行为型模式：Chain of Responsibility / Command / Iterator / Mediator / Memento / Observer / State / Strategy / Template Method / Visitor / Interpreter。聚焦对象间的职责分配与通信，事件驱动架构与观察者模式的深层关系。
    link: /03-gof-behavioral/overview
    linkText: 行为型总览
  - title: ✨ 现代模式
    details: 云原生时代的现代模式：依赖注入（DI 容器与控制反转）/ Repository（仓储模式与持久化抽象）/ Specification（规格模式与查询组合）/ Null Object（消除 null 检查）。Spring Boot / Go Wire / NestJS 框架源码解读。
    link: /04-modern-patterns/overview
    linkText: 现代模式总览
  - title: 🌐 架构模式
    details: 8 大架构模式：CQRS / Event Sourcing / Saga / Sidecar / Circuit Breaker / Bulkhead / Strangler Fig / Outbox。微服务时代的关键武器：Axon 框架 / Kafka 事件流 / Resilience4j / Istio 数据面实战。
    link: /05-architectural-patterns/overview
    linkText: 架构模式总览
  - title: 🚫 反模式
    details: 7 大反模式自查表：God Object 上帝对象 / Anemic Model 贫血模型 / Big Ball of Mud 大泥球 / Callback Hell 回调地狱 / Circular Dependency 循环依赖 / Magic Number 魔数 / Premature Optimization 提前优化。每条配"症状-病因-药方"清单，code review 直接用。
    link: /06-anti-patterns/overview
    linkText: 反模式总览
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "GoF 23 式记不全，面试问到「装饰器 vs 代理」讲不清？",
      "创建型 / 结构型 / 行为型 分类背后的设计原则（开闭 / 里氏 / 依赖倒置）？",
      "现代模式（DI / Repository / Specification）跟 GoF 的关系？",
      "架构模式（CQRS / Event Sourcing / Saga / Sidecar）落地难？",
      "反模式（God Object / 贫血模型 / 大泥球）怎么识别 + 改造？"
    ]
const goals = [
      "GoF 23 式（创建型 5 + 结构型 7 + 行为型 11）三语言（Java / Go / TS）实现",
      "现代模式（DI / Repository / Specification / Null Object）",
      "架构模式（CQRS / Event Sourcing / Saga / Sidecar / Circuit Breaker）",
      "反模式自查（God Object / Anemic Model / Big Ball of Mud / Callback Hell）",
      "6 大主题（GoF 创建型 / GoF 结构型 / GoF 行为型 / 现代模式 / 架构模式 / 反模式）"
    ]
const relatedSites = [
      { site: "java-language", path: "/05-spring/ioc", label: "Spring IoC/AOP" },
      { site: "java", path: "/01-springboot/quickstart", label: "Spring Boot 实战" },
      { site: "architecture", path: "/05-patterns/circuit-breaker", label: "熔断 / 舱壁模式" },
      { site: "kafka", path: "/01-basics/architecture", label: "Event Sourcing 架构" },
      { site: "system-design", path: "/01-theory/cap-theorem", label: "系统设计基础" }
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

## 🗺️ GoF 23 模式总览

```mermaid
graph TB
    GoF23["GoF 23 设计模式"]
    
    GoF23 --> C["🏗️ 创建型 5"]
    C --> C1["Singleton<br/>单例"]
    C --> C2["Factory Method<br/>工厂方法"]
    C --> C3["Abstract Factory<br/>抽象工厂"]
    C --> C4["Builder<br/>建造者"]
    C --> C5["Prototype<br/>原型"]
    
    GoF23 --> S["🧩 结构型 7"]
    S --> S1["Adapter<br/>适配器"]
    S --> S2["Bridge<br/>桥接"]
    S --> S3["Composite<br/>组合"]
    S --> S4["Decorator<br/>装饰器"]
    S --> S5["Facade<br/>外观"]
    S --> S6["Flyweight<br/>享元"]
    S --> S7["Proxy<br/>代理"]
    
    GoF23 --> B["🎭 行为型 11"]
    B --> B1["Chain of<br/>Responsibility"]
    B --> B2["Command<br/>命令"]
    B --> B3["Iterator<br/>迭代器"]
    B --> B4["Mediator<br/>中介者"]
    B --> B5["Memento<br/>备忘录"]
    B --> B6["Observer<br/>观察者"]
    B --> B7["State<br/>状态"]
    B --> B8["Strategy<br/>策略"]
    B --> B9["Template Method<br/>模板方法"]
    B --> B10["Visitor<br/>访问者"]
    B --> B11["Interpreter<br/>解释器"]
    
    style GoF23 fill:#8b5cf6,color:#fff,stroke:#7c3aed
    style C fill:#3b82f6,color:#fff,stroke:#2563eb
    style S fill:#10b981,color:#fff,stroke:#059669
    style B fill:#f59e0b,color:#fff,stroke:#d97706
```

> 三大类对应本站三大目录（01 创建型 / 02 结构型 / 03 行为型），每类都有 overview 总览页。


## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [java-language](https://java-px.bot.cd/java-language/)：Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/)：Java 实现
- [architecture](https://java-px.bot.cd/architecture/)：架构模式
- [system-design](https://java-px.bot.cd/system-design/)：系统设计
