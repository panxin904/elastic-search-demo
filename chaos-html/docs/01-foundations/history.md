---
title: 历史与哲学
---

# 历史与哲学

## 起源与发展

混沌工程的起源可以追溯到 2010 年 Netflix 的云架构迁移。当时 Netflix 把单体应用迁移到 AWS 云上，失去对硬件的直接控制，需要一种方法来验证云上系统的韧性。

2010 年 Netflix 内部开始开发 Chaos Monkey，自动随机终止 EC2 实例。2012 年 Netflix 把 Chaos Monkey 开源，业界开始关注。2014 年 Netflix 推出 Simian Army（Chaos Gorilla 模拟整个可用区故障 / Chaos Kong 模拟整个 Region 故障）。

2015 年 Netflix、Disney、Microsoft 等公司联合发布 Principles of Chaos 白皮书，正式确立了混沌工程的四大原则。2016 年 Netflix 推出 ChAP（Chaos Automation Platform），把混沌工程从单点实验升级为平台化。

2018 年 Gremlin 完成 2950 万美元 A 轮融资，商业化混沌工程。2019 年阿里开源 ChaosBlade，PingCAP 开源 Chaos Mesh。2021 年 Chaos Mesh 进入 CNCF Sandbox，Litmus 进入 CNCF Sandbox。

2022 年 Gremlin 完成 C 轮融资，企业市场爆发。2023 年 Chaos Mesh 晋升 CNCF Incubating。2024 年 11 月 Chaos Mesh 毕业（CNCF Graduated），标志着混沌工程成为云原生领域的主流实践。

**关键里程碑时间线**：

- 2010：Netflix Chaos Monkey 内部开发
- 2012：Chaos Monkey 开源
- 2014：Simian Army 发布
- 2015：Principles of Chaos 白皮书
- 2016：ChAP 平台化
- 2018：Gremlin 商业化
- 2019：ChaosBlade / Chaos Mesh 开源
- 2021：Chaos Mesh + Litmus 进入 CNCF Sandbox
- 2024：Chaos Mesh CNCF 毕业
- 2025+：AI 辅助故障画像 + 自适应混沌

**哲学思考**：

混沌工程不是「破坏测试」，而是「**对系统韧性的科学实验**」。它有方法论、有假设、有验证、有复盘。这与「故意搞破坏」（breaking things for fun）有本质区别。

混沌工程的哲学基础是「**拥抱失败**」（embrace failure）：失败不是异常状态，而是系统的常态。系统的设计应该假设失败会发生，并提前准备好应对措施。

**与 SRE 文化的关系**：

混沌工程是 SRE 文化的重要组成部分。Google SRE Book Chapter 22「Addressing Cascading Failures and Other Bad Behavior」详细描述了类似实践，包括 DiRT（Disaster Recovery Testing）和 FireDrill（小规模演练）。

## 关键人物与组织

**Netflix**：

- Adrian Cockcroft（架构师，2010 年推动 Chaos Monkey）
- Yury Izrailevsky（VP Cloud Architecture）
- Casey Rosenthal（Chaos Engineering 团队 Lead）

**PingCAP**：

- 周畅（CEO）
- 吴雪晶（Chaos Mesh Lead Maintainer）

**MayaData**（Litmus 创始））：

- Karthik Satchitanand（创始人）

**Gremlin**：

- Kolton Andrus（CEO，前 AWS Chaos Engineer）
- Matt Fornaciari（CTO）

**阿里**：

- 李三红（ChaosBlade Lead）
- 陈洁萌（AHAS Lead）

**社区贡献者**：

- Yuri Shkuro（Jaeger / Dapper 作者，Chaos Mesh 用户）
- Henrik Høegh（Observability 专家）

## 与其他站点关系

- **observability**：混沌实验验证 observability 设计的正确性 → 引用 observability/01-foundations
- **devops**：混沌工程纳入 CI/CD → 引用 devops/01-pipeline/overview
- **system-design**：可用性原则的工程化 → 引用 system-design/08-availability
