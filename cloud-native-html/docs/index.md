---

date: 2026-08-15  # date-auto-injected
layout: home

hero:
  name: 云原生 / Docker / K8s 知识图谱
  text: 系统化学习
  tagline: 用知识图谱串联 Docker → Kubernetes → 生态
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 🧠 思维导图
      link: /mindmap
    - theme: alt
      text: 📋 命令速查
      link: /cheatsheet

features:
  - icon: 🐳
    title: Docker 容器
    details: Docker 基础 · 镜像 · 容器 · 网络 · 卷 · Compose
    link: /01-docker/intro
    linkText: 开始 Docker →
  - icon: 🏛️
    title: k8s 架构
    details: 控制面 / Node / kubectl / etcd · 集群全貌
    link: /02-k8s-arch/overview
    linkText: 看 k8s 架构 →
  - icon: 📦
    title: 工作负载
    details: Pod / Deployment / StatefulSet / DaemonSet / Job
    link: /03-k8s-workload/pod
    linkText: 看工作负载 →
  - icon: 🌐
    title: Service / 网络
    details: Service 三种类型 · Ingress · NetworkPolicy
    link: /04-k8s-service/service
    linkText: 看网络 →
  - icon: 💾
    title: 存储 / 配置
    details: PV / PVC · StorageClass · ConfigMap / Secret
    link: /05-k8s-storage/pv-pvc
    linkText: 看存储 →
  - icon: ⛵
    title: Helm 包管理
    details: Chart 结构 · template · values · 仓库
    link: /06-helm/chart
    linkText: 看 Helm →
  - icon: 📈
    title: 可观测性
    details: Prometheus · Grafana · Loki · Alertmanager
    link: /07-observability/prometheus
    linkText: 看可观测 →
  - icon: 🕸️
    title: Service Mesh
    details: Istio · Sidecar · 流量管理
    link: /08-service-mesh/istio
    linkText: 看 Service Mesh →
  - icon: 🚀
    title: CI/CD & GitOps
    details: GitOps · ArgoCD · Tekton · JenkinsX
    link: /09-cicd/gitops
    linkText: 看 CI/CD →
  - icon: 🏗️
    title: IaC 基础设施
    details: Terraform · Pulumi · Helmfile / Kustomize
    link: /10-iac/terraform
    linkText: 看 IaC →
  - icon: 🔒
    title: 安全
    details: RBAC · Secret · NetworkPolicy + PodSecurity · Falco
    link: /11-security/rbac
    linkText: 看安全 →
  - icon: ☁️
    title: Serverless
    details: Knative Serving · AWS Lambda / GCP Cloud Run
    link: /12-serverless/knative
    linkText: 看 Serverless →
  - icon: 🔧
    title: 排错
    details: kubectl debug · Pod 卡死 · 网络 / DNS 排错套路
    link: /13-troubleshooting/debug
    linkText: 看排错 →
  - icon: 🎯
    title: CKA / CKS / 面试
    details: CKA 考试要点 · CKS 安全 · 高频面试题
    link: /14-interview/cka
    linkText: 看面试 →


---


<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "写了 Dockerfile 不知道 -it / -d / -p 的区别",
      "kubectl apply 后 Pod 一直 Pending / CrashLoopBackOff",
      "Deployment / StatefulSet / DaemonSet 不知道该用哪个",
      "写 Helm Chart 不会 values.yaml",
      "Service Mesh / GitOps 只听过没用过"
    ]
const goals = [
      "系统化讲清 Docker 镜像 / 容器 / 网络 / 卷",
      "深入 k8s 控制面 / 工作负载 / Service / 网络 / 存储",
      "Helm 包管理 + Kustomize",
      "可观测（Prometheus / Grafana / Loki）",
      "Service Mesh（Istio）+ GitOps（ArgoCD）",
      "安全（RBAC / NetworkPolicy / Falco）",
      "排错套路 + CKA / CKS 考试"
    ]
const relatedSites = [
      { site: "architecture", path: "/04-micro/overview", label: "云原生架构" },
      { site: "bigdata", path: "/06-warehouse/overview", label: "云上数仓" },
      { site: "observability", path: "/01-prometheus/overview", label: "云原生监控" },
      { site: "chaos", path: "/01-concepts/overview", label: "云原生韧性" }
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
## 🎯 学习路径

```
🐳 入门     →  Docker 容器 →  Compose 多容器
🏛️ 架构     →  k8s 架构 →  kubectl 命令行
📦 工作负载 →  Pod →  Deployment / StatefulSet / Job
🌐 网络     →  Service →  Ingress →  NetworkPolicy
💾 存储     →  PV / PVC →  ConfigMap / Secret
⛵ Helm    →  Chart 结构 →  template / values
📈 可观测   →  Prometheus →  Grafana →  Alertmanager
🕸️ Mesh   →  Istio 核心 →  Sidecar / 流量
🚀 CI/CD   →  GitOps →  ArgoCD
🏗️ IaC    →  Terraform →  Kustomize
🔒 安全     →  RBAC →  NetworkPolicy →  Falco
☁️ Serverless →  Knative →  Lambda / Cloud Run
🔧 排错     →  kubectl debug →  Pod 卡死 →  DNS
🎯 求职     →  CKA →  CKS →  高频题
```

完整路径请看 [📖 学习路径](/path)。


## 💡 学习建议

```
1. 后端 / 运维新人  →  从 Docker / k8s 架构 / 工作负载 开始
2. SRE / 平台       →  加 Helm / 可观测 / Service Mesh
3. 安全 / 审计      →  加安全章节 + CKS
4. 求职 / 跳槽      →  排错 + CKA 备考
```

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [cloud](https://java-px.bot.cd/cloud/)：Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/)：Linux 内核基础
- [devops](https://java-px.bot.cd/devops/)：DevOps 流程
- [observability](https://java-px.bot.cd/observability/)：K8s 监控
- [architecture](https://java-px.bot.cd/architecture/)：云原生架构
- [security](https://java-px.bot.cd/security/)：容器安全


## 💬 评论与反馈

有问题或建议？欢迎在下方评论。

<ClientOnly>
  <GiscusComment />
</ClientOnly>
