---
title: Shuffle 详解
---
# MapReduce Shuffle 详解

## 1. Shuffle 是什么

Shuffle = Map 输出 → Reduce 输入的中间过程（网络 + 磁盘 IO）。

MR 程序 80% 时间在 Shuffle → Shuffle 优化 = 性能优化。

## 2. Shuffle 流程

```
Map 阶段输出 (K, V)
   ↓
Partitioner (hash(K) % numReduceTasks) → 决定到哪个 Reduce
   ↓
环形缓冲（100MB）收集
   ↓
Spill 到磁盘（按 partition 排序）
   ↓
Merge Sort（合并溢写文件）
   ↓
Reduce 端 fetch（HTTP 拉取自己 partition 的数据）
   ↓
Sort + Group → reduce(K, [V]) → output
```

## 3. Shuffle 的关键参数

| 参数 | 默认 | 调优 |
|------|------|------|
| `mapreduce.task.io.sort.mb` | 100MB | 增大减少 spill |
| `mapreduce.map.sort.spill.percent` | 0.8 | 80% 触发 spill |
| `mapreduce.reduce.shuffle.parallelcopies` | 5 | 并行 fetch 数 |
| `mapreduce.shuffle.input.buffer.percent` | 0.7 | map 后 70% buffer |
| `mapreduce.shuffle.compress.mapoutput` | false | 大输出开压缩 |

## 4. Shuffle 数据倾斜

```
key 1 → Reduce 1 → 处理 100 万条
key 2 → Reduce 2 → 处理 10 万条
key 3 → Reduce 3 → 处理 1 万条

→ 整体耗时 = max(各 reduce 处理时间)
→ 整个 job 拖到最慢的 reduce 上
```

### 解决

1. **加盐打散**：
   ```java
   newKey = key + "_" + random(0..99)  // 写到 100 个 reduce
   // 客户端聚合
   sum = 0; for v in values: sum += v
   // 第二轮 MR 去掉随机后缀
   ```

2. **自定义 Partitioner**：
   ```java
   // 大 key 单独 partition
   if (key.equals("HOT")) return 0;  // 专属 reduce
   return (key.hashCode() & Integer.MAX_VALUE) % numReduceTasks;
   ```

3. **Combine 本地预聚合**：减少 Shuffle 数据量

4. **Bloom filter / HyperLogLog**：近似统计

## 5. Shuffle 性能优化

| 优化 | 描述 |
|------|------|
| Map 端 Combine | 减少 Shuffle 数据量 |
| 输出压缩 | map 输出 gzip 压缩 |
| 大缓冲 | io.sort.mb 增大（堆内存够） |
| Combiner | sum / count / max 适用 |
| 二级排序 | sort.spill.percent 调整 |
| 推测执行 | 慢 Task 备份 |

## 6. MR 与 Spark Shuffle 对比

| | MR Shuffle | Spark Shuffle |
|--|-------------|----------------|
| 介质 | 磁盘 | 内存（默认） |
| 排序 | Sort by key | HashPartitioner |
| 优化 | Combiner | mapSideCombine / 序列化 |
| 数据倾斜 | 加盐 / 自定义 Partition | 加盐 / AQE |
| 溢写 | 磁盘 | 内存 + 磁盘 |
| 调优 | io.sort.mb | spark.sql.shuffle.partitions |

## 7. 实战：观测 Shuffle

```bash
# MR 计数器
Counter shuffleBytes = context.getCounter("Shuffle", "Bytes")
// Shuffle 阶段读 / 写 字节数

# Spark Web UI
http://driver:4040
// Stages → Shuffle Read/Write
```

## 8. 实战优化案例

```
场景：日志分析 (1 TB)
  1000 万用户行为日志
  按 user_id 分组求和

问题：1000 个 key 中 1 个 key 占 50% 数据 → 倾斜
解决：
  1. 第一次 MR：map → 加盐 (key + random(0..99))
  2. 100 个 reduce 并行聚合
  3. 第二次 MR：map → 去盐 → 求总和
  耗时：60 min → 5 min
```

## 🔗 下一步
- [MapReduce 原理](/03-mapreduce/principle)
- [Combiner 与 Partitioner](/03-mapreduce/optimize)
