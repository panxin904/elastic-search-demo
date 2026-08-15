---
title: 自定义分区器
---

# 🎯 自定义分区器

> 默认分区器按 `hash(key) % partitions` 分配消息，但在**实际业务**中往往需要更复杂的路由策略。本章讲解如何自定义分区器。

## 🎯 默认分区器回顾

```java
// DefaultPartitioner 默认实现
public int partition(String topic, Object key, byte[] keyBytes,
                    Object value, byte[] valueBytes, Cluster cluster) {
    if (keyBytes == null) {
        // 无 key：轮询所有分区
        return stickyPartitionCache.partition(topic, cluster);
    }
    // 有 key：hash(key) % partitions
    return Utils.toPositive(Utils.murmur2(keyBytes)) % 
        cluster.partitionsForTopic(topic).size();
}
```

**默认行为**：
- 有 Key → `hash(key) % partitions`（hash 一致）
- 无 Key → 轮询（Kafka 2.4+ 用粘性分区优化）

## 🎯 为什么需要自定义？

```
业务需求：
  - 不同业务类型走不同分区（如 VIP 用户独立分区）
  - 同 Key 必须同 Partition（保证顺序）
  - 同 Key 必须跨 Partition（负载均衡）
  - 灰度发布（新版本先发到部分 Partition）
  - 按机房就近路由
```

## 🔧 Partitioner 接口

```java
public interface Partitioner extends Configurable, Closeable {
    
    /**
     * 计算消息应该发到哪个 Partition
     * @return 分区编号（0-based）
     * @return -1 表示使用 Kafka 默认分区器
     */
    int partition(String topic, Object key, byte[] keyBytes,
                  Object value, byte[] valueBytes, Cluster cluster);
    
    /**
     * 关闭资源
     */
    @Override default void close() {}
    
    /**
     * 配置回调
     */
    @Override default void configure(Map<String, ?> configs) {}
}
```

## 📊 实战：5 种业务场景的分区器

### 场景 1：按业务类型路由

```java
public class OrderPartitioner implements Partitioner {
    
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        int partitionCount = cluster.partitionsForTopic(topic).size();
        
        // 1. 优先按 Key 路由（保证同 Key 顺序）
        if (keyBytes != null) {
            return Utils.toPositive(Utils.murmur2(keyBytes)) % partitionCount;
        }
        
        // 2. 无 Key 时，按 value 业务类型路由
        if (value instanceof OrderEvent) {
            OrderEvent event = (OrderEvent) value;
            switch (event.getType()) {
                case "VIP_ORDER":
                    return 0;  // VIP 订单走 P0
                case "NORMAL_ORDER":
                    return 1;  // 普通订单走 P1
                case "REFUND":
                    return 2;  // 退款走 P2
                default:
                    return Math.abs(event.getType().hashCode()) % partitionCount;
            }
        }
        
        return -1;
    }
}
```

### 场景 2：按机房就近路由

```java
public class GeoPartitioner implements Partitioner {
    
    private final Map<String, Integer> brokerPartitionMap = new HashMap<>();
    
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        if (keyBytes == null) return -1;
        
        // 1. 解析 Key 中的机房信息
        String keyStr = (String) key;  // 格式: "BJ:user123"
        String region = keyStr.split(":")[0];  // "BJ" / "SH" / "GZ"
        
        // 2. 获取该机房的 Partition
        Integer partition = brokerPartitionMap.get(region);
        if (partition != null) return partition;
        
        // 3. 默认 hash 路由
        return Utils.toPositive(Utils.murmur2(keyBytes)) % 
            cluster.partitionsForTopic(topic).size();
    }
}
```

### 场景 3：灰度发布分区器

```java
public class CanaryPartitioner implements Partitioner {
    
    private static final double CANARY_RATIO = 0.1;  // 10% 流量走灰度
    
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        int partitionCount = cluster.partitionsForTopic(topic).size();
        
        // 1. 同 Key 必须同 Partition（保证顺序）
        if (keyBytes != null) {
            int hashPartition = Utils.toPositive(Utils.murmur2(keyBytes)) % partitionCount;
            
            // 2. 按 Hash 一致性分配（10% Key 永远走灰度分区）
            // 简单实现：根据 Key 的 hash 前缀
            int prefix = Math.abs(java.util.Arrays.hashCode(keyBytes)) % 100;
            if (prefix < CANARY_RATIO * 100) {
                // 灰度 Key 走 P0（最稳定的灰度分区）
                return 0;
            }
            
            // 普通 Key：使用 hash 路由，但跳过 P0
            return hashPartition == 0 ? 1 : hashPartition;
        }
        
        return -1;
    }
}
```

### 场景 4：多 Key 关联（Join 场景）

```java
public class OrderItemPartitioner implements Partitioner {
    
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        // Key 格式: "{orderId}:item:itemId" 或 "{orderId}:status"
        // 需要所有同 orderId 的消息走同一 Partition
        
        String keyStr = (String) key;
        
        // 提取 {} 中的内容（hash tag）
        int start = keyStr.indexOf('{');
        int end = keyStr.indexOf('}');
        
        String hashKey = (start >= 0 && end > start) 
            ? keyStr.substring(start + 1, end)
            : keyStr;
        
        byte[] hashKeyBytes = hashKey.getBytes(StandardCharsets.UTF_8);
        
        return Utils.toPositive(Utils.murmur2(hashKeyBytes)) % 
            cluster.partitionsForTopic(topic).size();
    }
}

// 使用：
// "order:{1001}:info" 和 "order:{1001}:items" 走同一 Partition
// "order:{1002}:info" 和 "order:{1002}:items" 走同一 Partition（不同于 1001）
```

### 场景 5：粘性分区（Sticky Partition）

```java
// Kafka 2.4+ 默认行为：空 Key 时用粘性分区
// 即同一批次消息发到同一 Partition，减少 Broker 连接开销

// 模拟实现：
public class StickyPartitioner implements Partitioner {
    
    private final ThreadLocal<Integer> stickyPartition = new ThreadLocal<>();
    
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        // 有 Key：按 Key 路由
        if (keyBytes != null) {
            return Utils.toPositive(Utils.murmur2(keyBytes)) % 
                cluster.partitionsForTopic(topic).size();
        }
        
        // 无 Key：粘性分区（同一线程固定分区）
        Integer current = stickyPartition.get();
        if (current != null) {
            return current;
        }
        
        int newPartition = (int) (Math.random() * 
            cluster.partitionsForTopic(topic).size());
        stickyPartition.set(newPartition);
        return newPartition;
    }
}
```

## 🔧 注册自定义分区器

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

// 注册自定义分区器
props.put(ProducerConfig.PARTITIONER_CLASS_CONFIG, OrderPartitioner.class.getName());

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// 使用
ProducerRecord<String, String> record = new ProducerRecord<>(
    "orders", "key1", "value1");
producer.send(record);  // 使用自定义分区器
```

## 🛠️ 实战：电商订单智能分区

```java
public class SmartOrderPartitioner implements Partitioner {
    
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        int partitionCount = cluster.partitionsForTopic(topic).size();
        
        // 策略 1：相同 orderId 的所有事件进入同一 Partition（保证顺序）
        if (keyBytes != null) {
            String keyStr = new String(keyBytes);
            if (keyStr.startsWith("order:")) {
                String orderId = keyStr.substring(6);
                return Utils.toPositive(Utils.murmur2(orderId.getBytes())) % partitionCount;
            }
        }
        
        // 策略 2：按订单类型路由（VIP / 普通 / 秒杀）
        if (value instanceof OrderEvent) {
            OrderEvent event = (OrderEvent) value;
            
            // VIP 订单专用分区
            if (event.isVip()) {
                return 0;  // P0 专门处理 VIP
            }
            
            // 秒杀订单单独分区
            if (event.isFlashSale()) {
                return 1;  // P1 专门处理秒杀
            }
            
            // 普通订单 hash 路由
            return Utils.toPositive(Utils.murmur2(event.getOrderId().getBytes())) 
                % Math.max(2, partitionCount - 2) + 2;  // 避开 P0、P1
        }
        
        // 兜底：Kafka 默认
        return -1;
    }
}
```

## 📊 注意事项

### 分区器是无状态的

```java
// ⚠️ 不要在分区器中保存可变状态
public class BadPartitioner implements Partitioner {
    private int counter = 0;  // 多线程会有线程安全问题
    
    @Override
    public int partition(...) {
        counter++;  // ⚠️ 危险！
        return counter % partitions;
    }
}

// ✅ 使用 ThreadLocal 或无状态
```

### 性能考虑

```
分区器调用频率：
  - 每次 send() 都调用
  - 高 QPS 时（百万/秒）性能影响显著

优化：
  1. 分区器逻辑尽量简单
  2. 避免在分区器中做 IO
  3. 避免在分区器中做复杂计算
  4. 缓存常用结果
```

### 集群变更感知

```java
@Override
public int partition(String topic, Object key, byte[] keyBytes,
                    Object value, byte[] valueBytes, Cluster cluster) {
    // cluster 参数提供最新集群信息
    // Partition 数量变化时会实时更新
    int partitionCount = cluster.partitionsForTopic(topic).size();
    // ...
}
```

## ⚠️ 常见问题

### 问题 1：自定义分区器导致数据倾斜

```
现象：某些 Partition 接收大量消息，其他 Partition 闲置
原因：分区器返回固定值或分布不均
解决：
  1. 确保 Key 经过 hash 分布
  2. 避免返回固定值
  3. 测试时观察 Partition 分布
```

### 问题 2：自定义分区器导致顺序错乱

```
现象：同 Key 消息进入不同 Partition
原因：分区器返回 -1 或随机值
解决：
  1. 始终返回相同 Key 的相同 Partition
  2. 使用 hash 路由保证一致性
```

### 问题 3：分区器抛异常

```
原因：分区器 bug
影响：整个 Producer 卡死
解决：
  1. 分区器内 try-catch
  2. 出错时返回 -1（Kafka 默认）
  3. 充分测试
```

## 🎯 总结

**自定义分区器核心要点**：
- ✅ 实现 Partitioner 接口
- ✅ 按 Key 路由保证同 Key 同 Partition
- ✅ 按 Value 路由实现业务分类
- ✅ 使用 ThreadLocal 保持线程安全状态
- ⚠️ 分区器逻辑尽量简单
- ⚠️ 避免数据倾斜

**下一步：** [🚨 异常处理](/06-jdk/exception) — Producer/Consumer 异常处理
