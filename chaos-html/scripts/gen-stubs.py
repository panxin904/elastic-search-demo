#!/usr/bin/env python3
"""Generate 24 stub markdown files for chaos-html sidebar."""
from pathlib import Path

ROOT = Path('/Users/a1111/work_space/elastic-search-demo/chaos-html/docs')

STUBS = [
    # (path, title, sections)
    ('01-foundations/history', '历史与哲学', [
        ('起源与发展', r'''混沌工程的起源可以追溯到 2010 年 Netflix 的云架构迁移。当时 Netflix 把单体应用迁移到 AWS 云上，失去对硬件的直接控制，需要一种方法来验证云上系统的韧性。

2010 年 Netflix 内部开始开发 Chaos Monkey，自动随机终止 EC2 实例。2012 年 Netflix 把 Chaos Monkey 开源，业界开始关注。2014 年 Netflix 推出 Simian Army（Chaos Gorilla 模拟整个可用区故障 / Chaos Kong 模拟整个 Region 故障）。

2015 年 Netflix、Disney、Microsoft 等公司联合发布 Principles of Chaos 白皮书，正式确立了混沌工程的四大原则。2016 年 Netflix 推出 ChAP（Chaos Automation Platform），把混沌工程从单点实验升级为平台化。

2018 年 Gremlin 完成 2950 万美元 A 轮融资，商业化混沌工程。2019 年阿里开源 ChaosBlade，PingCAP 开源 Chaos Mesh。2021 年 Chaos Mesh 进入 CNCF Sandbox，Litmus 进入 CNCF Sandbox。

2022 年 Gremlin 完成 C 轮融资，企业市场爆发。2023 年 Chaos Mesh 晋升 CNCF Incubating。2024 年 11 月 Chaos Mesh 毕业（CNCF Graduated），标志着混沌工程成为云原生领域的主流实践。

**关键里程碑时间线**：

- 2010：Netflix Chaos Monkey 内部开发
- 2012：Chaos Monkey 开源
- 2014：Simian Army 发布
- 2015：Principles of Chaos 白皮书
- 2016：ChAP 平台化
- 2018：Gremlin 商业化
- 2019：ChaosBlade / Chaos Mesh 开源
- 2021：Chaos Mesh + Litmus 进入 CNCF Sandbox
- 2024：Chaos Mesh CNCF 毕业
- 2025+：AI 辅助故障画像 + 自适应混沌

**哲学思考**：

混沌工程不是「破坏测试」，而是「**对系统韧性的科学实验**」。它有方法论、有假设、有验证、有复盘。这与「故意搞破坏」（breaking things for fun）有本质区别。

混沌工程的哲学基础是「**拥抱失败**」（embrace failure）：失败不是异常状态，而是系统的常态。系统的设计应该假设失败会发生，并提前准备好应对措施。

**与 SRE 文化的关系**：

混沌工程是 SRE 文化的重要组成部分。Google SRE Book Chapter 22「Addressing Cascading Failures and Other Bad Behavior」详细描述了类似实践，包括 DiRT（Disaster Recovery Testing）和 FireDrill（小规模演练）。'''),

        ('关键人物与组织', r'''**Netflix**：

- Adrian Cockcroft（架构师，2010 年推动 Chaos Monkey）
- Yury Izrailevsky（VP Cloud Architecture）
- Casey Rosenthal（Chaos Engineering 团队 Lead）

**PingCAP**：

- 周畅（CEO）
- 吴雪晶（Chaos Mesh Lead Maintainer）

**MayaData**（Litmus 创始））：

- Karthik Satchitanand（创始人）

**Gremlin**：

- Kolton Andrus（CEO，前 AWS Chaos Engineer）
- Matt Fornaciari（CTO）

**阿里**：

- 李三红（ChaosBlade Lead）
- 陈洁萌（AHAS Lead）

**社区贡献者**：

- Yuri Shkuro（Jaeger / Dapper 作者，Chaos Mesh 用户）
- Henrik Høegh（Observability 专家）'''),

        ('与其他站点关系', r'''- **observability**：混沌实验验证 observability 设计的正确性 → 引用 observability/01-foundations
- **devops**：混沌工程纳入 CI/CD → 引用 devops/01-pipeline/overview
- **system-design**：可用性原则的工程化 → 引用 system-design/08-availability'''),
    ]),

    ('01-foundations/steady-state', '稳态假设', [
        ('什么是稳态', r'''稳态（Steady State）是系统在正常情况下的可度量行为模式。它是混沌实验的「对照组」—— 没有稳态，实验结果无法解读。

**稳态三要素**：

1. **可度量的指标（Measurable）**：CPU 使用率、订单成功率、P99 延迟、错误率等
2. **基线值（Baseline）**：过去 7 天 / 30 天的 P50 / P95 / P99
3. **区间范围（Range）**：不是单点值，而是「区间 + 时间窗口」

**稳态示例**：

- 订单成功率：99.5% - 99.9%，持续 5 分钟
- P99 延迟：700ms - 900ms，持续 10 分钟
- 错误率：0.01% - 0.1%，持续 15 分钟
- 队列积压：< 1000 条消息，持续 5 分钟

**为什么稳态是「区间」而不是「单点」**？

- 单点值波动大（每秒成功率可能波动 0.5%）
- 区间 + 窗口更稳定（5 分钟聚合窗口）

**稳态计算（滑动窗口）**：

```promql
# 订单成功率（5 分钟窗口）
sum(rate(order_success_total[5m]))
/ sum(rate(order_total[5m]))
```

**稳态基线建立流程**：

1. 收集 7-30 天数据
2. 计算 P5 / P95（剔除异常值）
3. 定义区间 = [P5, P95]
4. 加上窗口期（如 5 分钟）
5. 写入 runbook'''),

        ('稳态验证方法', r'''**1. 阈值法**：

```yaml
# 稳态判定（Prometheus alert）
alert: SteadyStateViolation
expr: |
  abs(
    sum(rate(order_success_total[5m]))
    / sum(rate(order_total[5m]))
    - 0.997
  ) > 0.005
for: 5m
```

**2. 同比/环比法**：

```promql
# 与上周同时段对比
sum(rate(order_success_total[5m]))
/ sum(rate(order_total[5m]))
> on() (0.997 - 0.005)
```

**3. 3-sigma 法**：

```python
import numpy as np

def steady_state_check(observed, history):
    mean = np.mean(history)
    std = np.std(history)
    return abs(observed - mean) < 3 * std
```

**4. 机器学习（Prophet / LSTM）**：

```python
from prophet import Prophet

model = Prophet()
model.fit(history_df)

future = model.make_future_dataframe(periods=300, freq='1min')
forecast = model.predict(future)

# 检测观测值是否在预测区间外
is_anomaly = observed < forecast.yhat_lower or observed > forecast.yhat_upper
```

**5. CUSUM（累积和算法）**：

```python
def cusum_check(observed, baseline, threshold):
    cumulative = 0
    for value in observed:
        cumulative = max(0, cumulative + (baseline - value))
        if cumulative > threshold:
            return True  # 异常
    return False
```'''),

        ('稳态常见误区', r'''**误区 1：用 CPU 使用率做稳态**

- CPU 使用率高 ≠ 系统故障（可能正常负载）
- 关注**用户感知**指标（订单成功率 / 延迟）

**误区 2：用瞬时值**

- 每秒成功率波动 0.5% 是正常的
- 用滑动窗口聚合（如 5 分钟）

**误区 3：单一指标**

- 订单成功率 99.5% 但 P99 延迟 5 秒 → 用户体验差
- 多维度（成功率 + 延迟 + 错误率）

**误区 4：忽略季节性**

- 大促期间订单量翻倍，指标波动大
- 用同比/环比对比同时段

**误区 5：稳态不变**

- 系统升级 / 流量增长后，稳态基线需要重新建立
- 每月 / 每季度重新计算'''),

        ('与其他站点关系', r'''- **observability/03-prometheus**：Prometheus 采集稳态指标
- **observability/08-alerting**：稳态偏离告警
- **system-design/08-availability**：SLO 与稳态关系'''),
    ]),

    ('01-foundations/blast-radius', '爆炸半径', [
        ('爆炸半径分级', r'''爆炸半径（Blast Radius）是「实验失败时的最大影响范围」。分级管理：

| 级别 | 流量 | 实例 | 区域 | 时长 | 适用 |
|---|---|---|---|---|---|
| L1 · 单测 | 0% | 1 Pod | 单 AZ | 5s | 首次实验 |
| L2 · 金丝雀 | 1% | 10% Pods | 单 AZ | 30s | 灰度验证 |
| L3 · 灰度 | 10% | 50% Pods | 单 Region | 5min | 回归测试 |
| L4 · 全量 | 100% | 100% Pods | 多 Region | 30min | 持续运行 |

**L1（单测）**：1 个 Pod，无真实流量（仅探活），单 AZ，5 秒。适用于首次实验，验证工具链 + 流程。

**L2（金丝雀）**：10% 真实流量，10% Pods，单 AZ，30 秒。验证核心假设（如 Pod kill 时流量转移）。

**L3（灰度）**：10-50% 流量，半数 Pods，单 Region，5 分钟。验证依赖链路（如支付失败是否影响订单）。

**L4（全量）**：100% 流量，所有 Pods，多 Region，30 分钟。生产环境持续运行（每周 / 每月）。'''),

        ('爆炸半径控制四要素', r'''**1. 流量比例**：

- 金丝雀 1% → 灰度 10% → 全量 100%
- 实现：Service Mesh（Istio VirtualService）或 API Gateway

```yaml
# Istio VirtualService（流量切分）
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts: [order-service]
  http:
  - route:
    - destination:
        host: order-service
        subset: v1
      weight: 90
    - destination:
        host: order-service
        subset: v2
      weight: 10  # 灰度 10% 到 v2
```

**2. 实例比例**：

- 1 个 Pod → 10% Pods → 50% Pods → 100% Pods
- 实现：PodChaos `mode` 字段

```yaml
spec:
  mode: fixed-percent
  value: "10"  # 10% Pods
```

**3. 区域比例**：

- 单 AZ → 同城双活 → 跨 Region
- 实现：chaos-mesh `nodeSelectors`

```yaml
selector:
  nodeSelectors:
    topology.kubernetes.io/zone: us-east-1a
```

**4. 时长控制**：

- 实验时长 ≤ 影响传播时间
- 实现：`duration` 字段（自动恢复）

```yaml
spec:
  duration: "30s"  # 30 秒后自动恢复
```

**回滚预案（必备）**：

- 自动化：SLO breach → 自动 kill chaos
- 手动化：「红色按钮」一键 kill
- 退出条件：业务影响超阈值'''),

        ('退出条件设计', r'''**退出条件三要素**：

1. **业务退出条件**：业务指标跌至阈值
2. **时间退出条件**：实验超过最大时长
3. **错误退出条件**：实验连续失败 N 次

**示例**：

```yaml
# chaos-experiment.yaml
spec:
  duration: "5m"
  auto_termination:
    - condition: "order_success_rate < 95"
      action: "kill_chaos"
      notification: "pagerduty:high"
    - condition: "p99_latency > 3000ms"
      action: "kill_chaos"
      notification: "slack:#chaos-game-day"
    - condition: "duration > 10m"
      action: "kill_chaos"
      notification: "slack:oncall"
```

**退出条件最佳实践**：

1. **必有**：实验无退出条件 = 灾难
2. **可量化**：用 SLO 指标，不用「感觉慢」
3. **可测试**：先在测试环境验证退出条件
4. **可追溯**：每次退出都有原因记录（用于改进）'''),

        ('与其他站点关系', r'''- **chaos/02-chaos-mesh**：Chaos Mesh 的爆炸半径配置
- **system-design/08-availability**：可用性分级
- **devops/06-best-practices**：灰度发布流程'''),
    ]),

    ('02-chaos-mesh/architecture', 'Chaos Mesh 架构', [
        ('三大核心组件', r'''Chaos Mesh 由三个核心组件构成：

**1. chaos-controller-manager**：

- 监听 CRD 变化（PodChaos / NetworkChaos / StressChaos 等 11 种）
- 调度 chaos daemon 执行故障
- 高可用：Deployment 多副本 + leader election
- 资源占用低（< 256Mi 内存 / 100m CPU）

```yaml
# chaos-controller-manager deployment
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: manager
        image: chaos-mesh/chaos-mesh:v2.7.0
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
```

**2. chaos-daemon**（DaemonSet）：

- 每个 K8s Node 一个 Pod
- 通过 Linux 内核能力（tc / iptables / cgroup）执行故障
- 共享宿主机 PID / Network namespace
- 需要 privileged 权限

```yaml
# chaos-daemon daemonset
spec:
  template:
    spec:
      hostPID: true
      hostNetwork: true
      containers:
      - name: chaos-daemon
        securityContext:
          privileged: true
        volumeMounts:
        - name: var-run-docker
          mountPath: /var/run/docker.sock
```

**3. chaos-dashboard**（可选）：

- Web UI（实验编排 / 监控 / 历史）
- 前后端分离（React + Go）
- 支持 RBAC 权限管理
- 实验模板复用'''),

        ('故障控制器（11 种）', r'''| CRD | 故障类型 | 关键参数 |
|---|---|---|
| PodChaos | pod-kill / pod-failure | mode / selector |
| NetworkChaos | delay / loss / duplicate / corrupt / partition | latency / loss / direction |
| StressChaos | CPU / Memory 抢占 | workers / load |
| IOChaos | 文件系统延迟 / 错误 | latency / errno |
| TimeChaos | 时钟漂移 | timeOffset / clockIds |
| DNSChaos | DNS 解析失败 | patterns |
| KernelChaos | 内核错误注入 | callchain / failtype |
| JVMChaos | JVM GC / OOM / 线程池 | area / type |
| AWSChaos | EC2 / EBS 故障 | action / duration |
| GCPChaos | GCE / Disk 故障 | action / duration |
| AzureChaos | VM / Disk 故障 | action / duration |

**控制器架构**：

每个 CRD 类型对应一个 Controller（在 chaos-controller-manager 内）。Controller 监听 CRD 变化 → 调度 chaos-daemon 执行 → 监控执行状态 → 写入 Status。

**Controller 故障恢复**：

- chaos-daemon 故障 → Controller 重新调度
- chaos-controller-manager 重启 → leader election 选举新 leader
- CRD 删除 → chaos-daemon 清理故障'''),

        ('Workflow 工作流', r'''Workflow CRD 支持多步骤实验编排（DAG）：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Workflow
metadata:
  name: e2e-resilience
spec:
  entry: e2e
  templates:
    - name: e2e
      templateType: Serial  # 顺序执行
      children: [order-pod-kill, payment-network-delay]
    - name: order-pod-kill
      templateType: PodChaos
      duration: "30s"
      podChaos:
        action: pod-kill
        mode: one
        selector:
          namespaces: [order]
    - name: payment-network-delay
      templateType: NetworkChaos
      duration: "60s"
      networkChaos:
        action: delay
        delay: { latency: "200ms" }
```

**Workflow 模板类型**：

- Serial：顺序执行（一个接一个）
- Parallel：并行执行（同时进行）
- Suspend：等待人工确认
- PodChaos / NetworkChaos 等：实际故障

**典型场景**：

- 大促前全链路验证（订单 → 支付 → 库存 → 物流）
- 跨 Region 故障转移演练
- 数据库主从切换验证'''),

        ('与其他站点关系', r'''- **observability/03-prometheus**：Chaos Mesh 指标导出
- **devops/05-cicd-observability**：CI/CD 集成
- **chaos/03-litmus**：Litmus 对比
- **chaos/04-platform-compare**：选型决策'''),
    ]),

    ('02-chaos-mesh/pod-chaos', 'PodChaos 实验', [
        ('PodChaos action 类型', r'''PodChaos 支持四种故障动作：

**1. pod-kill**：

- SIGKILL 杀进程（立即）
- 最常见场景：验证 Pod 重启 + 流量转移
- 应用：Deployments / StatefulSets / DaemonSets

```yaml
spec:
  action: pod-kill
  mode: one
  duration: "30s"
```

**2. pod-failure**：

- 容器启动失败（不可恢复）
- 需要手动删除 Pod 才能恢复
- 应用：测试 readinessProbe / startupProbe

```yaml
spec:
  action: pod-failure
  mode: one
  duration: "60s"
```

**3. container-kill**：

- 杀容器（保留 Pod）
- 验证 kubelet 自动重启容器
- 不重启 Pod（仅重启容器）

```yaml
spec:
  action: container-kill
  mode: one
  duration: "30s"
```

**4. pod-schedule**：

- 延迟调度（不创建 Pod）
- 验证「Pod 不可用时」的 fallback 行为

```yaml
spec:
  action: pod-schedule
  mode: one
  duration: "30s"
```'''),

        ('实战案例：订单服务 Pod kill', r'''**场景**：验证 order-service 在 1 个 Pod 被 kill 时的韧性。

**实验 YAML**：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: order-pod-kill-001
  namespace: chaos-mesh
  labels:
    chaos: production
spec:
  action: pod-kill
  mode: one
  selector:
    namespaces: [order]
    labelSelectors:
      app: order-service
  duration: "30s"
```

**执行**：

```bash
# 应用实验
kubectl apply -f pod-chaos-order.yaml

# 查看实验状态
kubectl get podchaos order-pod-kill-001 -o jsonpath='{.status.conditions[0].message}'

# 查看 Pod 状态（30 秒内被 kill 一次）
kubectl get pods -n order -l app=order-service -w
```

**观察指标**：

```promql
# 5xx 错误率（期望峰值 < 5%）
sum(rate(http_requests_total{status=~"5..",app="order-service"}[5m]))
/ sum(rate(http_requests_total{app="order-service"}[5m]))

# P99 延迟（期望峰值 < 1.5s）
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{app="order-service"}[5m])) by (le))

# Pod 重启次数（期望 = 1）
increase(kube_pod_container_status_restarts_total{pod=~"order-service-.*"}[5m])
```

**预期结果**：

- 错误率峰值 < 5%（单 Pod 流量转移）
- P99 延迟 < 1.5s（无雪崩）
- K8s 自动重启 Pod + 服务自动恢复
- 30 秒内所有指标回到稳态

**故障排查（如果不符合预期）**：

- 错误率 > 5% → readinessProbe 延迟太久 / 流量转移慢
- 延迟 > 1.5s → 缓存击穿 / 连接池重建
- Pod 重启失败 → 镜像拉取问题 / 资源不足'''),

        ('PodChaos 高级用法', r'''**1. 灰度 Pod kill（fixed-percent）**：

```yaml
spec:
  action: pod-kill
  mode: fixed-percent
  value: "10"  # 10% Pods
  selector:
    namespaces: [order]
    labelSelectors: { app: order-service }
```

**2. 限制爆炸半径（指定数量）**：

```yaml
spec:
  action: pod-kill
  mode: fixed
  value: "3"  # 最多 3 个 Pod
```

**3. 跨 namespace 实验**：

```yaml
spec:
  action: pod-kill
  mode: all
  selector:
    namespaces: [order, payment, inventory]  # 3 个 namespace
    labelSelectors: { tier: backend }
```

**4. 通过 annotation 选择**：

```yaml
spec:
  action: pod-kill
  mode: one
  selector:
    annotationSelectors:
      chaos-test: enabled
```

**5. 排除某些 Pod**：

```yaml
spec:
  action: pod-kill
  mode: all
  selector:
    namespaces: [order]
    labelSelectors: { app: order-service }
    # 不包括 has-experiment Pod
    expressionSelectors:
      - { key: has-experiment, operator: NotIn, values: ["true"] }
```'''),

        ('与其他站点关系', r'''- **observability/03-prometheus**：稳态指标
- **chaos/03-litmus**：Litmus pod-delete 对应
- **system-design/08-availability**：可用性验证
- **devops/05-cicd-observability**：CI/CD 集成'''),
    ]),

    ('02-chaos-mesh/network-chaos', 'NetworkChaos 实验', [
        ('NetworkChaos action 类型', r'''NetworkChaos 支持六种网络故障动作：

**1. delay（延迟）**：

```yaml
spec:
  action: delay
  delay:
    latency: "200ms"
    correlation: "75"  # 75% 流量同步延迟
    jitter: "50ms"     # 抖动
  direction: to
```

**2. loss（丢包）**：

```yaml
spec:
  action: loss
  loss:
    loss: "1.0"  # 1% 丢包率
    correlation: "75"
```

**3. duplicate（重复）**：

```yaml
spec:
  action: duplicate
  duplicate:
    duplicate: "0.5"  # 0.5% 重复率
    correlation: "75"
```

**4. corrupt（损坏）**：

```yaml
spec:
  action: corrupt
  corrupt:
    corrupt: "0.1"  # 0.1% 损坏率
    correlation: "75"
```

**5. partition（分区）**：

```yaml
spec:
  action: partition
  direction: both
  target:
    selector:
      namespaces: [default]
    mode: all
```

**6. bandwidth（带宽限制）**：

```yaml
spec:
  action: bandwidth
  bandwidth:
    rate: "1mbps"
    buffer: 10000
```'''),

        ('实战案例：跨 AZ 延迟', r'''**场景**：验证 checkout-service 在跨 AZ 网络延迟 200ms 时的可用性。

**实验 YAML**：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: checkout-az-delay
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
    correlation: "75"
    jitter: "50ms"
  direction: to
  duration: "60s"
```

**观察指标**：

```promql
# P99 延迟（期望 + 200ms 但 < 1.5s）
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{app="checkout-service"}[5m])) by (le))

# 错误率（期望 < 1%）
sum(rate(http_requests_total{status=~"5..",app="checkout-service"}[5m]))
/ sum(rate(http_requests_total{app="checkout-service"}[5m]))

# TCP 重传率（关键信号）
rate(node_netstat_tcp_retransmits[5m])
```

**预期结果**：

- 延迟增加 ~200ms
- 错误率 < 1%（circuit breaker 保护）
- 服务降级生效（fallback 到 cached data）'''),

        ('实战案例：网络分区', r'''**场景**：payment-service 与 order-service 之间网络完全断开。

**实验 YAML**：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: payment-partition
  namespace: chaos-mesh
spec:
  action: partition
  mode: all
  selector:
    namespaces: [payment]
    labelSelectors:
      app: payment-service
  target:
    selector:
      namespaces: [order]
      labelSelectors:
        app: order-service
    mode: all
  direction: both
  duration: "30s"
```

**观察指标**：

```promql
# payment-service 的成功调用率（期望快速下降）
sum(rate(payment_success_total[1m]))
/ sum(rate(payment_total[1m]))

# order-service 的支付相关错误（期望快速上升）
sum(rate(http_requests_total{status=~"5..",app="order-service",endpoint="/pay"}[1m]))
```

**预期结果**：

- order-service 在 5 秒内检测到 payment 不可用
- 熔断器 OPEN（circuit breaker）
- order-service 返回降级结果（fallback）
- 支付流程暂停（不报错，用户友好提示）
- 30 秒后自动恢复'''),

        ('与其他站点关系', r'''- **observability/03-prometheus**：网络指标采集
- **chaos/03-litmus**：pod-network-latency 对应
- **design-pattern/05-architectural-patterns**：Circuit Breaker 验证
- **system-design/08-availability**：多活架构验证'''),
    ]),

    ('02-chaos-mesh/workflow', '工作流编排', [
        ('Workflow 简介', r'''**Workflow 是 Chaos Mesh 的多步骤实验编排（DAG）**。

**典型场景**：

- 大促前全链路验证（订单 → 支付 → 库存 → 物流）
- 跨服务故障传播测试
- 复杂业务场景模拟（用户下单 → 失败 → 重试 → 成功）

**优势**：

- 多步骤串联（真实场景模拟）
- 状态可视化（chaos-dashboard 显示每个步骤）
- 失败自动中止 + 通知
- 与 Schedule 集成（cron 触发）'''),

        ('Workflow YAML', r'''```yaml
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
```'''),

        ('模板类型', r'''**Workflow 模板类型**：

- **Serial**：顺序执行（一个接一个）
- **Parallel**：并行执行（同时进行）
- **Suspend**：等待人工确认
- **PodChaos / NetworkChaos / StressChaos**：实际故障类型

**典型应用**：

- 大促前全链路验证
- 跨 Region 故障转移演练
- 数据库主从切换验证
- 微服务链路故障传播测试'''),

        ('与其他站点关系', r'''- **chaos/02-chaos-mesh/architecture**：Chaos Mesh 架构
- **observability**：监控集成
- **devops/05-cicd-observability**：CI/CD 集成'''),
    ]),

    ('03-litmus/chaos-experiment', 'ChaosExperiment CRD', [
        ('CRD 体系三层', r'''Litmus 的 CRD 分三层：

1. **ChaosExperiment**：故障定义（可复用）
2. **ChaosEngine**：实验编排（绑定 Experiment + Probe）
3. **ChaosSchedule**：定时调度（cron 触发）

**ChaosExperiment 示例**：

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
        resources: ["pods"]
        verbs: ["create", "delete", "get", "list"]
    image: "litmuschaos/go-runner:latest"
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
```

**ChaosEngine 示例**：

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: chaos-engine-example
spec:
  appinfo:
    appns: "default"
    applabel: "app=nginx"
    appkind: "deployment"
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        probe:
          - name: check-nginx-status
            type: httpProbe
            httpProbe:
              url: "http://nginx:80"
              expectedResponseCodes: ["200"]
  jobCleanUpPolicy: "delete"
```

**ChaosSchedule 示例**：

```yaml
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosSchedule
metadata:
  name: weekly-pod-delete
spec:
  schedule: "0 14 * * 1"  # 每周一 14:00
  type: Schedule
  chaosEngine: chaos-engine-example
```'''),

        ('自定义实验（Litmus SDK）', r'''通过 `litmus-go` SDK 编写自定义实验：

```go
package main
import (
    "context"
    "github.com/litmuschaos/litmus-go/pkg/clients"
    "github.com/litmuschaos/litmus-go/pkg/result"
    "github.com/litmuschaos/litmus-go/pkg/utils"
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

**SDK 关键函数**：

- `clients.Init()`：初始化 K8s client
- `clients.GetExperiment()`：获取实验参数
- `result.Initialize()`：初始化结果记录
- `result.RecordSuccess()` / `result.RecordFailure()`：记录结果
- `utils.DeletePod()` / `utils.NetworkDelay()`：实验辅助函数

**编译 + 部署**：

```bash
# 编译 Docker 镜像
docker build -t my-registry/custom-experiment:v1.0 .

# 推送到 registry
docker push my-registry/custom-experiment:v1.0

# 创建 ChaosExperiment CRD（指定镜像）
kubectl apply -f custom-experiment.yaml
```

**与 ChaosHub 集成**：

- 自定义实验注册到 ChaosHub
- 其他团队通过 `kubectl apply` 复用'''),

        ('与其他站点关系', r'''- **observability/03-prometheus**：Probe 集成
- **chaos/02-chaos-mesh**：CRD 对比
- **design-pattern/05-architectural-patterns**：ChaosExperiment 验证'''),
    ]),

    ('03-litmus/probe-check', 'Probe 与 Check', [
        ('五种 Probe 类型', r'''Litmus 提供五种 Probe 类型，用于显式断言实验成功/失败：

**1. httpProbe**：

```yaml
httpProbe:
  url: http://app:80/health
  method: GET
  expectedResponseCodes: ["200"]
  timeout: 5s
  interval: 2s
  retries: 3
```

**2. cmdProbe**：

```yaml
cmdProbe:
  command: "kubectl get pods -l app=nginx -o jsonpath='{.items[?(@.status.phase==\"Running\")].metadata.name}' | wc -l"
  expectedOutput: ">=3"
```

**3. promProbe**：

```yaml
promProbe:
  endpoint: http://prometheus:9090
  query: "rate(http_requests_total{status=~\"5..\"}[5m])"
  comparator: "LessThan"
  value: "0.05"
```

**4. sqlProbe**：

```yaml
sqlProbe:
  connectionInfo:
    host: postgres
    port: 5432
    user: chaos
    password: secret
    dbname: orders
  query: "SELECT COUNT(*) FROM orders WHERE created_at > NOW() - INTERVAL '5 minutes'"
  comparator: "GreaterThan"
  value: "100"
```

**5. k8sProbe**：

```yaml
k8sProbe:
  resourceType: "deployment"
  resourceName: "nginx"
  namespace: "default"
  statusCheck: true
  timeout: 30s
```'''),

        ('Probe 模式', r'''**Continuous（持续探测）**：

- 实验期间持续探测
- 失败立即中止实验
- 默认模式

```yaml
probe:
  - name: check-health
    type: httpProbe
    mode: Continuous
    runProperties:
      interval: 5s
      stopOnFailure: true
```

**OnChaos（故障时探测）**：

- 仅在故障开始时探测一次
- 验证「故障注入后」系统行为

```yaml
probe:
  - name: check-initial-response
    type: httpProbe
    mode: OnChaos
    runProperties:
      timeout: 30s
```

**EOT（End of Test）**：

- 故障结束时探测
- 验证「故障恢复后」系统行为

```yaml
probe:
  - name: check-recovery
    type: httpProbe
    mode: EOT
    runProperties:
      timeout: 60s
```'''),

        ('Probe Property 详解', r'''**runProperties 完整配置**：

```yaml
probe:
  - name: comprehensive-check
    type: promProbe
    mode: Continuous
    runProperties:
      probeTimeout: 60s       # 总超时（超过则失败）
      interval: 5s            # 探测间隔
      retry: 3                # 重试次数（连续 3 次失败才算失败）
      stopOnFailure: true     # 失败立即中止实验
      verbosity: info         # 日志级别（debug/info/warn/error）
```

**Probe 状态机**：

```
Probe Pending → Probe Running → Probe Completed
                  │
                  └→ Probe Failed (重试中)
```

**Probe 与 ChaosResult 关联**：

- Probe 成功 → ChaosResult verdict: Pass
- Probe 失败 → ChaosResult verdict: Fail

**实战建议**：

1. **多维度**：同时 Probe 业务指标 + 系统指标 + 资源
2. **持续探测**：Continuous 模式捕获「瞬时失败」
3. **快速失败**：stopOnFailure 减少实验影响
4. **合理重试**：retry=3 避免「假阳性」'''),

        ('与其他站点关系', r'''- **observability/03-prometheus**：Prometheus Probe
- **devops/05-cicd-observability**：CI/CD 集成
- **chaos/02-chaos-mesh**：Chaos Mesh 间接验证对比'''),
    ]),

    ('03-litmus/sdk', 'Litmus SDK', [
        ('SDK 核心 API', r'''Litmus 提供 Go SDK 用于编写自定义实验。

**SDK 核心 API**：

```go
package main
import (
    "context"
    "github.com/litmuschaos/litmus-go/pkg/clients"
    "github.com/litmuschaos/litmus-go/pkg/log"
    "github.com/litmuschaos/litmus-go/pkg/result"
    "github.com/litmuschaos/litmus-go/pkg/utils"
    appsv1 "k8s.io/api/apps/v1"
    corev1 "k8s.io/api/core/v1"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
)

func main() {
    clients.Init()
    experimentsDetails := clients.GetExperiment()
    result.Initialize(context.Background(), clients.ClientSet, experimentsDetails)

    // 实验逻辑
    if err := deletePod(); err != nil {
        result.RecordFailure(context.Background(), fmt.Sprintf("failed: %v", err))
        return
    }
    result.RecordSuccess(context.Background(), "pod deleted")
}
```'''),

        ('实验参数定义', r'''**实验参数定义（环境变量）**：

```go
type ExperimentsDetails struct {
    ExperimentName           string
    AppKind                  string
    AppNamespace             string
    AppLabel                 string
    ChaosDuration            string
    ChaosInterval            string
    TargetPods               string
    PodsAffectedPerc         string
    Force                    string
}
```'''),

        ('编写自定义实验步骤', r'''1. 在 `litmus-go/contrib/developer-experiments/` 创建新目录
2. 实现 main.go（使用 SDK）
3. 添加 Dockerfile
4. 创建 ChaosExperiment CRD（指向你的镜像）
5. 注册到 ChaosHub（GitHub PR）'''),

        ('SDK 工具函数', r'''**SDK 工具函数**：

```go
// Pod 操作
utils.GetPod(client, name, namespace)
utils.DeletePod(client, name, namespace, force)
utils.GetDeployments(client, namespace, label)

// 网络操作
utils.NetworkDelay(targetPod, latency, jitter)
utils.NetworkLoss(targetPod, lossPercent)

// 资源操作
utils.StressCPU(pod, workers, load)
utils.StressMemory(pod, vmBytes)

// 结果记录
result.RecordSuccess(ctx, message)
result.RecordFailure(ctx, message)
```'''),

        ('与社区贡献', r'''**与社区贡献**：

- Litmus 社区欢迎贡献新实验
- 标准实验仓库：https://github.com/litmuschaos/litmus-go
- 提交 PR → ChaosHub 自动索引

**实战建议**：

- 复用 SDK 工具函数（避免重复造轮子）
- 错误处理要完整（result.RecordFailure 必须调用）
- 镜像要小（multi-stage build）
- 测试要全（unit test + integration test）'''),
    ]),

    ('04-platform-compare/mesh-vs-litmus', 'Chaos Mesh vs Litmus', [
        ('架构对比', r'''| 维度 | Chaos Mesh | Litmus |
|---|---|---|
| CRD 数量 | 10+ 故障类型 | 3 核心 |
| 故障定义位置 | Chaos CRD 内联 | ChaosExperiment 单独资源 |
| Probe 机制 | 间接验证（dashboard / Grafana） | 内置 5 种 Probe 类型 |
| 工作流 | Workflow CRD（DAG） | ChaosEngine 串联 |
| 调度 | Schedule CRD（cron） | ChaosSchedule CRD |
| 多运行时 | 仅 K8s | K8s + VM（litmus-go SDK） |
| UI | chaos-dashboard | Litmus Portal |
| 中文社区 | 活跃（PingCAP） | 一般 |
| 学习曲线 | 中（需 K8s） | 中（需 K8s + Probe） |'''),

        ('故障类型对比', r'''| 故障类型 | Chaos Mesh | Litmus |
|---|---|---|
| Pod Kill | PodChaos | pod-delete (ChaosHub) |
| Pod Restart | PodChaos | （需自定） |
| 网络延迟 | NetworkChaos delay | pod-network-latency |
| 网络丢包 | NetworkChaos loss | pod-network-loss |
| 网络分区 | NetworkChaos partition | pod-network-partition |
| CPU 抢占 | StressChaos cpu | pod-cpu-hog |
| 内存压力 | StressChaos memory | pod-memory-hog |
| 磁盘压力 | IOChaos | disk-fill |
| DNS 故障 | DNSChaos | dns-chaos |
| 时间漂移 | TimeChaos | time-chaos |
| 进程杀 | PodChaos | （需自定） |
| 内核故障 | KernelChaos | （需自定） |
| JVM 故障 | JVMChaos | （需自定） |
| 云资源故障 | AWSChaos/GCPChaos/AzureChaos | （需自定） |

**Chaos Mesh 优势**：故障类型丰富（含 JVMChaos / KernelChaos / 云资源故障）

**Litmus 优势**：ChaosHub 实验市场（50+ 预置实验）+ Probe 体系完整'''),

        ('性能对比', r'''**1000 个 Pod 注入网络延迟**：

- Chaos Mesh：daemonSet 模式，~5 秒完成
- Litmus：chaos-runner Pod 模式，~15 秒完成（要起 Runner）

**大规模实验（500+ 故障同时运行）**：

- Chaos Mesh：chaos-daemon 直接执行，无额外开销
- Litmus：每个实验独立 Pod，资源开销大

**冷启动时间**：

- Chaos Mesh：< 1 秒（CRD apply 即可）
- Litmus：~15 秒（创建 chaos-runner Pod + 注入实验）'''),

        ('选型建议', r'''**选 Chaos Mesh**：

- K8s only
- 性能要求高（大量故障并行）
- 中文社区（PingCAP 主导）
- 喜欢 CRD 直接表达故障

**选 Litmus**：

- K8s + VM（多运行时）
- Probe 强需求（显式断言）
- 团队不熟 K8s（Portal UI 友好）
- 需要 ChaosHub 实验市场

**混合使用**：

- K8s 层用 Chaos Mesh（基础设施故障）
- 应用层用 Litmus（Probe 验证 SLO）'''),

        ('与其他站点关系', r'''- **chaos/01-foundations**：选型决策
- **chaos/04-platform-compare/decision-tree**：详细决策树
- **observability**：监控集成'''),
    ]),

    ('04-platform-compare/open-vs-commercial', '开源 vs 商业（Gremlin）', [
        ('Gremlin 商业模式', r'''**Gremlin 公司**：

- 2018 商业化 / 总部旧金山
- 创始人：Kolton Andrus（前 AWS Chaos Engineer）
- 累计融资：5500 万美元（B / C 轮）

**产品套餐**：

- **Free**：$0，10 个 Pod，单用户
- **Pro**：$5k/月（年付 $60k），500 Pod，5 用户
- **Enterprise**：$20k+/月（年付 $240k+），无限 Pod，无限用户
- **Self-Hosted Enterprise**：定制（年付 $500k+）

**典型客户**：

- Salesforce / Twilio / Datadog
- Atlassian / AMD / Credible
- Mailchimp / Zola / Remind

**Gremlin 独特优势**：

1. **SaaS 控制台**：Web UI（无 K8s YAML 基础也能用）
2. **故障类型最全**：12 大类 100+ 故障
3. **审批流**：实验需 manager 审批
4. **审计日志**：SOC2 / HIPAA / PCI-DSS 认证
5. **状态注入**：业务层故障（如「注入 30% 订单失败」）
6. **游戏日服务**：Gremlin 团队提供专业 Game Day 主持人'''),

        ('Gremlin vs 开源对比', r'''| 维度 | Chaos Mesh / Litmus | Gremlin |
|---|---|---|
| 成本 | $0 | $60k-$240k/年 |
| 数据合规 | 完全自托管 | 默认出境（可配 EU） |
| 故障覆盖 | 10-15 类 | 12 大类 100+ |
| 学习曲线 | 中（需 K8s） | 低（Web UI） |
| 审批流 | 需自建 | 内置 |
| 审计 | K8s audit | SOC2 内置 |
| 定制 | 高度灵活 | 黑盒 |

**Gremlin 劣势**：

1. **贵**：年付 $60k+（Pro）起步
2. **Agent 闭源**：故障逻辑在 Gremlin 私有二进制
3. **数据出境**：实验日志默认上传 Gremlin 云（GDPR 风险）
4. **耦合度高**：从 Pro 迁到自托管很困难（vendor lock-in）

**开源方案优势**：

1. **零成本**：免费
2. **数据不出境**：完全自托管
3. **可定制**：CRD + Go SDK 任意修改
4. **中文社区**：Chaos Mesh 中文文档完善'''),

        ('选型决策', r'''**选 Gremlin**：

- 团队 < 5 SRE + 合规要求高
- 预算 > $50k/年
- 无 K8s 基础（需要 Web UI）
- 想要「游戏日」托管服务

**选开源（Chaos Mesh / Litmus）**：

- 团队技术强（K8s 熟练）
- 数据合规要求高（不出境）
- 预算紧张 / 开源文化
- 需要深度定制（修改故障逻辑）

**混合方案**：

- 内部实验：开源（成本低）
- 商业验证：Gremlin（专业服务）

**关键问题**：你买的不是工具，是「**让团队敢做混沌工程的能力**」。

- 如果团队技术强 + 自托管文化 → 开源
- 如果团队运维弱 + 合规压力大 → 商业'''),

        ('与其他站点关系', r'''- **chaos/04-platform-compare/decision-tree**：选型决策树
- **observability**：监控集成
- **devops**：CI/CD 集成'''),
    ]),

    ('04-platform-compare/decision-tree', '选型决策树', [
        ('5 步选型法', r'''**Step 1：你的运行时是什么？**

- **仅 K8s** → Chaos Mesh 或 Litmus（两大开源主力）
- **K8s + VM** → Litmus / Gremlin / ChaosBlade（多运行时支持）
- **VM + Host**（传统数据中心） → Gremlin / ChaosBlade（覆盖宿主机）
- **多云**（AWS/GCP/Azure） → Gremlin / Steadybit / 云厂商原生命令

**Step 2：你的预算？**

- **$0**（开源） → Chaos Mesh / Litmus / ChaosBlade
- **$5k-50k/年**（商业） → Gremlin（Pro 套餐）
- **$100k+/年**（企业） → Steadybit / Gremlin Enterprise

**Step 3：你的团队规模？**

- **3 人以下**：Chaos Mesh（CRD 直接 kubectl，UI 可选）
- **5-10 人**：Litmus（Portal UI + 共享实验库）
- **20 人以上**：Gremlin（权限管理 + 审批流 + 审计）

**Step 4：你的合规要求？**

- **PCI-DSS / HIPAA**：Gremlin（审计日志完整）/ Steadybit（SOC2）
- **GDPR**：开源（数据不出公司）/ Gremlin Enterprise（EU 数据中心）

**Step 5：你的实验类型？**

- **基础设施层**（Pod/Node/Network） → Chaos Mesh / Litmus / ChaosBlade 都能
- **应用层**（HTTP/SQL/缓存） → Litmus Probe 最强
- **业务层**（订单/支付） → Litmus 自定义 Probe + 业务指标'''),

        ('典型选型示例', r'''**示例 1：互联网初创公司（50 人）**：

- 运行时：仅 K8s（EKS）
- 预算：$0
- 团队：3 SRE
- 合规：无特殊要求
- 实验：Pod kill / 网络延迟
- **推荐**：Chaos Mesh

**示例 2：金融科技公司（200 人）**：

- 运行时：K8s + 传统 VM
- 预算：$50k/年
- 团队：8 SRE + 4 DevOps
- 合规：PCI-DSS
- 实验：Pod kill / Redis failover / 业务层故障
- **推荐**：Litmus + Gremlin Pro 混合

**示例 3：传统银行（5000 人）**：

- 运行时：多云 + 私有数据中心
- 预算：$200k+/年
- 团队：30+ SRE
- 合规：SOC2 + GDPR + 银保监
- 实验：跨 Region 故障转移 / 数据库主从切换
- **推荐**：Gremlin Enterprise + Steadybit

**示例 4：电商大促准备**：

- 运行时：阿里云（K8s）
- 预算：$20k/年
- 团队：10 SRE
- 合规：等保三级
- 实验：JVM 故障 / 流量调度 / 多活切换
- **推荐**：ChaosBlade + AHAS（阿里云）'''),

        ('与其他站点关系', r'''- **chaos/04-platform-compare/mesh-vs-litmus**：深度对比
- **chaos/04-platform-compare/open-vs-commercial**：商业模式对比
- **observability**：监控集成对比'''),
    ]),

    ('05-resilience-patterns/retry-backoff', '重试与退避', [
        ('重试三要素', r'''**1. 重试条件**：

- 重试：网络错误 / 超时 / 5xx / 特定业务码
- 不重试：4xx（业务错误 / 权限 / 参数错误）

**2. 退避策略**：

- **指数退避（Exponential Backoff）**：`delay = base * 2^attempt`
  - 示例：1s, 2s, 4s, 8s, 16s
- **指数退避 + 抖动（Jitter）**：`delay = base * 2^attempt * (1 + random(0, 0.5))`
  - 避免「thundering herd」（多个客户端同时重试）
- **固定退避**：固定 1s（不推荐，易雪崩）

**3. 重试上限**：

- 最大次数：3-5 次（避免无限重试）
- 最大时长：30 秒（总耗时上限）'''),

        ('Resilience4j 实现（Java）', r'''```java
RetryConfig config = RetryConfig.custom()
    .maxAttempts(3)
    .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(
        Duration.ofMillis(500),  // initialInterval
        2.0,                     // multiplier
        0.5                      // randomizationFactor
    ))
    .retryExceptions(IOException.class, TimeoutException.class)
    .build();

Retry retry = Retry.of("paymentService", config);

CheckedSupplier<String> supplier = Retry.decorateCheckedSupplier(retry,
    () -> paymentClient.charge(orderId, amount));

try {
    return supplier.get();
} catch (Throwable t) {
    return "fallback";
}
```'''),

        ('Go 实现（cenkalti/backoff）', r'''```go
func chargeWithRetry(ctx context.Context, orderID string, amount int) error {
    backoff := backoff.NewExponentialBackOff()
    backoff.InitialInterval = 500 * time.Millisecond
    backoff.MaxInterval = 30 * time.Second
    backoff.MaxElapsedTime = 2 * time.Minute

    operation := func() error {
        _, err := paymentClient.Charge(ctx, orderID, amount)
        return err
    }
    return backoff.RetryNotify(operation, backoff.WithContext(ctx), onError)
}
```

**参数调优**：

- `InitialInterval`：初始延迟（500ms - 1s）
- `MaxInterval`：最大延迟（30s - 1min）
- `MaxElapsedTime`：总耗时上限（1min - 5min）
- `Multiplier`：指数倍数（2.0 - 3.0）'''),

        ('幂等性要求', r'''**重试必须保证「多次调用效果一致」**。

**支付场景**：

```http
POST /payments HTTP/1.1
Host: api.example.com
Authorization: Bearer xxx
Idempotency-Key: ord_12345_pay_v1  # 关键
Content-Type: application/json

{"orderId": "12345", "amount": 1000}
```

服务端处理：

```python
def charge_with_idempotency(order_id, amount, idempotency_key):
    # 检查 Idempotency-Key 是否已处理
    cached = redis.get(f"idempotency:{idempotency_key}")
    if cached:
        return cached

    # 实际扣款
    result = payment_client.charge(order_id, amount)

    # 缓存结果（24 小时）
    redis.setex(f"idempotency:{idempotency_key}", 86400, result)
    return result
```

**数据库乐观锁**：

```sql
UPDATE accounts
SET balance = balance - 100
WHERE account_id = 12345
  AND version = 1  -- 乐观锁
  AND balance >= 100;
-- 如果影响行数 = 0 → 重试
```'''),

        ('与其他站点关系', r'''- **chaos/05-resilience-patterns/circuit-breaker**：重试 + 熔断组合
- **design-pattern/05-architectural-patterns**：重试模式
- **system-design/08-availability**：可用性原则'''),
    ]),

    ('05-resilience-patterns/circuit-breaker', '熔断器', [
        ('三态状态机', r'''熔断器三态：

```
       成功 / 错误率低于阈值
CLOSED ─────────────────────────► CLOSED (继续请求)
  │                                    ▲
  │ 错误率超阈值                        │
  ▼                                    │
OPEN ──── 经过 sleepWindow ────► HALF_OPEN
  │                                    │
  │ 直接拒绝                            │
  ▼                                    │
直接失败 (Fallback)                  探测请求
                                  成功→CLOSED
                                  失败→OPEN
```

**CLOSED（关闭）**：正常状态，请求正常通过。

**OPEN（开启）**：错误率超阈值，所有请求直接失败（不调用下游）。

**HALF_OPEN（半开）**：经过 sleepWindow 后，允许少量探测请求。成功 → CLOSED，失败 → OPEN。'''),

        ('Resilience4j 实现', r'''```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)
    .slowCallRateThreshold(80)
    .slowCallDurationThreshold(Duration.ofSeconds(2))
    .slidingWindowSize(100)
    .minimumNumberOfCalls(20)
    .waitDurationInOpenState(Duration.ofSeconds(30))
    .build();

CircuitBreaker breaker = CircuitBreaker.of("paymentService", config);

CheckedSupplier<String> supplier = CircuitBreaker.decorateCheckedSupplier(breaker,
    () -> paymentClient.charge(orderId, amount));

try {
    return supplier.get();
} catch (CallNotPermittedException e) {
    return "fallback";
}
```

**关键参数**：

- `failureRateThreshold`：错误率阈值（默认 50%）
- `slidingWindowSize`：统计窗口（默认 100 请求）
- `permittedNumberOfCallsInHalfOpenState`：半开探测请求数（默认 10）
- `waitDurationInOpenState`：OPEN 状态持续时间（默认 60s）
- `slowCallDurationThreshold`：慢调用阈值（默认 2s）
- `slowCallRateThreshold`：慢调用率阈值（默认 100%）'''),

        ('gobreaker（Go）实现', r'''```go
settings := gobreaker.Settings{
    Name:        "paymentService",
    MaxRequests: 5,            // HALF_OPEN 最大探测
    Interval:    60 * time.Second,
    Timeout:     30 * time.Second,
    ReadyToTrip: func(counts gobreaker.Counts) bool {
        failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
        return counts.Requests >= 10 && failureRatio >= 0.5
    },
}
cb := gobreaker.NewCircuitBreaker(settings)
result, err := cb.Execute(func() (interface{}, error) {
    return paymentClient.Charge(ctx, orderID, amount)
})
```'''),

        ('熔断器与重试组合', r'''**调用链**：

```
调用方 → Retry → CircuitBreaker → 实际下游
```

**原则**：

- Retry 在 CircuitBreaker 外层
- 避免熔断状态变化干扰重试逻辑
- Retry + CircuitBreaker 都失败 → 触发 Fallback

**陷阱**：重试次数过多会「穿透」熔断器（破坏熔断效果）。例：每次重试 3 次 → 实际请求 9 次。

**Resilience4j 组合**：

```java
// 顺序：Retry → CircuitBreaker → Bulkhead → 实际调用
Supplier<String> decorated = Decorators.ofSupplier(() -> paymentClient.charge(orderId, amount))
    .withRetry(retry)
    .withCircuitBreaker(breaker)
    .withBulkhead(bulkhead)
    .withFallback(Arrays.asList(CallNotPermittedException.class, BulkheadFullException.class),
                  e -> "fallback")
    .decorate();
```'''),

        ('与其他站点关系', r'''- **chaos/05-resilience-patterns/retry-backoff**：重试 + 熔断
- **design-pattern/05-architectural-patterns**：Circuit Breaker 模式
- **system-design/08-availability**：可用性原则'''),
    ]),

    ('05-resilience-patterns/rate-limit-degrade', '限流与降级', [
        ('限流算法', r'''**1. 令牌桶（Token Bucket）**：

- 桶容量 N，每 R 秒加 1 个令牌
- 请求消耗 1 个令牌，无令牌则拒绝
- 允许突发（桶满时可瞬时 N 个）

**2. 漏桶（Leaky Bucket）**：

- 请求进入桶，桶以固定速率漏水
- 桶满则溢出（拒绝）
- 强制平滑输出

**3. 滑动窗口（Sliding Window）**：

- 滚动时间窗口（1 分钟内最多 N 个请求）
- 比固定窗口更平滑

**4. 计数器（Counter）**：

- 简单：每分钟一个计数器
- 缺点：窗口边界突刺（59 秒 + 1 秒可瞬时 2N）'''),

        ('Sentinel（阿里）实现', r'''```java
@SentinelResource(value = "orderCreate", blockHandler = "handleBlock")
public Order createOrder(OrderRequest req) {
    return orderService.create(req);
}

public Order handleBlock(OrderRequest req, BlockException e) {
    throw new RateLimitException("too many requests");
}

FlowRule rule = new FlowRule("orderCreate")
    .setGrade(RuleConstant.FLOW_GRADE_QPS)
    .setCount(1000);
FlowRuleManager.loadRules(Collections.singletonList(rule));
```

**Sentinel 特性**：

- QPS 限流
- 并发线程数限流
- 慢调用比例降级
- 异常比例降级
- Sentinel Dashboard 实时监控'''),

        ('Istio 限流（Envoy Filter）', r'''```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: rate-limit
spec:
  configPatches:
  - applyTo: HTTP_FILTER
    match:
      context: SIDECAR_INBOUND
      listener:
        filterChainMatch:
          destinationPort: 8080
    patch:
      operation: INSERT_BEFORE
      value:
        name: envoy.filters.http.local_ratelimit
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
          stat_prefix: http_local_rate_limiter
          token_bucket:
            max_tokens: 1000
            tokens_per_fill: 1000
            fill_interval: 60s
```'''),

        ('降级策略', r'''**1. 功能降级**：

- 大促期间关闭「推荐」「个性化」非核心功能
- 关闭「历史订单查询」→ 只显示最近 7 天
- 关闭「评论 / 评分」

**2. 数据降级**：

- 用 cached data 替代实时查询
- 用 default value（如返回空列表）
- 用上次成功结果（stale-while-error）

**3. 链路降级**：

- 主链路 → 简化版（跳过非关键步骤）
- 同步链路 → 异步链路

**4. 自动 vs 手动降级**：

- 自动：根据 SLO / 错误率自动触发
- 手动：运维手动开关（如「双 11 大促开关」）'''),

        ('与其他站点关系', r'''- **chaos/05-resilience-patterns/circuit-breaker**：熔断 + 降级
- **design-pattern/05-architectural-patterns**：限流模式
- **observability/08-alerting**：限流告警'''),
    ]),

    ('05-resilience-patterns/bulkhead', '舱壁与隔离', [
        ('隔离层级', r'''**1. 线程池隔离**：

- 每个下游服务一个独立线程池
- payment-service 线程池满 → order-service 不受影响
- 缺点：线程上下文切换开销

**2. 信号量隔离**：

- 轻量（不切换线程）
- 仅限制并发数，不隔离线程
- 适用：纯计算型调用

**3. 进程隔离**：

- 每个下游服务独立进程（Sidecar）
- Istio / Linkerd 默认采用

**4. 集群隔离**：

- 物理集群分组（核心 / 非核心）
- 大促前把核心服务独立集群'''),

        ('Resilience4j Bulkhead（线程池版）', r'''```java
BulkheadConfig config = BulkheadConfig.custom()
    .maxConcurrentCalls(20)
    .maxWaitDuration(Duration.ofMillis(500))
    .build();

Bulkhead bulkhead = Bulkhead.of("paymentService", config);

CheckedSupplier<String> supplier = Bulkhead.decorateCheckedSupplier(bulkhead,
    () -> paymentClient.charge(orderId, amount));
```'''),

        ('Sidecar 隔离（Istio）', r'''每个 Pod 一个 Envoy Sidecar，自动隔离：

- payment-service Pod 的 Envoy 故障 → order-service 不受影响
- Envoy 资源（CPU / 内存）独立管理

**Istio 资源隔离配置**：

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    sidecar.istio.io/proxyCPU: "200m"
    sidecar.istio.io/proxyMemory: "256Mi"
    sidecar.istio.io/proxyCPULimit: "500m"
    sidecar.istio.io/proxyMemoryLimit: "1Gi"
```

**Outbound 隔离**：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: payment-service
spec:
  host: payment-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        h2UpgradePolicy: UPGRADE
        maxRequestsPerConnection: 10
```'''),

        ('数据库连接池隔离', r'''**HikariCP 多实例**：

```java
@Bean(name = "orderDataSource")
@ConfigurationProperties("spring.datasource.order")
public DataSource orderDataSource() {
    return DataSourceBuilder.create().build();
}

@Bean(name = "paymentDataSource")
@ConfigurationProperties("spring.datasource.payment")
public DataSource paymentDataSource() {
    return DataSourceBuilder.create().build();
}
```

**配置**：

```yaml
spring:
  datasource:
    order:
      url: jdbc:mysql://order-db:3306/order
      hikari:
        maximum-pool-size: 20
    payment:
      url: jdbc:mysql://payment-db:3306/payment
      hikari:
        maximum-pool-size: 10
```

**效果**：

- 慢查询拖垮 payment 连接池 → 不影响 order
- 每个服务独立的连接池（独立资源）'''),

        ('与其他站点关系', r'''- **design-pattern/05-architectural-patterns**：Bulkhead 模式
- **system-design/08-availability**：隔离原则
- **architecture/05-microservices**：微服务隔离'''),
    ]),

    ('05-resilience-patterns/multi-region-dr', '多活与灾备', [
        ('多活 vs 灾备', r'''**多活（Active-Active）**：

- 多个 Region 同时服务流量
- 任意 Region 故障，其他 Region 接管
- 资源利用率高（无闲置）

**灾备（Active-Passive / DR）**：

- 主 Region 服务流量，备 Region 待机
- 主 Region 故障，备 Region 接管
- 资源利用率低（备 Region 闲置）'''),

        ('灾备 RTO / RPO 矩阵', r'''| 级别 | RTO（恢复时间） | RPO（数据丢失） | 成本 |
|---|---|---|---|
| L0（无灾备） | 小时级 | 不保证 | $0 |
| L1（备份恢复） | 24 小时 | 24 小时 | $ |
| L2（同城灾备） | 1 小时 | 几分钟 | $$ |
| L3（异地灾备） | 4 小时 | 几分钟 | $$$ |
| L4（同城多活） | 分钟级 | 秒级 | $$$$ |
| L5（异地多活） | 分钟级 | 秒-分钟 | $$$$$ |

**金融业典型要求**：

- 支付系统：L4（同城多活）
- 银行核心：L5（异地多活）'''),

        ('多活架构层级', r'''**1. DNS 层**：

- 智能 DNS（Route 53 / AliDNS）按地理位置解析
- 健康检查 + 故障转移

**2. 全球负载均衡**：

- AWS Global Accelerator / Cloudflare Spectrum
- 任意cast IP（Anycast）

**3. 数据库同步**：

- 同步复制（强一致）：性能损耗
- 异步复制（最终一致）：性能高，但 RPO > 0
- 双向同步（Active-Active）：冲突处理复杂'''),

        ('混沌验证', r'''**1. Region kill 实验**：

- chaos-mesh AWSChaos：随机停止一个 AZ 的 EC2
- 验证：流量 100% 自动转移到其他 AZ
- 验证：RTO < 5 分钟（自动恢复）

**2. 数据库主从切换实验**：

- chaos-mesh + Redis Sentinel：手动 failover
- 验证：写请求自动路由到新主
- 验证：RPO < 1 秒（异步复制延迟）

**3. DNS 切换实验**：

- 注入 DNS 解析失败
- 验证：客户端 failover 到备用 DNS'''),

        ('多活陷阱', r'''- 不考虑数据冲突（同一订单在两个 Region 创建）
- 时钟不同步（订单时间错乱）
- 流量调度策略简单（无权重 / 无健康检查）
- 灾备演练不足（主 Region 真挂了切不动）

**典型多活案例**：

- **阿里淘宝**：3 地 5 中心（同城 + 异地）
- **AWS S3**：11 个 9 的可用性（多区域存储）
- **Netflix**：跨 AWS Region 多活 + Chaos Monkey 持续验证'''),

        ('与其他站点关系', r'''- **system-design/08-availability**：可用性分级
- **design-pattern/05-architectural-patterns**：多活架构模式
- **chaos/01-foundations/blast-radius**：爆炸半径分级'''),
    ]),

    ('06-game-day/exercise-design', '演练设计', [
        ('5 步设计法', r'''**Step 1：确定演练目标**

- 示例：「验证大促期间 Region 故障时的应急能力」
- 目标要 SMART：Specific / Measurable / Achievable / Relevant / Time-bound

**Step 2：选择故障场景**

- 故障画像优先级（P × I 模型）
- 本季度 TOP 5 故障

**Step 3：设计爆炸半径**

- L1（首次）：1 Pod / 5 分钟
- L2（成熟）：10% 流量 / 30 分钟
- L3（大促前）：跨 Region / 2 小时

**Step 4：定义观察指标**

- 业务指标：订单成功率 / GMV
- 系统指标：错误率 / P99 延迟
- 流程指标：oncall 响应时间

**Step 5：制定回滚预案**

- 自动化：SLO breach → 自动 kill
- 退出条件：业务影响 > 阈值'''),

        ('故障场景选择（P × I 模型）', r'''**P（Probability 发生概率） × I（Impact 业务影响）**：

| 故障 | P | I | 优先级 |
|---|---|---|---|
| Redis 主从切换 | 高 | 高 | 高 |
| 支付网关超时 | 中 | 高 | 高 |
| 数据库慢查询 | 高 | 中 | 中 |
| CDN 节点失效 | 中 | 中 | 中 |
| Region 断网 | 低 | 极高 | 高 |

**优先级排序**：

1. Redis 主从切换（高 P × 高 I）
2. 支付网关超时（中 P × 高 I）
3. Region 断网（低 P × 极高 I）
4. 数据库慢查询（高 P × 中 I）
5. CDN 节点失效（中 P × 中 I）'''),

        ('爆炸半径分级', r'''| 级别 | 流量 | 实例 | 区域 | 时长 |
|---|---|---|---|---|
| L1 | 0% | 1 Pod | 单 AZ | 5s |
| L2 | 1% | 10% Pods | 单 AZ | 30s |
| L3 | 10% | 50% Pods | 单 Region | 5min |
| L4 | 100% | 100% Pods | 多 Region | 30min |

**渐进原则**：

- 首次游戏日从 L1 开始
- 每次游戏日升级 1 级
- 大促前可短时间 L4（持续运行验证）'''),

        ('退出条件设计', r'''**业务退出条件**：

- 订单成功率 < 95% → 中止
- P99 延迟 > 3s → 中止
- 错误率 > 5% → 中止

**时间退出条件**：

- 单场景超时 30 分钟 → 中止
- 整体演练超时 8 小时 → 中止

**错误退出条件**：

- 连续失败 3 次 → 中止
- 同一失败模式重复出现 → 中止

**退出条件必设**：

- 没有退出条件 = 灾难
- 指挥官「红色按钮」一键 kill all chaos'''),

        ('与其他站点关系', r'''- **chaos/06-game-day/roles**：角色分工
- **chaos/06-game-day/retro**：复盘改进
- **observability/03-prometheus**：监控指标'''),
    ]),

    ('06-game-day/roles', '角色分工', [
        ('核心角色', r'''**1. 指挥官（Game Master / Commander）**：

- 主持游戏日
- 选择故障场景 + 决定爆炸半径
- 决定「继续 / 暂停 / 中止」
- **绝对权威**：业务影响超阈值 → 立即 kill chaos

**2. 注入者（Injector）**：

- 执行 chaos 命令（kubectl apply / ChaosBlade CLI）
- 监控 chaos 状态
- 与指挥官确认爆炸半径调整

**3. 观察员（Observer）**：

- 监控 dashboard（Grafana / Kibana / Prometheus）
- 实时报告指标变化
- 不直接干预，只观察

**4. 记录员（Scribe）**：

- 记录每个时间点的现象
- 录音 + 截图 + 时间线
- 后续输出 Postmortem 报告

**5. oncall 工程师（On-call Engineer）**：

- 真实响应告警
- 不知道是演练（避免「演戏」）
- 测试真实应急流程'''),

        ('辅助角色', r'''**6. 业务代表（Business Owner）**：

- 监控业务指标（订单 / GMV）
- 决定是否「业务可接受」

**7. 客服代表（Customer Support）**：

- 监控用户投诉
- 测试客服应对流程

**8. 旁观者（Observer / Learner）**：

- 团队成员学习
- 不直接参与，但可提问'''),

        ('典型团队组成', r'''**中型公司（8-12 人）**：

- 指挥官 1 人
- 注入者 2 人
- 观察员 1 人
- 记录员 1 人
- oncall 工程师 3-5 人（不同服务）
- 业务代表 1 人
- 客服代表 1 人

**大型公司（15-20 人）**：

- 指挥官 1 人 + 副指挥官 1 人
- 注入者 3-4 人
- 观察员 2-3 人
- 记录员 1-2 人
- oncall 工程师 5-8 人（不同服务）
- 业务代表 2-3 人
- 客服代表 1 人
- 旁观者 3-5 人

**小型团队（4-6 人）**：

- 指挥官 1 人（兼任）
- 注入者 1 人
- 观察员 1 人
- oncall 工程师 1-2 人'''),

        ('角色职责矩阵', r'''| 角色 | 故障注入 | 监控 | 决策 | 复盘 |
|---|---|---|---|---|
| 指挥官 | 审批 | 决策 | ✅ | 主持 |
| 注入者 | ✅ | 监控 | - | 参与 |
| 观察员 | - | ✅ | - | 参与 |
| 记录员 | - | 时间线 | - | ✅ |
| oncall | - | 监控 | 应急 | 反馈 |
| 业务代表 | - | 业务指标 | 业务决策 | 评估 |
| 客服代表 | - | 用户投诉 | - | 反馈 |

**职责分离原则**：

- 注入 ≠ 监控（避免利益冲突）
- 监控 ≠ 决策（避免「自导自演」）
- 决策 ≠ 应急（指挥官 vs oncall）'''),

        ('与其他站点关系', r'''- **chaos/06-game-day/exercise-design**：演练设计
- **chaos/06-game-day/retro**：复盘改进
- **architecture/05-microservices**：oncall Runbook'''),
    ]),

    ('06-game-day/retro', '复盘与改进', [
        ('Postmortem 文化', r'''**Blameless（无指责）原则**：

- 聚焦「系统如何失败」而非「谁犯了错」
- 故障 = 学习机会
- 严禁「追责文化」

**事实优先**：

- 时间线 + 数据 + 截图
- 不猜测、不臆断、不甩锅

**学习导向**：

- 每个故障都是改进机会
- 输出 Action Items（不是抱怨）

**公开分享**：

- 内部 Wiki / 公众号
- 跨团队学习'''),

        ('复盘会议程（90 分钟）', r'''```
00:00 - 00:15  时间线回放（记录员主导）
  ├─ 投影时间线
  ├─ 每个关键节点：发生了什么 + 谁响应了 + 决策是什么
  └─ 客观陈述（无指责）

00:15 - 00:45  oncall 感受分享
  ├─ oncall A：「收到告警后我以为是真的，10 分钟才发现是演练」
  ├─ oncall B：「诊断假设走错了 2 次方向，浪费了 15 分钟」
  └─ 指挥官：「我在 30 分钟时本应中止但没有，导致影响扩大」

00:45 - 01:15  改进清单（Action Items）
  ├─ 监控：增加订单成功率 SLO dashboard
  ├─ 流程：oncall 收到告警后 5 分钟无人工响应 → 自动 page backup
  ├─ 文档：应急 Runbook 缺失 Redis failover 步骤
  ├─ 架构：payment-service 缺少 bulkhead 隔离
  └─ 工具：chaos-dashboard 增加「指挥官视图」

01:15 - 01:30  责任分配
  ├─ 每条 Action Item 指定：负责人 + 截止日期 + 验证标准
  └─ 写入 Jira / Linear
```'''),

        ('Action Items 跟踪', r'''**Jira Epic 模板**：

```
Epic: Game Day 改进 Q3-2024
├── [HIGH] STORY-101: 增加订单成功率 SLO dashboard
│   ├─ 负责人：张三（SRE）
│   ├─ 截止：2024-10-15
│   └─ 验证：dashboard 显示成功率 + 告警配置
├── [MED] STORY-102: 应急 Runbook 补充 Region 切换步骤
│   ├─ 负责人：李四（SRE）
│   ├─ 截止：2024-10-30
│   └─ 验证：Runbook 通过 Game Day 演练
└── [LOW] STORY-103: chaos-dashboard 增加「指挥官视图」
    ├─ 负责人：王五（前端）
    ├─ 截止：2024-11-15
    └─ 验证：截图 + 演练使用反馈
```

**Sprint Review 跟踪**：

- 每 Sprint Review 汇报 Action Items 完成度
- 未完成项说明原因 + 调整截止日期
- 累积 3 个未完成 → 升级到管理层'''),

        ('游戏日报告模板', r'''```markdown
# Q3 Game Day 报告

## 元数据
- 日期：2024-09-15
- 主题：Region Failover 演练
- 参与者：12 人
- 指挥官：张三（SRE Lead）

## 目标
- 验证 us-east-1 故障时 us-west-2 接管能力

## 场景
1. Redis 主从切换（30min）
2. 跨 Region 网络分区（30min）

## 结果
- 场景 1：通过（P99 < 1.2s，错误率 < 0.5%）
- 场景 2：部分通过（circuit breaker 10s 内打开，但 fallback 返回过期数据）

## 时间线
- 13:00 注入故障
- 13:05 oncall 告警
- 13:10 开始诊断

## 改进清单
1. [HIGH] 增加 fallback 数据的 staleness 标记
2. [MED] oncall Runbook 补充 Region 切换步骤
3. [LOW] chaos-dashboard 增加「指挥官视图」

## 经验教训
- 跨团队沟通顺畅
- Redis 切换时间过长（45 秒）
- fallback 数据无 staleness 标识
```'''),

        ('与其他站点关系', r'''- **chaos/06-game-day/exercise-design**：演练设计
- **chaos/06-game-day/roles**：角色分工
- **devops/06-best-practices**：Postmortem 流程'''),
    ]),

    ('07-observability-for-chaos/measure-steady-state', '稳态假设度量', [
        ('稳态度量五要素', r'''**1. 业务指标（KBI）**：

- 电商：订单成功率 / 支付成功率
- 视频：缓冲率 / 卡顿率 / 首帧时间
- 金融：交易成功率 / 清算时效

**2. 系统指标（SLI）**：

- 可用性：成功率 = 成功请求 / 总请求
- 延迟：P50 / P95 / P99
- 吞吐：QPS / TPS
- 错误：错误率 / 5xx 比例

**3. 资源指标**：

- CPU / 内存 / 磁盘 / 网络
- K8s：Pod 重启 / OOM / 节点状态

**4. 滑动窗口**：

- 不是「瞬时值」，而是「窗口期聚合」
- 常见窗口：1 分钟 / 5 分钟 / 15 分钟

**5. 稳态区间**：

- 不是「单点值」，而是「区间 + 时间窗口」
- 示例：订单成功率稳态 = [99.5%, 99.9%]，持续 5 分钟'''),

        ('Prometheus 查询示例', r'''```promql
# 订单成功率（5 分钟窗口）
sum(rate(order_success_total[5m]))
/ sum(rate(order_total[5m]))

# P99 延迟
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{app="order-service"}[5m])) by (le))

# 错误率（5xx）
sum(rate(http_requests_total{status=~"5..",app="order-service"}[5m]))
/ sum(rate(http_requests_total{app="order-service"}[5m]))

# Pod 重启次数（异常信号）
increase(kube_pod_container_status_restarts_total[5m])
```'''),

        ('异常检测算法', r'''**1. 阈值法**：

```yaml
alert: SteadyStateViolation
expr: |
  abs(
    sum(rate(order_success_total[5m]))
    / sum(rate(order_total[5m]))
    - 0.997
  ) > 0.005
for: 5m
```

**2. 同比/环比**：

```promql
# 与上周同时段对比
sum(rate(order_success_total[5m]))
/ sum(rate(order_total[5m]))
> on() (0.997 - 0.005)
```

**3. 3-sigma**：

```python
def steady_state_check(observed, history):
    mean = np.mean(history)
    std = np.std(history)
    return abs(observed - mean) < 3 * std
```

**4. CUSUM**：

```python
def cusum_check(observed, baseline, threshold):
    cumulative = 0
    for value in observed:
        cumulative = max(0, cumulative + (baseline - value))
        if cumulative > threshold:
            return True
    return False
```'''),

        ('稳态对比 Dashboard', r'''**Grafana Dashboard 示例**：

```
┌─────────────────────────────┐
│  实验前稳态 (过去 7 天)        │
│  - 订单成功率: 99.72% ± 0.05% │
│  - P99 延迟: 800ms ± 50ms    │
│  - 错误率: 0.05% ± 0.01%     │
└─────────────────────────────┘

┌─────────────────────────────┐
│  实验中（实时）                │
│  - 订单成功率: 99.45% ↓       │
│  - P99 延迟: 1200ms ↑         │
│  - 错误率: 0.42% ↑            │
│  判定: 偏离稳态（但仍可接受）   │
└─────────────────────────────┘

┌─────────────────────────────┐
│  实验后（恢复期）              │
│  - 订单成功率: 99.71% (恢复)   │
│  - P99 延迟: 850ms (恢复)     │
│  - 错误率: 0.06% (恢复)       │
│  恢复时间: 35 秒              │
└─────────────────────────────┘
```'''),

        ('与其他站点关系', r'''- **chaos/01-foundations/steady-state**：稳态定义
- **observability/03-prometheus**：Prometheus 集成
- **system-design/08-availability**：SLO 体系'''),
    ]),

    ('07-observability-for-chaos/slo-feedback-loop', 'SLO 反馈环', [
        ('SLO 三要素', r'''**SLI（Service Level Indicator）**：可度量的指标

- 例：订单成功率、P99 延迟

**SLO（Service Level Objective）**：目标值

- 例：99.5% 成功率、P99 < 1.5s

**Error Budget**：可消耗的错误预算

- 例：每月 0.5% 错误预算'''),

        ('反馈环流程', r'''```
SLO 定义 → 稳态采集 → 混沌实验 → SLO 对比 → 持续验证
   │          │          │           │            │
   ↓          ↓          ↓           ↓            ↓
业务承诺    实时指标    注入故障     偏离判定     累计统计
                                                   │
                                                   ↓
                                            触发改进
```'''),

        ('Error Budget 与混沌实验', r'''**每月 Error Budget 计算**：

```python
monthly_budget = (1 - slo_objective) * monthly_request_count
```

例：SLO 99.5% × 月请求量 100M → Budget = 0.5M 错误请求

**混沌实验消耗**：

- 每次混沌实验消耗多少？**取决于实验影响**
- 例：Pod kill 实验影响 0.1% 错误率 / 1 分钟 → 消耗 ~0.0007% 预算
- 每周 1 次 × 4 周 = 0.003% 预算

**混沌日（Chaos Day）**：

- 季度 / 半年：消耗 0.1% 预算做大型实验
- 大促窗口：冻结实验（保护预算）'''),

        ('Sloth SLO 定义', r'''**Sloth 自动生成 Prometheus rules**：

```yaml
service: order-service
slos:
  - name: availability
    objective: 99.5
    description: "订单成功率 SLO"
    sli:
      events:
        error_query: sum(rate(http_requests_total{status=~"5..",app="order-service"}[5m]))
        total_query: sum(rate(http_requests_total{app="order-service"}[5m]))
    alerting:
      page_alert:
        burnrate: 14.4
        for: 2m
      ticket_alert:
        burnrate: 1
        for: 1h
```

**多窗口 Burn Rate 报警**：

- 5 分钟 × 14.4 倍率：短期爆发（page alert）
- 30 分钟 × 6 倍率：中期泄漏（page alert）
- 1 小时 × 3 倍率：缓慢泄漏（ticket alert）
- 6 小时 × 1 倍率：长期泄漏（ticket alert）'''),

        ('与其他站点关系', r'''- **observability/03-prometheus**：Prometheus 集成
- **system-design/08-availability**：SLO 设计
- **chaos/01-foundations/steady-state**：稳态定义'''),
    ]),

    ('07-observability-for-chaos/case-study', '实战案例', [
        ('Netflix Chaos + Vizceral', r'''**Vizceral**：Netflix 开源实时流量拓扑图

- 显示服务间流量（线宽代表 QPS）
- Chaos Monkey 注入故障 → Vizceral 实时显示流量转移
- SRE 一眼看出「哪些服务受影响」

**关键洞察**：

- 故障注入是「视觉化」的
- 团队可以「看到」故障传播
- 沟通效率提升（不用看 dashboard）'''),

        ('Uber Chaos Mesh + M3 + Grafana', r'''**M3**：Uber 自研时序数据库（基于 Cassandra）

- 高吞吐（每秒百万级指标）
- 长时间存储（保留 1 年+）
- 多集群联邦

**集成流程**：

```
Chaos Mesh → 注入故障 → M3 记录指标 → Grafana 显示
```

**自研 Chaos Dashboard**：

- 实验成功率（过去 30 天）
- SLO 影响（实验期间偏离）
- 故障类型分布（柱状图）
- Top 失败实验（列表）'''),

        ('阿里 AHAS + ARMS', r'''**AHAS**：阿里云流量防护 + 故障注入

- Sentinel（限流 / 降级 / 熔断）
- 故障注入（CPU / 网络 / 进程）
- 一键启用（无需 K8s）

**ARMS（应用实时监控服务）**：

- APM（应用性能监控）
- 业务监控（订单 / 支付 / 用户）
- 告警 + dashboard

**集成**：混沌实验 → ARMS 自动采集 → 实时展示业务影响'''),

        ('字节跳动 Chaos Mesh + 自研 metric', r'''**自研 metric 平台**：

- 基于 Prometheus 扩展（千万级 metric）
- 「实验 vs 基线」对比 dashboard
- 自动判定「稳态偏离度」

**关键工具**：

- Chaos Mesh 注入故障
- 自研 metric 平台记录
- 自研 dashboard 可视化
- PagerDuty 告警联动'''),

        ('Shopify Black Friday 演练', r'''**2023 Black Friday 演练**：

- 演练前 6 个月：500+ 实验 + 100+ SLO
- 「Chaos Dashboard」显示实验成功率
- 大促日：实时对比「稳态 vs 实测」

**关键工具集成**：

```
Chaos Mesh ──┐
             ├──→ Prometheus ──→ Grafana (稳态 dashboard)
             ├──→ OpenTelemetry ──→ Jaeger (trace 链路)
             └──→ AlertManager ──→ PagerDuty / Slack
```

**实战成果**：

- Black Friday 期间零 P0 故障
- 演练发现的 50+ 问题全部修复
- oncall 应急能力提升 200%'''),

        ('与其他站点关系', r'''- **observability**：监控集成
- **chaos/02-chaos-mesh**：Chaos Mesh 案例
- **chaos/06-game-day**：实战游戏日'''),
    ]),
]


def main():
    for path, title, sections in STUBS:
        parts = [f'---\ntitle: {title}\n---\n', f'# {title}\n']
        for h2, content in sections:
            parts.append(f'## {h2}\n\n{content}\n')
        full_path = ROOT / f'{path}.md'
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text('\n'.join(parts))
        print(f'wrote {path}.md')


if __name__ == '__main__':
    main()