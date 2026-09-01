---
title: 命令速查
date: 2026-08-15  # date-auto-injected
---
# 📋 大数据命令速查

## 📦 HDFS

```bash
hdfs dfs -mkdir /data                       # 建目录
hdfs dfs -put local.txt /data/               # 上传
hdfs dfs -get /data/file ./local            # 下载
hdfs dfs -ls /data                          # 列
hdfs dfs -cat /data/file                    # 看
hdfs dfs -du -h /data                       # 看大小
hdfs dfs -rm -r /data/old                   # 删
hdfs dfs -mv /data/x /data/y                # 改名
hdfs dfs -chmod 755 /data                   # 改权限
hdfs dfs -du -h / | head                     # 看根占用
hdfs dfs -count /data/q=*.json              # 统计
hdfs dfs -getmerge /data/out /tmp/all.csv   # 合并下载
hdfs dfs -put -f - /data/x                   # 从 stdin 读

# 集群管理
hdfs dfsadmin -report                       # 集群报告
hdfs dfsadmin -safemode get                 # 安全模式
hdfs haadmin -getServiceState nn1            # NN HA 状态
hdfs fsck /data -files                      # 检查
hdfs balancer -threshold 10                # 均衡
hdfs dfs -setrep 3 /data/important          # 副本数
hdfs crypto -createZone -path /secure ...   # 加密区
```

## ⚙️ Spark

```bash
spark-submit   --master yarn   --deploy-mode cluster   --num-executors 100   --executor-memory 4g   --executor-cores 4   --driver-memory 4g   --conf spark.sql.shuffle.partitions=200   --class com.example.MyApp   my-app.jar   --input /data/in   --output /data/out

# spark-shell
spark.sql("SELECT count(*) FROM events").show()
df.groupBy("user").count().show()
df.write.mode("overwrite").parquet("/data/out")
```

## 🌊 Flink

```bash
# Standalone 集群
jobmanager.sh start cluster
taskmanager.sh start

# 提交作业
flink run -c com.example.MyJob   /opt/my-job.jar   --input /data/in   --output /data/out

# Savepoint
flink savepoint <jobId> /savepoints/sp1
flink cancel -s /savepoints/sp1 <jobId>

# SQL Client
flink-sql-client.sh
> CREATE TABLE events (...)
> SELECT count(*) FROM events;
```

## 🏛️ Hive

```sql
-- 数据库
CREATE DATABASE IF NOT EXISTS dw;
USE dw;

-- 内部表（管理表）
CREATE TABLE orders (
  id BIGINT,
  user_id BIGINT,
  amount DECIMAL(10,2),
  created_at TIMESTAMP
) PARTITIONED BY (dt STRING)
STORED AS PARQUET;

-- 加载
LOAD DATA INPATH '/data/orders/' INTO TABLE orders PARTITION (dt='2024-01-15');

-- 查询
SELECT user_id, count(*) FROM orders
WHERE dt BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY user_id;

-- 导出
INSERT OVERWRITE DIRECTORY '/data/export'
SELECT * FROM orders WHERE dt = '2024-01-15';
```

## 📨 Kafka

```bash
# Topic
kafka-topics --create --topic events   --bootstrap-server localhost:9092   --partitions 6 --replication-factor 3
kafka-topics --list --bootstrap-server localhost:9092
kafka-topics --describe --topic events

# 生产
kafka-console-producer --bootstrap-server localhost:9092   --topic events --property parse.key=true   --property key.separator=:

# 消费
kafka-console-consumer --bootstrap-server localhost:9092   --topic events --from-beginning   --property print.key=true --property key.separator=:

# Consumer Group
kafka-consumer-groups --bootstrap-server localhost:9092 --list
kafka-consumer-groups --bootstrap-server localhost:9092   --group my-app --reset-offsets --to-earliest --topic events
```

## 🔄 Flink CDC

```bash
flink run -c org.apache.flink.cdc.connectors.mysql.debezium.DebeziumSource   /opt/flink-cdc.jar   --hostname localhost --port 3306   --username root --password xxx   --database-name-list mydb   --table-name-list orders   --sink-path hdfs:///data/ods/

# Debezium 单独
debezium-connector mysql ... 
```

## 🌊 数据湖（Iceberg / Delta / Hudi）

```sql
-- Iceberg
CREATE TABLE events (
  id BIGINT, ts TIMESTAMP, data STRING
) USING iceberg
PARTITIONED BY (days(ts));

INSERT INTO events VALUES (1, NOW(), '...');
SELECT * FROM events WHERE ts > '2024-01-01';

-- Delta Lake
CREATE TABLE events USING delta AS SELECT * FROM parquet.`/data/in/`;
SELECT * FROM events VERSION AS OF 10;

-- Hudi
INSERT INTO events SELECT ..., 'ts' FROM ...;
```

## 🔄 Airflow / dbt

```bash
# Airflow
airflow dags list
airflow dags trigger my_dag
airflow tasks test my_dag my_task 2024-01-15

# dbt
dbt run --select my_model
dbt test
dbt docs generate
```

## 📊 ClickHouse

```sql
CREATE TABLE events (
  ts DateTime,
  user_id UInt64,
  event String
) ENGINE = MergeTree()
ORDER BY (ts, user_id);

INSERT INTO events VALUES (NOW(), 123, 'click');
SELECT count(), uniq(user_id) FROM events WHERE ts > NOW() - INTERVAL 1 DAY;
```

## 🛠️ 性能排查

```bash
# Spark
spark.history.fs.logDirectory=hdfs:///logs/spark
spark.ui.port=4040
# 看 Web UI: http://driver:4040

# YARN
yarn application -list
yarn logs -applicationId <id>

# HDFS 热点
hdfs dfsadmin -report
hdfs dfs -ls /tmp/ | head -20

# Kafka 消费 lag
kafka-consumer-groups --bootstrap-server kafka:9092   --describe --group my-consumer
```

## 🔗 下一步
- [HDFS 架构](/02-hdfs/architecture)
- [Spark Core / RDD](/04-spark/rdd)
- [Flink 架构](/05-flink/architecture)
- [Kafka Streams](/07-kafka-streaming/streams)


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
