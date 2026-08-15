---
title: 面试案例
---
# 大数据面试案例

## 1. 数据倾斜案例

### 案例 1：Spark 数据倾斜

**问题**：电商订单表 join 用户表时，99% 用户集中在少数几个 key（null / 0）。

**排查**：
```
1. 看 stage 详情：某个 task 数据量巨大
2. 看 SQL：left join with user_id is null
3. 看数据：发现 user_id = 0 占 90%
```

**解决**：
```python
# 方案 1：过滤 + 单独处理
df_clean = df.filter("user_id IS NOT NULL AND user_id != 0")
df_null = df.filter("user_id IS NULL OR user_id == 0")
df_null = df_null.withColumn("user_id", lit(-1))  # 加盐

# 正常 join
df_result = df_clean.join(users, "user_id", "left")

# 单独处理 null
df_null_result = df_null.join(users, "user_id", "left")
df_final = df_result.union(df_null_result)

# 方案 2：AQE 自适应
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
```

**效果**：原 8 小时 → 优化后 1 小时。

### 案例 2：Hive 数据倾斜

**问题**：某 Reduce 任务跑了 6 小时仍未完成。

**解决**：
```sql
-- 1. 开启倾斜 Join 优化
SET hive.optimize.skewjoin = true;
SET hive.skewjoin.key = 100000;  -- 阈值

-- 2. 加盐
SELECT
  CASE WHEN user_id IS NULL THEN concat('null_', rand()) ELSE user_id END AS salted_key,
  ...
FROM orders;

-- 局部聚合
SELECT salted_key, count(*) cnt FROM orders GROUP BY salted_key;

-- 全局聚合
SELECT user_id, sum(cnt) FROM temp GROUP BY user_id;
```

## 2. Hive 数仓案例

### 案例 3：电商数仓分层

**ODS（贴源）**：
```sql
-- 原始订单
CREATE TABLE ods_order (
  order_id BIGINT,
  user_id BIGINT,
  item_id BIGINT,
  amount DECIMAL(10,2),
  ts TIMESTAMP,
  dt STRING
) PARTITIONED BY (dt STRING)
STORED AS PARQUET;
```

**DWD（清洗 + 规范化）**：
```sql
-- 清洗：过滤无效订单 + 关联商品
CREATE TABLE dwd_order AS
SELECT
  o.order_id,
  o.user_id,
  o.item_id,
  i.item_category,
  i.brand,
  o.amount,
  o.ts,
  o.dt
FROM ods_order o
JOIN dim_item i ON o.item_id = i.item_id
WHERE o.amount > 0;
```

**DWS（轻度聚合）**：
```sql
-- 按用户 + 天聚合
CREATE TABLE dws_user_daily AS
SELECT
  user_id,
  dt,
  SUM(amount) AS gmv,
  COUNT(DISTINCT order_id) AS order_cnt,
  COUNT(DISTINCT item_id) AS item_cnt
FROM dwd_order
GROUP BY user_id, dt;
```

**ADS（应用指标）**：
```sql
-- 实时大屏 GMV
CREATE TABLE ads_gmv_daily AS
SELECT
  dt,
  SUM(gmv) AS total_gmv,
  COUNT(DISTINCT user_id) AS user_cnt,
  SUM(gmv) / COUNT(DISTINCT user_id) AS arpu
FROM dws_user_daily
GROUP BY dt;
```

## 3. Flink 实时案例

### 案例 4：实时大屏（GMV / UV）

**架构**：
```
Kafka（订单） → Flink → Redis（实时指标） → 大屏
  　　　　　　　↓
  　　　　　 HBase（明细）
```

**实现**：
```java
public class GMVJob {
  public static void main(String[] args) throws Exception {
    StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
    env.enableCheckpointing(60000);  // 1 分钟 checkpoint
    env.setStateBackend(new RocksDBStateBackend("hdfs://..."));

    DataStream<Order> orders = env
      .addSource(new FlinkKafkaConsumer<>("orders", new OrderDeserializer(), kafkaProps))
      .filter(o -> o.amount > 0);

    // 按 user_id 聚合 + 写入 Redis
    orders
      .keyBy(Order::getUserId)
      .window(TumblingEventTimeWindows.of(Time.minutes(1)))
      .aggregate(new GMVAggregator(), new RedisWindowFunction())
      .addSink(new RedisSink<>("gmv_realtime"));

    env.execute("GMV Job");
  }
}
```

### 案例 5：Flink CDC MySQL → Doris

**架构**：
```
MySQL → Flink CDC → Doris（实时同步）
```

**实现**：
```sql
-- Flink CDC 启动
INSERT INTO mysql_users
SELECT * FROM mysql_cdc_users;

-- Doris 建表
CREATE TABLE users (
  id BIGINT,
  name STRING,
  age INT
) UNIQUE KEY (id)
DISTRIBUTED BY HASH (id) BUCKETS 32;
```

## 4. Kafka 案例

### 案例 6：Kafka Exactly-once

**问题**：Kafka 生产者重复发送消息。

**解决**：幂等生产者 + 事务。
```java
Properties props = new Properties();
props.put("enable.idempotence", "true");
props.put("transactional.id", "tx-id");

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.initTransactions();

try {
  producer.beginTransaction();
  for (String msg : messages) {
    producer.send(new ProducerRecord<>("topic", msg));
  }
  producer.commitTransaction();
} catch (Exception e) {
  producer.abortTransaction();
}
```

### 案例 7：Kafka 顺序消费

**问题**：多分区下消息乱序。

**解决**：
```java
// 1. 生产者：key 路由到同一分区
producer.send(new ProducerRecord<>("topic", userId, msg));

// 2. 消费者：单线程消费（每个分区独立线程）
props.put("max.poll.records", "1");  // 单条处理

// 3. 消费端：保证处理顺序
```

## 5. 数据治理案例

### 案例 8：元数据管理

**痛点**：
  - 表多（数仓数千张表）
  - 字段多（每张表几十字段）
  - 数据血缘不清

**解决**：
```
1. 元数据平台（Apache Atlas / DataHub）
   - 表 / 字段 / 血缘
   - 自动化采集（爬虫）
   - 检索 / 标签

2. 数据血缘
   - SQL 解析（生成 DAG）
   - 字段级血缘
   - 影响分析
```

### 案例 9：数据质量

**维度**：
  - 完整性（非空率）
  - 准确性（异常值检测）
  - 一致性（多源对账）
  - 时效性（延迟监控）
  - 唯一性（主键去重）

**实现**：
```sql
-- 完整性检查
SELECT
  COUNT(*) AS total,
  COUNT(user_id) AS user_id_not_null,
  COUNT(user_id) / COUNT(*) AS completeness
FROM dwd_order
WHERE dt = '2024-01-15';
-- 要求：completeness > 0.99

-- 唯一性检查
SELECT
  COUNT(*) AS total,
  COUNT(DISTINCT order_id) AS unique_cnt
FROM dwd_order
WHERE dt = '2024-01-15';
-- 要求：total = unique_cnt
```

## 6. 性能优化案例

### 案例 10：Spark 调优

**问题**：3 TB 数据聚合耗时 4 小时。

**排查**：
```
1. 看 UI：某个 stage shuffle 写入 1 TB
2. 看代码：groupBy 后 select 多列（数据膨胀）
3. 看配置：executor 内存 4 GB（小）
```

**优化**：
```python
# 1. 减少数据膨胀
# 原：df.groupBy("user_id").agg(sum("amount"), collect_list("items"))  # 危险
# 优化：先 filter 再 groupBy
df_filtered = df.filter("amount > 0")
df_agg = df_filtered.groupBy("user_id").agg(sum("amount").alias("gmv"))

# 2. 开启 AQE
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")

# 3. 调参
spark.conf.set("spark.sql.shuffle.partitions", "200")  # 适当并行度
spark.conf.set("spark.executor.memory", "16g")

# 4. 启用压缩
spark.conf.set("spark.sql.parquet.compression.codec", "snappy")

# 5. 启用广播 Join（小表）
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "10485760")  # 10 MB
```

**效果**：4 小时 → 1 小时。

## 7. 数据湖案例

### 案例 11：Iceberg 数仓

**架构**：
```
Kafka → Spark / Flink → Iceberg（湖仓） → Trino / Doris
```

**实现**：
```python
# 1. 创建 Iceberg 表
spark.sql("""
CREATE TABLE iceberg.db.orders (
  order_id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  ts TIMESTAMP
) USING iceberg
PARTITIONED BY (days(ts))
""")

# 2. 写入
df.write.format("iceberg").mode("append").save("iceberg.db.orders")

# 3. 时间旅行
spark.read.format("iceberg").option("snapshot-id", 12345).load("iceberg.db.orders")

# 4. Schema 演进
spark.sql("ALTER TABLE iceberg.db.orders ADD COLUMN new_field STRING")
```

### 案例 12：Hudi 实时同步

**架构**：
```
MySQL → Flink CDC → Hudi → Hive / Doris
```

**优势**：
  - 实时 upsert（按主键）
  - 增量查询
  - 时间旅行

## 8. 实时计算案例

### 案例 13：实时风控

**架构**：
```
请求 → Kafka → Flink（实时规则） → Redis（黑名单）
  　　　　　　　　　↓
  　　　　　　XGBoost（模型评分）
```

**实现**：
```java
// 实时特征 + 模型评分
DataStream<Request> requests = env
  .addSource(new KafkaSource<>("requests"));

// 实时特征
DataStream<Feature> features = requests
  .keyBy(Request::getUserId)
  .window(SlidingEventTimeWindows.of(Time.minutes(10), Time.minutes(1)))
  .aggregate(new FeatureAggregator());

// 评分
features
  .map(new ModelScoring())
  .addSink(new RedisSink<>("risk_score"));
```

## 9. 数据治理案例

### 案例 14：数据安全

**痛点**：
  - 敏感数据（身份证 / 手机 / 银行卡）
  - 权限控制（行 / 列）
  - 审计

**解决**：
```
1. 数据脱敏
   - 静态脱敏（生产）
   - 动态脱敏（查询）

2. 权限控制
   - Ranger / Sentry
   - 行级权限（按部门 / 角色）
   - 列级权限（按字段）

3. 审计
   - 访问日志
   - 异常访问告警
```

## 10. 综合案例

### 案例 15：实时数仓搭建

**架构**：
```
Kafka（MySQL CDC） → Flink → Iceberg（Hudi / Delta）
  　　　　　　　　　↓
  　　　　　Trino / Doris（查询）
  　　　　　　　　　↓
  　　　　　Grafana（可视化）
```

**分层**：
```
ODS（实时原始）
DWD（实时清洗 + 关联维度）
DWS（实时聚合）
ADS（实时指标）
```

**实现要点**：
```sql
-- DWD 实时
CREATE TABLE dwd_order_realtime (
  order_id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  ts TIMESTAMP,
  PRIMARY KEY (order_id) NOT ENFORCED
) WITH (
  'connector' = 'kafka',
  'topic' = 'dwd_order',
  'format' = 'debezium-json'
);

-- DWS 实时
INSERT INTO dws_user_realtime
SELECT
  user_id,
  TUMBLE_START(ts, INTERVAL '1' MINUTE) AS window_start,
  SUM(amount) AS gmv
FROM dwd_order_realtime
GROUP BY TUMBLE(ts, INTERVAL '1' MINUTE), user_id;
```

## 🔗 下一步
- [面试题](/14-interview-practice/questions)
- [推荐系统](/13-cases/recommendation)
- [用户画像](/13-cases/user-profile)