---
title: 自动埋点
description: Java agent / eBPF / 零代码埋点
---

# 自动埋点

> **TL;DR**：**自动埋点 = 不改业务代码，靠 SDK agent / eBPF 自动捕获 span/metric**。**Java：opentelemetry-javaagent.jar 一行命令搞定**。**eBPF：Parca / Pixie / Cilium Tetragon 不需要 SDK 也能自动捕获系统调用**。**新项目首选自动埋点 + 关键路径手动埋点**。

## 一句话定义

```
自动埋点 = 无侵入捕获调用栈
        = 三种实现：字节码注入（JVM）/ 运行时 hook（Node.js）/ eBPF（内核）
        = 优点：覆盖广 / 零代码 / 部署即生效
        = 缺点：捕获全但业务语义弱（需手动埋点补充）
```

## Java 自动埋点

```bash
# 1. 下载 opentelemetry-javaagent.jar
curl -L -o opentelemetry-javaagent.jar   https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar

# 2. 启动 jar 时附加
java -javaagent:./opentelemetry-javaagent.jar      -Dotel.service.name=order-service      -Dotel.exporter.otlp.endpoint=http://otel-collector:4317      -jar order-service.jar

# 自动埋点覆盖（2024）：
# - HTTP server: Tomcat, Jetty, Netty, Spring Web
# - HTTP client: Apache HttpClient, OkHttp, RestTemplate
# - Database: JDBC, HikariCP, R2DBC
# - Messaging: Kafka, RabbitMQ, JMS
# - RPC: gRPC, Dubbo
# - Cache: Redis (Jedis, Lettuce)
# - 框架: Spring Boot, Spring Data
```

## Node.js 自动埋点

```bash
# 1. 安装
npm install @opentelemetry/auto-instrumentations-node             @opentelemetry/sdk-node             @opentelemetry/exporter-trace-otlp-http

# 2. 启动命令前加载
node --require ./tracing.js server.js
```

```javascript
// tracing.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: 'http://otel-collector:4318/v1/traces' }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

// 自动埋点：http, express, koa, mongodb, mysql, redis, kafka
```

## Python 自动埋点

```bash
pip install opentelemetry-distro[otlp]
opentelemetry-bootstrap -a install   # 自动安装所有 instrumentation
opentelemetry-instrument python app.py
```

## eBPF 自动埋点（K8s）

```
代表项目：
  - Pixie（New Relic 开源）：eBPF 自动捕获应用 trace + metrics
  - Parca：CPU/内存剖析（Profiling）
  - Cilium Tetragon：安全 + 网络可观测
  - bpftrace：自定义 eBPF 脚本

Pixie 示例：
  - 自动捕获 HTTP 请求（无需 SDK）
  - 自动生成火焰图
  - 自动捕获 SQL 查询 + DB 耗时
  - 限制：语言运行时细节缺失（如 Java 方法名）
```

## 选择决策

| 场景 | 推荐方案 |
|---|---|
| 新 JVM 项目 | Java agent 自动 + 关键路径手动 |
| 新 Node.js 项目 | auto-instrumentations + 手动埋点 |
| Go 项目 | 必须手动埋点（无运行时 hook） |
| K8s 容器化项目 | 配 Java agent + Pixie（eBPF）做兜底 |
| 旧系统接入 | eBPF / sidecar 方式无侵入接入 |
| 性能敏感 | 不开 auto，CPU 影响 2-5% |

## 一句话总结

> **自动埋点 = 零代码接入**。**Java 用 javaagent，Node.js 用 auto-instrumentations，K8s 用 eBPF**。**Go 必须手动**。**auto + 关键路径手动 = 最佳组合**。

---

## 关联章节

- [SDK](../02-opentelemetry/sdk.md) — 自动 + 手动的 SDK
- [OTLP](../02-opentelemetry/otlp.md) — 自动埋点的数据输出
- [Collector](../02-opentelemetry/collector.md) — 数据汇聚点

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
