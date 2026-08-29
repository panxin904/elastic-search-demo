---
title: 数据一致性
date: 2026-08-15  # date-auto-injected
---

# 🔄 分布式数据一致性

> 微服务架构下，**跨服务的数据一致性**是核心难题。本章深入讨论最终一致性、分布式锁、Canal 同步等实战方案。

## 🎯 数据一致性的挑战

```
传统单体应用：
- 一次数据库事务 = 强一致
- BEGIN → UPDATE → UPDATE → COMMIT
- ✅ 原子性

微服务架构：
- 订单服务（写 order_db）
- 库存服务（写 inventory_db）
- 账户服务（写 account_db）
- ❌ 跨服务无法用一个事务保证
```

**CAP 理论：**
- **C**onsistency（一致性）
- **A**vailability（可用性）
- **P**artition tolerance（分区容错）

**微服务必须在 C 和 A 之间二选一：**
- 选 C：强一致（如 Seata AT 模式）
- 选 A：最终一致（更常见）

## 📊 4 种一致性方案

| 方案 | 一致性 | 性能 | 复杂度 | 适用 |
|---|---|---|---|---|
| 分布式事务（Seata） | 强 | 中 | 中 | 金融 |
| 本地消息表 | 最终 | 高 | 中 | 异步 |
| 事务消息（RocketMQ） | 最终 | 高 | 中 | 异步 |
| **Canal 订阅 binlog** | 最终 | 高 | 中 | 数据同步 |
| 分布式锁 | 强 | 中 | 低 | 互斥场景 |

## 🚀 方案 1：本地消息表（最终一致性）

### 原理

```
┌──────────────────────────────────────┐
│ 业务事务（强一致）                      │
│   ├─ 写业务表（order_db.orders）         │
│   └─ 写本地消息表（order_db.local_msg）  │
│   ✅ 同时成功或同时失败                  │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 后台任务：扫描消息表                     │
│   ├─ 查 status=0 的消息                 │
│   ├─ 发到 MQ（Kafka/RabbitMQ）          │
│   └─ 标记 status=1                      │
└──────────────────────────────────────┘
              ↓
┌──────────────────────────────────────┐
│ 消费者（库存服务 / 账户服务）            │
│   ├─ 收到消息                           │
│   └─ 处理业务                           │
└──────────────────────────────────────┘
```

### 完整实现

```sql
-- 本地消息表
CREATE TABLE local_message (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  topic VARCHAR(100) NOT NULL COMMENT '消息主题',
  content TEXT NOT NULL COMMENT '消息内容（JSON）',
  status TINYINT NOT NULL DEFAULT 0 COMMENT '0=待发送 1=已发送 2=失败',
  retry_count INT NOT NULL DEFAULT 0 COMMENT '重试次数',
  next_retry_at DATETIME COMMENT '下次重试时间',
  error_msg VARCHAR(500) COMMENT '错误信息',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sent_at DATETIME COMMENT '发送时间',
  KEY idx_status_retry (status, next_retry_at)
) ENGINE=InnoDB COMMENT='本地消息表';
```

```java
@Data
@TableName("local_message")
public class LocalMessage {
    @TableId(type = IdType.AUTO)
    private Long id;
    
    private String topic;
    private String content;
    private Integer status;
    private Integer retryCount;
    private LocalDateTime nextRetryAt;
    private String errorMsg;
    private LocalDateTime createdAt;
    private LocalDateTime sentAt;
}
```

### 业务代码（同事务写消息）

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private LocalMessageMapper messageMapper;
    
    @Autowired
    private KafkaTemplate<String, String> kafka;
    
    // ✅ 写业务 + 写消息 在同一个事务
    @Transactional(rollbackFor = Exception.class)
    public Order createOrder(OrderDTO dto) {
        // 1. 写订单
        orderMapper.insert(dto);
        
        // 2. 写本地消息（同事务，保证一致）
        LocalMessage msg = new LocalMessage();
        msg.setTopic("inventory.decrease");
        msg.setContent(JSON.toJSONString(dto));
        msg.setStatus(0);  // 待发送
        msg.setNextRetryAt(LocalDateTime.now());
        messageMapper.insert(msg);
        
        return dto;
    }
}
```

### 后台任务（扫描并发送）

```java
@Component
@Slf4j
public class LocalMessageSender {
    
    @Autowired
    private LocalMessageMapper messageMapper;
    
    @Autowired
    private KafkaTemplate<String, String> kafka;
    
    // 每 5 秒扫描一次
    @Scheduled(fixedRate = 5000)
    public void scanAndSend() {
        // 1. 查询待发送的消息（最多 100 条）
        List<LocalMessage> messages = messageMapper.selectList(
            Wrappers.<LocalMessage>lambdaQuery()
                .eq(LocalMessage::getStatus, 0)
                .lt(LocalMessage::getRetryCount, 5)
                .le(LocalMessage::getNextRetryAt, LocalDateTime.now())
                .orderByAsc(LocalMessage::getId)
                .last("LIMIT 100")
        );
        
        for (LocalMessage msg : messages) {
            try {
                // 2. 发送到 Kafka
                kafka.send(msg.getTopic(), msg.getContent());
                
                // 3. 标记已发送
                msg.setStatus(1);
                msg.setSentAt(LocalDateTime.now());
                messageMapper.updateById(msg);
                
            } catch (Exception e) {
                // 4. 失败处理：重试
                int retry = msg.getRetryCount() + 1;
                msg.setRetryCount(retry);
                msg.setErrorMsg(e.getMessage());
                
                // 指数退避：1s, 2s, 4s, 8s, 16s
                long delay = (long) Math.pow(2, retry);
                msg.setNextRetryAt(LocalDateTime.now().plusSeconds(delay));
                
                if (retry >= 5) {
                    msg.setStatus(2);  // 标记失败（人工介入）
                }
                messageMapper.updateById(msg);
            }
        }
    }
}
```

### 消费者幂等性

```java
@KafkaListener(topics = "inventory.decrease")
public void onMessage(String message) {
    OrderDTO dto = JSON.parseObject(message, OrderDTO.class);
    
    // ✅ 幂等性：用业务单号去重
    if (inventoryMapper.existsByOrderNo(dto.getOrderNo())) {
        log.info("已处理过: {}", dto.getOrderNo());
        return;
    }
    
    inventoryMapper.decrease(dto);
}
```

## 🚀 方案 2：RocketMQ 事务消息

### 原理

```
RocketMQ 提供事务消息：
- 第一阶段：发送 half 消息（对消费者不可见）
- 第二阶段：本地事务执行
- 第三阶段：commit / rollback
- 如果第二阶段超时：RocketMQ 回查生产者
```

### 完整示例

```xml
<dependency>
    <groupId>org.apache.rocketmq</groupId>
    <artifactId>rocketmq-spring-boot-starter</artifactId>
    <version>2.2.2</version>
</dependency>
```

```java
// 生产者
@Service
@Slf4j
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private RocketMQTemplate rocketMQTemplate;
    
    public Order createOrder(OrderDTO dto) {
        // 1. 发送事务消息（half 消息）
        Message msg = MessageBuilder.withPayload(dto)
            .setHeader(RocketMQHeaders.TRANSACTION_ID, dto.getOrderNo())
            .build();
        
        TransactionSendResult result = rocketMQTemplate.sendMessageInTransaction(
            "order-topic", msg, dto
        );
        
        return dto;
    }
    
    // 2. 本地事务执行（订单入库）
    @RocketMQTransactionListener
    public void onLocalTransactionExecuted(Message msg, Object arg) {
        try {
            // 执行业务（写订单表）
            orderMapper.insert((OrderDTO) arg);
            
            // commit（消息对消费者可见）
            // 框架自动处理
        } catch (Exception e) {
            // rollback（消息被丢弃）
            throw e;
        }
    }
    
    // 3. 回查（如果第二阶段超时）
    @RocketMQTransactionListener
    public void checkLocalTransaction(Message msg) {
        OrderDTO dto = (OrderDTO) rocketMQTemplate.getMessagePayload(msg);
        Order order = orderMapper.selectByOrderNo(dto.getOrderNo());
        
        if (order != null) {
            // 已入库，commit
            return LocalTransactionState.COMMIT_MESSAGE;
        } else {
            // 未入库，rollback
            return LocalTransactionState.ROLLBACK_MESSAGE;
        }
    }
}
```

```java
// 消费者
@RocketMQMessageListener(topic = "order-topic", consumerGroup = "inventory-group")
public class InventoryConsumer {
    
    @Autowired
    private InventoryMapper inventoryMapper;
    
    public void onMessage(OrderDTO dto) {
        inventoryMapper.decrease(dto.getProductId(), dto.getQuantity());
    }
}
```

**优势：**
- ✅ 不需要本地消息表
- ✅ 自动回查机制
- ✅ 高性能（异步）

## 🚀 方案 3：Canal 订阅 binlog

### 原理

```
┌──────────┐     ┌─────────┐     ┌──────────┐
│   MySQL  │ ──→ │  Canal  │ ──→ │  MQ/ES   │
│ (主库)   │ binlog│ Server │     │ (消费者) │
└──────────┘     └─────────┘     └──────────┘
  写业务         监听变化         同步数据
```

### Canal 部署

```bash
# 下载
wget https://github.com/alibaba/canal/releases/download/canal-1.1.6/canal.deployer-1.1.6.tar.gz
tar -xzf canal.deployer-1.1.6.tar.gz
cd canal
```

```properties
# conf/example/instance.properties
canal.instance.mysql.slaveId = 1234
canal.instance.master.address = 127.0.0.1:3306
canal.instance.dbUsername = canal
canal.instance.dbPassword = canal
canal.instance.defaultDatabaseName = mydb
canal.instance.filter.regex = .*\\..*
```

```sql
-- MySQL 创建 Canal 专用用户
CREATE USER 'canal'@'%' IDENTIFIED BY 'canal';
GRANT SELECT, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'canal'@'%';
FLUSH PRIVILEGES;
```

```bash
# 启动 Canal
./bin/startup.sh
```

### Java 集成 Canal

```xml
<dependency>
    <groupId>com.alibaba.otter</groupId>
    <artifactId>canal.client</artifactId>
    <version>1.1.6</version>
</dependency>
```

```java
@Component
@Slf4j
public class CanalClient {
    
    @PostConstruct
    public void start() {
        // 创建 Canal 客户端
        CanalConnector connector = CanalConnectors.newSingleConnector(
            new InetSocketAddress("127.0.0.1", 11111),
            "example", "canal", "canal"
        );
        
        connector.connect();
        connector.subscribe(".*\\..*");
        
        // 持续消费
        while (true) {
            Message message = connector.getWithoutAck(100);
            if (message.getId() != -1) {
                handleMessage(message);
                connector.ack(message.getId());
            }
        }
    }
    
    private void handleMessage(Message message) {
        for (CanalEntry.Entry entry : message.getEntries()) {
            if (entry.getEntryType() == EntryType.ROWDATA) {
                CanalEntry.RowChange rowChange = CanalEntry.RowChange.parseFrom(entry.getStoreValue());
                
                for (CanalEntry.RowData rowData : rowChange.getRowDatasList()) {
                    // 事件类型
                    EventType eventType = rowChange.getEventType();
                    String tableName = entry.getHeader().getTableName();
                    
                    log.info("Table: {}, Event: {}, Before: {}, After: {}",
                        tableName, eventType, rowData.getBeforeColumnsList(), rowData.getAfterColumnsList());
                    
                    // 处理数据（同步到 ES / Redis / 其他库）
                    if (eventType == EventType.INSERT || eventType == EventType.UPDATE) {
                        syncToES(tableName, rowData.getAfterColumnsList());
                    }
                }
            }
        }
    }
}
```

## 🚀 方案 4：分布式锁

### Redisson 分布式锁

```xml
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.23.4</version>
</dependency>
```

```yaml
spring:
  redis:
    host: 127.0.0.1
    port: 6379
```

```java
@Configuration
public class RedissonConfig {
    
    @Bean
    public RedissonClient redissonClient() {
        Config config = new Config();
        config.useSingleServer().setAddress("redis://127.0.0.1:6379");
        return Redisson.create(config);
    }
}
```

### 实战：库存扣减防超卖

```java
@Service
public class InventoryService {
    
    @Autowired
    private RedissonClient redisson;
    
    @Autowired
    private InventoryMapper inventoryMapper;
    
    public boolean decrease(Long productId, Integer quantity) {
        String lockKey = "inventory:lock:" + productId;
        RLock lock = redisson.getLock(lockKey);
        
        try {
            // 尝试加锁（最多等 3 秒，锁 10 秒自动释放）
            if (!lock.tryLock(3, 10, TimeUnit.SECONDS)) {
                throw new RuntimeException("系统繁忙，请稍后重试");
            }
            
            // 业务逻辑
            Product product = inventoryMapper.selectById(productId);
            if (product.getStock() < quantity) {
                throw new RuntimeException("库存不足");
            }
            
            // 用 SQL 原子操作（避免并发超卖）
            int affected = inventoryMapper.decreaseAtomic(productId, quantity);
            if (affected == 0) {
                throw new RuntimeException("库存不足");
            }
            
            return true;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        } finally {
            // 释放锁
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}

// SQL 原子扣减（推荐）
@Update("UPDATE inventory SET stock = stock - #{qty} " +
        "WHERE id = #{id} AND stock >= #{qty}")
int decreaseAtomic(@Param("id") Long id, @Param("qty") Integer qty);
```

### 实战：防重复提交

```java
public boolean submitOrder(OrderDTO dto) {
    String lockKey = "order:submit:" + dto.getUserId() + ":" + dto.getProductId();
    RLock lock = redisson.getLock(lockKey);
    
    try {
        if (!lock.tryLock(2, 5, TimeUnit.SECONDS)) {
            return false;  // 重复提交
        }
        
        // 执行业务
        return orderService.createOrder(dto);
    } finally {
        if (lock.isHeldByCurrentThread()) {
            lock.unlock();
        }
    }
}
```

## 🚀 方案 5：Canal + MQ 数据同步（实战最常用）

### 场景

```
订单服务写 order_db（强一致）
↓
Canal 监听 binlog
↓
发送到 Kafka
↓
搜索服务 / 报表服务 / 缓存服务 订阅
```

```java
@Component
@Slf4j
public class CanalToKafka {
    
    @Autowired
    private KafkaTemplate<String, String> kafka;
    
    public void onBinlogEvent(CanalEntry.RowChange rowChange, String table) {
        for (CanalEntry.RowData rowData : rowChange.getRowDatasList()) {
            // 构造同步消息
            DataSyncMessage msg = new DataSyncMessage();
            msg.setTable(table);
            msg.setEvent(rowChange.getEventType().name());
            msg.setData(rowData.getAfterColumnsList());
            msg.setTimestamp(System.currentTimeMillis());
            
            // 发送到 Kafka
            kafka.send("data.sync." + table, JSON.toJSONString(msg));
        }
    }
}
```

```java
// 搜索服务：消费并同步到 ES
@KafkaListener(topics = "data.sync.orders")
public void syncToES(String message) {
    DataSyncMessage msg = JSON.parseObject(message, DataSyncMessage.class);
    
    if ("INSERT".equals(msg.getEvent()) || "UPDATE".equals(msg.getEvent())) {
        OrderES orderES = convert(msg.getData());
        esTemplate.save(orderES);
    } else if ("DELETE".equals(msg.getEvent())) {
        esTemplate.delete(...);
    }
}
```

## 📊 方案选型

| 业务场景 | 推荐方案 | 理由 |
|---|---|---|
| 异步通知 / 触发其他服务 | **本地消息表** | 简单可靠 |
| RocketMQ 生态 | **事务消息** | 自动回查 |
| 跨库数据同步 | **Canal 订阅 binlog** | 零侵入 |
| 库存防超卖 | **Redis 分布式锁 + 原子 SQL** | 强一致 |
| 订单创建（多服务） | **Seata Saga** | 适合长事务 |
| 数据双写 | **本地消息表 + Canal** | 双保险 |

## 🛠️ 实战：完整的最终一致性方案

### 案例：订单创建（多服务）

```
┌─────────┐     ┌─────────┐     ┌──────────┐
│ 订单服务 │ ──→ │  库存服务  │ ──→ │  账户服务  │
└────┬────┘     └─────┬────┘     └─────┬────┘
     │              │               │
     └──────────────┴───────────────┘
                    ↓
              ┌──────────┐
              │  Kafka   │
              └──────────┘
```

```java
// 订单服务
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private LocalMessageMapper messageMapper;
    
    @Transactional
    public Order createOrder(OrderDTO dto) {
        // 1. 写订单（强一致）
        orderMapper.insert(dto);
        
        // 2. 写本地消息（强一致）
        LocalMessage msg = new LocalMessage();
        msg.setTopic("inventory.decrease");
        msg.setContent(JSON.toJSONString(dto));
        messageMapper.insert(msg);
        
        return dto;
    }
}

// 库存服务
@KafkaListener(topics = "inventory.decrease")
public class InventoryConsumer {
    
    @Autowired
    private InventoryMapper inventoryMapper;
    
    @Transactional
    public void onMessage(OrderDTO dto) {
        // ✅ 幂等性
        if (inventoryMapper.existsByOrderNo(dto.getOrderNo())) return;
        
        // 业务：扣减库存
        int affected = inventoryMapper.decreaseAtomic(
            dto.getProductId(), dto.getQuantity()
        );
        
        if (affected == 0) {
            // 库存不足，发失败事件
            kafka.send("inventory.failed", JSON.toJSONString(dto));
        } else {
            // 成功，发下一步事件
            kafka.send("account.debit", JSON.toJSONString(dto));
        }
    }
}
```

### 失败处理

```java
@KafkaListener(topics = "inventory.failed")
public class onInventoryFailed(String message) {
    OrderDTO dto = JSON.parseObject(message, OrderDTO.class);
    
    // 补偿 1：取消订单
    orderService.cancel(dto.getOrderNo());
}
```

## 🎯 总结

**数据一致性方案选型：**
- ✅ **金融级**：Seata AT 模式（强一致）
- ✅ **异步通知**：本地消息表（最终一致）
- ✅ **RocketMQ 生态**：事务消息
- ✅ **跨库同步**：Canal 订阅 binlog
- ✅ **互斥场景**：Redis 分布式锁
- ✅ **订单流程**：Seata Saga

**最佳实践：**
- ✅ 业务 + 消息 在同一事务（本地消息表）
- ✅ 幂等性（业务单号去重）
- ✅ 重试 + 指数退避
- ✅ 失败告警 + 人工介入
- ✅ 监控消息堆积

**Canal 优势：**
- ✅ 零侵入（不改业务代码）
- ✅ 实时同步（毫秒级）
- ✅ 完整数据变更历史
- ✅ 适合数据双写 / 异构同步

**下一步：** [🌀 Saga 模式详解](/14-microservice/saga-pattern) — 跨服务长事务的编排