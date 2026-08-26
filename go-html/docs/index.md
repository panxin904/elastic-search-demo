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

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "goroutine 调度原理、栈扩容讲不清？",
      "channel vs sync.Mutex 不知道选哪个？",
      "Go 错误处理（error / panic / recover）哲学？",
      "微服务架构、gRPC、Service Mesh 怎么落地？",
      "K8s operator / controller-runtime 不会写？"
    ]
const goals = [
      "Go 基础语法 + 类型系统 + 函数闭包",
      "并发模型（CSP / goroutine / channel / context）",
      "错误处理 + 包管理 + 工具链",
      "云原生生态（Docker / K8s / Prometheus / etcd）",
      "微服务实战（gRPC / 服务发现 / 链路追踪）"
    ]
const relatedSites = [
      { site: "cloud-native", path: "/01-docker/overview", label: "Docker 全栈" },
      { site: "java-language", path: "/04-jvm/overview", label: "JVM 对比" },
      { site: "architecture", path: "/01-distributed/cap", label: "分布式 CAP" },
      { site: "devops", path: "/01-pipeline/overview", label: "CI/CD 流水线" },
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

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [rust](https://java-px.bot.cd/rust/)：Rust 对比
- [cloud-native](https://java-px.bot.cd/cloud-native/)：K8s / Docker
- [devops](https://java-px.bot.cd/devops/)：DevOps 工具
- [java](https://java-px.bot.cd/java-web-manual/)：Java 对比
- [network](https://java-px.bot.cd/network/)：Go 高并发网络


<!-- auto-enrich:do-not-edit -->

## 实战示例

\`\`\`bash
# TODO: 在此补充本页主题的实战命令
echo "hello"
\`\`\`

\`\`\`yaml
# TODO: 配置示例
key: value
\`\`\`

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
