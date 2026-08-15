---
title: 安装部署
---

# 📥 安装部署

> 5 分钟搭建一个本地 Kafka 集群。本章涵盖 JDK 安装、Kafka 下载、单机/集群模式、KRaft 配置。

## 🎯 环境要求

```
✅ JDK 11+（Kafka 3.x 要求）
✅ 至少 4GB 可用内存（开发环境）
✅ 至少 10GB 可用磁盘
✅ Linux / macOS / Windows（WSL2 推荐）
✅ Zookeeper 3.6+（仅 Kafka 2.x 以前版本需要）
```

## 📦 步骤 1：下载安装包

```bash
# 下载 Kafka 3.7（最新稳定版）
wget https://archive.apache.org/dist/kafka/3.7.0/kafka_2.13-3.7.0.tgz

# 解压
tar -xzf kafka_2.2.13-3.7.0.tgz
cd kafka_2.13-3.7.0

# 目录结构
bin/      # 启动脚本（kafka-server-start.sh 等）
config/   # 配置文件（server.properties 等）
libs/     # 依赖 jar 包
logs/     # 日志目录
data/     # 数据目录（默认 /tmp/kafka-logs）
```

## 🚀 步骤 2：单机模式（开发环境）

### 启动 KRaft 单节点（Kafka 3.x）

```bash
# 1. 生成集群 ID
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
echo $KAFKA_CLUSTER_ID
# 输出类似：MkU3OEVBNTcwNTJENDM2Qk

# 2. 格式化存储目录（首次启动前）
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties

# 3. 启动 Kafka
bin/kafka-server-start.sh -daemon config/kraft/server.properties

# 4. 验证启动成功
ps -ef | grep kafka
tail -f logs/server.log
```

### 创建第一个 Topic

```bash
# 创建一个 3 分区、1 副本的 topic
bin/kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic my-first-topic \
    --partitions 3 \
    --replication-factor 1

# 查看 topic 列表
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# 查看 topic 详情
bin/kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic my-first-topic
```

### 生产/消费测试

```bash
# 启动生产者（命令行交互）
bin/kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic my-first-topic

# 在另一个终端启动消费者
bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic my-first-topic \
    --from-beginning
```

## 🐳 步骤 3：Docker 方式（推荐）

```bash
# docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    
  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on: [zookeeper]
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
EOF

docker-compose up -d
```

## 🏗️ 步骤 4：集群模式（生产环境）

### 多节点规划

```
3 节点集群：
  node1: kafka-broker-1 (Controller + Broker)
  node2: kafka-broker-2 (Controller + Broker)
  node3: kafka-broker-3 (Controller + Broker)

KRaft 模式：
  - 3 节点各启动 Controller + Broker
  - 自动选主，无需 ZooKeeper
```

### 配置 server.properties（每节点）

```properties
# ==== 集群标识 ====
# node1 配置：broker.id=1
# node2 配置：broker.id=2
# node3 配置：broker.id=3
broker.id=1

# ==== 监听地址 ====
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://node1:9092

# ==== 日志目录 ====
log.dirs=/data/kafka-logs

# ==== 分区数（默认 1） ====
num.partitions=3

# ==== 默认副本数 ====
default.replication.factor=2
min.insync.replicas=2

# ==== KRaft 配置（Kafka 3.x 替代 ZooKeeper） ====
process.roles=broker,controller
controller.quorum.voters=1@node1:9093,2@node2:9093,3@node3:9093
controller.listener.names=CONTROLLER
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
inter.broker.listener.name=PLAINTEXT
```

### 启动集群

```bash
# 在每台节点执行
KAFKA_CLUSTER_ID="$(bin/kafka-storage.sh random-uuid)"
bin/kafka-storage.sh format -t $KAFKA_CLUSTER_ID -c config/kraft/server.properties
bin/kafka-server-start.sh -daemon config/kraft/server.properties

# 验证集群状态
bin/kafka-broker-api-versions.sh --bootstrap-server node1:9092
```

## 🔧 关键配置详解

```properties
# 消息保留策略（默认 7 天）
log.retention.hours=168
log.retention.bytes=1073741824

# 单分区最大消息数（避免单分区过大）
log.segment.bytes=1073741824      # 1GB（分段）
log.segment.ms=604800000          # 7 天（按时间分段）

# 网络线程池
num.network.threads=3
num.io.threads=8

# 日志刷盘策略
log.flush.interval.messages=10000
log.flush.interval.ms=1000

# 自动创建 Topic（生产环境建议关闭）
auto.create.topics.enable=false
```

## 🐛 常见问题

### 问题 1：端口被占用

```
报错：Address already in use: bind
解决：换端口或杀掉占用进程
netstat -tlnp | grep 9092
kill -9 <pid>
```

### 问题 2：磁盘空间满

```
报错：No space left on device
解决：
  1. 清理过期日志：log.retention.hours 调小
  2. 增加磁盘
  3. 配置多 log.dirs（不同磁盘）
```

### 问题 3：内存不足

```
报错：OutOfMemoryError
解决：
  1. 调大 JVM 堆：KAFKA_HEAP_OPTS="-Xmx4G"
  2. 增加服务器内存
```

## 🎯 总结

**安装部署核心要点**：
- ✅ 单机：KRaft 模式 + 1 个节点
- ✅ 集群：3 节点 KRaft + 2 副本
- ✅ Docker：docker-compose 快速启动
- ✅ 生产：3 节点起步 + 多副本 + 监控
- ⚠️ Kafka 3.x 用 KRaft 替代 ZooKeeper

**下一步：** [🧩 核心概念](/01-basics/concepts) — Broker / Topic / Partition 详解
