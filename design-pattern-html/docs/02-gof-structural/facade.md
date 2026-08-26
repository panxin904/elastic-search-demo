---
title: Facade 外观模式
description: 子系统统一高层接口 + Spring JdbcTemplate + 第三方 SDK 封装 + API Gateway
---

# Facade 外观模式

## 核心问题

子系统中存在多个相互关联的类（典型如：JDBC 的 Connection/Statement/ResultSet），客户端直接使用这些类需要写大量样板代码（获取连接 / 创建 Statement / 设置参数 / 执行 / 解析结果 / 关闭资源）。

**真实场景**：
- JDBC：Connection/Statement/ResultSet 模板代码
- 第三方 SDK（支付 / OAuth / 短信）：多个 API 调用拼成业务
- 数据库 ORM（MyBatis / Hibernate）：把 SQL 隐藏在方法后面
- 微服务 API Gateway：把多个下游服务聚合成一个接口

## 核心思想

为子系统中的一组接口提供一个**统一的高层接口**，使子系统更易使用。

**关键点**：
- Facade 不限制客户端使用子系统（保留高级用法）
- Facade 只是「推荐入口」，简化 80% 场景
- Facade 不增加新功能，只是把现有功能编排

## 实战：Spring JdbcTemplate

```java
// ❌ 没有 JdbcTemplate 时，JDBC 模板代码
try (Connection conn = dataSource.getConnection()) {
    PreparedStatement ps = conn.prepareStatement(
        "SELECT name FROM users WHERE id = ?");
    ps.setLong(1, userId);
    ResultSet rs = ps.executeQuery();
    if (rs.next()) {
        String name = rs.getString("name");
        // 用完 rs / ps / conn 都得 try-with-resources
    }
}

// ✅ JdbcTemplate 一行搞定
String name = jdbcTemplate.queryForObject(
    "SELECT name FROM users WHERE id = ?",
    String.class,
    userId);
```

`JdbcTemplate` 帮你处理了：
1. 获取连接（从 DataSource）
2. 创建 PreparedStatement
3. 设置参数（用 PreparedStatementSetter）
4. 执行 SQL
5. 映射 ResultSet 到对象（用 RowMapper）
6. 关闭连接 / Statement / ResultSet
7. 异常翻译（SQLException → DataAccessException）

## MyBatis Mapper 接口

```java
// 定义接口
public interface UserMapper {
    @Select("SELECT * FROM users WHERE id = #{id}")
    User findById(long id);

    @Insert("INSERT INTO users(name, age) VALUES(#{name}, #{age})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    void insert(User user);
}

// 用法
User user = userMapper.findById(1L);
userMapper.insert(newUser);
```

MyBatis 在运行时生成 Mapper 的代理实现（Facade），把 JDBC 调用隐藏起来。

## 实战：支付 SDK 封装

```typescript
// 第三方支付 SDK（支付宝）
class AlipaySDK {
    createOrder(params: any): Promise<any> { /* ... */ }
    queryOrder(orderId: string): Promise<any> { /* ... */ }
    refund(orderId: string, amount: number): Promise<any> { /* ... */ }
}

// 第三方支付 SDK（微信支付）
class WechatPaySDK {
    unifiedOrder(params: any): Promise<any> { /* ... */ }
    orderQuery(orderId: string): Promise<any> { /* ... */ }
    refund(orderId: string, amount: number): Promise<any> { /* ... */ }
}

// Facade：业务统一接口
interface PaymentFacade {
    create(order: Order): Promise<PaymentResult>;
    query(orderId: string): Promise<PaymentStatus>;
    refund(orderId: string, amount: number): Promise<RefundResult>;
}

class PaymentService implements PaymentFacade {
    constructor(
        private alipay: AlipaySDK,
        private wechat: WechatPaySDK,
        private logger: Logger
    ) {}

    async create(order: Order): Promise<PaymentResult> {
        // 业务封装：选择通道 + 记录日志 + 异常处理
        const channel = order.channel;  // 'alipay' or 'wechat'
        if (channel === 'alipay') {
            return this.alipay.createOrder({
                out_trade_no: order.id,
                total_amount: order.amount,
                subject: order.title,
            });
        }
        return this.wechat.unifiedOrder({
            out_trade_no: order.id,
            total_fee: order.amount * 100,
            body: order.title,
        });
    }

    // query / refund 类似封装
}
```

业务方只依赖 `PaymentFacade`，不用知道底层是支付宝还是微信的 SDK。

## 实战：API Gateway

微服务的 API Gateway 是宏观层面的 Facade：

```typescript
// 4 个微服务，每个都有自己的 REST API
class OrderService { createOrder(req): Promise<Order> { /* ... */ } }
class PaymentService { charge(req): Promise<PaymentResult> { /* ... */ } }
class InventoryService { reserve(items): Promise<void> { /* ... */ } }
class ShippingService { createShipment(req): Promise<Shipment> { /* ... */ } }

// API Gateway（Facade）：聚合成一个端点
@Controller('/checkout')
class CheckoutGateway {
    constructor(
        private order: OrderService,
        private payment: PaymentService,
        private inventory: InventoryService,
        private shipping: ShippingService,
    ) {}

    @Post('/')
    async checkout(@Body() req: CheckoutRequest) {
        // 串联多个微服务
        const order = await this.order.create(req);
        await this.payment.charge({ orderId: order.id, amount: order.total });
        await this.inventory.reserve(order.items);
        const shipment = await this.shipping.createShipment({ orderId: order.id });

        return { orderId: order.id, shipmentId: shipment.id };
    }
}
```

客户端只需要调 `POST /checkout`，不用知道背后有 4 个微服务。

## 适用边界

✅ **使用场景**：
- 封装第三方 SDK（多个调用聚合成一个方法）
- 简化子系统 API（JDBC / 文件系统 / 进程）
- API Gateway（微服务聚合）
- 老系统现代化（保留旧接口，内部用新实现）

❌ **避免场景**：
- 子系统非常简单（直接用更清晰）
- 客户端需要精细控制每个子系统（Facade 不应成为限制）
- 把所有业务逻辑都堆在 Facade（变成 God Class）

🔄 **与相关模式区别**：
- **Facade**：简化接口（多个 → 一个）
- **Adapter**：转换接口（不兼容 → 兼容）
- **Mediator**：集中对象间交互（双向解耦）

💡 **最佳实践**：
- Facade 是「推荐入口」，不限制使用子系统
- 多个子系统聚合到 Facade 时，注意性能（并发 / 异步）
- Facade 方法应该和业务用例对应（一个业务 = 一个 Facade 方法）


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料
<!-- auto-enrich:do-not-edit -->
