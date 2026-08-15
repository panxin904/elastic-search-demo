---
title: Knative Serving
---

# Knative Serving - k8s 上的 Serverless

> Knative = k8s 之上的 serverless / event 层。由 Google + Pivotal + Red Hat 等发起。

## 🤔 为什么需要 Knative

```
Lambda / Cloud Run：
  ❌ 厂商锁定
  ❌ 不能本地跑

Knative Serving：
  ✅ 在 k8s 上跑（本地 / 任何云）
  ✅ 从 0 扩到 N（缩容到 0 节省资源）
  ✅ HTTP 自动路由
  ✅ 与 Eventing / GitOps 集成
```

## 🏗️ 架构

```
                [Knative Service]
                     ↓
    ┌──────────┬─────────┬──────────┐
    ↓          ↓         ↓          ↓
 [Revision] [Revision] [Revision]  ← 灰度切流量
  100%       90%       10%  (--traffic)
    ↓
 [Pod (自动扩缩容 / 缩到 0)]
```

| 资源 | 作用 |
|------|------|
| **Service (KSVC)** | 用户面向的抽象（类似 Deployment + Service） |
| **Configuration** | 最新版本的 spec |
| **Revision** | 不可变快照（每次更新） |
| **Route** | 流量切分（灰度） |
| **Ingress** | 网关（自动创建 k8s Service + Ingress） |

## 🚀 装 Knative

```bash
# 装 CLI
curl -L -o kn https://github.com/knative/client/releases/latest/download/kn-linux-amd64
chmod +x kn
sudo mv kn /usr/local/bin/

# 装 serving（用 kourier 网关）
kubectl apply -f https://github.com/knative/serving/releases/latest/download/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/latest/download/serving-core.yaml
kubectl apply -f https://github.com/knative/net-kourier/releases/latest/download/kourier.yaml
kubectl patch configmap/config-network \
  -n knative-serving \
  --type merge \
  -p '{"data":{"ingress.class":"kourier.ingress.networking.knative.dev"}}'
```

## 📜 第一个 Service

```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hello
  namespace: default
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/min-scale: "0"      # 可缩到 0
        autoscaling.knative.dev/max-scale: "10"     # 最多 10
    spec:
      containers:
      - image: gcr.io/knative-samples/helloworld-go
        ports:
        - containerPort: 8080
        env:
        - name: TARGET
          value: "Hello Knative"
```

```bash
kubectl apply -f service.yaml

# 看
kn service list hello
kn service describe hello

# 拿 URL
kn route describe hello
# URL: http://hello.default.knative.example.com

# 测试
curl http://hello.default.knative.example.com
```

## 🎛 自动扩缩

Knative 杀手特性：**从 0 自动扩**。

| 模式 | 行为 |
|------|------|
| **scale-to-zero** | 30s 无流量 → 缩到 0（节省资源） |
| **冷启动** | 有请求 → 立刻启新 Pod（< 1s 镜像小 / 预热镜像） |
| **并发** | 100 in-flight 请求 / Pod（默认） |
| **RPS** | 每秒 200 / Pod（默认） |

```yaml
spec:
  template:
    metadata:
      annotations:
        # 并发
        autoscaling.knative.dev/metric: "concurrency"
        autoscaling.knative.dev/target: "100"
        # 缩容窗口
        autoscaling.knative.dev/scale-down-delay: "30s"
        autoscaling.knative.dev/scale-to-zero-delay: "5m"
```

## 🔄 灰度发布

```bash
# 创建新版本
kn service update hello --image=gcr.io/.../helloworld:v2

# 自动建新 Revision

# 切流量（10% 给新）
kn service update hello --traffic=@latest=10,@previous=90

# 100%
kn service update hello --traffic=@latest=100
```

```yaml
# 用 yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hello
spec:
  traffic:
  - revisionName: hello-00001
    percent: 90
  - latestRevision: true
    percent: 10
```

## 🔌 事件（Knative Eventing）

```yaml
apiVersion: eventing.knative.dev/v1
kind: Broker
metadata:
  name: default
---
apiVersion: eventing.knative.dev/v1
kind: Trigger
metadata:
  name: my-trigger
spec:
  broker: default
  filter:
    attributes:
      type: com.github.pull_request.opened
  subscriber:
    ref:
      apiVersion: serving.knative.dev/v1
      kind: Service
      name: event-handler
```

- GitHub 事件
- Kafka
- Cloud Storage 事件
- 自定义 Source

## 🆚 vs 托管 Serverless

| | Knative | AWS Lambda | GCP Cloud Run | Azure Container Apps |
|--|---------|------------|---------------|----------------------|
| 跑在哪 | 你的 k8s | AWS 独占 | GCP 独占 | Azure 独占 |
| 冷启动 | 取决于镜像 | ~100ms | 极快 | 快 |
| 缩到 0 | ✅ | ✅ | ✅ | ✅ |
| 锁定 | 无 | 强 | 强 | 强 |
| 适合 | 多云 / 混合 | AWS 深度 | GCP 深度 | Azure 深度 |

## 🛠 实战

```bash
# 部署
kn service create web \
  --image=myapp:1.0 \
  --port=8080 \
  --min-scale=0 --max-scale=20 \
  --env KEY=VALUE

# 灰度
kn service update web --image myapp:2.0
kn service update web --traffic @latest=10,@previous=90

# 看
kn service list
kn service describe web
curl https://web.default.knative.example.com

# 删
kn service delete web
```

## 🩹 故障

```bash
# Pod 启不来
kubectl -n knative-serving logs -l app=controller

# 冷启动太慢
# 解决：
# 1. 用 distroless 镜像（更小）
# 2. 预热镜像（Knative 拉镜像 + 解压）
# 3. min-scale=1（保活）
```

## 🔗 下一步

- [Lambda / Cloud Run](/12-serverless/managed)
- [Deployment](/03-k8s-workload/deployment)
- [Knative Serving (官方)](https://knative.dev)