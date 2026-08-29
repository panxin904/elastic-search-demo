---
title: MapReduce 原理
date: 2026-08-15  # date-auto-injected
---
# MapReduce 原理

## 1. 核心思想

```
分而治之 + 移动计算不移动数据：
  Map（映射）→ Shuffle（混洗）→ Reduce（归约）
```

## 2. WordCount 例子

```
输入：hello world hello
目标：统计每个词出现次数

Map 阶段：
  (hello, 1) (world, 1) (hello, 1)

Shuffle 阶段（隐式）：
  hello → [1, 1]
  world → [1]

Reduce 阶段：
  hello → sum([1, 1]) = 2
  world → sum([1]) = 1
```

## 3. MapReduce 1.x 数据流

```
Input → Split (切片)
   ↓
Map (K1, V1) → intermediate (K2, V2)
   ↓
Combine (本地聚合, 可选)
   ↓
Shuffle & Sort (按 Key 分组)
   ↓
Reduce (K2, list<V2>) → output
   ↓
Output → write
```

## 4. MapReduce 2.x 改进

| 改进 | 描述 |
|------|------|
| 无 sort 阶段 | Reduce 直接接 Map |
| Combine 优化 | Map 端本地聚合，减少 shuffle |
| 推测执行 | 慢任务备份，缩短总时间 |
| YARN | 通用资源调度 |

## 5. Shuffle 详解

```
Map 输出  →  Partitioner (按 key hash)  → 环形缓冲 (100MB)
   ↓
   Sort  →  Combine (本地归并)
   ↓
   Spill to disk  →  合并溢写文件
   ↓
   Reduce 通过 HTTP 拉取属于自己 partition 的数据
   ↓
   Sort + Group → reduce(k, list<V>) → output
```

**Shuffle 是 MR 最慢的阶段**，80% 时间在 Shuffle。

## 6. 数据倾斜

```
现象：某些 key 数据量极大 → 单一 Reduce 处理慢 → 整体拖慢
解决：
  1. Combine 本地聚合（map 端预聚合）
  2. 加盐（key + 随机前缀）→ 打散到多个 reduce → 再合并
  3. 自定义 Partitioner
  4. 过滤异常 key
```

## 7. Combiner

```
Map → combine (本地聚合) → reduce

例：词频统计
  Map 输出 (hello, 1) (hello, 1) → send all to reduce
  Map + combine → (hello, 2) → send to reduce

效果：减少 Shuffle 数据量
适用：满足结合律（sum / count / max）
不适用：avg / median
```

## 8. Partitioner

```java
public class WordCountPartitioner extends Partitioner<Text, IntWritable> {
  @Override
  public int getPartition(Text key, IntWritable value, int numPartitions) {
    return (key.toString().hashCode() & Integer.MAX_VALUE) % numPartitions;
  }
}
```

控制 K → Reduce 的映射，**数据倾斜调优核心**。

## 9. 性能调优

| 调优 | 场景 | 影响 |
|------|------|------|
| mapreduce.job.reduces | Reduce 数 | 并行度 |
| mapreduce.map.output.compress | 输出大 | Shuffle 减少 IO |
| mapreduce.task.io.sort.mb | 排序内存 | 减少 spill |
| mapreduce.job.jvm.numtasks | Task 数 | 并行度 |
| mapreduce.map.sort.spill.percent | Spill 阈值 | 内存 vs 磁盘 |
| Combiner | 聚合场景 | 减少 Shuffle |

## 10. 实战：写一个 WordCount

```java
public class WordCount {
  public static class TokenizerMapper extends Mapper<LongWritable, Text, Text, IntWritable> {
    private final static IntWritable one = new IntWritable(1);
    private Text word = new Text();
    public void map(LongWritable key, Text value, Context ctx) {
      StringTokenizer itr = new StringTokenizer(value.toString());
      while (itr.hasMoreTokens()) {
        word.set(itr.nextToken());
        ctx.write(word, one);
      }
    }
  }
  public static class IntSumReducer extends Reducer<Text, IntWritable, Text, IntWritable> {
    public void reduce(Text key, Iterable<IntWritable> values, Context ctx) {
      int sum = 0;
      for (IntWritable val : values) sum += val.get();
      ctx.write(key, new IntWritable(sum));
    }
  }
  public static void main(String[] args) throws Exception {
    Configuration conf = new Configuration();
    Job job = Job.getInstance(conf, "word count");
    job.setMapperClass(TokenizerMapper.class);
    job.setReducerClass(IntSumReducer.class);
    job.setOutputKeyClass(Text.class);
    job.setOutputValueClass(IntWritable.class);
    FileInputFormat.addInputPath(job, new Path(args[0]));
    FileOutputFormat.setOutputPath(job, new Path(args[1]));
    System.exit(job.waitForCompletion(true) ? 0 : 1);
  }
}
```

## 11. MR vs Spark

| | MR | Spark |
|--|----|-------|
| 计算模型 | 磁盘迭代 | 内存 DAG |
| 速度 | 慢（10x） | 快 |
| 编程模型 | 简单 | 复杂（RDD / DataFrame） |
| 适用 | 一次性超大数据 | 迭代 ML / SQL |

Spark 在绝大多数场景取代了 MR。

## 🔗 下一步
- [Shuffle 详解](/03-mapreduce/shuffle)
- [Combiner 与 Partitioner](/03-mapreduce/optimize)
- [Spark Core / RDD](/04-spark/rdd)
