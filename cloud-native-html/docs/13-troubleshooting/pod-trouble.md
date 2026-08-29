---
title: Pod 卡死 / 排错套路
---

# Pod 卡死 / 排错套路

> 90% 的生产问题都能用一套固定套路定位。

## 🧭 排错流程（黄金圈）

```
1. 看状态 — kubectl get pods -A
2. 看事件 — kubectl describe pod
3. 看日志 — kubectl logs --previous
4. 看资源 — kubectl describe node
5. 进 Pod — kubectl debug
6. 找上游 — 看 Service / Endpoints
7. 找依赖 — DNS / 网络 / 配置
8. 找进程 — crictl / 节点工具
```

## 📊 状态解读

```bash
kubectl get pods -A
# NAME                  READY  STATUS              RESTARTS  AGE
# myapp-abc-123         1/1    Running            0         10m
# myapp-abc-124         0/1    Pending            0         5m
# myapp-abc-125         0/1    ContainerCreating 0         30s
# myapp-abc-126         0/1    CrashLoopBackOff  3         2m
# myapp-abc-127         0/1    ImagePullBackOff  0         1m
# myapp-abc-128         0/1    Error              0         30s
# myapp-abc-129         1/1    Terminating      0         1m
```

| 状态 | 含义 |
|------|------|
| `Running` | 至少一个容器跑着 ✅ |
| `Pending` | 没调度到 Node（资源 / 选择器 / 镜像） |
| `ContainerCreating` | 在拉镜像 / 挂卷 |
| `CrashLoopBackOff` | 容器反复崩 |
| `ImagePullBackOff` | 拉镜像失败 |
| `Error` | 启动失败 |
| `Terminating` | 收尾中 |

## 🔍 第一步：describe（最有用！）

```bash
kubectl describe pod myapp-abc-125
```

看 **Events**（最关键）：

```
Events:
  Type     Reason     Age   From               Message
  ----     ------     ----  ----               -------
  Warning  FailedScheduling  5m  default-scheduler  0/3 nodes are available
  Warning  FailedScheduling  5m  default-scheduler  pod has unmet immediate PVC claims
  Normal   Scheduled   5m  default-scheduler  Successfully assigned myapp-abc-125 to node2
  Normal   Pulling    4m   kubelet            Pulling image "myapp:1.0"
  Warning  Failed      30s  kubelet            Failed to pull image "myapp:1.0":
                                                       rpc error: code = NotFound desc = ...
  Warning  Failed      30s  kubelet            Error: ErrImagePull
```

## 🐛 卡 Pending 怎么办

```bash
# 0. 节点资源
kubectl describe node | grep -A 5 "Allocated resources"

# 1. 镜像存在吗
docker manifest inspect myapp:1.0

# 2. PVC bound 了吗
kubectl get pvc
kubectl describe pvc data

# 3. nodeSelector 匹配吗
kubectl describe node <node> | grep Labels

# 4. taint 拒绝吗
kubectl describe node <node> | grep Taints
# 需要 toleration 匹配
```

## 💥 CrashLoopBackOff 排查套路

```bash
# 1. 看上次实例日志（已崩的那个）
kubectl logs myapp-abc-125 --previous
# 通常：启动失败 / 配置错 / 健康检查不过

# 2. 看启动命令 / 镜像
kubectl get pod myapp-abc-125 -o yaml | grep -A 5 containers

# 3. 看 Events
kubectl describe pod myapp-abc-125

# 4. 改 image 跑 bash 验证
kubectl run debug --image=myapp:1.0 --rm -it -- bash
# 看启动错误

# 5. 临时改 liveness
# 把 readinessProbe / livenessProbe 去掉
```

## 🔁 容器"假死"（running 但不服务）

```bash
# 1. 看 Endpoints（背后有 Pod 吗）
kubectl get endpoints myapp
# 空 → selector 错 / Pod 没匹配

# 2. readinessProbe 不过 → 流量没过来
kubectl describe pod myapp-xxx | grep -A 5 Readiness
kubectl logs myapp-xxx

# 3. 进 Pod
kubectl debug -it myapp-xxx --image=nicolaka/netshoot

# 4. 看 socket
ss -tlnp                  # 监听端口对吗
curl localhost:8080/health
```

## 📉 OOMKilled

```bash
# 状态显示 OOMKilled
kubectl describe pod myapp-xxx
# Last State: Terminated, Reason: OOMKilled

# 解决：
# 1. 提高 limits.memory
# 2. 找内存泄漏（heap dump / pprof）
# 3. 用 jvm -Xmx / node --max-old-space-size 限制应用
```

## ⏳ 长时 Pending 调度失败

```bash
kubectl describe pod myapp-xxx
# Events: Warning FailedScheduling
#   0/3 nodes are available: 3 Insufficient memory.

# 解决：
# 1. 减小 request
# 2. 加 Node
# 3. 容忍某些 Node
```

## 🪜 Node 失联 / NotReady

```bash
kubectl get nodes
# node2    NotReady   ...   v1.28.0

# 1. 看 Node 详情
kubectl describe node node2

# 2. 看 kubelet 日志（要 SSH 到 Node）
journalctl -u kubelet -f

# 3. 资源？
df -h
free -h
top

# 4. 强制删除 NotReady Node（小心）
kubectl delete node node2
# Pod 自动迁走（短暂 disruption）
```

## 🩹 Pod 卡在 ContainerCreating

```bash
# 通常：拉镜像慢 / 失败 / 卷挂不上
kubectl describe pod myapp-xxx

# 看：
# - ImagePullBackOff → 镜像名错 / 私有仓库密钥
# - FailedMount → PVC 还在 Pending / StorageClass 错
# - FailedScheduling → Node 资源满
```

## 🧰 终极套路

```bash
# 1. 列所有"不健康"Pod
kubectl get pods -A --field-selector=status.phase!=Running

# 2. 看集群事件
kubectl get events -A --sort-by=.lastTimestamp | tail -30

# 3. 看 kube-system
kubectl get pods -n kube-system
kubectl get pods -n kube-public

# 4. 看 Node 资源
kubectl describe nodes | grep -A 5 "Allocated resources"

# 5. 看 controller 日志
kubectl -n kube-system logs -l component=kube-controller-manager
```

## 🛠 实战

```bash
# 通用排查脚本
#!/bin/bash
POD=$1
NS=${2:-default}

echo "=== Pod status ==="
kubectl get pod $POD -n $NS

echo "=== Events ==="
kubectl describe pod $POD -n $NS | tail -20

echo "=== Current logs ==="
kubectl logs $POD -n $NS --tail 50

echo "=== Previous logs (if crashed) ==="
kubectl logs $POD -n $NS --previous --tail 50 2>/dev/null

echo "=== Endpoints ==="
kubectl get endpoints -n $NS

echo "=== Service ==="
kubectl get svc -n $NS
```

## 🔗 下一步

- [kubectl debug](/13-troubleshooting/debug)
- [网络 / DNS 排错](/13-troubleshooting/network)
- [k8s 是什么](/02-k8s-arch/overview)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud](https://java-px.bot.cd/cloud/):Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/):Linux 内核基础
- [devops](https://java-px.bot.cd/devops/):DevOps 流程
