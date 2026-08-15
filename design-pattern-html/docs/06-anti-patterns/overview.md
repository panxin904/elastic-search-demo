---
title: 反模式（应避免的反面案例）
---

# 反模式总览

> 反模式（Anti-Pattern）是「表面看起来是解决方案，实际上会让代码/系统变得更糟」的常见做法。每个反模式都附「症状-病因-药方」清单，可以直接用作 code review checklist。

## 为什么要学反模式

学习设计模式是学「**怎么做好**」，学习反模式是学「**怎么识别坏**」。code review 中 80% 的问题都是反模式的重复出现：

- 「这个类 5000 行」→ 上帝对象
- 「Service 只有 getter/setter」→ 贫血模型
- 「改了 A 就要改 B/C/D」→ 循环依赖
- 「回调嵌套 8 层」→ 回调地狱

掌握反模式能在 PR 5 秒内识别这些问题，比学 100 个设计模式都实用。

## 7 种反模式速览

| 反模式 | 核心症状 | 病因 |
|---|---|---|
| **God Object 上帝对象** | 一个类承担所有职责，5000+ 行 | 缺少职责拆分 / 急于交付 |
| **Anemic Model 贫血模型** | 领域对象只有 getter/setter | 误把 Entity 当 Data Transfer Object |
| **Big Ball of Mud 大泥球** | 代码无结构，谁都能改任何地方 | 没有架构规范 / 缺少 code review |
| **Callback Hell 回调地狱** | 嵌套 5+ 层回调 | 不熟悉 Promise / async-await |
| **Circular Dependency 循环依赖** | A 依赖 B，B 依赖 A | 模块边界混乱 |
| **Magic Number 魔数** | 代码中充斥 `100`、`0.95` 这类无解释数字 | 没有常量 / 没有命名 |
| **Premature Optimization 提前优化** | 为不可能出现的瓶颈写复杂代码 | 不懂「先测量后优化」 |

## God Object 上帝对象

### 症状

```java
// 一个类 5000+ 行，承担一切职责
public class UserManager {
    public User createUser(...) { /* 50 行 */ }
    public void sendEmail(...) { /* 100 行 */ }
    public Order processOrder(...) { /* 200 行 */ }
    public Report generateReport(...) { /* 300 行 */ }
    public void exportCSV(...) { /* 150 行 */ }
    public void auditLog(...) { /* 80 行 */ }
    // ... 30+ 个职责
}
```

### 病因

1. 「这个类刚好能装下这些功能」
2. 缺少职责拆分意识（违反 SRP 单一职责原则）
3. 工期压力下"先这样吧"

### 药方

1. **按职责拆分**：UserService / EmailService / OrderService / ReportService
2. **组合优于继承**：用 Facade 模式组合多个子服务
3. **定期审视**：每月 review 类行数排行，把超长类列入重构清单

### 检测工具

- SonarQube：`Cognitive Complexity` / `Class size` 阈值
- CodeScene：识别「Hotspot」（频繁修改 + 复杂度高）

## Anemic Model 贫血模型

### 症状

```java
// 领域对象只有 getter/setter，业务逻辑都在 Service
public class User {
    private Long id;
    private String email;
    private boolean active;
    private LocalDateTime lastLoginAt;
    // 只有 getter/setter，30+ 个字段
}

@Service
public class UserService {
    public void deactivate(User user) {
        user.setActive(false);  // 业务逻辑应该在 User 里
        userRepo.save(user);
    }
}
```

### 病因

1. 把 Entity 当 DTO 用（很多 ORM 鼓励这种做法）
2. 误以为「业务逻辑只在 Service」是 Clean Architecture
3. 测试 Service 时为了 mock 简单，把逻辑外移

### 药方

1. **业务行为回到实体**：`user.deactivate()` 而不是 `userService.deactivate(user)`
2. **充血模型**：实体不仅有状态，还有行为
3. **Rich Domain Model**：与 DDD（领域驱动设计）结合

```java
// ✅ 充血模型
public class User {
    private Long id;
    private String email;
    private boolean active;

    public void deactivate() {
        if (!this.active) throw new IllegalStateException("already deactivated");
        this.active = false;
        DomainEvents.raise(new UserDeactivatedEvent(this.id));
    }
}
```

## Big Ball of Mud 大泥球

### 症状

- 没有模块边界，任何文件都能 import 任何文件
- 命名混乱（`Manager1`、`Helper`、`Util2`、`NewService`）
- 业务逻辑分散在 Controller、Service、Util、Helper 等 5+ 个地方
- 改一行代码不知道会破坏什么

### 病因

1. 没有架构规范，谁都能加新模块
2. 缺少 code review
3. 业务变更频繁，代码跟着打补丁

### 药方

1. **DDD 限界上下文**：按业务拆分模块，模块间通过 API 通信
2. **架构守护**：ArchUnit / Dependency Cruiser 检查依赖方向
3. **命名规范**：每个类名要能回答「我是谁」+「我能做什么」

```java
// ❌ 大泥球
public class Util {  // 什么都往里塞
    public static String formatDate(...) { /* ... */ }
    public static User parseUserJson(...) { /* ... */ }
    public static BigDecimal calcTax(...) { /* ... */ }
}

// ✅ 拆分
public class DateFormatter { /* 只做日期格式化 */ }
public class UserJsonParser { /* 只做 User JSON 解析 */ }
public class TaxCalculator { /* 只计算税 */ }
```

## Callback Hell 回调地狱

### 症状

```javascript
// 嵌套 8 层回调，可读性为 0
getData(function(a) {
    getMoreData(a, function(b) {
        getMoreData(b, function(c) {
            getMoreData(c, function(d) {
                getMoreData(d, function(e) {
                    getMoreData(e, function(f) {
                        // 最终在这里写业务逻辑
                    });
                });
            });
        });
    });
});
```

### 病因

1. JavaScript 早期没有 Promise / async-await
2. 不熟悉现代异步原语
3. 强行用回调解决异步问题

### 药方

1. **Promise 链**：`.then().then().catch()`
2. **async/await**：最现代的写法
3. **RxJS / Observables**：复杂异步流
4. **co-routine**：Python `asyncio` / Kotlin coroutine

```typescript
// ✅ async/await
async function process() {
    const a = await getData();
    const b = await getMoreData(a);
    const c = await getMoreData(b);
    const d = await getMoreData(c);
    const e = await getMoreData(d);
    const f = await getMoreData(e);
    // 业务逻辑
}
```

### Go 中对应

```go
// ❌ 回调地狱（Go 也有）
go func() {
    data1, err := fetch1()
    if err != nil { callback(err); return }
    go func() {
        data2, err := fetch2(data1)
        // ...
    }()
}()

// ✅ channel + goroutine
func process(ctx context.Context) (Result, error) {
    data1, err := fetch1(ctx)
    if err != nil { return nil, err }
    data2, err := fetch2(ctx, data1)
    if err != nil { return nil, err }
    // 顺序逻辑
}
```

## Circular Dependency 循环依赖

### 症状

```
ServiceA → ServiceB → ServiceC → ServiceA
```

启动失败：

```
A depends on B
B depends on C
C depends on A  ← 启动失败
```

### 病因

1. 模块边界设计错误（A 用了 B 的字段，B 又用了 A 的字段）
2. 两个 Service 互相调用对方方法
3. ORM 双向关联 + 序列化

### 药方

1. **依赖反转**：抽出 Interface，让双方都依赖抽象
2. **领域事件**：用事件替代直接调用
3. **重新审视边界**：两个模块循环依赖可能说明它们应该合并

```java
// ❌ 循环依赖
@Service class UserService { @Autowired OrderService orderService; }
@Service class OrderService { @Autowired UserService userService; }

// ✅ 通过事件解耦
@Service class UserService {
    @Autowired ApplicationEventPublisher events;
    public void register(User u) { events.publishEvent(new UserRegisteredEvent(u)); }
}

@Service class OrderService {
    @EventListener
    public void onUserRegistered(UserRegisteredEvent e) {
        // 处理订单初始化
    }
}
```

### 检测工具

- **ArchUnit**（Java）：禁止循环依赖
- **dependency-cruiser**（JS）：模块依赖图
- **go vet**：go.mod 检查

## Magic Number 魔数

### 症状

```java
// 代码中充斥无解释数字
if (retryCount > 3) { /* ... */ }
if (temperature > 100) { /* ... */ }
if (cacheSize * 0.95 > maxSize) { /* ... */ }
Thread.sleep(5000);  // 为什么是 5 秒？
```

### 病因

1. 直接 hardcode 数字（最常见）
2. 没有常量定义规范
3. "反正能跑"心态

### 药方

1. **命名常量**：每个魔数都要有名字 + 注释

```java
public class RetryConfig {
    public static final int MAX_RETRY_COUNT = 3;
    public static final Duration RETRY_INTERVAL = Duration.ofMillis(5000);
}

public class CacheConfig {
    public static final double HIGH_WATER_RATIO = 0.95;
}
```

2. **配置文件化**：业务参数走 `@ConfigurationProperties` / `application.yml`

3. **单元化常量**：避免 `1000`（ms? KB? Mbps?）

```java
// ❌ 单位不明
Thread.sleep(5000);

// ✅ 明确单位
Thread.sleep(Duration.ofSeconds(5).toMillis());
```

## Premature Optimization 提前优化

### 症状

```java
// 为了不存在的瓶颈写复杂代码
public class OrderRepository {
    // 3 层缓存 + Redis + 本地 LRU + 数据库
    public Order findById(long id) {
        Order o = lruCache.get(id);
        if (o == null) {
            o = caffeineCache.get(id);
            if (o == null) {
                o = redis.get(id);
                if (o == null) {
                    o = jdbc.query("SELECT * FROM orders WHERE id = ?", id);
                    redis.set(id, o);
                    caffeineCache.put(id, o);
                }
                lruCache.put(id, o);
            }
        }
        return o;
    }
}
```

### 病因

1. Donald Knuth 警告过：「过早优化是万恶之源」
2. 没做 profiling 就开始优化
3. 「听说 Redis 很快」就加缓存

### 药方

1. **先测量，后优化**：用 JMH / pprof / async-profiler 找到真瓶颈
2. **80/20 法则**：20% 的代码承担 80% 的性能问题
3. **不要优化 hot path 之外**：`@Transactional` 包 10 个微服务调用才是真问题
4. **可读性优先**：90% 情况下，简洁的代码已经够快

```java
// ✅ 简单直接
public Order findById(long id) {
    return jdbc.query("SELECT * FROM orders WHERE id = ?", id);
}

// 当且仅当真的慢，再加缓存
// @Cacheable("orders")
// public Order findById(long id) { ... }
```

### Donald Knuth 原话

> 「We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil.」
> —— Donald Knuth, 1974

## 反模式自查 Checklist

代码 review 时 5 秒扫一眼：

- [ ] **类行数 > 1000？** → 拆分（可能 God Object）
- [ ] **领域对象只有 getter/setter？** → 充血（可能 Anemic Model）
- [ ] **新代码不知道往哪里放？** → 大泥球（需要架构守护）
- [ ] **嵌套 > 3 层回调？** → async/await
- [ ] **模块间互相 import？** → 循环依赖（重新设计边界）
- [ ] **数字 > 0 没命名？** → 命名常量
- [ ] **3 层缓存 + 2 个 DB？** → 拆掉，先 profile

## 反模式 vs 设计模式的关系

每个反模式都对应一个正确的设计模式：

| 反模式 | 对应正确模式 |
|---|---|
| God Object | Facade + SRP（拆分为多个专门 Service） |
| Anemic Model | Rich Domain Model / DDD 充血模型 |
| Big Ball of Mud | Modular Monolith / Bounded Context |
| Callback Hell | Promise / async-await / Coroutine |
| Circular Dependency | Dependency Inversion（依赖接口） |
| Magic Number | Named Constant / Configuration |
| Premature Optimization | 先 Profiling + YAGNI（You Aren't Gonna Need It） |

## 实战建议

1. **code review 时优先看反模式**：90% 的设计问题都在反模式清单里
2. **设立架构守护**：ArchUnit / Checkstyle / ESLint 自定义规则
3. **季度重构**：把反模式列入技术债，定期清理
4. **培训比 review 更重要**：新人入职讲一遍反模式清单
5. **以身作则**：自己写代码时主动避开反模式

## 下一步

- 阅读每篇单独的反模式细节：[God Object](./god-object) / [Anemic Model](./anemic-model) / [Big Ball of Mud](./big-ball-of-mud) / [Callback Hell](./callback-hell) / [Circular Dependency](./circular-dependency) / [Magic Number](./magic-number) / [Premature Optimization](./premature-optimization)
- 进阶：[现代模式 · DI](../04-modern-patterns/dependency-injection)（避免 God Object 的工具）
- 返回首页：[设计模式总览](../index.md)