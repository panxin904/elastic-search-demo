---
title: Pod 最小单元
date: 2026-08-15  # date-auto-injected
---

# Pod - k8s 最小调度单位

> Pod = 1+ 共享网络 / 存储的容器。**不是容器**。

![Kubernetes Scheduler 调度流程](/k8s-scheduler-flow.svg)

## 🤔 为什么需要 Pod

```
单容器：直接 docker run
多容器（紧密耦合）：
  - 主应用 + 日志收集
  - Web + 边车代理
  - 应用 + init 容器

Pod = "逻辑主机"，多个容器共享：
  - 网络命名空间（同一 IP / 端口）
  - 存储卷
  - 生命周期
```

## 📜 最小 Pod manifest

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: hello
  labels:
    app: hello
spec:
  containers:
  - name: hello
    image: nginx:alpine
    ports:
    - containerPort: 80
```

## 🧬 Pod 生命周期

```
Pending     → 容器还没起来
ContainerCreating
Running      → 至少一个容器运行
Succeeded    → 全部成功退出（Job）
Failed       → 至少一个失败
Unknown      → apiserver 失联

CrashLoopBackOff    容器反复崩溃（最常见）
ImagePullBackOff    镜像拉不下来
Pending              调度不到 Node
```

## 🏗️ Pod 内容

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  namespace: default
  labels:
    app: myapp
    env: prod
spec:
  # Node 选择
  nodeSelector:
    disktype: ssd
  
  # 节点名（一般不指定）
  # nodeName: node1

  # 初始化容器
  initContainers:
  - name: init-db
    image: busybox
    command: ['sh', '-c', 'until nslookup db; do sleep 1; done']

  # 主容器
  containers:
  - name: app
    image: myapp:1.0
    ports:
    - containerPort: 8080
    env:
    - name: DB_HOST
      value: db
    envFrom:
    - configMapRef:
        name: app-config
    - secretRef:
        name: app-secret
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        cpu: 500m
        memory: 256Mi
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
    volumeMounts:
    - name: data
      mountPath: /var/lib/app
    securityContext:
      runAsNonRoot: true
      readOnlyRootFilesystem: true

  # 卷
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: app-data

  # 重启
  restartPolicy: Always             # Deployment 一定是 Always
  # restartPolicy: OnFailure       # Job
  # restartPolicy: Never            # 不重启
```

## 🔍 看 Pod

```bash
kubectl get pod
kubectl get pod -o wide
kubectl get pod -o yaml
kubectl describe pod <name>     # 看 Events（重要！）

# 容器日志
kubectl logs <pod>
kubectl logs -f <pod>
kubectl logs <pod> -c <container>
kubectl logs <pod> --previous    # 上一个实例
```

![K8S Probe Lifecycle](/k8s-probe-lifecycle.svg)

## 🚦 健康检查

### livenessProbe（活着没）

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30      # 启动后等多久开始探
  periodSeconds: 10           # 探活间隔
  timeoutSeconds: 1
  failureThreshold: 3          # 连续失败 3 次重启
  successThreshold: 1
```

### readinessProbe（准备好接流量没）

```yaml
readinessProbe:
  exec:
    command: ['sh', '-c', 'test -f /tmp/ready']
  initialDelaySeconds: 5
  periodSeconds: 5
```

### startupProbe（启动慢的应用）

```yaml
startupProbe:
  httpGet:
    path: /health
    port: 8080
  failureThreshold: 30        # 30 次 × 10s = 5min 内必须 ready
  periodSeconds: 10
```

不通过 startup → liveness / readiness 不跑（避免启动慢被误杀）。

## 💾 资源限制

```yaml
resources:
  requests:
    cpu: 100m       # 0.1 核（保证）
    memory: 128Mi
  limits:
    cpu: 500m       # 最多 0.5 核（超了 throttle）
    memory: 256Mi   # 最多 256MB（超了 OOM kill）
```

| 资源 | 单位 | 超过后果 |
|------|------|----------|
| CPU | 1 = 1 核 | throttle（不杀） |
| memory | 字节 | OOM kill |

**始终设 requests**，否则 Pod 可能调度到无法承载的 Node。

## 🪜 Pod 调度

```yaml
spec:
  # 节点选择
  nodeSelector:
    disktype: ssd
  
  # 亲和 / 反亲和
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values: [ssd]
  
  # 污点容忍
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "gpu"
    effect: "NoSchedule"
  
  # 拓扑分布
  topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: kubernetes.io/hostname
    whenUnsatisfiable: DoNotSchedule
    labelSelector:
      matchLabels:
        app: myapp
```

## 🩺 故障排查

```bash
# Pod 卡 Pending
kubectl describe pod <name> | grep Events
# 通常：资源不足 / nodeSelector 没匹配 / PVC 没 bound

# Pod CrashLoopBackOff
kubectl logs <pod> --previous
# 通常：应用启动失败 / 配置错 / 镜像错

# Pod ImagePullBackOff
kubectl describe pod <name>
# 通常：镜像名错 / 私有仓库没配 secret

# 进 Pod
kubectl exec -it <pod> -- bash
# 没 bash / sh 的话
kubectl exec -it <pod> -- sh
# alpine 镜像默认 sh
```

## 🛠 实战

```bash
# 跑一个
kubectl run myapp --image=myapp:1.0 --port=8080

# 看
kubectl get pod myapp
kubectl get pod myapp -o wide
kubectl describe pod myapp

# 排错
kubectl logs myapp --tail 100
kubectl exec -it myapp -- bash

# 删
kubectl delete pod myapp
```

## 🔗 下一步

- [k8s 是什么](/02-k8s-arch/overview)
- [Deployment](/03-k8s-workload/deployment)
- [StatefulSet](/03-k8s-workload/statefulset)
- [排错](/13-troubleshooting/pod-trouble)