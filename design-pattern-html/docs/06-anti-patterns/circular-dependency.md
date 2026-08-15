---
title: Circular Dependency 循环依赖
description: 症状 + 病因 + 药方 + 依赖反转 + 领域事件 + 检测工具
---

# Circular Dependency 循环依赖

## 症状

```
ServiceA → ServiceB → ServiceC → ServiceA
```

启动失败：
```
A depends on B
B depends on C
C depends on A  ← 启动失败
```

**典型表现**：
1. 启动报错 `Circular reference detected`
2. 单测时 `NullPointerException`（依赖未注入）
3. 修改 A 触发 B 改，B 触发 C 改，C 又触发 A 改
4. 模块边界混乱（拆分不彻底）
5. ORM 双向关联 + JSON 序列化 → StackOverflowError

## 病因

1. **模块边界设计错误**
   - A 用了 B 的字段，B 又用了 A 的字段
   - 没想清楚「谁依赖谁」

2. **两个 Service 互相调用对方方法**
   - `UserService.delete()` 调用 `OrderService.cancelByUser()`
   - `OrderService.cancel()` 又调用 `UserService.update()`

3. **ORM 双向关联 + 序列化**
   - `User.orders` + `Order.user` 双向引用
   - Jackson 序列化时无限递归

4. **公共包被滥用**
   - `common` 包被多个业务包依赖，业务包之间也互相依赖 `common`
   - 实际形成了环形

5. **拆分不彻底**
   - 试图拆分微服务但公用同一份代码

## 药方

## 1. 依赖反转（DIP）

```java
// ❌ 循环依赖
@Service
public class UserService {
    @Autowired private OrderService orderService;  // UserService → OrderService
}

@Service
public class OrderService {
    @Autowired private UserService userService;     // OrderService → UserService（环）
}

// ✅ 通过接口反转（都依赖抽象）
public interface UserServiceInterface {
    void onUserDeleted(long userId);
}

public interface OrderServiceInterface {
    void cancelByUser(long userId);
}

@Service
public class UserService implements UserServiceInterface {
    private final OrderServiceInterface orderService;

    public UserService(OrderServiceInterface orderService) {
        this.orderService = orderService;  // 依赖抽象
    }

    public void delete(long userId) {
        // 删除用户
        orderService.onUserDeleted(userId);  // 通知订单服务
    }
}

@Service
public class OrderService implements OrderServiceInterface {
    private final UserServiceInterface userService;

    public OrderService(UserServiceInterface userService) {
        this.userService = userService;
    }

    public void cancelByUser(long userId) {
        // 取消订单
    }

    @Override
    public void onUserDeleted(long userId) {
        cancelByUser(userId);
    }
}
```

## 2. 领域事件解耦

```java
// ✅ 通过事件彻底解耦（最干净）
@Service
public class UserService {
    @Autowired private ApplicationEventPublisher events;

    public void delete(long userId) {
        // 删除用户
        events.publishEvent(new UserDeletedEvent(userId));  // 发事件
    }
}

@Service
public class OrderService {
    @EventListener
    public void onUserDeleted(UserDeletedEvent event) {
        // 取消该用户的所有订单
        cancelByUser(event.getUserId());
    }
}
```

UserService 不直接依赖 OrderService，完全解耦。

## 3. 重新审视边界

如果两个模块互相调用，应该考虑：
- **合并**：A 和 B 本来就是一个模块
- **提取公共**：抽出一个 C 模块，让 A 和 B 都依赖 C
- **事件解耦**：A 发事件，B 订阅

## ORM 双向关联 + 序列化

```java
// ❌ 双向关联 + JSON 序列化
@Entity
public class User {
    @OneToMany(mappedBy = "user")
    private List<Order> orders;  // User → Order
}

@Entity
public class Order {
    @ManyToOne
    private User user;  // Order → User（环）
}

// REST API 返回 User 时
@GetMapping("/users/{id}")
public User getUser(@PathVariable long id) {
    return userRepo.findById(id).orElseThrow();
    // Jackson 序列化：User → orders → Order → user → orders → ... (无限递归)
}

// 修复 1：@JsonIgnore
@Entity
public class User {
    @OneToMany(mappedBy = "user")
    @JsonIgnore  // 序列化时忽略
    private List<Order> orders;
}

// 修复 2：DTO 分离
public class UserDTO {
    private Long id;
    private String name;
    // 不含 orders
}

public class OrderDTO {
    private Long id;
    private Long userId;  // 只存 userId，不含 user 对象
    // 不含 user
}

// 用 MapStruct / ModelMapper 自动转换
@Mapper
public interface UserMapper {
    UserDTO toDTO(User user);
}
```

## 检测工具

## Java ArchUnit

```java
@ArchTest
static final ArchRule no_cycles = slices()
    .matching("com.example.(*)..")
    .should().beFreeOfCycles()
    .because("Cyclic dependencies between modules violate bounded context");
```

## JavaScript / TypeScript dependency-cruiser

```json
// .dependency-cruiser.json
{
    "forbidden": [
        {
            "name": "no-circular",
            "severity": "error",
            "comment": "禁止循环依赖",
            "from": {},
            "to": { "circular": true }
        }
    ]
}
```

```bash
depcruise --validate .dependency-cruiser.json src/
```

## Go

```bash
# go.mod 自带循环检查
go list -e -json ./... | jq -r '.Imports | .[]' | sort -u
# 手动检查 Import 是否有环
```

## IntelliJ IDEA

```
右键包 → Diagrams → Show Dependencies
自动可视化依赖图，循环依赖一目了然
```

## 实战案例：拆分用户和订单

## 重构前（循环依赖）

```java
@Service
class UserService {
    @Autowired OrderService orderService;

    void deleteUser(long id) {
        userRepo.delete(id);
        orderService.cancelAllByUser(id);  // 直接调
    }
}

@Service
class OrderService {
    @Autowired UserService userService;

    void createOrder(OrderRequest req) {
        User user = userService.findById(req.userId);  // 直接调
        // 创建订单
    }
}
```

## 重构后（事件解耦）

```java
@Service
class UserService {
    @Autowired EventPublisher events;
    @Autowired UserRepository userRepo;

    void deleteUser(long id) {
        userRepo.delete(id);
        events.publish(new UserDeletedEvent(id));  // 发事件
    }
}

@Service
class OrderService {
    @Autowired EventPublisher events;
    @Autowired UserCache userCache;  // 本地缓存用户信息

    void createOrder(OrderRequest req) {
        User user = userCache.get(req.userId);  // 读本地缓存（不调 UserService）
        // 创建订单
        events.publish(new OrderCreatedEvent(order));
    }

    @EventListener
    void onUserDeleted(UserDeletedEvent event) {
        orderRepo.cancelByUser(event.userId);  // 订阅事件
    }
}
```

**好处**：
- UserService 和 OrderService 完全解耦
- 各自独立测试（不需要对方）
- 可以独立部署 / 拆分微服务

## 适用边界

✅ **识别循环依赖**：
- 启动报错 `Circular reference`
- 改 A 触发 B 改，B 又触发 A 改
- 单测难以独立运行

✅ **用 DIP 解耦**：
- 两个 Service 都需要对方，但只调用 1-2 个方法
- 业务逻辑相对独立

✅ **用事件解耦**：
- 多对多依赖（> 2 个模块互相依赖）
- 业务流程异步可接受
- 跨服务 / 跨模块

✅ **重新设计边界**：
- A 和 B 经常一起改（应该合并）
- A 和 B 拆分不合理

❌ **避免**：
- 业务简单，强行引入接口反转（过度设计）
- 性能极敏感（事件传递有延迟）

💡 **最佳实践**：
- **CI 检查**：ArchUnit / dependency-cruiser 拦截循环依赖
- **code review**：每个 PR 检查「这依赖真的必要吗」
- **优先事件**：跨服务 / 跨模块通信用事件
- **本地缓存**：频繁访问的跨服务数据用本地缓存
- **重新设计边界**：拆不开就合（拆不开说明本来就是一个）
