---
title: PodChaos 实验
---

# PodChaos 实验

## PodChaos action 类型

PodChaos 支持四种故障动作：

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
```

## 实战案例：订单服务 Pod kill

**场景**：验证 order-service 在 1 个 Pod 被 kill 时的韧性。

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
- Pod 重启失败 → 镜像拉取问题 / 资源不足

## PodChaos 高级用法

**1. 灰度 Pod kill（fixed-percent）**：

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
```

## 与其他站点关系

- **observability/03-prometheus**：稳态指标
- **chaos/03-litmus**：Litmus pod-delete 对应
- **system-design/08-availability**：可用性验证
- **devops/05-cicd-observability**：CI/CD 集成


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 混沌
- [observability](https://java-px.bot.cd/observability/):故障注入监控
- [system-design](https://java-px.bot.cd/system-design/):系统韧性
