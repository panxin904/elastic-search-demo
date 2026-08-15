---
title: 消息队列 MQ
---

# 消息队列

消息队列实现异步解耦、削峰填谷、最终一致性。

## RabbitMQ vs Kafka

| | RabbitMQ | Kafka |
|---|---|---|
| 定位 | 消息代理 | 分布式流平台 |
| 吞吐量 | 万级/秒 | 百万级/秒 |
| 消息可靠性 | 高（ACK确认） | 高（副本机制） |
| 适用场景 | 业务异步解耦 | 日志收集、流处理、大数据 |
| 协议 | AMQP | 自定义 |

## Spring Boot 集成 RabbitMQ

```java
// 生产者
@Autowired
private RabbitTemplate rabbitTemplate;

public void sendOrderCreated(Order order) {
    rabbitTemplate.convertAndSend(
        "order.exchange",    // 交换机
        "order.created",     // 路由键
        order
    );
}

// 消费者
@RabbitListener(queues = "order.created.queue")
public void handleOrderCreated(Order order) {
    // 处理订单创建后的异步操作
    // 1. 发短信通知
    // 2. 更新统计
    // 3. 同步到 ES
}
```

## 常见场景

| 场景 | 说明 |
|---|---|
| 异步处理 | 下单后发短信/邮件（不阻塞主流程） |
| 削峰填谷 | 秒杀时先入队列，慢慢消费 |
| 解耦 | 订单服务不直接调通知服务 |
| 最终一致性 | 分布式事务的消息补偿方案 |
| 数据同步 | 数据库变更同步到 ES/Cache |

## 消息可靠性

| 阶段 | 保障机制 |
|---|---|
| 生产者发送 | confirm 确认模式 |
| Broker 存储 | 持久化 + 镜像队列 |
| 消费者处理 | 手动 ACK，处理完再确认 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="message-queue" :height="400" />
