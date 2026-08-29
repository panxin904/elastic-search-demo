---
title: 创建型模式总览
date: 2026-08-15  # date-auto-injected
---

# 创建型模式总览

> GoF 23 模式中专门解决「对象创建」问题的 5 个模式。它们把 `new` 这个动作从客户端代码中抽离出来，根据场景选择不同的创建策略：单实例、工厂、抽象工厂、建造者、原型。

## 为什么需要创建型模式

业务代码里最常见的耦合是「客户端直接 `new` 具体类」。例如：

```java
// 强耦合：客户端依赖具体实现类，单元测试无法替换
OrderService service = new OrderServiceImpl();
```

这样做有三个问题：

1. **编译期耦合**：改个实现就要改所有客户端
2. **无法 mock**：单测时没法替换成测试替身
3. **生命周期混乱**：不知道这个对象是单例、多例还是池化

创建型模式通过「把创建逻辑封装到一个抽象层」解决这三个问题。客户端只依赖抽象接口（`OrderService`），由创建层决定用什么实现、何时创建、怎么管理生命周期。

## 5 种创建型模式速览

| 模式 | 核心问题 | 典型场景 | Java 标准库案例 |
|---|---|---|---|
| **Singleton 单例** | 全局只允许一个实例 | 配置中心 / 日志器 / 线程池 | `Runtime.getRuntime()` |
| **Factory Method 工厂方法** | 创建逻辑延迟到子类 | 框架扩展点（Spring BeanFactory）| `java.util.Calendar.getInstance()` |
| **Abstract Factory 抽象工厂** | 一族相关对象的创建 | 跨数据库 / 跨 UI 主题切换 | `javax.xml.parsers.DocumentBuilderFactory` |
| **Builder 建造者** | 多参数对象的构造 | HTTP Client / Lombok @Builder | `StringBuilder` / `Stream.Builder` |
| **Prototype 原型** | 通过克隆创建对象 | 对象创建成本高（DB 连接 / 大文档）| `Object.clone()` |

## Singleton 单例模式

### 核心思想

保证一个类只有一个实例，并提供全局访问点。

### 多语言实现要点

```java
// Java: 双重检查锁 + volatile（Java 5+ 后 volatile 语义保证可见性）
public final class Singleton {
    private static volatile Singleton instance;
    private Singleton() {}
    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

```go
// Go: 包级变量 + sync.Once（最简洁的实现）
package singleton

import "sync"

var (
    instance *Service
    once     sync.Once
)

func Get() *Service {
    once.Do(func() {
        instance = &Service{config: loadConfig()}
    })
    return instance
}
```

```typescript
// TypeScript: 模块本身就是单例（ES Module 缓存）
// service.ts
class ApiClient { /* ... */ }
export const apiClient = new ApiClient();
```

### 何时使用 / 不使用

✅ **使用**：配置管理器 / 日志器 / 线程池 / 硬件访问抽象
❌ **避免**：业务实体（User / Order 应该是多例）/ 有状态的对象 / 需要测试替换的场景
⚠️ **分布式陷阱**：单 JVM/进程的 Singleton 不是分布式单例，集群下会有 N 个实例

## Factory Method 工厂方法模式

### 核心思想

定义一个创建对象的接口，但让子类决定实例化哪一个类。把「实例化」延迟到子类。

### 与「简单工厂」的区别

简单工厂用 if-else 硬编码创建逻辑；工厂方法把这个 if-else 推迟到子类覆写。

```java
// 框架：抽象类定义创建接口
abstract class Logistics {
    // 业务方法使用 transport，但不知道它是什么
    public void planDelivery() {
        Transport t = createTransport();  // 工厂方法
        t.deliver();
    }
    protected abstract Transport createTransport();  // 子类决定
}

// 扩展点：子类决定具体类型
class RoadLogistics extends Logistics {
    @Override
    protected Transport createTransport() {
        return new Truck();
    }
}
```

### 典型应用

- **Spring BeanFactory**：所有 bean 都是通过工厂方法创建
- **JDBC Connection**：DriverManager 通过工厂方法返回 Connection
- **Java 集合**：Collections.synchronizedList() / unmodifiableList() 都是工厂方法
- **Go http.Handler**：实现方提供 ServeHTTP，框架决定何时调用

## Abstract Factory 抽象工厂模式

### 核心思想

提供一个接口，用于创建**相关或依赖对象的家族**，而不需要指定具体类。

### 与 Factory Method 的区别

| | Factory Method | Abstract Factory |
|---|---|---|
| 抽象层级 | 一个产品的创建 | 一族产品的创建 |
| 方法数 | 1 个抽象方法 | 多个抽象方法 |
| 关注点 | 类延迟实例化 | 主题/族切换 |

### 典型应用

```typescript
// TypeScript: 跨主题 UI 组件库
interface UIFactory {
    createButton(): Button;
    createCheckbox(): Checkbox;
    createInput(): Input;
}

class MaterialUIFactory implements UIFactory {
    createButton() { return new MaterialButton(); }
    createCheckbox() { return new MaterialCheckbox(); }
    createInput() { return new MaterialInput(); }
}

// 客户端只依赖 UIFactory，具体工厂在运行时注入
class Form {
    constructor(private factory: UIFactory) {}
    render() {
        const btn = this.factory.createButton();
        const cb = this.factory.createCheckbox();
    }
}
```

实战：Ant Design / Material-UI / Chakra UI 都是抽象工厂模式。

## Builder 建造者模式

### 核心思想

将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示。

### 多语言对照

```java
// Java: 经典 Builder 模式（Lombok @Builder 自动生成）
HttpRequest req = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Content-Type", "application/json")
    .timeout(Duration.ofSeconds(30))
    .POST(BodyPublishers.ofString(payload))
    .build();
```

```go
// Go: Functional Options Pattern（Go 社区最 idiomatic 的 builder）
type Server struct {
    addr    string
    timeout time.Duration
    logger  *log.Logger
}

type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func WithLogger(l *log.Logger) Option {
    return func(s *Server) { s.logger = l }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{addr: addr, timeout: 30 * time.Second}
    for _, o := range opts {
        o(s)
    }
    return s
}

// 使用
srv := NewServer(":8080",
    WithTimeout(60 * time.Second),
    WithLogger(customLogger),
)
```

```typescript
// TypeScript: 链式 builder
const query = new QueryBuilder()
    .select('id', 'name', 'email')
    .from('users')
    .where('age > ?', 18)
    .orderBy('created_at', 'desc')
    .limit(10)
    .toSQL();
```

### 何时使用

✅ **构造参数 ≥ 4 个**：避免「telescoping constructor」
✅ **对象状态分步构建**：必须按特定顺序设置字段
✅ **不可变对象**：所有字段在 build() 时一次性设定

❌ **避免**：「一个参数也用 builder」会增加 4 倍代码量，没有收益

## Prototype 原型模式

### 核心思想

通过克隆（而非 `new`）来创建对象。

### 何时使用

- **创建成本高**：连接池中的数据库连接、大文档（Office 文件）
- **避免重复初始化**：从模板克隆比 `new + setX` 10 次字段高效
- **运行时决定具体类**：客户端不知道要克隆的对象类型

### 实现要点

```java
// Java: 实现 Cloneable 接口 + 浅/深拷贝
class MailTemplate implements Cloneable {
    private String subject;
    private String body;

    @Override
    public MailTemplate clone() {
        try {
            return (MailTemplate) super.clone();  // 浅拷贝
        } catch (CloneNotSupportedException e) {
            throw new AssertionError();
        }
    }
}
```

### 多语言对比

| 语言 | 原生克隆支持 | 推荐做法 |
|---|---|---|
| Java | `Cloneable` 接口 | 不推荐（深拷贝语义模糊）/ 用拷贝构造器 |
| Go | 无 | 手动写 `Clone() T` 方法 |
| TypeScript | `structuredClone()` (ES2022+) | 现代浏览器 + Node 17+ 原生支持 |
| Python | `copy.copy/deepcopy` | 简单场景用 `copy.deepcopy()` |

## 5 模式选择决策树

```
创建对象时，是否需要"全局唯一实例"？
├── 是 → Singleton
└── 否 → 创建逻辑是否复杂（>3 步 / 多个参数）？
    ├── 是 → 是否需要分步构建？
    │   ├── 是 → Builder
    │   └── 否 → 多个相关对象一起创建？→ Abstract Factory
    └── 否 → 创建逻辑是否因场景变化？
        ├── 是 → Factory Method（框架）/ 抽象工厂（多个产品族）
        └── 否 → 对象创建成本是否高？→ Prototype
            └── 默认 → 直接 new（不必套模式）
```

## 与 Spring / Go Wire / NestJS 框架的关系

| 框架 | 核心创建模式 |
|---|---|
| Spring / Spring Boot | BeanFactory（Factory Method + Singleton） + ApplicationContext（抽象工厂） |
| Go Wire | Provider + Injector（编译期 DI，本质是工厂方法） |
| NestJS | Module + Provider（依赖注入容器，Factory Method + Singleton） |
| Dagger / Hilt | 编译期生成的 Factory Method |

## 实战建议

1. **优先用框架提供的工厂**：Spring `@Bean` / NestJS `@Module` 比手写工厂方法靠谱
2. **Builder 是多参数对象的默认选择**：构造参数 ≥ 3 就该用
3. **单例慎用**：集群环境下「单例」会变成「多例」，考虑分布式锁
4. **不要为模式而模式**：能直接 `new` 就 `new`，抽象的成本由「未来扩展需求」承担
5. **多语言实现是面试加分项**：Java + Go + TS 三语言对比展示深度

## 下一步

- 阅读每篇单独的 GoF 23 模式细节：[Singleton](./singleton) / [Factory Method](./factory-method) / [Abstract Factory](./abstract-factory) / [Builder](./builder) / [Prototype](./prototype)
- 进阶：[现代模式 · 依赖注入](../04-modern-patterns/dependency-injection)
- 反向自查：[反模式 · 上帝对象](../06-anti-patterns/god-object)（单例滥用是常见病）

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
