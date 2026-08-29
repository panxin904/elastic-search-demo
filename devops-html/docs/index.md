---
layout: home
title: DevOps 知识图谱
date: 2026-08-27  # date-auto-injected
hero:
  name: DevOps
  text: 软件交付链深度图谱
  tagline: CI/CD Pipeline · IaC · GitOps · 蓝绿/灰度/金丝雀 · DORA Metrics · 平台工程
  actions:
    - theme: brand
      text: ⚙️ 进入 Pipeline
      link: /01-pipeline/overview
    - theme: alt
      text: 🏗️ IaC
      link: /02-iac/overview
    - theme: alt
      text: 🔄 GitOps
      link: /03-gitops/overview
    - theme: alt
      text: 🚀 发布策略
      link: /04-release/overview
features:
  - title: ⚙️ CI/CD Pipeline
    details: Pipeline as Code 范式、GitHub Actions / GitLab CI / Jenkins / Tekton 横向对比、构建缓存、Pipeline 编排。
    link: /01-pipeline/overview
    linkText: Pipeline 总览
  - title: 🏗️ IaC 基础设施即代码
    details: Terraform / Pulumi / Ansible / CloudFormation 设计取舍、状态管理、模块化、最佳实践与 drift 检测。
    link: /02-iac/overview
    linkText: IaC 总览
  - title: 🔄 GitOps
    details: ArgoCD / Flux / Argo Rollouts 核心原理、声明式同步、渐进式交付、回滚机制、与 CI/CD 的边界划分。
    link: /03-gitops/overview
    linkText: GitOps 总览
  - title: 🚀 渐进式发布
    details: 蓝绿 / 灰度 / 金丝雀 / 影子流量 / Feature Flag 五种发布策略原理、风险、适用场景与回滚机制。
    link: /04-release/overview
    linkText: 发布策略
  - title: 📊 DORA Metrics
    details: 部署频率 / 变更前置时间 / 变更失败率 / 恢复时间 4 个核心指标，研发效能度量的行业标准。
    link: /05-cicd-observability/dora-metrics
    linkText: DORA 度量
  - title: ⭐ 平台工程
    details: 构建缓存、安全流水线、Secrets 管理、OIDC 联邦身份、AI 时代 GPU/LLM 推理发布新场景。
    link: /06-best-practices/case-study
    linkText: 最佳实践
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "CI/CD 工具太多（Jenkins / GitLab CI / GitHub Actions / Argo），怎么选？",
      "Pipeline as Code 怎么写才不会变成 YAML 屎山？",
      "Terraform / Pulumi / Ansible 三大 IaC 工具怎么选？",
      "ArgoCD / Flux GitOps 的「声明式真相源」怎么落地？",
      "蓝绿 / 灰度 / 金丝雀 发布策略与回滚机制怎么设计？",
      "DORA 4 个核心指标（部署频率 / 变更前置时间 / 变更失败率 / 恢复时间）怎么度量？"
    ]
const goals = [
      "CI/CD 全链路（Pipeline as Code / Artifact / 制品库 / 部署）",
      "IaC 框架（Terraform / Pulumi / Ansible）",
      "GitOps 落地（ArgoCD / Flux / 渐进式交付）",
      "发布策略（蓝绿 / 灰度 / 金丝雀 / Argo Rollouts）",
      "研发效能度量（DORA 4 指标 / 平台工程）",
      "安全流水线（OIDC / Sigstore / SBOM）"
    ]
const relatedSites = [
      { site: "observability", path: "/05-sre/overview", label: "SRE 实践" },
      { site: "cloud-native", path: "/03-gitops/argocd", label: "ArgoCD 落地" },
      { site: "security", path: "/06-best-practices/secure-pipeline", label: "安全流水线" },
      { site: "architecture", path: "/01-pipeline/overview", label: "软件交付架构" },
      { site: "chaos", path: "/04-release/canary", label: "蓝绿 + 混沌验证" }
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


## 关联站点

- **observability/** → SLO / 告警如何挂在流水线产物上 → 链到 `05-cicd-observability/`
- **cloud-native/** → K8s 上跑 ArgoCD / Helm → 链到 `03-gitops/argocd`
- **security/** → 流水线集成 Sigstore / SBOM → 链到 `06-best-practices/secure-pipeline`
- **architecture/** → 软件交付架构、平台工程 → 链到 `01-pipeline/overview`
- **ai/** → LLM 推理服务 A/B / 影子流量 / GPU 资源调度 → 链到 `06-best-practices/case-study`
- **chaos/** → 流水线注入故障：CI 阶段跑 chaos-mesh / 蓝绿切换的混沌验证 → 链到 `04-release/canary`

## 学习路径建议

| 阶段 | 时长 | 章节 |
|------|------|------|
| 入门 | 1-2 周 | 01-pipeline → 02-iac |
| 进阶 | 2-3 周 | 03-gitops → 04-release |
| 高级 | 2-3 周 | 05-cicd-observability → 06-best-practices |
| 实战 | 持续 | 配套 cloud-native / observability / ai 实战案例 |

---

**适用读者**：SRE / DevOps 工程师 / 平台工程师 / 后端架构师 / 研发效能负责人 / 关注 AI 部署的算法工程师。

**前置知识**：Linux 命令行、Git、Docker 基础、至少一门后端语言、HTTP 协议。

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [cloud-native](https://java-px.bot.cd/cloud-native/)：K8s 编排
- [linux](https://java-px.bot.cd/linux/)：Linux 运维
- [observability](https://java-px.bot.cd/observability/)：监控告警
- [python](https://java-px.bot.cd/python/)：脚本工具
- [go](https://java-px.bot.cd/go/)：Go 工具链
