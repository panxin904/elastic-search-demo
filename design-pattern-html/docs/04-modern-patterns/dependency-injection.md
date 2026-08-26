---
title: 依赖注入 DI
description: 解耦对象创建 + Spring IoC / NestJS Provider / Go Wire + 构造器 vs Setter vs 字段注入
---

# 依赖注入 DI

## 核心问题

业务对象 A 需要使用对象 B，但 A 不应该自己 `new B()`（编译期耦合）。应该由外部容器把 B 注入到 A。

**问题场景**：
- `OrderService` 直接 `new PaymentService()` → 单测无法替换 mock
- `UserController` 直接 `new UserRepository()` → 难以切换数据库实现
- `NotificationService` 直接 `new EmailSender()` → 难以切换到短信

## 控制反转（IoC）

**传统流程**：
```java
// OrderService 自己创建依赖（控制权在 OrderService）
public class OrderService {
    private PaymentService payment = new PaymentService();  // 硬编码
    private InventoryService inventory = new InventoryService();
}
```

**IoC 流程**：
```java
// 容器创建依赖并注入（控制权在容器）
public class OrderService {
    private final PaymentService payment;        // 由外部注入
    private final InventoryService inventory;    // 由外部注入

    public OrderService(PaymentService payment, InventoryService inventory) {
        this.payment = payment;
        this.inventory = inventory;
    }
}
```

**核心思想**：对象只声明「我需要什么」，由容器决定「怎么提供」。

## 三种注入方式

## 1. 构造器注入（推荐）

```java
@Service
public class OrderService {
    private final PaymentService payment;
    private final InventoryService inventory;

    @Autowired  // Spring 4+ 可省略，构造器注入自动
    public OrderService(PaymentService payment, InventoryService inventory) {
        this.payment = payment;
        this.inventory = inventory;
    }
}
```

**优点**：
- 不可变（final 字段）
- 强依赖必须存在
- 容易测试（直接 new + 传 mock）

**缺点**：参数过多时构造器臃肿

## 2. Setter 注入

```java
@Service
public class OrderService {
    private PaymentService payment;

    @Autowired(required = false)
    public void setPayment(PaymentService payment) {
        this.payment = payment;
    }
}
```

**优点**：可选依赖
**缺点**：可变状态 + 时序问题

## 3. 字段注入（不推荐）

```java
@Service
public class OrderService {
    @Autowired
    private PaymentService payment;  // 直接注入字段
}
```

**优点**：简洁
**缺点**：
- 不可测试（需要反射）
- 隐藏依赖关系
- 不可变对象无法用

⚠️ **Google / SonarQube 都建议避免字段注入**

## Spring IoC 容器

```java
@Configuration
@ComponentScan("com.example")
public class AppConfig {
    @Bean
    public PaymentService paymentService() {
        return new PaymentService(stripeClient());
    }

    @Bean
    public StripeClient stripeClient() {
        return new StripeClient(apiKey());
    }

    @Bean
    public String apiKey() {
        return System.getenv("STRIPE_API_KEY");
    }
}

// 启动
ApplicationContext ctx = new AnnotationConfigApplicationContext(AppConfig.class);
OrderService orderService = ctx.getBean(OrderService.class);
```

## Spring Bean 作用域

```java
@Service
@Scope("singleton")  // 默认：单例，整个 Spring 容器只有一个
public class OrderService { }

@Service
@Scope("prototype")  // 多例：每次 getBean 创建新实例
public class ReportGenerator { }

@Service
@Scope("request")   // Web 请求作用域
public class RequestContext { }

@Service
@Scope("session")   // Web session 作用域
public class UserSession { }
```

## NestJS Provider

```typescript
// service.ts
@Injectable()
export class OrderService {
    constructor(
        private readonly payment: PaymentService,
        private readonly inventory: InventoryService,
    ) {}

    async create(req: OrderRequest): Promise<Order> {
        await this.payment.charge(req);
        await this.inventory.reserve(req.items);
        return Order.of(req);
    }
}

// module.ts
@Module({
    providers: [OrderService, PaymentService, InventoryService],
    exports: [OrderService],
})
export class OrderModule {}
```

NestJS 的 Module 系统本质上就是 IoC 容器：
- `@Injectable()`：标记类可被注入
- `constructor` 参数：声明依赖
- `providers`：告诉容器怎么创建
- `@Module`：模块边界（类似 Java package）

## Go Wire（编译期 DI）

Go 推荐用 Google Wire 做编译期 DI：

```go
// wire.go
//go:build wireinject

package main

import "github.com/google/wire"

func InitializeApp() (*App, error) {
    wire.Build(
        NewStripeClient,
        NewPaymentService,
        NewInventoryService,
        NewOrderService,
        NewApp,
    )
    return nil, nil
}

// 编译时 wire 生成 wire_gen.go
// func InitializeApp() (*App, error) {
//     stripeClient := NewStripeClient()
//     payment := NewPaymentService(stripeClient)
//     inventory := NewInventoryService()
//     order := NewOrderService(payment, inventory)
//     app := NewApp(order)
//     return app, nil
// }
```

Wire 不依赖反射，编译期生成依赖注入代码，比 Spring 更明确、更快。

## 适用边界

✅ **使用场景**：
- 业务对象有多个依赖
- 需要单测（mock 依赖）
- 多个实现可切换（生产 + 测试 + Mock）
- 中大型应用（Spring / NestJS / Angular / Dagger）

❌ **避免场景**：
- 业务对象极简（无依赖）
- 一次性脚本（直接 new 就行）
- 性能极敏感场景（反射有开销）

🔄 **与 Service Locator 区别**：
- **DI**：显式声明依赖（构造器 / 字段）
- **Service Locator**：调用 `ServiceLocator.lookup()`（隐藏依赖）

💡 **最佳实践**：
- 优先构造器注入（不可变 + 易测试）
- 避免字段注入（用 lombok @RequiredArgsConstructor）
- 单例 + 不可变 + 线程安全
- Wire / Dagger 是编译期 DI（比 Spring 更快）


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
