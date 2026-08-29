---
title: CKA 考试要点
date: 2026-08-15  # date-auto-injected
---

# CKA 考试要点

> **C**ertified **K**ubernetes **A**dministrator = CNCF 官方 k8s 管理员认证。

## 📋 考试信息

| 项 | 详情 |
|----|------|
| 主办 | CNCF + Linux Foundation |
| 时长 | 2 小时 |
| 题目 | 15-20 道实操 |
| 费用 | ~$395（含一次重考） |
| 通过 | 66% |
| 形式 | 在线 PSI Bridge / 线下考试中心 |
| 有效期 | 2 年（之后续证） |
| 资源 | killercoda / killer.sh 模拟环境 |

## 🎯 考试范围（22% × 5 块）

| 比重 | 主题 |
|------|------|
| **25%** | 集群架构 / 安装 / 配置 |
| **15%** | 工作负载 / Scheduling |
| **20%** | Service / Networking |
| **10%** | 存储 |
| **30%** | 排错 |

## 🔥 高频考点

### 1. etcd 备份 / 恢复

```bash
ETCDCTL_API=3 etcdctl snapshot save /tmp/snap.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

ETCDCTL_API=3 etcdctl snapshot restore /tmp/snap.db \
  --data-dir=/var/lib/etcd-restore
```

### 2. 静态 Pod 改回 kubeadm managed

```bash
# 改 /etc/kubernetes/manifests/kube-apiserver.yaml
# 加 --service-account-issuer / --service-account-signing-key-file
# 用 kubeadm 重生成
kubeadm init phase control-plane all
```

### 3. Pod 调度

```bash
# 节点选择
nodeSelector:
  disktype: ssd
# 亲和
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        topologyKey: kubernetes.io/hostname
        labelSelector:
          matchLabels:
            app: web
# 污点容忍
tolerations:
- key: "dedicated"
  operator: "Equal"
  value: "gpu"
  effect: "NoSchedule"
```

### 4. RBAC 速写

```bash
# 创建 SA + Role + RoleBinding 一条命令
kubectl create serviceaccount my-sa -n prod
kubectl create rolebinding my-sa-edit \
  --clusterrole=edit \
  --serviceaccount=prod:my-sa
```

### 5. Service + Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
```

### 6. NetworkPolicy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-db
spec:
  podSelector:
    matchLabels: { app: db }
  policyTypes: [IngressPolicy]
  ingress:
  - from:
    - podSelector: { matchLabels: { app: frontend } }
    ports: [{ port: 5432 }]
```

### 7. 部署 / 升级 / 回滚

```bash
kubectl set image deploy/web web=myapp:2.0
kubectl rollout status deploy/web
kubectl rollout undo deploy/web
kubectl rollout history deploy/web
```

### 8. 排错

```bash
# Pod Pending
kubectl describe pod <name> | grep -A 5 Events
# 通常：资源 / nodeSelector / taints / PVC

# CrashLoopBackOff
kubectl logs <pod> --previous
# 通常：应用启动失败

# Network 不通
kubectl exec -it <pod> -- nslookup kubernetes
# 进 debug 容器测
kubectl debug -it <pod> --image=nicolaka/netshoot

# 节点 NotReady
kubectl describe node <node>
journalctl -u kubelet -f
```

### 9. 存储

```bash
# PVC 改大
kubectl edit pvc data
# 改 spec.resources.requests.storage

# StorageClass
kubectl get sc
kubectl get pvc
# 排错：kubectl describe pvc
```

### 10. 维护 / 升级

```bash
# 排空节点
kubectl drain node1 --ignore-daemonsets --delete-emptydir-data
# 升级 kubeadm
kubeadm upgrade plan
kubeadm upgrade apply v1.29.0
# 升级 kubelet
apt-get install -y kubelet=1.29.0-00
```

## 🪜 速记要点

| 主题 | 关键命令 |
|------|----------|
| Pod 调度 | nodeSelector / affinity / toleration |
| RBAC | ClusterRole / RoleBinding |
| 存储 | PV / PVC / StorageClass |
| 网络 | Service / Ingress / NetworkPolicy |
| 升级 | drain / upgrade / cordon / uncordon |
| 备份 | etcd snapshot / restore |
| 排错 | describe / logs --previous / debug |

## 🛠 实战训练

### 免费模拟环境

- **killercoda.com** — 直接浏览器跑 k8s 集群
- **labs.play-with-k8s.com** — 4 小时临时集群
- **kodekloud.com** — 系统课 + 模拟

### 付费

- **killer.sh** — CKA 官方合作伙伴，$29 模拟
- **Mumshad** (Udemy) — 视频课
- **KodeKloud CKA course** — 最受欢迎

### 节奏

```
前 2 周：刷完 kk8s.io 文档 + Udemy 视频
第 3 周：killer.sh 模拟 5+ 次（错题重做）
第 4 周：killercoda + 计时练习（每题 < 6 分钟）
考前：再刷 2 套 killer.sh
```

## 🎯 实战

```bash
# 装单节点集群练手（kind / minikube）
kind create cluster --config kind.yaml

# 看所有考点
kubectl get all -A
# 练习每个考点 5 遍
```

## 🩹 考场注意

```
1. 切上下文（kubectl config use-context）
2. 看时间分配（每题 ≤ 7 分钟）
3. 不确定的先跳过做记号
4. 仔细看题（每题多读一遍）
5. 验证结果（kubectl get 看是否对）
6. 用 --dry-run 测命令
7. 用 YAML 改比 edit 更稳
```

## 🔗 下一步

- [CKS 安全加固](/14-interview/cks)
- [高频面试题](/14-interview/questions)
- [k8s 是什么](/02-k8s-arch/overview)