---
title: 多环境隔离
---

# 🌍 多环境隔离

> **多环境隔离**是企业级 Kafka 部署的关键。生产、预发、测试环境需要**严格隔离**，避免相互影响。

## 🎯 多环境策略

### 方案 1：单集群多 Topic 隔离（推荐）

```
集群：production-kafka（3 节点）
环境隔离通过 Topic 前缀：
  - dev.orders / dev.payments / dev.users
  - test.orders / test.payments / test.users
  - prod.orders / prod.payments / prod.users

✅ 简单：同一集群
✅ 资源共享（成本低）
⚠️ 风险：环境间可能影响（资源争抢）
```

### 方案 2：多集群隔离

```
集群：
  - dev-kafka（1 节点，单机）
  - test-kafka（3 节点）
  - staging-kafka（3 节点）
  - production-kafka（5+ 节点）

✅ 严格隔离
⚠️ 成本高
⚠️ 运维复杂
```

### 方案 3：多集群 + 镜像（MirrorMaker）

```
生产集群 ← MirrorMaker ← 测试集群
  - 测试集群镜像生产数据
  - 测试环境使用真实数据
  - 生产环境不受影响

✅ 严格隔离 + 测试真实
⚠️ 镜像延迟
⚠️ 配置复杂
```

## 📊 环境规划

### 环境命名规范

```
环境类型：
  - dev：开发环境（开发者本地）
  - test：测试环境（QA 团队）
  - staging：预发环境（与生产相同配置）
  - prod：生产环境

Topic 命名：
  - {env}.{业务域}.{事件类型}
  - dev.order.events
  - test.order.events
  - prod.order.events

应用命名：
  - {业务}-{环境}
  - order-service-dev
  - order-service-test
  - order-service-prod
```

### 集群规划

```
生产环境：
  - 5+ Broker
  - 3 副本
  - KRaft 模式
  - 高配置（64GB RAM、NVMe SSD）

预发环境：
  - 3 Broker
  - 3 副本
  - KRaft 模式
  - 中等配置（32GB RAM）

测试环境：
  - 3 Broker
  - 2 副本
  - KRaft 模式
  - 低配置（16GB RAM）

开发环境：
  - 1 Broker（单机）
  - 1 副本
  - KRaft 模式
  - 最低配置（4GB RAM）
```

## 🔧 方案 1：单集群多 Topic 隔离

### 配置

```yaml
# application.yml（不同环境）

# 开发环境
spring:
  profiles: dev
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: order-service-dev

# 测试环境
spring:
  profiles: test
  kafka:
    bootstrap-servers: test-kafka:9092
    consumer:
      group-id: order-service-test

# 生产环境
spring:
  profiles: prod
  kafka:
    bootstrap-servers: prod-kafka:9092
    consumer:
      group-id: order-service-prod
```

### Topic 前缀动态化

```java
@Component
@Profile("dev")
public class DevKafkaConfig {
    @Value("${kafka.topic-prefix:dev.}")
    private String prefix;
}

@Component
@Profile("prod")
public class ProdKafkaConfig {
    @Value("${kafka.topic-prefix:prod.}")
    private String prefix;
}

@Service
public class OrderProducer {
    
    @Value("${kafka.topic-prefix:dev.}")
    private String prefix;
    
    public void send(OrderEvent event) {
        // 自动添加前缀
        kafkaTemplate.send(prefix + "order.events", event.getOrderId(), event);
    }
}
```

## 🔧 方案 2：多集群隔离

### Spring Boot 多 Kafka 配置

```yaml
# application-dev.yml
spring:
  kafka:
    bootstrap-servers: dev-kafka:9092

# application-test.yml
spring:
  kafka:
    bootstrap-servers: test-kafka:9092

# application-prod.yml
spring:
  kafka:
    bootstrap-servers: prod-kafka:9092
```

### 跨集群迁移

```java
@Service
public class CrossClusterMigration {
    
    @Autowired
    private KafkaTemplate<String, String> sourceKafkaTemplate;
    
    @Autowired
    private KafkaTemplate<String, String> targetKafkaTemplate;
    
    // 从 dev 集群消费，写到 test 集群
    @KafkaListener(topics = "dev.orders", groupId = "migration")
    public void migrate(ConsumerRecord<String, String> record) {
        // 写入目标集群
        targetKafkaTemplate.send("test.orders", record.key(), record.value());
    }
}
```

## 🔧 方案 3：MirrorMaker 2.0

### 架构

```
Source Cluster                Target Cluster
   (prod)                    (staging/test)
     |                            ↑
     |-------- MirrorMaker -------|
```

### 配置

```properties
# mm2.properties
clusters=source,target
source.bootstrap.servers=prod-kafka:9092
target.bootstrap.servers=staging-kafka:9092

source->target.enabled=true
source->target.topics=prod.orders,prod.payments,prod.users

target->source.enabled=false

# 复制策略
replication.factor=3
```

### 启动

```bash
bin/connect-mirror-maker.sh config/mm2.properties
```

### MirrorMaker 2.0 特性

```
✅ 基于 Kafka Connect 框架
✅ 支持双向复制
✅ 支持 Topic 选择
✅ 支持配置转换
✅ 容错性强
```

## 🛠️ 实战：Spring Boot 多环境配置

### application.yml

```yaml
spring:
  profiles:
    active: dev
  application:
    name: order-service

# 默认配置（被 profile 覆盖）
kafka:
  topic-prefix: prod.
  replication-factor: 3

---
spring:
  config:
    activate:
      on-profile: dev
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: order-service-dev
  logging:
    level:
      root: DEBUG

---
spring:
  config:
    activate:
      on-profile: test
  kafka:
    bootstrap-servers: test-kafka:9092
    consumer:
      group-id: order-service-test

---
spring:
  config:
    activate:
      on-profile: staging
  kafka:
    bootstrap-servers: staging-kafka:9092
    consumer:
      group-id: order-service-staging

---
spring:
  config:
    activate:
      on-profile: prod
  kafka:
    bootstrap-servers: prod-kafka-1:9092,prod-kafka-2:9092,prod-kafka-3:9092
    consumer:
      group-id: order-service-prod
```

### Topic 自动创建

```java
@Component
public class TopicProvisioner {
    
    @Autowired
    private AdminClient adminClient;
    
    @Value("${spring.profiles.active}")
    private String env;
    
    @Value("${kafka.topic-prefix}")
    private String topicPrefix;
    
    @PostConstruct
    public void provisionTopics() {
        // 仅在 dev/test 环境自动创建 Topic
        if (!"dev".equals(env) && !"test".equals(env)) {
            return;
        }
        
        // 创建 Topic
        List<NewTopic> topics = Arrays.asList(
            new NewTopic(topicPrefix + "orders", 3, (short) 1),
            new NewTopic(topicPrefix + "payments", 3, (short) 1),
            new NewTopic(topicPrefix + "users", 3, (short) 1)
        );
        
        try {
            adminClient.createTopics(topics).all().get();
            log.info("Topics created: {}", topics);
        } catch (Exception e) {
            log.warn("Topics may already exist", e);
        }
    }
}
```

## 🔧 资源隔离

### 命名空间隔离

```bash
# 不同环境使用不同的 Topic 前缀
# dev 环境：dev.* （包含测试数据）
# test 环境：test.*（QA 数据）
# staging 环境：staging.*（预发数据）
# prod 环境：prod.*（生产数据）
```

### ACL 隔离

```bash
# dev：开发团队全部权限
kafka-acls.sh --bootstrap-server localhost:9092 \
    --add --allow-principal User:dev-team --allow-host '*' \
    --operation ALL --topic 'dev.*' --cluster

# test：QA 团队读 + 写
kafka-acls.sh --bootstrap-server test-kafka:9092 \
    --add --allow-principal User:qa-team --allow-host '*' \
    --operation READ,WRITE --topic 'test.*'

# prod：生产团队只读
kafka-acls.sh --bootstrap-server prod-kafka:9092 \
    --add --allow-principal User:prod-team --allow-host '*' \
    --operation READ --topic 'prod.*'
```

## 📊 环境对比表

| 维度 | dev | test | staging | prod |
|------|-----|------|---------|------|
| 集群 | 单机 | 3 Broker | 3 Broker | 5+ Broker |
| 副本 | 1 | 2 | 3 | 3 |
| 容量 | 10GB | 100GB | 1TB | 10TB+ |
| 流量 | 极低 | 低 | 中 | 高 |
| 镜像 | 无 | 无 | MirrorMaker | 源 |
| ACL | 开发全权 | QA 部分 | 运维+开发 | 严格 |

## ⚠️ 常见问题

### 问题 1：环境间相互影响

```
场景：测试环境发送大量消息影响生产
解决：
  1. 严格 Topic 前缀
  2. 资源配额（限流）
  3. 多集群隔离
```

### 问题 2：配置漂移

```
场景：dev 和 prod 配置不一致
解决：
  1. 统一配置中心（Nacos / Apollo）
  2. Profile 严格管理
  3. 配置审计
```

### 问题 3：数据混淆

```
场景：test 环境用 prod 数据
解决：
  1. 数据脱敏
  2. 数据隔离
  3. 自动化测试数据生成
```

## 🎯 总结

**多环境隔离核心要点**：
- ✅ 单集群多 Topic（推荐，简单）
- ✅ 多集群隔离（严格，成本高）
- ✅ MirrorMaker 2.0 用于跨集群数据同步
- ✅ 严格 Topic 前缀和 ACL
- ✅ Spring Boot Profile 管理配置
- ⚠️ 环境间可能相互影响（资源争抢）
- ⚠️ 配置漂移需要统一管理

**下一步：** [🏭 集群部署](/08-enterprise/cluster) — 生产环境 Kafka 集群搭建
