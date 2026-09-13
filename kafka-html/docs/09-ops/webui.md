---
title: Kafka WebUI
date: 2026-09-13  # date-auto-injected
---

# 🖥️ Kafka WebUI

> WebUI 是 Kafka 日常运维、问题排查、Schema 演进的高频工具。本章对主流方案横向对比，并给出使用手册、查询语法与实战场景。

## 🌐 主流 WebUI 横向对比

| 工具 | 维护方 | 协议 | 优势 | 局限 | 推荐场景 |
|---|---|---|---|---|---|
| **AKHQ** (formerly Kafka HQ) | tchiotludo | HTTP API | Topic/Consumer/Schema 全功能，ACL 友好，Docker 一键 | 高级 SQL 弱 | **首选**，通用运维 |
| **Confluent Control Center** | Confluent | JMX + REST | 企业级，告警/监控/流治理一站式 | 商业，集群规模敏感 | 大厂商业版 |
| **Kafdrop** | HomeAdvisor | HTTP | 轻量、UI 漂亮、启动快 | 功能较薄 | 开发测试 / 小集群 |
| **Kafbat UI** | kafbat | HTTP | Kafdrop 现代 fork，**多集群 + Connect + Schema + ACL** 全功能，GitHub 8k+ ⭐ 活跃维护 | 文档略薄，但 UI/性能优于 Kafdrop | **生产运维首选**，多集群统一视图 |
| **Redpanda Console** | Redpanda | HTTP | 现代 UI + Schema Registry 集成 | Kafka 兼容性偶有问题 | 已用 Redpanda |
| **Conduktor** | Conduktor | 桌面 | 多集群、流量录制 | 客户端软件 | 多集群开发 |
| **UI for Apache Kafka** | Provectus | HTTP | 简单直观 | 功能最小 | Demo / 教学 |
| **Lenses** | Landoop | HTTP | KSQL/Connect 全栈 + GitOps | 商业 | 复杂流处理 |

**结论**：自建/开源场景 **AKHQ / Kafbat UI 二选一**（AKHQ 老牌稳，Kafbat UI 更现代且多集群视图更友好）。开发测试可选 Kafdrop。商业场景选 Control Center 或 Lenses。

## 🚀 快速部署（Kafbat UI）

> **Kafbat UI 是 Kafdrop 的官方 fork，由社区接手维护**，功能远超原 Kafdrop，是当前 2026 年最值得选的开源 Kafka WebUI。

### Docker 一键启动

```bash
# 单集群模式（最快）
docker run -d     --name kafbat-ui     -p 8080:8080     -e KAFKATOOL_CONFIGURATION='{
        "kafkaClusters": [
          {
            "name": "local",
            "bootstrapServers": "localhost:9092",
            "properties": {
              "security.protocol": "PLAINTEXT"
            }
          }
        ]
      }'     kafbat/kafka-ui:latest

# 访问：http://localhost:8080
```

### Docker Compose（多集群 + Schema Registry + Connect）

```yaml
version: '3'
services:
  kafbat-ui:
    image: kafbat/kafka-ui:latest
    container_name: kafbat-ui
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      KAFKATOOL_CONFIGURATION: |
        kafka:
          clusters:
            - name: dev
              bootstrapServers: dev-kafka:9092
              properties:
                sasl.mechanism: SCRAM-SHA-512
                security.protocol: SASL_PLAINTEXT
                sasl.jaas.config: org.apache.kafka.common.security.scram.ScramLoginModule required username="dev-user" password="dev-pass"
            - name: prod
              bootstrapServers: prod-kafka-1:9092,prod-kafka-2:9092
              properties:
                security.protocol: SASL_SSL
                ssl.truststore.location: /certs/kafka.truststore.jks
                ssl.truststore.password: changeit
              schemaRegistry: https://schema-registry.prod:8081
              kafkaConnect:
                - name: connect-1
                  address: https://kafka-connect.prod:8083
                  username: connect-user
                  password: connect-pass
    volumes:
      - ./truststore.jks:/certs/kafka.truststore.jks:ro
      - ./kafbat-config.yml:/app/config.yml:ro
```

### 配置文件版（推荐生产用）

```yaml
# kafbat-config.yml
kafka:
  clusters:
    - name: dev
      bootstrapServers: dev-kafka:9092
      properties:
        security.protocol: SASL_PLAINTEXT
        sasl.mechanism: SCRAM-SHA-512
        sasl.jaas.config: org.apache.kafka.common.security.scram.ScramLoginModule required username="dev" password="dev-pwd"
    - name: prod
      bootstrapServers: prod-kafka:9092
      properties:
        security.protocol: SASL_SSL
        ssl.truststore.location: /app/certs/truststore.jks
        ssl.truststore.password: changeit
        ssl.key.password: changeit
        ssl.key.location: /app/certs/keystore.p12
      schemaRegistry: https://schema-registry.prod:8081
      kafkaConnect:
        - name: connect-prod
          address: https://kafka-connect.prod:8083
auth:
  type: LOGIN_FORM  # 可选 LOGIN_FORM / OAUTH2 / DISABLED
  simple:
    users:
      - username: admin
        password: $2a$10$...  # bcrypt 哈希
        roles:
          - admin
roles:
  - name: admin
    clusters:
      - dev
      - prod
    permissions:
      - topic:*:*
      - consumer-group:*:*
      - acls:full
```

```bash
# 启动
docker-compose up -d kafbat-ui
# 访问 http://localhost:8080，admin / 你的密码
```

### Kubernetes（Helm）

```bash
helm repo add kafbat https://kafbat.github.io/helm-charts
helm install kafbat kafbat/kafka-ui     --set clusters[0].name=prod     --set clusters[0].bootstrapServers=prod-kafka:9092
```

### Kafbat UI vs AKHQ：选哪个？

| 维度 | Kafbat UI | AKHQ |
|---|---|---|
| UI 设计 | ✅ 更现代，React 18 + Material-UI | 一般，Vue 风格传统 |
| 多集群切换 | ✅ 顶栏一键切，无缝 | 顶部下拉，每次重载 |
| Connect/Schema 支持 | ✅ 内置，操作流畅 | ✅ 也有，UI 略弱 |
| 消息浏览 | ✅ JSON/Avro/Protobuf 自动 schema 解析 | ✅ 需手动选 schema |
| ACL 管理 | ✅ 细粒度（按 topic/cluster/role） | ✅ 基础 CRUD |
| 社区活跃度 | ✅ GitHub 8k+ ⭐，周更 | ⚠️ 节奏放缓，月更 |
| 资源占用 | ⚠️ Spring Boot 启动慢（~30s），内存 ~512MB | ✅ 更轻（~256MB） |
| 部署复杂度 | ⚠️ 配置文件略复杂 | ✅ env 注入更简单 |

**选型建议**：
- **多集群统一运维** → 选 Kafbat UI
- **资源敏感/容器小** → 选 AKHQ
- **生产 Schema Registry 密集** → 选 Kafbat UI（Avro 反序列化体验更好）

## 🚀 快速部署（AKHQ）

### Docker Compose（推荐）

```yaml
version: '3'
services:
  akhq:
    image: tchiotludo/akhq:latest
    container_name: akhq
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      AKHQ_CONFIGURATION: |
        akhq:
          connections:
            local:
              properties:
                bootstrap.servers: "kafka-1:9092,kafka-2:9092,kafka-3:9092"
              schema-registry:
                url: "http://schema-registry:8081"
              connect:
                - name: connect-1
                  url: "http://kafka-connect:8083"
          security:
            basic-auth:
              - username: admin
                password: ${AKHQ_ADMIN_PASSWORD}
                roles:
                  - admin
    volumes:
      - ./akhq-config.yml:/app/configuration/akhq.yml:ro
```

```bash
# 启动
docker-compose up -d akhq

# 访问
open http://localhost:8080
# 默认 admin/ademin（首次登录强制改密）
```

### 配置多集群 + Schema Registry + Connect

```yaml
# akhq-config.yml
akhq:
  connections:
    dev:
      properties:
        bootstrap.servers: "dev-kafka:9092"
    prod:
      properties:
        bootstrap.servers: "prod-kafka-1:9092,prod-kafka-2:9092"
        security.protocol: SASL_SSL
        sasl.mechanism: SCRAM-SHA-512
        sasl.jaas.config: |
          org.apache.kafka.common.security.scram.ScramLoginModule required
            username="${KAFKA_USER}" password="${KAFKA_PASS}";
      schema-registry:
        url: "https://schema-registry.prod:8081"
        username: "${SR_USER}"
        password: "${SR_PASS}"
      connect:
        - name: connect-1
          url: "https://kafka-connect.prod:8083"
```

### Kubernetes（Helm）

```bash
helm repo add akhq https://akhq.io
helm install akhq akhq/akhq \
  --set akhq.connections.prod.properties.bootstrap.servers="prod-kafka:9092"
```

## 🧭 界面功能详解（以 AKHQ 为例）

### 1️⃣ Topics 视图

| 操作 | 路径 | 用途 |
|---|---|---|
| 列表 | `/ui/{cluster}/topics` | 按分区数/副本数排序、看 lag 增量 |
| 详情 | `/ui/{cluster}/topic/{name}` | 偏移量水位图（线上/线下） |
| 浏览消息 | 点 topic → Messages tab | 实时拉取最新 N 条 |
| 消费 | 点 Consume 按钮 | 模拟消费者组，输出 JSON |
| 生产 | 点 Produce 按钮 | 表单填 key/value + headers |
| 配置 | 点 Settings → Edit | 改 retention / cleanup.policy |
| ACL | 点 Permissions | 用户/组的读/写/管理权限 |

**消息浏览技巧**：
- `Partition` 选择器：按分区查看（避免重排序）
- `Offset` 范围：`earliest` / `latest` / 自定义
- `Timestamp` 过滤：按时间窗定位
- `Search in value`：JSON path 搜索（akhq 0.21+ 支持 `$.user.id` 语法）

### 2️⃣ Consumer Groups 视图

```bash
# 排查 lag 三大指标
1. CURRENT OFFSET   ← 消费组当前位置
2. LOG END OFFSET   ← 最新消息位置
3. LAG               ← 2 - 1（堆积量）
```

操作：
- **Reset Offset**：把消费组重置到 earliest/latest/指定时间点（⚠️ 会重放）
- **Topic Offset**：单分区重置
- **Lag History 图**：看趋势，确认是否持续增长

### 3️⃣ Schema Registry

- **Subjects 列表**：所有 schema subject
- **Versions**：一个 subject 的多个历史版本（向后兼容演进）
- **Compatibility**：BACKWARD / FORWARD / FULL / NONE
- **Diff**：对比 v3 vs v4 字段差异

### 4️⃣ Kafka Connect

- **Connectors**：所有 connector 实例
- **Tasks**：每个 connector 的并行 task
- **Config**：动态更新 connector 配置（无需重启）
- **Status**：RUNNING / FAILED / PAUSED

### 5️⃣ ACL 管理

- 主体维度：User、Group、Topic、Cluster
- 权限：READ / WRITE / DESCRIBE / DELETE / ALTER / ALL
- 操作：grant / revoke / list

## 🔎 查询语法

### AKHQ 内置 JSON Path 搜索

```
# 在 topic 浏览消息时，搜索框支持 JSON Path
$                       → 整条消息
$.user.id               → 顶层 user.id
$.order.items[*].sku    → 数组通配
$.payload.event_type    → 嵌套对象
$..timestamp            → 递归搜索
```

### KSQL/ksqlDB 实时查询

> 需要额外部署 ksqlDB（`cpdibauer/ksqldb-server`），不属 WebUI 自带，但常配合使用。

```sql
-- 1. 创建流（声明 schema）
CREATE STREAM orders (
    order_id   VARCHAR,
    user_id    BIGINT,
    amount     DECIMAL(10,2),
    event_time TIMESTAMP
) WITH (
    KAFKA_TOPIC = 'orders',
    VALUE_FORMAT = 'json',
    TIMESTAMP = 'event_time'
);

-- 2. 窗口聚合：每分钟下单金额
CREATE TABLE order_per_minute AS
    SELECT user_id,
           SUM(amount) AS total_amount
    FROM orders
    WINDOW TUMBLING (SIZE 1 MINUTE)
    GROUP BY user_id
    EMIT CHANGES;

-- 3. 实时 JOIN：订单流 + 用户表
CREATE STREAM enriched_orders AS
    SELECT o.order_id,
           o.amount,
           u.user_name,
           u.city
    FROM orders o
    LEFT JOIN users u
      ON o.user_id = u.user_id
    EMIT CHANGES;

-- 4. 流-表 JOIN 后落地到新 topic
CREATE SINK TABLE high_value_users
    WITH (KAFKA_TOPIC = 'high-value-users') AS
    SELECT user_id, SUM(amount) AS total
    FROM orders
    GROUP BY user_id
    HAVING SUM(amount) > 10000
    EMIT CHANGES;
```

### Kafka REST Proxy（curl 直接查询）

```bash
# 1. 列出所有 topic
curl -s http://kafka-rest:8082/topics | jq

# 2. 生产消息
curl -X POST -H "Content-Type: application/vnd.kafka.json.v2+json" \
  --data '{
    "records": [
      {"key":"u001","value":{"order_id":"o100","amount":99.5}}
    ]
  }' \
  http://kafka-rest:8082/topics/orders

# 3. 消费（创建 instance + subscription）
curl -X POST -H "Content-Type: application/vnd.kafka.json.v2+json" \
  --data '{"name":"debug-consumer","format":"json","auto.offset.reset":"earliest"}' \
  http://kafka-rest:8082/consumers/debug-group

curl -X POST -H "Content-Type: application/vnd.kafka.json.v2+json" \
  --data '{"topics":["orders"]}' \
  http://kafka-rest:8082/consumers/debug-group/instances/debug-consumer/subscription

curl -s -X GET -H "Accept: application/vnd.kafka.json.v2+json" \
  http://kafka-rest:8082/consumers/debug-group/instances/debug-consumer/records | jq

# 4. 查看 consumer group 提交位点
curl -s http://kafka-rest:8082/consumers/debug-group/instances/debug-consumer/offsets
```

### Schema Registry REST 查询

```bash
# 列出所有 subject
curl -s http://schema-registry:8081/subjects | jq

# 看 v1 schema
curl -s http://schema-registry:8081/subjects/orders-value/versions/1 | jq

# 全局兼容性检查
curl -s http://schema-registry:8081/config | jq
```

## 🎯 实战场景实例

### 场景 1：消费组 lag 突然飙升排查

**现象**：告警 `consumer_lag > 100000` 持续 5 分钟。

**AKHQ 排查步骤**：

```
1. Consumer Groups → 找到目标 group
2. 看 Lag History 图：
   - 锯齿状增长 → 消费慢（GC/DB/下游阻塞）
   - 阶跃式跳变 → 重平衡（rebalance）
   - 持续陡增 → 消费彻底卡死
3. 点 group 详情 → Members tab：
   - 看分配的分区是否均衡
   - 看 client.id/host 区分消费实例
4. 点 topic → Settings → 看 retention.ms 是否过小
```

**常见根因**：
- 下游 DB 慢查询 → 加索引/异步化
- 消费逻辑抛异常 → 看日志（不 commit 进度）
- 分区键设计倾斜 → 改 key
- consumer 实例数变化 → 触发 rebalance

### 场景 2：消息时间回溯（业务对账）

**需求**：重新处理 2 小时前的订单数据。

```bash
# 1. 在 AKHQ → Consumer Groups → 找到对账 group → Reset Offset
# 2. 选择 Reset to specific time → 填入 2 小时前时间戳
# 3. 选 Reset All Partitions
# 4. 触发对账任务
```

**CLI 等价命令**（更稳妥）：
```bash
kafka-consumer-groups.sh \
    --bootstrap-server localhost:9092 \
    --group audit-group \
    --topic orders \
    --reset-offsets \
    --to-datetime 2026-09-13T10:00:00.000 \
    --execute
```

⚠️ **生产环境约束**：
- 先停止消费实例（避免双消费）
- 对账任务单独 consumer group（不要污染线上 group）
- 设 `isolation.level=read_committed`（只读已提交事务消息）

### 场景 3：Schema 演进导致反序列化失败

**现象**：新版本 Consumer 启动报 `Schema not found` / `deserialize error`。

```bash
# 1. AKHQ → Schema Registry → 找到 subject
# 2. 看 Versions 时间线：
#    v1: 2026-01 (old field)
#    v2: 2026-09 (新加了字段)
# 3. 看 compatibility 级别：默认 BACKWARD（消费者用新 schema 能读旧数据）

# 测试新 schema 是否兼容
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data "$(cat new-schema.json)" \
  http://schema-registry:8081/subjects/orders-value/versions

# 如果不兼容：
# - 改 default.deserialization.target.type
# - 或临时回退 producer schema
```

### 场景 4：ACL 审计与权限修复

**需求**：某服务报 `TopicAuthorizationException`，无写权限。

```bash
# 1. AKHQ → Permissions → 选 topic
# 2. 看现有 ACL：
#    User  service-A  Topic orders  READ   ✓
#    User  service-A  Topic orders  WRITE  ✗  ← 缺这个
# 3. Add ACL：
#    Principal: User:service-A
#    Operation: WRITE
#    Permission: ALLOW

# CLI 等价
kafka-acls.sh --bootstrap-server localhost:9092 \
    --add \
    --allow-principal User:service-A \
    --operation WRITE \
    --topic orders
```

### 场景 5：Connect 任务失败定位

**现象**：source-connector 状态 `FAILED`，数据停了 10 分钟。

```
AKHQ → Connect → 找到 connector → Tasks tab：
1. 看错误堆栈（搜索 Exception）
2. 看 Records Sent/Processed 速率：0/0 表示完全没进
3. 常见原因：
   - 源 DB 连不上（网络/账号）
   - 字段类型不匹配（MySQL tinyint → Kafka INT）
   - Topic 名冲突（已有同名 topic 分区数不匹配）

4. 临时方案：Pause → 改 Config → Restart
5. 永久方案：加 dead-letter-queue topic（errors.deadletterqueue.topic.name）
```

### 场景 6：跨集群消息镜像（MirrorMaker）

**需求**：把 dev 集群的 `orders` topic 镜像到 staging。

```bash
# 1. AKHQ 在 staging 集群上 → 看 MirrorMaker 状态
# 2. 验证消息条数对齐：
#    dev:   1000000 records
#    stage:  998234 records  ← 接近但差 1700 条（in-flight）

# MirrorMaker2 配置
clusters:
  - name: dev
    bootstrap.servers: dev-kafka:9092
  - name: stage
    bootstrap.servers: stage-kafka:9092
mirrors:
  - source.cluster: dev
    target.cluster: stage
    topics: ^orders\..*
    replication.factor: 3
```

## ⚠️ 常见坑与最佳实践

### 坑 1：生产消息到错误 partition

```bash
# 错误：用 round-robin 分区（顺序错乱）
# 正确：让 producer 自带 partition key
producer.send(new ProducerRecord<>("orders", orderId, payload));
//                              ^^^^^^^^^ partition key
```

### 坑 2：消费组 offset 重置导致数据丢失

```bash
# 永远不要直接对生产 group 用 --to-earliest
# 对账用独立 group（带 -audit 后缀）
kafka-consumer-groups.sh --group orders-audit \
    --reset-offsets --to-datetime 2026-09-13T10:00 --execute
```

### 坑 3：WebUI 暴露在公网

```yaml
# akhq.yml：必须开启 basic-auth + TLS
akhq:
  security:
    basic-auth:
      - username: admin
        password: ${STRONG_PASS}
        roles: [admin]
# 反向代理加 HTTPS（Nginx / Caddy）
```

### 坑 4：AKHQ 起不来但容器不退出

```bash
# 排查：docker logs akhq | grep -i error
# 常见：
# 1. bootstrap.servers 写错
# 2. SASL 账号密码不对（启 30s 重试）
# 3. Schema Registry url 路径写错
```

### 坑 5：误删 Topic

```bash
# Topic 删除不可逆！生产前必看：
kafka-topics.sh --delete --topic my-topic
# 如果 delete.topic.enable=false（生产默认），命令静默失败
# 验证：
kafka-topics.sh --describe --topic my-topic   ← 仍存在
```

## 🧪 一键排查清单

```bash
# 1. 集群健康
curl -s http://akhq:8080/api/health

# 2. 关键 topic 偏移量
kafka-run-class.sh kafka.tools.GetOffsetShell \
    --broker-list localhost:9092 --topic orders

# 3. 消费组 lag
kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --describe --group my-group

# 4. 看 schema 兼容性
curl -s http://schema-registry:8081/config/compatibility

# 5. Connector 状态
curl -s http://kafka-connect:8083/connectors | jq

# 6. ACL 审计
kafka-acls.sh --bootstrap-server localhost:9092 --list
```

## 📚 延伸阅读

- AKHQ 官方文档：https://akhq.io/docs/
- Kafbat UI（Kafdrop fork）：https://github.com/kafbat/kafka-ui
- Kafbat Helm Chart：https://github.com/kafbat/helm-charts
- Confluent Schema Registry：https://docs.confluent.io/platform/current/schema-registry/
- ksqlDB 语法速查：https://ksqldb.io/quickstart
- Kafka REST Proxy：https://docs.confluent.io/platform/current/kafka-rest/
- Kafka 官方工具集：`kafka-topics.sh` / `kafka-consumer-groups.sh` / `kafka-acls.sh`
