---
title: Rust 知识图谱
layout: home
hero:
  name: "Rust 知识图谱"
  text: "系统编程 & 高性能服务"
  tagline: "🦀 内存安全 · 零成本抽象 · 强大生态 · 6 大类 35 节点"
  actions:
    - theme: brand
      text: 从所有权开始 →
      link: /01-basics/overview
    - theme: alt
      text: 并发与异步
      link: /04-concurrency/overview
    - theme: alt
      text: 系统编程
      link: /05-systems/overview
features:
  - title: 🦀 基础与所有权
    details: Rust 入门核心：所有权系统 / 借用规则 / 生命周期 / 模式匹配 / 零成本抽象。从所有权机制开始，建立 Rust 思维模型。
    link: /01-basics/overview
    linkText: 基础总览
  - title: 🏷️ 类型系统与 Trait
    details: 深度类型系统：枚举 + 模式匹配 / 泛型 / Trait 抽象 / 高级类型（Newtype / PhantomData / DST）/ Trait 对象与动态分发。
    link: /02-types-traits/overview
    linkText: 类型系统
  - title: 📦 生态与工具链
    details: Cargo 工作流 / crates.io 生态 / 标准库 / 测试体系 / rustfmt + clippy + rust-analyzer。掌握 Rust 工程实践。
    link: /03-ecosystem/overview
    linkText: 生态总览
  - title: ⚡ 并发与异步
    details: 线程与消息传递 / async-await / Tokio 运行时 / Channel 与共享状态。构建高性能异步服务。
    link: /04-concurrency/overview
    linkText: 并发总览
  - title: ⚙️ 系统编程
    details: unsafe Rust / FFI 与 C 互操作 / 嵌入式 / WebAssembly / 性能分析与优化。深入系统底层。
    link: /05-systems/overview
    linkText: 系统编程
  - title: 🚀 进阶与实战
    details: 声明宏与过程宏 / 闭包与迭代器 / 智能指针 / 错误处理 / 异步生态对比 / 真实案例研究。
    link: /06-advanced/case-study
    linkText: 案例研究
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "所有权 / 借用 / 生命周期推导卡壳？",
      "异步编程（async-await / Tokio）复杂？",
      "Trait / 泛型 / 高级类型（新类型 / PhantomData）难理解？",
      "宏系统（声明宏 / 过程宏）门槛高？",
      "生态相对小、生产案例少？"
    ]
const goals = [
      "基础与所有权（Ownership / Borrowing / Lifetime）",
      "类型系统与 Trait（枚举 / 泛型 / 高级类型）",
      "生态与工具链（Cargo / crates.io / rustfmt / clippy）",
      "并发与异步（async-await / Tokio / Channel）",
      "系统编程（unsafe / FFI / 嵌入式 / WebAssembly）"
    ]
const relatedSites = [
      { site: "go", path: "/01-basics/golang-intro", label: "Go 对比" },
      { site: "linux", path: "/14-kernel/overview", label: "Linux 内核" },
      { site: "security", path: "/01-basics/permissions", label: "内存安全" },
      { site: "architecture", path: "/01-distributed/cap", label: "分布式架构" },
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

## 6 大知识领域

| 领域 | 节点 | 核心问题 |
|------|------|----------|
| 🦀 **基础与所有权** | 6 | Rust 与其他语言的核心区别是什么？所有权 / 借用 / 生命周期如何协同？ |
| 🏷️ **类型系统与 Trait** | 6 | Rust 类型系统的"零成本抽象"如何实现？Trait 与泛型如何组合？ |
| 📦 **生态与工具链** | 5 | 如何管理依赖 / 写测试 / 用工具链保证代码质量？ |
| ⚡ **并发与异步** | 5 | Rust 并发模型的核心原语是什么？async-await 在生产环境如何用？ |
| ⚙️ **系统编程** | 5 | 如何使用 unsafe / FFI / WASM？性能优化如何做？ |
| 🚀 **进阶与实战** | 6 | 宏 / 智能指针 / 错误处理 / 真实案例的关键模式是什么？ |

## 为什么学 Rust

- **内存安全无 GC**：所有权系统在编译期保证内存安全，无运行时 GC 停顿
- **零成本抽象**：泛型 / Trait / 宏 全部编译为与手写代码等效的机器码
- **强类型系统**：类型系统 + 模式匹配让 bug 在编译期被捕获
- **现代工具链**：Cargo / rustfmt / clippy / rust-analyzer 体验一流
- **生产可用**：Discord / Cloudflare / AWS / Microsoft 等公司大规模生产部署

## 学习路径

```
入门（1-2 周）
  → 01-basics 所有权 + 借用 + 生命周期
  → 02-types-traits 枚举 + Trait + 泛型
  → 03-ecosystem Cargo + 基础测试

进阶（2-4 周）
  → 04-concurrency 线程 + async-await
  → 06-advanced 错误处理 + 智能指针
  → 实战项目（CLI / Web Service）

高级（持续）
  → 05-systems unsafe / FFI / 性能
  → 06-advanced 宏 + 异步生态
  → 贡献开源 / 写生产服务
```

## 关联站点

- **cloud-native/** → Rust 写 K8s Operator（kube-rs）
- **observability/** → Tokio Console / eBPF 追踪
- **security/** → Rust 内存安全作为安全防御
- **devops/** → Rust 工具链（cargo / rustfmt / clippy）
- **chaos/** → Rust 写 chaos-mesh / fault-injection 工具 → 高性能故障注入

---

> **Rust 不是更安全的 C++，是一种全新的系统编程思维**。开始你的 Rust 之旅，从 [基础总览](/01-basics/overview) 开始。