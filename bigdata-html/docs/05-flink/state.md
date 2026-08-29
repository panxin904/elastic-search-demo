---
title: Flink 状态与 Checkpoint
date: 2026-08-15  # date-auto-injected
---
# Flink 状态与 Checkpoint

## 1. 状态类型

### Keyed State（按 Key 划分）

```
ValueState<T>          单值
ListState<T>           列表
MapState<UK, UV>       映射
ReducingState<T>       归约（聚合）
AggregatingState<IN, OUT>  聚合
FoldingState<T>        折叠
```

### Operator State（算子级）

```
ListCheckpointed<T>    列表（均匀划分）
UnionCheckpointed<T>  列表（联合划分）
```

## 2. 状态后端（State Backend）

```java
env.setStateBackend(new HashMapStateBackend());  // 内存（默认）
env.setStateBackend(new EmbeddedRocksDBStateBackend());  // 磁盘（推荐生产）
env.getCheckpointConfig().setCheckpointStorage("hdfs:///ck/");
```

## 3. Checkpoint 机制

```
Stream  →  Barrier 注入（周期）
   ↓
   算子对齐（等待所有输入 barrier）
   ↓
   状态快照（异步）
   ↓
   写入持久化（HDFS / S3）
   ↓
   Barrier 传递到下游
   ↓
   下游对齐 + 快照
```

## 4. 实战 Checkpoint 配置

```java
env.enableCheckpointing(60_000L);  // 60s 一次
env.getCheckpointConfig()
  .setMinPauseBetweenCheckpoints(30_000L)  // 最小间隔 30s
  .setCheckpointTimeout(60_000L)  // 单次超时 60s
  .setMaxConcurrentCheckpoints(1)  // 同时只 1 个 checkpoint
  .setTolerableCheckpointFailureNumber(3);  // 容忍 3 次失败

env.getCheckpointConfig()
  .setExternalizedCheckpointRetention(ExternalizedCheckpointRetention.RETAIN_ON_CANCELLATION);
```

## 5. Savepoint（手动快照）

```bash
# 触发 savepoint
flink savepoint <jobId> hdfs:///savepoints/sp1

# 从 savepoint 启动
flink run -s hdfs:///savepoints/sp1 ...

# 删除
flink savepoint -d hdfs:///savepoints/sp1
```

**vs Checkpoint**：
- Checkpoint：自动 / 周期 / 失败即失效
- Savepoint：手动 / 升级 / 回滚

## 6. Exactly-once 原理

```
Flink 内部通过 2PC（两阶段提交）：
  1. 注入 Barrier → 所有 source 对齐
  2. 算子快照状态 → 写 State Backend
  3. 写 Sink（如 Kafka）→ 预提交
  4. 所有算子都完成 → 通知 JobManager
  5. JobManager 通知所有 Sink 提交
  → 任何失败 → 回滚
```

## 7. 状态查询实战

```java
// 通过 Queryable State
env.enableCheckpointing(60_000L);
env.setStateBackend(new HashMapStateBackend());

DataStream<Tuple2<String, Long>> counts = ...;
counts.keyBy(t -> t.f0)
  .map(new RichMapFunction<Tuple2<String, Long>, Tuple2<String, Long>>() {
    private ValueState<Long> state;
    @Override
    public void open(Configuration parameters) {
      state = getRuntimeContext().getState(
        new ValueStateDescriptor<>("count", Types.LONG)
      );
    }
    @Override
    public Tuple2<String, Long> map(Tuple2<String, Long> value) {
      Long curr = state.value() == null ? 0L : state.value();
      curr += value.f1;
      state.update(curr);
      return Tuple2.of(value.f0, curr);
    }
  })
  .print();
```

## 8. 实战调优

```java
// 1. RocksDB 调优
EmbeddedRocksDBStateBackend backend = new EmbeddedRocksDBStateBackend();
backend.setRocksDBOptions(new RocksDBOptions()
  .setCompactionStyle(CompactionStyle.UNIVERSAL)
  .setIncreaseParallelism(4)
  .setMaxBackgroundJobs(4));
env.setStateBackend(backend);

// 2. 状态 TTL
StateTtlConfig ttl = StateTtlConfig
  .newBuilder(Time.days(7))
  .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
  .cleanupFullSnapshot()
  .build();
ValueStateDescriptor<String> desc = new ValueStateDescriptor<>("k", Types.STRING);
desc.enableTimeToLive(ttl);
```

## 9. 实战：状态后端选型

| 场景 | 选 |
|------|-----|
| 小状态 / 低延迟 | MemoryStateBackend |
| 大状态 / 持久化 | RocksDBStateBackend |
| 极端大状态 | 自定义 HDFS / S3 后端 |
| 状态可重建 | 无状态（避免 checkpoint） |

## 10. 实战 checklist

- [ ] Checkpoint 间隔（10-60 秒）
- [ ] State Backend（RocksDB 推荐）
- [ ] State TTL（清理过期数据）
- [ ] Savepoint（升级 / 回滚前）
- [ ] 监控（checkpoint 大小 / 时长）

## 🔗 下一步
- [Flink 架构](/05-flink/architecture)
- [Exactly-once](/05-flink/exactly-once)
- [Flink CDC](/05-flink/cdc)
