---
title: 集群部署
date: 2026-08-15  # date-auto-injected
---

# 🏭 集群部署

> **生产环境 Kafka 集群**的部署是高可用、高性能的基础。本章详解集群规划、部署和验证。

## 🎯 集群规划

### 集群规模评估

```
问题：需要多大集群？

输入：
  - 业务 QPS（读写消息数）
  - 单消息大小
  - 副本数
  - 保留天数
  - SLA（可用性、延迟）

输出：
  - Broker 数量
  - Broker 配置（CPU / 内存 / 磁盘）
  - Partition 数量
```

### 容量评估公式

```
磁盘容量 = 消息数 × 单消息大小 × 副本数 × 保留天数

示例：
  - 每天 10 亿条消息
  - 单消息 1KB
  - 3 副本
  - 保留 7 天

磁盘容量 = 10亿 × 1KB × 3 × 7 = 210TB
```

### Broker 配置推荐

```
小型集群（< 10GB/s）：
  - CPU：8 核
  - 内存：32GB
  - 磁盘：4TB NVMe SSD
  - 网络：万兆网卡
  - Broker 数量：3-5

中大型集群（10-100GB/s）：
  - CPU：16-32 核
  - 内存：64-128GB
  - 磁盘：8-16TB NVMe SSD
  - 网络：万兆或更高
  - Broker 数量：5-10

超大型集群（> 100GB/s）：
  - CPU：32+ 核
  - 内存：128GB+
  - 磁盘：16TB+ NVMe SSD
  - 网络：25G / 100G
  - Broker 数量：10+
```

## 🛠️ 部署架构

### 单机房 3 节点（最小）

```
┌──────────────────────────────────┐
│         单机房                     │
│                                  │
│  Broker1  Broker2  Broker3       │
│    ↓        ↓        ↓          │
│  交换机（万兆）                   │
│    ↓        ↓        ↓          │
│  Producer / Consumer              │
└──────────────────────────────────┘

优点：简单
缺点：机房故障 = 服务不可用
```

### 双机房 6 节点（推荐）

```
┌────────────────┬────────────────┐
│   机房 A        │   机房 B        │
│                │                │
│  B1   B2       │   B3   B4       │
│                │                │
│   Active       │   Standby      │
│                │                │
└────────────────┴────────────────┘
       ↑            ↑
       └───── 双活 ─────┘

优点：机房级容灾
缺点：跨机房复制延迟
```

### 多机房 9 节点（大型）

```
┌─────────┬─────────┬─────────┐
│ 机房 A  │ 机房 B  │ 机房 C  │
│         │         │         │
│ B1 B2   │ B3 B4   │ B5 B6   │
│         │         │         │
│ Active  │ Active  │ Backup  │
└─────────┴─────────┴─────────┘
```

## 🔧 服务器规划

### 服务器规格推荐

```yaml
# 小型集群 Broker
hardware:
  cpu: 8 核 (Intel Xeon 或 AMD EPYC)
  memory: 32GB DDR4
  disk: 4TB NVMe SSD（推荐 Intel Optane 或 Samsung PM9A3）
  network: 10Gbps

# 中大型集群 Broker
hardware:
  cpu: 16 核
  memory: 64GB DDR4
  disk: 8TB NVMe SSD
  network: 25Gbps
```

### 操作系统配置

```bash
# 文件描述符限制
cat >> /etc/security/limits.conf << EOF
* soft nofile 65535
* hard nofile 65535
* soft nproc 32768
* hard nproc 32768
EOF

# 内核参数调优
cat >> /etc/sysctl.conf << EOF
# 网络优化
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216

# 虚拟内存
vm.max_map_count=262144
vm.dirty_ratio=10
vm.dirty_background_ratio=5

# 关闭 swap
vm.swappiness=1
EOF

sysctl -p
```

### 磁盘规划

```bash
# 1. 多磁盘分散（推荐）
# 配置多个 log.dirs，每个目录对应一块磁盘
log.dirs=/data1/kafka-logs,/data2/kafka-logs,/data3/kafka-logs

# 2. RAID 0（性能优先）或 RAID 10（安全）
# 推荐：RAID 10 + BBU

# 3. 监控磁盘空间（保留 20% 余量）
```

## 🚀 部署步骤

### 步骤 1：环境准备

```bash
# 1. 安装 JDK 17+
yum install -y java-17-openjdk-devel

# 2. 创建 Kafka 用户
useradd -r -s /sbin/nologin kafka

# 3. 下载 Kafka
cd /opt
wget https://archive.apache.org/dist/kafka/3.7.0/kafka_2.13-3.7.0.tgz
tar -xzf kafka_2.13-3.7.0.tgz
ln -s kafka_2.13-3.7.0 kafka
chown -R kafka:kafka /opt/kafka
```

### 步骤 2：配置 Kafka

```properties
# /opt/kafka/config/kraft/server.properties

# ==== 节点标识 ====
node.id=1
process.roles=broker,controller

# ==== 网络配置 ====
listeners=PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
advertised.listeners=PLAINTEXT://kafka-1:9092
controller.listener.names=CONTROLLER
inter.broker.listener.name=PLAINTEXT

# ==== KRaft 集群 ====
controller.quorum.voters=1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093

# ==== 日志配置 ====
log.dirs=/data1/kafka-logs,/data2/kafka-logs,/data3/kafka-logs
num.partitions=6
default.replication.factor=3
min.insync.replicas=2

# ==== 性能调优 ====
num.network.threads=4
num.io.threads=8
log.flush.interval.messages=10000
log.flush.interval.ms=1000

# ==== 保留策略 ====
log.retention.hours=168
log.retention.bytes=1073741824
log.segment.bytes=1073741824
log.segment.ms=604800000

# ==== 安全（可选）====
# listeners=SASL_SSL://0.0.0.0:9092
# security.protocol=SASL_SSL
# sasl.mechanism=SCRAM-SHA-512
```

### 步骤 3：格式化存储

```bash
# 每个节点生成集群 ID（保持一致）
KAFKA_CLUSTER_ID=$(/opt/kafka/bin/kafka-storage.sh random-uuid)
echo $KAFKA_CLUSTER_ID  # 如：MkU3OEVBNTcwNTJENDM2Qk

# 在每个节点上格式化存储
/opt/kafka/bin/kafka-storage.sh format \
    -t $KAFKA_CLUSTER_ID \
    -c /opt/kafka/config/kraft/server.properties
```

### 步骤 4：启动服务

```bash
# 创建 systemd service
cat > /etc/systemd/system/kafka.service << EOF
[Unit]
Description=Apache Kafka Server
After=network.target

[Service]
Type=simple
User=kafka
Group=kafka
ExecStart=/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/kraft/server.properties
ExecStop=/opt/kafka/bin/kafka-server-stop.sh
Restart=always
RestartSec=10
LimitNOFILE=65535

Environment=JAVA_HOME=/usr/lib/jvm/java-17-openjdk
Environment=KAFKA_HEAP_OPTS="-Xms4G -Xmx4G"
Environment=KAFKA_JVM_PERFORMANCE_OPTS="-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20 -XX:+DisableExplicitGC"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable kafka
systemctl start kafka

# 查看状态
systemctl status kafka
```

### 步骤 5：验证集群

```bash
# 1. 查看集群状态
bin/kafka-metadata-quorum.sh --bootstrap-server kafka-1:9092 describe --status

# 2. 查看 Broker 列表
bin/kafka-broker-api-versions.sh --bootstrap-server kafka-1:9092

# 3. 创建测试 Topic
bin/kafka-topics.sh --create \
    --bootstrap-server kafka-1:9092 \
    --topic test \
    --partitions 3 \
    --replication-factor 3

# 4. 测试生产消费
echo "hello" | bin/kafka-console-producer.sh --bootstrap-server kafka-1:9092 --topic test
bin/kafka-console-consumer.sh --bootstrap-server kafka-1:9092 --topic test --from-beginning
```

## 🐳 Docker 部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  kafka-1:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka-1
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: 'broker,controller'
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: 'CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT'
      KAFKA_ADVERTISED_LISTENERS: 'PLAINTEXT://kafka-1:9092'
      KAFKA_CONTROLLER_LISTENER_NAMES: 'CONTROLLER'
      KAFKA_LISTENERS: 'PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093'
      KAFKA_INTER_BROKER_LISTENER_NAME: 'PLAINTEXT'
      KAFKA_CONTROLLER_QUORUM_VOTERS: '1@kafka-1:9093,2@kafka-2:9093,3@kafka-3:9093'
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
      CLUSTER_ID: 'MkU3OEVBNTcwNTJENDM2Qk'
    volumes:
      - /var/lib/kafka/kafka-1:/var/lib/kafka/data

  kafka-2:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka-2
    ports:
      - "9093:9092"
    environment:
      # 类似 kafka-1，但 KAFKA_NODE_ID: 2
      ...

  kafka-3:
    image: confluentinc/cp-kafka:7.5.0
    hostname: kafka-3
    ports:
      - "9094:9092"
    environment:
      # 类似 kafka-1，但 KAFKA_NODE_ID: 3
      ...
```

## 🔒 安全配置

### SASL 认证

```properties
# server.properties
listeners=SASL_SSL://0.0.0.0:9092
advertised.listeners=SASL_SSL://kafka:9092
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-512
sasl.enabled.mechanisms=SCRAM-SHA-512

# SSL 配置
ssl.keystore.location=/var/ssl/kafka.server.keystore.jks
ssl.keystore.password=keystore-password
ssl.key.password=key-password
ssl.truststore.location=/var/ssl/kafka.server.truststore.jks
ssl.truststore.password=truststore-password
```

### 创建用户

```bash
# 创建管理员
bin/kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=admin-secret]' \
    --entity-type users --entity-name admin

# 创建应用用户
bin/kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --add-config 'SCRAM-SHA-512=[iterations=8192,password=app-secret]' \
    --entity-type users --entity-name app-user
```

### ACL 配置

```bash
# 给 app-user 授权
bin/kafka-acls.sh --bootstrap-server localhost:9092 \
    --add --allow-principal User:app-user \
    --allow-host '*' \
    --operation READ,WRITE \
    --topic 'orders' \
    --group 'order-processor'
```

## 🛠️ 高可用部署

### 多可用区部署（AWS）

```
Region: us-east-1
  AZ-a:
    Broker 1
    Broker 2
  AZ-b:
    Broker 3
  AZ-c:
    Broker 4
  Broker 5

副本分布：
  Partition 0: Leader=B1 (AZ-a), Replica=[B1, B3, B4] (跨 3 个 AZ)
  Partition 1: Leader=B2 (AZ-a), Replica=[B2, B4, B5]
  ...
```

### 同城双活（两地三中心）

```
同城：
  机房 A（Active）：Broker 1, 2, 3
  机房 B（Standby）：Broker 4, 5, 6

异地：
  机房 C（备份）：Broker 7, 8, 9
```

### MirrorMaker 2.0 跨机房

```properties
# mm2-cross-region.properties
clusters=primary,secondary
primary.bootstrap.servers=primary-kafka:9092
secondary.bootstrap.servers=secondary-kafka:9092

primary->secondary.enabled=true
primary->secondary.topics=orders,payments,users

# 配置心跳
heartbeat.interval.ms=1000
```

## 📊 部署验证清单

```markdown
✅ 集群状态正常（3 个 Broker 加入集群）
✅ KRaft 模式正常运行
✅ Controller 选举成功
✅ Topic 创建成功（3 副本）
✅ Producer 发送成功
✅ Consumer 消费成功
✅ 监控指标正常（无告警）
✅ ACL 配置正确
✅ SSL 加密（可选）
✅ 备份策略就绪
✅ 灾难恢复预案
```

## ⚠️ 常见问题

### 问题 1：启动失败

```
原因：
  1. 配置错误（broker.id 冲突）
  2. 端口被占用
  3. 磁盘权限
解决：
  1. 检查 logs/server.log
  2. 验证网络
  3. 检查防火墙
```

### 问题 2：副本同步失败

```
原因：
  1. Broker 宕机
  2. 网络问题
  3. 磁盘满
解决：
  1. 检查 Broker 状态
  2. 验证 ISR
  3. 监控 under-replicated partitions
```

### 问题 3：性能不佳

```
原因：
  1. 磁盘 IO 不足（HDD 而非 SSD）
  2. 网络带宽不够
  3. JVM 配置不合理
解决：
  1. 升级到 NVMe SSD
  2. 使用万兆网卡
  3. 调优 JVM 参数
```

## 🎯 总结

**集群部署核心要点**：
- ✅ 至少 3 Broker + 3 副本
- ✅ KRaft 模式（Kafka 3.x）
- ✅ NVMe SSD + 万兆网卡
- ✅ JVM 调优（G1GC）
- ✅ 多 AZ 部署（高可用）
- ✅ 监控 + 告警
- ⚠️ 容量评估很重要
- ⚠️ 备份和灾难恢复预案

**下一步：** [📐 集群规划](/09-ops/capacity) — 容量评估


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
