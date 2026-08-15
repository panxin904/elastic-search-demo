---
title: 微服务数据库模式
---

# ☕ 微服务数据库模式

> 微服务架构下，**每个服务一个数据库**是核心原则。本章深入讨论各种数据库模式、CQRS、Saga 等企业级实战。

## 🎯 微服务数据库核心原则

### "每个服务一个数据库"（Database per Service）

```
❌ 反例：单体数据库（所有服务共享）
┌──────────┐
│   App    │
└─────┬────┘
      │
┌─────▼────────────────────────┐
│  Shared Database (mydb)         │
│  users, orders, products, ...   │
└────────────────────────────────┘
# 紧耦合：表 JOIN 跨服务，事务跨服务

✅ 推荐：每个服务独立数据库
┌──────────┐
│   App    │
└─────┬────┘
      │
   ┌──┴─────────────────────┐
   │                        │
┌──▼─────────┐  ┌────────────▼┐  ┌──────────────┐
│ 用户服务   │  │ 订单服务    │  │ 库存服务     │
│ user_db    │  │ order_db    │  │ inventory_db │
└────────────┘  └─────────────┘  └──────────────┘
# 松耦合：服务自治，独立部署
```

### 优势

- ✅ **服务自治**：独立部署、扩容、技术选型
- ✅ **故障隔离**：一个服务挂掉不影响其他
- ✅ **独立扩展**：订单库压力大，只扩订单服务
- ✅ **团队独立**：不同团队负责不同服务

### 挑战

- ❌ **跨服务 JOIN**：不能直接 SQL JOIN
- ❌ **跨服务事务**：需要分布式事务
- ❌ **数据一致性**：需要最终一致性
- ❌ **数据查询**：需要数据聚合（API 组合 / 事件溯源）

## 📊 5 种数据库模式

### 模式 1：每个服务一个数据库（最常用）

```
用户服务 → user_db
订单服务 → order_db
库存服务 → inventory_db
账户服务 → account_db
```

**特点：**
- ✅ 完全自治
- ✅ 独立扩容
- ❌ 跨服务查询困难

### 模式 2：共享数据库（不推荐）

```
所有服务共享一个数据库
- 优点：跨服务 JOIN 容易
- 缺点：紧耦合，违反微服务原则
```

### 模式 3：Saga 模式（长事务）

```
订单服务：创建订单
   ↓
库存服务：扣减库存
   ↓
账户服务：扣款
   ↓
完成
```

如果中途失败，按反向补偿：
- 账户扣款 → 退款
- 库存扣减 → 恢复

### 模式 4：CQRS（命令查询职责分离）

```
写模型（Command）：用户服务
读模型（Query）：查询服务（专用）
```

```
写：app → order_db（写入）
读：query → mongodb / es（专门为查询优化）
```

**特点：**
- ✅ 读写分离
- ✅ 读模型可独立扩展
- ❌ 数据同步（用事件）

### 模式 5：事件溯源（Event Sourcing）

```
不存当前状态，只存事件
- OrderCreated
- OrderPaid
- OrderShipped
- OrderDelivered

需要聚合事件得到当前状态
```

## 🎯 实战：微服务数据库设计

### 案例：电商系统

```
服务划分：
- 用户服务（user_db）
- 商品服务（product_db）
- 订单服务（order_db）
- 库存服务（inventory_db）
- 支付服务（payment_db）
- 物流服务（logistics_db）
- 评价服务（review_db）
- 通知服务（notification_db）
```

### 服务间通信

#### 同步调用（REST / gRPC）

```java
@Service
public class OrderService {
    
    @Autowired
    private RestTemplate restTemplate;
    
    public Order createOrder(OrderDTO dto) {
        // 1. 创建订单（写自己的库）
        orderMapper.insert(dto);
        
        // 2. 同步调用库存服务
        String url = "http://inventory-service/decrease";
        restTemplate.postForEntity(url, dto, Boolean.class);
        
        return dto;
    }
}
```

#### 异步事件（Kafka / RabbitMQ）

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private KafkaTemplate<String, String> kafka;
    
    public Order createOrder(OrderDTO dto) {
        // 1. 创建订单
        orderMapper.insert(dto);
        
        // 2. 发布事件（其他服务订阅）
        OrderCreatedEvent event = new OrderCreatedEvent(dto);
        kafka.send("order.created", JSON.toJSONString(event));
        
        return dto;
    }
}
```

```java
// 库存服务订阅
@KafkaListener(topics = "order.created")
public void onOrderCreated(String message) {
    OrderCreatedEvent event = JSON.parseObject(message, OrderCreatedEvent.class);
    inventoryMapper.decrease(event.getProductId(), event.getQuantity());
}
```

## 🔄 Saga 模式详解

### 两种编排方式

#### 1. 协调式 Saga（Orchestration）

```java
// 订单服务作为协调者
@Service
public class OrderSaga {
    
    public void createOrderSaga(OrderDTO dto) {
        // 1. 创建订单
        try {
            orderService.create(dto);
        } catch (Exception e) {
            // 触发补偿
            return;
        }
        
        // 2. 扣库存
        try {
            inventoryService.decrease(dto);
        } catch (Exception e) {
            // 补偿 1：取消订单
            orderService.cancel(dto);
            return;
        }
        
        // 3. 扣款
        try {
            accountService.debit(dto);
        } catch (Exception e) {
            // 补偿 2：恢复库存
            inventoryService.rollback(dto);
            // 补偿 1：取消订单
            orderService.cancel(dto);
        }
    }
}
```

**问题：** 业务代码复杂，每个步骤都要写补偿

#### 2. 编排式 Saga（Choreography）⭐⭐⭐

```
通过事件驱动，每个服务只关心自己的补偿
```

```java
// 订单服务：创建订单 + 发布事件
@Service
public class OrderService {
    public Order createOrder(OrderDTO dto) {
        orderMapper.insert(dto);
        kafka.send("order.created", JSON.toJSONString(dto));
        return dto;
    }
    
    // 补偿：监听支付失败
    @KafkaListener(topics = "payment.failed")
    public void onPaymentFailed(String message) {
        orderMapper.cancelByOrderNo(...);
    }
}

// 库存服务：监听订单创建 + 扣减
@KafkaListener(topics = "order.created")
public void onOrderCreated(String message) {
    inventoryMapper.decrease(...);
}

// 库存失败：发布库存失败事件
@KafkaListener(topics = "inventory.failed")
public void onInventoryFailed(String message) {
    // 补偿：恢复库存
    inventoryMapper.rollback(...);
}
```

**优势：**
- ✅ 服务之间松耦合
- ✅ 没有中心协调者
- ✅ 易于扩展

## 🔍 CQRS 详解

### 写模型（Command）

```java
// 写：操作核心业务表
@Entity
@Table(name = "orders")
public class Order {
    private Long id;
    private Long userId;
    private String status;
    private BigDecimal amount;
}

@Service
public class OrderCommandService {
    public void createOrder(Order order) {
        // 写 MySQL（强一致）
        orderMapper.insert(order);
        
        // 发布事件
        kafka.send("order.created", ...);
    }
}
```

### 读模型（Query）

```java
// 读：从专门的查询库查询（可为 NoSQL）
@Document(indexName = "orders")
public class OrderView {
    private Long id;
    private Long userId;
    private String userName;  // 反范式：冗余
    private String status;
    private BigDecimal amount;
}

@Service
public class OrderQueryService {
    @Autowired
    private ElasticsearchTemplate esTemplate;
    
    public List<OrderView> searchOrders(OrderQuery query) {
        // 从 ES 查（专为查询优化）
        return esTemplate.queryForList(...);
    }
}
```

### 数据同步（事件驱动）

```java
// 写完 MySQL 后，发送事件
// 消费者：更新 ES

@KafkaListener(topics = "order.created")
public void syncToES(String message) {
    OrderCreatedEvent event = JSON.parseObject(message, ...);
    esTemplate.save(toOrderView(event));
}
```

## 📊 实战：微服务数据查询

### 挑战：订单列表页

```
订单列表页需要：
- 订单信息（订单服务）
- 用户名（用户服务）
- 商品图片（商品服务）
```

### 方案 1：API 组合（推荐）

```java
@GetMapping("/orders")
public List<OrderListDTO> listOrders(@RequestParam Long userId) {
    // 1. 调用订单服务
    List<Order> orders = orderClient.listByUserId(userId);
    
    // 2. 批量获取用户信息
    Set<Long> userIds = orders.stream().map(Order::getUserId).collect(toSet());
    Map<Long, User> users = userClient.listByIds(userIds);
    
    // 3. 组装数据
    return orders.stream().map(o -> {
        OrderListDTO dto = new OrderListDTO();
        dto.setOrderId(o.getId());
        dto.setAmount(o.getAmount());
        dto.setUserName(users.get(o.getUserId()).getName());
        return dto;
    }).collect(toList());
}
```

**优点：** 简单  
**缺点：** 多次远程调用

### 方案 2：数据冗余（高性能）

```
订单表冗余用户名字段：
- 创建订单时，从用户服务获取名字，冗余到订单表
- 订单列表直接从订单服务查（无 JOIN）
```

```sql
-- order_db.orders 表
CREATE TABLE orders (
  id BIGINT PRIMARY KEY,
  user_id BIGINT,
  user_name VARCHAR(50),  -- 冗余字段
  amount DECIMAL(10, 2)
);
```

```java
// 创建订单时同步冗余字段
public void createOrder(OrderDTO dto) {
    // 1. 获取用户信息（实时）
    User user = userClient.getById(dto.getUserId());
    
    // 2. 写入订单（含冗余字段）
    order.setUserName(user.getName());
    orderMapper.insert(order);
}
```

**优点：** 查询快（单表）  
**缺点：** 数据冗余，需要同步

### 方案 3：宽表 / 视图（数仓）

```
用 ClickHouse / StarRocks / ES 构建宽表
- 把多服务的数据聚合到一个宽表
- 专门用于查询 / 报表
```

## 🛠️ 实战：服务间数据一致性

### 场景：订单创建后，库存要扣减

```
订单服务：写 orders 表（强一致）
库存服务：扣减 inventory（异步）
```

### 用本地消息表（最终一致性）

```java
// 订单服务
@Transactional
public Order createOrder(OrderDTO dto) {
    // 1. 写订单（本地事务）
    orderMapper.insert(dto);
    
    // 2. 写本地消息（同一个事务）
    LocalMessage msg = new LocalMessage();
    msg.setTopic("inventory.decrease");
    msg.setContent(JSON.toJSONString(dto));
    messageMapper.insert(msg);
    
    return dto;
}

// 后台任务：扫描消息
@Scheduled(fixedRate = 5000)
public void scan() {
    List<LocalMessage> msgs = messageMapper.selectList(
        Wrappers.<LocalMessage>lambdaQuery()
            .eq(LocalMessage::getStatus, 0)
            .last("LIMIT 100")
    );
    
    for (LocalMessage msg : msgs) {
        try {
            kafka.send(msg.getTopic(), msg.getContent());
            msg.setStatus(1);
            messageMapper.updateById(msg);
        } catch (Exception e) {
            // 重试
        }
    }
}
```

## 📊 数据迁移策略

### 双写阶段

```
新服务上线，但旧服务还在：
1. 旧服务：写老库
2. 新服务：写新库
3. 数据同步：定时任务从老库读，写到新库
4. 读切换：从新库读
5. 下线旧服务
```

### 渐进迁移

```
- 10% 流量走新服务
- 20%
- 50%
- 100%
- 下线旧服务
```

## 🎯 总结

**微服务数据库核心原则：**
- ✅ **每个服务一个数据库**（最重要）
- ✅ 服务之间通过 **API / 事件** 通信
- ✅ 避免跨服务 JOIN（用 API 组合）
- ✅ 跨服务事务用 **Saga / Seata**
- ✅ 数据冗余 + 最终一致性

**数据库模式选择：**
- ✅ 简单系统：每个服务一个库
- ✅ 复杂查询：CQRS（读写分离）
- ✅ 事件驱动：事件溯源
- ✅ 长事务：Saga

**跨服务通信：**
- ✅ 同步：REST / gRPC（强一致）
- ✅ 异步：Kafka / RabbitMQ（最终一致）
- ✅ 选择：业务实时性要求

**性能优化：**
- ✅ 数据冗余（避免远程 JOIN）
- ✅ 宽表（ES / OLAP）
- ✅ 本地缓存
- ✅ 异步处理

**下一步：** [🆔 分布式 ID 生成](/14-microservice/distributed-id) — 雪花算法、Leaf、UUID