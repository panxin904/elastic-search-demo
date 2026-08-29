---
title: Chaos Mesh 架构
date: 2026-08-15  # date-auto-injected
---

# Chaos Mesh 架构

## 三大核心组件

Chaos Mesh 由三个核心组件构成：

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
- 实验模板复用

## 故障控制器（11 种）

| CRD | 故障类型 | 关键参数 |
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
- CRD 删除 → chaos-daemon 清理故障

## Workflow 工作流

Workflow CRD 支持多步骤实验编排（DAG）：

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
- 数据库主从切换验证

## 与其他站点关系

- **observability/03-prometheus**：Chaos Mesh 指标导出
- **devops/05-cicd-observability**：CI/CD 集成
- **chaos/03-litmus**：Litmus 对比
- **chaos/04-platform-compare**：选型决策


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

<!-- svg-injected:do-not-edit -->

## 图示：Chaos Mesh 控制面 + 注入面

![Chaos Mesh 控制面 + 注入面](/chaos-mesh-arch.svg)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 混沌
- [observability](https://java-px.bot.cd/observability/):故障注入监控
- [system-design](https://java-px.bot.cd/system-design/):系统韧性
