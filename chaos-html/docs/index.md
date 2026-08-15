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

## 关联站点

混沌工程不是孤岛 — 它需要与可观测性、系统架构、CI/CD、数据库韧性深度协同：

- **observability/** → 混沌可观测性的姐妹篇：稳态假设需要 metric/log/trace 三件套验证 → 链到 `07-observability-for-chaos/overview`
- **system-design/** → 混沌思维下的系统设计：副本数 / 隔离域 / 优雅降级的工程权衡 → 链到 `01-theory/cap-theorem`
- **postgresql/** → 数据库故障演练：主从切换延迟 / 脑裂恢复 / 慢查询风暴 → 链到 `09-connection/failover`
- **devops/** → 流水线注入故障 / 蓝绿切换中的混沌验证 / Argo Rollouts 渐进式发布 → 链到 `04-release/canary`
- **architecture/** → 韧性架构全景：熔断 / 限流 / 舱壁 / 重试 / 多活 → 链到 `05-patterns/circuit-breaker`

## 学习路径建议

| 阶段 | 时长 | 路径 |
|------|------|------|
| 入门 | 1 周 | 01-foundations → 02-chaos-mesh |
| 进阶 | 2 周 | 03-litmus → 04-platform-compare |
| 实战 | 2 周 | 05-resilience-patterns → 06-game-day → 07-observability-for-chaos |
