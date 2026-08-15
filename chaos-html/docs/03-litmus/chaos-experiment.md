---
title: ChaosExperiment CRD
---

# ChaosExperiment CRD

## CRD 体系三层

Litmus 的 CRD 分三层：

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
```

## 自定义实验（Litmus SDK）

通过 `litmus-go` SDK 编写自定义实验：

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
- 其他团队通过 `kubectl apply` 复用

## 与其他站点关系

- **observability/03-prometheus**：Probe 集成
- **chaos/02-chaos-mesh**：CRD 对比
- **design-pattern/05-architectural-patterns**：ChaosExperiment 验证
