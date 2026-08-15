---
title: 学习路径
---

# 📖 云原生学习路径

> 根据你的角色选择对应路径，每条路径推荐了核心阅读顺序。

## 🛤️ 路径 1：纯新手（1 周）

适合**没碰过 Docker / k8s** 的开发者。

1. [Docker 基础](/01-docker/intro) — 容器是什么
2. [镜像 image](/01-docker/image) — docker build / pull
3. [容器 container](/01-docker/container) — docker run 基础
4. [Docker Compose](/01-docker/compose) — 多容器编排
5. [k8s 是什么](/02-k8s-arch/overview) — 集群全貌
6. [kubectl 命令行](/02-k8s-arch/kubectl) — 最常用
7. [Pod 最小单元](/03-k8s-workload/pod) — 核心抽象

**目标**：能 run 一个 docker container + kubectl get pods。

## 🛤️ 路径 2：后端 / DevOps 入门（2-3 周）

适合**想把服务容器化**或**管理 k8s 集群**。

- 完成"新手"路径
- [Docker 网络](/01-docker/network) — bridge / host
- [Docker 存储 / 卷](/01-docker/volume) — bind mount / volume
- [k8s 架构](/02-k8s-arch/control-plane) — 控制面 / 工作节点
- [Deployment](/03-k8s-workload/deployment) — 无状态应用
- [Service 三种类型](/04-k8s-service/service) — ClusterIP / NodePort / LoadBalancer
- [ConfigMap / Secret](/05-k8s-storage/configmap-secret) — 配置管理
- [PV / PVC](/05-k8s-storage/pv-pvc) — 持久化
- [Helm Chart](/06-helm/chart) — 包管理

**目标**：能 docker-compose 起多服务；能 kubectl apply 上 k8s。

## 🛤️ 路径 3：SRE / 平台工程师（4-5 周）

适合**做生产集群 / 平台**。

- 完成"后端"路径
- [Ingress 入口](/04-k8s-service/ingress) — 七层路由
- [NetworkPolicy](/04-k8s-service/network-policy) — 东西向隔离
- [StorageClass / CSI](/05-k8s-storage/storageclass) — 动态供给
- [Helm template / values](/06-helm/template) — 自定义 chart
- [Prometheus](/07-observability/prometheus) — 指标采集
- [Grafana 仪表板](/07-observability/grafana) — 可视化
- [Loki 日志聚合](/07-observability/loki) — 集中日志
- [Alertmanager](/07-observability/alertmanager) — 告警
- [Istio 核心](/08-service-mesh/istio) — 流量治理
- [ArgoCD](/09-cicd/argocd) — GitOps 部署
- [RBAC](/11-security/rbac) — 权限管理

**目标**：能搭建生产集群 + 监控 + 告警 + 持续部署。

## 🛤️ 路径 4：Service Mesh / 云原生架构（4 周）

适合**做微服务 / Service Mesh / 安全**。

- 完成"SRE"路径
- [Sidecar 模式](/08-service-mesh/sidecar) — Envoy 注入
- [流量管理](/08-service-mesh/traffic) — 金丝雀 / 蓝绿
- [GitOps 思想](/09-cicd/gitops)
- [Tekton / JenkinsX](/09-cicd/tekton) — 流水线
- [Terraform](/10-iac/terraform) — 基础设施
- [Helmfile / Kustomize](/10-iac/helmfile) — 渐进式发布
- [Secret 管理](/11-security/secret) — Vault 集成
- [NetworkPolicy + PodSecurity](/11-security/policy) — 纵深防御
- [Falco 运行时检测](/11-security/falco) — 异常行为

**目标**：能设计云原生架构、落地 Service Mesh、安全审计。

## 🛤️ 路径 5：Serverless 实践（1-2 周）

适合**想用 Knative / 云函数**。

- 完成"后端"路径
- [Knative Serving](/12-serverless/knative) — k8s 上的 FaaS
- [Lambda / Cloud Run](/12-serverless/managed) — 托管 Serverless

**目标**：能在 k8s 上跑 Serverless workload。

## 🛤️ 路径 6：面试冲刺（4 周）

适合**1-3 个月要面试云原生岗**。

- 复习 [kubectl 命令行](/02-k8s-arch/kubectl)
- 复习 [Pod / Deployment / Service](/03-k8s-workload/pod)
- 复习 [Helm Chart](/06-helm/chart) + [Ingress](/04-k8s-service/ingress)
- [kubectl debug](/13-troubleshooting/debug) — 排错套路
- [Pod 卡死](/13-troubleshooting/pod-trouble) — 常见 case
- [网络 / DNS 排错](/13-troubleshooting/network)
- [CKA 考试要点](/14-interview/cka) — 必看
- [CKS 安全加固](/14-interview/cks) — 进阶
- [高频面试题](/14-interview/questions) — 真实题

## 🎯 速查卡片

| 我想 | 推荐先看 |
|------|---------|
| 入门容器 | [Docker 基础](/01-docker/intro) → [Docker Compose](/01-docker/compose) |
| 学 k8s | [k8s 架构](/02-k8s-arch/overview) → [Pod](/03-k8s-workload/pod) |
| 上线应用 | [Deployment](/03-k8s-workload/deployment) → [Service](/04-k8s-service/service) |
| 域名访问 | [Ingress](/04-k8s-service/ingress) |
| 用 Helm | [Chart 结构](/06-helm/chart) |
| 监控 | [Prometheus](/07-observability/prometheus) → [Grafana](/07-observability/grafana) |
| 部署流水线 | [GitOps](/09-cicd/gitops) → [ArgoCD](/09-cicd/argocd) |
| 排查故障 | [kubectl debug](/13-troubleshooting/debug) |
| 找云原生工作 | [CKA 考试要点](/14-interview/cka) |
