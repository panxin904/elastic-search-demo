---
title: AdminClient
date: 2026-08-15  # date-auto-injected
---

# 🔧 AdminClient

> **AdminClient** 是 Kafka 提供的集群管理 API，可以**程序化**地创建 Topic、修改配置、管理副本等。

## 🎯 AdminClient 是什么？

```
AdminClient = Kafka 集群管理客户端

功能：
  ✅ Topic 管理（创建、删除、修改）
  ✅ 配置管理（动态修改 Broker / Topic 配置）
  ✅ 副本管理（增加副本、副本分配）
  ✅ ACL 管理（权限控制）
  ✅ Consumer Group 管理
  ✅ 集群元数据查询
```

## 🚀 快速开始

```java
Properties props = new Properties();
props.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");

AdminClient admin = AdminClient.create(props);

// 查看集群信息
DescribeClusterResult cluster = admin.describeCluster();
cluster.clusterId().get();
System.out.println("Cluster ID: " + cluster.clusterId().get());
System.out.println("Controller: " + cluster.controller().get());

admin.close();
```

## 📝 Topic 管理

### 创建 Topic

```java
NewTopic newTopic = new NewTopic("orders", 3, (short) 2);
    .configs(Map.of(
        "retention.ms", "604800000",
        "cleanup.policy", "delete",
        "compression.type", "lz4"
    ));

CreateTopicsResult result = admin.createTopics(List.of(newTopic));
result.all().get();  // 阻塞等待完成
System.out.println("Topic created");
```

### 删除 Topic

```java
DeleteTopicsResult result = admin.deleteTopics(List.of("old-topic"));
result.all().get();
System.out.println("Topic deleted");
```

### 修改 Topic（增加分区）

```java
NewPartitions newPartitions = NewPartitions.increaseTo(6);
Map<String, NewPartitions> map = Map.of("orders", newPartitions);
CreatePartitionsResult result = admin.createPartitions(map);
result.all().get();
System.out.println("Partitions increased to 6");

// ⚠️ Kafka 不支持减少分区
```

### 修改 Topic 配置

```java
ConfigResource resource = new ConfigResource(
    ConfigResource.Type.TOPIC, "orders");

Map<ConfigResource, Collection<AlterConfigOp>> configs = Map.of(
    resource, List.of(
        new AlterConfigOp(
            new ConfigEntry("retention.ms", "1209600000"),
            AlterConfigOp.OpType.SET
        ),
        new AlterConfigOp(
            new ConfigEntry("cleanup.policy", "compact"),
            AlterConfigOp.OpType.SET
        )
    )
);

AlterConfigsResult result = admin.alterConfigs(configs);
result.all().get();
System.out.println("Config updated");
```

### 查看 Topic 列表

```java
ListTopicsResult result = admin.listTopics();
Set<String> topicNames = result.names().get();
System.out.println("Topics: " + topicNames);

// 列出内部 Topic
ListTopicsOptions options = new ListTopicsOptions().listInternal(true);
ListTopicsResult result2 = admin.listTopics(options);
Set<String> allTopics = result2.names().get();
```

### 查看 Topic 详情

```java
DescribeTopicsResult result = admin.describeTopics(List.of("orders"));
Map<String, TopicDescription> descriptions = result.allTopicNames().get();

for (Map.Entry<String, TopicDescription> entry : descriptions.entrySet()) {
    TopicDescription desc = entry.getValue();
    System.out.println("Topic: " + entry.getKey());
    System.out.println("Partitions: " + desc.partitions().size());
    
    for (TopicPartitionInfo partition : desc.partitions()) {
        System.out.println("  Partition " + partition.partition() + 
            ": leader=" + partition.leader() + ", replicas=" + partition.replicas());
    }
}
```

## 📝 副本管理

### 增加副本因子

```java
// 将 orders topic 的所有分区副本数从 1 增加到 2
Map<TopicPartition, Optional<NewPartitionReassignment>> reassignment = new HashMap<>();

DescribeTopicsResult topicsResult = admin.describeTopics(List.of("orders"));
TopicDescription topic = topicsResult.allTopicNames().get().get("orders");

for (TopicPartitionInfo partition : topic.partitions()) {
    int currentRf = partition.replicas().size();
    // 计算目标副本（+1）
    int targetRf = currentRf + 1;
    List<Integer> targetReplicas = new ArrayList<>(partition.replicas());
    for (int i = 0; i < targetRf; i++) {
        if (!targetReplicas.contains(i)) {
            targetReplicas.add(i);
        }
    }
    
    reassignment.put(
        new TopicPartition("orders", partition.partition()),
        Optional.of(new NewPartitionReassignment(targetReplicas))
    );
}

AlterPartitionReassignmentsResult result = 
    admin.alterPartitionReassignments(reassignment);
result.all().get();
System.out.println("Replica reassignment started");
```

### 触发 Preferred Replica Election

```java
// 让所有 Partition 的 Preferred Replica 成为 Leader
admin.alterPartitionReassignments(Map.of())  // 清空正在进行的 reassignment
    .all().get();

Map<String, Optional<NewPartitionReassignment>> empty = Map.of();
admin.alterPartitionReassignments(empty).all().get();

// 触发 Preferred Replica Election
// 实际通过 kafka-preferred-replica-election.sh 命令
// AdminClient 没有直接 API，可以用自定义脚本
```

### 平衡 Partition

```java
// 重新分配副本（均衡分布）
Map<TopicPartition, Optional<NewPartitionReassignment>> reassignment = new HashMap<>();

// 所有 broker 列表
DescribeClusterResult cluster = admin.describeCluster();
int brokerCount = cluster.nodes().get().size();

DescribeTopicsResult topicsResult = admin.describeTopics(
    admin.listTopics().names().get());

for (TopicPartitionInfo partition : topicsResult.allTopicNames().get()
        .get("orders").partitions()) {
    List<Integer> targetReplicas = new ArrayList<>();
    // 均匀分配到所有 broker
    for (int i = 0; i < partition.replicas().size(); i++) {
        targetReplicas.add((partition.partition() + i) % brokerCount);
    }
    
    reassignment.put(
        new TopicPartition("orders", partition.partition()),
        Optional.of(new NewPartitionReassignment(targetReplicas))
    );
}

admin.alterPartitionReassignments(reassignment).all().get();
```

## 📝 Consumer Group 管理

### 查看 Consumer Group

```java
ListConsumerGroupsResult result = admin.listConsumerGroups();
Collection<ConsumerGroupListing> groups = result.all().get();

for (ConsumerGroupListing group : groups) {
    System.out.println("Group: " + group.groupId() + ", State: " + group.state().orElse(null));
}
```

### 查看 Group Offset

```java
Map<TopicPartition, OffsetAndMetadata> offsets = admin
    .listConsumerGroupOffsets("order-processor")
    .partitionsToOffsetAndMetadata()
    .get();

for (Map.Entry<TopicPartition, OffsetAndMetadata> entry : offsets.entrySet()) {
    System.out.println(entry.getKey() + " offset=" + entry.getValue().offset());
}
```

### 删除 Consumer Group

```java
DeleteConsumerGroupsResult result = admin.deleteConsumerGroups(List.of("old-group"));
result.all().get();
System.out.println("Group deleted");
```

### 重置 Group Offset

```java
// 重置到最早
Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
offsets.put(new TopicPartition("orders", 0), new OffsetAndMetadata(0L));
offsets.put(new TopicPartition("orders", 1), new OffsetAndMetadata(0L));
offsets.put(new TopicPartition("orders", 2), new OffsetAndMetadata(0L));

AlterConsumerGroupOffsetsResult result = admin.alterConsumerGroupOffsets(
    "order-processor", offsets);
result.all().get();
```

## 📝 ACL 管理

### 列出所有 ACL

```java
DescribeAclsResult result = admin.describeAcls(
    new AclBindingFilter(ResourcePatternFilter.ANY, AccessControlEntryFilter.ANY));

Collection<AclBinding> bindings = result.values().get();
for (AclBinding binding : bindings) {
    System.out.println("Pattern: " + binding.pattern() + 
        ", Entry: " + binding.entry());
}
```

### 添加 ACL

```java
AclBinding aclBinding = new AclBinding(
    new ResourcePattern(ResourceType.TOPIC, "orders", PatternType.LITERAL),
    new AccessControlEntry(
        "User:alice",            // principal
        "*",                      // host
        AclOperation.READ,        // operation
        AclPermissionType.ALLOW   // permission type
    )
);

CreateAclsResult result = admin.createAcls(List.of(aclBinding));
result.all().get();
System.out.println("ACL added");
```

### 删除 ACL

```java
DeleteAclsResult result = admin.deleteAcls(List.of(aclBinding));
result.all().get();
```

## 📝 配置管理

### 查看 Broker 配置

```java
ConfigResource resource = new ConfigResource(
    ConfigResource.Type.BROKER, "1");

DescribeConfigsResult result = admin.describeConfigs(List.of(resource));
Map<ConfigResource, Config> configs = result.all().get();

Config config = configs.get(resource);
for (ConfigEntry entry : config.entries()) {
    System.out.println(entry.name() + " = " + entry.value());
}
```

### 动态修改 Broker 配置

```java
Map<ConfigResource, Collection<AlterConfigOp>> configs = Map.of(
    resource, List.of(
        new AlterConfigOp(
            new ConfigEntry("log.retention.ms", "86400000"),
            AlterConfigOp.OpType.SET
        )
    )
);

AlterConfigsResult result = admin.alterConfigs(configs);
result.all().get();
```

## 📝 集群元数据

### 查看集群信息

```java
DescribeClusterResult cluster = admin.describeCluster();
System.out.println("Cluster ID: " + cluster.clusterId().get());
System.out.println("Controller: " + cluster.controller().get());
System.out.println("Brokers: " + cluster.nodes().get().size());
```

### 查看 Broker 列表

```java
Collection<Node> brokers = admin.describeCluster().nodes().get();
for (Node broker : brokers) {
    System.out.println("Broker " + broker.id() + ": " + 
        broker.host() + ":" + broker.port());
}
```

## 🛠️ 实战：Topic 自动管理服务

```java
@Service
public class TopicManagerService {
    
    @Autowired
    private AdminClient admin;
    
    public void createTopicIfNotExists(String topic, int partitions, short replicationFactor) {
        try {
            // 检查 Topic 是否存在
            Set<String> existing = admin.listTopics().names().get();
            
            if (existing.contains(topic)) {
                log.info("Topic {} already exists", topic);
                return;
            }
            
            // 创建 Topic
            NewTopic newTopic = new NewTopic(topic, partitions, replicationFactor)
                .configs(Map.of(
                    "retention.ms", "604800000",
                    "cleanup.policy", "delete"
                ));
            
            admin.createTopics(List.of(newTopic)).all().get();
            log.info("Topic {} created", topic);
            
        } catch (Exception e) {
            log.error("Failed to create topic {}", topic, e);
            throw new RuntimeException(e);
        }
    }
    
    public void expandTopic(String topic, int newPartitionCount) {
        try {
            // 获取当前 Partition 数
            TopicDescription desc = admin.describeTopics(List.of(topic))
                .allTopicNames().get().get(topic);
            
            int currentCount = desc.partitions().size();
            
            if (newPartitionCount <= currentCount) {
                log.warn("New partition count {} <= current {}, skipped",
                    newPartitionCount, currentCount);
                return;
            }
            
            // 扩容
            NewPartitions newPartitions = NewPartitions.increaseTo(newPartitionCount);
            admin.createPartitions(Map.of(topic, newPartitions)).all().get();
            
            log.info("Topic {} expanded from {} to {} partitions",
                topic, currentCount, newPartitionCount);
            
        } catch (Exception e) {
            log.error("Failed to expand topic {}", topic, e);
        }
    }
    
    public void rebalanceCluster() {
        try {
            // 列出所有 Topic
            Set<String> topics = admin.listTopics().names().get();
            
            for (String topic : topics) {
                // 跳过内部 Topic
                if (topic.startsWith("__")) continue;
                
                TopicDescription desc = admin.describeTopics(List.of(topic))
                    .allTopicNames().get().get(topic);
                
                // 检查是否有 Partition 不均衡
                // ... 业务逻辑
            }
            
        } catch (Exception e) {
            log.error("Failed to rebalance cluster", e);
        }
    }
}
```

## ⚙️ AdminClient 配置

```java
Properties props = new Properties();
props.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(AdminClientConfig.REQUEST_TIMEOUT_MS_CONFIG, 30000);
props.put(AdminClientConfig.DEFAULT_API_TIMEOUT_MS_CONFIG, 60000);
props.put(AdminClientConfig.SECURITY_PROTOCOL_CONFIG, "SASL_SSL");
// ... SASL 配置

AdminClient admin = AdminClient.create(props);
```

## ⚠️ 常见问题

### 问题 1：AdminClient 操作超时

```
原因：操作耗时长（如 reassignment）
解决：
  1. 增加 default.api.timeout.ms
  2. 异步操作（不调用 .get()）
  3. 检查 Kafka 集群健康
```

### 问题 2：Topic 已存在错误

```
报错：TopicAlreadyExistsException
解决：
  1. 先 list 检查
  2. 捕获异常忽略
```

### 问题 3：权限不足

```
报错：AuthorizationException
解决：
  1. 配置 ACL 权限
  2. 使用 admin 用户
  3. 启用 SASL/SSL
```

## 🎯 总结

**AdminClient 核心要点**：
- ✅ Kafka 集群管理 API
- ✅ Topic / Broker / Group / ACL 管理
- ✅ 程序化管理集群（替代命令行）
- ✅ 异步操作（Future）
- ⚠️ 大操作耗时长（如 reassignment）
- ⚠️ 异步操作需捕获异常

**下一步：** [🔄 序列化与反序列化](/06-jdk/serialization) — SerDe 详解


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
