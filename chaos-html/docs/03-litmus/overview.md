---
title: Litmus 总览
date: 2026-08-15  # date-auto-injected
---

# Litmus 总览

## 项目背景与定位

Litmus 是 **CNCF Incubating 项目**（2021 年进入 Sandbox，2023 年 Incubating），最初由 MayaData 开源，专注 **Kubernetes + 云的混沌工程**。

**核心理念**：
- Chaos Experiments 即代码（CRD）
- ChaosHub 实验市场（社区贡献 50+ 预置实验）
- Probe-based 验证（显式断言 vs Chaos Mesh 的间接验证）

**与 Chaos Mesh 差异**：
- Litmus 更「实验驱动」：每个实验有明确的「Probe」（断言机制）
- Chaos Mesh 更「故障驱动」：CRD 直接描述故障，无显式 Probe
- Litmus 有「ChaosHub」：社区贡献的 50+ 预置实验（pod-delete / node-cordoned / dns-outage 等）
- Litmus 探针体系更完整：HTTP / SQL / K8s API / Prometheus / Datadog / 自定义

**GitHub 数据**（截至 2026.08）：★ 4.2k+ / Fork 600+ / Release v3.x

**项目状态变化**：
- 2017：MayaData 内部项目（验证 OpenEBS 韧性）
- 2020：v1.0 GA 开源
- 2021：CNCF Sandbox
- 2023：CNCF Incubating
- 2024：MayaData 解散，迁移至商业公司 Harness 维护
- 2025：v3.x（Litmus Edge 平台化）

## 整体架构

Litmus 由 **5 个核心组件** 组成：

```
┌────────────────────────────────────────────────┐
│  Litmus Portal (Web UI)                         │
│  - 实验编排 / 探针配置 / 历史 / RBAC            │
└──────────────┬─────────────────────────────────┘
               │ kubectl / API
               ▼
┌────────────────────────────────────────────────┐
│  Chaos-Operator (K8s Operator)                  │
│  - 管理 ChaosEngine / Experiment / Schedule      │
│  - watch CRD 变化并创建 ChaosRun Pod             │
└──────────────┬─────────────────────────────────┘
               │ create ChaosRun
               ▼
┌────────────────────────────────────────────────┐
│  Chaos-Runner (Pod)                             │
│  - 执行 Experiment CRD 描述的故障                │
│  - 注入 / 探针 / 报告                            │
└──────────────┬─────────────────────────────────┘
               │ metrics / logs
               ▼
┌────────────────────────────────────────────────┐
│  Chaos-Exporter (Deployment)                    │
│  - 导出实验指标到 Prometheus                    │
│  - 暴露 chaos_verdict 状态                      │
└────────────────────────────────────────────────┘
```

**辅助组件**：
- **ChaosHub**：实验市场（GitHub 仓库，预置实验 YAML）
- **Subscriber**：事件订阅（Slack / PagerDuty / Webhook）
- **Workflow Controller**：多步骤实验编排（v3.x 引入）

## CRD 体系

Litmus 的 CRD 比 Chaos Mesh 多一层抽象（Experiment + Engine + Schedule）：

**1. ChaosExperiment**（故障定义，可复用）：

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosExperiment
metadata:
  name: pod-delete
  namespace: litmus
spec:
  description: "Delete a pod"
  definition:
    scope: Namespaced
    permissions:
      - apiGroups: [""]
        resources: ["pods", "events"]
        verbs: ["create", "delete", "get", "list", "patch", "update"]
    image: "litmuschaos/go-runner:latest"
    imagePullPolicy: Always
    args:
      - -c
      - chaos-experiment
    command:
      - /bin/bash
    env:
      - name: TOTAL_CHAOS_DURATION
        value: "30"
      - name: CHAOS_INTERVAL
        value: "10"
      - name: TARGET_PODS
        value: ""
      - name: PODS_AFFECTED_PERC
        value: "50"
      - name: FORCE
        value: "true"
    labels:
      name: pod-delete
```

**2. ChaosEngine**（实验编排，绑定 Experiment + Probe）：

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: chaos-engine-example
  namespace: litmus
spec:
  appinfo:
    appns: "default"
    applabel: "app=nginx"
    appkind: "deployment"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          runner:
            image: "litmuschaos/chaos-runner:2.13.0"
        probe:
          - name: check-nginx-status
            type: httpProbe
            httpProbe:
              url: "http://nginx.default.svc.cluster.local:80"
              method: GET
              expectedResponseCodes: ["200"]
              timeout: 5s
              interval: 2s
              retries: 3
  jobCleanUpPolicy: "delete"
```

**3. ChaosSchedule**（定时调度，可选）：

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosSchedule
metadata:
  name: weekly-nginx-test
spec:
  schedule: "0 14 * * 1"  # 每周一 14:00
  type: Schedule
  chaosEngine: chaos-engine-example
```

**CRD 分层意义**：
- **ChaosExperiment**：可复用（一个实验定义可被多个 Engine 引用）
- **ChaosEngine**：实例化（绑定业务应用 + Probe）
- **ChaosSchedule**：调度（cron 触发）
- **ChaosResult**：实验结果（verdict：Pass / Fail）

## Probe 与断言

Probe 是 Litmus 的「**稳态验证机制**」。每个 ChaosEngine 可挂多个 Probe。

**Probe 类型**（v2.13+）：

**1. httpProbe**：HTTP 请求

```yaml
httpProbe:
  url: http://app:80/health
  method: GET
  expectedResponseCodes: ["200"]
  timeout: 5s
  interval: 2s
  retries: 3
```

**2. cmdProbe**：命令行（在 chaos-runner Pod 中执行）

```yaml
cmdProbe:
  command: "kubectl get pods -l app=nginx -o jsonpath='{.items[?(@.status.phase==\"Running\")].metadata.name}' | wc -l"
  expectedOutput: ">=3"
```

**3. promProbe**：Prometheus 查询

```yaml
promProbe:
  endpoint: http://prometheus.monitoring:9090
  query: "rate(http_requests_total{status=~\"5..\",app=\"nginx\"}[5m])"
  comparator: "LessThan"
  value: "0.05"  # 5xx 错误率 < 5%
```

**4. sqlProbe**：SQL 查询

```yaml
sqlProbe:
  connectionInfo:
    host: postgres.default.svc.cluster.local
    port: 5432
    user: chaos
    password: secret
    dbname: orders
  query: "SELECT COUNT(*) FROM orders WHERE status = 'PAID' AND created_at > NOW() - INTERVAL '5 minutes'"
  comparator: "GreaterThan"
  value: "100"
```

**5. k8sProbe**：K8s 资源查询

```yaml
k8sProbe:
  resourceType: "deployment"
  resourceName: "nginx"
  namespace: "default"
  statusCheck: true
  timeout: 30s
```

**Probe 模式**：
- **Continuous**：故障期间持续探测（默认）
- **OnChaos**：仅在故障开始时探测
- **EOT**（End of Test）：故障结束时探测

**Probe 失败 → 实验失败**：自动 rollback + 写入事件 + 通知 oncall

**Probe Property**：

```yaml
probe:
  - name: check-app-health
    type: httpProbe
    mode: Continuous
    runProperties:
      probeTimeout: 30s        # 总超时
      interval: 5s             # 探测间隔
      retry: 3                 # 重试次数
      stopOnFailure: true      # 失败立即中止
```

## ChaosHub 实验市场

ChaosHub 是 Litmus 的「**预置实验仓库**」（https://hub.litmuschaos.io），社区贡献 50+ 实验。

**热门实验**：

| 实验 | 用途 | Chaos Mesh 对应 |
|---|---|---|
| `pod-delete` | 删除 Pod | PodChaos pod-kill |
| `pod-cpu-hog` | CPU 抢占 | StressChaos cpu |
| `pod-memory-hog` | 内存压力 | StressChaos memory |
| `pod-network-loss` | 网络丢包 | NetworkChaos loss |
| `pod-network-latency` | 网络延迟 | NetworkChaos delay |
| `disk-fill` | 磁盘写满 | StressChaos disk |
| `node-drain` | 节点 drain | （kubectl drain） |
| `kubelet-service-kill` | kubelet 重启 | （脚本） |
| `dns-chaos` | DNS 故障 | DNSChaos |
| `time-chaos` | 时间漂移 | TimeChaos |
| `pod-network-partition` | Pod 网络分区 | NetworkChaos partition |
| `pod-autoscaler-kill` | HPA 故障 | （脚本） |

**使用方式**：

```bash
# 从 ChaosHub 安装实验
kubectl apply -f https://hub.litmuschaos.io/api/chaos?file=charts/generic/pod-delete/experiment.yaml

# 查看
kubectl get chaosexperiments -n litmus
```

**自定义实验**：
- 通过 `litmus-go` SDK 编写 Go 代码
- 编译为 Docker 镜像
- 注册到 ChaosHub（GitHub PR）

**Litmus SDK 示例（pod-delete 简化版）**：

```go
package main
import (
    "context"
    "github.com/litmuschaos/litmus-go/pkg/clients"
    "github.com/litmuschaos/litmus-go/pkg/log"
    "github.com/litmuschaos/litmus-go/pkg/result"
    "github.com/litmuschaos/litmus-go/pkg/utils"
    appsv1 "k8s.io/api/apps/v1"
)

func main() {
    clients.Init()
    experimentsDetails := clients.GetExperiment()
    result.Initialize(context.Background(), clients.ClientSet, experimentsDetails)

    // 实验逻辑：删除 Pod
    err := utils.DeletePod(...)
    if err != nil {
        result.RecordFailure(ctx, fmt.Sprintf("pod delete failed: %v", err))
    }
    result.RecordSuccess(ctx, "pod deleted successfully")
}
```

## 实战案例与最佳实践

**案例 1：Netflix 2023 公开分享**

- 用 Litmus ChaosHub 的 50+ 预置实验
- 每周自动运行（ChaosSchedule cron）
- Probe 验证 30+ SLO
- 实验失败自动 rollback + 写入 Jira

**案例 2：Stripe 2024 公开分享**

- 自定义 200+ 实验（覆盖所有微服务）
- 与 CI/CD 集成（PR 合并触发）
- Probe 同时验证 5 个 SLO（延迟 / 错误率 / 饱和度 / 流量 / 成本）

**最佳实践**：

1. **实验分层**：
   - L1（基础设施）：pod-delete / node-drain
   - L2（应用）：connection-pool / cache-miss
   - L3（业务）：订单失败 / 支付超时

2. **Probe 多维度**：
   - 业务（订单成功率）
   - 系统（错误率 / P99 延迟）
   - 资源（CPU / 内存）

3. **爆炸半径渐进**：
   - 单 Pod → 10% → 50% → 100%
   - 单 AZ → 跨 AZ

4. **结果可视化**：
   - chaos-dashboard 实时面板
   - 实验成功/失败率 + 影响时长
   - 与 SLO breach 联动

5. **事故复盘**：
   - 实验失败自动创建 Postmortem 模板
   - 与 Confluence / Notion 集成

**Litmus 优势**：
- 探针体系完整（5 种 Probe 类型）
- 实验可复用（ChaosExperiment 独立 CRD）
- 实验市场成熟（ChaosHub 50+ 预置）
- 与 Harness CD 深度集成（v3.x）

**Litmus 劣势**：
- 启动 chaos-runner Pod 较慢（~15s）
- 仅 K8s（不支持 VM / Host）原生
- 多运行时需要用 litmus-go 自定义
- 文档相对少（英文为主）

## 与其他站点的关系

- **observability**：Probe 引用 observability/03-prometheus（稳态指标）
- **devops**：实验纳入 CI/CD → 引用 devops/05-cicd-observability
- **chaos-engineering 04-platform-compare**：Litmus vs Chaos Mesh 选型
- **system-design**：实验验证可用性原则 → 引用 system-design/08-availability
- **architecture**：服务网格 + Litmus 集成 → 引用 architecture/05-microservices

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 混沌
- [observability](https://java-px.bot.cd/observability/):故障注入监控
- [system-design](https://java-px.bot.cd/system-design/):系统韧性
