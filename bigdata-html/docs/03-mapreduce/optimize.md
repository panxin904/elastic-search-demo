---
title: Combiner / Partitioner
date: 2026-08-15  # date-auto-injected
---
# Combiner 与 Partitioner 优化

## 1. Combiner 原理

```
Map 输出 → Combiner (本地聚合) → Reduce (全局聚合)

例：词频统计
  Map: hello→1, hello→1, hello→1, world→1
  Combine (本节点): hello→3, world→1
  Reduce (跨节点): hello→3, world→1

效果：
  - 减少 Shuffle 数据量
  - 减少磁盘 IO
  - 减少网络传输
```

## 2. Combiner 适用场景

满足**结合律**的算子：

| 算子 | 适用 Combiner |
|------|---------------|
| sum / count | ✅ |
| max / min | ✅ |
| avg | ❌（需要分子分母分别加和） |
| median | ❌ |
| distinct | ❌ |

## 3. Partitioner 详解

```java
public class CustomPartitioner extends Partitioner<Text, IntWritable> {
  @Override
  public int getPartition(Text key, IntWritable value, int numReduceTasks) {
    // 自定义分片规则
    return Math.abs(key.toString().hashCode() % numReduceTasks);
  }
}
```

**作用**：决定 K 到哪个 Reduce。

## 4. Partitioner 实战

```java
// 场景：大客户 key 单独 partition
public class HotKeyPartitioner extends Partitioner<Text, IntWritable> {
  private static final Set<String> HOT_KEYS = Set.of("vip_alice", "vip_bob");
  
  @Override
  public int getPartition(Text key, IntWritable value, int numReduceTasks) {
    if (HOT_KEYS.contains(key.toString())) {
      return 0;  // 热点 key → reduce 0 专属
    }
    return (key.toString().hashCode() & Integer.MAX_VALUE) % numReduceTasks;
  }
}
```

## 5. Combiner + Partitioner 组合

```java
job.setPartitionerClass(CustomPartitioner.class);
job.setCombinerClass(SumReducer.class);
job.setReducerClass(SumReducer.class);
```

## 6. Combiner 调优

```xml
<property>
  <name>mapreduce.combine.class</name>
  <value>org.apache.hadoop.examples.SumReducer</value>
</property>
<property>
  <name>mapreduce.map.output.compress</name>
  <value>true</value>
</property>
```

## 7. 实战案例

### 大文件分组统计

```java
// 100 GB 用户日志
// 计算每个 user_id 的 PV
// 默认按 user_id hash 分到 100 个 reduce

// 优化：加自定义 Partitioner
//  - 热用户单独 partition（保证进度）
//  - 加 Combiner 本地预聚合
//  - 启用 map 输出压缩
```

效果：job 时间从 30 min 减到 5 min。

## 8. 经典调优

| 调优 | 场景 |
|------|------|
| Combiner | 任何聚合操作（sum/count/max） |
| Partitioner | 数据倾斜 / 业务分区 |
| 输出压缩 | map 输出大 / 网络慢 |
| 推测执行 | 慢任务 |

## 🔗 下一步
- [MapReduce 原理](/03-mapreduce/principle)
- [Shuffle 详解](/03-mapreduce/shuffle)
