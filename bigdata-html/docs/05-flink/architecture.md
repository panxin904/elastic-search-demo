---
title: Flink 架构
date: 2026-08-15  # date-auto-injected
---
# Flink 架构

## 1. 整体架构

```
        Client
          ↓ 提交 Job
        JobManager (Master)
        - 调度 (Scheduler)
        - Checkpoint 协调
        - HA (ZooKeeper)
          ↓
        TaskManagers (Worker)
        - TaskSlots (并行度)
        - 内存 + 磁盘
        - 算子链
```

## 2. 核心概念

### Stream / Batch（统一）

```
有界流：批处理（DataSet API 已废弃，用 Table / DataStream）
无界流：真正的流处理

Flink 一切都是流：
  批 = 有界流
  流 = 无界流
  同一套 API
```

### 算子（Operator）

```
Source → map → filter → keyBy → window → aggregate → Sink
  ↕         ↕        ↕         ↕         ↕           ↕
  并行度     并行度    分组     窗口     聚合       输出
```

### 时间（Event Time vs Processing Time）

```
Event Time：事件实际发生时间（业务时间戳）
Processing Time：算子处理时间（系统时间）

推荐：Event Time + Watermark
  - 准确（即使乱序）
  - 可重放（replay）
```

### Watermark（水位线）

```
表示"时间 < T 的事件都已到达"
例：Watermark(10:00:05) 表示 10:00:05 之前的事件都到了
```

## 3. 核心 API

```java
// 1. DataStream API（核心流 API）
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
DataStream<String> stream = env.socketTextStream("localhost", 9999);

// 2. Table API（SQL 风格）
EnvironmentSettings settings = EnvironmentSettings.inBatchMode();
TableEnvironment tableEnv = TableEnvironment.create(settings);
tableEnv.executeSql("CREATE TABLE events (id STRING, ts TIMESTAMP(3)) WITH (...)");

// 3. Flink SQL（推荐）
tableEnv.executeSql("SELECT user_id, COUNT(*) FROM events GROUP BY TUMBLE(ts, INTERVAL '1' MINUTE), user_id");
```

## 4. 部署模式

### 4.1 单机模式

```bash
# 本地开发
flink run -c com.example.MyJob /opt/my-job.jar
```

### 4.2 Standalone 集群

```bash
jobmanager.sh start cluster
taskmanager.sh start

# 提交
flink run -c com.example.MyJob /opt/my-job.jar
# Web UI: http://jobmanager:8081
```

### 4.3 YARN

```bash
flink run -m yarn-cluster -yjm 1024m -ytm 4096m   -c com.example.MyJob /opt/my-job.jar
```

### 4.4 Kubernetes

```yaml
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: basic-example
spec:
  image: flink:1.18
  flinkVersion: v1_18
  jobManager:
    resource:
      memory: "1024m"
      cpu: 1
  taskManager:
    resource:
      memory: "2048m"
      cpu: 1
  job:
    jarURI: local:///opt/my-job.jar
```

## 5. 实战：Word Count

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
DataStream<Tuple2<String, Integer>> counts = env
  .socketTextStream("localhost", 9999)
  .flatMap((line, out) -> {
    for (String word : line.split(" ")) {
      out.collect(Tuple2.of(word, 1));
    }
  })
  .returns(Types.TUPLE(Types.STRING, Types.INT))
  .keyBy(t -> t.f0)
  .sum(1);

counts.print();
env.execute("Word Count");
```

## 6. 窗口（Window）

```
时间窗口：
  TumblingEventTimeWindows.of(Time.minutes(5))     // 滚动
  SlidingEventTimeWindows.of(Time.minutes(5), Time.minutes(1))  // 滑动
  EventTimeSessionWindows.withGap(Time.minutes(10))  // 会话

计数窗口：
  GlobalWindows.create()  // 全局
```

```java
stream.keyBy(...)
  .window(TumblingEventTimeWindows.of(Time.minutes(5)))
  .aggregate(new MyCountAgg(), new MyWindowFunc());
```

## 7. 实战选型

| 场景 | 选 |
|------|-----|
| 实时低延迟 | Flink（强项） |
| ETL + 流批一体 | Flink + Iceberg |
| CEP（复杂事件） | Flink CEP |
| 状态复杂（聚合 / 关联） | Flink + RocksDB State |
| 高吞吐消息队列 | Kafka + Flink |
| 简单实时 | Spark Streaming |

## 8. 关键设计

- **Checkpoint**：分布式快照（障碍式）
- **Savepoint**：手动快照（升级 / 回滚）
- **Watermark**：处理乱序
- **State Backend**：Memory / RocksDB
- **Exactly-once**：两阶段提交

## 9. 实战建议

- 流批一体：Flink SQL 同时处理 Kafka + Hive
- 状态：RocksDB State（推荐生产）
- 监控：Flink Web UI + Prometheus + Grafana
- 部署：K8s Operator（Flink Kubernetes Operator）

## 10. Flink vs Spark Streaming

| | Flink | Spark Streaming |
|--|-------|------------------|
| 流模型 | True streaming | Micro-batch（默认） |
| 延迟 | 毫秒 | 秒 |
| 状态 | 内置丰富 | 需自实现 |
| Exactly-once | ✅（核心） | ✅（结构化流） |
| 事件时间 | 一等公民 | 需水印 |
| 流批一体 | ✅ | ✅ |

## 🔗 下一步
- [状态与 Checkpoint](/05-flink/state)
- [Exactly-once](/05-flink/exactly-once)
- [Flink CDC](/05-flink/cdc)

<!-- svg-injected:do-not-edit -->

## 图示：Flink 运行时架构（JobManager/TaskManager）

![Flink 运行时架构（JobManager/TaskManager）](/flink-architecture.svg)
