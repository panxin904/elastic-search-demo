---
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