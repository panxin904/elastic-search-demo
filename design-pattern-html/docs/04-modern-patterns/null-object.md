---
title: Null Object 空对象模式
date: 2026-08-15  # date-auto-injected
description: 消除 null 检查 + Optional / Maybe / 空集合 / NoopLogger
---

# Null Object 空对象模式

## 核心问题

业务代码中充斥 `if (obj != null) { ... } else { ... }`，导致：
1. **NullPointerException**：忘了 null 检查
2. **代码冗长**：每个字段都可能 null，if 链遍布
3. **业务含义模糊**：null 是「不存在」还是「错误」？
4. **多重传播**：null 在调用链中传递

## 核心思想

用「什么都不做的对象」替代 null，使调用方**不必做空值检查**。

**两种形式**：
1. **Null Object Pattern**：提供一个空对象（如 `Collections.emptyList()` / `Logger.NOOP`）
2. **Optional/Maybe**：容器包装，强制处理空值

## Optional 实战（Java）

```java
// ❌ 传统 null 检查
public String getUserName(long id) {
    User u = userRepo.findById(id);
    if (u != null) {
        return u.getName();
    } else {
        return "Anonymous";  // 或抛异常
    }
}

// ✅ Optional：调用方决定
public Optional<User> findById(long id) {
    return userRepo.findById(id);
}

public String getUserName(long id) {
    return userRepo.findById(id)
        .map(User::getName)
        .orElse("Anonymous");
}

public User getUserOrThrow(long id) {
    return userRepo.findById(id)
        .orElseThrow(() -> new UserNotFoundException(id));
}
```

## Optional 链式操作

```java
public String getUserCity(long userId) {
    return userRepo.findById(userId)
        .map(User::getAddress)
        .map(Address::getCity)
        .map(City::getName)
        .orElse("Unknown");
}

public Optional<Email> getPrimaryEmail(long userId) {
    return userRepo.findById(userId)
        .flatMap(user -> user.getEmails().stream()
            .filter(Email::isPrimary)
            .findFirst());
}
```

## Optional 与 Stream 结合

```java
public List<Order> getRecentOrders(long userId) {
    return userRepo.findById(userId)
        .map(user -> orderRepo.findByUser(user.getId()))
        .orElse(Collections.emptyList());  // Null Object：空集合
}
```

## TypeScript：可选链与空值合并

```typescript
// 可选链（Optional Chaining）ES2020+
const city = user?.address?.city;  // 任一环节 undefined，整体 undefined

// 空值合并
const name = user?.name ?? 'Anonymous';  // null/undefined 用默认值

// 组合
const cityName = user?.address?.city ?? 'Unknown';

// TypeScript 类型系统
function getUserName(user: User | null): string {
    return user?.name ?? 'Anonymous';
}

function getUserEmails(user: User | null): Email[] {
    return user?.emails ?? [];  // 默认空数组
}

function findUser(id: number): User | null {
    return users.find(u => u.id === id) ?? null;
}
```

## async/await + Optional

```typescript
async function getUserEmail(id: number): Promise<string | null> {
    const user = await db.findUser(id);
    return user?.email ?? null;
}
```

## 经典案例：Null Object

## Logger.NOOP

```java
interface Logger {
    void info(String msg);
    void error(String msg);
}

class ConsoleLogger implements Logger {
    public void info(String msg) { System.out.println(msg); }
    public void error(String msg) { System.err.println(msg); }
}

class NoopLogger implements Logger {
    public void info(String msg) { /* 什么都不做 */ }
    public void error(String msg) { /* 什么都不做 */ }
}

// 用法
class Foo {
    private final Logger logger;

    public Foo(Logger logger) { this.logger = logger; }

    public void bar() {
        logger.info("bar called");
        // 测试时：new Foo(new NoopLogger()) — 不污染测试输出
    }
}
```

## Collections.emptyList()

```java
List<String> empty = Collections.emptyList();  // 单例空 List
empty.add("a");  // UnsupportedOperationException（不可变）

// Map.of() / Set.of()
Map<String, Integer> emptyMap = Map.of();  // 单例空 Map
```

## Go：nil 是 Null Object

```go
// Go 没有 Null Object，但 nil 接口「什么都不做」天然实现
type Logger interface {
    Info(msg string)
}

var _ Logger = (*noopLogger)(nil)

type noopLogger struct{}
func (noopLogger) Info(msg string) {}

// 用法
var logger Logger = noopLogger{}  // 测试时静默
logger.Info("test")  // 什么都没发生
```

## 实战：策略模式 + Null Object

```typescript
interface PaymentStrategy {
    pay(amount: number): Promise<PaymentResult>;
}

class AlipayStrategy implements PaymentStrategy { /* ... */ }
class WechatPayStrategy implements PaymentStrategy { /* ... */ }
class NoPaymentStrategy implements PaymentStrategy {
    async pay(amount: number) {
        return { success: false, message: 'No payment method configured' };
    }
}

class PaymentContext {
    constructor(private strategy: PaymentStrategy) {}

    async execute(amount: number) {
        return this.strategy.pay(amount);
    }
}

// 用法：避免 null 检查
const strategy = selectStrategy(user)
    ?? new NoPaymentStrategy();  // 永远不是 null
const result = await new PaymentContext(strategy).execute(amount);
```

## 链式 Null Object

```typescript
class User {
    constructor(
        public name: string,
        public email: Email | null,
    ) {}
}

class Email {
    constructor(public address: string, public isVerified: boolean) {}
}

const EMPTY_EMAIL = new Email('unknown@example.com', false);

function getVerifiedEmail(user: User): Email {
    return user.email?.isVerified ? user.email : EMPTY_EMAIL;
}
```

## 适用边界

✅ **使用场景**：
- null 是「合法状态」（缓存未命中 / 可选组件）
- 集合可能为空（默认返回 `Collections.emptyList()`）
- 策略模式中的「默认策略」
- Logger / EventBus 测试时静音

❌ **避免场景**：
- null 表示「错误」（应该抛异常）
- 业务方明确知道 null（不需要默认行为）
- 过度使用 Optional（性能开销 + 代码冗长）

🔄 **Optional vs Null Object Pattern**：
| | Optional | Null Object Pattern |
|---|---|---|
| 形式 | 容器包装 | 「什么都不做」的对象 |
| 调用 | `.map()` / `.orElse()` | 直接调用方法 |
| 案例 | `Optional<T>` | `Collections.emptyList()` |

💡 **最佳实践**：
- 用 Optional 替代 return null（Optional\<T\>）
- Java 9+ `Optional.stream()` 与其他 API 配合
- TypeScript 用 `??` 和 `?.` 而非 `||` 和 `.`
- 不要 `Optional<Optional<T>>`（嵌套 Optional 反模式）


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
