---
title: 持续剖析
description: Continuous Profiling — 生产环境不间断 profiling
---

# 持续剖析

> **TL;DR**：**持续剖析（Continuous Profiling）= 在生产环境 7×24 收集 CPU / 内存 / 锁 / IO 剖析数据**，**而不是故障后临时 attach profiler**。**代表项目：Pyroscope（Grafana Labs）+ Google gVisor + Datadog Continuous Profiler + Uber profig + Microsoft OneProfiler**。**parca + eBPF 是新范式（无需代码侵入）**。

## 一句话定义

```
持续剖析 = 生产环境永远运行 profiler
         = 100% 流量采样（不是 1%）
         = 火焰图（Flame Graph）形式可视化
         = 故障前就能发现性能热点
         = 跟传统 profiler 的区别：传统 = 故障后 attach，持续 = 永远在跑
```

## 与传统 Profiling 对比

```
┌─────────────┬────────────────────┬──────────────────┐
│ 维度        │ 传统 Profiling      │ 持续 Profiling   │
├─────────────┼────────────────────┼──────────────────┤
│ 触发时机    │ 故障后人工 attach   │ 7×24 自动收集    │
│ 采样率      │ 100%（短时间）     │ 1-10%（长时间）  │
│ 覆盖率      │ 单进程 / 单请求    │ 全集群全流量     │
│ 存储        │ 临时文件            │ 长期时序存储     │
│ 火焰图      │ 1 个时间点         │ 时间序列对比     │
│ 工具        │ perf / async-profiler│ Pyroscope / Parca │
│ 成本        │ 性能影响 5-10%     │ 性能影响 0.5-2% │
│ 适用        │ 故障定位            │ 性能基线 / 趋势   │
└─────────────┴────────────────────┴──────────────────┘
```

## 代表项目

| 项目 | 出品 | 特点 | 适用 |
|---|---|---|---|
| **Pyroscope** | Grafana Labs | 多语言 / 集成 Grafana / pull+push / OSS | 主流选择 |
| **Parca** | Polar Signals | eBPF + 零代码侵入 | K8s / 容器化 |
| **Datadog Profiler** | Datadog | SaaS / 商用 | Datadog 用户 |
| **Google Cloud Profiler** | GCP | 集成 GCP | GCP 用户 |
| **prof-viz / profig** | Uber | Go / 大规模 | Go 项目 |
| **async-profiler** | async-profiler | Java / 单机 | Java 故障定位 |

## Pyroscope 架构

```
┌──────────┐  push (gRPC)  ┌──────────┐  ingest   ┌──────────┐
│ App SDK  │ ────────────▶ │ Pyroscope│ ────────▶ │ Storage  │
│ (agent)  │                │ Server   │           │ (TSDB +  │
│          │  scrape (HTTP) │          │           │  blocks) │
│ pyroscope│ ◀─────────────│          │           └──────────┘
│ SDK      │                │          │                │
└──────────┘                └──────────┘                │
       ↑                            │                   │
       │ pull (15s)                 │ query             ▼
       │                            │              ┌──────────┐
┌──────────┐                        └────────────▶ │ Grafana  │
│ Sidecar  │                                       │ Flame    │
│ pyroscope│ ◀─── scrape config                    │ Graph    │
└──────────┘                                       └──────────┘
```

## Pyroscope 实战（Go）

```go
// 1. 安装 pyroscope + go integration
// go get github.com/grafana/pyroscope-go

package main

import (
    "github.com/grafana/pyroscope-go"
)

func main() {
    // 2. 启动 pyroscope agent
    pyroscope.Start(pyroscope.Config{
        ApplicationName: "my-service",
        ServerAddress:   "http://pyroscope:4040",
        Tags: map[string]string{
            "env":     "prod",
            "version": "2.3.0",
        },
        ProfileTypes: []pyroscope.ProfileType{
            pyroscope.ProfileCPU,
            pyroscope.ProfileAllocObjects,
            pyroscope.ProfileAllocSpace,
            pyroscope.ProfileInuseObjects,
            pyroscope.ProfileInuseSpace,
            pyroscope.ProfileGoroutines,
        },
    })

    // 业务代码...
}
```

```yaml
# 3. Kubernetes 部署（sidecar 模式）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  template:
    spec:
      containers:
        - name: my-service
          image: my-service:2.3.0
          env:
            - name: PYROSCOPE_SERVER_ADDRESS
              value: "http://pyroscope:4040"
            - name: PYROSCOPE_APPLICATION_NAME
              value: "my-service"

        - name: pyroscope-sidecar
          image: grafana/pyroscope:latest
          args:
            - "exec"
            - "/usr/bin/my-service"
          # 自动注入 pyroscope agent
```

## Pyroscope 实战（Java）

```bash
# 1. async-profiler attach 模式
java -javaagent:./async-profiler.jar \
     -agentpath:./libasyncProfiler.so=start,event=cpu,flamegraph \
     -jar myapp.jar

# 2. Pyroscope Java agent（推荐）
# 下载 pyroscope java agent jar
java -javaagent:./pyroscope-javaagent.jar \
     -Dpyroscope.application.name=my-service \
     -Dpyroscope.server.address=http://pyroscope:4040 \
     -Dpyroscope.tags.env=prod \
     -Dpyroscope.tags.version=2.3.0 \
     -jar myapp.jar
```

```promql
# 3. Grafana 火焰图查询（Pyroscope 数据源）
# 直接在 Grafana 选 Pyroscope 数据源 → 选择 service → 时间范围 → 看火焰图
```

## Parca（eBPF 零侵入）

```yaml
# Parca 部署：完全无需代码改动
# 1. 部署 Parca Agent（DaemonSet）
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: parca-agent
spec:
  template:
    spec:
      containers:
        - name: parca-agent
          image: ghcr.io/parca-dev/parca-agent:latest
          args:
            - "--node=$(NODE_NAME)"
            - "--remote-store-address=parca-server:7070"
            - "--kubernetes"        # 自动发现 K8s pods
            - "--enable-cpu-profiling"
            - "--enable-allocation-profiling"
          securityContext:
            privileged: true   # 需要 BPF 权限
```

```yaml
# 2. Parca Server（中心化）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: parca-server
spec:
  template:
    spec:
      containers:
        - name: parca-server
          image: ghcr.io/parca-dev/parca:latest
          args:
            - "--config-path=/etc/parca/parca.yaml"
            - "--storage-path=/data"
```

```
优势：
  - 零代码改动（eBPF 内核态采样）
  - 自动覆盖所有进程（无需 SDK）
  - 自动识别语言（Go / Java / Rust / Python / C++）
  - K8s 友好（DaemonSet + 自动 label）

限制：
  - 需要 privileged 权限
  - 不支持特定业务栈帧归因（语言运行时细节）
  - 内核版本要求 ≥ 4.18
```

## 火焰图阅读

```
火焰图（Flame Graph）= Brendan Gregg 2011 发明
                  = 栈帧柱状图，y 轴是栈深度，x 轴是采样次数
                  = 顶部是最热函数（火焰）

阅读步骤：
  1. 从最宽的顶层函数开始（最热点）
  2. 沿 x 轴看每个函数耗时占比
  3. 下钻看调用链（y 轴方向）
  4. 找"平顶"（Plateau）= 该函数自身耗时（不是被调用方）

实战案例：
  ┌────────────────────────────────────────┐
  │ main (100%)                            │
  │   └─ handleRequest (85%)               │  ← 看这里，handler 自身占 85%
  │       └─ queryDatabase (12%)           │
  │           └─ pgx.Query (8%)            │
  │       └─ json.Marshal (3%)             │
  └────────────────────────────────────────┘

结论：handler 自身占 85%（如 JSON 序列化、复杂业务计算）
      数据库查询只占 12%（不是瓶颈）
      优化方向：减少 handler 自身计算（缓存 / 异步）
```

## 一句话总结

> **持续剖析 = 生产环境永远跑 profiler**。**代表：Pyroscope（多语言）/ Parca（eBPF 零侵入）**。**火焰图找最热点 = 平顶（plateau）= 函数自身耗时**。**新项目标配：Pyroscope + Grafana**。

---

## 关联章节

- [Pyroscope](./pyroscope.md) — Grafana Labs 持续剖析实战
- [Go pprof](./pprof.md) — Go 内置 profiler
- [Java async-profiler](./async-profiler.md) — Java 故障定位
- [微服务性能瓶颈](../11-scenarios/microservice-trace.md) — 持续剖析实战

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
