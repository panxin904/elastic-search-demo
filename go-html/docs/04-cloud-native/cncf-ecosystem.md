---
title: CNCF 项目全景
---

# CNCF 项目全景

**CNCF（Cloud Native Computing Foundation）= 云原生生态**——80% 项目是 Go 写。

## 一句话总结

> **CNCF Landscape = 130+ 毕业项目 + 200+ 沙盒项目**。**Go 是云原生时代的 C 语言**。

---

## 一、CNCF 是什么

- 2015 年成立，Linux Foundation 旗下
- 总部：旧金山
- 会员：红帽 / 谷歌 / AWS / Azure / 阿里 / 华为 / 腾讯 / 字节...
- 目标：推广云原生技术（容器 / 服务网格 / 监控 / GitOps）

## 二、毕业项目 TOP 30

| 阶段 | 项目 | 用途 | Go 占比 |
|---|---|---|---|
| 🎓 | **Kubernetes** | 容器编排 | 100% |
| 🎓 | **Prometheus** | 监控 | 100% |
| 🎓 | **etcd** | KV 存储 | 100% |
| 🎓 | **containerd** | 容器 runtime | 100% |
| 🎓 | **CoreDNS** | DNS 服务 | 100% |
| 🎓 | **Fluentd** | 日志收集 | 30% (CRuby) |
| 🎓 | **Envoy** | 服务代理 | 60% (C++) |
| 🎓 | **Helm** | K8s 包管理 | 100% |
| 🎓 | **TiKV** | 分布式 KV | 100% (Rust 10%) |
| 🎓 | **Jaeger** | 分布式追踪 | 100% |
| 🎓 | **Vitess** | MySQL 集群 | 100% |
| 🎓 | **TUF** | 安全更新 | 100% |
| 🎓 | **Argo** | 工作流 | 100% |
| 🎓 | **Cilium** | CNI + Service Mesh | 70% (C 30%) |
| 🎓 | **Crossplane** | K8s 控制平面 | 100% |
| 🎓 | **Backstage** | 开发者门户 | 80% (TS 20%) |
| 🎓 | **Cortex** | Prometheus 集群 | 100% |
| 🎓 | **Thanos** | Prometheus 长期存储 | 100% |
| 🎓 | **OpenTelemetry** | 可观测性 | 70% |
| 🎓 | **KubeVirt** | 虚拟机 K8s | 100% |
| 🎓 | **Karmada** | 多云 K8s | 100% |
| 🎓 | **Keda** | 事件驱动 K8s | 100% |
| 🎓 | **cert-manager** | TLS 证书 | 100% |
| 🎓 | **Dapr** | 应用运行时 | 100% |
| 🎓 | **Istio** | Service Mesh | 100% (Envoy 60%) |
| 🎓 | **rook** | 存储编排 | 100% |
| 🎓 | **Linkerd** | Service Mesh | 90% (Rust 10%) |
| 🎓 | **SPIFFE/SPIRE** | 身份认证 | 100% |
| 🎓 | **Dragonfly** | 镜像分发 | 100% |
| 🎓 | **WasmEdge** | WebAssembly runtime | 70% (C++) |

**Go 比例**：约 80% 的 CNCF 项目主要用 Go 写。

## 三、沙盒项目精选

| 项目 | 用途 |
|---|---|
| **Kubewarden** | K8s admission policy（用 Rust 沙箱） |
| **KubeArmor** | K8s 运行时安全 |
| **Parsec** | 云原生 PKI |
| **Tinkerbell** | bare-metal 编排 |
| **Curiefense** | API 安全网关 |
| **PipeCD** | GitOps（CD） |
| **OpenFeature** | Feature flag 标准 |
| **KCL** | 配置语言 |
| **KubeVela** | 应用抽象层 |
| **Sealer** | K8s 集群镜像 |

## 四、CNCF Landscape 分层

```
┌─────────────────────────────────────────┐
│  App Definition & Development           │
│  Helm / Skaffold / Tilt / Backstage     │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Orchestration & Management             │
│  Kubernetes / Argo / Crossplane / Karmada│
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Runtime                                │
│  containerd / runc / gVisor / Kata      │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Provisioning                           │
│  Terraform / Crossplane / Pulumi        │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Platform                               │
│  Rancher / OpenShift / TKE              │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Observability & Analysis               │
│  Prometheus / Loki / Tempo / Jaeger     │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Service Mesh / RPC / API Gateway       │
│  Istio / Linkerd / Envoy / Dapr         │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Storage                                │
│  Rook / MinIO / TiKV / Vitess           │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Security & Compliance                  │
│  cert-manager / TUF / SPIFFE / Falco    │
└─────────────────────────────────────────┘
```

## 五、Go 在 CNCF 中的技术垄断

**原因 1：Go 的语言特性契合云原生**

| 需求 | Go 的方案 |
|---|---|
| 静态二进制（容器友好） | `CGO_ENABLED=0` 单文件几 MB |
| 跨平台编译 | `GOOS=linux GOARCH=arm64 go build` |
| 高并发 | goroutine + channel |
| 网络协议 | gRPC 官方支持 |
| 标准库 | net/http / crypto/tls / encoding/json |
| 部署简单 | 单二进制 + 配置文件 |

**原因 2：Google 的示范效应**

- K8s（Google）= Go
- gRPC（Google）= Go
- Borg → K8s → 全行业跟进

**原因 3：Docker / K8s 时代红利**

- 2014 年 Docker 爆发，Go 工程师需求暴增
- K8s 1.0（2015）需要 Go 开发者

**原因 4：库生态正循环**

- client-go、controller-runtime → K8s operator
- gRPC-Go / protobuf → 微服务
- prometheus/client_golang → 监控

## 六、Go 写的明星项目

### 容器 & 编排
- Kubernetes（10w+ stars）
- Docker（68k+）
- containerd（15k+）
- Helm（25k+）
- Argo（15k+）
- k3s / k0s（轻量 K8s）

### 服务网格 & API
- Istio（35k+）
- Linkerd（10k+）
- Dapr（23k+）
- Traefik（47k+）
- Caddy（54k+）

### 可观测性
- Prometheus（53k+）
- Thanos（12k+）
- Cortex（5k+）
- Loki（22k+）
- Tempo（4k+）
- OpenTelemetry（Go SDK 1.5k+）

### 数据库 & 存储
- etcd（46k+）
- TiKV（14k+）
- Vitess（17k+）
- MinIO（44k+）
- CockroachDB（28k+）
- InfluxDB（28k+）
- ClickHouse（C++ 但有 Go client）
- Dragonfly（13k+）
- NATS（15k+）

### DevOps
- Terraform（41k+）
- Vault（29k+）
- Packer（14k+）
- Consul（27k+）
- Nomad（14k+）

## 七、非 Go 但同生态

- **Rust**：Linkerd 2-proxy / TiKV 部分 / Kubewarden / Deno runtime
- **C++**：Envoy / Istio data plane / ClickHouse
- **TypeScript**：Backstage / Deno（少数）
- **Java**：Elasticsearch / Solr / Cassandra
- **Python**：Pyroscope / Apache Airflow

## 八、Go 在 CNCF 贡献者生态

**贡献数据**（2024）：
- 70%+ 的 CNCF 项目核心维护者用 Go
- CNCF 维护者中 Go 开发者占 60%
- K8s 1.30 release 有 400+ 贡献者

## 九、学习路径

**入门路径**：
1. **Go 基础**：语法 / goroutine / interface
2. **net/http**：写 REST API
3. **gRPC**：服务间通信
4. **Docker**：容器化
5. **K8s**：deploy 到集群
6. **Prometheus**：埋点 + 抓取
7. **Operator / CRD**：K8s 扩展
8. **Service Mesh**：Istio / Linkerd

**项目参与路径**：
- 入门：good first issue
- 进阶：fix bug / improve docs
- 高级：feature / design proposal

## 关联章节

- **04-cloud-native/docker-internals**：容器
- **04-cloud-native/kubernetes-internals**：编排
- **04-cloud-native/prometheus-internals**：监控
- **04-cloud-native/etcd-internals**：存储

## 一句话总结

> **CNCF Landscape = 云原生生态地图**。**Go 是云原生时代的 C 语言，统治 80% 项目**。

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [rust](https://java-px.bot.cd/rust/):Rust 对比
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s / Docker
- [devops](https://java-px.bot.cd/devops/):DevOps 工具
