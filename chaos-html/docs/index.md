---
layout: home

hero:
  name: 'Chaos Engineering'
  text: '混沌工程知识图谱'
  tagline: '原则 → 工具（Chaos Mesh / Litmus / Gremlin / ChaosBlade）→ 韧性模式 → 游戏日 → 可观测性闭环'
  actions:
    - theme: brand
      text: 开始学习
      link: /01-foundations/overview
    - theme: alt
      text: 工具对比
      link: /04-platform-compare/overview
  image:
    src: /favicon.svg
    alt: Chaos Engineering

features:
  - icon: 🧪
    title: 基础篇
    details: Netflix Chaos Monkey 起源 / 稳态假设 / 爆炸半径 / 故障画像 / 实验方法论
    link: /01-foundations/overview
  - icon: 🔥
    title: Chaos Mesh
    details: CNCF 毕业项目 / PodChaos / NetworkChaos / StressChaos / IOChaos / 工作流编排
    link: /02-chaos-mesh/overview
  - icon: 🧬
    title: Litmus
    details: CNCF 沙箱项目 / ChaosExperiment CRD / Probe 与 Check / Litmus SDK / 50+ 内置实验
    link: /03-litmus/overview
  - icon: ⚖️
    title: 工具对比
    details: Chaos Mesh vs Litmus vs Gremlin vs ChaosBlade 选型矩阵 / 开源 vs 商业 / 多运行时支持
    link: /04-platform-compare/overview
  - icon: 🛡️
    title: 韧性模式
    details: 重试+退避 / 超时与舱壁 / 熔断器 / 限流与降级 / 多活与灾备
    link: /05-resilience-patterns/overview
  - icon: 🎯
    title: 游戏日
    details: 演练设计 / 角色分工（指挥官/注入者/观察员/记录员）/ 注入流程 / 复盘与改进
    link: /06-game-day/overview
  - icon: 📊
    title: 混沌可观测性
    details: 稳态假设度量 / metric-log-trace 联动 / SLO 反馈环 / 实战案例
    link: /07-observability-for-chaos/overview
---


<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "Netflix Chaos Monkey 起源：混沌工程到底解决什么问题？",
      "稳态假设（steady state）怎么定义才不会被实验打破？",
      "爆炸半径（blast radius）如何控制才安全？",
      "Chaos Mesh / Litmus / Gremlin / ChaosBlade 工具怎么选？",
      "故障画像、实验报告、复盘怎么写才有用？"
    ]
const goals = [
      "混沌工程基础（稳态 / 爆炸半径 / 实验方法论）",
      "Chaos Mesh 全场景实操（PodChaos / NetworkChaos / StressChaos / IOChaos）",
      "Litmus ChaosExperiment CRD + Probe / Check + 50+ 内置实验",
      "韧性模式（重试 / 超时 / 舱壁 / 熔断 / 限流 / 降级 / 多活 / 灾备）",
      "游戏日演练设计（指挥官 / 注入者 / 观察员 / 记录员角色分工）",
      "混沌可观测性闭环（metric/log/trace 联动 + SLO 反馈）"
    ]
const relatedSites = [
      { site: "observability", path: "/07-operations/slo", label: "SLO 与稳态假设" },
      { site: "system-design", path: "/01-theory/cap-theorem", label: "副本与隔离域" },
      { site: "postgresql", path: "/09-connection/failover", label: "主从切换演练" },
      { site: "devops", path: "/04-release/canary", label: "蓝绿 + 灰度验证" },
      { site: "architecture", path: "/05-patterns/circuit-breaker", label: "熔断 / 限流 / 舱壁" }
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

## 学习路径建议

| 阶段 | 时长 | 路径 |
|------|------|------|
| 入门 | 1 周 | 01-foundations → 02-chaos-mesh |
| 进阶 | 2 周 | 03-litmus → 04-platform-compare |
| 实战 | 2 周 | 05-resilience-patterns → 06-game-day → 07-observability-for-chaos |
