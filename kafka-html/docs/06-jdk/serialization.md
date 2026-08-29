---
title: 序列化与反序列化
date: 2026-08-15  # date-auto-injected
---

# 🔄 序列化与反序列化

> 序列化（Serialize）和反序列化（Deserialize）是 Kafka 客户端与 Broker 之间数据转换的关键环节。选择合适的序列化器直接影响性能、可靠性和可维护性。

## 🎯 序列化基础

### 为什么需要序列化？

```
Producer（Java 对象）→ 序列化（字节数组）→ Kafka Broker
Kafka Broker → 反序列化（字节数组）→ Consumer（Java 对象）
```

### 序列化器接口

```java
// Serializer<T>
public interface Serializer<T> extends Closeable {
    // 核心方法：对象 → 字节数组
    byte[] serialize(String topic, T data);
    
    // 默认实现（Java 序列化，效率低）
    default byte[] serialize(String topic, Headers headers, T data) {
        return serialize(topic, data);
    }
    
    // 关闭资源
    @Override default void close() {}
    
    // 配置回调
    default void configure(Map<String, ?> configs, boolean isKey) {}
}
```

### 反序列化器接口

```java
// Deserializer<T>
public interface Deserializer<T> extends Closeable {
    // 核心方法：字节数组 → 对象
    T deserialize(String topic, byte[] data);
    
    // 高级版本（带 Headers）
    default T deserialize(String topic, Headers headers, byte[] data) {
        return deserialize(topic, data);
    }
    
    @Override default void close() {}
    default void configure(Map<String, ?> configs, boolean isKey) {}
}
```

## 📊 内置序列化器

### Kafka 内置

| 序列化器 | 类 | 用途 |
|---------|---|------|
| StringSerializer | String | 字符串 |
| ByteArraySerializer | byte[] | 字节数组 |
| ByteBufferSerializer | ByteBuffer | NIO 缓冲 |
| IntegerSerializer | Integer | 4 字节 int |
| LongSerializer | Long | 8 字节 long |
| FloatSerializer | Float | 4 字节 float |
| DoubleSerializer | Double | 8 字节 double |
| ShortSerializer | Short | 2 字节 short |
| UUIDSerializer | UUID | 16 字节 |
| VoidSerializer | Void | null |

### 配置

```java
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
```

### 内置序列化器使用场景

```java
// 1. 字符串
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
producer.send(new ProducerRecord<>("logs", "log message"));

// 2. 字节数组
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, ByteArraySerializer.class.getName());
producer.send(new ProducerRecord<>("binary", byteData));

// 3. 自定义对象（结合 JSON / Avro / Protobuf）
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class.getName());
producer.send(new ProducerRecord<>("orders", orderEvent));
```

## 🔧 常用序列化方案

### 方案 1：JSON（最常用）

```java
// 自定义 JSON 序列化器
public class JsonSerializer<T> implements Serializer<T> {
    
    private final ObjectMapper mapper = new ObjectMapper()
        .registerModule(new JavaTimeModule());  // 支持 LocalDateTime
    
    @Override
    public byte[] serialize(String topic, T data) {
        if (data == null) return null;
        try {
            return mapper.writeValueAsBytes(data);
        } catch (Exception e) {
            throw new SerializationException("Failed to serialize", e);
        }
    }
}

// 反序列化器
public class JsonDeserializer<T> implements Deserializer<T> {
    
    private final ObjectMapper mapper = new ObjectMapper()
        .registerModule(new JavaTimeModule());
    private Class<T> targetClass;
    
    @Override
    public T deserialize(String topic, byte[] data) {
        if (data == null) return null;
        try {
            return mapper.readValue(data, targetClass);
        } catch (Exception e) {
            throw new SerializationException("Failed to deserialize", e);
        }
    }
    
    @Override
    public void configure(Map<String, ?> configs, boolean isKey) {
        String className = (String) configs.get("json.deserializer.class");
        try {
            this.targetClass = (Class<T>) Class.forName(className);
        } catch (ClassNotFoundException e) {
            throw new SerializationException("Class not found", e);
        }
    }
}
```

**使用**：
```java
// Producer
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class.getName());
props.put(JsonSerializerConfig.JSON_VALUE_CLASS_TYPE, OrderEvent.class.getName());

// Consumer
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class.getName());
props.put(JsonDeserializerConfig.JSON_VALUE_CLASS_TYPE, OrderEvent.class.getName());
```

**优点**：
- ✅ 可读性好
- ✅ 跨语言
- ✅ 兼容老系统

**缺点**：
- ❌ 体积大（JSON 元数据）
- ❌ 性能中等

### 方案 2：Protobuf（推荐生产）

```protobuf
// user.proto
syntax = "proto3";

message User {
    int64 id = 1;
    string name = 2;
    int32 age = 3;
    string email = 4;
}
```

```java
// Protobuf 序列化器
public class ProtobufSerializer<T extends MessageLite> implements Serializer<T> {
    
    @Override
    public byte[] serialize(String topic, T data) {
        if (data == null) return null;
        return data.toByteArray();
    }
}
```

**优点**：
- ✅ 体积小（二进制）
- ✅ 性能好
- ✅ Schema 管理（向后兼容）
- ✅ 跨语言

**缺点**：
- ❌ 需要 .proto 文件
- ❌ 不可读

### 方案 3：Avro（大数据常用）

```json
// user.avsc
{
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "id", "type": "long"},
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"}
    ]
}
```

```java
// Avro 序列化
User user = User.newBuilder()
    .setId(1001L)
    .setName("Alice")
    .setAge(28)
    .build();

byte[] data = user.toByteBuffer().array();
```

### 方案 4：Java 序列化（不推荐）

```java
// Java 序列化（Kryo 替代）
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, 
    "org.apache.kafka.common.serialization.ByteArraySerializer");

// 自定义对象用 Kryo 序列化
public class KryoSerializer<T> implements Serializer<T> {
    
    private final ThreadLocal<Kryo> kryo = ThreadLocal.withInitial(() -> {
        Kryo kryo = new Kryo();
        kryo.setRegistrationRequired(false);
        return kryo;
    });
    
    @Override
    public byte[] serialize(String topic, T data) {
        if (data == null) return null;
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        Output output = new Output(baos);
        kryo.get().writeObject(output, data);
        output.close();
        return baos.toByteArray();
    }
}
```

**⚠️ Java 序列化问题**：
- ❌ 二进制不可读
- ❌ 体积大
- ❌ 性能差
- ❌ **存在反序列化漏洞（CVE）**
- ❌ 不可跨语言

## 📊 序列化方案对比

| 方案 | 体积 | 速度 | 可读性 | Schema | 跨语言 | 推荐度 |
|------|------|------|--------|--------|--------|--------|
| **Java** | 大 | 慢 | ❌ | ❌ | ❌ | ❌ |
| **JSON** | 中 | 中 | ✅ | ❌ | ✅ | ✅ |
| **XML** | 大 | 慢 | ✅ | ❌ | ✅ | ❌ |
| **Protobuf** | 小 | 快 | ❌ | ✅ | ✅ | ✅✅ |
| **Avro** | 小 | 快 | ❌ | ✅ | ✅ | ✅ |
| **MsgPack** | 小 | 快 | ❌ | ❌ | ✅ | ✅ |
| **Thrift** | 小 | 快 | ❌ | ✅ | ✅ | ✅ |

## 🔧 实战：选择合适的序列化方案

### 场景 1：日志收集

```java
// JSON：可读性好，吞吐要求不高
public class LogEvent {
    private String level;     // INFO / WARN / ERROR
    private String message;
    private long timestamp;
    private Map<String, Object> context;
}
```

### 场景 2：高吞吐事件流

```java
// Protobuf：体积小，吞吐高
message OrderEvent {
    int64 order_id = 1;
    string status = 2;
    double amount = 3;
    int64 timestamp = 4;
}
```

### 场景 3：大数据 ETL

```java
// Avro：与 Hive / Spark 集成好
{
    "type": "record",
    "name": "UserEvent",
    "namespace": "com.example.events",
    "fields": [...]
}
```

### 场景 4：HTTP API + Kafka

```java
// JSON：HTTP API 默认 JSON
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class.getName());
```

## 🔧 Schema 管理

### Schema Registry

```
推荐使用 Confluent Schema Registry 管理 Schema 演进
  - 自动验证 Schema 兼容性
  - 支持多版本
  - 兼容 Avro / Protobuf / JSON Schema
```

### Protobuf 兼容性规则

```
✅ 向后兼容（推荐）：
  - 添加新字段
  - 删除可选字段
  
⚠️ 需要谨慎：
  - 修改已有字段类型
  - 重命名字段
  
❌ 不兼容：
  - 修改已有字段编号（field number）
  - 删除必填字段
```

## 🔧 自定义序列化器完整示例

### 通用 JSON 序列化器

```java
public class JsonSerializer<T> implements Serializer<T>, Deserializer<T> {
    
    private final ObjectMapper mapper = new ObjectMapper()
        .registerModule(new JavaTimeModule())
        .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);
    
    private Class<T> targetClass;
    
    @Override
    public byte[] serialize(String topic, T data) {
        if (data == null) return null;
        try {
            return mapper.writeValueAsBytes(data);
        } catch (Exception e) {
            throw new SerializationException("Serialize failed for " + data, e);
        }
    }
    
    @Override
    public T deserialize(String topic, byte[] data) {
        if (data == null) return null;
        try {
            if (targetClass != null) {
                return mapper.readValue(data, targetClass);
            }
            return mapper.readValue(data, new TypeReference<T>() {});
        } catch (Exception e) {
            throw new SerializationException("Deserialize failed", e);
        }
    }
    
    @Override
    public void configure(Map<String, ?> configs, boolean isKey) {
        String className = (String) configs.get("json.value.class");
        if (className != null) {
            try {
                this.targetClass = (Class<T>) Class.forName(className);
            } catch (ClassNotFoundException e) {
                throw new SerializationException("Class not found: " + className, e);
            }
        }
    }
}
```

## 🔧 异常处理

```java
// 序列化异常处理
try {
    byte[] data = serializer.serialize("topic", obj);
    producer.send(new ProducerRecord<>("topic", data));
} catch (SerializationException e) {
    // 序列化失败（不可重试）
    log.error("Serialization failed", e);
    // 发送到死信队列或告警
}

// 反序列化异常处理
try {
    MyEvent event = deserializer.deserialize("topic", data);
    processEvent(event);
} catch (SerializationException e) {
    // 反序列化失败
    log.error("Deserialization failed", e);
    
    // 跳过这条消息（但更新 offset 避免重复失败）
    // 或发送到死信队列
    sendToDeadLetter(rawData);
    
    // 监控告警
    metrics.counter("kafka_deserialization_error").increment();
}
```

## ⚠️ 常见问题

### 问题 1：生产者和消费者序列化不匹配

```
报错：ClassCastException
解决：
  1. 生产者和消费者使用相同的序列化器
  2. 检查依赖版本一致性
  3. 使用 Schema Registry
```

### 问题 2：反序列化漏洞

```
Java 序列化存在远程代码执行漏洞（CVE-2015-7501 等）
解决：
  1. 不使用 Java 序列化
  2. 使用 JSON / Protobuf / Avro
  3. 自定义反序列化校验
```

### 问题 3：Schema 演进不兼容

```
报错：SchemaNotCompatibleException
解决：
  1. 使用 Schema Registry
  2. 添加新字段而非修改
  3. 默认值填充
```

## 🎯 总结

**序列化核心要点**：
- ✅ 选择合适的序列化方案（推荐 Protobuf / Avro）
- ✅ 生产者和消费者必须兼容
- ✅ 自定义序列化器实现 Serializer/Deserializer
- ✅ Schema 管理（Schema Registry）
- ⚠️ 不推荐 Java 序列化（性能 + 安全）
- ⚠️ 序列化失败不可重试

**下一步：** [🎯 自定义分区器](/06-jdk/partitioner) — 业务路由策略

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
