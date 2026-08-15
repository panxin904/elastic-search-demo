---
layout: home

hero:
  name: "Go 知识图谱"
  text: "云原生 + 后端微服务深度图谱"
  tagline: "从 goroutine 到 Kubernetes —— Go 是云原生时代的母语"
  actions:
    - theme: brand
      text: 开始学习
      link: /01-basics/overview
    - theme: alt
      text: 云原生生态
      link: /04-cloud-native/overview
    - theme: alt
      text: 微服务实战
      link: /05-microservices/overview

features:
  - title: 🐹 Go 基础
    details: "语法速览 / 类型系统 / 函数闭包 / 错误处理 error-panic-recover / 包管理 go.mod / Hello World。简洁哲学：少即是多"
    link: /01-basics/overview
    linkText: 开始学习基础
  - title: ⚡ 并发模型
    details: "CSP 模型 / goroutine / channel / sync.Mutex+WaitGroup+Once / context 上下文传递 / worker pool / pipeline / fan-out 实战模式"
    link: /02-concurrency/overview
    linkText: 掌握并发
  - title: 🔧 生态与工具链
    details: "go build / test / vet / fmt / mod / 标准库 net.http / testing 表驱动 / 覆盖率 / benchmark / pprof 入门"
    link: /03-ecosystem/overview
    linkText: 工具链全景
  - title: ☁️ 云原生生态
    details: "Docker / Kubernetes / Prometheus / etcd 源码导读 + CNCF 项目全景。Go 是云原生时代的母语，所有头部项目都用 Go 写"
    link: /04-cloud-native/overview
    linkText: 云原生全景
  - title: 🌐 后端微服务
    details: "Gin / Echo / gRPC + Protobuf / Kratos / go-zero / go-micro / 服务治理（限流 / 熔断 / 链路追踪）+ 实战案例"
    link: /05-microservices/overview
    linkText: 微服务实战
  - title: 🚀 进阶与 runtime
    details: "runtime.GMP 调度器 / GC 三色标记 + 调优 / pprof + trace 性能分析 / cgo 与 FFI / reflect 反射"
    link: /06-advanced/overview
    linkText: 进阶专题
---
