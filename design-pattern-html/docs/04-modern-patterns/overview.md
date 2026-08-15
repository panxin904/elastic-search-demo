---
title: 现代模式（响应式 / 事件驱动 / 六边形等）
---

# 现代模式总览

> 云原生时代涌现的「新一代设计模式」。它们不是 GoF 23 模式的标准成员，但在主流框架（Spring Boot / Go Wire / NestJS / .NET Core）中已成为不可替代的核心抽象。理解这些模式能帮你看清框架源码的设计哲学。

## 为什么需要现代模式

GoF 1994 年的 23 模式针对的是 OOP 语言的**类与对象**，但 2020 年后的软件工程发生了根本变化：

1. **依赖管理从硬编码变成注入**：DI 容器接管对象生命周期
2. **持久化从 SQL 拼接变成仓储抽象**：Repository 模式统一 CRUD
3. **查询从拼接字符串变成规格对象**：Specification 把查询条件变成 first-class 值
4. **空值检查从 `if` 链变成 Null Object**：让空值也是「合法值」

这些模式在 Spring Boot / Laravel / NestJS / Django / ASP.NET Core 中已经事实标准化。

## 4 种现代模式速览

| 模式 | 核心问题 | 典型场景 |
|---|---|---|
| **Dependency Injection 依赖注入** | 解耦对象创建与使用 | Spring Bean / NestJS Provider / Angular Service |
| **Repository 仓储** | 封装数据访问逻辑 | MyBatis Mapper / JPA Repository / TypeORM Repository |
| **Specification 规格** | 把查询条件变成可组合对象 | JPA Specification / Laravel 查询构造器 / Go func filter |
| **Null Object 空对象** | 消除空值检查 | Optional / Stream.ofNullable / Kotlin `?` |

## Dependency Injection 依赖注入

### 核心思想

对象只声明自己需要什么依赖，由外部容器（DI 容器）注入具体的实现。这是**控制反转（IoC）**的最常见实现。

### 三种注入方式

| 方式 | 实现 | 优缺点 |
|---|---|---|
| **构造器注入**（推荐） | 通过构造函数传入 | 不可变 / 易测试 / 强制依赖可见 |
| **Setter 注入** | 通过 setter 传入 | 可选依赖 / 但可变状态难测试 |
| **字段注入** | `@Autowired` 直接注入字段 | 简洁但难测试（reflection） |

### 多语言实现

```java
// Java Spring: 构造器注入（推荐）
@Service
public class OrderService {
    private final PaymentService payment;
    private final InventoryService inventory;

    public OrderService(PaymentService payment, InventoryService inventory) {
        this.payment = payment;
        this.inventory = inventory;
    }

    public Order create(OrderRequest req) {
        payment.charge(req);
        inventory.reserve(req.items);
        return Order.of(req);
    }
}
```

```go
// Go: 不需要 DI 容器，靠接口 + 手动注入
type OrderService struct {
    payment   PaymentService
    inventory InventoryService
}

func NewOrderService(p PaymentService, i InventoryService) *OrderService {
    return &OrderService{payment: p, inventory: i}
}

// 编译期 DI：Google Wire 自动生成
// func initializeOrderService(...) *OrderService {
//     payment := NewPaymentService(...)
//     inventory := NewInventoryService(...)
//     return NewOrderService(payment, inventory)
// }
```

```typescript
// TypeScript NestJS: Provider 注入
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
```

### 与 Service Locator 的区别

```java
// ❌ Service Locator: 反模式（隐藏依赖）
@Service
public class OrderService {
    public void create(OrderRequest req) {
        PaymentService p = ServiceLocator.lookup(PaymentService.class);
        // 难测试，难看出依赖关系
    }
}

// ✅ DI: 显式声明依赖
public OrderService(PaymentService payment) {
    this.payment = payment;
}
```

### 何时用 DI 框架

✅ **Spring / Spring Boot**：项目 ≥ 50 个 bean
✅ **NestJS**：模块化大型应用
✅ **Angular**：组件树 + Service
✅ **Google Wire (Go)**：编译期 DI，避免运行时反射

❌ **小脚本 / CLI 工具**：直接 `new` 就够了

## Repository 仓储模式

### 核心思想

把数据访问逻辑封装到独立的接口层，让业务层不直接依赖数据库访问技术。业务只依赖 `Repository` 接口，而不是 JDBC / JPA / MongoDB driver。

### 实战对比

```java
// ❌ 业务层直接用 JDBC（耦合数据库细节）
public class OrderService {
    public List<Order> findByUser(long userId) {
        try (Connection c = dataSource.getConnection()) {
            PreparedStatement ps = c.prepareStatement(
                "SELECT * FROM orders WHERE user_id = ?");
            ps.setLong(1, userId);
            ResultSet rs = ps.executeQuery();
            // ... 解析 ResultSet
        }
    }
}

// ✅ 业务层只依赖 Repository 接口
public interface OrderRepository {
    Optional<Order> findById(long id);
    List<Order> findByUser(long userId);
    void save(Order order);
}

public class OrderService {
    private final OrderRepository repo;

    public OrderService(OrderRepository repo) { this.repo = repo; }

    public Order getOrder(long id) {
        return repo.findById(id).orElseThrow(OrderNotFoundException::new);
    }
}
```

### 多语言生态

| 语言 | Repository 实现 | 案例 |
|---|---|---|
| Java | Spring Data JPA | `interface OrderRepository extends JpaRepository<Order, Long>` |
| TypeScript | TypeORM / Prisma | `@EntityRepository(Order)` |
| Python | Django ORM | `class OrderRepository(models.Manager)` |
| Go | 自定义 / sqlc | `interface OrderRepo { ... }` + sqlc 生成 |
| C# | EF Core | `class OrderRepository : IOrderRepository` |

### Repository vs DAO

| | Repository | DAO |
|---|---|---|
| 抽象层级 | 聚合根为单位 | 表为单位 |
| 方法命名 | `findByUser` 业务语义 | `selectByUserId` SQL 语义 |
| 返回值 | 领域对象 | Entity / DTO |

## Specification 规格模式

### 核心思想

把查询/筛选条件封装成 first-class 对象，可以组合、复用、传递。**Composite Specification** 让多个条件 AND/OR/NOT 自由组合。

### 实战：JPA Specification

```java
// JPA 自带 Specification API
public class OrderSpecs {
    public static Specification<Order> hasUser(long userId) {
        return (root, q, cb) -> cb.equal(root.get("userId"), userId);
    }

    public static Specification<Order> createdAfter(LocalDateTime time) {
        return (root, q, cb) -> cb.greaterThan(root.get("createdAt"), time);
    }

    public static Specification<Order> totalGreaterThan(BigDecimal min) {
        return (root, q, cb) -> cb.greaterThan(root.get("total"), min);
    }
}

// 自由组合
Specification<Order> spec = Specification
    .where(OrderSpecs.hasUser(123))
    .and(OrderSpecs.createdAfter(LocalDateTime.now().minusDays(30)))
    .and(OrderSpecs.totalGreaterThan(new BigDecimal("100")));

List<Order> orders = orderRepository.findAll(spec);
```

### TypeScript 实战

```typescript
interface Specification<T> {
    isSatisfiedBy(entity: T): boolean;
    and(other: Specification<T>): Specification<T>;
    or(other: Specification<T>): Specification<T>;
    not(): Specification<T>;
}

class UserSpec implements Specification<User> {
    constructor(private predicate: (u: User) => boolean) {}
    isSatisfiedBy(u: User) { return this.predicate(u); }
    and(other: Specification<User>) {
        return new UserSpec(u => this.isSatisfiedBy(u) && other.isSatisfiedBy(u));
    }
    // ... or, not
}

const activeAdult = new UserSpec(u => u.age >= 18)
    .and(new UserSpec(u => u.status === 'active'));
const result = users.filter(activeAdult.isSatisfiedBy.bind(activeAdult));
```

### 何时使用

✅ **多条件组合搜索**：电商筛选（品类 + 价格区间 + 评分）
✅ **复杂权限规则**：角色 + 资源 + 状态组合判定
✅ **查询条件复用**：相同条件在多个 controller 复用

❌ **简单 CRUD**：单个条件直接写 SQL 更快

## Null Object 空对象模式

### 核心思想

用「什么都不做的对象」替代 null，使调用方不必做空值检查。

### 实战：Optional / Maybe

```java
// ❌ 传统 null 检查（污染业务代码）
public String getUserName(Long id) {
    User u = userRepo.findById(id);
    if (u != null) {
        return u.getName();
    } else {
        return "Anonymous";  // 或者抛异常
    }
}

// ✅ Null Object：用 Optional 让调用方决定
public Optional<User> findById(long id) {
    return userRepo.findById(id);
}

public String getUserName(long id) {
    return userRepo.findById(id)
        .map(User::getName)
        .orElse("Anonymous");
}
```

### Null Object Pattern vs Optional

| | Null Object Pattern | Optional |
|---|---|---|
| 形式 | 提供一个「什么都不做的对象」 | 容器包装 |
| 调用 | 直接调用方法，不需检查 | `.map()` / `.orElse()` |
| 案例 | `Collections.emptyList()` / `Logger.NOOP` | `Optional<T>` / `Stream.ofNullable` |

```typescript
// Null Object 经典案例
interface Logger {
    info(msg: string): void;
}

class ConsoleLogger implements Logger {
    info(msg: string) { console.log(msg); }
}

class NoopLogger implements Logger {
    info(msg: string) { /* 什么都不做 */ }
}

// 测试时用 NoopLogger 替代 ConsoleLogger
class Foo {
    constructor(private logger: Logger) {}
    bar() { this.logger.info('bar called'); }
}

new Foo(new NoopLogger());  // 测试时静默
new Foo(new ConsoleLogger());  // 生产时输出
```

### 何时用 / 避免

✅ **使用**：null 是「合法状态」（缓存未命中 / 可选组件）
✅ **使用**：策略模式中的「默认策略」
❌ **避免**：null 表示「错误」（应该抛异常）

## 现代模式与 GoF 23 的关系

| 现代模式 | 与 GoF 的关系 | 演进 |
|---|---|---|
| DI | Factory Method + Singleton 的容器化 | Spring 把「构造对象」抽象成容器 |
| Repository | Facade 的领域特定版本 | Facade 通用，Repository 专门包装持久化 |
| Specification | Composite + Interpreter | 多个条件组合（Composite）+ 条件求值（Interpreter）|
| Null Object | Strategy 的特例 | Null Object 是一种特殊的「什么都不做」策略 |

## 现代模式的反模式风险

1. **DI 滥用**：过度依赖注入会让代码像「依赖图」，调试困难。**只用必要的依赖**。
2. **Repository 变 DAO**：业务层直接调用 `findByIdAndStatus` SQL 命名 → Repository 退化成 DAO。
3. **Specification 过度泛化**：简单条件也用 Specification 反而增加复杂度。
4. **Null Object 滥用**：把所有 null 都替换成 Null Object 会模糊「错误」和「默认值」边界。

## 实战建议

1. **优先构造器注入**：字段注入 (`@Autowired`) 难测试
2. **Repository 接口放在领域层**：实现在基础设施层
3. **Specification 在 2 个条件以上再用**：1 个条件直接传参即可
4. **Optional 不当返回值滥用**：仅在「明确可能为空」时返回
5. **Null Object 配合策略模式**：用策略消除 if-else

## 下一步

- 阅读每篇单独的现代模式细节：[DI](./dependency-injection) / [Repository](./repository) / [Specification](./specification) / [Null Object](./null-object)
- 进阶：[架构模式 · CQRS](../05-architectural-patterns/cqrs)（Repository + Event Sourcing 的架构升级）
- 反向自查：[反模式 · 上帝对象](../06-anti-patterns/god-object)（DI 容器膨胀的常见病）