---
title: 生产消费调试
---

# ✉️ 生产消费调试

> 命令行生产消费工具是 Kafka 调试的利器。本章详解 kafka-console-producer.sh 和 kafka-console-consumer.sh 的所有用法。

## ✉️ 命令行生产者

### 基础生产

```bash
# 最简单的生产（无 key）
kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders

# > 启动后进入交互模式
# > 输入消息，回车发送
> order-001 alice 99.9
> order-002 bob 88.8
> Ctrl+D 退出
```

### 带 Key 的生产

```bash
# 指定 Key（保证相同 key 进入同一 partition）
kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --property "parse.key=true" \
    --property "key.separator=:"

# 输入格式：key:value
> user123:order-001 alice 99.9
> user123:order-002 alice 88.8
# 这两条消息会进入同一个 partition（hash(key) % partitions）
```

### 批量生产（从文件）

```bash
# 准备消息文件
cat > messages.txt << EOF
{"id": 1, "name": "alice", "amount": 99.9}
{"id": 2, "name": "bob", "amount": 88.8}
{"id": 3, "name": "carol", "amount": 77.7}
EOF

# 通过管道批量发送
cat messages.txt | kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders
```

### 高级参数

```bash
# 指定 acks 级别
kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --producer-property "acks=all"

# 启用压缩
kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --producer-property "compression.type=lz4"

# 限速（每秒 100 条）
kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --producer-property "max.in.flight.requests.per.connection=1"

# 设置客户端 ID
kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --producer-property "client.id=my-producer"
```

## 📥 命令行消费者

### 基础消费

```bash
# 从头消费所有消息
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning

# 实时消费（从最新开始）
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders

# 限制消费数量
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --max-messages 10 \
    --from-beginning

# 限制超时
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --timeout-ms 5000 \
    --from-beginning
```

### 指定消费者组

```bash
# 指定 group（offset 持久化到 group）
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --group order-processor \
    --from-beginning

# group 第一次消费后，再次启动会从上次 offset 继续
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --group order-processor
```

### 显示详细信息

```bash
# 显示 Key
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning \
    --property "print.key=true"

# 显示 Key + Partition + Offset
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning \
    --property "print.key=true" \
    --property "print.partition=true" \
    --property "print.offset=true"

# 显示时间戳
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning \
    --property "print.timestamp=true"

# 完整格式（带分隔符）
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning \
    --property "print.key=true" \
    --property "print.partition=true" \
    --property "print.offset=true" \
    --property "print.timestamp=true" \
    --property "key.separator= | " \
    --property "line.separator= || "
```

### 指定 Partition 消费

```bash
# 消费指定 partition（--partition）
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partition 0 \
    --from-beginning

# 指定多个 partition
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partition 0,1,2 \
    --from-beginning

# 指定 offset 范围
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partition 0 \
    --offset 100 \
    --max-messages 10
```

## 🔧 调试技巧

### 场景 1：验证消息是否真的写入了

```bash
# 1. 生产消息
echo "test-msg-1" | kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders

# 2. 验证消费（从最新开始）
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning \
    --max-messages 5

# 应该看到：test-msg-1
```

### 场景 2：检查消息是否丢失

```bash
# 1. 查看生产者发送量
kafka-console-producer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --producer-property "acks=all"  # 确保写入成功

# 2. 计数验证（生产者）
... 等待生产完成

# 3. 计数验证（消费者）
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning | wc -l
```

### 场景 3：调试分区分配

```bash
# 生产带 key 的消息，看消息分布
for i in {1..100}; do
    echo "user$i:msg-$i" | kafka-console-producer.sh \
        --bootstrap-server localhost:9092 \
        --topic orders \
        --property "parse.key=true" \
        --property "key.separator=:" \
        --max-messages 1 2>/dev/null
done

# 查看各 partition 的消息数
kafka-console-consumer.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --from-beginning \
    --property "print.partition=true" | sort | uniq -c | head
```

### 场景 4：性能基准测试

```bash
# 用 kafka-producer-perf-test.sh 测试吞吐
kafka-producer-perf-test.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --num-records 1000000 \
    --record-size 1024 \
    --throughput -1 \
    --producer-props \
        acks=all \
        batch.size=65536 \
        linger.ms=10

# 输出：
# 1000000 records sent, 234567.89 records/sec (229.06 MB/sec)
# 1234 ms total time
```

### 场景 5：消费性能测试

```bash
# 用 kafka-consumer-perf-test.sh
kafka-consumer-perf-test.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --messages 1000000 \
    --threads 1 \
    --group perf-test

# 输出：
# start.time, end.time, data.consumed.in.MB, MB.sec, data.consumed.in.nMsg, nMsg.sec, rebalance.time.ms, fetch.time.ms, fetch.MB.sec, records.count
# 2024-07-15 10:00:00, 2024-07-15 10:01:00, 1024.00, 17.07, 1000000, 16666.67, 100, 59900, 17.07, 1000000
```

## 🛠️ Kafka Playground（浏览器版）

<ClientOnly>
  <KafkaPlayground />
</ClientOnly>

试试用 Playground 执行 CLI 命令，实时观察消息流转：

```bash
CREATE TOPIC orders 3 2
LIST TOPICS
PRODUCE orders "order-001 alice 99.9"
PRODUCE orders "order-002 bob 88.8"
PRODUCE orders "order-003 carol 77.7"
CONSUMER orders GROUP order-processor 5
```

## 📊 输出格式

### 默认输出

```
value1
value2
value3
```

### 带 Key 输出

```
key1 : value1
key2 : value2
key3 : value3
```

### 完整格式

```
CreateTime:1698000000000	Partition:0	Offset:0	Key:user1 : value1
CreateTime:1698000001000	Partition:1	Offset:0	Key:user2 : value2
CreateTime:1698000002000	Partition:2	Offset:0	Key:user3 : value3
```

## ⚠️ 常见问题

### 问题 1：消费不到消息

```
原因：
  1. topic 为空
  2. group 已消费过（用 --from-beginning）
  3. 从错误的 broker 连接
解决：
  1. 确认 producer 发送成功
  2. 加 --from-beginning
  3. 检查 --bootstrap-server
```

### 问题 2：Key 没生效

```
原因：忘加 --property "parse.key=true"
解决：
  kafka-console-producer.sh ... \
      --property "parse.key=true" \
      --property "key.separator=:"
```

### 问题 3：中文乱码

```
原因：终端编码不是 UTF-8
解决：
  export LANG=en_US.UTF-8
  或
  export LC_ALL=en_US.UTF-8
```

## 🎯 总结

**生产消费调试核心要点**：
- ✅ kafka-console-producer.sh 交互式生产
- ✅ kafka-console-consumer.sh 实时消费
- ✅ 支持 Key、Partition、Offset 详细查看
- ✅ 批量生产从文件（管道）
- ✅ 性能测试工具 perf-test.sh
- ⚠️ 中文消息注意终端编码
- ⚠️ from-beginning 仅在 group 第一次消费生效

**下一步：** [👥 消费者组](/03-cli/consumer-group) — Group 管理命令详解
