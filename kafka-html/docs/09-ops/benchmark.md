---
title: 性能压测
date: 2026-08-15  # date-auto-injected
---

# ⚡ 性能压测

> **性能压测**是 Kafka 上线前必做的环节，能提前发现性能瓶颈，验证 SLA。

## 🎯 压测目标

```
压测回答的问题：
  - 当前集群能扛多少 QPS？
  - 延迟是多少（P50 / P99 / P999）？
  - 资源使用率（CPU / 内存 / 磁盘 / 网络）？
  - 性能瓶颈在哪里？
  - 是否满足 SLA？
```

## 🛠️ 压测工具

### 1. kafka-producer-perf-test.sh（官方工具）

```bash
# 发送 100 万条消息，每条 1KB
kafka-producer-perf-test.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --num-records 1000000 \
    --record-size 1024 \
    --throughput -1 \
    --producer-props \
        acks=all \
        batch.size=65536 \
        linger.ms=10 \
        compression.type=lz4 \
        enable.idempotence=true

# 输出：
# 1000000 records sent, 89432.18 records/sec (87.34 MB/sec)
# 11234 ms total time
```

### 2. kafka-consumer-perf-test.sh

```bash
# 消费 100 万条消息
kafka-consumer-perf-test.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --messages 1000000 \
    --threads 1 \
    --group perf-test

# 输出：
# data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec
# 1024.00, 17.07, 1000000, 16666.67
```

### 3. JMeter

```bash
# 用 JMeter 的 Kafka 插件
# 1. 下载 plugins-manager.jar
# 2. 安装 kafka 插件
# 3. 配置 Kafka Producer Sampler
# 4. 运行压测
```

### 4. 自定义压测程序

```java
public class KafkaStressTest {
    
    public static void main(String[] args) throws Exception {
        int numThreads = 10;
        int recordsPerThread = 100_000;
        int recordSize = 1024;
        
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.LINGER_MS_CONFIG, "10");
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, "65536");
        props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        KafkaProducer<String, byte[]> producer = new KafkaProducer<>(props);
        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        CountDownLatch latch = new CountDownLatch(numThreads);
        AtomicLong totalLatency = new AtomicLong();
        AtomicInteger successCount = new AtomicInteger();
        AtomicInteger errorCount = new AtomicInteger();
        
        byte[] payload = new byte[recordSize];
        Arrays.fill(payload, (byte) 'a');
        
        long start = System.currentTimeMillis();
        
        for (int t = 0; t < numThreads; t++) {
            executor.submit(() -> {
                try {
                    for (int i = 0; i < recordsPerThread; i++) {
                        long sendStart = System.nanoTime();
                        try {
                            RecordMetadata metadata = producer
                                .send(new ProducerRecord<>("stress-test", "key-" + i, payload))
                                .get(10, TimeUnit.SECONDS);
                            long latency = (System.nanoTime() - sendStart) / 1_000;
                            totalLatency.addAndGet(latency);
                            successCount.incrementAndGet();
                        } catch (Exception e) {
                            errorCount.incrementAndGet();
                        }
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await();
        long duration = System.currentTimeMillis() - start;
        
        // 输出统计
        long totalRecords = (long) numThreads * recordsPerThread;
        double throughput = totalRecords * 1000.0 / duration;
        double avgLatency = totalLatency.get() / (double) successCount.get();
        
        System.out.printf("总记录: %d, 耗时: %d ms%n", totalRecords, duration);
        System.out.printf("吞吐: %.2f records/sec%n", throughput);
        System.out.printf("平均延迟: %.2f μs%n", avgLatency);
        System.out.printf("错误数: %d%n", errorCount.get());
        
        producer.close();
        executor.shutdown();
    }
}
```

## 📊 压测场景设计

### 场景 1：基础吞吐压测

```
目标：测试最大吞吐
  - 10 个 Producer 线程
  - 每线程发送 100 万条消息
  - 单消息 1 KB
  - 不限速
  - 测量：吞吐、延迟、错误率
```

### 场景 2：延迟压测

```
目标：测试固定 QPS 下的延迟
  - 10 个 Producer
  - 每秒发送 10 万条（限速）
  - 测试 P50 / P99 / P999 延迟
```

### 场景 3：长时间稳定性

```
目标：测试长时间运行稳定性
  - 持续发送 1 小时
  - 监控：内存、GC、磁盘、网络
  - 检测：内存泄漏、性能下降
```

### 场景 4：故障恢复

```
目标：测试 Broker 故障后的恢复
  - 正常压测 5 分钟
  - Kill 一个 Broker
  - 观察：延迟变化、是否丢消息
  - Broker 恢复
  - 观察：恢复时间
```

## 🛠️ 实战：完整压测流程

### 步骤 1：环境准备

```bash
# 1. 准备测试集群（与生产相同配置）
# 3 Broker + NVMe SSD + 万兆网卡

# 2. 创建测试 Topic
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic stress-test --partitions 12 --replication-factor 3 \
    --config retention.ms=3600000

# 3. 准备压测工具
# 下载 kafka-producer-perf-test.sh
# 或准备 JMeter
```

### 步骤 2：基线压测

```bash
# 测试 1：单 Producer 单 Partition
kafka-producer-perf-test.sh \
    --bootstrap-server localhost:9092 \
    --topic stress-test:0 \
    --num-records 1000000 \
    --record-size 1024 \
    --throughput -1 \
    --producer-props acks=1

# 记录基线数据
# 例如：100 MB/s / 单 Partition

# 测试 2：多 Producer 多 Partition
kafka-producer-perf-test.sh \
    --bootstrap-server localhost:9092 \
    --topic stress-test \
    --num-records 1000000 \
    --record-size 1024 \
    --throughput -1 \
    --producer-props acks=all batch.size=65536 linger.ms=10

# 记录：吞吐（应该更高）
```

### 步骤 3：压力递进

```bash
# 测试不同 QPS 下的延迟
for qps in 10000 30000 50000 100000 150000 200000; do
    echo "=== QPS: $qps ==="
    kafka-producer-perf-test.sh \
        --bootstrap-server localhost:9092 \
        --topic stress-test \
        --num-records $((qps * 60)) \
        --record-size 1024 \
        --throughput $qps \
        --producer-props acks=all batch.size=65536 linger.ms=10
done

# 输出：QPS vs 延迟 曲线
```

### 步骤 4：收集结果

```bash
# 收集 Broker 指标
while true; do
    echo "=== $(date) ==="
    echo "CPU: $(top -bn1 | grep 'Cpu(s)' | awk '{print $2}')"
    echo "Memory: $(free -h | awk 'NR==2 {print $3/$2 * 100.0}')"
    echo "Disk: $(df -h /var/lib/kafka | awk 'NR==2 {print $5}')"
    echo "Network: $(sar -n DEV 1 1 | grep 'Average' | awk '{print $2" "$5}')"
    sleep 10
done > /tmp/kafka-stress-test-$(date +%Y%m%d-%H%M%S).log

# 收集 Kafka JMX 指标
jmxterm -l localhost:9999 << EOF
get -b kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec
get -b kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec
EOF
```

### 步骤 5：分析结果

```python
# 压测结果分析示例
results = {
    'baseline': {
        'qps': 100000,
        'latency_p50': 5,    # ms
        'latency_p99': 50,   # ms
        'latency_p999': 200, # ms
        'cpu_usage': 60,     # %
        'memory_usage': 70,  # %
        'network_usage': 50, # %
    },
    'peak': {
        'qps': 200000,
        'latency_p50': 8,
        'latency_p99': 100,
        'latency_p999': 500,
        'cpu_usage': 85,    # 接近瓶颈
        'memory_usage': 80,
        'network_usage': 80,
    }
}

# 结论：
# - 当前集群在 10 万 QPS 下延迟 < 50ms（满足 SLA）
# - 峰值 20 万 QPS 下延迟 < 100ms（满足 SLA）
# - CPU 在 85% 接近瓶颈（建议扩容）
```

## 📊 性能基线参考

### 硬件配置下的吞吐

```
单机 Kafka 性能（NVMe SSD + 32GB RAM）：

配置：acks=1 + 不压缩
  - 写入：~150 MB/s
  - 延迟：~3 ms (P99)

配置：acks=all + lz4 压缩
  - 写入：~120 MB/s（压缩后 ~60 MB/s 实际数据）
  - 延迟：~10 ms (P99)

配置：acks=all + 幂等性
  - 写入：~100 MB/s
  - 延迟：~15 ms (P99)
```

### 延迟分布参考

```
典型延迟分布（NVMe SSD）：

操作                 P50    P99    P999
单条 Produce (acks=1)   1ms   5ms   20ms
单条 Produce (acks=all) 5ms   50ms  200ms
单条 Consume (fetch)    1ms   10ms  50ms
事务提交                10ms  100ms 500ms
```

## 📊 性能优化清单

### Producer 优化

```yaml
# 启用所有性能优化
linger.ms: 20                  # 批处理等待
batch.size: 131072             # 128 KB 批次
compression.type: lz4          # 压缩
buffer.memory: 134217728       # 128 MB 累加器
enable.idempotence: true       # 幂等性
max.in.flight.requests.per.connection: 5
acks: 1                         # 牺牲一致性换吞吐（或 all 视场景）
```

### Consumer 优化

```yaml
fetch.min.bytes: 1
fetch.max.wait.ms: 100         # 长轮询
max.poll.records: 1000         # 一次拉 1000 条
max.partition.fetch.bytes: 1048576  # 1 MB
isolation.level: read_committed
```

### Broker 优化

```properties
# 网络
num.network.threads: 4
num.io.threads: 8

# 磁盘
log.flush.interval.messages: 10000
log.flush.interval.ms: 1000
log.segment.bytes: 1073741824

# JVM
KAFKA_HEAP_OPTS="-Xmx6G -Xms6G"
KAFKA_JVM_PERFORMANCE_OPTS="-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20"
```

## 🛠️ 性能瓶颈诊断

### 瓶颈 1：CPU 高

```
原因：频繁 GC、加密/解密、压缩
诊断：
  jstack <pid> | grep -c "RUNNABLE"
  jstat -gcutil <pid> 1000
解决：
  1. 减少 GC（调优堆）
  2. 关闭压缩（如果不需要）
  3. 增加 CPU 核心
```

### 瓶颈 2：磁盘 IO 高

```
原因：机械硬盘、过多磁盘操作
诊断：
  iostat -x 1
解决：
  1. 升级 NVMe SSD
  2. 多磁盘分散
  3. 减少 log.flush 频率
```

### 瓶颈 3：网络带宽

```
原因：单网卡带宽不足
诊断：
  sar -n DEV 1
解决：
  1. 升级 10G → 25G → 100G 网卡
  2. 多网卡绑定
  3. 启用压缩
```

### 瓶颈 4：Lag 持续增长

```
原因：Consumer 处理慢
诊断：
  - Consumer 日志
  - 慢请求
解决：
  1. 优化消费逻辑
  2. 增加 Consumer 实例
  3. 增加 Partition
```

## ⚠️ 压测注意事项

```
⚠️ 压测环境应与生产环境配置一致
⚠️ 压测数据应模拟真实业务
⚠️ 压测时间应足够长（至少 10 分钟）
⚠️ 多次压测取平均值
⚠️ 监控所有指标（不只看吞吐）
⚠️ 注意磁盘空间（压测可能产生大量数据）
```

## 🎯 总结

**性能压测核心要点**：
- ✅ 使用官方工具或自定义压测
- ✅ 设计多种场景（吞吐/延迟/稳定性/故障）
- ✅ 收集全维度指标（CPU/内存/磁盘/网络）
- ✅ 与生产环境配置一致
- ✅ 性能优化清单
- ⚠️ 多次压测取平均值
- ⚠️ 关注延迟分布（P50/P99/P999）

**下一步：** [💾 JVM 调优](/09-ops/jvm) — Broker 性能优化


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
