---
title: 控制面 Control Plane
date: 2026-08-15  # date-auto-injected
---

# 控制面 Control Plane

> k8s 集群的"大脑" — 接收请求、调度、维护期望状态。

![K8S Scheduler Framework](/k8s-scheduler-framework.svg)

## 🧠 三大核心组件

### 1. kube-apiserver

**所有交互的唯一入口**。

```bash
# 内部：组件间都走 API Server
# 外部：kubectl / dashboard / Operator 都调它

# API Server 提供：
# - REST API（kubectl / API 调用）
# - 鉴权 + 准入控制
# - 状态机（更新 etcd）
```

特点：
- **无状态**（可水平扩）
- **唯一与 etcd 通讯的组件**
- **所有 list/watch 都走它**

### 2. kube-scheduler

**决定 Pod 放哪个 Node**。

```yaml
# 调度过程：
# 1. 过滤：排除不满足条件的 Node（资源 / 端口 / 选择器）
# 2. 打分：剩余 Node 按多个维度评分
#    - LeastRequestedPriority（资源空闲多）
#    - BalancedResourceAllocation（CPU/内存均衡）
#    - NodeAffinity / PodAffinity
#    - Taints / Tolerations
#    - 拓扑分布
# 3. 选最高分
```

自定义调度器也可（Volcano / scheduler-plugins）。

### 3. kube-controller-manager

**状态控制循环**。

```bash
# 各种 Controller 一起跑
# - Deployment Controller：维持 replicas
# - StatefulSet Controller：维持有序副本
# - Node Controller：监测 Node 健康
# - Service Account Controller
# - Endpoints Controller
# - Job / CronJob Controller
# - 各种云厂商 Controller（AWS / GCP / Azure）
```

每个 Controller 的核心循环：
```
期望状态 (spec) vs 实际状态 (status)
如果不符 → 调 API 修复
```

## 🗃️ etcd

**集群状态**存储。

```bash
# 看 etcd
etcdctl endpoint status \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# 备份
ETCDCTL_API=3 etcdctl snapshot save /tmp/snap.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=... --cert=... --key=...

# 恢复
ETCDCTL_API=3 etcdctl snapshot restore /tmp/snap.db
```

特点：
- 强一致性（RAFT）
- KV 存储
- 监听：apiserver 监听变化 → 通知 Controller / Scheduler

![K8S Crd Extension](/k8s-crd-extension.svg)

## 🔌 cloud-controller-manager

云厂商专用组件（AWS / GCP / Azure）：
- Node Lifecycle（云上节点增删）
- LoadBalancer Service（云 LB 集成）
- Route（路由表）
- 持久化卷

裸机集群不需要。

## 🪛 高可用控制面

```
生产建议：控制面 3 节点起步

   Master1            Master2            Master3
┌──────────┐       ┌──────────┐       ┌──────────┐
│ apiserver │       │ apiserver │       │ apiserver │
│ sched    │       │ sched    │       │ sched    │
│ c-m      │       │ c-m      │       │ c-m      │
└─────┬────┘       └─────┬────┘       └─────┬────┘
      └──────────┬──────────┴──────────┬──────┘
                 ┌───▼────────────────┐
                 │  etcd 集群（3节点）  │
                 └────────────────────┘
```

| 数量 | 容错 | 适合 |
|------|------|------|
| 1 | 0 | 测试 |
| 3 | 1 节点 | 小生产 |
| 5 | 2 节点 | 大生产 |

## 🔧 调试

```bash
# 看 API Server 日志
journalctl -u kube-apiserver -f
# 或（k0s/k3s/microk8s）
k0s kubectl logs --follow kube-apiserver

# 看 API Server 状态
kubectl get --raw='/healthz'
kubectl get --raw='/readyz'

# 看 etcd 集群
etcdctl member list

# 自定义资源（CRD）状态
kubectl get crd
kubectl describe crd <name>
```

## 🛠 实战

### 自建控制面（k0s / k3s）

```bash
# k3s（单二进制）
curl -sfL https://get.k3s.io | sh -

# 启动后
k3s kubectl get nodes
# 看到 master 节点 Ready
```

### 加新 Master

```bash
# kubeadm
kubeadm join <control-plane-endpoint>:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --control-plane
```

## 🆚 托管服务

不想自己运维控制面？

| 服务 | 提供方 |
|------|--------|
| EKS | AWS |
| GKE | Google Cloud |
| AKS | Azure |
| ACK | 阿里云 |
| TKE | 腾讯云 |
| DOKS | DigitalOcean |
| Linode K8s | Linode |

**生产推荐**：用托管，省心。

## 🔗 下一步

- [k8s 是什么](/02-k8s-arch/overview)
- [工作节点 Node](/02-k8s-arch/node)
- [etcd 存储](/02-k8s-arch/etcd)
- [kubectl 命令行](/02-k8s-arch/kubectl)