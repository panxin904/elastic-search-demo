---
title: Chaos Mesh 总览
---

# Chaos Mesh 总览

## 项目背景与里程碑

Chaos Mesh 是 **CNCF Graduated 项目**（2024 年毕业），由 PingCAP 团队 2019 年 12 月开源，2021 年 2 月进入 CNCF Sandbox，2022 年 6 月晋升 Incubating，2023 年 12 月发布 v2.6（Workflow / Schedule / Resource Manager 全面成熟），2024 年 11 月毕业（Graduated）。

**核心定位**：Kubernetes 原生的混沌工程平台，**CRD-first 设计**——所有故障都是 K8s 资源，`kubectl apply` 即可管理。

**GitHub 数据**（截至 2026.08）：★ 6.8k+ / Fork 800+ / Contributor 300+ / Release v2.7.x

**关键设计理念**：
- **故障即资源**：PodChaos、NetworkChaos、StressChaos 等都是 K8s CRD
- **可视化优先**：内置 chaos-dashboard（Web UI）
- **Kubernetes 深度集成**：selector / namespace / annotation 全兼容
- **多运行时支持**：docker / containerd / crio / kata

**关键里程碑时间线**：
- 2019.12：v1.0 发布（仅 PodChaos + NetworkChaos）
- 2020.06：v1.0 RC（StressChaos + IOChaos）
- 2021.02：CNCF Sandbox
- 2022.06：CNCF Incubating
- 2023.12：v2.6（Workflow + Schedule 成熟）
- 2024.11：CNCF Graduated（毕业）
- 2025.06：v2.7（JVMChaos + KernelChaos GA）
- 2026.03：v2.8（AI 辅助故障画像实验性）

## 整体架构

Chaos Mesh 由 **3 个核心组件 + 多个故障控制器** 组成：

**1. chaos-controller-manager**
- 监听 CRD 变化（PodChaos / NetworkChaos / StressChaos 等）
- 调度 chaos daemon 执行故障
- 高可用：Deployment 多副本 + leader election
- 资源占用低（< 256Mi 内存 / 100m CPU）

**2. chaos-daemon**（DaemonSet）
- 每个 K8s Node 一个 Pod
- 通过 Linux 内核能力（tc / iptables / cgroup）执行故障
- 共享宿主机 PID / Network namespace
- 资源隔离：--cpu=200m / --memory=256Mi

**3. chaos-dashboard**（可选）
- Web UI（实验编排 / 监控 / 历史）
- 前后端分离（React + Go）
- 支持 RBAC 权限管理
- 实验模板复用（Template Library）

**故障控制器**（每类故障一个 Controller）：

| CRD | 用途 | 关键字段 |
|---|---|---|
| **PodChaos** | Pod 故障 | action: pod-kill / pod-failure |
| **NetworkChaos** | 网络故障 | delay / loss / duplicate / corrupt / partition |
| **StressChaos** | 资源压力 | cpu / memory workers + load |
| **IOChaos** | 文件系统故障 | latency / errno |
| **TimeChaos** | 时间漂移 | timeOffset / clockIds |
| **DNSChaos** | DNS 故障 | patterns: NXDOMAIN / timeout |
| **KernelChaos** | 内核故障 | callchain / failtype |
| **JVMChaos** | JVM 故障 | OOM / GC / CPU / latency |
| **AWSChaos** | AWS 资源故障 | ec2-stop / detach-volume |
| **GCPChaos** | GCP 资源故障 | compute-stop / disk-loss |
| **AzureChaos** | Azure 资源故障 | vm-stop / disk-detach |

**辅助资源**：
- **Schedule**：定时任务（cron 表达式，符合 RFC 5545）
- **Workflow**：多步骤实验编排（DAG，支持 Serial / Parallel / Suspend / TypeChaos）
- **Status**：实验执行进度（运行中 / 已完成 / 已中止 / 错误）
- **Grafana 面板**：内置 dashboard（实验成功率 / 故障影响 / SLO breach）

## 核心 CRD 通用字段

每个 Chaos CRD 都有统一的 `Spec` 字段：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: pod-kill-example
  namespace: chaos-mesh
  labels:
    chaos: production
spec:
  action: pod-kill              # 故障动作
  mode: one                      # 选择模式：one/all/fixed/fixed-percent/maximum
  selector:                      # 目标 Pod 选择器
    namespaces:
      - default
    labelSelectors:
      app: order-service
    annotationSelectors:
      chaos-test: enabled
  duration: "30s"                # 故障持续时间（自动恢复）
  scheduler:                     # 调度策略（可选）
    cron: "@every 1m"
```

**action**：故障具体动作（如 `pod-kill` / `pod-failure` / `network-delay`）

**mode**：选择模式
- `one`：随机 1 个
- `all`：所有
- `fixed`：固定数量
- `fixed-percent`：百分比
- `maximum`：最多 N 个

**selector**：选择目标 Pod
- `namespaces`：namespace 列表
- `labelSelectors`：K8s label 选择器
- `annotationSelectors`：annotation 选择器
- `pods`：直接指定 Pod（namespaced name）
- `nodeSelectors`：node 选择器

**duration**：实验时长（Chaos Mesh 会自动恢复，等同于 `chaoskillfinalizer`）

**scheduler**：定时调度（cron 表达式）

**priorityClassName**：调度优先级（影响 Pod 抢占）

## 安装与部署

**前置要求**：
- Kubernetes ≥ 1.16（推荐 1.22+）
- Helm 3（推荐）或 kubectl
- Linux kernel ≥ 4.9（tc 高级特性）
- containerd / docker / crio 之一

**方式 1：Helm 安装（推荐）**：

```bash
# 添加 Chaos Mesh Helm Repo
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update

# 安装到 chaos-mesh namespace
helm install chaos-mesh chaos-mesh/chaos-mesh \
  --namespace chaos-mesh --create-namespace \
  --set chaosDaemon.runtime=containerd \
  --set chaosDaemon.socket=/run/containerd/containerd.sock \
  --version 2.7.0

# 验证
kubectl get pods -n chaos-mesh
```

**方式 2：kubectl apply**：

```bash
kubectl apply -f https://mirrors.chaos-mesh.org/v2.7.0/install.sh | bash
```

**关键参数**：

| 参数 | 默认 | 说明 |
|---|---|---|
| `chaosDaemon.runtime` | docker | 容器运行时（docker / containerd / crio） |
| `chaosDaemon.socket` | /var/run/docker.sock | runtime socket 路径 |
| `dashboard.securityMode` | true | 启用 RBAC |
| `clusterScoped` | true | 跨 namespace 实验 |
| `chaosControllerManager.replicas` | 3 | controller 高可用副本数 |
| `chaosDaemon.resources.limits.cpu` | 200m | daemon CPU 上限 |
| `chaosDaemon.resources.limits.memory` | 256Mi | daemon 内存上限 |

**生产环境清单**：
- RBAC：创建 `chaos-engineer` / `chaos-viewer` 角色
- ResourceQuota：限制 Chaos CRD 数量（避免误操作）
- NetworkPolicy：限制 chaos-daemon 跨 namespace 访问
- 审计日志：开启 K8s audit + chaos-controller-manager 日志
- 高可用：chaos-controller-manager ≥ 2 副本 + PodDisruptionBudget
- 资源限制：避免 chaos-daemon 抢占业务 Pod 资源

## PodChaos 实战案例

**场景**：验证 order-service 在 1 个 Pod 被 kill 时的韧性。

**实验 YAML**：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: order-service-pod-kill
  namespace: chaos-mesh
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces: [order]
    labelSelectors:
      app: order-service
  duration: "30s"
```

**应用实验**：

```bash
kubectl apply -f pod-chaos.yaml
# 30 秒内 1 个 Pod 被 SIGKILL，30 秒后 chaos 自动恢复
kubectl get podchaos order-service-pod-kill -o jsonpath='{.status.conditions[0].message}'
```

**观察指标（Prometheus）**：

```promql
# 5xx 错误率
sum(rate(http_requests_total{status=~"5..",app="order-service"}[5m]))
/
sum(rate(http_requests_total{app="order-service"}[5m]))

# P99 延迟
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{app="order-service"}[5m])) by (le))

# Pod 重启次数
increase(kube_pod_container_status_restarts_total{pod=~"order-service-.*"}[5m])
```

**预期结果（稳态假设）**：
- 错误率峰值 < 5%（单 Pod 流量转移）
- P99 延迟 < 1.5s（无雪崩）
- K8s 自动重启 Pod + 服务自动恢复

**PodChaos action 类型**：
- `pod-kill`：SIGKILL 杀进程（立即）
- `pod-failure`：容器启动失败（不可恢复，需要手动恢复）
- `container-kill`：杀容器（保留 Pod）
- `pod-schedule`：延迟调度（不创建 Pod）

**混沌即代码（Chaos as Code）**：
- 用 ArgoCD / Flux 把所有 chaos YAML 写入 Git
- PR 评审 = 混沌实验评审
- 自动同步到测试 / 生产环境

## NetworkChaos 实战案例

**场景**：验证 checkout-service 在跨 AZ 网络延迟 200ms 时的可用性。

**实验 YAML**：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: checkout-network-delay
  namespace: chaos-mesh
spec:
  action: delay
  mode: all
  selector:
    namespaces: [checkout]
    labelSelectors:
      app: checkout-service
  delay:
    latency: "200ms"
    correlation: "75"      # 相关性（0-100，75% 流量同步延迟）
    jitter: "50ms"          # 抖动
  direction: to            # 目标（出方向）
  duration: "60s"
```

**action 类型**：
- `delay`：延迟
- `loss`：丢包（百分比）
- `duplicate`：重复（百分比）
- `corrupt`：损坏（百分比）
- `partition`：分区（与目标 Pod 完全断网）
- `bandwidth`：带宽限制（rate limit）

**direction**：
- `to`：出方向（本 Pod → 目标）
- `from`：入方向（目标 → 本 Pod）
- `both`：双向

**correlation**：
- 100 = 完全同步（每个包都延迟）
- 0 = 完全独立（随机）
- 75 = 大部分同步（更真实）

**jitter**：
- 在 `latency` 基础上的随机抖动
- 模拟真实网络抖动（不规则延迟）

**实战案例（Netflix 公开分享）**：
- 在跨 AZ 部署中注入 200ms 延迟 + 0.5% 丢包
- 验证「服务降级开关」是否自动启用（fallback 到 cached data）
- 验证「超时+重试」配置是否合理（避免雪崩）

**NetworkChaos 高级用法**：

```yaml
# 跨 namespace 网络分区
spec:
  action: partition
  mode: all
  selector:
    namespaces: [payment]
    labelSelectors:
      app: payment-service
  direction: both
  # 与 default namespace 的 order-service 隔离
  target:
    selector:
      namespaces: [default]
      labelSelectors:
        app: order-service
    mode: all
```

## Workflow 工作流编排

**场景**：电商大促前的全链路韧性验证（订单 → 支付 → 库存 → 物流）。

**Workflow YAML**：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Workflow
metadata:
  name: e2e-resilience-validation
  namespace: chaos-mesh
spec:
  entry: e2e
  templates:
    - name: e2e
      templateType: Serial
      children:
        - order-pod-kill
        - payment-network-delay
        - inventory-stress
        - logistics-partition
    - name: order-pod-kill
      templateType: PodChaos
      duration: "30s"
      podChaos:
        action: pod-kill
        mode: one
        selector:
          namespaces: [order]
          labelSelectors: { app: order-service }
    - name: payment-network-delay
      templateType: NetworkChaos
      duration: "60s"
      networkChaos:
        action: delay
        delay: { latency: "300ms" }
        selector:
          namespaces: [payment]
          labelSelectors: { app: payment-service }
    - name: inventory-stress
      templateType: StressChaos
      duration: "60s"
      stressChaos:
        stressors: { cpu: { workers: 2, load: 80 } }
        selector:
          namespaces: [inventory]
          labelSelectors: { app: inventory-service }
    - name: logistics-partition
      templateType: NetworkChaos
      duration: "30s"
      networkChaos:
        action: partition
        selector:
          namespaces: [logistics]
          labelSelectors: { app: logistics-service }
```

**Workflow 优势**：
- 多步骤串联（Serial / Parallel / Suspend）
- 状态可视化（chaos-dashboard 显示每个步骤）
- 失败自动中止 + 通知
- 与 CI/CD 集成（PR 合并触发）

**与 Schedule 集成**：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Schedule
metadata:
  name: weekly-e2e-resilience
spec:
  schedule: "0 14 * * 1"     # 每周一 14:00
  type: Schedule
  historyLimit: 10
  concurrencyPolicy: Forbid   # 防止重叠
  workflow: e2e-resilience-validation
```

## 与其他站点的关系

- **observability 站**：稳态指标采集 → 引用 observability/03-prometheus
- **devops 站**：实验纳入 CI/CD → 引用 devops/05-cicd-observability
- **chaos-engineering 04-platform-compare**：与 Litmus / Gremlin 对比
- **system-design**：可用性原则验证 → 引用 system-design/08-availability
- **design-pattern**：Circuit Breaker / Bulkhead 验证 → 引用 design-pattern/05-architectural-patterns