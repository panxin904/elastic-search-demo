---
layout: home
title: Spring Cloud Alibaba 知识图谱
date: 2026-08-16  # date-auto-injected
hero:
  name: Spring Cloud
  text: Alibaba 系统化学习
  tagline: 用知识图谱串联微服务组件与实战场景
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 🧭 思维导图
      link: /mindmap
features:
  - icon: 🍃
    title: Spring Boot 基础
    details: 快速开始 / 自动配置 / Web / 数据访问 / 事务管理 — 微服务开发的地基
    link: /01-springboot/quickstart
    linkText: 入门 Spring Boot
  - icon: 🌐
    title: 分布式理论
    details: CAP / BASE / 分布式锁 / 分布式事务 / 分布式 ID / 分布式消息 / 分布式追踪 — 系统化梳理
    link: /07-distributed/cap-base
    linkText: 学习分布式理论
  - icon: ☁️
    title: Nacos 服务治理
    details: 服务发现 / 配置中心 / 命名空间 / 集群 — 阿里巴巴开源的核心组件
    link: /02-overview/nacos-discovery
    linkText: 学习 Nacos
  - icon: 🚪
    title: Gateway 网关
    details: 路由 / 断言 / 过滤器 / 限流 — 统一流量入口
    link: /03-gateway/basic
    linkText: 掌握 Gateway
  - icon: ⚖️
    title: 负载均衡
    details: LoadBalancer / Ribbon / 自定义策略 — 客户端负载均衡
    link: /04-loadbalancer/basic
    linkText: 学习负载均衡
  - icon: 🔐
    title: 认证授权
    details: Spring Security / OAuth2 / JWT / 统一认证中心 — 微服务安全
    link: /05-security/oauth2
    linkText: 掌握认证授权
  - icon: 🛡️
    title: Sentinel + Seata
    details: 流控 / 熔断 / 分布式事务 — 微服务稳定性保障
    link: /06-practice/comprehensive
    linkText: 综合实战
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "微服务架构选型：Spring Cloud Alibaba vs Spring Cloud Netflix vs Istio？",
      "Gateway / Nacos / Sentinel / Seata 组件怎么用？",
      "服务注册发现、配置中心、负载均衡、熔断限流怎么串联？",
      "分布式事务（Seata AT / TCC / SAGA）模式怎么选？",
      "Spring Boot 3 + Spring Cloud 2023 新特性？"
    ]
const goals = [
      "微服务架构核心组件（Gateway / Nacos / Sentinel / Seata）",
      "请求链路可视化（从网关到数据库全链路）",
      "服务治理（注册发现 / 配置中心 / 负载均衡 / 熔断限流）",
      "分布式事务（Seata AT / TCC / SAGA 模式选型）",
      "Spring Boot 3 + Spring Cloud 2023 新特性",
      "6 大主题（入门 / 进阶 / 实战 / 监控 / 安全 / 部署）"
    ]
const relatedSites = [
      { site: "java", path: "/01-springboot/quickstart", label: "Spring Boot 入门" },
      { site: "cloud-native", path: "/02-k8s-arch/control-plane", label: "K8s 架构" },
      { site: "observability", path: "/03-otel/overview", label: "OpenTelemetry" },
      { site: "architecture", path: "/01-distributed/cap", label: "分布式理论" },
      { site: "kafka", path: "/01-basics/architecture", label: "消息架构" }
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


<span class="kg-badge kg-badge-springboot">Spring Cloud</span>

# Spring Cloud Alibaba 知识图谱

> **20+ 核心概念节点** + **实战配置速查** + **请求链路可视化** + **6 大主题**
> 系统化学习 Spring Boot + Spring Cloud Alibaba 微服务架构

## 🚀 快速开始

- 📖 **[学习路径](/path)** — 不知道从哪开始？看这里！
- 🌐 **[知识图谱](/graph)** — 20+ 概念的全局关系图
- 🧭 **[思维导图](/mindmap)** — 按主题分类的结构化展示
- 📋 **[组件速查表](/cheatsheet)** — 常用配置模板，一键复制
- ⚙️ **[配置模拟器](#配置模拟器)** — 实时生成 application.yml
- 🌊 **[请求链路演示](#请求链路演示)** — 微服务请求流程可视化

## 🎓 学习建议

1. **入门 (1-2 周)**：Spring Boot 基础 + Nacos
2. **进阶 (2-3 周)**：Gateway + 负载均衡
3. **高级 (2-3 周)**：Spring Security + OAuth2 + JWT
4. **实战 (1-2 月)**：Sentinel + Seata + 综合项目

## 🛠️ 交互组件

| 组件 | 说明 |
|---|---|
| 🌐 知识图谱 | 20+ 概念节点的关系图（可点击跳转） |
| 🧭 思维导图 | 6 大主题的树状展示（可展开/收起） |
| 📋 组件速查 | 30+ 常用配置模板（可搜索 + 一键复制） |
| ⚙️ 配置模拟器 | 实时生成 application.yml |
| 🌊 请求链路 | 微服务请求全流程可视化演示 |

## ⚙️ 配置模拟器

调整参数，实时生成 application.yml 配置：

<ConfigPlayground />

## 🌊 请求链路演示

可视化微服务从客户端到数据库的完整调用流程：

<RequestFlow />

## 🔗 关联资源

- [Spring Boot 官方文档](https://spring.io/projects/spring-boot)
- [Spring Cloud Alibaba 官方文档](https://spring.io/projects/spring-cloud-alibaba)
- [Nacos 官方文档](https://nacos.io/)
- [Spring Cloud Gateway 官方文档](https://spring.io/projects/spring-cloud-gateway)