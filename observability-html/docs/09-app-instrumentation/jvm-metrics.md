---
title: JVM 指标采集
description: JMX / Micrometer / async-profiler
---

# JVM 指标采集

> **TL;DR**：**JVM 指标采集 = JMX → Prometheus 格式**。**主流方案：Micrometer + Prometheus Registry + JMX Exporter**。**关键指标：堆内存 / GC / 线程 / 类加载 / JIT**。**生产必备：堆内存 + GC 暂停时间 + 线程数 + JIT 编译**。

## 一句话定义

```
JVM 指标 = Java 应用的内部状态
        = 通过 JMX 暴露
        = 转换为 Prometheus 格式后抓取
        = 工具：Micrometer / JMX Exporter / async-profiler
```

## Micrometer + Prometheus（推荐）

```xml
<!-- Maven 依赖 -->
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```java
// Spring Boot 自动配置（application.yml）
management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics, prometheus
  metrics:
    tags:
      application: order-service
    distribution:
      percentiles-histogram:
        http.server.requests: true
      percentiles:
        http.server.requests: 0.5, 0.95, 0.99
```

```java
// 手动埋点
@RestController
public class OrderController {
    private final Counter orderCounter;
    private final Timer orderTimer;

    public OrderController(MeterRegistry registry) {
        this.orderCounter = Counter.builder("orders.processed")
            .tag("status", "success")
            .register(registry);
        this.orderTimer = Timer.builder("orders.duration")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(registry);
    }

    @PostMapping("/orders")
    public Order create() {
        return orderTimer.record(() -> {
            // 业务
            orderCounter.increment();
            return newOrder;
        });
    }
}
```

## JMX Exporter（独立 Java agent）

```bash
# 1. 下载 jmx_prometheus_javaagent
curl -L -o jmx_prometheus_javaagent.jar   https://github.com/prometheus/jmx_exporter/releases/latest/download/jmx_prometheus_javaagent.jar

# 2. 创建 config.yml
cat > config.yml << 'EOF'
---
lowercaseOutputName: true
lowercaseOutputLabelNames: true
rules:
  - pattern: 'java.lang<type=Memory><HeapMemoryUsage>(\w+):'
    name: jvm_memory_heap_bytes
    type: GAUGE
    attrNameSnakeCase: true
    labels:
      area: heap
  - pattern: 'java.lang<type=Memory><NonHeapMemoryUsage>(\w+):'
    name: jvm_memory_nonheap_bytes
    type: GAUGE
    labels:
      area: nonheap
  - pattern: 'java.lang<type=GarbageCollector, name=(\w+)><CollectionCount>'
    name: jvm_gc_collection_seconds_count
    type: COUNTER
    labels:
      gc: $1
  - pattern: 'java.lang<type=GarbageCollector, name=(\w+)><CollectionTime>'
    name: jvm_gc_collection_seconds_sum
    type: COUNTER
    labels:
      gc: $1
  - pattern: 'java.lang<type=Threading><(.*)>'
    name: jvm_threads_$2
    type: GAUGE
EOF

# 3. 启动 jar
java -javaagent:./jmx_prometheus_javaagent.jar=8080:config.yml      -jar order-service.jar
```

## 关键 JVM 指标

```promql
# 1. 堆内存使用
jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} * 100

# 2. GC 暂停时间（最关键）
rate(jvm_gc_collection_seconds_sum[5m])
/ rate(jvm_gc_collection_seconds_count[5m])
# G1 通常 5-50ms，ZGC/Shenandoah < 1ms

# 3. GC 频率
rate(jvm_gc_collection_seconds_count[5m])

# 4. 活跃线程
jvm_threads_current

# 5. 守护线程
jvm_threads_daemon

# 6. 类加载
jvm_classes_loaded

# 7. JIT 编译（OpenJ9 才有，HotSpot 不暴露）

# 8. JVM CPU
process_cpu_seconds_total
```

## 实战告警

```yaml
# Prometheus rules
- alert: JVMHeapHigh
  expr: jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} > 0.85
  for: 5m
  labels: {severity: warning}
  annotations:
    summary: "堆内存使用率 > 85%"

- alert: JVMLongGCPause
  expr: |
    rate(jvm_gc_collection_seconds_sum[5m])
    / rate(jvm_gc_collection_seconds_count[5m])
    > 0.1   # 100ms
  for: 5m
  labels: {severity: warning}
  annotations:
    summary: "平均 GC 暂停 > 100ms（考虑 G1 → ZGC）"

- alert: JVMThreadLeak
  expr: |
    jvm_threads_current
    >
    jvm_threads_current offset 1h * 1.5   # 1 小时增长 50%
  for: 10m
  labels: {severity: critical}
  annotations:
    summary: "线程数 1h 内增长 50%（可能是线程泄漏）"
```

## GC 选择对比

| GC | 暂停时间 | 适用 |
|---|---|---|
| G1 | 50-200ms | 默认 / 通用 |
| ZGC | < 1ms | 大堆（>32G）/ 低延迟 |
| Shenandoah | < 1ms | 低延迟（同 ZGC） |
| Parallel | 100ms+ | 高吞吐 / 批处理 |
| CMS | 已废弃 | 不要再用 |

## 一句话总结

> **JVM 指标 = Micrometer + JMX Exporter**。**关键指标：堆 / GC / 线程 / 类加载**。**GC 暂停 < 100ms 是健康值**。**大堆 + 低延迟选 ZGC / Shenandoah**。

---

## 关联章节

- [RED 方法](./red-method.md) — 服务级指标
- [USE 方法](./use-method.md) — JVM 即资源
- [业务指标](./business-metrics.md) — 业务维度
- [持续剖析](../10-profiling/continuous-profiling.md) — 更深定位

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
