---
title: 工作节点 Node
date: 2026-08-15  # date-auto-injected
---

# 工作节点 Node

> Node = 跑 Pod 的机器。k8s 集群里除控制面外都是 Node。

## 🧬 节点架构

```
┌────────────────────────────────────┐
│                Node                 │
│  ┌────────────────────────────┐    │
│  │  kubelet                    │    │
│  │  - 接收 Pod spec            │    │
│  │  - 通过 CRI 启动容器        │    │
│  │  - 健康检查                 │    │
│  │  - 报告 Pod 状态            │    │
│  └────────────────────────────┘    │
│  ┌────────────────────────────┐    │
│  │  kube-proxy                 │    │
│  │  - Service IP 转发         │    │
│  │  - iptables / IPVS          │    │
│  └────────────────────────────┘    │
│  ┌────────────────────────────┐    │
│  │  容器运行时 (CRI)            │    │
│  │  - containerd / CRI-O       │    │
│  │  - 启动 / 停止 / 监控容器   │    │
│  └────────────────────────────┘    │
│  ┌────────────────────────────┐    │
│  │  Pods                       │    │
│  │  ┌──────┐  ┌──────┐  ┌────┐ │    │
│  │  │  c1  │  │  c2  │  │... │ │    │
│  │  └──────┘  └──────┘  └────┘ │    │
│  └────────────────────────────┘    │
└────────────────────────────────────┘
```

![Kubernetes CNI / CSI / CRI 插件体系](/k8s-cni-csi-cri.svg)

## 🛠 kubelet

**Node 代理**，k8s 在每个 Node 上的"客户端"。

职责：
- 接收 API Server 的 Pod spec
- 通过 CRI（Container Runtime Interface）启动容器
- 挂载卷
- 健康检查（liveness / readiness）
- 报告 Pod / Node 状态

```bash
journalctl -u kubelet -f           # 看日志
```

## 🌐 kube-proxy

**Service IP 转发**（不是七层代理，是 iptables / IPVS 模式）。

| 模式 | 实现 |
|------|------|
| iptables | 默认（Linux 通用） |
| IPVS | 更快（基于 hash 表） |
| userspace | 老模式（已不推荐） |

```bash
# 看模式
kubectl -n kube-system logs kube-proxy-<pod>
# 或
curl localhost:10249/mode

# 改模式（kubeadm 集群）
kubectl -n kube-system edit cm kube-proxy
# mode: ipvs
kubectl -n kube-system delete pod -l k8s-app=kube-proxy
```

## 🏃 容器运行时（CRI）

```bash
# 看当前
kubectl get nodes -o wide
# CONTAINER-RUNTIME 列

# 主流
# - containerd（最常见）
# - CRI-O（Red Hat 主导）
# - Docker（v1.24 之后已不直接支持，要 dockershim）
```

```bash
# containerd 调试
ctr -n k8s.io containers ls
crictl ps
crictl logs <container>
crictl exec -it <container> sh
```

## 📦 Pod 是什么

**Pod = 1+ 共享网络 / 存储的容器**：

- 共享 network namespace（同一 IP + 端口空间）
- 共享 volume
- 共享 lifecycle（同启同停）

## 🏷️ 节点信息

```bash
kubectl get nodes
# NAME           STATUS   ROLES    AGE   VERSION
# node1          Ready    <none>   10d   v1.28.0
# node2          Ready    <none>   10d   v1.28.0

kubectl get nodes -o wide
# 看 IP / OS / 内核 / 运行时

kubectl describe node node1
# 资源 / 污点 / 标签 / Pod 列表
```

## 🏷️ 标签 / 污点

### Labels（K-V 标签）

```bash
# 给 Node 加 label
kubectl label node node1 role=worker
kubectl label node node2 role=worker
kubectl label node node1 env=prod

# 调度时指定
spec:
  nodeSelector:
    role: worker
```

### Taints（污点）+ Tolerations（容忍）

```bash
# Node 加污点（不允许调度，除非 Pod 容忍）
kubectl taint nodes node1 key=value:NoSchedule
# 三种效应：
# NoSchedule     硬不调度
# PreferNoSchedule 软不调度
# NoExecute     已运行的也驱逐

# Pod 容忍
tolerations:
- key: "key"
  operator: "Equal"
  value: "value"
  effect: "NoSchedule"
```

## 🔧 节点维护

```bash
# 标记不可调度
kubectl cordon node1

# 排空 Pod（驱逐）
kubectl drain node1 --ignore-daemonsets

# 排空 + 删除 local 数据
kubectl drain node1 --ignore-daemonsets --delete-emptydir-data

# 恢复
kubectl uncordon node1
```

## 📊 节点资源

```bash
# 实时
kubectl top node

# 详细
kubectl describe node node1 | grep -A 5 "Allocated resources"

# Capacity / Allocatable
# CPU: 8 (4 allocatable)
# Memory: 16Gi (12Gi allocatable)
```

## 🩹 节点故障

```bash
# Node NotReady
kubectl describe node node1
journalctl -u kubelet -f

# 常见原因
# - kubelet 停了
# - 容器运行时挂了
# - 网络断了
# - 磁盘满
# - 资源耗尽

# 强制下线（清空状态）
kubectl delete node node1
# Node 会从 etcd 删除（pod 自动重新调度到其他 Node）
```

## 🛠 实战

```bash
# 加 Node（kubeadm）
# Master 上获取 token
kubeadm token create --print-join-command

# 新 Node 上跑
kubeadm join <api-server>:6443 --token xxx --discovery-token-ca-cert-hash sha256:xxx

# 看集群
kubectl get nodes
kubectl get nodes -o yaml | grep -A 5 addresses
```

## 🔗 下一步

- [k8s 是什么](/02-k8s-arch/overview)
- [控制面 Control Plane](/02-k8s-arch/control-plane)
- [kubectl 命令行](/02-k8s-arch/kubectl)
- [Pod 最小单元](/03-k8s-workload/pod)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud](https://java-px.bot.cd/cloud/):Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/):Linux 内核基础
- [devops](https://java-px.bot.cd/devops/):DevOps 流程
