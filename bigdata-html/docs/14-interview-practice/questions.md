---
title: 面试题
date: 2026-08-15  # date-auto-injected
---
# 大数据面试题

## 1. HDFS

### Q1：HDFS 写流程？

```
1. Client 调 create（请求 NameNode）
2. NameNode 检查 + 返回块位置（DataNode 列表）
3. Client 写第一个块（pipeline）：
   - Block 1 → DN1 → DN2 → DN3
   - DN1 收到 → 转发 DN2 → DN2 转发 DN3
   - DN3 ACK → DN2 ACK → DN1 ACK → Client
4. Client 写第二个块（同 pipeline）
5. 所有块写完 → Client 调 complete
6. NameNode 确认文件创建
```

### Q2：HDFS 读流程？

```
1. Client 调 open（请求 NameNode）
2. NameNode 返回块位置（按距离排序）
3. Client 读第一个块（从最近的 DataNode）
4. 读第二个块...
5. 拼装 + 返回
```

### Q3：NameNode HA？

```
NameNode HA（避免单点故障）：
  - 主 NameNode（Active）
  - 备 NameNode（Standby）
  - 共享存储（QJM / JournalNode）
  - ZKFC（Zookeeper Failover Controller）

故障切换：
  - ZKFC 检测 Active 故障
  - 切换 Standby → Active
  - < 30 秒恢复
```

### Q4：HDFS 小文件问题？

```
问题：
  - 每个文件 = 1 个块 + 元数据
  - 1 亿小文件 = 1 亿块（NameNode 压力大）

解决：
  - 合并小文件（HAR / SequenceFile）
  - 开启 Federation（多 NameNode）
  - 压缩（gzip / snappy）
```

## 2. MapReduce

### Q5：MapReduce Shuffle？

```
Map 端：
  - 环形缓冲区（100 MB）
  - 阈值 80% → spill 到磁盘
  - 多个 spill 文件 → 合并（分区 + 排序）

Reduce 端：
  - Copy（从各 Map 拉取对应分区）
  - Merge（合并 + 排序）
  - Reduce（聚合）
```

### Q6：MapReduce 数据倾斜？

```
表现：某个 Reduce 任务特别慢

解决：
  - 自定义分区（避免热点 key）
  - 二次聚合（局部 + 全局）
  - 采样（识别热点）
  - 增加 Reduce 数
  - 数据预处理（拆分热点 key）
```

### Q7：Combiner 作用？

```
Combiner = 本地 Reduce（Map 端聚合）
  - 减少 Shuffle 数据量
  - 适用场景：求和 / 计数（满足结合律）
  - 不适用：求平均数（损失精度）
```

## 3. Spark

### Q8：Spark vs MapReduce？

```
Spark 优势：
  - 内存计算（迭代快）
  - DAG（有向无环图）
  - RDD / DataFrame API
  - 多种语言（Scala / Python / Java）
  - Structured Streaming

MapReduce 优势：
  - 稳定（生态成熟）
  - 适合超大数据（TB+）
```

### Q9：Spark Shuffle？

```
Spark Shuffle = 类似 MapReduce
  - Map 端：写磁盘（按分区）
  - Reduce 端：拉取 + 合并

优化：
  - Shuffle Read 合并
  - 自定义分区器
  - 广播小表（避免 Shuffle）
  - 调参：spark.sql.shuffle.partitions
```

### Q10：Spark 数据倾斜？

```
解决：
  - 自定义分区（打散热点）
  - 加盐（局部聚合 + 全局聚合）
  - 过滤异常数据
  - 增加并行度
  - 采样 + 拆分热点 key
```

### Q11：RDD / DataFrame / Dataset 区别？

```
RDD：分布式弹性数据集（强类型 + 弱类型）
DataFrame：带 Schema 的 RDD（优化好）
Dataset：DataFrame + 强类型（编译期类型安全）

性能：
  - DataFrame / Dataset > RDD
  - Tungsten 优化（内存 + CPU）
```

### Q12：Spark Streaming vs Structured Streaming？

```
Spark Streaming（DStream）：
  - 基于 RDD
  - 微批处理（秒级）

Structured Streaming：
  - 基于 DataFrame
  - 端到端 exactly-once
  - 事件时间 + 水印
  - 推荐用 Structured Streaming
```

## 4. Flink

### Q13：Flink vs Spark Streaming？

```
Flink：
  - 流式优先（事件驱动）
  - 毫秒级延迟
  - 状态管理（强）
  - Exactly-once

Spark Streaming：
  - 微批（秒级延迟）
  - 生态成熟
  - 批流统一（Structured Streaming）
```

### Q14：Flink 状态后端？

```
MemoryStateBackend：内存（开发用）
FsStateBackend：文件系统（生产用）
RocksDBStateBackend：RocksDB（大数据量）

生产推荐：RocksDBStateBackend
  - 增量 checkpoint
  - 大状态支持
  - 性能好
```

### Q15：Flink Exactly-once？

```
实现：
  - Checkpoint（分布式快照）
  - 两阶段提交（2PC）
  - Source / Sink 幂等

Sink：
  - Kafka（事务）
  - MySQL（2PC）
  - HDFS（幂等写入）
```

### Q16：Flink 水印（Watermark）？

```
水印 = 事件时间进度标记
  - 用于处理乱序事件
  - 触发窗口计算

公式：
  watermark = max_event_time - allowed_lateness
```

### Q17：Flink 反压？

```
反压 = 下游处理慢，上游被阻塞

表现：背压指标 > 0.5

解决：
  - 优化下游（并行度 / 资源）
  - 状态优化（异步 / RocksDB）
  - 数据倾斜（自定义分区）
  - 限流
```

## 5. Hive

### Q18：Hive 内部表 vs 外部表？

```
内部表（Managed Table）：
  - Hive 拥有数据
  - DROP TABLE → 删除数据

外部表（External Table）：
  - Hive 仅管理元数据
  - DROP TABLE → 不删除数据（生产推荐）
```

### Q19：Hive 分区 / 分桶？

```
分区（Partition）：
  - 按列分区（dt / region）
  - 减少扫描
  - 分区裁剪

分桶（Bucket）：
  - 按哈希分桶（user_id % 32）
  - JOIN 优化（桶连接）
  - 采样
```

### Q20：Hive UDF？

```
UDF（User Defined Function）：
  - 一进一出（upper / lower）
  - Java 实现

UDAF（聚合）：
  - 多进一出（sum / avg）

UDTF（表生成）：
  - 一进多出（explode）
```

### Q21：Hive 数据倾斜？

```
表现：某个 Reduce 任务特别慢

解决：
  - Map Join（小表广播）
  - 自定义分区
  - 二次聚合
  - 采样 + 拆分热点
  - Skew Join（hive.optimize.skewjoin）
```

## 6. Kafka

### Q22：Kafka 为什么快？

```
1. 顺序写（磁盘顺序写 = 内存写）
2. 零拷贝（sendfile）
3. 批量发送（积累到一定大小再发）
4. 页缓存（Page Cache）
5. 分区并行
```

### Q23：Kafka Exactly-once？

```
实现（Kafka 0.11+）：
  - 幂等生产者（PID + 序列号）
  - 事务（原子写 + 读）
  - 消费端：read_committed

API：
  - producer.initTransactions()
  - producer.beginTransaction()
  - producer.send(...)
  - producer.commitTransaction()
```

### Q24：Kafka 消费者组？

```
消费者组（Consumer Group）：
  - 一个分区只能被组内一个消费者消费
  - 多消费者并行消费
  - 自动 rebalance

提交 offset：
  - 自动（enable.auto.commit）
  - 手动（commitSync / commitAsync）
```

### Q25：Kafka 分区策略？

```
1. 默认（轮询）
2. Hash（key 哈希）
3. 自定义（RoundRobin / 自定义）
4. 黏性（Sticky）
```

## 7. 数据建模

### Q26：维度建模？

```
事实表（Fact Table）：
  - 业务度量（GMV / 订单数）
  - 外键（维度键）

维度表（Dimension Table）：
  - 描述性属性（用户 / 商品 / 时间）

模型：
  - 星型模型（事实 + 多个维度）
  - 雪花模型（维度进一步规范化）
```

### Q27：SCD（Slowly Changing Dimension）？

```
SCD1：覆盖（新值替旧值）
SCD2：新增（保留历史，加版本字段）
SCD3：新增列（保留当前 + 上一次）

最常用：SCD2
  - dt_start / dt_end
  - is_current
```

### Q28：分层架构？

```
ODS（原始层）：贴源
DWD（明细层）：清洗 + 规范化
DWS（汇总层）：轻度聚合
ADS（应用层）：指标 / 报表
DIM（维度层）：公共维度
```

## 8. 数据湖

### Q29：数据湖 vs 数据仓库？

```
数据湖：
  - 原始数据（结构化 / 半结构化 / 非结构化）
  - Schema-on-read
  - 灵活

数据仓库：
  - 处理后数据
  - Schema-on-write
  - 高性能查询

湖仓（Lakehouse）：
  - 两者结合（Iceberg / Delta / Hudi）
  - 数据湖 + 数据仓库优势
```

### Q30：Iceberg / Delta / Hudi 区别？

```
Iceberg：
  - 通用性强
  - 隐藏分区
  - 多引擎（Spark / Flink / Trino）

Delta Lake：
  - Databricks 主推
  - 事务 + 时间旅行
  - 深度集成 Spark

Hudi：
  - 插入 / 更新 / 删除（强）
  - 适合 CDC
  - 多引擎
```

## 9. 实时计算

### Q31：Lambda vs Kappa 架构？

```
Lambda：
  - 批 + 流（双链路）
  - 复杂
  - 历史准确

Kappa：
  - 纯流
  - Kafka + Flink
  - 简单
  - 实时
```

### Q32：流批一体？

```
技术：
  - Flink（流批统一）
  - Spark（Structured Streaming）
  - Iceberg（统一存储）

优势：
  - 减少重复代码
  - 一致性
  - 简化运维
```

## 10. 综合

### Q33：Hadoop 生态？

```
存储：
  - HDFS（Hadoop 分布式文件系统）

计算：
  - MapReduce（批）
  - Spark（内存批 / 流）
  - Flink（流）

资源调度：
  - YARN（资源管理）
  - Mesos

协调：
  - Zookeeper（一致性）

数据仓库：
  - Hive（SQL 引擎）

消息队列：
  - Kafka

NoSQL：
  - HBase（列式）
```

### Q34：数仓 vs 数据库？

```
数据库（OLTP）：
  - 事务（ACID）
  - 行存储
  - 实时写入
  - 点查

数仓（OLAP）：
  - 大数据分析
  - 列存储
  - 批量写入
  - 复杂查询
```

### Q35：数据倾斜解决方法？

```
通用方案：
  - 加盐（局部聚合 + 全局聚合）
  - 自定义分区
  - 采样 + 拆分热点
  - 增加并行度
  - 过滤异常数据
  - Map Join（小表）

Spark 特有：
  - 启用 AQE（自适应查询执行）
  - 倾斜 JOIN 优化

Flink 特有：
  - 自定义分区器
  - KeyBy 前预处理
```

## 🔗 下一步
- [面试案例](/14-interview-practice/cases)
- [推荐系统](/13-cases/recommendation)
- [用户画像](/13-cases/user-profile)


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
