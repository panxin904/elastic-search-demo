---
title: 工作流编排
---

# 工作流编排

## Workflow 简介

**Workflow 是 Chaos Mesh 的多步骤实验编排（DAG）**。

**典型场景**：

- 大促前全链路验证（订单 → 支付 → 库存 → 物流）
- 跨服务故障传播测试
- 复杂业务场景模拟（用户下单 → 失败 → 重试 → 成功）

**优势**：

- 多步骤串联（真实场景模拟）
- 状态可视化（chaos-dashboard 显示每个步骤）
- 失败自动中止 + 通知
- 与 Schedule 集成（cron 触发）

## Workflow YAML

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

## 模板类型

**Workflow 模板类型**：

- **Serial**：顺序执行（一个接一个）
- **Parallel**：并行执行（同时进行）
- **Suspend**：等待人工确认
- **PodChaos / NetworkChaos / StressChaos**：实际故障类型

**典型应用**：

- 大促前全链路验证
- 跨 Region 故障转移演练
- 数据库主从切换验证
- 微服务链路故障传播测试

## 与其他站点关系

- **chaos/02-chaos-mesh/architecture**：Chaos Mesh 架构
- **observability**：监控集成
- **devops/05-cicd-observability**：CI/CD 集成


## ## 实战案例

**美团 Workflow 编排**：美团把多个 Chaos 实验编排成 Workflow，每周自动在预发布环境跑 30+ 复合场景，验证整体韧性。

**小米 Chaos CI**：PR 提交后自动触发 Chaos Mesh Workflow，先在预发布环境跑 5 分钟基础故障，确认通过后再合入主线。

**网易 Workflow 模板复用**：团队共享 Workflow 模板库（kube-apiserver 故障、etcd 故障、Node 故障），新人 5 分钟就能搭出复合实验。


## ## 故障排查清单

1. Workflow 卡住 → 检查 status.condition，看是哪个 task 失败
2. 并发任务冲突 → 同一资源的多个 chaos 互相覆盖
3. 节点随机性过强 → 用 nodeSelector 收敛到测试节点
4. 清理不彻底 → serial chaos 结束后手动 verify
5. 时间窗口失效 → confirm 字段检查 resourceVersion
