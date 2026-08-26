---
title: Anemic Model 贫血模型
description: 症状 + 病因 + 药方 + 充血模型 vs 贫血模型
---

# Anemic Model 贫血模型

## 症状

```java
// 领域对象只有 getter/setter，业务逻辑都在 Service
public class User {
    private Long id;
    private String email;
    private boolean active;
    private LocalDateTime lastLoginAt;
    private int loginAttempts;
    private Set<Role> roles = new HashSet<>();
    // 30+ 个字段，只有 getter/setter
}

@Service
public class UserService {
    public void deactivate(User user) {
        user.setActive(false);  // 业务逻辑应该在 User 里
        userRepo.save(user);
    }

    public boolean canLogin(User user) {
        // 业务规则散落在 Service
        return user.isActive()
            && user.getLoginAttempts() < 5
            && user.getLastLoginAt() > LocalDateTime.now().minusDays(90);
    }

    public void incrementLoginAttempts(User user) {
        user.setLoginAttempts(user.getLoginAttempts() + 1);
        if (user.getLoginAttempts() >= 5) {
            user.setActive(false);  // 业务规则：5 次失败后禁用
        }
        userRepo.save(user);
    }
}
```

**典型表现**：
1. 实体类只有 getter/setter
2. 业务规则都在 `*Service` 里
3. 实体变成「数据传输对象」（DTO）
4. 业务变更要改 Service + Entity 两边
5. 单测要 mock 大量 Service 才能测业务

## 病因

1. **把 Entity 当 DTO 用**
   - 很多 ORM（MyBatis / JPA）鼓励「字段映射」用法
   - DDD 实体 ≠ JPA Entity（概念混淆）

2. **误以为"业务逻辑只在 Service"是 Clean Architecture**
   - Clean Architecture 是「接口在领域层，实现在基础设施层」
   - 不是「业务逻辑全在 Service」

3. **测试 Service 时为了 mock 简单，把逻辑外移**
   - 「Service 太多依赖不好 mock，把逻辑挪到 Entity」反而更好

4. **把 Entity 当成贫血的数据结构**
   - 误以为 OOP = 数据 + 行为拆开
   - 实际 OOP = 数据 + 行为内聚

5. **团队没有 DDD 培训**
   - 不懂「充血模型」/「Rich Domain Model」

## 药方：充血模型

```java
// ✅ 充血模型：实体有状态 + 行为
public class User {
    private Long id;
    private String email;
    private boolean active;
    private LocalDateTime lastLoginAt;
    private int loginAttempts;
    private Set<Role> roles = new HashSet<>();

    // 业务行为：实体自己实现
    public void deactivate() {
        if (!this.active) {
            throw new IllegalStateException("User already deactivated");
        }
        this.active = false;
        DomainEvents.raise(new UserDeactivatedEvent(this.id));
    }

    public void activate() {
        if (this.active) {
            throw new IllegalStateException("User already active");
        }
        this.active = true;
        this.loginAttempts = 0;
        DomainEvents.raise(new UserActivatedEvent(this.id));
    }

    public void recordLoginFailure() {
        this.loginAttempts++;
        if (this.loginAttempts >= 5) {
            deactivate();  // 5 次失败自动禁用
        }
    }

    public boolean canLogin() {
        return this.active
            && this.loginAttempts < 5
            && (this.lastLoginAt == null
                || this.lastLoginAt.isAfter(LocalDateTime.now().minusDays(90)));
    }

    public void changeEmail(String newEmail) {
        if (newEmail == null || !newEmail.matches("^.+@.+\\..+$")) {
            throw new IllegalArgumentException("Invalid email");
        }
        this.email = newEmail;
        DomainEvents.raise(new EmailChangedEvent(this.id, newEmail));
    }

    public boolean hasRole(Role role) {
        return this.roles.contains(role);
    }

    public void grantRole(Role role) {
        this.roles.add(role);
    }

    // getter
    public Long getId() { return id; }
    public String getEmail() { return email; }
    // 不暴露 setter！
}
```

## Service 变成薄包装

```java
@Service
@Transactional
public class UserService {
    @Autowired private UserRepository repo;

    public void deactivate(long userId) {
        User user = repo.findById(userId).orElseThrow();
        user.deactivate();  // 行为在实体里
        repo.save(user);
    }

    public boolean canLogin(long userId) {
        User user = repo.findById(userId).orElseThrow();
        return user.canLogin();  // 行为在实体里
    }
}
```

## Domain Events 模式

```java
// 领域事件：实体状态变化时发布
public class DomainEvents {
    private static final ThreadLocal<List<Object>> events = new ThreadLocal<>();

    public static void raise(Object event) {
        events.get().add(event);
    }

    public static List<Object> getAndClear() {
        var list = events.get();
        events.remove();
        return list;
    }
}

// 在 Repository 实现中发布事件
@Repository
public class JpaUserRepository implements UserRepository {
    @PersistenceContext private EntityManager em;

    @Override
    public User save(User user) {
        em.persist(user);
        // 发布领域事件
        for (var event : DomainEvents.getAndClear()) {
            em.publishEvent(event);  // Spring Event
        }
        return user;
    }
}

// 监听者
@Component
public class UserEventListener {
    @EventListener
    public void onUserDeactivated(UserDeactivatedEvent e) {
        // 通知管理员 / 取消订阅 / 等
    }
}
```

## 充血模型 vs 贫血模型对比

| | 贫血模型 | 充血模型 |
|---|---|---|
| 实体 | 只有 getter/setter | 有状态 + 行为 |
| 业务逻辑 | 在 Service | 在实体 |
| Service | 编排 + 业务 | 编排（薄） |
| 测试 | 测 Service | 测实体（纯逻辑） |
| 复用 | 难（逻辑在 Service）| 易（实体行为可）） |
| 维护 | 改动要改多处 | 改动集中 |
| 学习 | 简单 | 需 DDD |

## 重构案例

## 重构前：贫血模型

```java
// Entity
public class Order {
    private Long id;
    private Long userId;
    private BigDecimal total;
    private OrderStatus status;
    private List<OrderItem> items;
    // 只有 getter/setter
}

// Service
@Service
public class OrderService {
    public void pay(Long orderId, BigDecimal amount) {
        Order order = orderRepo.findById(orderId).orElseThrow();
        if (order.getStatus() != OrderStatus.PENDING) {
            throw new IllegalStateException("Only pending orders can be paid");
        }
        if (order.getTotal().compareTo(amount) != 0) {
            throw new IllegalArgumentException("Amount mismatch");
        }
        order.setStatus(OrderStatus.PAID);
        orderRepo.save(order);
        eventBus.publish(new OrderPaidEvent(order));
    }
}
```

## 重构后：充血模型

```java
// Entity（含业务）
public class Order {
    @Getter private Long id;
    @Getter private Long userId;
    @Getter private BigDecimal total;
    @Getter private OrderStatus status;
    @Getter private List<OrderItem> items;

    public void pay(BigDecimal amount) {
        if (this.status != OrderStatus.PENDING) {
            throw new OrderAlreadyPaidException(this.id);
        }
        if (this.total.compareTo(amount) != 0) {
            throw new PaymentAmountMismatchException(this.id, this.total, amount);
        }
        this.status = OrderStatus.PAID;
        DomainEvents.raise(new OrderPaidEvent(this));
    }

    public void cancel(String reason) {
        if (this.status == OrderStatus.SHIPPED || this.status == OrderStatus.COMPLETED) {
            throw new OrderCannotBeCancelledException(this.id);
        }
        this.status = OrderStatus.CANCELLED;
        DomainEvents.raise(new OrderCancelledEvent(this, reason));
    }

    public void ship(String trackingNo) {
        if (this.status != OrderStatus.PAID) {
            throw new OrderNotPaidException(this.id);
        }
        this.status = OrderStatus.SHIPPED;
        DomainEvents.raise(new OrderShippedEvent(this, trackingNo));
    }
}

// Service（薄）
@Service
public class OrderService {
    @Autowired private OrderRepository repo;

    @Transactional
    public void pay(Long orderId, BigDecimal amount) {
        Order order = repo.findById(orderId).orElseThrow();
        order.pay(amount);  // 业务在实体里
        repo.save(order);
    }
}
```

## 适用边界

✅ **充血模型适用**：
- 业务规则明确（订单状态机 / 用户权限）
- 业务复用多（多个 Service 用同一个业务）
- 长期演进的系统（业务会复杂化）
- 团队有 DDD 经验

❌ **贫血模型可接受**：
- 简单 CRUD（无业务规则）
- 一次性脚本 / Demo
- 性能极敏感（充血模型有方法调用开销）
- 团队无 DDD 经验（过度设计反而坏事）

💡 **最佳实践**：
- **业务行为进实体**：任何 `if-else` 检查业务规则都该在实体
- **不暴露 setter**：用行为方法替代（`user.changeEmail(...)` vs `user.setEmail(...)`）
- **领域事件**：实体状态变化触发事件
- **测试实体**：实体测试是纯单元测试（不需要 mock）

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
