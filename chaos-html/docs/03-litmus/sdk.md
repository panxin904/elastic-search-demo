---
title: Litmus SDK
---

# Litmus SDK

## SDK 核心 API

Litmus 提供 Go SDK 用于编写自定义实验。

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
```

## 实验参数定义

**实验参数定义（环境变量）**：

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
```

## 编写自定义实验步骤

1. 在 `litmus-go/contrib/developer-experiments/` 创建新目录
2. 实现 main.go（使用 SDK）
3. 添加 Dockerfile
4. 创建 ChaosExperiment CRD（指向你的镜像）
5. 注册到 ChaosHub（GitHub PR）

## SDK 工具函数

**SDK 工具函数**：

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
```

## 与社区贡献

**与社区贡献**：

- Litmus 社区欢迎贡献新实验
- 标准实验仓库：https://github.com/litmuschaos/litmus-go
- 提交 PR → ChaosHub 自动索引

**实战建议**：

- 复用 SDK 工具函数（避免重复造轮子）
- 错误处理要完整（result.RecordFailure 必须调用）
- 镜像要小（multi-stage build）
- 测试要全（unit test + integration test）


## ## 实战案例

**Go SDK 实战**：字节跳动用 Go SDK 集成 Litmus 到自研平台，10 行代码注入 Pod kill，同时上报结果到内部 dashboard。

**Java SDK 集成**：京东把 Java SDK 嵌入 Spring Boot Starter，业务代码用 `@ChaosTest` 注解即可启用，0 业务代码改动。

**Python SDK 离线使用**：快手用 Python SDK 跑离线混沌实验（数据库故障模拟、消息队列延迟），无需 K8s 集群。


## ## 故障排查清单

1. SDK 注入无效果 → 检查 chaosServiceAccount / chaosRole
2. 探针失败 → 检查 probe httpGet / exec 命令
3. 结果上报失败 → 检查 litmusportal-rbac
4. SDK 版本过旧 → 升级到 2.x，与 control-plane 兼容
5. 跨语言实验 → 用 ChaosHub 统一分发实验
