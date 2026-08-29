---
title: Sidecar 模式
date: 2026-08-15  # date-auto-injected
---
# Sidecar 模式

## 1. 核心思想

**把不属于业务的"横切关注点"抽到独立的伴生容器**，与主容器共享网络/存储。

```
Pod
├── app container    ← 业务逻辑
└── sidecar       ← 基础设施（日志 / 代理 / 配置同步）
```

## 2. Sidecar 能做什么

| 用途 | Sidecar 例子 |
|------|------------|
| **日志收集** | Filebeat / Fluentd / Vector |
| **配置同步** | Confd / Reloader / ConfigMapWatcher |
| **代理** | Envoy / Sidecar proxy |
| **缓存** | 本地缓存（Redis client side） |
| **熔断** | Sentinel client |
| **安全** | Vault agent（短 TTL 凭据） |
| **健康检查** | Sidecar 探活 |
| **TLS 终止** | Cert-manager sidecar |

## 3. K8s Sidecar 模式

```yaml
apiVersion: apps/v1
kind: Pod
metadata:
  name: myapp
spec:
  containers:
  # 主容器
  - name: app
    image: myapp:1.0
    ports: [{containerPort: 8080}]
  # Sidecar：日志收集
  - name: log-shipper
    image: fluentd:1.16
    volumeMounts:
    - name: log-vol
      mountPath: /var/log/app
  volumes:
  - name: log-vol
    emptyDir: {}
```

**共享网络**：所有容器共享 Pod IP（localhost 互通）。
**共享存储**：可挂同一 Volume。

## 4. 实战：Service Mesh Sidecar

```
Pod
├── my-app        ← 业务容器
├── istio-proxy   ← 自动注入的 Sidecar（Envoy）
    - mTLS
    - 流量管理
    - 熔断
    - 可观测
```

**零应用改动**：通过 annotation 自动注入。

## 5. 实战：日志收集 Sidecar

```yaml
containers:
- name: app
  volumeMounts:
  - { name: logs, mountPath: /var/log/app }
- name: log-shipper
  image: fluent/fluentd:1.16
  volumeMounts:
  - { name: logs, mountPath: /var/log/app }
volumes:
- name: logs
  emptyDir: {}
```

**优势**：app 不需要知道日志在哪，由 sidecar 推到 ES/Loki。

## 6. 实战：配置热更新 Sidecar

```yaml
# Reloader 监控 ConfigMap 变化，自动重建 Pod
- name: reloader
  image: stakater/reloader:v1.4.0
  args: ["--configmap-glob", "myapp-*"]
```

或用 Reloader Operator 给 Pod 打 annotation，自动 reload。

## 7. 实战：Vault Agent Sidecar

```yaml
# Vault Agent Sidecar 注入短期凭据
- name: vault-agent
  image: vault:1.15
  args: ["agent", "-config=/etc/vault/config.hcl"]
  env:
  - name: VAULT_ADDR
    value: https://vault.example.com
  volumeMounts:
  - name: vault-token
    mountPath: /var/run/secrets/vault
```

App 容器从 /var/run/secrets/vault 读凭据（自动定期轮转）。

## 8. Sidecar 模式优缺点

✅ **优**：
- 单一职责（业务 vs 基础设施）
- 跨语言（任何容器能跑）
- 复用（sidecar 写一次，注入所有 Pod）

❌ **缺**：
- 资源消耗（+50MB / pod）
- 启动顺序（要等 sidecar 启动）
- 调试复杂（看两个进程）

## 9. 实战：Service Mesh 的 Sidecar

详见 [Service Mesh](/12-microservice-patterns/service-mesh) - Istio/Linkerd 自动注入 Envoy sidecar。

## 10. Sidecar 模式 vs Init Container

| | Sidecar | Init Container |
|--|---------|-----------------|
| 运行时机 | 全生命周期 | 启动前一次性 |
| 用途 | 长期后台 | 初始化（等 DB / 拉配置） |
| 共享网络 | ✅ 同一 Pod | 同一 Pod |
| 典型例子 | 日志 / 代理 | 等待 / 拉镜像 |

## 11. 反模式

- ❌ 业务代码依赖 sidecar 接口 → 强耦合
- ❌ sidecar 做太多事 → 单点
- ❌ 不用 emptyDir → 共享 Volume 撑爆
- ❌ 忘了设资源限制 → sidecar 吃满 CPU

## 12. 实战选型

| 场景 | Sidecar |
|------|---------|
| 日志 / 指标采集 | ✅ Fluentd / Vector sidecar |
| 配置热更新 | ✅ Reloader sidecar |
| 短 TTL 凭据 | ✅ Vault agent sidecar |
| Service Mesh | ✅ Envoy sidecar（自动注入） |
| 简单文件解析 | ❌ Init Container |
| 启动前等待依赖 | ❌ Init Container |

## 🔗 下一步
- [Service Mesh](/12-microservice-patterns/service-mesh)
- [Saga / Bulkhead](/12-microservice-patterns/saga)
