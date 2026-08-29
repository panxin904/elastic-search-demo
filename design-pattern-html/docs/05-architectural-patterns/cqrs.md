---
title: CQRS 命令查询分离
description: 读写模型分离 + Axon / EventStoreDB / Kafka Streams + 4 种架构演进
---

# CQRS 命令查询分离

## 核心问题

传统 CRUD 模型用同一张表同时承担读和写：
- **读写竞争**：写加锁影响读性能
- **模型冲突**：写模型要范式化，读模型要反范式化
- **扩展困难**：报表查询（OLAP）跟在线交易（OLTP）放一个库不合理
- **业务耦合**：读和写共享业务模型，难以独立优化

## 核心思想

把**写操作（Command）**和**读操作（Query）**分离到不同的模型 / 服务 / 数据库上。

**关键点**：
- Command 端：写模型（范式化、事务强一致）
- Query 端：读模型（反范式化、查询优化）
- 两者通过**事件**同步（Event-Driven）

## 4 种架构演进

```text
Level 1：单库读写分离（最简单）
┌─────────────────┐
│   Application   │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  MySQL (主从)    │ ← 主库写，从库读
└─────────────────┘

Level 2：单服务读写分离（代码层）
┌─────────────────┐
│   Application   │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Command │ │  Query  │  ← 同库不同表 / 视图
│  Side   │ │  Side   │
└─────────┘ └─────────┘

Level 3：CQRS（不同模型）
┌─────────────────┐
│   Application   │
└────────┬────────┘
         │
    ┌────┴────────────┐
    ▼                 ▼
┌─────────┐    ┌─────────┐
│ Command │    │  Query  │  ← 不同表 / 不同数据库
│  Side   │───→│  Side   │  ← 通过事件同步
│(MySQL)  │    │(ElasticSearch)│
└─────────┘    └─────────┘

Level 4：CQRS + Event Sourcing（最强）
┌─────────────────┐
│   Application   │
└────────┬────────┘
         │
    ┌────┴────────────┐
    ▼                 ▼
┌─────────┐    ┌─────────┐
│ Command │    │  Query  │
│  Side   │    │  Side   │
│(Event   │    │(Elastic │
│ Store)  │───→│ Search) │
└─────────┘    └─────────┘
   │ ↑
   │ │ 事件溯源
   ▼ │
┌─────────────────┐
│ Event Stream    │
└─────────────────┘
```

## 实战：Axon Framework

```java
// 命令端：处理写请求
@Aggregate
public class Order {
    @AggregateIdentifier
    private String orderId;
    private OrderStatus status;

    @CommandHandler
    public Order(CreateOrderCommand cmd) {
        // 业务校验
        if (cmd.getItems().isEmpty()) throw new IllegalArgumentException("empty items");
        // 产生事件（不直接修改状态）
        apply(new OrderCreatedEvent(cmd.getOrderId(), cmd.getItems()));
    }

    @EventSourcingHandler
    public void on(OrderCreatedEvent event) {
        this.orderId = event.getOrderId();
        this.status = OrderStatus.PENDING;
    }
}

// 事件投影：把事件流同步到读库
@EventHandler
public class OrderProjection {
    @EventHandler
    public void on(OrderCreatedEvent event, EntityManager em) {
        OrderView view = new OrderView(event.getOrderId(), event.getTotal(), OrderStatus.PENDING);
        em.persist(view);  // 写入读库（MySQL / ES）
    }

    @EventHandler
    public void on(OrderPaidEvent event, EntityManager em) {
        OrderView view = em.find(OrderView.class, event.getOrderId());
        view.setStatus(OrderStatus.PAID);
    }
}

// 查询端：处理读请求
@QueryHandler
public OrderView handle(GetOrderQuery query) {
    return entityManager.find(OrderView.class, query.getOrderId());
}
```

## Java + Spring 手写简易 CQRS

```java
// Command 端：写服务
@Service
@Transactional
public class OrderCommandService {
    @Autowired private OrderRepository writeRepo;
    @Autowired private EventPublisher events;

    public void create(CreateOrderCommand cmd) {
        Order order = Order.create(cmd);
        writeRepo.save(order);
        events.publish(new OrderCreatedEvent(order));
    }

    public void pay(PayOrderCommand cmd) {
        Order order = writeRepo.findById(cmd.getOrderId()).orElseThrow();
        order.pay();
        writeRepo.save(order);
        events.publish(new OrderPaidEvent(order));
    }
}

// 事件投影：异步同步到读库
@Component
public class OrderProjection {
    @Autowired private OrderReadRepository readRepo;

    @EventListener
    @Async
    public void on(OrderCreatedEvent event) {
        readRepo.save(OrderView.from(event.getOrder()));
    }

    @EventListener
    @Async
    public void on(OrderPaidEvent event) {
        OrderView view = readRepo.findById(event.getOrder().getId()).orElseThrow();
        view.markPaid();
        readRepo.save(view);
    }
}

// Query 端：读服务
@Service
public class OrderQueryService {
    @Autowired private OrderReadRepository readRepo;

    public OrderView findById(String id) {
        return readRepo.findById(id).orElseThrow();
    }

    public Page<OrderView> findByUser(long userId, Pageable pageable) {
        return readRepo.findByUser(userId, pageable);  // 反范式化 + 索引优化
    }
}
```

## 读模型选择

不同读模型适合不同场景：

| 读模型 | 适用 | 案例 |
|---|---|---|
| **MySQL 反范式化** | 简单查询、报表 | 订单详情、用户信息 |
| **Elasticsearch** | 全文检索、复杂查询 | 商品搜索、日志分析 |
| **ClickHouse** | OLAP 聚合 | 统计、报表、UV/DAU |
| **Redis** | 缓存、排行榜 | 实时数据、热数据 |
| **MongoDB** | 半结构化数据 | 用户画像、商品属性 |

读模型选择原则：
- 写一次查多次 → 反范式化（MySQL 宽表）
- 全文搜索 → Elasticsearch
- 大量聚合 → ClickHouse
- 实时性要求高 → Redis

## 适用边界

✅ **使用场景**：
- 读写比例严重失衡（1:1000+）
- 读写模型差异巨大（OLTP + OLAP）
- 多查询数据源（不同业务用不同读模型）
- 高并发读（读写分离 + 多级缓存）

❌ **避免场景**：
- 简单 CRUD（直接读写同库）
- 团队无 Event Sourcing 经验
- 业务规模小（增加复杂度无收益）

🔄 **演进路径**：
1. 单库读写分离
2. 单服务读写分离（代码层）
3. CQRS（不同读模型）
4. CQRS + Event Sourcing（事件溯源）

💡 **最佳实践**：
- 事件是连接 Command / Query 的桥梁
- 读模型可以最终一致（异步投影）
- 投影要幂等（可能被重复消费）
- 监控读写延迟差异（设置 SLA）

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
