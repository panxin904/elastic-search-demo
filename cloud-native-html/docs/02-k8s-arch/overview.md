---
title: k8s 是什么
date: 2026-08-15  # date-auto-injected
---

![Kubernetes 集群架构](/kubernetes-architecture.svg)

# Kubernetes 是什么

> **K8s** = 自动部署、扩缩、运维容器化应用的**容器编排平台**。Google 2014 年开源，源自内部 Borg。

## 🤔 为什么需要 k8s

```
单容器时代：
  Docker run → 进程挂了手动启

多容器 + 多机：
  ❌ 10 台机器，每台 5 个容器 = 50 个容器手工管理
  ❌ 一台机器挂了要重新调度
  ❌ 滚动升级 / 回滚
  ❌ 服务发现 / 负载均衡
  ❌ 配置 / 密钥管理

k8s 自动化以上一切
```

## 🏗️ 集群架构

```
┌──────────────────────────────┐
│       Control Plane           │
│  ┌────────────┐ ┌──────────┐ │
│  │ API Server │ │ Scheduler │ │
│  └────────────┘ └──────────┘ │
│  ┌────────────┐ ┌──────────┐ │
│  │ Controller │ │  etcd    │ │
│  │  Manager   │ │          │ │
│  └────────────┘ └──────────┘ │
└──────────────────────────────┘
            │
    ┌───────┴────────┐
    │                │
┌───▼────┐      ┌───▼────┐
│  Node  │      │  Node  │
│ - kubelet    │ - kubelet
│ - kube-proxy │ - kube-proxy
│ - 容器运行时 │ - 容器运行时
│ - Pods   │ - Pods
└────────┘      └────────┘
```

| 组件 | 作用 |
|------|------|
| **API Server** | REST API 入口，所有组件通讯都走它 |
| **Scheduler** | 决定 Pod 放哪个 Node |
| **Controller Manager** | 状态循环（确保实际状态 = 期望状态） |
| **etcd** | 分布式 KV，存所有集群数据 |
| **kubelet** | Node 上的代理，管理 Pod 生命周期 |
| **kube-proxy** | Node 上的网络代理（Service IP） |
| **容器运行时** | containerd / CRI-O（运行容器） |

## 🔄 工作流（用户视角）

```
1. kubectl apply -f deployment.yaml
2. 请求到 API Server
3. etcd 存 spec
4. Controller Manager 看到 spec → 创建 Pod 对象
5. Scheduler 看到未调度的 Pod → 决定 Node
6. 目标 Node 的 kubelet 看到 → 调用 CRI 启动容器
7. kube-proxy 配网络（Service IP）
8. kubectl get pods 看状态 Running
```

## 🧬 核心抽象

```yaml
# Pod（最小调度单位）
apiVersion: v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  - name: myapp
    image: myapp:1.0
    ports:
    - containerPort: 8080
```

```yaml
# Deployment（Pod 的控制器）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:1.0
```

| 抽象 | 一句话 |
|------|--------|
| Pod | 1+ 共享网络 / 存储的容器组 |
| Deployment | 无状态 Pod 的控制器 |
| StatefulSet | 有状态 Pod 的控制器 |
| Service | Pod 集合的稳定入口 |
| Ingress | 七层路由（HTTP） |
| ConfigMap | 非密配置 |
| Secret | 敏感数据 |
| PVC | 持久化卷申请 |
| Namespace | 资源隔离 |

## 📦 实际工作流

```bash
# 1. 写 manifest
vim deployment.yaml

# 2. 应用
kubectl apply -f deployment.yaml

# 3. 看
kubectl get pods
kubectl get svc

# 4. 暴露
kubectl expose deploy myapp --port=80 --type=LoadBalancer
# 或写 ingress.yaml
kubectl apply -f ingress.yaml

# 5. 滚动升级
kubectl set image deploy/myapp myapp=myapp:2.0

# 6. 扩缩
kubectl scale deploy/myapp --replicas=10
```

## 🪛 适用 vs 不适用

| 适合 | 不适合 |
|------|--------|
| 微服务架构 | 单体（直接 VM 跑） |
| 高可用 / 自动恢复 | 极端延迟敏感（FPGA） |
| 混合云 / 多云 | 单语言简单应用 |
| 频繁部署 | 不需要弹性的服务 |

## 🆚 竞品

| 工具 | 风格 |
|------|------|
| **Kubernetes** | 事实标准，生态最大 |
| Docker Swarm | 简单（已边缘化） |
| Nomad (HashiCorp) | 轻量、灵活 |
| Mesos | 老牌（已少用） |

## 🔗 下一步

- [控制面 Control Plane](/02-k8s-arch/control-plane)
- [工作节点 Node](/02-k8s-arch/node)
- [kubectl 命令行](/02-k8s-arch/kubectl)
- [Pod 最小单元](/03-k8s-workload/pod)