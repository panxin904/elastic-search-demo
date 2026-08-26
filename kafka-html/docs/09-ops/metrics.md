---
title: 监控指标
---

# 📈 监控指标

> **Kafka 监控指标**是保障集群健康的基础。本章详解所有关键指标的采集、监控和告警。

## 🎯 监控层次

```
Kafka 监控 4 个层次：
  1. 基础设施层（CPU、内存、磁盘、网络）
  2. JVM 层（GC、Heap、线程）
  3. Broker 层（吞吐量、副本、Controller）
  4. 应用层（Producer/Consumer 业务指标）
```

## 📊 Broker 关键指标

### 1. 集群状态

```bash
# 活跃 Controller（必须 = 1）
kafka_controller_active_count

# 在线 Broker 数
kafka_cluster_brokers

# Topic 总数
kafka_topic_partitions

# Under-Replicated Partition（必须 = 0）
kafka_topic_partition_under_replicated_partition_count

# 离线 Partition
kafka_topic_partition_offline_partition_count
```

### 2. 吞吐量

```bash
# 写入速率（消息/秒）
kafka_server_broker_topic_metrics_messages_in_per_sec

# 写入字节速率
kafka_server_broker_topic_metrics_bytes_in_per_sec

# 读取字节速率
kafka_server_broker_topic_metrics_bytes_out_per_sec

# Producer 请求速率
kafka_network_request_metrics_total_time_ms

# Consumer 请求速率
kafka_network_request_metrics_total_time_ms
```

### 3. 副本同步

```bash
# ISR 收缩次数（不应该频繁发生）
kafka_server_replica_manager_under_replicated_partitions

# 副本同步速率
kafka_server_replica_fetcher_manager_max_lag

# Leader 选举速率
kafka_controller_controller_stats_leader_election_rate_and_time_ms
```

### 4. 网络

```bash
# 请求队列大小
kafka_network_request_channel_queue_size

# 响应队列大小
kafka_network_response_queue_size

# 网络空闲时间百分比（越高越好）
kafka_network_socket_server_network_processor_idle_percent
```

## 📊 Producer 关键指标

### 1. 发送速率

```bash
# 发送消息速率
producer_record_send_rate

# 发送字节速率
producer_byte_rate
```

### 2. 错误与重试

```bash
# 错误率（应该接近 0）
producer_record_error_rate

# 重试率
producer_record_retry_rate
```

### 3. 延迟

```bash
# 请求延迟平均值（毫秒）
producer_request_latency_avg

# 请求延迟 P99
producer_request_latency_p99

# 队列等待时间
producer_record_queue_time_avg
```

### 4. 资源

```bash
# 累加器等待线程数（> 0 表示背压）
producer_waiting_threads

# 累加器内存使用
producer_buffer_available_bytes

# 活跃连接数
producer_connection_count
```

## 📊 Consumer 关键指标

### 1. 消费速率

```bash
# 拉取速率
consumer_fetch_rate

# 消费速率
consumer_records_consumed_rate

# 消费字节速率
consumer_bytes_consumed_rate
```

### 2. 延迟

```bash
# 拉取延迟
consumer_fetch_latency_avg

# 拉取延迟 P99
consumer_fetch_latency_p99
```

### 3. Lag（最关键）

```bash
# Records Lag
consumer_records_lag

# Consumer Group Lag
kafka_consumergroup_lag

# 每个 Partition 的 Lag
kafka_consumergroup_lag{consumergroup="order-processor"}
```

### 4. Rebalance

```bash
# Rebalance 频率（每小时 < 5 次）
consumer_coordinator_rebalance_rate_per_hour

# 分配 Partition 数
consumer_assigned_partitions
```

## 📊 JVM 关键指标

### 1. GC

```bash
# GC 暂停时间（秒）
jvm_gc_pause_seconds_sum
jvm_gc_pause_seconds_max

# GC 暂停次数
jvm_gc_pause_seconds_count
```

### 2. 内存

```bash
# 堆内存使用
jvm_memory_bytes_used{area="heap"}

# 堆内存最大
jvm_memory_bytes_max{area="heap"}

# 各区域使用
jvm_memory_bytes_used{area="eden"}
jvm_memory_bytes_used{area="old"}
jvm_memory_bytes_used{area="survivor"}
```

### 3. 线程

```bash
# 活跃线程
jvm_threads_live_threads

# 守护线程
jvm_threads_daemon_threads

# 死锁线程（必须 = 0）
jvm_threads_deadlocked
```

## 📊 基础设施指标

### 1. CPU

```bash
# CPU 使用率
node_cpu_seconds_total{mode="user"}
node_cpu_seconds_total{mode="system"}
node_load1
node_load5
```

### 2. 内存

```bash
# 内存使用
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes
node_memory_Buffers_bytes
node_memory_Cached_bytes

# Swap（应该 = 0）
node_memory_SwapTotal_bytes
```

### 3. 磁盘

```bash
# 磁盘使用
node_filesystem_size_bytes
node_filesystem_avail_bytes
node_filesystem_used_percent

# 磁盘 IO
node_disk_read_bytes_total
node_disk_written_bytes_total
node_disk_io_now
```

### 4. 网络

```bash
# 网络流量
node_network_receive_bytes_total
node_network_transmit_bytes_total

# 网络丢包
node_network_receive_drop_total
node_network_transmit_drop_total
```

## 🛠️ 监控体系搭建

### 1. JMX Exporter（采集 JVM 指标）

```bash
# 下载 JMX Exporter
wget https://repo1.maven.org/maven2/io/prometheus/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar

# Kafka 启动配置
export KAFKA_JMX_OPTS="-javaagent:/opt/jmx_prometheus_javaagent.jar=7071:/opt/kafka-jmx.yml"
```

```yaml
# kafka-jmx.yml
---
lowercaseOutputName: true
rules:
  # Kafka Broker
  - pattern: "kafka.server<type=(.+), name=(.+)><>Value"
    name: "kafka_server_$1_$2"
    type: GAUGE
  - pattern: "kafka.server<type=(.+), name=(.+)><>Count"
    name: "kafka_server_$1_$2_total"
    type: COUNTER
  
  # JVM
  - pattern: "java.lang<type=(.+), name=(.+)><>Value"
    name: "jvm_$1_$2"
  
  # GC
  - pattern: "java.lang<type=GarbageCollector, name=(.+)><>CollectionCount"
    name: "jvm_gc_collection_count_$1_total"
    type: COUNTER
  - pattern: "java.lang<type=GarbageCollector, name=(.+)><>CollectionTime"
    name: "jvm_gc_collection_time_$1_seconds"
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

### 3. Prometheus + Grafana

```yaml
# docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
  
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
  
  alertmanager:
    image: prom/alertmanager:latest
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml

volumes:
  prometheus-data:
  grafana-data:
```

### 4. Grafana Dashboard

```yaml
# 推荐 Dashboard
1. Confluent Kafka Dashboard（官方）
   - https://grafana.com/grafana/dashboards/721

2. Kafka Lag Exporter
   - https://grafana.com/grafana/dashboards/12485

3. 自定义业务 Dashboard
   - 业务相关指标
   - 业务 SLA
```

## 📊 关键监控指标查询（PromQL）

### Lag 查询

```promql
# 总 Lag
sum(kafka_consumergroup_lag) by (consumergroup, topic)

# 平均 Lag
avg(kafka_consumergroup_lag) by (consumergroup)

# 最大 Lag
max(kafka_consumergroup_lag) by (consumergroup)

# Lag 增长率
rate(kafka_consumergroup_lag[5m])
```

### 吞吐量查询

```promql
# 总写入速率
sum(rate(kafka_server_broker_topic_metrics_messages_in_total[5m]))

# 读取速率
sum(rate(kafka_server_broker_topic_metrics_bytes_out_total[5m]))

# Top 10 Topic（按写入速率）
topk(10, sum by (topic) (rate(kafka_server_broker_topic_metrics_messages_in_total[5m])))
```

### 健康检查

```promql
# Active Controller
kafka_controller_active_count

# Under-Replicated Partition
sum(kafka_topic_partition_under_replicated_partition_count)

# Offline Partition
sum(kafka_topic_partition_offline_partition_count)
```

## 📊 告警规则（完整版）

```yaml
groups:
  - name: kafka_cluster
    interval: 30s
    rules:
      # Broker 不可用
      - alert: KafkaBrokerDown
        expr: kafka_controller_active_count == 0
        for: 1m
        labels:
          severity: critical
      
      # Broker 离线
      - alert: KafkaBrokerOffline
        expr: kafka_cluster_brokers < 3
        for: 5m
        labels:
          severity: critical
      
      # Under-Replicated Partition
      - alert: KafkaUnderReplicatedPartitions
        expr: sum(kafka_topic_partition_under_replicated_partition_count) > 0
        for: 5m
        labels:
          severity: warning
      
      # Offline Partition
      - alert: KafkaOfflinePartitions
        expr: sum(kafka_topic_partition_offline_partition_count) > 0
        for: 1m
        labels:
          severity: critical
  
  - name: kafka_consumer
    interval: 30s
    rules:
      # Consumer 积压严重
      - alert: KafkaConsumerLagHigh
        expr: kafka_consumergroup_lag > 10000
        for: 5m
        labels:
          severity: warning
      
      # Consumer 积压严重（小时级）
      - alert: KafkaConsumerLagCritical
        expr: kafka_consumergroup_lag > 100000
        for: 30m
        labels:
          severity: critical
      
      # Consumer 离线
      - alert: KafkaConsumerDown
        expr: kafka_consumergroup_members == 0
        for: 2m
        labels:
          severity: critical
  
  - name: kafka_producer
    interval: 30s
    rules:
      # Producer 错误率高
      - alert: KafkaProducerErrorRate
        expr: rate(producer_record_error_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
      
      # Producer 延迟高
      - alert: KafkaProducerLatencyHigh
        expr: producer_request_latency_p99 > 100
        for: 5m
        labels:
          severity: warning
  
  - name: kafka_jvm
    interval: 30s
    rules:
      # GC 暂停过长
      - alert: KafkaLongGCPause
        expr: jvm_gc_pause_seconds_max > 5
        for: 5m
        labels:
          severity: warning
      
      # 堆内存使用率高
      - alert: KafkaHeapMemoryHigh
        expr: jvm_memory_bytes_used{area="heap"} / jvm_memory_bytes_max{area="heap"} > 0.85
        for: 5m
        labels:
          severity: warning
  
  - name: kafka_disk
    interval: 30s
    rules:
      # 磁盘使用率高
      - alert: KafkaDiskUsageHigh
        expr: (node_filesystem_avail_bytes{mountpoint="/var/lib/kafka"} / node_filesystem_size_bytes{mountpoint="/var/lib/kafka"}) * 100 < 20
        for: 5m
        labels:
          severity: warning
```

## 🛠️ 监控最佳实践

### 1. 分层监控

```
✅ 基础设施层（必选）
   - CPU、内存、磁盘、网络

✅ JVM 层（必选）
   - GC、Heap、线程

✅ Kafka 层（必选）
   - Broker 状态、副本、吞吐

✅ 应用层（推荐）
   - Producer/Consumer 业务指标
```

### 2. 告警分级

```
P0 / Critical（立即处理）：
  - Kafka 集群不可用
  - 数据丢失风险
  - 磁盘满

P1 / Warning（工作时间处理）：
  - Lag 持续高
  - 副本同步失败

P2 / Info（观察）：
  - 资源使用率高
```

### 3. 告警要 actionable

```
✅ 告警要有明确行动
   - "增加 Consumer 实例"
   - "清理磁盘空间"
   - "重启 Broker"

❌ 告警模糊不清
   - "Kafka 不正常"
```

### 4. 告警聚合

```
✅ 多告警合并（同一个问题）
✅ 告警静默（已处理的问题）
✅ 告警升级（未处理的 P1 → P0）
```

## ⚠️ 常见问题

### 问题 1：监控指标缺失

```
原因：JMX Exporter 配置不正确
解决：
  1. 检查 Kafka 启动参数
  2. 访问 :7071/metrics 验证
  3. 检查 Prometheus target
```

### 问题 2：告警太多

```
原因：阈值设置不合理
解决：
  1. 调整告警阈值
  2. 告警聚合
  3. 静默已处理告警
```

### 问题 3：监控延迟

```
原因：Prometheus scrape interval 太长
解决：
  调整 scrape_interval 到 15-30 秒
```

## 🎯 总结

**监控指标核心要点**：
- ✅ 4 层监控（基础设施/JVM/Broker/应用）
- ✅ 关键指标：Lag、副本、GC、磁盘
- ✅ Prometheus + Grafana + AlertManager
- ✅ 告警分级（P0/P1/P2）
- ✅ 告警要 actionable
- ⚠️ 监控全维度（不仅看 QPS）
- ⚠️ 定期 review 告警规则

**下一步：** [🚑 故障恢复](/09-ops/disaster-recovery) — 灾难恢复方案


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
