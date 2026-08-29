---
title: 分布式链路追踪
date: 2026-08-15  # date-auto-injected
---

# 分布式链路追踪

> 一个请求跨多个服务时，**如何追踪它从进入到返回的完整路径**。

## 1. 为什么需要链路追踪？

```
单体应用：
  - 一个请求只在一个进程内
  - 日志集中，排查简单

微服务架构：
  - 一个请求可能跨 5-10 个服务
  - 日志分散在多个机器
  - 一次慢响应，不知道卡在哪
  - 一次错误，不知道哪个服务抛的

例：用户下单
  Gateway → OrderService → InventoryService → PaymentService → MQ → NotificationService

用户反馈"下单失败"，问题在哪？
  - Gateway？网络？
  - OrderService？DB 慢？
  - InventoryService？库存锁？
  - PaymentService？支付失败？
  - MQ？消息丢失？
  → 必须有链路追踪才能定位
```

## 2. 链路追踪的核心概念

### 2.1 Trace / Span

```
Trace = 一次完整的请求链路
Span = Trace 中的一个工作单元（一个 RPC / DB 查询 / 缓存访问）

例：下单 trace
  Trace ID: abc123
    Span 1: Gateway (10ms)
      Span 2: OrderService.createOrder (50ms)
        Span 3: InventoryService.lockStock (15ms)
          Span 4: MySQL UPDATE inventory (8ms)
        Span 5: PaymentService.charge (30ms)
          Span 6: Redis SET cart (2ms)
        Span 7: MQ Produce (5ms)

关系：
  Span 1 是根（root span）
  Span 2/3/4/5/6/7 是 Span 1 的子（child）
  Span 4 是 Span 3 的子（grandchild）
```

### 2.2 Trace ID / Span ID / Parent Span ID

```
Trace ID：
  - 唯一标识一次完整请求
  - 全链路传递
  - 格式：128 bit（hex 字符串），如 abc123def456

Span ID：
  - 唯一标识一个 Span
  - 64 bit

Parent Span ID：
  - 父 Span 的 ID
  - 通过父子关系重建调用树
```

## 3. 数据模型

### 3.1 OpenTelemetry Span 数据

```
每个 Span 包含：
  - trace_id
  - span_id
  - parent_span_id
  - operation_name（如 HTTP GET /api/order）
  - start_time / end_time
  - attributes（如 http.method、http.status_code、db.statement）
  - events（如异常、里程碑）
  - status（OK / ERROR）
  - kind（CLIENT / SERVER / PRODUCER / CONSUMER / INTERNAL）
```

### 3.2 调用关系

```
Span Tree：

Trace abc123
├─ Span A (Gateway) [SERVER]
│  ├─ Span B (OrderService.createOrder) [SERVER]
│  │  ├─ Span C (InventoryService.lockStock) [CLIENT] ─► [SERVER]
│  │  │  └─ Span D (MySQL UPDATE) [CLIENT]
│  │  └─ Span E (PaymentService.charge) [CLIENT] ─► [SERVER]
│  │     └─ Span F (Redis SET) [CLIENT]
│  └─ Span G (MQ Produce) [CLIENT]

C 和 E 是 client span（发起调用）
B 是 server span（接收调用）
D / F 也是 client span（数据库调用）
```

## 4. Trace 传递（Context Propagation）

### 4.1 三大难题

```
1. 跨进程传递：
   - HTTP Header
   - gRPC Metadata
   - MQ Header / Properties

2. 跨线程传递：
   - ThreadLocal
   - InheritableThreadLocal
   - 显式传递（协程 / 异步）

3. 异步链路：
   - 线程池切换
   - 异步回调
   - MQ 异步消息

📌 最容易丢的就是异步链路
```

### 4.2 W3C Trace Context

```
标准 Header：
  traceparent: 00-{trace_id}-{span_id}-{flags}
  示例：00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

字段：
  - version (00)
  - trace-id (16 bytes)
  - parent-id (8 bytes)
  - flags (01 = sampled)

优势：
  - 行业标准（W3C）
  - 多语言 SDK 互通
  - 兼容 Zipkin B3
```

### 4.3 异步场景的处理

```
线程池：
  - 主线程 Submit 到线程池时，捕获当前 Context
  - 任务执行时，恢复 Context 到新线程
  - Java：InheritableThreadLocal + 包装 Runnable

异步回调：
  - 显式把 Context 当参数传递
  - 回调时设置到当前线程

MQ 消息：
  - Producer：把 traceparent 塞到消息 header
  - Consumer：消费时从 header 取出，设到当前线程
  → 关键是 trace 能"跨进程 + 跨时间"传递
```

## 5. 采样策略

```
全量采集数据量巨大：
  - 1 万 QPS × 每个 trace 10 spans × 每个 span 1 KB
  - = 100 MB/s
  → 存不下也传不完

采样（Sampling）：
  - 决定哪些 trace 要采集
  - 哪些丢弃
```

### 5.1 头部采样（Head-based）

```
请求开始时决定是否采样：
  - 概率采样：1% 概率采样
  - 比例采样：每秒最多 100 个
  - 自适应：根据错误率动态调

优点：决策一次
缺点：可能错过"罕见错误"
```

### 5.2 尾部采样（Tail-based）

```
请求结束时决定：
  - 全部 trace 都记录到本地
  - 后台聚合分析
  - 只保留"值得保留"的（如错误 / 慢）

优点：能捕获所有错误
缺点：存储开销大、决策延迟
```

### 5.3 实际选择

```
头部采样 + 强制保留：
  - 默认 1%-10% 概率采样
  - 错误请求 100% 采样
  - 慢请求 100% 采样

📌 业界主流是头部采样，简单可控
```

## 6. 主流实现

### 6.1 OpenTelemetry（OTel）

```
CNCF 项目（2021 年毕业）：
  - 统一了 OpenTracing + OpenCensus
  - 行业标准
  - 多语言 SDK（Java/Go/Python/Node/...）
  - 与 Jaeger / Zipkin / Prometheus / Vendor 各家后端互通
```

### 6.2 Jaeger（Uber 开源）

```
架构：
  - Client SDK
  - Agent（本地收集）
  - Collector（聚合）
  - Storage（ES / Cassandra）
  - UI（查询 / 可视化）

特点：
  - OpenTelemetry 原生支持
  - UI 体验好
  - 大规模生产验证
```

### 6.3 Zipkin（Twitter 开源）

```
老牌项目：
  - 最早的开源分布式追踪系统
  - OpenTelemetry 兼容
  - 后端：ES / MySQL / Cassandra
```

### 6.4 SkyWalking（国产）

```
Apache 项目：
  - 国产最流行的 APM
  - 链路追踪 + 监控 + 告警
  - 自动探针（无侵入）
  - UI 完善

特点：
  - 多语言支持
  - 自动埋点（Java Agent）
  - 国内使用广泛
```

### 6.5 商业方案

```
- DataDog APM
- New Relic
- Dynatrace
- AWS X-Ray
- Google Cloud Trace
- 阿里云 ARMS
- 腾讯云 CAT
```

## 7. 关键能力

### 7.1 Trace 查询

```
UI 提供：
  - Trace ID 搜索
  - 服务过滤
  - 时间范围
  - 错误 / 慢 trace 筛选

例：搜索"过去 1 小时，所有 500 错误的 trace"
  → 看到哪些服务的哪些接口报错
```

### 7.2 服务依赖图

```
自动生成：
  ┌────────┐ ──HTTP──► ┌────────┐
  │Gateway │           │Order   │
  └────────┘           └────────┘
       │                  │
       │                  ├─HTTP──► ┌────────────┐
       │                  │         │Inventory   │
       │                  │         └────────────┘
       │                  │
       │                  └─gRPC──► ┌────────────┐
       │                            │Payment     │
       │                            └────────────┘

基于 trace 数据自动绘制
```

### 7.3 Span 详情

```
点击某个 Span：
  - 耗时（精确到 ms）
  - 调用栈（同步代码 + 异步回调）
  - Attributes（http.method / db.statement / rpc.system）
  - Events（异常堆栈 / 自定义事件）
  - Logs（结构化日志关联）
```

### 7.4 Trace + Logs 关联

```
通过 trace_id 关联日志：
  - trace 里点 Span → 跳转到日志
  - 日志里搜 trace_id → 跳回 trace

实现：
  - 日志框架输出 trace_id / span_id（MDC）
  - trace UI 提供跳转链接
```

## 8. 实战陷阱

### 8.1 Trace 丢失

```
常见原因：
  - 异步调用忘记传递 Context
  - MQ 消息 header 没带 trace
  - 线程池没包装
  - SDK 没初始化

排查：
  - 找"孤儿 Span"（有 parent_span_id 但找不到 parent）
  - 用 trace UI 看是否有断链
```

### 8.2 性能开销

```
SDK 的开销：
  - 创建 Span 对象
  - 序列化到 Collector
  - 网络 IO

📌 优化：
  - 异步批量上报
  - 采样降低开销
  - 本地采样（agent）
  - 控制 attribute 数量
```

### 8.3 数据膨胀

```
一个 Span 含很多 attributes：
  - db.statement 可能含全部 SQL
  - 上传 PII 敏感数据

📌 注意：
  - SQL 截断 / 参数化
  - 不上传敏感字段
  - 定期清理 attribute
```

## 9. 一句话总结

```
📌 分布式追踪是微服务的"X 光片"：看清请求跨服务的完整路径
📌 核心概念：Trace（请求）+ Span（工作单元）+ Parent-Child（调用关系）
📌 数据标准：W3C Trace Context（traceparent header）
📌 跨进程传递：HTTP/gRPC/MQ 的 header + 跨线程的 Context
📌 采样策略：头部采样 1-10% + 错误慢请求强制保留
📌 主流实现：OpenTelemetry（标准）+ Jaeger/Zipkin/SkyWalking（后端）
📌 关键能力：Trace 查询 + 服务依赖图 + Trace-Logs 关联
📌 最大陷阱：异步调用容易丢 trace，需要传递 Context
```

## 10. 参考资料

- OpenTelemetry: https://opentelemetry.io/
- W3C Trace Context: https://www.w3.org/TR/trace-context/
- Jaeger: https://www.jaegertracing.io/
- Zipkin: https://zipkin.io/
- Apache SkyWalking: https://skywalking.apache.org/
- Distributed Tracing (Ben Sigelman, 2020) —— O'Reilly
- Google Dapper Paper (2010) —— 链路追踪鼻祖


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

- [architecture](https://java-px.bot.cd/architecture/):企业架构
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [kafka](https://java-px.bot.cd/kafka/):消息
