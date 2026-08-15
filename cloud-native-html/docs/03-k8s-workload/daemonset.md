---
title: DaemonSet
---

# DaemonSet - 每个 Node 一个 Pod

> DaemonSet = 确保**所有 / 部分 Node 都跑一个 Pod**。典型：日志、监控、网络插件。

## 🤔 典型场景

```
✅ 节点日志收集：Fluentd / Filebeat
✅ 节点监控：node-exporter / Datadog agent
✅ 网络插件：CNI 插件（Calico / Cilium）
✅ 存储插件：ceph / glusterd
✅ 安全：falco / trivy
```

## 📜 manifest

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
  namespace: monitoring
spec:
  selector:
    matchLabels:
      app: node-exporter
  template:
    metadata:
      labels:
        app: node-exporter
    spec:
      # 关键：能跑在系统命名空间
      hostNetwork: true                # 用宿主机网络
      hostPID: true                    # 用宿主机 PID（看进程）
      containers:
      - name: node-exporter
        image: prom/node-exporter:v1.7.0
        ports:
        - containerPort: 9100
          hostPort: 9100              # 宿主机也可访问
        volumeMounts:
        - name: proc
          mountPath: /host/proc
          readOnly: true
        - name: sys
          mountPath: /host/sys
          readOnly: true
      volumes:
      - name: proc
        hostPath:
          path: /proc
      - name: sys
        hostPath:
          path: /sys
      tolerations:
      - effect: NoSchedule           # 容忍 master 污点
        operator: Exists
```

## 🔧 关键字段

| 字段 | 用途 |
|------|------|
| `hostNetwork: true` | 共享宿主机网络命名空间 |
| `hostPID: true` | 共享 PID 命名空间 |
| `hostPort` | 宿主机端口直接暴露 |
| `hostPath` | 挂载宿主机目录 |
| `tolerations` | 容忍 master / 特殊节点污点 |
| `nodeSelector` | 限定 Node（如 only GPU） |

## 📜 高频命令

```bash
# 看
kubectl get ds
kubectl get pods -l app=node-exporter -o wide

# 升级镜像
kubectl set image ds/node-exporter node-exporter=prom/node-exporter:v1.8.0

# 删 node-exporter → 新 Node 自动起
kubectl delete pod node-exporter-abcde -n monitoring
```

## 🆚 vs Deployment

| | DaemonSet | Deployment |
|--|-----------|-------------|
| 副本数 | = Node 数 | replicas: N（自己定） |
| 调度 | 每个 Node 一个 | Scheduler 决定 |
| 适合 | 节点级（监控 / 日志） | 应用 |
| 副本数变化 | 增 Node 自动 +1 | 手动 scale |

## 🪛 实战：装日志收集

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: filebeat
  namespace: kube-system
spec:
  selector:
    matchLabels:
      app: filebeat
  template:
    metadata:
      labels:
        app: filebeat
    spec:
      hostNetwork: true
      containers:
      - name: filebeat
        image: elastic/filebeat:8.11
        args: ["filebeat", "-e", "--strict.perms=false"]
        env:
        - name: ELASTICSEARCH_HOST
          value: elastic.logging.example.com
        volumeMounts:
        - name: varlog
          mountPath: /var/log
          readOnly: true
        - name: dockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: varlibdocker
          mountPath: /var/lib/docker
          readOnly: true
      volumes:
      - name: varlog
        hostPath: { path: /var/log }
      - name: dockercontainers
        hostPath: { path: /var/lib/docker/containers }
      - name: varlibdocker
        hostPath: { path: /var/lib/docker }
      tolerations:
      - effect: NoSchedule
        operator: Exists
```

## 🩹 故障

```bash
# 部分 Node 没起
kubectl get ds
# DESIRED  CURRENT  READY  UP-TO-DATE  AVAILABLE  NODE SELECTOR
# 6         6        4      6           4          <none>
# 4 ready / 6 desired → 2 个 Node 没起

# 看为什么
kubectl describe pod filebeat-xxxx
# 通常：toleration 不够 / 资源满 / 镜像拉不下来
```

## 🔗 下一步

- [Pod 最小单元](/03-k8s-workload/pod)
- [Deployment](/03-k8s-workload/deployment)
- [Job / CronJob](/03-k8s-workload/job)