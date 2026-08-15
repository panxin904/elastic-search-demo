---
title: 监控告警
---

# 📊 监控告警

> **监控告警**是 Kafka 生产环境稳定运行的基石。本章详解 Kafka 监控体系、关键指标和告警规则。

## 🎯 监控层次

```
Kafka 监控 4 层：
  1. 基础设施层（磁盘、内存、网络、CPU）
  2. JVM 层（GC、堆内存、线程）
  3. Kafka Broker 层（吞吐量、Lag、副本）
  4. 应用层（Producer/Consumer 业务指标）
```

## 📊 关键指标

### 1. Broker 指标

```bash
# Broker 数量、活跃 Controller
kafka_controller_active_count
kafka_cluster_brokers

# Topic 数量、Partition 数量
kafka_topic_partitions

# 副本数、Under-Replicated Partition
kafka_topic_partition_replicas
kafka_topic_partition_under_replicated_partition_count

# ISR 数量
kafka_topic_partition_in_sync_replica_count
```

### 2. 吞吐量指标

```bash
# 消息入/出速率
kafka_server_broker_topic_metrics_messages_in_per_sec
kafka_server_broker_topic_metrics_bytes_in_per_sec
kafka_server_broker_topic_metrics_bytes_out_per_sec

# Producer/Consumer 请求速率
kafka_network_request_metrics_total_time_ms
kafka_network_socket_server_network_processor_idle_percent
```

### 3. Consumer Lag（最关键）

```bash
# 每个 Group 的 Lag
kafka_consumergroup_lag
kafka_consumergroup_members

# Consumer 提交延迟
kafka_consumer_fetch_manager_records_lag
```

### 4. JVM 指标

```bash
# GC 次数和时间
jvm_gc_pause_seconds_count
jvm_gc_pause_seconds_sum

# 堆内存使用
jvm_memory_bytes_used{area="heap"}
jvm_memory_bytes_max{area="heap"}

# 线程数
jvm_threads_live_threads
```

### 5. 磁盘指标

```bash
# 磁盘使用
node_filesystem_avail_bytes
node_filesystem_used_percent
```

## 🛠️ 部署监控体系

### 1. JMX Exporter（采集 JVM 指标）

```bash
# 下载 JMX Exporter
wget https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar

# Kafka Broker 启动配置
export KAFKA_JMX_OPTS="-javaagent:/opt/jmx_prometheus_javaagent.jar=7071:/opt/kafka-jmx.yml"

# kafka-jmx.yml 配置
---
lowercaseOutputName: true
rules:
  - pattern: "kafka.server<type=(.+), name=(.+)><>Value"
    name: "kafka_server_$1_$2"
    type: GAUGE
  - pattern: "kafka.server<type=(.+), name=(.+)><>Count"
    name: "kafka_server_$1_$2_total"
    type: COUNTER
```

### 2. Kafka Exporter（采集 Kafka 指标）

```bash
# 部署 kafka_exporter
docker run -d --name kafka-exporter \
    -p 9308:9308 \
    bitnami/kafka-exporter \
    --kafka.server=localhost:9092
```

```yaml
# prometheus.yml
scrape_configs:
  - job_name: kafka-exporter
    static_configs:
      - targets: ['localhost:9308']
```

### 3. Prometheus + Grafana

```yaml
# docker-compose.yml
version: '3'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

### 4. Grafana Dashboard

```
推荐 Dashboard：
  - Confluent Kafka Dashboard（官方）
  - Kafka Lag Exporter Dashboard
  - 自定义业务 Dashboard
```

## 📊 Prometheus 告警规则

```yaml
groups:
  - name: kafka_broker
    interval: 30s
    rules:
      # Broker 不可用
      - alert: KafkaBrokerDown
        expr: kafka_controller_active_count == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kafka Broker 不可用"
      
      # 副本同步失败
      - alert: KafkaUnderReplicatedPartitions
        expr: sum(kafka_topic_partition_under_replicated_partition_count) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "存在副本同步失败的 Partition"
      
      # 磁盘使用率高
      - alert: KafkaDiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/var/lib/kafka"} / node_filesystem_size_bytes{mountpoint="/var/lib/kafka"}) < 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka 磁盘使用超过 90%"
  
  - name: kafka_consumer
    interval: 30s
    rules:
      # Consumer 积压严重
      - alert: KafkaConsumerLagHigh
        expr: kafka_consumergroup_lag > 10000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Consumer Group {{ $labels.consumergroup }} 积压 {{ $value }} 条"
      
      # Consumer 离线
      - alert: KafkaConsumerDown
        expr: kafka_consumergroup_members == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Consumer Group {{ $labels.consumergroup }} 没有活跃 Consumer"
  
  - name: kafka_jvm
    interval: 30s
    rules:
      # GC 暂停过长
      - alert: KafkaLongGCPause
        expr: jvm_gc_pause_seconds_max > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "JVM GC 暂停超过 5 秒"
      
      # 堆内存使用率高
      - alert: KafkaHeapMemoryHigh
        expr: jvm_memory_bytes_used{area="heap"} / jvm_memory_bytes_max{area="heap"} > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka JVM 堆内存使用超过 85%"
```

## 📊 自定义业务监控

### Spring Boot 应用指标

```java
@Component
public class KafkaBusinessMetrics {
    
    private final Counter messagesSent;
    private final Counter messagesConsumed;
    private final Counter messagesError;
    private final Timer processingTime;
    
    public KafkaBusinessMetrics(MeterRegistry registry) {
        this.messagesSent = Counter.builder("kafka_messages_sent_total")
            .description("Total Kafka messages sent")
            .tag("topic", "orders")
            .register(registry);
        this.messagesConsumed = Counter.builder("kafka_messages_consumed_total")
            .description("Total Kafka messages consumed")
            .tag("topic", "orders")
            .tag("group", "order-processor")
            .register(registry);
        this.messagesError = Counter.builder("kafka_messages_error_total")
            .description("Total Kafka error messages")
            .register(registry);
        this.processingTime = Timer.builder("kafka_processing_time")
            .description("Time to process a Kafka message")
            .register(registry);
    }
    
    public void recordSent() {
        messagesSent.increment();
    }
    
    public void recordConsumed() {
        messagesConsumed.increment();
    }
    
    public void recordError() {
        messagesError.increment();
    }
    
    public void recordProcessingTime(Duration duration) {
        processingTime.record(duration);
    }
}
```

### 应用层埋点

```java
@Service
public class MonitoredOrderConsumer {
    
    @Autowired
    private KafkaBusinessMetrics metrics;
    
    @KafkaListener(topics = "orders")
    public void consume(OrderEvent event, Acknowledgment ack) {
        Timer.Sample sample = Timer.start();
        try {
            // 业务处理
            processOrder(event);
            
            // 记录成功
            metrics.recordConsumed();
            ack.acknowledge();
            
        } catch (Exception e) {
            // 记录失败
            metrics.recordError();
            throw e;
        } finally {
            // 记录处理时间
            sample.stop(metrics.getProcessingTimer());
        }
    }
}
```

## 📊 监控指标分类

### 业务指标

```java
// 业务自定义指标
Counter.builder("orders_processed_total")
    .tag("type", "create")
    .register(registry);

Counter.builder("orders_amount_total")
    .tag("currency", "USD")
    .register(registry);

Gauge.builder("active_users")
    .register(registry, this, MonitoredOrderConsumer::getActiveUserCount);
```

### 链路追踪

```java
@Service
public class TracedOrderProducer {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    public void sendOrder(OrderEvent event) {
        // 1. 设置 traceId
        MDC.put("traceId", UUID.randomUUID().toString());
        
        // 2. 通过 Headers 传递 traceId
        Message<OrderEvent> message = MessageBuilder.withPayload(event)
            .setHeader("traceId", MDC.get("traceId"))
            .setHeader("source", "order-service")
            .build();
        
        kafkaTemplate.send(message);
    }
}

@Service
public class TracedOrderConsumer {
    
    @KafkaListener(topics = "orders")
    public void consume(OrderEvent event, @Header("traceId") String traceId) {
        try {
            MDC.put("traceId", traceId);
            processOrder(event);
        } finally {
            MDC.clear();
        }
    }
}
```

## 📊 告警渠道

```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'cluster']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://example.com/alert'
  
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: '<pagerduty-key>'
  
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/...'
        channel: '#kafka-alerts'
```

## 📊 监控最佳实践

### 1. 关键指标金字塔

```
                  用户体验
                  ↑（业务指标：处理延迟、成功率）
               API 响应时间
               ↑（应用指标：消息处理时间）
            Kafka Consumer Lag
            ↑（Kafka 指标：消息积压）
         Broker 吞吐量
         ↑（Kafka 指标：messages/sec）
      JVM 性能
      ↑（JVM 指标：GC、堆内存）
   基础设施
   ↑（OS 指标：CPU、内存、磁盘、网络）
```

### 2. 告警分级

```
P0 / Critical（立即处理）：
  - Broker 不可用
  - Consumer 全部离线
  - 磁盘满
  - 数据丢失风险

P1 / Warning（工作时间处理）：
  - Lag 持续高
  - 副本同步失败
  - GC 暂停过长

P2 / Info（观察）：
  - Lag 略高
  - 资源使用率高
```

### 3. 告警疲劳预防

```
✅ 告警要 actionable（能采取行动）
✅ 告警要有上下文（包含原因）
✅ 告警要分级（不同级别不同渠道）
✅ 告警要避免重复（聚合）
✅ 告警要定期 review
```

## ⚠️ 常见问题

### 问题 1：监控不全面

```
解决：
  1. 监控 4 个层次（基础设施/JVM/Broker/应用）
  2. 业务指标 + 技术指标
  3. 主动监控 + 被动告警
```

### 问题 2：告警疲劳

```
现象：告警太多被忽略
解决：
  1. 告警分级
  2. 告警合并（多个一起告）
  3. 静默期（已处理的告警不发）
```

### 问题 3：监控数据不准

```
原因：采样、时钟不同步
解决：
  1. 全量采集
  2. NTP 同步
  3. 定期校验
```

## 🎯 总结

**监控告警核心要点**：
- ✅ 4 个监控层次（基础设施/JVM/Broker/应用）
- ✅ 关键指标：Lag、副本、吞吐、GC
- ✅ Prometheus + Grafana 推荐
- ✅ 告警分级（P0/P1/P2）
- ✅ 业务指标 + 技术指标结合
- ⚠️ 告警疲劳预防
- ⚠️ 监控数据准确性

**下一步：** [🌍 多环境隔离](/08-enterprise/multi-env) — dev/test/prod 隔离
