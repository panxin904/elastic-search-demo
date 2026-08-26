---
title: K8s 指标采集
description: kube-state-metrics / cAdvisor / Prometheus Operator
---

# K8s 指标采集

> **TL;DR**：**K8s 指标采集 = kube-state-metrics（K8s 对象）+ cAdvisor（容器）+ node-exporter（主机）+ Prometheus Operator（部署）**。**生产标配：kube-prometheus-stack Helm Chart（一键全套）**。**指标涵盖：Pod / Deployment / Node / PVC / Service / Ingress**。

## 一句话定义

```
K8s 指标采集 = 4 类 exporter 配合
             = node-exporter（主机）
             = cAdvisor（容器，kubelet 内置）
             = kube-state-metrics（K8s 对象状态）
             = Prometheus Operator（自动化）

完整可观测：
  Prometheus + Alertmanager + Grafana + node-exporter + kube-state-metrics
```

## kube-prometheus-stack（一键部署）

```bash
# Helm 安装
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack   --namespace monitoring   --create-namespace
```

```
自动部署：
  - prometheus-operator
  - prometheus（StatefulSet）
  - alertmanager（StatefulSet）
  - grafana（Deployment）
  - node-exporter（DaemonSet）
  - kube-state-metrics（Deployment）
  - 预置 ServiceMonitor / PrometheusRule / Grafana Dashboard
```

## kube-state-metrics 关键指标

```promql
# 1. Pod 状态
kube_pod_status_phase{phase="Running"}        # 运行中的 pod
kube_pod_container_status_ready                # 容器就绪
kube_pod_container_status_restart_total       # 重启次数

# 2. Deployment 状态
kube_deployment_status_replicas_available      # 可用副本数
kube_deployment_spec_replicas                  # 期望副本数

# 3. Node 状态
kube_node_status_condition{condition="Ready",status="true"}

# 4. PVC / PV
kube_persistentvolumeclaim_status_phase{phase="Bound"}

# 5. 资源请求 / 限制（用于容量规划）
kube_pod_container_resource_requests{resource="cpu"}
kube_pod_container_resource_limits{resource="memory"}
```

## cAdvisor / kubelet 指标

```promql
# 1. 容器 CPU 使用
rate(container_cpu_usage_seconds_total{name!="", name!="POD"}[5m])

# 2. 容器内存使用
container_memory_usage_bytes{name!="", name!="POD"}

# 3. 容器网络 IO
rate(container_network_receive_bytes_total[5m])
rate(container_network_transmit_bytes_total[5m])

# 4. 容器文件系统
container_fs_usage_bytes

# 5. OOM 事件（重启原因）
kube_pod_container_status_last_terminated_reason{reason="OOMKilled"}
```

## 实战告警

```yaml
groups:
  - name: k8s-alerts
    rules:
      # Pod 频繁重启
      - alert: PodCrashLooping
        expr: |
          rate(kube_pod_container_status_restart_total[10m]) > 0
        for: 5m
        labels: {severity: warning}

      # 容器 OOMKilled
      - alert: ContainerOOMKilled
        expr: |
          kube_pod_container_status_last_terminated_reason{reason="OOMKilled"} == 1
        for: 0m
        labels: {severity: critical}

      # Pod Pending 超过 5 分钟
      - alert: PodPendingLong
        expr: kube_pod_status_phase{phase="Pending"} == 1
        for: 5m
        labels: {severity: warning}

      # 节点 NotReady
      - alert: NodeNotReady
        expr: |
          kube_node_status_condition{condition="Ready",status="true"} == 0
        for: 2m
        labels: {severity: critical}

      # PVC Pending（存储问题）
      - alert: PVCPending
        expr: |
          kube_persistentvolumeclaim_status_phase{phase="Pending"} == 1
        for: 5m
        labels: {severity: warning}

      # 节点磁盘即将耗尽
      - alert: NodeDiskPressure
        expr: |
          (1 - node_filesystem_avail_bytes{mountpoint="/"}
          / node_filesystem_size_bytes{mountpoint="/"}) > 0.85
        for: 10m
        labels: {severity: warning}

      # Deployment 副本不足
      - alert: DeploymentReplicasMismatch
        expr: |
          kube_deployment_status_replicas_available
          != kube_deployment_spec_replicas
        for: 5m
        labels: {severity: critical}
```

## Prometheus Operator 优势

```
1. ServiceMonitor：自动发现 + 抓取配置（CRD）
2. PrometheusRule：告警规则 CRD
3. AlertmanagerConfig：Alertmanager 路由 CRD
4. Grafana Dashboard 自动导入

# ServiceMonitor 示例（自动抓取 ingress-nginx）
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ingress-nginx
  labels:
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: ingress-nginx
  endpoints:
    - port: metrics
      interval: 30s
```

## 一句话总结

> **K8s 监控 = kube-prometheus-stack（Helm 一键）+ 4 类指标**。**关键告警：Pod 重启 / OOMKilled / Node NotReady / PVC Pending**。**生产必备**。

---

## 关联章节

- [K8s 监控](../11-scenarios/k8s-monitor.md)
- [Exporter](../03-prometheus/exporter.md)
- [Prometheus 告警](../03-prometheus/alert.md)
- [PromQL](../03-prometheus/promql.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
