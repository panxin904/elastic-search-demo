---
title: 消费者组
date: 2026-08-15  # date-auto-injected
---

# 👥 消费者组

> kafka-consumer-groups.sh 是 Kafka 运维的瑞士军刀，可以查看 lag、重置 offset、管理 group 等。

![Kafka Rebalance Protocol](/kafka-rebalance-protocol.svg)

## 🎯 查看消费者组

### 列出所有 Group

```bash
# 列出所有消费者组
kafka-consumer-groups.sh --list --bootstrap-server localhost:9092

# 输出：
# order-processor
# payment-processor
# audit-consumer
# __consumer_offsets  # 内部 group（存储 offset）
```

### 查看 Group 详情

```bash
# 查看 group 消费进度（最常用）
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor

# 输出示例：
# GROUP            TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG    CONSUMER-ID     HOST            CLIENT-ID
# order-processor  orders   0          12345           12400           55     consumer-1-abc  /192.168.1.10   consumer-1
# order-processor  orders   1          67890           67900           10     consumer-1-abc  /192.168.1.10   consumer-1
# order-processor  orders   2          1234            1300            66     consumer-1-abc  /192.168.1.10   consumer-1
```

字段说明：
- `CURRENT-OFFSET`：消费者当前提交的 offset
- `LOG-END-OFFSET`：分区最新消息的 offset
- `LAG`：消息积压（CURRENT-OFFSET 与 LOG-END-OFFSET 之差）
- `CONSUMER-ID`：消费者 ID
- `HOST`：消费者所在主机

### 查看 Lag 排行榜

```bash
# 按 LAG 排序，找到积压最多的 group
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --all-groups | sort -k 6 -n -r | head -10

# 输出：LAG 最大的 10 个 group
```

### 查看 Group 成员

```bash
# 查看 group 成员和分区分配
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --members

# 输出：
# GROUP            CONSUMER-ID           HOST            CLIENT-ID       #PARTITIONS
# order-processor  consumer-1-abc        /192.168.1.10   consumer-1      2
# order-processor  consumer-2-def        /192.168.1.11   consumer-2      1
```

### 查看 Group 状态

```bash
# 查看 group 状态
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --state

# 输出：
# GROUP            COORDINATOR (ID)      STATE
# order-processor  1 (node1:9092)        Stable
# 
# 状态说明：
# - Stable：正常运行
# - PreparingRebalance：正在重新分配
# - CompletingRebalance：完成重新分配
# - Empty：没有活跃消费者
```

## 🔄 重置 Offset

### 重置到指定位置

```bash
# 重置到最早（从头开始消费）
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-earliest \
    --execute

# 重置到最新（跳过所有历史消息）
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-latest \
    --execute

# 重置到指定 offset
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-offset 100 \
    --execute

# 重置到指定时间（回溯到某个时间点）
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-datetime 2024-07-15T10:00:00.000 \
    --execute

# 按 partition 分别重置
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-offset 100:200:300 \
    --execute

# 分区 0 重置到 100
# 分区 1 重置到 200
# 分区 2 重置到 300
```

### 重置模式

```bash
# --execute：立即执行
# --dry-run：仅测试，不执行
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-earliest \
    --dry-run  # 仅预览，不执行

# 输出会显示将要重置的 offset
```

### 重要：重置 Offset 的限制

```
⚠️ 重置 Offset 仅在以下条件满足时生效：
  1. 消费者组没有任何活跃消费者
  2. 消费者组是 Empty 状态
  3. 重置后立即启动消费者

⚠️ 否则需要：
  1. 停止所有消费者
  2. 执行重置命令
  3. 重启消费者
```

## 🗑️ 删除消费者组

```bash
# 删除单个 group（必须先停止消费者）
kafka-consumer-groups.sh --delete \
    --bootstrap-server localhost:9092 \
    --group order-processor

# 确认：
# Deleting group 'order-processor'
# Are you sure? (yes/no)
# 输入 yes 确认

# 批量删除多个 group
for group in old-group-1 old-group-2 old-group-3; do
    kafka-consumer-groups.sh --delete \
        --bootstrap-server localhost:9092 \
        --group $group
done
```

## 🔧 高级用法

### 监控消息积压（重要！）

```bash
# 1. 定时检查 lag 并告警
cat > check-lag.sh << 'EOF'
#!/bin/bash
THRESHOLD=10000
BROKER="localhost:9092"

lag=$(kafka-consumer-groups.sh --describe \
    --bootstrap-server $BROKER \
    --group order-processor | \
    awk 'NR>1 {sum+=$5} END {print sum}')

if [ "$lag" -gt "$THRESHOLD" ]; then
    echo "ALERT: order-processor lag=$lag exceeds $THRESHOLD"
    # 发送告警（钉钉 / 邮件 / 企业微信）
fi
EOF

chmod +x check-lag.sh

# 2. 加入 crontab 每分钟检查
crontab -e
# * * * * * /path/to/check-lag.sh >> /var/log/kafka-lag.log
```

### 查看 Group 偏移量（详细）

```bash
# 查看 group 在每个 partition 的 offset
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --offsets

# 输出：
# GROUP            TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG    MEMBER-ID       CLIENT-ID
# order-processor  orders   0          12345           12400           55     consumer-1-...  consumer-1
```

### 平衡 Group 分区

```bash
# 重新分配分区（让所有 partition 均匀分布）
kafka-reassign-partitions.sh \
    --bootstrap-server localhost:9092 \
    --reassignment-json-file reassign.json \
    --execute

# 或手动指定
cat > reassign.json << EOF
{
  "version": 1,
  "partitions": [
    {"topic": "orders", "partition": 0, "replicas": [1, 2]},
    {"topic": "orders", "partition": 1, "replicas": [2, 3]},
    {"topic": "orders", "partition": 2, "replicas": [3, 1]}
  ]
}
EOF
```

### 查看 Group 提交记录

```bash
# 查看 group 的 offset 提交记录（__consumer_offsets topic）
# 这种方式不推荐（内部细节），建议用 --describe
```

## 🛠️ 实战场景

### 场景 1：消费者处理慢导致积压

```bash
# 1. 查看 lag
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor

# 发现 lag=10000+

# 2. 处理方案：
# a) 增加消费者实例（横向扩展）
# b) 增加每个消费者的批量拉取
# c) 优化消费者处理逻辑
# d) 检查消费者机器资源（CPU、内存、网络）
```

### 场景 2：消费者错误导致卡住

```bash
# 1. 查看消费者实例
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --members

# 发现 1 个消费者长期不消费

# 2. 处理方案：
# a) 重启消费者
# b) 查看消费者日志（为什么挂起）
# c) 检查 partition 分配（可能所有 partition 都分配给了挂的 consumer）
```

### 场景 3：重新消费历史消息

```bash
# 1. 停止消费者
kubectl scale deployment order-consumer --replicas=0

# 2. 重置 offset
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-datetime 2024-07-15T00:00:00.000 \
    --execute

# 3. 重启消费者
kubectl scale deployment order-consumer --replicas=3

# 4. 监控 lag 减小
watch -n 5 "kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor"
```

### 场景 4：删除历史 Group

```bash
# 1. 列出所有 group
kafka-consumer-groups.sh --list --bootstrap-server localhost:9092

# 2. 确认无用 group
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group old-group-1

# 3. 删除
kafka-consumer-groups.sh --delete \
    --bootstrap-server localhost:9092 \
    --group old-group-1
```

## ⚠️ 常见问题

### 问题 1：group 在 rebalance 中

```
报错：GroupCoordinatorNotAvailableException
解决：
  1. 等待 rebalance 完成（通常 5-10 秒）
  2. 检查 GroupCoordinator 状态
  3. 查看 broker 日志
```

### 问题 2：重置 Offset 失败

```
报错：ResetOffset operation failed
原因：
  1. group 有活跃消费者
  2. offset 越界（小于 earliest 或大于 latest）
解决：
  1. 停止所有消费者
  2. 确认 offset 在合法范围内
```

### 问题 3：Lag 一直增长

```
原因：
  1. 生产速度 > 消费速度
  2. 消费者处理慢
  3. 网络问题
解决：
  1. 扩容消费者
  2. 增加 partition 数
  3. 优化消费逻辑
```

## 🎯 总结

**消费者组管理核心要点**：
- ✅ kafka-consumer-groups.sh 是核心工具
- ✅ --describe 查看 lag（监控关键）
- ✅ --reset-offsets 重置 offset（谨慎使用）
- ✅ --delete 删除 group
- ⚠️ 重置 offset 必须停掉所有消费者
- ⚠️ 删除 group 不可逆

**下一步：** [🎯 生产者原理](/04-producer/principle) — Producer 内部机制


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
