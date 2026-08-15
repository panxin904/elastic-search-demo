---
title: 常用命令总览
---

# 📋 常用命令总览

> Kafka 提供丰富的命令行工具（CLI），位于 `bin/` 目录下。本章介绍最常用的命令工具。

## 🎯 bin/ 目录工具概览

```bash
# Kafka 3.x bin/ 目录
ls bin/

# 常用工具
kafka-topics.sh              # Topic 管理
kafka-console-producer.sh    # 命令行生产者
kafka-console-consumer.sh    # 命令行消费者
kafka-consumer-groups.sh     # 消费者组管理
kafka-reassign-partitions.sh # 分区重分配
kafka-configs.sh             # 配置管理
kafka-broker-api-versions.sh # Broker API 版本
kafka-cluster.sh             # 集群管理（KRaft）
kafka-storage.sh             # 存储初始化
kafka-acls.sh                # ACL 权限管理
kafka-delegation-tokens.sh   # 委派令牌
```

## 🔧 通用命令格式

```bash
kafka-工具名.sh \
    --bootstrap-server <host:port>  # Kafka 服务器地址
    --topic <name>                  # Topic 名
    --partitions <n>                # 分区数
    --replication-factor <n>        # 副本数
    --config <key>=<value>          # 配置
```

```bash
# 通用参数
--bootstrap-server localhost:9092    # Kafka 地址
--bootstrap-servers host1:9092,host2:9092  # 多个地址
--command-config client.properties   # 客户端配置文件
--dry-run                            # 仅测试，不执行
```

## 🎯 Topic 管理命令

### 创建 Topic

```bash
# 创建 3 分区、2 副本的 topic
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 3 \
    --replication-factor 2

# 创建带配置的 topic
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic logs \
    --partitions 6 \
    --replication-factor 3 \
    --config retention.ms=604800000 \
    --config cleanup.policy=delete
```

### 查看 Topic

```bash
# 列出所有 topic
kafka-topics.sh --list --bootstrap-server localhost:9092

# 查看所有 topic（包括内部）
kafka-topics.sh --list --bootstrap-server localhost:9092 --exclude-internal

# 查看 topic 详情
kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders

# 输出：
# Topic: orders   PartitionCount: 3   ReplicationFactor: 2
#   Partition: 0   Leader: 1   Replicas: 1,2   Isr: 1,2
#   Partition: 1   Leader: 2   Replicas: 2,3   Isr: 2,3
#   Partition: 2   Leader: 3   Replicas: 3,1   Isr: 3,1
```

### 修改 Topic

```bash
# 增加分区（只能增加）
kafka-topics.sh --alter \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 6

# 修改 Topic 配置
kafka-topics.sh --alter \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --config retention.ms=1209600000 \
    --config cleanup.policy=compact

# 删除 Topic
kafka-topics.sh --delete \
    --bootstrap-server localhost:9092 \
    --topic orders
```

## ✉️ 生产消费命令

### 生产消息

```bash
# 启动命令行生产者（交互式）
kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders

# 输入消息后回车发送
# > order-001 alice 99.9
# > order-002 bob 88.8

# 带 Key 的生产
kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --property "parse.key=true" \
    --property "key.separator=:"

# 输入格式：key:value
# > user123:order-001 alice 99.9
```

### 消费消息

```bash
# 从头消费
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning

# 指定消费者组
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --group order-processor \
    --from-beginning

# 显示 Key 和时间戳
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning \
    --property "print.key=true" \
    --property "print.timestamp=true"

# 限制消费数量
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --max-messages 10 \
    --from-beginning
```

## 👥 消费者组命令

```bash
# 列出所有消费者组
kafka-consumer-groups.sh --list --bootstrap-server localhost:9092

# 查看消费者组详情（lag、offset）
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor

# 重置 offset
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-earliest \
    --execute

# 删除消费者组
kafka-consumer-groups.sh --delete \
    --bootstrap-server localhost:9092 \
    --group order-processor
```

## 🔧 配置管理命令

```bash
# 查看 Broker 配置
kafka-configs.sh --bootstrap-server localhost:9092 \
    --describe --entity-type brokers --entity-name 1

# 动态修改配置
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type brokers --entity-name 1 \
    --add-config "log.retention.ms=86400000"

# 查看 Topic 配置
kafka-configs.sh --bootstrap-server localhost:9092 \
    --describe --entity-type topics --entity-name orders

# 撤销配置
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type brokers --entity-name 1 \
    --delete-config "log.retention.ms"
```

## 🔍 集群管理命令

```bash
# 查看 Broker API 版本
kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# 查看集群元数据
kafka-metadata-quorum.sh --bootstrap-server localhost:9092 describe --status

# 查看分区分配
kafka-describe-consumer-groups.sh --bootstrap-server localhost:9092 --group order-processor

# ACL 权限管理
kafka-acls.sh --bootstrap-server localhost:9092 --list

# 添加 ACL
kafka-acls.sh --bootstrap-server localhost:9092 \
    --add --allow-principal User:alice --operation read --topic orders
```

## 🛠️ Kafka Playground（浏览器版）

<ClientOnly>
  <KafkaPlayground />
</ClientOnly>

试试用 Playground 执行 Kafka CLI 命令：

```bash
# 创建 Topic
CREATE TOPIC orders 3 2

# 查看 Topic 列表
LIST TOPICS

# 生产消息
PRODUCE orders "order-001 alice 99.9"
PRODUCE orders "order-002 bob 88.8"

# 消费消息
CONSUMER orders GROUP order-processor 5

# 查看消费者组
GROUP LIST
```

## ⚙️ 客户端配置文件

```bash
# 复杂客户端配置（用户名密码 + SSL）
cat > client.properties << EOF
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
    username="alice" \
    password="alice-secret";
ssl.truststore.location=/var/ssl/kafka.client.truststore.jks
ssl.truststore.password=changeit
EOF

# 使用配置文件
kafka-topics.sh --bootstrap-server localhost:9092 \
    --command-config client.properties \
    --list
```

## ⚠️ 常见问题

### 问题 1：找不到类

```
报错：Could not find or load main class
解决：使用完整路径
/path/to/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### 问题 2：超时连接

```
报错：Connection to node -1 could not be established
解决：
  1. 检查 Kafka 服务是否启动
  2. 检查 --bootstrap-server 地址是否正确
  3. 检查防火墙
```

### 问题 3：权限不足

```
报错：Topic authorization failed
解决：
  1. 检查 ACL 配置
  2. kafka-acls.sh --list 查看权限
  3. 添加对应权限：kafka-acls.sh --add
```

## 🎯 总结

**Kafka CLI 核心要点**：
- ✅ kafka-topics.sh - Topic 管理
- ✅ kafka-console-producer.sh - 生产消息
- ✅ kafka-console-consumer.sh - 消费消息
- ✅ kafka-consumer-groups.sh - 消费者组
- ✅ kafka-configs.sh - 配置管理
- ✅ kafka-reassign-partitions.sh - 分区重分配
- ⚠️ 复杂场景使用 --command-config 配置文件

**下一步：** [📂 Topic 管理](/03-cli/topic) — 详细命令 + 实战
