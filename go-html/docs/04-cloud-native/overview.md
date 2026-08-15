---
title: 云原生总览
---

# 云原生总览

CNCF（Cloud Native Computing Foundation）是云原生生态的"联合国"，旗下项目几乎全部用 Go 写。Go 是云原生时代的"母语"。

## 一句话总结

> **Go = 云原生时代的母语**。**CNCF 毕业项目 100% Go 写**：Kubernetes / Docker / Prometheus / etcd / Consul / Terraform / Vitess / TiKV / Argo / Flux。**掌握 Go = 掌握云原生源码**。

---

## 一、CNCF 生态全景

### CNCF 三层成熟度

```
Graduated（毕业 · 生产可用）
   │
   ├── Incubating（孵化 · 早期生产）
   │
   └── Sandbox（沙箱 · 实验）
```

### 毕业项目（Graduated）

| 项目 | 用途 | 语言 | 主要公司 |
|---|---|---|---|
| **Kubernetes** | 容器编排 | Go | Google |
| **Docker / containerd** | 容器运行时 | Go | Docker Inc |
| **Prometheus** | 监控系统 | Go | CNCF |
| **etcd** | 分布式 KV | Go | CoreOS / Red Hat |
| **CoreDNS** | DNS 服务器 | Go | Miek Gieben |
| **Envoy** | 服务代理 | C++ | Lyft |
| **containerd** | 容器运行时 | Go | Docker Inc |
| **Fluentd** | 日志收集 | Ruby + C | Treasure Data |
| **Jaeger** | 链路追踪 | Go | Uber |
| **Helm** | K8s 包管理 | Go | Deis / Microsoft |
| **Argo** | K8s 工作流 | Go | Intuit |
| **Cortex** | Prometheus 多租户 | Go | CNCF |
| **TiKV** | 分布式 KV | Rust | PingCAP |
| **Vitess** | MySQL 分布式 | Go | YouTube / PlanetScale |
| **CNI** | 容器网络 | Go | CNCF |
| **gRPC** | RPC 框架 | Go/C++ | Google |
| **SPIFFE/SPIRE** | 身份认证 | Go | Scytale |
| **Thanos** | Prometheus 长期存储 | Go | Improbable |
| **Open Policy Agent** | 策略引擎 | Go | Styra |
| **Rook** | K8s 存储编排 | Go | Upbound |
| **Submariner** | K8s 多集群 | Go | Rancher |
| **Volcano** | K8s 批调度 | Go | Huawei |
| **KubeEdge** | K8s 边缘 | Go | Huawei |
| **Karmada** | K8s 多集群 | Go | Huawei |
| **KEDA** | K8s 事件驱动 | Go | Microsoft / Red Hat |

> **数据**：CNCF Graduated 项目中 **80%** 是 Go 写的（少数是 C++ / Ruby / Rust）

---

## 二、为什么云原生项目都用 Go

### 1. 单二进制部署

```bash
# Docker 容器中部署 Go 应用 vs Python 应用

# Go：FROM scratch，镜像 5-15MB
FROM scratch
COPY myapp /
ENTRYPOINT ["/myapp"]

# Python：FROM python:3.12，镜像 200MB+
FROM python:3.12
COPY app.py /app/
RUN pip install -r requirements.txt
CMD ["python", "/app/app.py"]
```

- **镜像小**：分发快、攻击面小
- **启动快**：无需运行时初始化
- **冷启动友好**：适合 Serverless / Function

### 2. 静态链接 + 跨平台编译

```bash
# 一行命令交叉编译到 Linux ARM64
GOOS=linux GOARCH=arm64 go build -o myapp-arm64

# 编译到 macOS
GOOS=darwin GOARCH=amd64 go build -o myapp-mac

# 编译到 Windows
GOOS=windows GOARCH=amd64 go build -o myapp.exe
```

- **无运行时依赖**：部署只需复制二进制
- **CI/CD 简化**：单一产物，多平台通用

### 3. 原生并发

```go
// K8s 中每个 Pod 一个 goroutine 池
// 单个 K8s 组件可管理 10k+ Pod
go func() {
    for {
        select {
        case pod := <-podCh:
            go syncPod(pod)  // 每 Pod 一个 goroutine
        case <-ctx.Done():
            return
        }
    }
}()
```

- **轻量 goroutine**：2KB 栈，可创建数十万
- **channel 通信**：天然的并发模型

### 4. 快速编译

```bash
# K8s 整个项目（几百万行）编译时间
time go build ./...
# real    1m30s

# 对比 Java Maven
time mvn package
# real    8m+
```

- **开发效率**：CI/CD 流水线更快
- **大项目友好**：K8s 工程师不会等编译等到崩溃

### 5. 标准库强大

```go
// net/http：内置 HTTP 服务器（K8s API Server）
// crypto/tls：内置 TLS（所有 HTTPS 通信）
// encoding/json：内置 JSON（K8s API 协议）
// context：内置 context（请求取消传播）
// net：内置网络编程（gRPC / HTTP / DNS）
```

---

## 三、CNCF 核心项目速览

### Kubernetes（容器编排）

- **架构**：API Server + Scheduler + Controller Manager + etcd + Kubelet + Kube-proxy
- **核心抽象**：Pod / Deployment / Service / Ingress / ConfigMap / Secret
- **API 协议**：HTTP + JSON（也有 gRPC）
- **扩展点**：CRD / Operator / Webhook / CSI / CNI

### Prometheus（监控系统）

- **架构**：Pull 模型（主动拉取）+ TSDB + PromQL + AlertManager
- **核心组件**：Prometheus Server + Pushgateway + Exporter + AlertManager
- **数据模型**：Metric (name + labels) + Sample (timestamp + value)
- **生态**：client_golang / node_exporter / kube-state-metrics

### etcd（分布式 KV）

- **架构**：Raft 一致性算法 + WAL + BoltDB
- **核心 API**：gRPC + HTTP/JSON
- **用途**：K8s 的"数据库"，存储所有集群状态
- **特性**：强一致、高可用、watch 机制

### Docker / containerd

- **Docker**：CLI + daemon + REST API
- **containerd**：行业标准容器运行时（Docker 内部也用）
- **OCI 标准**：镜像格式 + 运行时规范

### Envoy（服务代理）

- **架构**：xDS 配置分发 + HTTP/2 + HTTP/3 + WASM
- **数据面**：服务网格（Istio / Consul Connect）的基础
- **不是 Go**：C++ 写（性能考量）

---

## 四、CNCF 与"云原生"全景

### CNCF Landscape

CNCF 维护了一个庞大的 Landscape：https://landscape.cncf.io/

按类别：

```
📦 编排与管理（Orchestration）
   Kubernetes, Docker Swarm, Mesos

🚀 应用定义与镜像构建（App Definition）
   Helm, Kustomize, Skaffold, Buildpacks

🌐 协调与服务发现（Coordination）
   etcd, Consul, ZooKeeper

📊 可观测与分析（Observability）
   Prometheus, Grafana, Loki, Tempo, Jaeger, OpenTelemetry

💾 平台（Platform）
   Crossplane, Rook, KubeVirt

🛡️ 安全与合规（Security）
   Falco, OPA, SPIFFE/SPIRE, cert-manager

🗄️ 存储（Storage）
   Rook, MinIO, TiKV

🌐 消息（Messaging）
   NATS, Strimzi (Kafka), RabbitMQ

📡 数据库（Database）
   Vitess, TiKV

⚙️ 运行时（Runtimes）
   containerd, runc, gVisor

🖥️ 供应（Provisioning）
   Terraform, Pulumi, Crossplane

💻 无服务器（Serverless）
   Knative, OpenFaaS, KEDA

📦 配置管理（Config Management）
   Argo, Flux

🔄 持续集成与交付（CI/CD）
   Argo, Flux, Tekton

🎯 服务网格（Service Mesh）
   Istio, Linkerd, Consul Connect
```

---

## 五、学习路径

### 入门（先会用）

1. **Docker**：docker run / docker build / docker-compose
2. **Kubernetes 基础**：Pod / Deployment / Service / Ingress
3. **kubectl**：常用命令
4. **Helm**：chart 编写与使用

### 进阶（读懂源码）

1. **Kubernetes 源码导读**：kube-apiserver / kube-scheduler
2. **Prometheus 源码导读**：TSDB / PromQL / scrape
3. **etcd 源码导读**：Raft / WAL / BoltDB

### 高级（参与贡献）

1. KEP（Kubernetes Enhancement Proposal）
2. CNCF 项目 SIG（Special Interest Group）
3. KubeCon 演讲 / 技术分享

---

## 关联章节

- **04-cloud-native/docker-internals**：Docker 源码导读
- **04-cloud-native/kubernetes-internals**：Kubernetes 源码导读
- **04-cloud-native/prometheus-internals**：Prometheus 源码导读
- **04-cloud-native/etcd-internals**：etcd 源码导读
- **04-cloud-native/cncf-ecosystem**：CNCF 全景

## 一句话总结

> **Go = 云原生母语**。**掌握 Go = 看得懂 Kubernetes / Prometheus / etcd 源码 = 真正理解云原生**。
