---
title: Pyroscope 持续剖析实战
date: 2026-08-15  # date-auto-injected
description: Grafana Labs 持续剖析平台
---

# Pyroscope 持续剖析实战

> **TL;DR**：Pyroscope = **Grafana Labs 开源的持续剖析平台**。**支持 Go/Java/Python/Rust/Node.js/PHP**。**部署模式：embedded agent / sidecar / pull（scrape）**。**2023 年与 Grafana 深度集成，火焰图直接在 Grafana 看**。**新项目首选 Pyroscope**。

## 一句话定义

```
Pyroscope = 持续剖析平台（CSP）
         = 2019 Pyroscope Inc. 开源，2023 被 Grafana Labs 收购
         = 支持 7+ 语言：Go / Java / Python / Rust / Node.js / PHP / .NET
         = 数据模型：{service} × {tags} × {timeline} × {stack traces}
         = 集成 Grafana：火焰图作为可视化层
```

## 核心概念

```
Profile = 一段时间内的栈采样集合
       = { start, end, samples, stacktraces }

Label（标签）= 区分不同维度的剖析数据
            = 服务名 / 环境 / 版本 / 实例 / 业务标签
            = 例：{service: order, env: prod, version: 2.3.0, region: cn}

Profile Type（剖析类型）= 剖析哪个维度
  - CPU（CPU 时间）
  - AllocSpace（内存分配字节数）
  - AllocObjects（内存分配对象数）
  - InuseSpace（当前占用字节）
  - InuseObjects（当前占用对象数）
  - Goroutines（Go 协程数）
  - LockCount（锁竞争次数）
  - LockTime（锁等待时间）
```

## 架构与部署

```
┌─────────────────────────────────────────────────────────┐
│  App 进程                                                │
│  ┌──────────────────────────────────────┐               │
│  │ Pyroscope Agent / SDK                │               │
│  │  - 周期性采样栈帧                     │               │
│  │  - push (gRPC) 或 pull (HTTP) 发送   │               │
│  └──────────────────────────────────────┘               │
└─────────┬───────────────────────────────────────────────┘
          │
          │ push gRPC :4040   /   pull :4040/api/scrape
          ▼
┌─────────────────────────────────────────────────────────┐
│  Pyroscope Server                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Ingester │→ │ Storage  │→ │ Querier  │               │
│  └──────────┘  │ (S3/GCS/ │  └──────────┘               │
│                │  MinIO)  │                              │
│                └──────────┘                              │
└─────────┬───────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│  Grafana（数据源：Pyroscope）                            │
│  - Explore → Pyroscope 数据源 → 选择 service + 时间范围  │
│  - Dashboard 集成火焰图                                  │
│  - 报警：基于 profile 的阈值                             │
└─────────────────────────────────────────────────────────┘
```

## 多语言接入

### Go

```go
import "github.com/grafana/pyroscope-go"

func main() {
    pyroscope.Start(pyroscope.Config{
        ApplicationName: "order-service",
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

    // 业务代码
}
```

### Java

```bash
# 启动 jar 时附加 pyroscope java agent
java -javaagent:./pyroscope-javaagent.jar \
     -Dpyroscope.application.name=order-service \
     -Dpyroscope.server.address=http://pyroscope:4040 \
     -Dpyroscope.tags.env=prod \
     -Dpyroscope.tags.version=2.3.0 \
     -Dpyroscope.config.file=/etc/pyroscope/config.json \
     -jar order-service.jar
```

```json
// config.json（可选）
{
  "applicationName": "order-service",
  "serverAddress": "http://pyroscope:4040",
  "tags": {
    "env": "prod",
    "version": "2.3.0"
  },
  "profileInterval": 10
}
```

### Python

```python
import pyroscope

pyroscope.configure(
    application_name="python-service",
    server_address="http://pyroscope:4040",
    tags={"env": "prod", "version": "2.3.0"},
)

# 业务代码
```

### Node.js

```javascript
const Pyroscope = require('@pyroscope/nodejs');

Pyroscope.init({
    serverAddress: 'http://pyroscope:4040',
    appName: 'node-service',
    tags: { env: 'prod', version: '2.3.0' },
});

Pyroscope.start();

// 业务代码
```

## Kubernetes 部署（embedded sidecar）

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  template:
    spec:
      containers:
        - name: app
          image: order-service:2.3.0
          env:
            - name: PYROSCOPE_SERVER_ADDRESS
              value: "http://pyroscope.pyroscope.svc:4040"
            - name: PYROSCOPE_APPLICATION_NAME
              value: "order-service"

        - name: pyroscope-sidecar
          image: grafana/pyroscope:latest
          args: ["exec", "/usr/local/bin/app"]
          # sidecar 模式：sidecar 启动主进程并自动注入 agent
```

## 自部署 Pyroscope Server

```yaml
# docker-compose 简易版
version: '3'
services:
  pyroscope:
    image: grafana/pyroscope:latest
    command:
      - "--storage.tsdb.path=/data"
      - "--storage.tsdb.retention-period=7d"
      - "--auth.enabled=false"
    ports:
      - "4040:4040"
    volumes:
      - ./pyroscope-data:/data
```

```yaml
# 生产级：MinIO 作为对象存储
services:
  pyroscope:
    image: grafana/pyroscope:latest
    command:
      - "--storage.backend=s3"
      - "--storage.s3.bucket-name=pyroscope"
      - "--storage.s3.endpoint=minio.storage:9000"
      - "--storage.s3.access-key-id=admin"
      - "--storage.s3.secret-access-key=password"
```

## Grafana 集成

```yaml
# Grafana 数据源配置（UI 界面也可）
apiVersion: 1
datasources:
  - name: Pyroscope
    type: grafana-pyroscope-datasource
    url: http://pyroscope:4040
    jsonData:
      keepCookies: []
```

```
Grafana 使用流程：
  1. Explore → 选择 Pyroscope 数据源
  2. service = order-service
  3. profile type = cpu (默认)
  4. 时间范围选择（如最近 1 小时）
  5. 点击 Run → 显示火焰图
  6. 下钻 / 搜索函数 / 对比时间窗口
```

## 实战案例：定位 CPU spike

```
场景：凌晨 3 点 CPU 100%，但 QPS 不高

排查步骤：
  1. Grafana → Explore → Pyroscope
  2. service = order-service, time = 凌晨 3 点 ± 1h
  3. 看到火焰图：100% 占用在 "JSON.Marshal" 上
  4. 下钻：调用链是 handleOrderRequest → buildResponse → JSON.Marshal
  5. 看代码：buildResponse 在做全量字段序列化（含历史订单 1000+ 条）
  6. 优化：分页返回 + 字段精简
  7. 修复后火焰图：CPU 80% 降到 30%

火焰图优势：
  - 1 步定位（不需要 log + trace + metric 三件套）
  - 直接看到函数耗时占比
  - 历史对比（同一服务不同时间）
```

## 实战案例：内存泄漏

```
场景：服务运行 24h 后 OOM 被 K8s 重启

排查步骤：
  1. Grafana → Pyroscope
  2. profile type = inuse_space（当前占用字节）
  3. 时间窗口 = 过去 24h，对比 4 个时间点
  4. 发现：某个缓存对象持续增长
     - t0: 100MB
     - t6h: 500MB
     - t12h: 1.2GB
     - t18h: 2.4GB
  5. 看代码：本地缓存无 TTL + 无 LRU 淘汰
  6. 修复：加 LRU + max size 限制
```

## 一句话总结

> **Pyroscope = 持续剖析 + Grafana 集成**。**支持 7+ 语言**。**部署：embedded SDK / sidecar / K8s**。**火焰图 + 标签 = 故障定位 1 步到位**。**生产标配：Pyroscope + Grafana + Prometheus + Tempo/Loki**。

---

## 关联章节

- [持续剖析](./continuous-profiling.md) — Continuous Profiling 概念
- [Go pprof](./pprof.md) — Go 内置 profiler
- [Java async-profiler](./async-profiler.md) — Java 故障定位
- [微服务全链路追踪](../11-scenarios/microservice-trace.md) — Profiling + Tracing 联动

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
