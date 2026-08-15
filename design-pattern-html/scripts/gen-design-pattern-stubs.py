#!/usr/bin/env python3
"""Generate Design Pattern substantial stub docs for design-pattern-html site.

Strategy:
- Each stub is a full-quality markdown file (≥3KB) with real design pattern content.
- Pattern: helper `mk(path, title, desc, sections)` where sections is a list of
  (heading, content) tuples. Run from design-pattern-html/ root.

Generated: 42 stubs across 6 chapters:
  01-gof-creational: singleton / factory-method / abstract-factory / builder / prototype  (5)
  02-gof-structural: adapter / bridge / composite / decorator / facade / flyweight / proxy  (7)
  03-gof-behavioral: chain-of-responsibility / command / iterator / mediator / memento / observer / state / strategy / template-method / visitor / interpreter  (11)
  04-modern-patterns: dependency-injection / repository / specification / null-object  (4)
  05-architectural-patterns: cqrs / event-sourcing / saga / sidecar / circuit-breaker / bulkhead / strangler-fig / outbox  (8)
  06-anti-patterns: god-object / anemic-model / big-ball-of-mud / callback-hell / circular-dependency / magic-number / premature-optimization  (7)
"""
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"


def mk(path: str, title: str, description: str, sections: list) -> None:
    """Render a substantial stub markdown file.

    `sections` is a list of (heading, content) tuples. Headings are ## level.
    """
    body = [f"# {title}\n"]
    for h, c in sections:
        body.append(f"## {h}\n")
        body.append(c.strip() + "\n")
    full = (
        f"---\n"
        f"title: {title}\n"
        f"description: {description}\n"
        f"---\n\n"
        + "\n".join(body)
    )
    target = DOCS / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(full, encoding="utf-8")
    size = len(full.encode("utf-8"))
    print(f"  + {path} ({size} B)")


# ============================================================================
# Chapter 01: GoF Creational (5 stubs)
# ============================================================================

def ch01_singleton() -> None:
    mk("01-gof-creational/singleton.md", "Singleton 单例模式",
       "全局唯一实例 + 多语言实现 + 线程安全 + 序列化攻击 + 分布式陷阱",
       [
        ("核心问题", """保证一个类只有一个实例，并提供全局访问点。

**动机**：当系统中需要「全局唯一的资源」时（如配置管理器、日志器、线程池），用全局变量污染代码，又会被多线程并发问题反复纠缠。

**真实场景**：
- 应用配置（`application.properties` / `app.yaml`）：整个 JVM 一份
- 日志器（Logger）：所有业务代码共享一个，避免重复 IO
- 硬件抽象（GPU / 打印机）：物理资源只允许一个 wrapper"""),

        ("核心思想", """将「对象是否已存在」的判断逻辑放在类内部，对外只暴露一个 `getInstance()` 方法。

**实现三要点**：
1. **私有构造器**：外部无法 `new`
2. **静态实例变量**：类自己持有唯一实例
3. **静态访问方法**：第一次调用时创建，后续直接返回"""),

        ("Java 实现", r"""## 双重检查锁（DCL，推荐）

```java
public final class Singleton {
    // volatile 防止指令重排导致返回未初始化对象
    private static volatile Singleton instance;

    private Singleton() {
        // 防止反射攻击
        if (instance != null) {
            throw new RuntimeException("Singleton already constructed");
        }
    }

    public static Singleton getInstance() {
        if (instance == null) {                          // 第一次检查（无锁）
            synchronized (Singleton.class) {
                if (instance == null) {                  // 第二次检查（加锁）
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }

    // 防止反序列化创建新对象
    protected Object readResolve() {
        return getInstance();
    }
}
```

## 静态内部类（最优雅）

```java
public class Singleton {
    private Singleton() {}

    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;  // 类加载时初始化，JVM 保证线程安全
    }
}
```

## 枚举（Effective Java 作者 Josh Bloch 推荐）

```java
public enum Singleton {
    INSTANCE;
    private final Config config;

    Singleton() {
        this.config = loadConfig();
    }

    public Config getConfig() { return config; }
}
// 用法：Singleton.INSTANCE.getConfig();
```"""),

        ("多语言实现", r"""## Go：sync.Once 是事实标准

```go
package config

import "sync"

var (
    cfg  *Config
    once sync.Once
)

func Get() *Config {
    once.Do(func() {
        cfg = &Config{ApiKey: loadFromEnv()}
    })
    return cfg
}
```

`sync.Once` 底层使用 atomic + mutex，保证 `loadConfig()` 在并发下只执行一次。

## TypeScript：ES Module 单例

```typescript
// config.ts
class Config {
    public readonly apiKey = process.env.API_KEY!;
}

export const config = new Config();
// 任何地方 import { config } from './config' 都拿到同一个实例
```

ES Module 的 import 缓存机制天然就是单例。

## Python：`__new__` 重写

```python
class Singleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

s1 = Singleton()
s2 = Singleton()
print(s1 is s2)  # True
```"""),

        ("实战陷阱", """## 1. 分布式陷阱

单 JVM 的单例 ≠ 集群的单例。集群下每个 JVM 都有自己的「单例」，导致 N 个实例。

**解法**：用 Redis / ZooKeeper 实现分布式单例（但其实没必要——分布式场景通常用无状态服务 + 集中存储）。

## 2. 测试陷阱

单例难以替换 mock，导致单元测试无法隔离。

**解法**：
- 使用 DI 容器（Spring 默认单例，但可以被覆盖）
- 测试时 `@MockBean` 替换单例
- 或单例自身实现 `IConfig` 接口，测试时注入 fake

## 3. 序列化攻击

```java
// 如果 Singleton 实现 Serializable，反序列化会创建新对象
Singleton s1 = Singleton.getInstance();
ObjectOutputStream oos = new ObjectOutputStream(...);
oos.writeObject(s1);
// 反序列化得到新对象，破坏单例
```

**解法**：实现 `readResolve()` 返回原单例（见上面 Java 示例）。

## 4. 反射攻击

```java
Constructor<Singleton> ctor = Singleton.class.getDeclaredConstructor();
ctor.setAccessible(true);
Singleton hacked = ctor.newInstance();  // 绕过私有构造器
```

**解法**：在构造器中检查 `instance != null`（见上面 Java 示例）。"""),

        ("适用边界", """✅ **使用场景**：
- 无状态资源（Logger / Config / ThreadPool）
- 全局缓存（带 TTL 的进程内缓存）
- 硬件抽象（GPU / 打印机）

❌ **避免场景**：
- 业务实体（User / Order 必须多例）
- 有状态对象（会引发并发问题）
- 需要测试替身的场景
- 集群服务（用无状态 + Redis 替代）

🔄 **替代方案**：
- **Spring 容器**：`@Scope("singleton")` + DI（推荐）
- **Go sync.Once**：替代手写单例
- **Python 模块级变量**：本身就是单例
- **TypeScript ES Module**：天然单例

📚 **与其他模式关系**：
- **Factory Method**：工厂方法返回的可以是单例
- **Abstract Factory**：抽象工厂的每个具体工厂通常实现为单例
- **Facade**：外观类经常用单例实现"""),

       ])


def ch01_factory_method() -> None:
    mk("01-gof-creational/factory-method.md", "Factory Method 工厂方法模式",
       "创建逻辑延迟到子类 + 框架扩展点 + Java Spring BeanFactory / Go Wire 源码解读",
       [
        ("核心问题", """创建对象时不知道将来会创建哪些具体类，或者希望把「创建逻辑」推迟到子类决定。

**经典场景**：
- 日志库（Log4j / SLF4j）：业务方只调 `LoggerFactory.getLogger()`，不知道底层是 Log4j 还是 Logback
- 数据库驱动（JDBC）：业务方只调 `DriverManager.getConnection()`，不知道是 MySQL 还是 PG
- HTTP 服务器（Go `http.Handler`）：业务方实现 Handler 接口，框架决定何时调用"""),

        ("核心思想", """定义一个创建对象的抽象方法（`factoryMethod()`），让子类决定具体实例化哪个类。

**对比简单工厂**：简单工厂用 if-else 硬编码；工厂方法把 if-else 推迟到子类覆写。"""),

        ("UML 结构", r"""```text
            ┌─────────────────┐
            │   <<Creator>>   │
            │─────────────────│
            │ + factoryMethod │
            │ + someOperation │
            └─────────────────┘
                    △
                    │ extends
            ┌─────────────────┐
            │  ConcreteCreator│
            │─────────────────│
            │ + factoryMethod │
            └─────────────────┘
                    │ creates
                    ▼
            ┌─────────────────┐
            │  <<Product>>    │
            └─────────────────┘
                    △
                    │ implements
            ┌─────────────────┐
            │ ConcreteProduct │
            └─────────────────┘
```"""),

        ("多语言实现", r"""## Java：经典实现

```java
abstract class Logistics {
    // 业务方法使用 product，但不知道它是什么
    public void planDelivery() {
        Transport t = createTransport();
        t.deliver();
    }

    // 工厂方法：子类决定具体类型
    protected abstract Transport createTransport();
}

class RoadLogistics extends Logistics {
    @Override
    protected Transport createTransport() {
        return new Truck();
    }
}

class SeaLogistics extends Logistics {
    @Override
    protected Transport createTransport() {
        return new Ship();
    }
}

// 客户端
new RoadLogistics().planDelivery();   // 用卡车
new SeaLogistics().planDelivery();    // 用船
```

## Go：函数作为工厂

```go
package transport

type Transport interface {
    Deliver() error
}

type Truck struct{}
func (Truck) Deliver() error { /* ... */ return nil }

// 工厂函数
func NewRoadTransport() Transport {
    return &Truck{}
}

func NewSeaTransport() Transport {
    return &Ship{}
}

// 客户端按需选择
var t transport.Transport = transport.NewRoadTransport()
t.Deliver()
```

## TypeScript：工厂函数

```typescript
interface Transport { deliver(): Promise<void>; }

function createTransport(mode: 'road' | 'sea'): Transport {
    switch (mode) {
        case 'road': return new Truck();
        case 'sea':  return new Ship();
    }
}
```"""),

        ("实战：框架中的应用", r"""## Spring BeanFactory

Spring 的 BeanFactory 就是巨型工厂方法：

```java
// Spring 源码
public interface BeanFactory {
    Object getBean(String name) throws BeansException;
    <T> T getBean(Class<T> requiredType) throws BeansException;
    // ...
}

// 抽象类 AbstractBeanFactory 实现大部分逻辑
// 子类（DefaultListableBeanFactory）实现具体的 bean 创建逻辑
```

业务方写 `@Component` / `@Bean`，框架决定什么时候、怎么创建。

## JDBC DriverManager

```java
Connection conn = DriverManager.getConnection(url, user, pwd);
```

`getConnection()` 是静态工厂方法，但它内部委托给注册的 `Driver`：

```java
// Driver 接口
public interface Driver {
    Connection connect(String url, Properties info) throws SQLException;
    // 每个数据库厂商实现这个接口
}
```

每个 JDBC Driver 的 `connect()` 方法就是工厂方法。

## Go http.Handler

```go
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}

// net/http 是 Creator
func ListenAndServe(addr string, h Handler) error {
    // ... 接受请求后调用 h.ServeHTTP(w, r)
}

// 业务方实现 Product 接口
type MyHandler struct{}
func (MyHandler) ServeHTTP(w ResponseWriter, r *Request) { /* ... */ }

http.ListenAndServe(":8080", MyHandler{})
```"""),

        ("适用边界", """✅ **使用场景**：
- 框架扩展点（让用户决定实现类）
- 跨数据库 / 跨平台的 driver
- 测试 mock（创建 mock 实现）

❌ **避免场景**：
- 只有一种实现（直接 `new`）
- 创建逻辑不会变化（不需要延迟）

🔄 **演进路径**：
- 一个工厂方法 → Abstract Factory（多个产品族）
- 简单工厂 → 工厂方法（避免 if-else 硬编码）
- 工厂方法 → DI 容器（Spring / NestJS）

💡 **最佳实践**：
- 用 protected 修饰工厂方法（防止客户端误调用）
- 工厂方法返回抽象类型（不是具体类）
- 配合模板方法使用（父类定义流程，子类实现步骤）"""),

       ])


def ch01_abstract_factory() -> None:
    mk("01-gof-creational/abstract-factory.md", "Abstract Factory 抽象工厂模式",
       "一族相关对象的创建 + 主题切换 + UI 组件库 / 数据库 driver 族 / Spring ApplicationContext",
       [
        ("核心问题", """需要创建「一组相关或相互依赖的对象家族」，而不是单一对象。

**真实场景**：
- UI 组件库（Ant Design / Material UI）：所有组件风格必须统一，不能混搭
- 数据库 driver（MySQL 全家桶 / Oracle 全家桶）：Connection + Statement + ResultSet 必须配套
- 跨平台 GUI（macOS / Windows / Linux）：按钮 + 文本框 + 菜单风格必须统一"""),

        ("核心思想", """提供一个接口，用于创建**相关对象的家族**，而不需要指定具体类。每个具体工厂负责一个完整产品族。

**与 Factory Method 的区别**：
| | Factory Method | Abstract Factory |
|---|---|---|
| 抽象层级 | 一个产品的创建 | 一族产品的创建 |
| 方法数 | 1 个抽象方法 | 多个抽象方法 |
| 关注点 | 类延迟实例化 | 主题/族切换"""),

        ("多语言实现", r"""## Java：UI 组件族

```java
interface UIFactory {
    Button createButton();
    Checkbox createCheckbox();
    TextField createTextField();
}

class MaterialUIFactory implements UIFactory {
    public Button createButton() { return new MaterialButton(); }
    public Checkbox createCheckbox() { return new MaterialCheckbox(); }
    public TextField createTextField() { return new MaterialTextField(); }
}

class AntDesignUIFactory implements UIFactory {
    public Button createButton() { return new AntdButton(); }
    public Checkbox createCheckbox() { return new AntdCheckbox(); }
    public TextField createTextField() { return new AntdTextField(); }
}

// 客户端：只依赖 UIFactory 抽象
class Form {
    private final UIFactory factory;
    Form(UIFactory factory) { this.factory = factory; }

    void render() {
        Button btn = factory.createButton();
        Checkbox cb = factory.createCheckbox();
        // ... 渲染到屏幕
    }
}

// 运行时切换主题
Form materialForm = new Form(new MaterialUIFactory());
Form antdForm = new Form(new AntDesignUIFactory());
```

## TypeScript：跨主题 UI

```typescript
interface UIFactory {
    createButton(): Button;
    createInput(): Input;
    createCard(): Card;
}

class ChakraUIFactory implements UIFactory {
    createButton() { return new ChakraButton(); }
    createInput() { return new ChakraInput(); }
    createCard() { return new ChakraCard(); }
}

class Dashboard {
    constructor(private factory: UIFactory) {}
    render() {
        this.factory.createCard().render();
        this.factory.createButton().render();
    }
}

new Dashboard(new ChakraUIFactory()).render();
```"""),

        ("实战：JDBC 全家桶", r"""JDBC 是抽象工厂的经典案例：

```java
// JDBC 抽象产品
public interface Connection {
    Statement createStatement();
    PreparedStatement prepareStatement(String sql);
}

public interface Statement {
    ResultSet executeQuery(String sql) throws SQLException;
}

// MySQL 实现
// com.mysql.cj.jdbc.JdbcConnection implements Connection
// com.mysql.cj.jdbc.JdbcStatement implements Statement

// PG 实现
// org.postgresql.PgConnection implements Connection
// org.postgresql.PgStatement implements Statement

// 客户端只依赖 JDBC API
Connection conn = DriverManager.getConnection(url, user, pwd);
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT ...");
```

DriverManager 内部维护一组 `Driver`，每个 Driver 就是一个具体工厂。

## 与 Spring 的关系

```java
// Spring ApplicationContext 是抽象工厂
public interface ApplicationContext {
    BeanDefinition getBeanDefinition(String name);
    Object getBean(String name);
    // ... 几十个方法
}

// ClassPathXmlApplicationContext / AnnotationConfigApplicationContext
// 是具体工厂（XML 配置 vs 注解配置）
```

每个 ApplicationContext 都能创建一族相关 bean（你的 `@Service` + `@Repository` + `@Configuration`）。"""),

        ("适用边界", """✅ **使用场景**：
- 多主题 UI（设计系统切换）
- 跨数据库 driver 族
- 跨操作系统 GUI 工具包
- 跨消息中间件适配（Kafka 族 / RabbitMQ 族）

❌ **避免场景**：
- 只有一个产品族（直接用具体类）
- 产品族经常变化（抽象工厂难以演进）
- 业务方不需要切换主题（增加抽象成本）

🔄 **替代方案**：
- **DI 容器**（推荐）：Spring 自动按配置装配一族 bean
- **Strategy + Builder**：每个产品独立选择
- **Prototype**：运行时克隆现有族

💡 **最佳实践**：
- 抽象工厂的接口要稳定（一旦确定不轻易改）
- 产品族之间要强一致（不能出现 Material 按钮 + Antd 卡片）
- 配合 DI 使用：客户端通过配置注入具体工厂"""),

       ])


def ch01_builder() -> None:
    mk("01-gof-creational/builder.md", "Builder 建造者模式",
       "多参数对象构造 + Java Lombok @Builder + Go Functional Options + TypeScript chainable",
       [
        ("核心问题", """当一个对象的构造需要**很多参数**（≥ 4 个），且部分参数可选时：
1. 用构造器重载会爆炸（`new User(name)`, `new User(name, age)`, ...）
2. 用 setter 会变成「半成品对象」（构造后状态不完整）
3. 用 Map / Json 传参会失去类型安全"""),

        ("核心思想", """将「对象的构建」与「对象的表示」分离。用一个 Builder 类按步骤设置参数，最后调用 `build()` 一次性生成不可变对象。

**适用信号**：
- 构造参数 ≥ 4 个
- 部分参数可选
- 对象应该是不可变的
- 创建逻辑需要分步"""),

        ("Java 实现", r"""## 经典 Builder 模式

```java
public final class HttpRequest {
    private final URI uri;
    private final String method;
    private final Map<String, String> headers;
    private final Duration timeout;
    private final byte[] payload;

    private HttpRequest(Builder b) {
        this.uri = b.uri;
        this.method = b.method;
        this.headers = Map.copyOf(b.headers);  // 不可变
        this.timeout = b.timeout;
        this.payload = b.payload;
    }

    public static Builder newBuilder() { return new Builder(); }

    public static class Builder {
        private URI uri;
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();
        private Duration timeout = Duration.ofSeconds(30);
        private byte[] payload;

        public Builder uri(URI uri) { this.uri = uri; return this; }
        public Builder method(String m) { this.method = m; return this; }
        public Builder header(String k, String v) { this.headers.put(k, v); return this; }
        public Builder timeout(Duration d) { this.timeout = d; return this; }
        public Builder POST(byte[] body) { this.method = "POST"; this.payload = body; return this; }

        public HttpRequest build() {
            if (uri == null) throw new IllegalStateException("uri required");
            return new HttpRequest(this);
        }
    }
}

// 用法：链式调用，可读性极好
HttpRequest req = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Content-Type", "application/json")
    .timeout(Duration.ofSeconds(60))
    .POST(payload)
    .build();
```

## Lombok @Builder（推荐）

```java
@Builder
@Getter
public class User {
    private Long id;
    private String name;
    private String email;
    @Builder.Default private int age = 18;
    @Builder.Default private List<String> roles = List.of("user");
}

// 用法：Lombok 自动生成 UserBuilder
User u = User.builder()
    .id(1L)
    .name("Alice")
    .email("alice@example.com")
    .age(25)
    .role("admin")     // @Singular 自动支持
    .role("user")
    .build();
```"""),

        ("多语言实现", r"""## Go：Functional Options（最 idiomatic）

```go
package server

import (
    "context"
    "log"
    "time"
)

type Server struct {
    addr    string
    timeout time.Duration
    logger  *log.Logger
    handler http.Handler
}

type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func WithLogger(l *log.Logger) Option {
    return func(s *Server) { s.logger = l }
}

func WithHandler(h http.Handler) Option {
    return func(s *Server) { s.handler = h }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{
        addr:    addr,
        timeout: 30 * time.Second,
        logger:  log.Default(),
    }
    for _, o := range opts {
        o(s)
    }
    return s
}

// 用法：极简，参数顺序无关
srv := NewServer(":8080",
    WithTimeout(60*time.Second),
    WithLogger(customLogger),
    WithHandler(myHandler),
)
```

Functional Options 是 Rob Pike（Go 之父）推荐的 Go 模式，被 grpc-go、k8s 等大型项目广泛使用。

## TypeScript：链式 Builder

```typescript
class QueryBuilder {
    private selects: string[] = [];
    private froms: string[] = [];
    private wheres: string[] = [];
    private orders: string[] = [];
    private limitCount?: number;

    select(...cols: string[]) { this.selects.push(...cols); return this; }
    from(table: string) { this.froms.push(table); return this; }
    where(cond: string) { this.wheres.push(cond); return this; }
    orderBy(col: string, dir: 'ASC' | 'DESC' = 'ASC') { this.orders.push(`${col} ${dir}`); return this; }
    limit(n: number) { this.limitCount = n; return this; }

    toSQL(): string {
        let sql = `SELECT ${this.selects.join(', ')} FROM ${this.froms.join(', ')}`;
        if (this.wheres.length) sql += ` WHERE ${this.wheres.join(' AND ')}`;
        if (this.orders.length) sql += ` ORDER BY ${this.orders.join(', ')}`;
        if (this.limitCount) sql += ` LIMIT ${this.limitCount}`;
        return sql;
    }
}

// 用法
const sql = new QueryBuilder()
    .select('id', 'name', 'email')
    .from('users')
    .where('age > 18')
    .orderBy('created_at', 'DESC')
    .limit(10)
    .toSQL();
// SELECT id, name, email FROM users WHERE age > 18 ORDER BY created_at DESC LIMIT 10
```"""),

        ("适用边界", """✅ **使用场景**：
- 构造参数 ≥ 4 个（最重要信号）
- 多个参数可选
- 对象应该是不可变的
- 创建逻辑需要分步（如 `withHeader().withBody().build()`）
- 创建过程需要中间校验

❌ **避免场景**：
- 只有 1-2 个参数（直接 `new`）
- 所有参数必填且不多（构造器就够）
- 业务方需要中途修改字段（Builder 是一次性的）

🔄 **替代方案**：
- **构造器重载**：≤ 3 个参数时最简单
- **Setter / Lombok @Data**：可变对象
- **Map / Json**：动态配置（牺牲类型安全）
- **Functional Options (Go)**：Go 社区的 Builder

💡 **最佳实践**：
- Builder 本身应该是静态内部类（`HttpRequest.Builder`）
- `build()` 之前做参数校验
- 不要让 Builder 持有未初始化状态（爆 NullPointerException）
- `@Builder.Default` 给字段默认值"""),

       ])


def ch01_prototype() -> None:
    mk("01-gof-creational/prototype.md", "Prototype 原型模式",
       "通过克隆创建对象 + 深拷贝 vs 浅拷贝 + Java Cloneable + JavaScript structuredClone",
       [
        ("核心问题", """当创建对象的成本很高（DB 连接、大文档、复杂配置），而我们又要创建多个类似的对象时，反复 `new` 不划算。

**真实场景**：
- 加载数据库连接（耗时 100ms）
- 解析 Office 文档（耗时 1s+）
- 游戏地图（10MB 数据，克隆比重新加载快 1000x）
- 模板对象（邮件模板、报表模板）"""),

        ("核心思想", """通过克隆（`clone()`）而非 `new` 来创建对象。让对象自己负责「复制自己」的逻辑。

**两种拷贝**：
- **浅拷贝**：只复制对象本身 + 引用，不递归复制内部对象
- **深拷贝**：递归复制整个对象图（包括所有嵌套对象）"""),

        ("Java 实现", r"""## Cloneable 接口（不推荐）

```java
public class MailTemplate implements Cloneable {
    private String subject;
    private String body;
    private List<String> ccList;  // 引用类型

    public MailTemplate(String subject, String body) {
        this.subject = subject;
        this.body = body;
    }

    @Override
    public MailTemplate clone() {
        try {
            return (MailTemplate) super.clone();  // 浅拷贝
        } catch (CloneNotFoundException e) {
            throw new AssertionError();
        }
    }
}
```

**坑**：`Cloneable` 接口没有 `clone()` 方法（只有标记），靠 `Object.clone()`（protected）。深拷贝语义模糊，Effective Java 作者 Josh Bloch **明确不推荐** Cloneable。

## 拷贝构造器（推荐）

```java
public class MailTemplate {
    private final String subject;
    private final String body;
    private final List<String> ccList;

    public MailTemplate(String subject, String body) {
        this.subject = subject;
        this.body = body;
        this.ccList = new ArrayList<>();
    }

    // 拷贝构造器
    public MailTemplate(MailTemplate other) {
        this.subject = other.subject;
        this.body = other.body;
        this.ccList = new ArrayList<>(other.ccList);  // 深拷贝
    }

    public MailTemplate deepClone() {
        return new MailTemplate(this);
    }
}

// 用法
MailTemplate t1 = new MailTemplate("Welcome", "Hi {{name}}");
MailTemplate t2 = t1.deepClone();
t2.setBody("Hello {{name}}");  // 不影响 t1
```"""),

        ("多语言实现", r"""## JavaScript：structuredClone（ES2022+）

```javascript
const template = {
    subject: 'Welcome',
    body: 'Hi {{name}}',
    attachments: [{ filename: 'guide.pdf' }, { filename: 'logo.png' }]
};

// 一行完成深拷贝
const copy = structuredClone(template);
copy.attachments[0].filename = 'manual.pdf';

console.log(template.attachments[0].filename);  // 'guide.pdf'（未变）
console.log(copy.attachments[0].filename);       // 'manual.pdf'
```

支持 Date / RegExp / Map / Set / ArrayBuffer 等内置类型，比 `JSON.parse(JSON.stringify(x))` 强大。

## Go：手动 Clone 方法

```go
package mail

type Attachment struct {
    Filename string
    Data     []byte
}

type Template struct {
    Subject     string
    Body        string
    Attachments []*Attachment
}

func (t *Template) Clone() *Template {
    clone := &Template{
        Subject: t.Subject,
        Body:    t.Body,
    }
    for _, a := range t.Attachments {
        clone.Attachments = append(clone.Attachments, &Attachment{
            Filename: a.Filename,
            Data:     append([]byte(nil), a.Data...),  // 深拷贝 slice
        })
    }
    return clone
}
```

## Python：copy.deepcopy

```python
import copy

template = {
    'subject': 'Welcome',
    'body': 'Hi {{name}}',
    'attachments': [{'filename': 'guide.pdf', 'data': b'...'}]
}

cloned = copy.deepcopy(template)
cloned['attachments'][0]['filename'] = 'manual.pdf'

print(template['attachments'][0]['filename'])  # 'guide.pdf'
print(cloned['attachments'][0]['filename'])     # 'manual.pdf'
```"""),

        ("适用边界", """✅ **使用场景**：
- 对象创建成本高（DB 连接、复杂配置）
- 运行时决定具体类（不知道要克隆什么）
- 模板 / 原型对象（邮件模板、报表模板）
- 历史快照（Game save、撤销栈）

❌ **避免场景**：
- 对象很小（直接 `new` 更快）
- 循环引用（深拷贝会爆栈）
- 不可变对象（共享就好，不需要克隆）

🔄 **替代方案**：
- **拷贝构造器**（Java 推荐）：显式、可控、深浅可选
- **JSON.parse(JSON.stringify(x))**（JS）：简单场景
- **structuredClone()**（JS ES2022+）：浏览器原生
- **copy.deepcopy()**（Python）：标准库
- **Builder**：如果只是想分步创建，用 Builder 更合适

💡 **最佳实践**：
- 优先用拷贝构造器，不用 Cloneable（Effective Java 第 13 条）
- 深浅拷贝要有明确文档（共享可变状态 = bug）
- 不可变对象用「享元」共享，不需要克隆
- 循环引用需要特殊处理（用 id 或 marker）"""),

       ])


# ============================================================================
# Chapter 02: GoF Structural (7 stubs)
# ============================================================================

def ch02_adapter() -> None:
    mk("02-gof-structural/adapter.md", "Adapter 适配器模式",
       "接口不兼容 + 对象适配 vs 类适配 + Java IO 适配器 + Spring HandlerAdapter",
       [
        ("核心问题", """系统中已经存在两个独立开发的模块，它们的接口不兼容，但需要一起工作。直接改源码成本太高（可能破坏现有调用方）。

**真实场景**：
- 旧系统接入新 SDK（旧的 logger 接口 vs 新的 SLF4J）
- 集成第三方库（库 v1 vs 库 v2 接口不同）
- 跨平台（macOS 文件路径 vs Windows 文件路径）"""),

        ("核心思想", """把一个类的接口转换成客户端期望的另一种接口。让原本不兼容的类可以合作，而无需修改它们的源码。

**两种适配器**：
| 类型 | 实现 | 推荐 |
|---|---|---|
| 对象适配器 | 组合（持有被适配者） | ✅ |
| 类适配器 | 继承（多重继承） | ❌（Java / C# 不支持）"""),

        ("Java 实现", r"""## 对象适配器（推荐）

```java
// 目标接口（客户端期望的）
public interface MediaPlayer {
    void play(String audioType, String fileName);
}

// 被适配者（已存在的接口）
public class AdvancedMediaPlayer {
    public void playVlc(String fileName) { /* VLC 播放逻辑 */ }
    public void playMp4(String fileName) { /* MP4 播放逻辑 */ }
}

// 适配器
public class MediaAdapter implements MediaPlayer {
    private final AdvancedMediaPlayer advanced;

    public MediaAdapter(String audioType) {
        this.advanced = new AdvancedMediaPlayer();
    }

    @Override
    public void play(String audioType, String fileName) {
        if (audioType.equalsIgnoreCase("vlc")) {
            advanced.playVlc(fileName);
        } else if (audioType.equalsIgnoreCase("mp4")) {
            advanced.playMp4(fileName);
        }
    }
}

// 客户端使用
MediaPlayer player = new MediaAdapter("vlc");
player.play("vlc", "movie.vlc");  // 实际调用 AdvancedMediaPlayer.playVlc
```

## 类适配器（不推荐）

需要 Java 支持多重继承，目前用 `extends` + `implements` 模拟：

```java
public class MediaAdapter extends AdvancedMediaPlayer implements MediaPlayer {
    @Override
    public void play(String audioType, String fileName) {
        if (audioType.equalsIgnoreCase("vlc")) {
            playVlc(fileName);
        }
    }
}
```

C++ / Python 支持多重继承，但 Java / C# 只能走对象适配器。"""),

        ("实战案例", r"""## Java IO 适配器

```java
// 把字节流适配成字符流
Reader reader = new InputStreamReader(
    new FileInputStream("data.txt"), StandardCharsets.UTF_8);

// 反过来，把字符流转成字节流
Writer writer = new OutputStreamWriter(
    new FileOutputStream("out.txt"), StandardCharsets.UTF_8);
```

`InputStreamReader` 就是经典的适配器，把 `InputStream`（字节）适配成 `Reader`（字符）。

## Arrays.asList（数组 → List）

```java
String[] arr = {"a", "b", "c"};
List<String> list = Arrays.asList(arr);  // 数组 → List
list.add("d");  // UnsupportedOperationException！是固定大小 List
```

## Spring HandlerAdapter

Spring MVC 用 HandlerAdapter 适配各种类型的 Controller：

```java
public interface HandlerAdapter {
    boolean supports(Object handler);
    ModelAndView handle(HttpServletRequest req, HttpServletResponse resp, Object handler);
}

// SimpleControllerHandlerAdapter 适配实现 Controller 接口的类
// HttpRequestHandlerAdapter 适配实现 HttpRequestHandler 接口的类
// RequestMappingHandlerAdapter 适配 @RequestMapping 注解方法
```

Spring 通过 HandlerAdapter 把不同形态的 Controller 统一适配成 `handle()` 调用。"""),

        ("Go 适配器实战", r"""```go
// 旧接口（第三方库）
type OldLogger interface {
    LogMessage(level, msg string)
}

// 新接口（我们的项目标准）
type Logger interface {
    Debug(msg string)
    Info(msg string)
    Warn(msg string)
    Error(msg string)
}

// 适配器
type OldToNewAdapter struct {
    old OldLogger
}

func (a *OldToNewAdapter) Debug(msg string) {
    a.old.LogMessage("DEBUG", msg)
}

func (a *OldToNewAdapter) Info(msg string) {
    a.old.LogMessage("INFO", msg)
}

func (a *OldToNewAdapter) Warn(msg string) {
    a.old.LogMessage("WARN", msg)
}

func (a *OldToNewAdapter) Error(msg string) {
    a.old.LogMessage("ERROR", msg)
}
```

## TypeScript：跨浏览器 API 适配

```typescript
// 旧浏览器没有 fetch
declare const fetch: (input: RequestInfo, init?: RequestInit) => Promise<Response>;

// 适配到统一接口
interface Http {
    get(url: string): Promise<any>;
    post(url: string, body: any): Promise<any>;
}

class FetchHttp implements Http {
    async get(url: string) {
        const r = await fetch(url);
        return r.json();
    }
    async post(url: string, body: any) {
        const r = await fetch(url, {
            method: 'POST',
            body: JSON.stringify(body)
        });
        return r.json();
    }
}

class XMLHttpRequestHttp implements Http {
    // 老浏览器实现
    async get(url: string) {
        return new Promise((resolve) => {
            const xhr = new XMLHttpRequest();
            xhr.open('GET', url);
            xhr.onload = () => resolve(JSON.parse(xhr.responseText));
            xhr.send();
        });
    }
}
```"""),

        ("适用边界", """✅ **使用场景**：
- 接入第三方库（旧版本升级）
- 跨平台 / 跨语言集成
- 系统演进（保护现有代码）
- 单元测试（适配真实对象到 mock 接口）

❌ **避免场景**：
- 双方接口都你可控（直接改一边）
- 只是临时代码（一次性脚本不需要适配器）
- 适配链超过 3 层（说明接口设计本身有问题）

🔄 **与相关模式区别**：
- **Adapter**：转换现有接口
- **Bridge**：从设计开始就解耦抽象与实现
- **Decorator**：增强已有接口（不转换）
- **Facade**：简化子系统（多个 → 一个）

💡 **最佳实践**：
- 用对象适配器（组合），不用类适配器（继承）
- 适配器不暴露被适配者的方法（否则客户端会绕过适配器）
- 双适配器（两个接口互转）：考虑是否能合并成一个通用接口"""),

       ])


def ch02_bridge() -> None:
    mk("02-gof-structural/bridge.md", "Bridge 桥接模式",
       "抽象与实现分离 + JDBC Driver + 跨平台 UI + 多维度独立变化",
       [
        ("核心问题", """一个类有**两个独立变化的维度**（如：形状 + 颜色 / 数据库 + 协议 / 平台 + UI 组件），如果用继承会让类层次爆炸。

**举例**：
- 形状（圆形 / 矩形 / 三角形）× 颜色（红 / 蓝 / 绿）= 9 个类
- 数据库（MySQL / PG / Oracle）× 协议（Native / HTTP / gRPC）= 9 个类
- 平台（macOS / Windows / Linux）× 组件（按钮 / 文本框 / 菜单）= 9 个类"""),

        ("核心思想", """将「抽象」与「实现」分离，使它们都可以独立变化。用「组合」代替「继承」。

**与 Strategy / Adapter 的区别**：
| | Bridge | Strategy | Adapter |
|---|---|---|---|
| 目的 | 抽象与实现解耦 | 算法族切换 | 接口兼容 |
| 数量 | 多个实现 × 多个抽象 | 1 个抽象 × N 个算法 | 单向适配 |
| 设计阶段 | 从一开始 | 运行期替换 | 后期集成 |"""),

        ("实战：JDBC Driver", r"""JDBC 是 Bridge 模式的教科书例子：

```java
// 抽象：JDBC API（java.sql.*）
public interface Connection {
    Statement createStatement() throws SQLException;
    PreparedStatement prepareStatement(String sql) throws SQLException;
}

// 实现：各个数据库厂商
// com.mysql.cj.jdbc.JdbcConnection implements Connection
// org.postgresql.PgConnection implements Connection
// oracle.jdbc.OracleConnection implements Connection

// 桥接器：DriverManager
public class DriverManager {
    private static final CopyOnWriteArrayList<DriverInfo> registeredDrivers = new CopyOnWriteArrayList<>();

    public static Connection getConnection(String url, String user, String password) {
        // 遍历注册的 Driver，找到能处理这个 URL 的
        for (DriverInfo di : registeredDrivers) {
            if (di.driver.matchesURL(url)) {
                return di.driver.connect(url, new Properties() {{ put("user", user); put("password", password); }});
            }
        }
        throw new SQLException("No suitable driver");
    }
}

// 客户端：只依赖 JDBC API
Connection conn = DriverManager.getConnection(
    "jdbc:mysql://localhost:3306/mydb", "root", "secret");
```

**抽象**（Connection）和**实现**（MySQL / PG / Oracle）通过 `DriverManager` 桥接，两边都能独立扩展而不互相影响。"""),

        ("实战：跨平台 UI", r"""```java
// 实现层级（平台）
public interface WindowImpl {
    void drawText(String text);
    void drawRect(int x, int y, int w, int h);
    void open();
}

public class MacWindowImpl implements WindowImpl {
    @Override public void drawText(String text) { /* 调用 Cocoa */ }
    @Override public void drawRect(int x, int y, int w, int h) { /* NSRect */ }
    @Override public void open() { /* [NSWindow makeKeyAndOrderFront] */ }
}

public class WindowsWindowImpl implements WindowImpl {
    @Override public void drawText(String text) { /* 调用 Win32 GDI */ }
    // ...
}

// 抽象层级（窗口）
public abstract class Window {
    protected WindowImpl impl;  // 桥接
    public Window(WindowImpl impl) { this.impl = impl; }

    public void draw() {
        impl.open();
        impl.drawRect(0, 0, 100, 100);
    }
}

public class Dialog extends Window {
    public Dialog(WindowImpl impl) { super(impl); }

    public void drawDialog() {
        impl.drawText("Are you sure?");
        draw();
    }
}

// 客户端
Window mac = new Dialog(new MacWindowImpl());
Window win = new Dialog(new WindowsWindowImpl());
```

新增平台（Linux X11）只需要新增 `X11WindowImpl`，不需要改任何 Window 类。"""),

        ("TypeScript 实现", r"""```typescript
// 实现层（渲染后端）
interface Renderer {
    renderCircle(radius: number): string;
    renderSquare(size: number): string;
}

class VectorRenderer implements Renderer {
    renderCircle(radius: number) {
        return `Drawing a circle of radius ${radius} using vectors`;
    }
    renderSquare(size: number) {
        return `Drawing a square of size ${size} using vectors`;
    }
}

class RasterRenderer implements Renderer {
    renderCircle(radius: number) {
        return `Drawing a circle of radius ${radius} using pixels`;
    }
    renderSquare(size: number) {
        return `Drawing a square of size ${size} using pixels`;
    }
}

// 抽象层（形状）
abstract class Shape {
    protected renderer: Renderer;
    constructor(renderer: Renderer) { this.renderer = renderer; }
    abstract draw(): string;
}

class Circle extends Shape {
    constructor(private radius: number, renderer: Renderer) { super(renderer); }
    draw() {
        return this.renderer.renderCircle(this.radius);
    }
}

class Square extends Shape {
    constructor(private size: number, renderer: Renderer) { super(renderer); }
    draw() {
        return this.renderer.renderSquare(this.size);
    }
}

// 用法
const circle = new Circle(5, new VectorRenderer());
console.log(circle.draw());  // "Drawing a circle of radius 5 using vectors"
```

新增形状（Triangle / Pentagon）只需扩展抽象层；新增渲染（SVG / Canvas）只需扩展实现层——**两层独立变化**。"""),

        ("适用边界", """✅ **使用场景**：
- 两个独立变化的维度（形状×颜色 / 数据库×协议 / 平台×组件）
- 抽象和实现都要独立扩展
- 避免类层次爆炸（继承层级 > 3）

❌ **避免场景**：
- 只有一维变化（用继承就够了）
- 抽象与实现耦合紧密（拆不开）
- 业务规模小（不值得双层抽象）

🔄 **与 Adapter 区别**：
- **Adapter**：已有接口不兼容，后期适配
- **Bridge**：设计时就知道「抽象和实现」会独立变化，主动解耦

💡 **最佳实践**：
- 抽象层持有实现层的引用（组合）
- 实现层接口要稳定（一旦确定不改）
- 抽象层和实现层通过容器（DI / ServiceLoader）装配"""),

       ])


def ch02_composite() -> None:
    mk("02-gof-structural/composite.md", "Composite 组合模式",
       "树形结构 + 部分-整体 + 文件系统 / DOM / Kubernetes 资源树",
       [
        ("核心问题", """业务中存在「部分-整体」的层次结构（树 / 森林 / 递归结构），客户端需要**一致对待**「单个对象」和「组合对象」。

**真实场景**：
- 文件系统（文件 / 目录）
- HTML DOM（Node / Element / Document）
- 组织架构（员工 / 部门）
- Kubernetes 资源（Pod / Container）
- 公司股权（个人股东 / 公司股东）"""),

        ("核心思想", """将对象组合成树形结构，使客户端对单个对象（Leaf）和组合对象（Composite）使用**一致的接口**。

**两种角色**：
- **Component**：定义统一的接口（`operation()` / `add()` / `remove()` / `getChild()`）
- **Leaf**：叶子节点，没有子节点
- **Composite**：容器节点，包含子节点"""),

        ("实战：文件系统", r"""```typescript
// 统一接口
interface FileSystemNode {
    getName(): string;
    getSize(): number;
    print(indent: string): void;
}

// 叶子：文件
class File implements FileSystemNode {
    constructor(private name: string, private size: number) {}

    getName() { return this.name; }
    getSize() { return this.size; }
    print(indent: string) {
        console.log(`${indent}📄 ${this.name} (${this.size}B)`);
    }
}

// 容器：目录
class Directory implements FileSystemNode {
    private children: FileSystemNode[] = [];

    constructor(private name: string) {}

    add(node: FileSystemNode) { this.children.push(node); }
    remove(node: FileSystemNode) {
        this.children = this.children.filter(c => c !== node);
    }

    getName() { return this.name; }
    getSize(): number {
        return this.children.reduce((sum, c) => sum + c.getSize(), 0);
    }

    print(indent: string) {
        console.log(`${indent}📁 ${this.name}/`);
        this.children.forEach(c => c.print(indent + '  '));
    }
}

// 客户端：一致对待 file 和 directory
const root = new Directory('project');
const src = new Directory('src');
src.add(new File('index.ts', 1200));
src.add(new File('utils.ts', 800));
root.add(src);
root.add(new File('README.md', 2000));
root.add(new File('package.json', 500));

root.print('');
// 输出：
// 📁 project/
//   📁 src/
//     📄 index.ts (1200B)
//     📄 utils.ts (800B)
//   📄 README.md (2000B)
//   📄 package.json (500B)
```

注意 `getSize()` 是**递归**的（directory 把子节点的 size 累加），客户端不需要知道是 file 还是 directory。"""),

        ("Java 实战：AWT/Swing", r"""Java AWT/Swing 组件树是 Composite：

```java
// 统一抽象
public abstract class Component {
    public void add(Component c) { /* ... */ }
    public void paint(Graphics g) { /* 子类实现 */ }
}

// 叶子：Button
public class Button extends Component {
    @Override public void paint(Graphics g) { /* 画按钮 */ }
}

// 容器：Panel（可以装其他 Component）
public class Panel extends Component {
    private List<Component> children = new ArrayList<>();

    @Override public void add(Component c) { children.add(c); }

    @Override public void paint(Graphics g) {
        for (Component c : children) {
            c.paint(g);  // 递归绘制
        }
    }
}

// 客户端：随便嵌套
Panel root = new Panel();
Panel leftPanel = new Panel();
leftPanel.add(new Button("OK"));
leftPanel.add(new Button("Cancel"));
root.add(leftPanel);
root.add(new Label("Hello"));

root.paint(graphics);  // 递归绘制所有
```"""),

        ("实战：Kubernetes 资源树", r"""Kubernetes 资源天然是树形：

```yaml
# Deployment 包含 ReplicaSet
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: nginx
        # Container 是叶子
        resources:
          requests:
            cpu: 100m
---
# Pod 是容器（Composite）
apiVersion: v1
kind: Pod
metadata:
  name: web-abc123
spec:
  containers:
  - name: app
    image: nginx
  - name: sidecar
    image: istio-proxy
```

`kubectl get` 输出天然是树：

```
Deployment/web
├── ReplicaSet/web-abc
│   ├── Pod/web-abc-xyz1
│   │   ├── Container app
│   │   └── Container istio-proxy
│   ├── Pod/web-abc-xyz2
│   └── Pod/web-abc-xyz3
```

## 组织架构（最经典）

```
CEO
├── CTO
│   ├── 后端团队 Lead
│   │   ├── 后端工程师 A
│   │   └── 后端工程师 B
│   └── 前端团队 Lead
│       ├── 前端工程师 C
│       └── 前端工程师 D
├── CFO
└── COO
```

可以用 Composite 模式：
- `Employee` 抽象（所有员工）
- `IndividualEmployee` 叶子（普通员工）
- `Manager` Composite（持有下属列表）"""),

        ("适用边界", """✅ **使用场景**：
- 树形 / 递归结构（文件系统 / DOM / 组织架构）
- 客户端需要一致对待「单个」和「组合」
- 业务核心操作可递归（getSize / print / validate）

❌ **避免场景**：
- 结构不是树（用图或其他）
- 叶子 / Composite 行为差异巨大（强行一致接口会很难看）
- 客户端从不需要「穿透」Composite（直接用具体类更简单）

🔄 **变体**：
- **透明 Composite**：Component 接口包含 add/remove（叶子实现抛异常）
- **安全 Composite**：Component 接口只有通用方法，add/remove 在 Composite 子类

💡 **最佳实践**：
- 透明 Composite 更优雅但有 cast 风险
- 安全 Composite 更安全但失去「一致性」优势
- 推荐用透明 + 运行时检查（leaf 不应被 add）
- Java 用 `instanceof` / TS 用 `in` 操作符判断"""),

       ])


def ch02_decorator() -> None:
    mk("02-gof-structural/decorator.md", "Decorator 装饰器模式",
       "动态添加职责 + Java IO 流 + Go middleware + TypeScript 装饰器 + Spring AOP",
       [
        ("核心问题", """需要给对象动态添加职责，但又不能修改原类。继承的方案是「静态」的（编译期决定），且容易产生子类爆炸。

**真实场景**：
- Java IO 流：FileInputStream → BufferedInputStream → DataInputStream，每层都是一个装饰器
- HTTP 中间件：Logging → Auth → RateLimit，每层都是一个装饰器
- 咖啡价格：美式 + 糖 + 奶 + 巧克力，每加一份都是装饰
- React 高阶组件（HOC）：withRouter / withAuth / withTheme"""),

        ("核心思想", """装饰器持有「被装饰对象」的引用，并实现与被装饰对象**相同的接口**。装饰器在调用被装饰对象的方法前后，添加额外行为。

**关键点**：
- 装饰器与被装饰者实现**相同接口**
- 装饰器持有被装饰者的引用（组合）
- 可以**多层嵌套**装饰
- 运行时决定装饰链"""),

        ("Java IO 经典案例", r"""```java
// 装饰器与被装饰者都是 InputStream
InputStream in = new FileInputStream("data.bin");

// 第 1 层装饰：缓冲
InputStream buffered = new BufferedInputStream(in);

// 第 2 层装饰：支持基本数据类型读取
DataInputStream data = new DataInputStream(buffered);

// 用法：data 同时具备缓冲 + Data 类型读取能力
int magic = data.readInt();
long timestamp = data.readLong();
```

每一层都是装饰器：

| 类 | 装饰的能力 |
|---|---|
| FileInputStream | 基础字节读取 |
| BufferedInputStream | + 内存缓冲（减少 IO 次数） |
| DataInputStream | + 读取 Java 基本类型（int / long / double） |
| GZIPInputStream | + gzip 解压 |

装饰链顺序无关（可以 GZIPInputStream(BufferedInputStream(FileInputStream))）。"""),

        ("Go 中间件", r"""Go 的 HTTP 中间件是装饰器的典范：

```go
type Handler func(ctx *Context)

type Middleware func(Handler) Handler

// 日志中间件
func Logging(next Handler) Handler {
    return func(ctx *Context) {
        start := time.Now()
        log.Printf("--> %s %s", ctx.Method, ctx.Path)
        next(ctx)
        log.Printf("<-- %s %s (%v)", ctx.Method, ctx.Path, time.Since(start))
    }
}

// 鉴权中间件
func Auth(next Handler) Handler {
    return func(ctx *Context) {
        token := ctx.Header("Authorization")
        if !validateToken(token) {
            ctx.Abort(401)
            return
        }
        next(ctx)
    }
}

// 限流中间件
func RateLimit(next Handler) Handler {
    return func(ctx *Context) {
        if !limiter.Allow() {
            ctx.Abort(429)
            return
        }
        next(ctx)
    }
}

// 链式组装（装饰链）
handler := func(ctx *Context) { /* 业务逻辑 */ }

handler = Logging(Auth(RateLimit(handler)))
// 执行顺序：Logging -> Auth -> RateLimit -> business -> RateLimit -> Auth -> Logging
```

每个中间件都是装饰器，包装了下一个 handler 并添加额外逻辑。"""),

        ("TypeScript 装饰器", r"""TypeScript / ES 装饰器是语言级支持：

```typescript
// 类装饰器
function Sealed(constructor: Function) {
    Object.freeze(constructor);
    Object.freeze(constructor.prototype);
}

@Sealed
class User {
    constructor(public name: string) {}
}

// 方法装饰器
function Log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const original = descriptor.value;
    descriptor.value = function (...args: any[]) {
        console.log(`Calling ${propertyKey} with`, args);
        const result = original.apply(this, args);
        console.log(`Result:`, result);
        return result;
    };
}

class Calculator {
    @Log
    add(a: number, b: number) {
        return a + b;
    }
}

new Calculator().add(1, 2);
// Calling add with [1, 2]
// Result: 3
```

NestJS / Angular 的 `@Controller` / `@Get` / `@UseGuards` 都是装饰器：

```typescript
@Controller('/users')
@UseGuards(AuthGuard)
class UserController {
    @Get('/:id')
    getUser(@Param('id') id: string) {
        return this.userService.findById(id);
    }
}
```"""),

        ("与 Proxy 区别", """| | Decorator | Proxy |
|---|---|---|
| 目的 | 增加新职责 | 控制访问 |
| 创建方 | 客户端主动包裹 | 通常由框架/容器创建 |
| 关注点 | 行为增强 | 访问控制（鉴权 / 延迟加载 / 缓存）|
| 数量关系 | 多个叠加 | 通常一层 |"""),

        ("适用边界", """✅ **使用场景**：
- 动态给对象添加职责（编译期不确定）
- 多职责可自由组合（装饰链）
- 避免继承爆炸（每个新职责都生成子类不现实）
- 框架中间件 / 拦截器

❌ **避免场景**：
- 装饰链超过 5 层（debug 困难）
- 装饰顺序影响业务（要明确文档）
- 业务方需要直接访问被装饰者（破坏装饰的意义）

🔄 **替代方案**：
- **继承**：静态、简单、但子类爆炸
- **AOP**：运行时织入，但增加调试复杂度
- **Mixin**：JS / TS 中通过组合实现多继承效果

💡 **最佳实践**：
- 装饰器与被装饰者**同接口**（保证可替换）
- 装饰器构造函数接受被装饰者
- 装饰顺序可能影响业务，要明确文档
- Go 的 Middleware 是社区标准模式"""),

       ])


def ch02_facade() -> None:
    mk("02-gof-structural/facade.md", "Facade 外观模式",
       "子系统统一高层接口 + Spring JdbcTemplate + 第三方 SDK 封装 + API Gateway",
       [
        ("核心问题", """子系统中存在多个相互关联的类（典型如：JDBC 的 Connection/Statement/ResultSet），客户端直接使用这些类需要写大量样板代码（获取连接 / 创建 Statement / 设置参数 / 执行 / 解析结果 / 关闭资源）。

**真实场景**：
- JDBC：Connection/Statement/ResultSet 模板代码
- 第三方 SDK（支付 / OAuth / 短信）：多个 API 调用拼成业务
- 数据库 ORM（MyBatis / Hibernate）：把 SQL 隐藏在方法后面
- 微服务 API Gateway：把多个下游服务聚合成一个接口"""),

        ("核心思想", """为子系统中的一组接口提供一个**统一的高层接口**，使子系统更易使用。

**关键点**：
- Facade 不限制客户端使用子系统（保留高级用法）
- Facade 只是「推荐入口」，简化 80% 场景
- Facade 不增加新功能，只是把现有功能编排"""),

        ("实战：Spring JdbcTemplate", r"""```java
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

MyBatis 在运行时生成 Mapper 的代理实现（Facade），把 JDBC 调用隐藏起来。"""),

        ("实战：支付 SDK 封装", r"""```typescript
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

业务方只依赖 `PaymentFacade`，不用知道底层是支付宝还是微信的 SDK。"""),

        ("实战：API Gateway", r"""微服务的 API Gateway 是宏观层面的 Facade：

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

客户端只需要调 `POST /checkout`，不用知道背后有 4 个微服务。"""),

        ("适用边界", """✅ **使用场景**：
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
- Facade 方法应该和业务用例对应（一个业务 = 一个 Facade 方法）"""),

       ])


def ch02_flyweight() -> None:
    mk("02-gof-structural/flyweight.md", "Flyweight 享元模式",
       "共享细粒度对象 + 减少内存 / Integer 缓存 / 文本编辑器 / 游戏地图 / 字符串池",
       [
        ("核心问题", """应用中需要大量相似对象（百万级 / 千万级），如果每个对象都独立存储，内存消耗巨大。

**真实场景**：
- 文本编辑器：每篇文章 10 万字，每个字符如果独立对象 = 100 MB
- 游戏地图：1000x1000 格子，每个格子独立对象 = 100 万元数据
- Java Integer 缓存：-128~127 是高频整数，全部缓存
- Java String 常量池：所有 `"hello"` 字面量共享一个对象"""),

        ("核心思想", """把对象的**内部状态**（不变的部分）共享，把**外部状态**（变化的部分）从对象中抽离，由客户端在使用时传入。

**两种状态**：
- **内部状态（intrinsic）**：存储在享元对象内部，不随环境变化，可以共享
- **外部状态（extrinsic）**：由客户端传入（参数 / 上下文），享元对象不持有"""),

        ("Java Integer 缓存", r"""```java
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // true（同一对象，缓存命中）

Integer c = 128;
Integer d = 128;
System.out.println(c == d);  // false（不同对象，缓存未命中）

// 装箱
Integer e = Integer.valueOf(127);  // 从缓存取
Integer f = Integer.valueOf(128);  // 新建对象

// IntegerCache 源码（JDK 8+）
private static class IntegerCache {
    static final int low = -128;
    static final int high;  // 默认 127，但可配置 -XX:AutoBoxCacheMax=1000
    static final Integer cache[];

    static {
        int h = 127;
        String integerCacheHighPropValue = sun.misc.VM.getSavedProperty("java.lang.Integer.IntegerCache.high");
        if (integerCacheHighPropValue != null) {
            try { h = Integer.parseInt(integerCacheHighPropValue); } catch (...) {}
        }
        high = h;
        cache = new Integer[(high - low) + 1];
        int j = low;
        for (int k = 0; k < cache.length; k++) cache[k] = new Integer(j++);
    }

    public static Integer valueOf(int i) {
        if (i >= IntegerCache.low && i <= IntegerCache.high)
            return IntegerCache.cache[i + (-IntegerCache.low)];
        return new Integer(i);
    }
}
```

**注意**：`==` 比较引用，不能用于 Integer 一般场景（应该用 `.equals()`）。但在 -128~127 范围内 `==` 恰好为 true，会引发隐蔽 bug。"""),

        ("实战：文本编辑器", r"""```java
class CharacterFlyweight {
    private final char ch;  // 内部状态（共享）
    private final Font font;

    public CharacterFlyweight(char ch, Font font) {
        this.ch = ch;
        this.font = font;
    }

    // 外部状态（位置 / 颜色）作为参数传入
    public void render(int x, int y, Color color) {
        font.drawChar(ch, x, y, color);
    }
}

// 享元工厂
class FontFactory {
    private static final Map<String, CharacterFlyweight> cache = new HashMap<>();

    public static CharacterFlyweight get(char ch, Font font) {
        String key = ch + "_" + font.getName();
        return cache.computeIfAbsent(key, k -> new CharacterFlyweight(ch, font));
    }
}

// 文本编辑器
class Document {
    private List<CharacterPosition> characters = new ArrayList<>();

    public void append(char ch, Font font, int x, int y) {
        // 字符本身（内部状态）从享元工厂取
        CharacterFlyweight fly = FontFactory.get(ch, font);
        // 位置（外部状态）由 Document 保存
        characters.add(new CharacterPosition(fly, x, y));
    }

    public void render() {
        for (CharacterPosition p : characters) {
            p.flyweight.render(p.x, p.y, currentColor);
        }
    }
}
```

**内存计算**：26 个字母 × 4 种字体 = 104 个享元（不管 1000 篇文章 × 10 万字）。
如果不享元：1000 × 100000 = 1 亿个对象。"""),

        ("实战：游戏地图", r"""```typescript
// 地形类型（不变）
class TerrainTile {
    constructor(
        public readonly type: 'grass' | 'water' | 'mountain' | 'forest',
        public readonly texture: string,
        public readonly movementCost: number,
    ) {}

    render(x: number, y: number) {
        console.log(`Drawing ${this.type} at (${x},${y}) with texture ${this.texture}`);
    }
}

// 享元工厂
class TileFactory {
    private static tiles = new Map<string, TerrainTile>();

    static getTile(type: TerrainTile['type']): TerrainTile {
        if (!TileFactory.tiles.has(type)) {
            switch (type) {
                case 'grass': TileFactory.tiles.set(type, new TerrainTile(type, 'grass.png', 1)); break;
                case 'water': TileFactory.tiles.set(type, new TerrainTile(type, 'water.png', 3)); break;
                case 'mountain': TileFactory.tiles.set(type, new TerrainTile(type, 'mountain.png', 5)); break;
                case 'forest': TileFactory.tiles.set(type, new TerrainTile(type, 'forest.png', 2)); break;
            }
        }
        return TileFactory.tiles.get(type)!;
    }
}

// 地图（1000x1000 = 100 万格）
class GameMap {
    private grid: TerrainTile[][] = [];

    load() {
        for (let x = 0; x < 1000; x++) {
            this.grid[x] = [];
            for (let y = 0; y < 1000; y++) {
                const type = this.computeTileType(x, y);
                this.grid[x][y] = TileFactory.getTile(type);  // 共享！
            }
        }
    }

    render() {
        for (let x = 0; x < 1000; x++) {
            for (let y = 0; y < 1000; y++) {
                this.grid[x][y].render(x, y);  // 位置是外部状态
            }
        }
    }
}
```

**内存**：100 万格只有 4 个 TerrainTile 对象（不是 100 万个）。"""),

        ("适用边界", """✅ **使用场景**：
- 大量相似对象（百万级 / 千万级）
- 对象的大部分状态可以外部化
- 对象创建成本高（IO / DB）

❌ **避免场景**：
- 对象数量不大（JVM GC 已经很快）
- 对象状态难以外部化
- 业务需要每个对象独立可变（享元不可变）

🔄 **与缓存的区别**：
- **享元**：在设计阶段就规划共享
- **缓存**：运行时按需缓存（懒加载）

💡 **最佳实践**：
- 享元对象必须是**不可变**的（否则共享会破坏业务）
- 内部状态 vs 外部状态划分要清晰
- 用工厂管理享元（避免重复创建）
- 注意线程安全（共享对象可能是多线程读）"""),

       ])


def ch02_proxy() -> None:
    mk("02-gof-structural/proxy.md", "Proxy 代理模式",
       "控制对象访问 + 远程代理 / 虚拟代理 / 保护代理 / 智能引用 / 缓存代理 + Spring AOP",
       [
        ("核心问题", """需要控制对某个对象的访问（访问前 / 访问时 / 访问后插入逻辑），但又不能或不方便修改对象本身的代码。

**真实场景**：
- 远程访问：RPC 客户端 stub（gRPC / Dubbo / Thrift）
- 延迟加载：浏览器图片懒加载 / Hibernate 实体代理
- 权限控制：Spring Security 鉴权代理
- 缓存：MyBatis 二级缓存 / Caffeine 缓存代理
- 事务：Spring `@Transactional` 用代理织入事务"""),

        ("核心思想", """代理对象与真实对象实现**相同接口**，客户端通过代理访问真实对象，代理在调用真实对象前后可以插入额外逻辑。

**5 种代理**：
| 类型 | 用途 | 案例 |
|---|---|---|
| 远程代理 | 隐藏对象在远程地址 | RPC stub |
| 虚拟代理 | 延迟加载大对象 | 浏览器图片懒加载 |
| 保护代理 | 控制访问权限 | Spring Security |
| 智能引用 | 附加额外行为（计数 / 锁） | 缓存代理 |
| 缓存代理 | 缓存昂贵结果 | MyBatis 二级缓存 |"""),

        ("实战：Spring AOP 代理", r"""Spring AOP 是动态代理的典范：

```java
@Service
public class OrderService {
    @Transactional
    public void createOrder(Order o) {
        // 业务逻辑
    }
}

// Spring 在运行时生成 OrderService 的代理
// 实际注入的是代理对象，不是原 OrderService
OrderService proxy = context.getBean(OrderService.class);

proxy.createOrder(order);
// 代理内部：
// 1. 开启事务（@Transactional）
// 2. 调用真实 OrderService.createOrder(order)
// 3. 提交事务（或异常时回滚）
```

Spring AOP 底层：
- 接口 → JDK 动态代理（基于 InvocationHandler）
- 类 → CGLIB（基于字节码生成子类）

### 自定义 InvocationHandler

```java
public class LoggingHandler implements InvocationHandler {
    private final Object target;

    public LoggingHandler(Object target) { this.target = target; }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        long start = System.nanoTime();
        Object result = method.invoke(target, args);  // 调用真实方法
        long elapsed = System.nanoTime() - start;
        System.out.printf("%s took %dns%n", method.getName(), elapsed);
        return result;
    }
}

// 创建代理
OrderService realService = new OrderServiceImpl();
OrderService proxy = (OrderService) Proxy.newProxyInstance(
    OrderService.class.getClassLoader(),
    new Class<?>[] { OrderService.class },
    new LoggingHandler(realService)
);
```"""),

        ("实战：gRPC 远程代理", r"""gRPC 客户端 stub 是远程代理：

```go
// 自动生成的 stub（.pb.go）
type OrderServiceClient interface {
    CreateOrder(ctx context.Context, in *CreateOrderRequest, opts ...grpc.CallOption) (*CreateOrderResponse, error)
}

type orderServiceClient struct {
    cc *grpc.ClientConn
}

func (c *orderServiceClient) CreateOrder(ctx context.Context, in *CreateOrderRequest, opts ...grpc.CallOption) (*CreateOrderResponse, error) {
    out := new(CreateOrderResponse)
    err := c.cc.Invoke(ctx, "/order.OrderService/CreateOrder", in, out, opts...)
    if err != nil { return nil, err }
    return out, nil
}

// 客户端使用：调 stub 就像调本地方法
conn, _ := grpc.Dial("order-service:50051", grpc.WithInsecure())
client := pb.NewOrderServiceClient(conn)

resp, err := client.CreateOrder(ctx, &pb.CreateOrderRequest{
    UserId: 123,
    Items: []*pb.OrderItem{{ProductId: 456, Quantity: 2}},
})
// 背后：序列化 protobuf → HTTP/2 → 服务端反序列化 → 调用真实实现 → 返回
```

客户端完全感知不到「远程」——这就是远程代理的核心价值。"""),

        ("实战：保护代理（鉴权）", r"""```typescript
// 真实 API
interface UserAPI {
    getUser(id: string): Promise<User>;
    updateUser(id: string, data: Partial<User>): Promise<User>;
    deleteUser(id: string): Promise<void>;
}

// 真实实现
class UserAPIImpl implements UserAPI {
    async getUser(id: string) { /* 调用后端 */ }
    async updateUser(id: string, data: Partial<User>) { /* 调用后端 */ }
    async deleteUser(id: string) { /* 调用后端 */ }
}

// 保护代理：加鉴权
class ProtectedUserAPI implements UserAPI {
    constructor(
        private real: UserAPI,
        private currentUser: User,
        private permissions: Set<string>
    ) {}

    async getUser(id: string) {
        // 读权限检查
        if (!this.permissions.has('user:read')) throw new Error('Forbidden');
        return this.real.getUser(id);
    }

    async updateUser(id: string, data: Partial<User>) {
        if (!this.permissions.has('user:write')) throw new Error('Forbidden');
        // 还可以加：只能修改自己的数据
        if (this.currentUser.id !== id && !this.permissions.has('user:write:any')) {
            throw new Error('Can only update own profile');
        }
        return this.real.updateUser(id, data);
    }

    async deleteUser(id: string) {
        if (!this.permissions.has('user:delete')) throw new Error('Forbidden');
        return this.real.deleteUser(id);
    }
}
```"""),

        ("实战：缓存代理", r"""```typescript
// MyBatis 二级缓存的核心思路
class CachedUserRepo implements UserRepository {
    constructor(
        private realRepo: UserRepository,
        private cache: Map<string, { value: any, expireAt: number }> = new Map(),
        private ttl: number = 60_000  // 60 秒
    ) {}

    async findById(id: string): Promise<User> {
        // 1. 先查缓存
        const cached = this.cache.get(id);
        if (cached && cached.expireAt > Date.now()) {
            return cached.value;
        }

        // 2. 缓存未命中，查真实仓库
        const user = await this.realRepo.findById(id);

        // 3. 写入缓存
        this.cache.set(id, { value: user, expireAt: Date.now() + this.ttl });
        return user;
    }

    async save(user: User): Promise<void> {
        await this.realRepo.save(user);
        this.cache.delete(user.id);  // 失效缓存
    }
}
```"""),

        ("与 Decorator 区别", """| | Proxy | Decorator |
|---|---|---|
| 目的 | 控制访问（鉴权 / 缓存 / 远程）| 增加职责 |
| 创建方 | 通常由框架/容器创建 | 客户端主动包裹 |
| 关注点 | 不改变行为 | 行为增强 |
| 数量 | 通常一层（除非链式代理）| 多层叠加 |

代理侧重「替身」，装饰侧重「增强」。"""),

        ("适用边界", """✅ **使用场景**：
- 远程访问（RPC stub）
- 延迟加载（虚拟代理）
- 权限控制（保护代理）
- 缓存（缓存代理）
- 事务 / 日志（AOP 织入）

❌ **避免场景**：
- 业务逻辑简单（直接调用即可）
- 性能敏感的 hot path（代理有开销）
- 客户端需要直接访问真实对象（破坏代理的封装）

🔄 **与 Decorator 区别**：
- 装饰器由客户端组合
- 代理通常由框架 / 容器创建
- 装饰器侧重增强，代理侧重控制

💡 **最佳实践**：
- JDK 动态代理要求接口，CGLIB 不要求
- Spring 5+ 默认使用 CGLIB（更强大）
- 代理链不要太长（debug 困难）
- 代理本身应该是无业务逻辑的（薄包装）"""),

       ])


# ============================================================================
# Chapter 03: GoF Behavioral (11 stubs)
# ============================================================================

def ch03_chain_of_responsibility() -> None:
    mk("03-gof-behavioral/chain-of-responsibility.md", "Chain of Responsibility 责任链模式",
       "请求沿链传递 + HTTP 中间件 / Servlet Filter / Spring Interceptor",
       [
        ("核心问题", """一个请求需要被多个对象处理（鉴权 → 限流 → 业务），但具体由哪个对象处理在运行时才能确定。

**真实场景**：
- HTTP 中间件：CORS → 鉴权 → 限流 → 业务
- Servlet Filter：字符编码 → 鉴权 → 日志
- 工作流引擎：审批链（组长 → 经理 → 总监 → CEO）
- 异常处理：每个 catch 块都是责任链"""),

        ("核心思想", """把请求的发送者和接收者解耦。让多个对象都有机会处理请求，把这些对象连成一条链，沿链传递请求直到有对象处理它。

**关键点**：
- 每个处理者持有「下一个处理者」的引用
- 请求沿链传递，可在任意节点被处理或终止
- 处理顺序可在运行时配置"""),

        ("Go HTTP 中间件", r"""```go
package middleware

type Handler func(ctx *Context)

type Middleware func(Handler) Handler

// 日志中间件
func Logging(next Handler) Handler {
    return func(ctx *Context) {
        start := time.Now()
        log.Printf("--> %s %s", ctx.Method, ctx.Path)
        next(ctx)
        log.Printf("<-- %s %s (%v)", ctx.Method, ctx.Path, time.Since(start))
    }
}

// 鉴权中间件
func Auth(next Handler) Handler {
    return func(ctx *Context) {
        token := ctx.Header("Authorization")
        if !validateToken(token) {
            ctx.Abort(401)
            return  // 中断后续处理
        }
        next(ctx)
    }
}

// 限流中间件
func RateLimit(next Handler) Handler {
    return func(ctx *Context) {
        if !limiter.Allow(ctx.ClientIP()) {
            ctx.Abort(429)
            return
        }
        next(ctx)
    }
}

// 链式组装
func Chain(handler Handler, mws ...Middleware) Handler {
    // 倒序包裹：先执行的最外层
    for i := len(mws) - 1; i >= 0; i-- {
        handler = mws[i](handler)
    }
    return handler
}

// 用法
handler := func(ctx *Context) {
    ctx.JSON(200, map[string]string{"hello": "world"})
}

handler = Chain(handler, Logging, Auth, RateLimit)
// 执行顺序：Logging -> Auth -> RateLimit -> business -> RateLimit -> Auth -> Logging
```"""),

        ("TypeScript: Express middleware", r"""```typescript
import express, { Request, Response, NextFunction } from 'express';

const app = express();

// 中间件 1：CORS
app.use((req: Request, res: Response, next: NextFunction) => {
    res.header('Access-Control-Allow-Origin', '*');
    next();  // 传给下一个
});

// 中间件 2：JSON 解析
app.use(express.json());

// 中间件 3：日志
app.use((req, res, next) => {
    console.log(`${req.method} ${req.path} at ${new Date().toISOString()}`);
    next();
});

// 中间件 4：鉴权（可以终止）
app.use('/api', (req, res, next) => {
    if (!req.headers.authorization) {
        return res.status(401).send('Unauthorized');  // 不调 next()，链终止
    }
    next();
});

// 业务路由
app.get('/api/users', (req, res) => {
    res.json([{ id: 1, name: 'Alice' }]);
});
```

Express 的中间件就是责任链，`next()` 是传递，`return res.send()` 是终止。"""),

        ("Java Servlet Filter", r"""```java
@WebFilter("/api/*")
public class AuthFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest httpReq = (HttpServletRequest) req;
        String token = httpReq.getHeader("Authorization");

        if (token == null || !validate(token)) {
            ((HttpServletResponse) resp).sendError(401);
            return;  // 不调 chain.doFilter()，链终止
        }

        chain.doFilter(req, resp);  // 传给下一个 filter
    }
}

// web.xml 配置多个 filter 形成链
// <filter-mapping> 按声明顺序执行
```

## Spring Interceptor

```java
public class LoggingInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse resp, Object handler) {
        log.info("preHandle: {}", req.getRequestURI());
        return true;  // true=继续，false=终止
    }

    @Override
    public void postHandle(HttpServletRequest req, HttpServletResponse resp, Object handler, ModelAndView mv) {
        log.info("postHandle: {}", req.getRequestURI());
    }
}

// 注册
@Configuration
public class WebConfig implements WebMvcConfigurer {
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new LoggingInterceptor())
                .addPathPatterns("/api/**")
                .order(1);  // 顺序
    }
}
```"""),

        ("与 Decorator 区别", """| | Chain of Responsibility | Decorator |
|---|---|---|
| 链长度 | 可变（中途可终止） | 固定（每个都执行）|
| 处理方 | 链上某一节点处理 | 所有装饰器叠加 |
| 适用 | 鉴权 / 限流 / 校验 | 流式处理 / 缓存 / 日志 |
| 终止性 | 处理后可不调 next | 必须完成 |

## 与 Pipeline 模式的关系

责任链与 Pipeline 几乎一样，区别：
- Pipeline 通常是同步数据流（一个阶段的输出是下一个的输入）
- 责任链是请求处理（每个节点可独立决定是否处理 / 终止）"""),

        ("适用边界", """✅ **使用场景**：
- HTTP 请求处理链
- 工作流审批
- 异常处理链
- 多层校验（数据校验 → 业务规则校验 → 安全校验）

❌ **避免场景**：
- 链过长（> 10 层，debug 困难）
- 处理顺序有强依赖（明确文档）
- 单个处理者承担太多职责（拆成多个）

🔄 **演进路径**：
- 简单 if-else → 责任链（多个对象处理同一请求）
- 责任链 → Pipeline（数据流）
- 责任链 + 装饰器 = 完整拦截机制（Spring AOP）

💡 **最佳实践**：
- 链节点独立可测试（每个 filter / middleware 单独测）
- 显式终止（不调 next 或 return 响应）
- 中间件顺序明确文档化
- Go 用 `next(ctx)` 命名，TypeScript 用 `next()`"""),

       ])


def ch03_command() -> None:
    mk("03-gof-behavioral/command.md", "Command 命令模式",
       "请求封装为对象 + 撤销重做 + 任务队列 + CQRS / Saga 命令模式",
       [
        ("核心问题", """需要把请求封装为对象，从而支持：
1. 撤销（Undo）
2. 队列化（任务队列）
3. 日志记录（事务）
4. 参数化其他对象（不同请求做参数）
5. 多线程 / 异步执行"""),

        ("核心思想", """把「请求」的所有信息（URL / 参数 / 执行者）封装成一个**对象**。命令对象持有「接收者」的引用，调用 `execute()` 时让接收者执行动作。

**关键角色**：
- **Command**：抽象命令接口（`execute()` / `undo()`）
- **ConcreteCommand**：具体命令（持有 Receiver）
- **Receiver**：真正执行动作的对象
- **Invoker**：调用命令的对象（按钮 / 任务队列）"""),

        ("Java 实现", r"""```java
interface Command {
    void execute();
    void undo();
}

// 接收者
class TextEditor {
    private StringBuilder text = new StringBuilder();

    public void append(String s) { text.append(s); }
    public void delete(int length) { text.delete(text.length() - length, text.length()); }
    public String getText() { return text.toString(); }
}

// 具体命令
class AppendCommand implements Command {
    private final TextEditor editor;
    private final String text;

    public AppendCommand(TextEditor editor, String text) {
        this.editor = editor;
        this.text = text;
    }

    @Override public void execute() { editor.append(text); }
    @Override public void undo() { editor.delete(text.length()); }
}

// 调用者（按钮）
class Button {
    private Command command;
    public void setCommand(Command c) { this.command = c; }
    public void click() { command.execute(); }
}

// 撤销栈
class EditorWithUndo {
    private final TextEditor editor = new TextEditor();
    private final Stack<Command> history = new Stack<>();

    public void append(String text) {
        Command cmd = new AppendCommand(editor, text);
        cmd.execute();
        history.push(cmd);
    }

    public void undo() {
        if (!history.isEmpty()) history.pop().undo();
    }
}

// 用法
EditorWithUndo e = new EditorWithUndo();
e.append("Hello");  // text = "Hello"
e.append(" World"); // text = "Hello World"
e.undo();           // text = "Hello"
e.undo();           // text = ""
```"""),

        ("TypeScript：任务队列", r"""```typescript
interface Command {
    execute(): void;
    undo(): void;
}

class TaskQueue {
    private queue: Command[] = [];
    private history: Command[] = [];

    enqueue(cmd: Command) { this.queue.push(cmd); }
    run() {
        while (this.queue.length) {
            const cmd = this.queue.shift()!;
            cmd.execute();
            this.history.push(cmd);
        }
    }
    undoLast() {
        this.history.pop()?.undo();
    }
}

// 用例：图片编辑器
class AddLayerCommand implements Command {
    constructor(private editor: ImageEditor, private layer: Layer) {}
    execute() { this.editor.addLayer(this.layer); }
    undo() { this.editor.removeLayer(this.layer.id); }
}

class ResizeCommand implements Command {
    constructor(private element: Element, private newSize: Size, private oldSize: Size) {}
    execute() { this.element.size = this.newSize; }
    undo() { this.element.size = this.oldSize; }
}

const queue = new TaskQueue();
queue.enqueue(new AddLayerCommand(editor, layer1));
queue.enqueue(new ResizeCommand(element, { width: 200, height: 100 }, element.size));
queue.run();    // 顺序执行
queue.undoLast(); // 撤销 resize
```"""),

        ("实战：CQRS 命令", r"""CQRS 是 Command 模式的架构升级版：

```java
// 命令端：所有写请求都是 Command
public interface Command {}

public record CreateOrderCommand(String orderId, String userId, List<OrderItem> items) implements Command {}
public record CancelOrderCommand(String orderId, String reason) implements Command {}
public record UpdateShippingCommand(String orderId, Address address) implements Command {}

// 命令总线（类似 TaskQueue）
@Component
public class CommandBus {
    private final Map<Class<? extends Command>, CommandHandler> handlers = new HashMap<>();

    public <C extends Command> void dispatch(C command) {
        CommandHandler<C> handler = (CommandHandler<C>) handlers.get(command.getClass());
        if (handler == null) throw new IllegalArgumentException("No handler for " + command.getClass());
        handler.handle(command);
    }
}

// 命令处理器
@Component
public class CreateOrderCommandHandler implements CommandHandler<CreateOrderCommand> {
    private final OrderRepository repo;
    private final EventPublisher events;

    @Override
    public void handle(CreateOrderCommand cmd) {
        Order order = Order.create(cmd.orderId(), cmd.userId(), cmd.items());
        repo.save(order);
        events.publish(new OrderCreatedEvent(order));
    }
}
```

Axon Framework（Java 生态）就基于这种设计。"""),

        ("适用边界", """✅ **使用场景**：
- 需要撤销/重做（编辑器 / 浏览器历史）
- 任务队列（异步执行）
- 事务（命令对象就是事务日志）
- CQRS 架构（命令端 = Command 模式）
- 宏命令（一组命令组合）

❌ **避免场景**：
- 简单同步调用（直接调用即可）
- 不需要撤销/队列
- 命令对象创建成本高（业务极简时反而是负担）

🔄 **与相关模式区别**：
- **Command**：封装请求，支持撤销 / 队列
- **Strategy**：封装算法，可替换
- **Memento**：保存状态快照
- **CQRS**：Command 模式的架构升级

💡 **最佳实践**：
- 命令对象应该是不可变的（参数在构造时确定）
- 用宏命令（Composite）组合多个命令
- 命令执行前后记录日志（便于追踪）
- 撤销栈有大小限制（避免无限增长）"""),

       ])


def ch03_iterator() -> None:
    mk("03-gof-behavioral/iterator.md", "Iterator 迭代器模式",
       "顺序访问聚合对象 + Java Iterator / Go range / TypeScript Iterable / Rust IntoIterator",
       [
        ("核心问题", """需要**顺序访问**聚合对象中的元素，但不暴露聚合对象的**内部表示**（数组 / 列表 / 树）。

**真实场景**：
- Java Collection（List / Set / Map 都有 Iterator）
- JavaScript for-of（任何实现 Iterable 的对象）
- Rust `for x in vec`（任何实现 IntoIterator 的对象）
- 数据库游标（cursor）"""),

        ("核心思想", """提供一种方法顺序访问聚合对象中的各个元素，而不暴露其内部表示。

**关键角色**：
- **Iterator**：迭代器接口（`hasNext()` / `next()`）
- **ConcreteIterator**：具体迭代器（持有游标 + 聚合引用）
- **Aggregate**：聚合接口（创建迭代器）
- **ConcreteAggregate**：具体聚合（返回具体迭代器）"""),

        ("Java 实现", r"""```java
interface Iterator<E> {
    boolean hasNext();
    E next();
}

interface Iterable<E> {
    Iterator<E> iterator();
}

// 具体迭代器
class ListIterator<E> implements Iterator<E> {
    private final List<E> list;
    private int cursor = 0;

    public ListIterator(List<E> list) { this.list = list; }

    @Override public boolean hasNext() { return cursor < list.size(); }
    @Override public E next() { return list.get(cursor++); }
}

// 具体聚合
class MyList<E> implements Iterable<E> {
    private Object[] elements = new Object[10];
    private int size = 0;

    public void add(E e) { elements[size++] = e; }

    @Override public Iterator<E> iterator() { return new ListIterator<>(Arrays.asList((E[]) elements)); }
}

// 用法
MyList<String> list = new MyList<>();
list.add("a"); list.add("b"); list.add("c");

for (Iterator<String> it = list.iterator(); it.hasNext(); ) {
    System.out.println(it.next());
}

// 或 Java 5+ foreach（语法糖）
for (String s : list) {
    System.out.println(s);
}
```

## Java 8+ Stream API

```java
list.stream()
    .filter(s -> s.length() > 1)
    .map(String::toUpperCase)
    .forEach(System.out::println);
```"""),

        ("Go range 与 自定义迭代器", r"""```go
// 基本类型直接用 range
for i, v := range []string{"a", "b", "c"} {
    fmt.Println(i, v)
}

// Map
m := map[string]int{"a": 1, "b": 2}
for k, v := range m {
    fmt.Println(k, v)
}

// 自定义迭代器（Go 1.23+ range over func）
type Counter struct{ max int }

func (c *Counter) Yield() func() (int, bool) {
    i := 0
    return func() (int, bool) {
        if i < c.max {
            i++
            return i, true
        }
        return 0, false
    }
}

// Go 1.23+
c := &Counter{max: 5}
for v := range c.Yield() {
    fmt.Println(v)
}
// 1 2 3 4 5

// Go 1.22 及更早：用 callback 模拟
type Iter[T any] struct {
    next func() (T, bool)
}

func (it Iter[T]) ForEach(fn func(T)) {
    for v, ok := it.next(); ok; v, ok = it.next() {
        fn(v)
    }
}
```"""),

        ("TypeScript Iterable Protocol", r"""```typescript
// 实现 Symbol.iterator 协议
class Range implements Iterable<number> {
    constructor(private from: number, private to: number) {}

    *[Symbol.iterator]() {
        for (let i = this.from; i <= this.to; i++) {
            yield i;
        }
    }
}

// 用法：for-of
for (const n of new Range(1, 5)) {
    console.log(n);  // 1 2 3 4 5
}

// 用法：spread
const arr = [...new Range(1, 5)];  // [1, 2, 3, 4, 5]

// 用法：Array.from
const arr2 = Array.from(new Range(1, 5));  // [1, 2, 3, 4, 5]

// 用法：解构
const [first, second, ...rest] = new Range(1, 5);
// first=1, second=2, rest=[3,4,5]

// 异步迭代器
class AsyncStream implements AsyncIterable<number> {
    async *[Symbol.asyncIterator]() {
        yield 1;
        await new Promise(r => setTimeout(r, 1000));
        yield 2;
        yield 3;
    }
}

for await (const n of new AsyncStream()) {
    console.log(n);  // 1 (1s 后) 2 3
}
```"""),

        ("实战：数据库游标", r"""数据库游标是迭代器的天然案例：

```java
// JDBC ResultSet 就是迭代器
try (Connection conn = dataSource.getConnection();
     Statement stmt = conn.createStatement();
     ResultSet rs = stmt.executeQuery("SELECT * FROM users")) {
    while (rs.next()) {  // 迭代
        long id = rs.getLong("id");
        String name = rs.getString("name");
        // 处理一行
    }
}

// Spring JdbcTemplate + RowCallbackHandler
jdbcTemplate.query("SELECT * FROM large_table", rs -> {
    // 每行回调
});

// 流式 API（避免一次性加载到内存）
@Query("SELECT u FROM User u")
Stream<User> findAllStream();  // Hibernate stream

try (Stream<User> stream = repo.findAllStream()) {
    stream.forEach(user -> {
        // 处理一行
    });
}
```

流式迭代器只把当前行加载到内存，PB 级数据也能处理。"""),

        ("适用边界", """✅ **使用场景**：
- 集合遍历（List / Set / Map）
- 数据库游标（流式查询）
- 树形结构遍历（DFS / BFS）
- 自定义顺序访问

❌ **避免场景**：
- 直接用 for-each / range 更简单
- 随机访问为主（迭代器是单向的）
- 业务需要并行遍历（迭代器通常不是线程安全的）

🔄 **与 for-each 关系**：
- Java 的 for-each 就是 Iterator 的语法糖
- Python 的 for-in 也是迭代器协议
- JavaScript 的 for-of 调用 Symbol.iterator

💡 **最佳实践**：
- 迭代器应该是单向的（next() 不支持 previous）
- 用 fail-fast（检测到结构性修改抛 ConcurrentModificationException）
- Go 1.23+ 可以直接 range over function
- TypeScript 用 Generator (`function*`) 实现最简洁"""),

       ])


def ch03_mediator() -> None:
    mk("03-gof-behavioral/mediator.md", "Mediator 中介者模式",
       "集中对象间交互 + 聊天室 / GUI 组件协作 / MediatR / NestJS EventBus",
       [
        ("核心问题", """多个对象之间相互依赖，形成「网状」通信。如果新加一个对象，需要知道所有其他对象的接口，扩展困难。

**举例**：
- GUI 对话框：5 个组件（按钮 / 文本框 / 下拉框 / 复选框 / 列表）互相联动（按钮启用取决于文本框非空，复选框切换禁用下拉框...）
- 聊天室：N 个用户两两通信，N² 个关系
- 航空管制：N 架飞机由一个塔台协调"""),

        ("核心思想", """用一个中介对象来封装一系列对象的交互。中介者使各对象不需要显式相互引用，从而使其耦合松散，而且可以独立地改变它们之间的交互。

**关键点**：
- 各同事（Colleague）只与中介者通信
- 中介者知道所有同事的接口
- 中介者承担协调逻辑（复杂的同事间关系）"""),

        ("TypeScript：聊天室", r"""```typescript
// 中介者接口
interface ChatMediator {
    send(msg: string, from: User, to?: User): void;
    register(user: User): void;
}

// 具体中介者
class ChatRoom implements ChatMediator {
    private users: User[] = [];

    register(user: User) {
        this.users.push(user);
        user.setMediator(this);  // 注入中介者
    }

    send(msg: string, from: User, to?: User) {
        if (to) {
            // 私聊
            to.receive(msg, from);
        } else {
            // 群聊
            this.users.filter(u => u !== from).forEach(u => u.receive(msg, from));
        }
    }
}

// 同事
class User {
    constructor(private name: string, private mediator?: ChatMediator) {}

    setMediator(m: ChatMediator) { this.mediator = m; }

    send(msg: string, to?: User) {
        console.log(`${this.name} 发送: ${msg}`);
        this.mediator?.send(msg, this, to);
    }

    receive(msg: string, from: User) {
        console.log(`${this.name} 收到 from ${from.name}: ${msg}`);
    }
}

// 用法
const room = new ChatRoom();
const alice = new User('Alice');
const bob = new User('Bob');
const carol = new User('Carol');

room.register(alice);
room.register(bob);
room.register(carol);

alice.send('大家好');        // Bob, Carol 收到
bob.send('Hi Alice', alice); // Alice 收到（私聊）
```

各 User 只依赖 Mediator 接口，不需要知道其他 User 的存在。"""),

        ("实战：GUI 组件", r"""```java
// 中介者
class DialogMediator {
    private TextField nameField;
    private Button submitButton;
    private Checkbox agreeCheckbox;

    public void onNameChanged() {
        // 文本框非空且勾选 → 启用按钮
        submitButton.setEnabled(
            !nameField.getText().isEmpty() && agreeCheckbox.isChecked());
    }

    public void onAgreeChanged() {
        onNameChanged();  // 复用逻辑
    }

    public void onSubmit() {
        if (!submitButton.isEnabled()) return;
        System.out.println("Submit: " + nameField.getText());
    }

    // 注入组件
    public void setNameField(TextField f) { this.nameField = f; }
    public void setSubmitButton(Button b) { this.submitButton = b; }
    public void setAgreeCheckbox(Checkbox c) { this.agreeCheckbox = c; }
}

// 组件
class TextField {
    private String text = "";
    private DialogMediator mediator;

    public void setMediator(DialogMediator m) { this.mediator = m; }
    public void setText(String t) { this.text = t; mediator.onNameChanged(); }
    public String getText() { return text; }
}

// 类似 Checkbox / Button
```

不引入中介者的话：TextField 需要知道 Button 和 Checkbox 的存在，组件间形成网状依赖。"""),

        ("实战：MediatR (C# / .NET)", r"""MediatR 是 Mediator 模式在 .NET 的事实标准：

```csharp
// 请求（命令 / 查询）
public record CreateOrderCommand(string UserId, List<OrderItem> Items) : IRequest<Order>;

public record GetOrderQuery(string OrderId) : IRequest<Order>;

// 处理器
public class CreateOrderHandler : IRequestHandler<CreateOrderCommand, Order>
{
    private readonly IOrderRepository _repo;
    public CreateOrderHandler(IOrderRepository repo) { _repo = repo; }

    public async Task<Order> Handle(CreateOrderCommand cmd, CancellationToken ct) {
        var order = Order.Create(cmd.UserId, cmd.Items);
        await _repo.SaveAsync(order);
        return order;
    }
}

// Controller 中通过中介者调用（不直接依赖 handler）
public class OrderController : ControllerBase
{
    private readonly IMediator _mediator;

    public OrderController(IMediator mediator) { _mediator = mediator; }

    [HttpPost]
    public async Task<Order> Create([FromBody] CreateOrderCommand cmd) {
        return await _mediator.Send(cmd);  // 中介者分发
    }
}
```

Controller 不直接依赖 Handler，所有请求通过 `_mediator.Send()` 分发，天然解耦。"""),

        ("NestJS EventBus", r"""```typescript
// 中介者：EventBus
@Injectable()
export class EventBusService {
    private handlers = new Map<string, Function[]>();

    on(event: string, handler: Function) {
        if (!this.handlers.has(event)) this.handlers.set(event, []);
        this.handlers.get(event)!.push(handler);
    }

    emit(event: string, payload: any) {
        const handlers = this.handlers.get(event) || [];
        handlers.forEach(h => h(payload));
    }
}

// 各服务通过 EventBus 通信
@Injectable()
export class OrderService {
    constructor(private bus: EventBusService) {}

    async create(req: CreateOrderRequest) {
        const order = await this.repo.save(req);
        this.bus.emit('order.created', order);  // 发事件
    }
}

@Injectable()
export class NotificationService {
    constructor(private bus: EventBusService) {
        this.bus.on('order.created', (order: Order) => {
            this.sendEmail(order);  // 订阅事件
        });
    }
}
```

OrderService 不直接调 NotificationService，通过 EventBus 解耦。"""),

        ("适用边界", """✅ **使用场景**：
- 多个对象互相依赖（网状关系）
- GUI 对话框组件协作
- 聊天室 / 论坛 / 多 Agent 系统
- 微服务事件总线（弱耦合）

❌ **避免场景**：
- 对象间无复杂交互（直接调用即可）
- 只有 2-3 个对象（中介者反而是冗余）
- 中介者本身变成 God Class（要知道所有同事的接口）

🔄 **与 Facade 区别**：
- **Mediator**：双向通信（同事通过中介者交互）
- **Facade**：单向（客户端通过 Facade 使用子系统）

🔄 **与 Observer 区别**：
- **Mediator**：主动协调（中央调度）
- **Observer**：被动通知（发布订阅）

💡 **最佳实践**：
- 中介者接口要稳定（一旦确定不改）
- 同事类不知道中介者内部实现
- 警惕中介者膨胀（必要时拆为多个）"""),

       ])


def ch03_memento() -> None:
    mk("03-gof-behavioral/memento.md", "Memento 备忘录模式",
       "保存恢复对象状态 + 撤销操作 / 数据库快照 / Redux undo / Git 内部原理",
       [
        ("核心问题", """需要在不破坏封装性的前提下，捕获对象的内部状态，并在该对象之外保存这个状态，以便以后恢复。

**真实场景**：
- 撤销操作（编辑器 / IDE / Photoshop）
- 数据库快照（Redis RDB / PostgreSQL PITR）
- 游戏存档（保存当前进度）
- Git 内部（每次 commit 是对象状态的 memento）"""),

        ("核心思想", """用三个角色协作：
1. **Originator（原发器）**：要保存状态的对象
2. **Memento（备忘录）**：存储 Originator 的内部状态
3. **Caretaker（管理者）**：管理 Memento（保存栈 / 队列）

关键点：Memento 只暴露「窄接口」给 Caretaker（`getState()`），暴露「宽接口」给 Originator（`setState()`）。"""),

        ("TypeScript 实战：编辑器", r"""```typescript
// Memento：不可变快照
class EditorMemento {
    constructor(public readonly content: string) {}
}

// Originator：编辑器
class Editor {
    private content = '';

    type(text: string) { this.content += text; }
    save(): EditorMemento {
        return new EditorMemento(this.content);  // 创建快照
    }
    restore(m: EditorMemento) {
        this.content = m.content;  // 恢复
    }
    getContent() { return this.content; }
}

// Caretaker：撤销栈
class History {
    private stack: EditorMemento[] = [];

    push(m: EditorMemento) { this.stack.push(m); }
    pop(): EditorMemento | undefined { return this.stack.pop(); }
}

// 用法
const editor = new Editor();
const history = new History();

editor.type('Hello');
history.push(editor.save());
editor.type(' World');
history.push(editor.save());
editor.type('!');

console.log(editor.getContent());  // "Hello World!"

editor.restore(history.pop()!);    // 撤销 !
console.log(editor.getContent());  // "Hello World"

editor.restore(history.pop()!);    // 撤销 World
console.log(editor.getContent());  // "Hello"
```"""),

        ("Java 实战", r"""```java
// Memento（不可变快照）
public final class EditorMemento {
    private final String content;
    public EditorMemento(String content) { this.content = content; }
    public String getContent() { return content; }  // 窄接口给 Caretaker
}

// Originator
public class Editor {
    private StringBuilder content = new StringBuilder();

    public void type(String text) { content.append(text); }
    public EditorMemento save() { return new EditorMemento(content.toString()); }
    public void restore(EditorMemento m) { this.content = new StringBuilder(m.getContent()); }
    public String getContent() { return content.toString(); }
}

// Caretaker
public class History {
    private final Deque<EditorMemento> stack = new ArrayDeque<>();
    public void push(EditorMemento m) { stack.push(m); }
    public EditorMemento pop() { return stack.pop(); }
}
```"""),

        ("实战：数据库快照", r"""数据库的快照（snapshot）本质是 Memento：

```bash
# Redis RDB 快照（fork + copy-on-write）
> SAVE  # 阻塞式保存（生产禁用）
> BGSAVE  # 后台 fork 子进程，父进程继续服务

# 生成的 dump.rdb 是 Redis 数据集的 memento
```

PostgreSQL PITR（Point-in-Time Recovery）：

```sql
-- 基准备份（memento 1）
pg_basebackup -D /backup/base

-- WAL 日志（后续变更记录）
-- recovery 时把 base + WAL replay 到指定时间点
```

## Git 内部

每次 `git commit` 是工作区 + 暂存区的 memento：

```bash
git commit -m "feat: add login"
# 创建 commit 对象，包含：
# - tree（暂存区快照）
# - parent（前一个 commit）
# - author / message

git reset HEAD~1  # 撤销最后一次 commit（memento.pop()）
```

Git 的 reflog 是撤销栈的实现。"""),

        ("适用边界", """✅ **使用场景**：
- 撤销/重做（编辑器 / IDE）
- 数据库快照 / 事务回滚
- 游戏存档
- 长流程表单（保存草稿）
- 命令模式 + Memento = 可撤销命令

❌ **避免场景**：
- 对象状态很简单（直接保存就行）
- 快照成本很高（大数据对象序列化慢）
- 撤销栈无大小限制（内存泄漏）
- 业务不需要回退

🔄 **与 Command 区别**：
- **Memento**：保存状态快照（被动）
- **Command**：保存操作（主动）

🔄 **与 Prototype 区别**：
- **Prototype**：克隆对象（深拷贝）
- **Memento**：只快照部分状态（窄接口）

💡 **最佳实践**：
- Memento 应该不可变（避免 Caretaker 篡改）
- 撤销栈有大小限制（默认 50 ~ 100）
- 大对象 Memento 考虑增量快照
- Memento 序列化要考虑兼容性（不同版本的对象结构）"""),

       ])


def ch03_observer() -> None:
    mk("03-gof-behavioral/observer.md", "Observer 观察者模式",
       "一对多依赖 + 事件总线 + Vue 响应式 / Kafka consumer / Node EventEmitter / Spring Event",
       [
        ("核心问题", """一个对象的状态改变需要自动通知其他多个对象，且这些对象在编译期不知道具体是谁（运行时绑定）。

**真实场景**：
- GUI 按钮点击 → 更新多个 UI
- 微博关注：博主发文 → 所有粉丝收到通知
- Kafka topic：producer 发消息 → 所有 consumer 收到
- Vue 响应式：data 变化 → 自动更新所有依赖它的视图"""),

        ("核心思想", """定义对象间的一种一对多依赖关系，当一个对象（Subject）状态改变时，所有依赖它的对象（Observer）都得到通知并自动更新。

**关键点**：
- Subject 持有 Observer 列表
- Subject 提供 `subscribe()` / `unsubscribe()` / `notify()` 接口
- Observer 实现 `update()` 接口
- 通知可以是同步或异步"""),

        ("TypeScript：事件总线", r"""```typescript
class Subject {
    private observers: ((data: any) => void)[] = [];

    subscribe(fn: (data: any) => void): () => void {
        this.observers.push(fn);
        // 返回 unsubscribe
        return () => {
            this.observers = this.observers.filter(o => o !== fn);
        };
    }

    notify(data: any) {
        this.observers.forEach(fn => fn(data));
    }

    setState(newState: any) {
        this.notify(newState);  // 状态变化通知所有观察者
    }
}

// 用法
const subject = new Subject();

const unsub1 = subject.subscribe(data => console.log('观察者 1:', data));
const unsub2 = subject.subscribe(data => console.log('观察者 2:', data));

subject.setState('Hello');  // 观察者 1: Hello / 观察者 2: Hello

unsub1();  // 取消订阅

subject.setState('World');  // 观察者 2: World（观察者 1 不再收到）
```"""),

        ("Vue 3 响应式原理", r"""Vue 3 的响应式系统就是 Observer 模式：

```typescript
import { ref, watchEffect } from 'vue';

const count = ref(0);

// 第一次执行 watchEffect 时：
// 1. 读取 count.value（触发 track / 收集依赖）
// 2. 缓存当前 watchEffect 回调到 count 的依赖列表
watchEffect(() => {
    console.log(`count = ${count.value}`);
});

// 修改 count.value：
// 1. 触发 trigger
// 2. 通知所有依赖 watchEffect 回调重新执行
count.value++;
// 控制台：count = 1
```

**核心实现**（简化）：

```typescript
// dep 数组保存所有订阅当前 ref 的 effect
class Ref<T> {
    private _value: T;
    private deps: Set<Effect> = new Set();

    constructor(value: T) { this._value = value; }

    get value(): T {
        track(this);  // 把当前 effect 加入 deps
        return this._value;
    }

    set value(newValue: T) {
        this._value = newValue;
        trigger(this);  // 执行 deps 中所有 effect
    }
}
```

## Node.js EventEmitter

```javascript
const EventEmitter = require('events');

class MyEmitter extends EventEmitter {}
const emitter = new MyEmitter();

emitter.on('event', (data) => {
    console.log('listener 1:', data);
});

emitter.on('event', (data) => {
    console.log('listener 2:', data);
});

emitter.emit('event', { msg: 'Hello' });
// listener 1: { msg: 'Hello' }
// listener 2: { msg: 'Hello' }
```"""),

        ("实战：Kafka Consumer", r"""Kafka topic 是 Observer 模式在分布式系统的实现：

```java
// Kafka consumer 是 Observer，自动接收 producer 的消息
@KafkaListener(topics = "order-events", groupId = "notification-service")
public void onOrderCreated(ConsumerRecord<String, OrderEvent> record) {
    OrderEvent event = record.value();
    // 处理订单事件（发邮件 / 发短信）
    emailService.send(event.getUserId(), "您的订单已创建");
}

// 多 consumer 在同一个 group 中（每条消息只被一个 consumer 处理）
@KafkaListener(topics = "order-events", groupId = "analytics-service")
public void onOrderCreated(ConsumerRecord<String, OrderEvent> record) {
    analytics.track(event);  // 同一个事件，但 analytics service 也订阅了
}
```

## Spring Event

```java
// 发布事件
@Service
public class OrderService {
    @Autowired ApplicationEventPublisher publisher;

    public void createOrder(Order o) {
        orderRepo.save(o);
        publisher.publishEvent(new OrderCreatedEvent(o));  // 通知所有监听者
    }
}

// 监听者 1
@Component
public class NotificationListener {
    @EventListener
    public void onOrderCreated(OrderCreatedEvent e) {
        emailService.send(e.getOrder().getUserId(), "订单创建");
    }
}

// 监听者 2
@Component
public class AnalyticsListener {
    @EventListener
    public void onOrderCreated(OrderCreatedEvent e) {
        analytics.track(e.getOrder());
    }
}
```

OrderService 不直接依赖 NotificationService / AnalyticsService。"""),

        ("适用边界", """✅ **使用场景**：
- 事件驱动架构（微服务通信）
- UI 响应式（Vue / React）
- 跨服务通知（Kafka / RabbitMQ）
- 异步任务分发
- 数据库 binlog 订阅（Debezium）

❌ **避免场景**：
- 同步强一致需求（Observer 是最终一致）
- 简单一对调用（直接调即可）
- 订阅者执行缓慢（要异步 + 背压）
- 订阅者异常影响发布者（要 try-catch + 隔离）

🔄 **与 Mediator 区别**：
- **Observer**：单向通知（被观察者不知道观察者）
- **Mediator**：双向协调（同事通过中介者交互）

🔄 **与 Pub/Sub 区别**：
- **Observer**：通常在同一进程
- **Pub/Sub**：跨进程（Redis / Kafka）

💡 **最佳实践**：
- 异步通知 + 错误处理（订阅者异常不传播）
- 订阅者幂等（可能被多次通知）
- 避免循环订阅（A 通知 B，B 通知 A）
- 大量订阅考虑 Pub/Sub 中间件"""),

       ])


def ch03_state() -> None:
    mk("03-gof-behavioral/state.md", "State 状态模式",
       "行为随状态变化 + 订单状态机 / TCP 连接状态 / Spring StateMachine",
       [
        ("核心问题", """对象的行为随着其**内部状态**的改变而改变，看起来好像修改了它的类。

**真实场景**：
- 订单状态机：待支付 → 已支付 → 已发货 → 已完成 / 已取消
- TCP 连接：CLOSED → LISTEN → SYN_SENT → ESTABLISHED → ...
- 电梯状态：停止 / 运行 / 维修 / 故障
- 文档状态：草稿 / 审核中 / 已发布 / 已归档
- 工作流引擎节点状态"""),

        ("核心思想", """将「状态」封装成独立的类，把「状态相关的行为」从原对象移到状态类中。对象（Context）持有当前状态对象引用，把行为委托给状态对象。

**关键角色**：
- **Context**：持有当前状态，处理客户端请求
- **State**：状态接口（每个状态对应一个行为）
- **ConcreteState**：具体状态实现"""),

        ("Java 实战：订单状态机", r"""```java
// 状态接口
public interface OrderState {
    OrderState pay(Order order);             // 支付
    OrderState ship(Order order);             // 发货
    OrderState complete(Order order);         // 完成
    OrderState cancel(Order order);           // 取消
}

// 具体状态
public class PendingState implements OrderState {
    @Override public OrderState pay(Order o) {
        System.out.println("支付成功");
        return new PaidState();
    }
    @Override public OrderState ship(Order o) {
        throw new IllegalStateException("未支付不能发货");
    }
    @Override public OrderState complete(Order o) {
        throw new IllegalStateException("未支付不能完成");
    }
    @Override public OrderState cancel(Order o) {
        System.out.println("订单已取消");
        return new CancelledState();
    }
}

public class PaidState implements OrderState {
    @Override public OrderState ship(Order o) {
        System.out.println("已发货");
        return new ShippedState();
    }
    @Override public OrderState cancel(Order o) {
        System.out.println("已退款");
        return new CancelledState();
    }
    // ...
}

// 类似 ShippedState / CompletedState / CancelledState

// Context
public class Order {
    private OrderState state;

    public Order() { this.state = new PendingState(); }

    public void setState(OrderState s) { this.state = s; }

    public void pay() { this.state = this.state.pay(this); }
    public void ship() { this.state = this.state.ship(this); }
    public void complete() { this.state = this.state.complete(this); }
    public void cancel() { this.state = this.state.cancel(this); }
}

// 用法
Order order = new Order();
order.pay();     // PendingState → PaidState
order.ship();    // PaidState → ShippedState
order.complete();// ShippedState → CompletedState
// order.ship(); // 抛 IllegalStateException（已完成不能再发货）
```"""),

        ("TypeScript：TCP 简化版", r"""```typescript
interface TCPState {
    open(): TCPState;
    close(): TCPState;
    send(data: Buffer): TCPState;
    receive(): { data: Buffer; state: TCPState };
}

class ClosedState implements TCPState {
    open() {
        console.log('OPEN → LISTEN');
        return new ListenState();
    }
    close() {
        console.log('Already CLOSED');
        return this;
    }
    send() { throw new Error('Cannot send on closed connection'); }
    receive() { throw new Error('Cannot receive on closed connection'); }
}

class ListenState implements TCPState {
    open() {
        console.log('Already LISTEN');
        return this;
    }
    close() {
        console.log('LISTEN → CLOSED');
        return new ClosedState();
    }
    send() { throw new Error('LISTEN cannot send'); }
    receive() {
        // 收到 SYN → SYN_SENT
        return { data: Buffer.from('SYN'), state: new SynSentState() };
    }
}

class EstablishedState implements TCPState {
    open() {
        console.log('Already ESTABLISHED');
        return this;
    }
    close() {
        console.log('ESTABLISHED → CLOSED');
        return new ClosedState();
    }
    send(data: Buffer) {
        console.log('Sending data:', data);
        return this;
    }
    receive() {
        // 实际场景会有 buffer
        return { data: Buffer.alloc(0), state: this };
    }
}

// 类似 SynSentState / SynReceivedState / EstablishedState / ...

// Context
class TCPConnection {
    private state: TCPState = new ClosedState();

    open() { this.state = this.state.open(); }
    close() { this.state = this.state.close(); }
    send(data: Buffer) { this.state = this.state.send(data); }
}
```"""),

        ("实战：Spring StateMachine", r"""Spring 有官方的 StateMachine 框架：

```java
@Configuration
@EnableStateMachine
public class OrderStateMachineConfig extends StateMachineConfigurerAdapter<OrderState, OrderEvent> {

    @Override
    public void configure(StateMachineStateConfigurer<OrderState, OrderEvent> states) {
        states.withStates()
            .initial(pending)
            .states(Set.of(pending, paid, shipped, completed, cancelled))
            .end(completed)
            .end(cancelled);
    }

    @Override
    public void configure(StateMachineTransitionConfigurer<OrderState, OrderEvent> transitions) {
        transitions.withExternal()
            .source(pending).target(paid).event(OrderEvent.PAY)
            .and().withExternal()
            .source(paid).target(shipped).event(OrderEvent.SHIP)
            .and().withExternal()
            .source(shipped).target(completed).event(OrderEvent.COMPLETE)
            .and().withExternal()
            .source(pending).target(cancelled).event(OrderEvent.CANCEL)
            .and().withExternal()
            .source(paid).target(cancelled).event(OrderEvent.CANCEL);
    }
}

// 用法
@Service
public class OrderService {
    @Autowired StateMachine<OrderState, OrderEvent> stateMachine;

    public void pay(Long orderId) {
        stateMachine.sendEvent(MessageBuilder.withPayload(OrderEvent.PAY).build());
        // 状态自动转换 + 持久化
    }
}
```"""),

        ("与 Strategy 区别", """| | State | Strategy |
|---|---|---|
| 状态转换 | 状态间互相切换 | 互相独立，客户端选择 |
| 数量 | 通常有限状态机 | 多个等价的算法 |
| 触发 | 内部事件驱动 | 客户端主动选择 |
| 封装性 | 通常是 Context 内部的状态 | 通常是注入到 Context 的策略 |"""),

        ("适用边界", """✅ **使用场景**：
- 有限状态机（订单 / 工作流 / 协议状态）
- 业务规则复杂的状态转换
- UI 表单的步骤流转
- 设备状态管理

❌ **避免场景**：
- 状态极少（≤ 2 个，if-else 即可）
- 状态之间没有强转换约束
- 状态不需要携带自己的行为（只是数据）

🔄 **替代方案**：
- **switch-case / if-else**：状态少时简单
- **状态机库**：Spring StateMachine / XState / Stateless4j
- **数据库触发器**：业务状态由数据库管理

💡 **最佳实践**：
- 状态类持有 Context 引用（反向访问）
- 转换逻辑放在状态类里（不在 Context 中）
- 状态转换记录日志（审计）
- 持久化状态（重启可恢复）"""),

       ])


def ch03_strategy() -> None:
    mk("03-gof-behavioral/strategy.md", "Strategy 策略模式",
       "算法族互相替换 + 支付方式 / 排序算法 / 压缩算法 / Spring @Conditional",
       [
        ("核心问题", """需要在运行时选择算法的具体实现（多种算法实现同一接口），且算法经常变化或新增。

**真实场景**：
- 支付方式（支付宝 / 微信 / PayPal / Stripe）
- 排序算法（冒泡 / 快速 / 归并 / 堆排序）
- 压缩算法（gzip / zstd / lz4 / snappy）
- 路线规划（最短距离 / 最少时间 / 避开收费）
- 推荐算法（协同过滤 / 内容相似 / 深度学习）"""),

        ("核心思想", """定义一系列算法，把它们**一个个封装起来**，并且使它们可以**互相替换**。

**关键角色**：
- **Strategy**：策略接口（所有算法实现同一接口）
- **ConcreteStrategy**：具体策略
- **Context**：持有策略引用，按需调用"""),

        ("TypeScript：支付方式", r"""```typescript
interface PaymentStrategy {
    pay(amount: number): Promise<PaymentResult>;
}

class AlipayStrategy implements PaymentStrategy {
    async pay(amount: number): Promise<PaymentResult> {
        // 调用支付宝 SDK
        return { success: true, transactionId: 'alipay_' + Date.now() };
    }
}

class WechatPayStrategy implements PaymentStrategy {
    async pay(amount: number): Promise<PaymentResult> {
        // 调用微信支付 SDK
        return { success: true, transactionId: 'wxpay_' + Date.now() };
    }
}

class PayPalStrategy implements PaymentStrategy {
    async pay(amount: number): Promise<PaymentResult> {
        // 调用 PayPal SDK
        return { success: true, transactionId: 'pp_' + Date.now() };
    }
}

// Context
class PaymentContext {
    constructor(private strategy: PaymentStrategy) {}

    setStrategy(s: PaymentStrategy) { this.strategy = s; }

    async execute(amount: number) {
        return this.strategy.pay(amount);
    }
}

// 用法
const ctx = new PaymentContext(new AlipayStrategy());
await ctx.execute(100);

ctx.setStrategy(new WechatPayStrategy());
await ctx.execute(200);

ctx.setStrategy(new PayPalStrategy());
await ctx.execute(300);

// 新增支付方式：只需要新增一个 Strategy 类，不改其他代码
```"""),

        ("与 if-else 对比", r"""```typescript
// ❌ if-else 地狱
function pay(method: string, amount: number) {
    if (method === 'alipay') {
        // 20 行支付宝逻辑
    } else if (method === 'wechat') {
        // 20 行微信逻辑
    } else if (method === 'paypal') {
        // 20 行 PayPal 逻辑
    }
    // 新增支付方式必须改这里（违反开闭原则）
}

// ✅ 策略模式
function pay(strategy: PaymentStrategy, amount: number) {
    return strategy.pay(amount);  // 新增策略只需新增类
}

// 类型安全
// 不会传错 method（编译期检查）
```"""),

        ("Java 实战：压缩算法", r"""```java
public interface CompressionStrategy {
    byte[] compress(byte[] data);
    byte[] decompress(byte[] data);
}

public class GzipStrategy implements CompressionStrategy {
    @Override public byte[] compress(byte[] data) {
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream();
             GZIPOutputStream gzos = new GZIPOutputStream(baos)) {
            gzos.write(data);
            return baos.toByteArray();
        } catch (IOException e) { throw new RuntimeException(e); }
    }
    @Override public byte[] decompress(byte[] data) {
        try (GZIPInputStream gzis = new GZIPInputStream(new ByteArrayInputStream(data));
             ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            gzis.transferTo(baos);
            return baos.toByteArray();
        } catch (IOException e) { throw new RuntimeException(e); }
    }
}

public class Lz4Strategy implements CompressionStrategy { /* LZ4 实现 */ }
public class ZstdStrategy implements CompressionStrategy { /* Zstandard 实现 */ }

@Service
public class CompressionService {
    private CompressionStrategy strategy = new GzipStrategy();  // 默认

    @Autowired private Environment env;

    public void init() {
        String algo = env.getProperty("compression.algo", "gzip");
        switch (algo) {
            case "lz4": strategy = new Lz4Strategy(); break;
            case "zstd": strategy = new ZstdStrategy(); break;
            default: strategy = new GzipStrategy();
        }
    }

    public byte[] compress(byte[] data) { return strategy.compress(data); }
}
```"""),

        ("Spring 中的策略", r"""```java
// Spring 的 @Conditional 是策略模式的容器化
@Configuration
public class DataSourceConfig {

    @Bean
    @ConditionalOnProperty(name = "db.type", havingValue = "mysql")
    public DataSource mysqlDataSource() {
        return new MySQLDataSource();
    }

    @Bean
    @ConditionalOnProperty(name = "db.type", havingValue = "postgres")
    public DataSource postgresDataSource() {
        return new PostgreSQLDataSource();
    }

    @Bean
    @ConditionalOnProperty(name = "db.type", havingValue = "oracle")
    public DataSource oracleDataSource() {
        return new OracleDataSource();
    }
}

// application.yml
// db.type: postgres  ← 启动时 Spring 自动选 PostgreSQLDataSource
```

不同数据库驱动就是不同策略，Spring 根据配置自动选择。"""),

        ("适用边界", """✅ **使用场景**：
- 多种算法实现同一接口（支付 / 排序 / 压缩）
- 算法经常新增或变化
- 运行时选择算法（按配置 / 按业务条件）

❌ **避免场景**：
- 只有 1-2 个算法（直接调用即可）
- 业务方不需要切换（增加抽象成本）
- 算法差异不大（用参数化而非策略）

🔄 **与 State 区别**：
- **Strategy**：客户端主动选择
- **State**：状态间自动转换

🔄 **与 Template Method 区别**：
- **Strategy**：对象组合（运行期切换）
- **Template Method**：类继承（编译期决定）

💡 **最佳实践**：
- 策略接口要稳定（一旦确定不轻易改）
- 用工厂管理策略创建（避免到处 new）
- 配合 DI 容器使用（Spring 自动注入）
- 策略类应该是无状态的（方便复用）"""),

       ])


def ch03_template_method() -> None:
    mk("03-gof-behavioral/template-method.md", "Template Method 模板方法模式",
       "算法骨架不变 + 部分步骤延迟 + Spring JdbcTemplate / Go http.Handler / Java Servlet",
       [
        ("核心问题", """多个类有相似的算法流程，但部分步骤的具体实现不同。把**通用流程**抽到父类，把**变化部分**留给子类。

**真实场景**：
- Spring JdbcTemplate（流程固定，参数化 SQL 和 RowMapper）
- Java Servlet（service 方法固定，子类实现 doGet / doPost）
- Go http.Handler（HandleFunc 固定，业务实现 HandlerFunc）
- Java AbstractList（增删改固定，子类实现 get）"""),

        ("核心思想", """定义一个算法的**骨架**，将一些步骤延迟到子类。模板方法使得子类可以不改变算法结构即可重新定义算法的某些步骤。

**关键角色**：
- **AbstractClass**：抽象类，定义模板方法和抽象步骤
- **ConcreteClass**：子类，实现抽象步骤"""),

        ("Java 实战：Spring JdbcTemplate", r"""```java
// JdbcTemplate 的 query 方法（简化版）
public <T> T query(String sql, RowMapper<T> rowMapper, Object... args) {
    // 1. 获取连接（固定）
    Connection conn = dataSource.getConnection();

    // 2. 创建 PreparedStatement（固定）
    PreparedStatement ps = conn.prepareStatement(sql);

    // 3. 设置参数（固定）
    for (int i = 0; i < args.length; i++) {
        ps.setObject(i + 1, args[i]);
    }

    // 4. 执行 SQL（固定）
    ResultSet rs = ps.executeQuery();

    // 5. 映射结果（变化点，由 RowMapper 提供）
    T result = null;
    if (rs.next()) {
        result = rowMapper.mapRow(rs, 0);
    }

    // 6. 关闭资源（固定）
    rs.close();
    ps.close();
    conn.close();

    return result;
}

// 用法：业务方只提供 SQL + RowMapper
User user = jdbcTemplate.query(
    "SELECT id, name, email FROM users WHERE id = ?",
    (rs, rowNum) -> new User(rs.getLong("id"), rs.getString("name"), rs.getString("email")),
    userId
);
```

JdbcTemplate 帮你写好流程（获取连接 → 创建 statement → 设置参数 → 执行 → 关闭），你只需要提供变化的部分（SQL 和 RowMapper）。"""),

        ("Java Servlet", r"""```java
// 抽象类 HttpServlet（模板）
public abstract class HttpServlet extends GenericServlet {
    // 模板方法：处理 HTTP 请求
    @Override
    public void service(ServletRequest req, ServletResponse res) {
        HttpServletRequest request = (HttpServletRequest) req;
        HttpServletResponse response = (HttpServletResponse) res;
        service(request, response);  // 调用重载
    }

    protected void service(HttpServletRequest req, HttpServletResponse resp) {
        String method = req.getMethod();
        if (method.equals("GET")) doGet(req, resp);
        else if (method.equals("POST")) doPost(req, resp);
        // ... PUT / DELETE 等
    }

    // 抽象步骤（子类实现）
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) { /* 默认 405 */ }
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) { /* 默认 405 */ }
}

// 具体子类
public class UserServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
        // 业务逻辑
    }
}
```

Servlet 容器（Tomcat / Jetty）调用 `service()`，流程由 HttpServlet 决定，子类只实现 `doGet` / `doPost` 等钩子。"""),

        ("Go http.Handler", r"""```go
// net/http 包的 Handler 接口
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}

// ServeMux 是模板方法模式的实现
func (mux *ServeMux) ServeHTTP(w ResponseWriter, r *Request) {
    // 1. 解析请求路径
    // 2. 查找匹配的 handler
    // 3. 调用 handler.ServeHTTP(w, r)（变化点）
    h, _ := mux.Handler(r)
    h.ServeHTTP(w, r)
}

// 用法：业务方实现 ServeHTTP
type MyHandler struct{}

func (MyHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
}

http.ListenAndServe(":8080", MyHandler{})
```

net/http 是模板方法：ServeMux 处理路由分发，业务方只实现 ServeHTTP。"""),

        ("TypeScript：Abstract Class", r"""```typescript
abstract class DataExporter {
    // 模板方法：定义导出流程
    async export(data: any[]): Promise<void> {
        const formatted = this.format(data);
        await this.beforeWrite?.(formatted);
        await this.write(formatted);
        await this.afterWrite?.();
    }

    // 抽象步骤：子类必须实现
    protected abstract format(data: any[]): string;

    // 变化点：子类可覆盖
    protected async write(content: string): Promise<void> {
        await fs.writeFile('export.txt', content);
    }

    // 钩子方法：默认空实现，子类可选覆盖
    protected async beforeWrite?(content: string): Promise<void>;
    protected async afterWrite?(): Promise<void>;
}

// CSV 导出
class CSVExporter extends DataExporter {
    protected format(data: any[]) {
        if (data.length === 0) return '';
        const headers = Object.keys(data[0]).join(',');
        const rows = data.map(d => Object.values(d).join(','));
        return [headers, ...rows].join('\n');
    }
}

// JSON 导出
class JSONExporter extends DataExporter {
    protected format(data: any[]) {
        return JSON.stringify(data, null, 2);
    }

    protected async write(content: string) {
        await fs.writeFile('export.json', content);
    }
}

// 用法
const exporter: DataExporter = new CSVExporter();
await exporter.export([{ name: 'Alice', age: 25 }, { name: 'Bob', age: 30 }]);
```"""),

        ("与 Strategy 区别", """| | Template Method | Strategy |
|---|---|---|
| 抽象层级 | 类继承（编译期） | 对象组合（运行期） |
| 算法骨架 | 不变（基类） | 整个算法都可换 |
| 实现方式 | 抽象方法 | 接口注入 |
| 数量 | 通常一对多（一父多子）| 一对多（一个抽象 N 个实现） |"""),

        ("适用边界", """✅ **使用场景**：
- 多个类算法流程相同（spring JdbcTemplate / Servlet / Go http.Handler）
- 框架设计（让用户填钩子）
- 代码复用（公共流程抽父类）

❌ **避免场景**：
- 子类完全重写父类（违反模板初衷）
- 继承层级过深（> 3 层）
- 子类与父类耦合过紧（用组合替代）

🔄 **替代方案**：
- **Strategy**：运行期切换算法（更灵活）
- **回调函数**：把步骤作为参数传入
- **Pipeline**：数据流处理

💡 **最佳实践**：
- 模板方法应该在父类中（final 修饰）
- 抽象步骤用 `abstract` 修饰
- 钩子方法（hook）给默认实现（避免子类必须覆盖）
- 优先用组合（Strategy）而非继承"""),

       ])


def ch03_visitor() -> None:
    mk("03-gof-behavioral/visitor.md", "Visitor 访问者模式",
       "不修改元素类增加新操作 + AST 处理 / 编译器 / 文件遍历 + Java ElementVisitor",
       [
        ("核心问题", """需要在**不修改元素类**的前提下，对一个复杂对象结构（树 / 集合）中的元素进行**多种不同的操作**。

**真实场景**：
- 编译器：遍历 AST 进行类型检查 / 求值 / 代码生成 / 优化
- 文件系统遍历：遍历所有文件做压缩 / 备份 / 病毒扫描
- Java 编译器 API：ElementVisitor 遍历 Java 元素
- HTML 解析：遍历 DOM 进行各种处理"""),

        ("核心思想", """把「对元素的操作」从元素类中抽离出来，封装到 Visitor 类中。元素类提供 `accept(visitor)` 方法，让 visitor 来访问自己。

**关键点**：
- 元素类层次稳定（不变）
- 操作经常新增（用 Visitor 扩展）
- 通过**双重分派**实现：accept 调用 visitor 的 visit 方法"""),

        ("TypeScript：AST 求值与打印", r"""```typescript
interface Expr {
    accept<R>(visitor: ExprVisitor<R>): R;
}

interface ExprVisitor<R> {
    visitNumber(n: NumberExpr): R;
    visitBinary(b: BinaryExpr): R;
}

class NumberExpr implements Expr {
    constructor(public value: number) {}
    accept<R>(v: ExprVisitor<R>): R { return v.visitNumber(this); }
}

class BinaryExpr implements Expr {
    constructor(public op: '+' | '-', public left: Expr, public right: Expr) {}
    accept<R>(v: ExprVisitor<R>): R { return v.visitBinary(this); }
}

// 求值 visitor
class Evaluator implements ExprVisitor<number> {
    visitNumber(n: NumberExpr) { return n.value; }
    visitBinary(b: BinaryExpr) {
        const l = b.left.accept(this);
        const r = b.right.accept(this);
        return b.op === '+' ? l + r : l - r;
    }
}

// 打印 visitor
class Printer implements ExprVisitor<string> {
    visitNumber(n: NumberExpr) { return n.value.toString(); }
    visitBinary(b: BinaryExpr) {
        return `(${b.left.accept(this)} ${b.op} ${b.right.accept(this)})`;
    }
}

// 类型检查 visitor
class TypeChecker implements ExprVisitor<'number' | 'error'> {
    visitNumber(n: NumberExpr) { return 'number'; }
    visitBinary(b: BinaryExpr) {
        const l = b.left.accept(this);
        const r = b.right.accept(this);
        if (l === 'number' && r === 'number') return 'number';
        return 'error';
    }
}

// 用法：1 + 2 - 3
const expr = new BinaryExpr('-',
    new BinaryExpr('+', new NumberExpr(1), new NumberExpr(2)),
    new NumberExpr(3)
);

new Evaluator().visitBinary(expr as any);  // 0
new Printer().visitBinary(expr as any);   // "((1 + 2) - 3)"
new TypeChecker().visitBinary(expr as any); // 'number'
```

新增操作（如代码生成 visitor）只需要新增 Visitor 类，**不修改任何 Expr 类**。"""),

        ("Java 实战：Java 编译器 API", r"""```java
// Java 编译器 API 用 Visitor 遍历程序元素
public class ElementAnalyzer {
    void analyze(Element element) {
        // Visitor：遍历并收集信息
        element.accept(new ElementVisitor<Void, Void>() {
            @Override
            public Void visitType(TypeElement e, Void p) {
                System.out.println("Type: " + e.getQualifiedName());
                return super.visitType(e, p);
            }

            @Override
            public Void visitMethod(ExecutableElement e, Void p) {
                System.out.println("Method: " + e.getSimpleName());
                return super.visitMethod(e, p);
            }

            @Override
            public Void visitVariable(VariableElement e, Void p) {
                System.out.println("Variable: " + e.getSimpleName());
                return super.visitVariable(e, p);
            }
        }, null);
    }
}
```

## Spring BeanDefinitionVisitor

```java
public class MyBeanVisitor implements BeanDefinitionVisitor {
    @Override
    public void visitBeanDefinition(BeanDefinition beanDefinition) {
        // 自定义处理
    }

    @Override
    public void visitBeanDefinition(String beanName, BeanDefinition beanDefinition) {
        // 自定义处理
    }
}
```"""),

        ("实战：文件系统遍历", r"""```typescript
interface FileSystemVisitor<R> {
    visitFile(file: FileNode): R;
    visitDirectory(dir: DirectoryNode): R;
}

class FileNode {
    constructor(public name: string, public size: number) {}
    accept<R>(v: FileSystemVisitor<R>): R { return v.visitFile(this); }
}

class DirectoryNode {
    constructor(public name: string, public children: FileSystemNode[]) {}
    accept<R>(v: FileSystemVisitor<R>): R { return v.visitDirectory(this); }
}

type FileSystemNode = FileNode | DirectoryNode;

// 计算总大小
class SizeCalculator implements FileSystemVisitor<number> {
    visitFile(file: FileNode) { return file.size; }
    visitDirectory(dir: DirectoryNode) {
        return dir.children.reduce((sum, c) => sum + c.accept(this), 0);
    }
}

// 收集所有文件名
class FileCollector implements FileSystemVisitor<string[]> {
    visitFile(file: FileNode) { return [file.name]; }
    visitDirectory(dir: DirectoryNode) {
        return dir.children.flatMap(c => c.accept(this));
    }
}

// 用法
const root = new DirectoryNode('project', [
    new DirectoryNode('src', [new FileNode('index.ts', 1200)]),
    new FileNode('README.md', 2000),
]);

new SizeCalculator().visitDirectory(root);   // 3200
new FileCollector().visitDirectory(root);    // ['src', 'index.ts', 'README.md']
```"""),

        ("优缺点", """## 优点

- 新增操作容易（新增 Visitor 类，不改元素）
- 操作集中（所有操作在一个 Visitor 中）
- 元素类层次稳定（编译期确定）

## 缺点

- **增加新元素类困难**（必须改所有 Visitor）
- **双重分派**（double dispatch）依赖方法签名
- 违反**封装性**（Visitor 需要访问元素内部状态）"""),

        ("适用边界", """✅ **使用场景**：
- AST 处理（编译器 / 表达式求值）
- 文件系统遍历（多种操作：压缩 / 备份 / 搜索）
- 对象结构稳定但操作经常新增
- Java ElementVisitor / Spring BeanDefinitionVisitor

❌ **避免场景**：
- 元素类经常新增（Visitor 难以演进）
- 操作只有 1-2 种（直接写在元素类里）
- 不需要遍历整个结构（局部处理）

🔄 **替代方案**：
- **直接方法**：操作简单时直接在元素类加方法
- **pattern matching**：TypeScript / Rust 用 match 替代 Visitor
- **Lambda / 函数式**：操作作为函数传入

💡 **最佳实践**：
- Visitor 接口要尽量稳定（一旦确定不改）
- 用泛型让 Visitor 返回不同类型（`visitX(): R`）
- Go / TS 没有重载，可以用 `accept` 方法避免双重分派
- 警惕 Visitor 膨胀（操作太多 Visitor 难维护）"""),

       ])


def ch03_interpreter() -> None:
    mk("03-gof-behavioral/interpreter.md", "Interpreter 解释器模式",
       "自定义语言求值 + 表达式解析 + SQL parser / 正则表达式 / DSL",
       [
        ("核心问题", """需要实现一个**自定义语言**或**表达式**的求值。例如：
- 数学表达式：`(1 + 2) * 3`
- 布尔表达式：`(age > 18) AND (country = 'CN')`
- SQL 解析：`SELECT * FROM users WHERE age > 18`
- DSL（领域特定语言）：`order.create().item().pay()`"""),

        ("核心思想", """给定一个语言，定义它的**文法**（grammar）的一种表示，并定义一个**解释器**，使用该表示来解释语言中的句子。

**关键角色**：
- **AbstractExpression**：抽象表达式（`interpret()`）
- **TerminalExpression**：终结符表达式（数字 / 变量）
- **NonTerminalExpression**：非终结符表达式（+ / - / *）
- **Context**：上下文（存储变量值等）"""),

        ("TypeScript：数学表达式", r"""```typescript
// 抽象表达式
interface Expr {
    interpret(): number;
}

// 终结符：数字
class NumberExpr implements Expr {
    constructor(public value: number) {}
    interpret() { return this.value; }
}

// 终结符：变量
class VariableExpr implements Expr {
    constructor(public name: string, public context: Context) {}
    interpret() { return this.context.get(this.name); }
}

// 非终结符：加法
class PlusExpr implements Expression {
    constructor(public left: Expr, public right: Expr) {}
    interpret() { return this.left.interpret() + this.right.interpret(); }
}

class MinusExpr implements Expression {
    constructor(public left: Expr, public right: Expr) {}
    interpret() { return this.left.interpret() - this.right.interpret(); }
}

// 上下文
class Context {
    private vars = new Map<string, number>();
    set(name: string, value: number) { this.vars.set(name, value); }
    get(name: string) { return this.vars.get(name) ?? 0; }
}

// 用法：(x + 2) - 3，x = 5
const ctx = new Context();
ctx.set('x', 5);

const expr = new MinusExpr(
    new PlusExpr(new VariableExpr('x', ctx), new NumberExpr(2)),
    new NumberExpr(3)
);

console.log(expr.interpret());  // (5 + 2) - 3 = 4
```"""),

        ("实战：正则表达式", r"""正则表达式本身就是一种语言，Regexp 引擎是解释器：

```javascript
// JavaScript 正则表达式
const pattern = /^(\\d+)\\.(\\d+)\\.(\\d+)\\.(\\d+)$/;

const matcher = pattern.exec('192.168.1.1');
console.log(matcher);
// ['192.168.1.1', '192', '168', '1', '1']

// 实际场景：解析 IP 地址
function parseIP(ip: string) {
    const m = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/.exec(ip);
    if (!m) return null;
    return {
        a: parseInt(m[1]),
        b: parseInt(m[2]),
        c: parseInt(m[3]),
        d: parseInt(m[4]),
    };
}
```

正则表达式引擎内部用 NFA / DFA 解释正则语法。"""),

        ("实战：SQL 解析器", r"""```java
// ANTLR 生成的 SQL 解析器（简化）
public class SqlParser {
    public static void parse(String sql) {
        // ANTLR 自动生成的 Lexer / Parser
        CharStream input = CharStreams.fromString(sql);
        SqlLexer lexer = new SqlLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        SqlParser parser = new SqlParser(tokens);

        ParseTree tree = parser.selectStatement();
        System.out.println(tree.toStringTree(parser));

        // 用 Visitor 遍历 AST
        SqlBaseVisitor<Void> visitor = new SqlBaseVisitor<Void>() {
            @Override
            public Void visitSelectStatement(SqlParser.SelectStatementContext ctx) {
                System.out.println("Select columns:");
                ctx.columnList().column().forEach(c -> System.out.println(" - " + c.getText()));
                System.out.println("From table: " + ctx.tableName().getText());
                if (ctx.WHERE() != null) {
                    System.out.println("Where: " + ctx.expression().getText());
                }
                return null;
            }
        };
        visitor.visit(tree);
    }
}

// 用法
SqlParser.parse("SELECT id, name FROM users WHERE age > 18");
// 输出：
// Select columns:
//  - id
//  - name
// From table: users
// Where: age > 18
```

SQL 解析器 = Lexer（词法分析）+ Parser（语法分析）+ Visitor（语义分析）。"""),

        ("实战：DSL（领域特定语言）", r"""```typescript
// SQL DSL（TypeORM）
const users = await connection
    .createQueryBuilder()
    .select('user')
    .from(User, 'user')
    .where('user.age > :age', { age: 18 })
    .andWhere('user.country = :country', { country: 'CN' })
    .orderBy('user.createdAt', 'DESC')
    .limit(10)
    .getMany();

// 流式 API 是 DSL，每个方法是 Expression 节点
```

```typescript
// Cron 表达式解析
class CronExpression {
    constructor(
        public minute: string,
        public hour: string,
        public dayOfMonth: string,
        public month: string,
        public dayOfWeek: string
    ) {}

    static parse(expr: string): CronExpression {
        const parts = expr.split(' ');
        if (parts.length !== 5) throw new Error('Invalid cron');
        return new CronExpression(...parts);
    }

    matches(date: Date): boolean {
        return (
            this.matchesField(date.getMinutes(), this.minute) &&
            this.matchesField(date.getHours(), this.hour) &&
            this.matchesField(date.getDate(), this.dayOfMonth) &&
            this.matchesField(date.getMonth() + 1, this.month) &&
            this.matchesField(date.getDay(), this.dayOfWeek)
        );
    }

    private matchesField(value: number, pattern: string): boolean {
        if (pattern === '*') return true;
        if (pattern.includes(',')) return pattern.split(',').map(Number).includes(value);
        if (pattern.includes('/')) {
            const [, step] = pattern.split('/');
            return value % parseInt(step) === 0;
        }
        return parseInt(pattern) === value;
    }
}

// 用法
const cron = CronExpression.parse('0 0 * * *');  // 每天 0 点
cron.matches(new Date('2024-01-01 00:00:00'));  // true
```"""),

        ("何时使用 / 避免", """✅ **使用场景**：
- 简单 DSL / 表达式求值
- SQL / 数学公式 / 业务规则引擎
- 自定义配置格式（YAML / HCL / TOML）

❌ **避免场景**：
- 复杂语法（用 ANTLR / Yacc / Lex）
- 性能敏感（解释执行比编译慢 10-100x）
- 一次性脚本（直接写 if-else）

🔄 **替代方案**：
- **ANTLR / Yacc**：复杂语法解析
- **正则表达式**：文本匹配
- **JEXL / SpEL**：Java 表达式
- **Lambda / 闭包**：参数化行为

💡 **最佳实践**：
- 文法要简单（否则维护成本指数增长）
- 用 Visitor 遍历语法树（不直接递归）
- 错误处理要友好（明确语法错误位置）
- 考虑用现成库（ANTLR / PEG.js）而非手写"""),

       ])


# ============================================================================
# Chapter 04: Modern Patterns (4 stubs)
# ============================================================================

def ch04_dependency_injection() -> None:
    mk("04-modern-patterns/dependency-injection.md", "依赖注入 DI",
       "解耦对象创建 + Spring IoC / NestJS Provider / Go Wire + 构造器 vs Setter vs 字段注入",
       [
        ("核心问题", """业务对象 A 需要使用对象 B，但 A 不应该自己 `new B()`（编译期耦合）。应该由外部容器把 B 注入到 A。

**问题场景**：
- `OrderService` 直接 `new PaymentService()` → 单测无法替换 mock
- `UserController` 直接 `new UserRepository()` → 难以切换数据库实现
- `NotificationService` 直接 `new EmailSender()` → 难以切换到短信"""),

        ("控制反转（IoC）", """**传统流程**：
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

**核心思想**：对象只声明「我需要什么」，由容器决定「怎么提供」。"""),

        ("三种注入方式", r"""## 1. 构造器注入（推荐）

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

⚠️ **Google / SonarQube 都建议避免字段注入**"""),

        ("Spring IoC 容器", r"""```java
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
```"""),

        ("NestJS Provider", r"""```typescript
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
- `@Module`：模块边界（类似 Java package）"""),

        ("Go Wire（编译期 DI）", r"""Go 推荐用 Google Wire 做编译期 DI：

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

Wire 不依赖反射，编译期生成依赖注入代码，比 Spring 更明确、更快。"""),

        ("适用边界", """✅ **使用场景**：
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
- Wire / Dagger 是编译期 DI（比 Spring 更快）"""),

       ])


def ch04_repository() -> None:
    mk("04-modern-patterns/repository.md", "Repository 仓储模式",
       "封装数据访问 + Spring Data JPA / TypeORM / EF Core / Go sqlc + Repository vs DAO",
       [
        ("核心问题", """业务层直接使用 JDBC / JPA / MongoDB driver，耦合数据库细节。导致：
1. 业务层充斥 SQL 拼接
2. 难以切换数据库（MySQL → PG）
3. 单测需要真实数据库
4. 业务逻辑分散在多个层"""),

        ("核心思想", """把数据访问逻辑封装到独立的接口层（`Repository`），让业务层只依赖 Repository 接口，不依赖具体的数据库技术。

**关键点**：
- Repository 接口放在**领域层**（业务侧）
- Repository 实现在**基础设施层**（技术侧）
- 返回**领域对象**（不是 Entity / DTO）"""),

        ("Java 实战", r"""```java
// 领域层：定义接口
public interface OrderRepository {
    Optional<Order> findById(long id);
    List<Order> findByUser(long userId);
    void save(Order order);
    void delete(long id);
}

// 业务层：只依赖接口
@Service
public class OrderService {
    private final OrderRepository repo;

    public OrderService(OrderRepository repo) { this.repo = repo; }

    public Order getOrder(long id) {
        return repo.findById(id).orElseThrow(OrderNotFoundException::new);
    }

    @Transactional
    public Order create(OrderRequest req) {
        Order order = Order.create(req);
        repo.save(order);
        return order;
    }
}

// 基础设施层：JDBC 实现
@Repository
public class JdbcOrderRepository implements OrderRepository {
    @Autowired private JdbcTemplate jdbc;

    @Override
    public Optional<Order> findById(long id) {
        try {
            Order o = jdbc.queryForObject(
                "SELECT id, user_id, total, status FROM orders WHERE id = ?",
                (rs, rowNum) -> new Order(
                    rs.getLong("id"),
                    rs.getLong("user_id"),
                    rs.getBigDecimal("total"),
                    OrderStatus.valueOf(rs.getString("status"))
                ),
                id
            );
            return Optional.ofNullable(o);
        } catch (EmptyResultDataAccessException e) {
            return Optional.empty();
        }
    }

    @Override
    @Transactional
    public void save(Order order) {
        jdbc.update(
            "INSERT INTO orders(id, user_id, total, status) VALUES(?, ?, ?, ?)",
            order.getId(), order.getUserId(), order.getTotal(), order.getStatus().name()
        );
    }

    // ...
}

// 切换数据库：只需要新增 JpaOrderRepository，业务层零修改
```"""),

        ("Spring Data JPA", r"""```java
// Spring Data JPA：自动生成实现
public interface OrderRepository extends JpaRepository<Order, Long> {
    // 自动实现：findById / findAll / save / delete
    List<Order> findByUserId(long userId);

    @Query("SELECT o FROM Order o WHERE o.status = :status")
    List<Order> findByStatus(@Param("status") OrderStatus status);
}

// 用法
@Service
public class OrderService {
    private final OrderRepository repo;

    public OrderService(OrderRepository repo) { this.repo = repo; }

    public List<Order> getPaidOrders() {
        return repo.findByStatus(OrderStatus.PAID);
    }
}
```

Spring Data JPA 在运行时通过 JDK 动态代理自动生成 Repository 实现，业务方完全不用写 SQL。"""),

        ("TypeScript：TypeORM / Prisma", r"""```typescript
// TypeORM
@EntityRepository(Order)
class OrderRepository {
    async findById(id: number): Promise<Order | null> {
        return this.findOne({ where: { id } });
    }

    async findByUser(userId: number): Promise<Order[]> {
        return this.find({ where: { userId } });
    }

    async save(order: Order): Promise<Order> {
        return this.manager.save(order);
    }
}

// Prisma（schema-first）
const user = await prisma.user.findUnique({
    where: { id: 1 },
    include: { orders: true },
});
```

## Go sqlc（编译期生成）

```sql
-- queries.sql
-- name: GetOrder :one
SELECT * FROM orders WHERE id = $1 LIMIT 1;

-- name: ListOrdersByUser :many
SELECT * FROM orders WHERE user_id = $1 ORDER BY created_at DESC;
```

```bash
# sqlc 生成 Go 代码
sqlc generate
```

```go
// 自动生成的 repository.go
type OrderRepository struct {
    db *sql.DB
    q  *Queries
}

func (r *OrderRepository) GetOrder(ctx context.Context, id int64) (Order, error) {
    return r.q.GetOrder(ctx, id)
}
```

sqlc 是编译期生成的 Type-safe SQL 客户端，比 ORM 更快更明确。"""),

        ("Repository vs DAO", """| | Repository | DAO |
|---|---|---|
| 抽象层级 | 聚合根为单位 | 表为单位 |
| 方法命名 | `findByUser` 业务语义 | `selectByUserId` SQL 语义 |
| 返回值 | 领域对象 | Entity / DTO |
| 业务封装 | 含业务校验 / 不变量 | 仅数据访问 |
| 适用 | DDD / 复杂业务 | 简单 CRUD |

## 与 Specification 配合

```java
public interface OrderRepository {
    List<Order> findBySpecification(Specification<Order> spec);
}

// 用法：组合多个条件
Specification<Order> spec = OrderSpecs.hasUser(123)
    .and(OrderSpecs.createdAfter(lastWeek))
    .and(OrderSpecs.totalGreaterThan(minTotal));

List<Order> orders = repo.findBySpecification(spec);
```"""),

        ("适用边界", """✅ **使用场景**：
- 业务层要访问数据库（所有业务系统）
- 业务对象持久化逻辑复杂（DDD）
- 多数据源（写 MySQL + 读 Redis / ES）

❌ **避免场景**：
- 业务极简（直接用 ORM）
- 一个方法调用就完成（过度抽象）
- 性能敏感（Repository 抽象有开销）

🔄 **演进路径**：
- 直接 ORM → Repository 接口（解耦）
- Repository + Specification（条件组合）
- Repository + CQRS（读写分离）

💡 **最佳实践**：
- Repository 接口放在领域层
- 实现放在基础设施层
- 每个聚合根一个 Repository
- 返回值用领域对象（不是 Entity）
- 业务校验在 Repository 内（不变量保护）"""),

       ])


def ch04_specification() -> None:
    mk("04-modern-patterns/specification.md", "Specification 规格模式",
       "查询条件可组合 + JPA Specification + Laravel Query Builder + 函数式 filter",
       [
        ("核心问题", """业务中需要多个动态查询条件组合（电商筛选、权限规则、复杂查询），用 SQL 拼接 / if-else 嵌套会导致：
1. 代码冗长（每个查询写一堆 if-else）
2. 难以复用（相同条件散落各处）
3. 难以测试（SQL 拼接难单元测试）
4. 业务方关心的是「条件」，不是 SQL"""),

        ("核心思想", """把查询/筛选条件封装成 **first-class 对象**，可以自由组合（AND / OR / NOT）、复用、传递。

**Composite Specification**：多个条件用 boolean operator 组合"""),

        ("TypeScript：函数式 Specification", r"""```typescript
// Specification 接口
interface Specification<T> {
    isSatisfiedBy(entity: T): boolean;
    and(other: Specification<T>): Specification<T>;
    or(other: Specification<T>): Specification<T>;
    not(): Specification<T>;
}

// 实现
class UserSpec implements Specification<User> {
    constructor(private predicate: (u: User) => boolean) {}

    isSatisfiedBy(u: User) { return this.predicate(u); }

    and(other: Specification<User>) {
        return new UserSpec(u => this.isSatisfiedBy(u) && other.isSatisfiedBy(u));
    }

    or(other: Specification<User>) {
        return new UserSpec(u => this.isSatisfiedBy(u) || other.isSatisfiedBy(u));
    }

    not() {
        return new UserSpec(u => !this.isSatisfiedBy(u));
    }
}

// 静态工厂
class UserSpecs {
    static isActive() {
        return new UserSpec(u => u.status === 'active');
    }
    static isAdult() {
        return new UserSpec(u => u.age >= 18);
    }
    static isInCountry(country: string) {
        return return new UserSpec(u => u.country === country);
    }
}

// 用法：自由组合
const spec = UserSpecs.isActive()
    .and(UserSpecs.isAdult())
    .and(UserSpecs.isInCountry('CN'))
    .or(UserSpecs.isInCountry('US'));

const result = users.filter(spec.isSatisfiedBy.bind(spec));
```

## Go：函数式 Specification

```go
type UserSpec func(User) bool

func (s UserSpec) IsSatisfiedBy(u User) bool { return s(u) }
func (s UserSpec) And(other UserSpec) UserSpec {
    return func(u User) bool { return s(u) && other(u) }
}
func (s UserSpec) Or(other UserSpec) UserSpec {
    return func(u User) bool { return s(u) && other(u) }
}
func (s UserSpec) Not() UserSpec {
    return func(u User) bool { return !s(u) }
}

// 静态规格
var (
    IsActive = UserSpec(func(u User) bool { return u.Status == "active" })
    IsAdult  = UserSpec(func(u User) bool { return u.Age >= 18 })
)

// 组合
spec := IsActive.And(IsAdult)
filtered := lo.Filter(users, func(u User, _ int) bool { return spec(u) })
```"""),

        ("JPA Specification", r"""```java
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

    public static Specification<Order> statusIn(OrderStatus... statuses) {
        return (root, q, cb) -> root.get("status").in(Arrays.asList(statuses));
    }
}

// Repository
public interface OrderRepository extends JpaRepository<Order, Long>, JpaSpecificationExecutor<Order> {
    // findAll(Specification) 已由 JpaSpecificationExecutor 提供
}

// Service
@Service
public class OrderService {
    @Autowired OrderRepository repo;

    public List<Order> search(OrderSearchCriteria criteria) {
        Specification<Order> spec = Specification.where(null);

        if (criteria.getUserId() != null) spec = spec.and(OrderSpecs.hasUser(criteria.getUserId()));
        if (criteria.getMinTotal() != null) spec = spec.and(OrderSpecs.totalGreaterThan(criteria.getMinTotal()));
        if (criteria.getStatuses() != null && !criteria.getStatuses().isEmpty())
            spec = spec.and(OrderSpecs.statusIn(criteria.getStatuses().toArray(new OrderStatus[0])));

        return repo.findAll(spec);
    }
}
```

## 实际查询生成的 SQL

```sql
SELECT * FROM orders
WHERE user_id = 123
  AND total > 100
  AND status IN ('PAID', 'SHIPPED')
  AND created_at > '2024-01-01'
ORDER BY created_at DESC
```"""),

        ("实战：电商筛选", r"""```typescript
interface ProductFilters {
    category?: string;
    brand?: string[];
    minPrice?: number;
    maxPrice?: number;
    minRating?: number;
    inStock?: boolean;
    searchQuery?: string;
}

class ProductSpec implements Specification<Product> {
    constructor(private predicate: (p: Product) => boolean) {}

    isSatisfiedBy(p: Product) { return this.predicate(p); }
    and(other: Specification<Product>) { return new ProductSpec(p => this.isSatisfiedBy(p) && other.isSatisfiedBy(p)); }
    // ...
}

function buildProductSpec(filters: ProductFilters): Specification<Product> {
    let spec: Specification<Product> = new ProductSpec(() => true);

    if (filters.category) {
        spec = spec.and(new ProductSpec(p => p.category === filters.category));
    }
    if (filters.brand?.length) {
        spec = spec.and(new ProductSpec(p => filters.brand!.includes(p.brand)));
    }
    if (filters.minPrice !== undefined) {
        spec = spec.and(new ProductSpec(p => p.price >= filters.minPrice!));
    }
    if (filters.maxPrice !== undefined) {
        spec = spec.and(new ProductSpec(p => p.price <= filters.maxPrice!));
    }
    if (filters.minRating !== undefined) {
        spec = spec.and(new ProductSpec(p => p.rating >= filters.minRating!));
    }
    if (filters.inStock) {
        spec = spec.and(new ProductSpec(p => p.stock > 0));
    }
    if (filters.searchQuery) {
        const q = filters.searchQuery.toLowerCase();
        spec = spec.and(new ProductSpec(p =>
            p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q)
        ));
    }

    return spec;
}

// 用法
const spec = buildProductSpec({
    category: 'electronics',
    brand: ['Apple', 'Samsung'],
    minPrice: 1000,
    maxPrice: 5000,
    minRating: 4.5,
    inStock: true,
});

const filtered = products.filter(spec.isSatisfiedBy.bind(spec));
```"""),

        ("适用边界", """✅ **使用场景**：
- 多条件动态组合查询（电商筛选）
- 复杂权限规则（角色 + 资源 + 状态）
- 查询条件复用（多个 controller 共享）
- 业务规则抽象（Specification 可被业务逻辑调用）

❌ **避免场景**：
- 单一固定条件（直接传参）
- 业务方不需要组合（增加复杂度）
- 性能极敏感（Specification 多了一层包装）

🔄 **替代方案**：
- **Query Builder**：Laravel / Knex 等
- **DSL**：jOOQ / QueryDSL
- **简单 if-else**：单条件查询

💡 **最佳实践**：
- Specification 是无状态对象（可以被复用、缓存）
- 组合方法（and/or/not）返回新对象（不可变）
- JPA Specification 配合 JpaSpecificationExecutor
- TS/Go 用函数式 Specification 更简洁"""),

       ])


def ch04_null_object() -> None:
    mk("04-modern-patterns/null-object.md", "Null Object 空对象模式",
       "消除 null 检查 + Optional / Maybe / 空集合 / NoopLogger",
       [
        ("核心问题", """业务代码中充斥 `if (obj != null) { ... } else { ... }`，导致：
1. **NullPointerException**：忘了 null 检查
2. **代码冗长**：每个字段都可能 null，if 链遍布
3. **业务含义模糊**：null 是「不存在」还是「错误」？
4. **多重传播**：null 在调用链中传递"""),

        ("核心思想", """用「什么都不做的对象」替代 null，使调用方**不必做空值检查**。

**两种形式**：
1. **Null Object Pattern**：提供一个空对象（如 `Collections.emptyList()` / `Logger.NOOP`）
2. **Optional/Maybe**：容器包装，强制处理空值"""),

        ("Optional 实战（Java）", r"""```java
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
```"""),

        ("TypeScript：可选链与空值合并", r"""```typescript
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
```"""),

        ("经典案例：Null Object", r"""## Logger.NOOP

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
```"""),

        ("实战：策略模式 + Null Object", r"""```typescript
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
```"""),

        ("适用边界", """✅ **使用场景**：
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
- 用 Optional 替代 return null（Optional<T>）
- Java 9+ `Optional.stream()` 与其他 API 配合
- TypeScript 用 `??` 和 `?.` 而非 `||` 和 `.`
- 不要 `Optional<Optional<T>>`（嵌套 Optional 反模式）"""),

       ])


# ============================================================================
# Chapter 05: Architectural Patterns (8 stubs)
# ============================================================================

def ch05_cqrs() -> None:
    mk("05-architectural-patterns/cqrs.md", "CQRS 命令查询分离",
       "读写模型分离 + Axon / EventStoreDB / Kafka Streams + 4 种架构演进",
       [
        ("核心问题", """传统 CRUD 模型用同一张表同时承担读和写：
- **读写竞争**：写加锁影响读性能
- **模型冲突**：写模型要范式化，读模型要反范式化
- **扩展困难**：报表查询（OLAP）跟在线交易（OLTP）放一个库不合理
- **业务耦合**：读和写共享业务模型，难以独立优化"""),

        ("核心思想", """把**写操作（Command）**和**读操作（Query）**分离到不同的模型 / 服务 / 数据库上。

**关键点**：
- Command 端：写模型（范式化、事务强一致）
- Query 端：读模型（反范式化、查询优化）
- 两者通过**事件**同步（Event-Driven）"""),

        ("4 种架构演进", r"""```text
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
```"""),

        ("实战：Axon Framework", r"""```java
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
```"""),

        ("Java + Spring 手写简易 CQRS", r"""```java
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
```"""),

        ("读模型选择", """不同读模型适合不同场景：

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
- 实时性要求高 → Redis"""),

        ("适用边界", """✅ **使用场景**：
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
- 监控读写延迟差异（设置 SLA）"""),

       ])


def ch05_event_sourcing() -> None:
    mk("05-architectural-patterns/event-sourcing.md", "Event Sourcing 事件溯源",
       "用事件序列保存状态 + Axon / EventStoreDB + 优势与挑战",
       [
        ("核心问题", """传统 CRUD 只保留对象当前状态，丢失历史：
- 无法审计（不知道谁改了什么）
- 无法回放（出错难以复现）
- 无法时间旅行（不能查询任意时间点的状态）
- 业务分析困难（缺少历史数据）"""),

        ("核心思想", """不保存对象的当前状态，而是保存**导致状态变化的全部事件**。当前状态 = replay 所有事件。

```sql
-- 传统：只保留最新状态
UPDATE accounts SET balance = 100 WHERE id = 'alice';
-- 历史丢失

-- Event Sourcing：保留事件流
-- 1. AccountOpened{alice, 0}
-- 2. MoneyDeposited{alice, +1000}
-- 3. MoneyWithdrawn{alice, -500}
-- 4. MoneyDeposited{alice, +200}
-- replay 后: balance = 700
```"""),

        ("实战：Axon Event Sourcing", r"""```java
// 聚合根只产生事件，不直接修改字段
@Aggregate
public class BankAccount {
    @AggregateIdentifier
    private String accountId;
    private BigDecimal balance;

    // 命令处理：校验 + 产生事件
    @CommandHandler
    public BankAccount(OpenAccountCommand cmd) {
        apply(new AccountOpenedEvent(cmd.getAccountId(), cmd.getInitialBalance()));
    }

    @CommandHandler
    public void handle(DepositMoneyCommand cmd) {
        if (cmd.getAmount().signum() <= 0) {
            throw new IllegalArgumentException("Deposit must be positive");
        }
        apply(new MoneyDepositedEvent(cmd.getAccountId(), cmd.getAmount()));
    }

    @CommandHandler
    public void handle(WithdrawMoneyCommand cmd) {
        if (balance.compareTo(cmd.getAmount()) < 0) {
            throw new IllegalStateException("Insufficient balance");
        }
        apply(new MoneyWithdrawnEvent(cmd.getAccountId(), cmd.getAmount()));
    }

    // 事件溯源：修改字段
    @EventSourcingHandler
    public void on(AccountOpenedEvent event) {
        this.accountId = event.getAccountId();
        this.balance = event.getInitialBalance();
    }

    @EventSourcingHandler
    public void on(MoneyDepositedEvent event) {
        this.balance = this.balance.add(event.getAmount());
    }

    @EventSourcingHandler
    public void on(MoneyWithdrawnEvent event) {
        this.balance = this.balance.subtract(event.getAmount());
    }
}

// 仓库：自动 replay 事件加载聚合
@Repository
public class BankAccountRepository {
    @Autowired private EventStore eventStore;

    public BankAccount findById(String id) {
        // 加载所有事件，replay 出当前状态
        DomainEventStream stream = eventStore.readEvents(id);
        BankAccount account = new BankAccount();  // 空状态
        while (stream.hasNext()) {
            AccountEvent event = (AccountEvent) stream.next();
            account.on(event);  // 应用事件，修改字段
        }
        return account;
    }
}
```"""),

        ("Snapshots 优化", r"""replay 100 万个事件太慢，**Snapshot（快照）** 优化：

```java
// 每 100 个事件做一次快照
public class BankAccountSnapshot {
    private String accountId;
    private BigDecimal balance;
    private long eventVersion;

    @EventSourcingHandler
    public void on(AccountOpenedEvent event) { /* ... */ }
}

// 加载流程：
// 1. 加载最近的快照（假设是 version 1000）
// 2. 加载 version 1001 之后的所有事件
// 3. 应用这些事件到快照状态

public BankAccount loadWithSnapshot(String id) {
    // 1. 加载快照
    BankAccountSnapshot snapshot = snapshotRepo.findLatest(id);

    // 2. 从快照版本之后加载事件
    DomainEventStream stream = eventStore.readEvents(id, snapshot.getEventVersion() + 1);

    // 3. 应用事件
    BankAccount account = new BankAccount(snapshot);
    while (stream.hasNext()) {
        account.on((AccountEvent) stream.next());
    }
    return account;
}
```

**Snapshot 策略**：
- 每 N 个事件（如 100 / 500）
- 或每 T 时间（如每天一次）
- 或聚合 size 超过阈值时"""),

        ("实战：Git 内部", r"""Git 是 Event Sourcing 的经典案例：

```bash
# 每次 commit 是一个事件
git log --oneline
# a3f2c8 (HEAD -> main) feat: add login
# 8d7e1b fix: handle null
# 6c5d9a initial commit

# 任意版本的状态 = checkout 对应 commit
git checkout a3f2c8  # 时间旅行到 a3f2c8

# git reset = 删除某些事件
git reset HEAD~1  # 撤销最后一次事件
```

## 数据库 binlog

MySQL / PostgreSQL / Oracle 的 binlog / WAL 也是 Event Sourcing：

```bash
# MySQL binlog
mysqlbinlog --start-datetime='2024-01-01' binlog.000001

# Debezium 监听 binlog 生成事件流
```

## Kafka 提交日志

Kafka topic 本身就是不可变的事件流：

```java
// Kafka topic：order-events
// 每个消息是一个领域事件
@KafkaListener(topics = "order-events")
public void process(String eventJson) {
    OrderEvent event = parse(eventJson);
    // 处理事件
}
```"""),

        ("优势与挑战", """## 优势

1. **完整审计**：所有状态变化可追溯
2. **时间旅行**：可以查询任意时间点的状态
3. **事件驱动**：天然适合 Event-Driven Architecture
4. **调试容易**：测试时 replay 真实事件
5. **业务洞察**：事件流可分析（用户行为 / 业务流程）

## 挑战

1. **复杂查询困难**：要算当前状态必须 replay 全部事件（用 snapshot 缓解）
2. **schema 演进**：事件结构变了要兼容老事件
3. **存储成本**：事件不断增长，需要冷热分离
4. **调试复杂**：业务方不熟悉事件模型
5. **查询能力受限**：需要 CQRS + 读模型补充"""),

        ("适用边界", """✅ **使用场景**：
- 金融 / 支付（必须审计）
- 业务规则复杂（订单状态机）
- 需要事件分析（用户行为）
- 跨服务集成（事件驱动）

❌ **避免场景**：
- 简单 CRUD（直接读写数据库）
- 团队无 Event Sourcing 经验
- 业务规则经常变（事件 schema 难维护）

🔄 **与 CQRS 关系**：
- Event Sourcing 是 CQRS 的**写端实现**
- CQRS 是 Event Sourcing 的**读端优化**
- 两者经常一起使用

💡 **最佳实践**：
- Event Schema 用 Avro / Protobuf（强 schema + 演进兼容）
- Snapshot 策略选择（每 N 事件 / 每 T 时间）
- 事件不可变（避免修改历史）
- 事件版本号管理（upcasting 处理 schema 演进）"""),

       ])


def ch05_saga() -> None:
    mk("05-architectural-patterns/saga.md", "Saga 分布式事务",
       "跨服务事务编排 + Orchestration vs Choreography + Temporal / Camunda",
       [
        ("核心问题", """分布式系统中，多个服务需要协同完成一个业务事务（如：下单 + 扣款 + 扣库存 + 发货），但无法用传统的 ACID 本地事务。

**矛盾**：
- 业务要求原子性（全成功或全失败）
- 分布式没有全局事务（CAP 定理）
- 2PC / 3PC 太重（性能差、不可用）"""),

        ("核心思想", """把分布式长事务拆成多个**本地事务 + 补偿操作**，实现最终一致性。

**两种 Saga**：

| 类型 | 实现 | 适用 |
|---|---|---|
| **Orchestration（编排）** | 中央协调器逐步调用 | 流程清晰 / 适合复杂业务 |
| **Choreography（编排）** | 各服务通过事件相互触发 | 简单流程 / 服务解耦 |"""),

        ("Orchestration Saga 实战", r"""```typescript
// Saga 协调器：中央控制流程
class OrderSagaOrchestrator {
    constructor(
        private orderService: OrderService,
        private paymentService: PaymentService,
        private inventoryService: InventoryService,
        private shippingService: ShippingService,
    ) {}

    async execute(orderReq: OrderRequest): Promise<string> {
        const sagaId = uuid();
        const steps: StepResult[] = [];

        try {
            // Step 1: 创建订单
            const order = await this.orderService.create(orderReq);
            steps.push({ name: 'create_order', status: 'completed' });

            // Step 2: 扣款
            await this.paymentService.charge(order);
            steps.push({ name: 'payment', status: 'completed' });

            // Step 3: 扣库存
            await this.inventoryService.reserve(order.items);
            steps.push({ name: 'inventory', status: 'completed' });

            // Step 4: 发货
            await this.shippingService.createShipment(order);
            steps.push({ name: 'shipping', status: 'completed' });

            await this.orderService.markCompleted(order.id);
            return order.id;

        } catch (error) {
            await this.compensate(sagaId, order, steps, error);
            throw error;
        }
    }

    // 补偿逻辑：反向撤销
    private async compensate(
        sagaId: string,
        order: Order,
        completedSteps: StepResult[],
        error: Error,
    ) {
        log.warn(`saga ${sagaId} failed, compensating`, error);

        // 逆序补偿
        for (let i = completedSteps.length - 1; i >= 0; i--) {
            const step = completedSteps[i];
            try {
                switch (step.name) {
                    case 'shipping':
                        if (order.shipped) await this.shippingService.cancelShipment(order.id);
                        break;
                    case 'inventory':
                        await this.inventoryService.release(order.items);
                        break;
                    case 'payment':
                        await this.paymentService.refund(order);
                        break;
                    case 'create_order':
                        await this.orderService.markFailed(order.id);
                        break;
                }
            } catch (e) {
                log.error(`compensate ${step.name} failed`, e);
                // 补偿失败需要人工介入
                await this.alert(sagaId, step.name, e);
            }
        }
    }
}
```"""),

        ("Choreography Saga 实战", r"""```typescript
// 各服务独立监听事件，无需中央协调器

// 订单服务
@EventsHandler
class OrderEvents {
    constructor(private bus: EventBus) {}

    @OnEvent('OrderCreateRequested')
    async handleOrderCreate(event: OrderCreateRequested) {
        const order = await this.createOrder(event);
        await this.bus.publish('OrderCreated', { orderId: order.id, total: order.total });
    }
}

// 支付服务
@EventsHandler
class PaymentEvents {
    @OnEvent('OrderCreated')
    async handleOrderCreated(event: OrderCreated) {
        const result = await this.charge(event.orderId, event.total);
        if (result.success) {
            await this.bus.publish('PaymentCompleted', { orderId: event.orderId });
        } else {
            await this.bus.publish('PaymentFailed', { orderId: event.orderId, reason: result.reason });
        }
    }
}

// 库存服务
@EventsHandler
class InventoryEvents {
    @OnEvent('PaymentCompleted')
    async handlePaymentCompleted(event: PaymentCompleted) {
        try {
            await this.reserve(event.orderId);
            await this.bus.publish('InventoryReserved', { orderId: event.orderId });
        } catch (e) {
            await this.bus.publish('InventoryReservationFailed', { orderId: event.orderId });
        }
    }
}

// 订单服务监听失败事件
@OnEvent('PaymentFailed')
async handlePaymentFailed(event: PaymentFailed) {
    await this.cancelOrder(event.orderId);
}

@OnEvent('InventoryReservationFailed')
async handleInventoryFailed(event: InventoryReservationFailed) {
    await this.cancelOrder(event.orderId);
    // 触发支付退款（通过另一个事件）
    await this.bus.publish('RefundRequested', { orderId: event.orderId });
}
```"""),

        ("实战工具", r"""## Temporal（最流行的 Saga 框架）

```typescript
// Workflow：业务逻辑
import { proxyActivities } from '@temporalio/workflow';

const activities = proxyActivities({
    startToCloseTimeout: '1 minute',
    retry: { maximumAttempts: 3 }
});

export async function orderWorkflow(orderReq: OrderRequest): Promise<string> {
    try {
        const order = await activities.createOrder(orderReq);
        await activities.chargePayment(order);
        await activities.reserveInventory(order);
        const shipment = await activities.createShipment(order);
        await activities.markCompleted(order.id);
        return order.id;
    } catch (e) {
        // Temporal 自动补偿
        await activities.compensate(order);
        throw e;
    }
}

// Activity：实际的服务调用
export async function createOrder(orderReq: OrderRequest): Promise<Order> {
    // 调用 OrderService
}

export async function chargePayment(order: Order): Promise<void> {
    // 调用 PaymentService
}
```

Temporal 提供：
- 自动重试
- 状态持久化
- 故障恢复
- 工作流可视化

## Camunda（Java BPMN）

```java
@ProcessApplication
public class OrderSagaProcess {
    public static final String KEY = "order-saga";

    @Autowired private RuntimeService runtimeService;

    public void start(OrderRequest request) {
        Map<String, Object> variables = Map.of("order", request);
        runtimeService.startProcessInstanceByKey(KEY, variables);
    }
}
```

Camunda 用 BPMN 图定义 Saga 流程，业务分析师可以直接修改。"""),

        ("适用边界", """✅ **使用场景**：
- 跨服务业务流程（下单 + 支付 + 库存 + 发货）
- 最终一致性可接受（不是强 ACID）
- 业务步骤可补偿（有明确的「撤销」动作）

❌ **避免场景**：
- 强一致要求（金融核心交易，用 2PC / 分布式锁）
- 没有补偿动作（业务操作不可逆）
- 业务极简（不需要 Saga）

🔄 **演进路径**：
- 单体本地事务 → 拆服务 → Saga
- Orchestration（中央协调） → Choreography（事件链）
- 手写 Saga → Temporal / Camunda

💡 **最佳实践**：
- 每个 Saga 操作都要有补偿动作
- 补偿也要幂等（防止重复补偿）
- Saga 状态要持久化（崩溃可恢复）
- 监控 Saga 完成时间 + 失败率
- 优先 Orchestration（更易调试）"""),

       ])


def ch05_sidecar() -> None:
    mk("05-architectural-patterns/sidecar.md", "Sidecar 边车模式",
       "辅助能力剥离主应用 + K8s Pod / Istio / Dapr / Envoy",
       [
        ("核心问题", """业务应用经常需要一些**与业务无关**的辅助能力：
- 日志收集
- 监控埋点
- 配置中心
- 服务发现
- 链路追踪
- 熔断限流

但把这些能力塞进主应用会导致：
1. 语言绑定（Java 应用的日志格式 vs Node 应用不同）
2. 升级困难（日志 SDK 升级需要重写业务代码）
3. 主应用膨胀（10% 业务代码 + 90% 辅助代码）
4. 团队耦合（业务团队被迫关心基础设施）"""),

        ("核心思想", """把辅助能力从主应用中剥离，部署在同一个 Host / Pod 的「边车」容器 / 进程中。

**关键点**：
- 边车与主应用共享网络 / 存储 / 生命周期
- 边车与主应用通过本地 IPC 通信
- 边车可以独立升级、独立选择技术栈"""),

        ("Kubernetes Pod 实战", r"""```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-sidecars
spec:
  containers:
    - name: app                          # 主应用
      image: myapp:1.0
      ports:
        - containerPort: 8080
      volumeMounts:
        - name: logs
          mountPath: /var/log/app

    - name: fluent-bit                   # 边车 1：日志收集
      image: fluent-bit:2.0
      volumeMounts:
        - name: logs
          mountPath: /var/log/app  # 共享日志目录

    - name: istio-proxy                  # 边车 2：服务网格数据面
      image: istio/proxyv2:1.20.0

    - name: prometheus-exporter          # 边车 3：指标导出
      image: prom/node-exporter:1.5
      ports:
        - containerPort: 9100

  volumes:
    - name: logs
      emptyDir: {}  # Pod 共享存储
```

四个容器：
- **app**：业务应用
- **fluent-bit**：收集 app 日志并发送到 ES
- **istio-proxy**：拦截网络流量，提供熔断 / 链路追踪
- **prometheus-exporter**：暴露指标给 Prometheus"""),

        ("服务网格 Istio", r"""Istio 数据面就是经典的 Sidecar：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    metadata:
      labels:
        app: order-service
        # 关键：注入 Istio sidecar
    spec:
      containers:
        - name: order-service
          image: order-service:1.0
        # istio-proxy 自动注入：
        # - name: istio-proxy
        #   image: docker.io/istio/proxyv2:1.20.0
```

Istio sidecar 提供：
- **流量管理**：负载均衡 / 熔断 / 重试
- **安全**：mTLS 加密
- **可观测性**：自动埋点 / 链路追踪
- **策略**：限流 / 黑白名单

业务应用零修改，所有这些能力由 sidecar 提供。"""),

        ("Dapr（分布式应用运行时）", r"""Dapr 是 Sidecar 模式的另一个典范：

```yaml
# Kubernetes 部署
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:1.0
          env:
            - name: DAPR_HTTP_PORT
              value: "3500"
        - name: daprd
          image: daprio/daprd:1.10
          args:
            - "--app-id=order-service"
            - "--components-path=/components"
```

```typescript
// 业务应用通过 Dapr sidecar 调用
import { DaprClient } from '@dapr/dapr';

const client = new DaprClient();

// 调用其他服务（不直接 HTTP，交给 Dapr）
await client.invoker.invoke('payment-service', 'charge', { amount: 100 });

// 发布订阅
await client.pubsub.publish('order-events', { orderId: '123' });

// 状态存储
await client.state.save('statestore', [{ key: 'order-123', value: order }]);

// 密钥管理
const secret = await client.secret.get('vault', 'api-key');
```

Dapr 把分布式能力（服务调用 / 状态 / 事件 / 配置）封装成 sidecar，业务应用通过 HTTP / gRPC 调用 sidecar。"""),

        ("Envoy 边缘代理", r"""Envoy 是 Sidecar 模式的另一个核心实现：

```yaml
# Envoy 作为 sidecar 代理
static_resources:
  listeners:
    - name: listener_0
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 8080  # 拦截主应用的所有出口流量
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                route_config:
                  virtual_hosts:
                    - domains: ['*']
                      routes:
                        - match: { prefix: '/' }
                          route: { cluster: main_app }
  clusters:
    - name: main_app
      connect_timeout: 1s
      type: STATIC
      load_assignment:
        cluster_name: main_app
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address: { socket_address: { address: 127.0.0.1, port_value: 9090 } }
```

Envoy sidecar 提供：
- HTTP/2 / gRPC 代理
- 熔断 / 重试 / 超时
- 负载均衡
- 指标 / 日志 / 追踪"""),

        ("适用边界", """✅ **使用场景**：
- 多语言微服务（避免每个语言重写日志/监控/追踪）
- 辅助能力统一（Istio / Dapr 等基础设施）
- 升级解耦（业务应用不用随基础设施升级）
- 安全合规（统一加密 / 认证）

❌ **避免场景**：
- 性能极敏感（sidecar 有 IPC 开销）
- 单体应用（不需要拆）
- 边车能力极简（直接放主应用更简单）

🔄 **演进路径**：
- 单体应用 → 微服务
- 业务代码内置辅助能力 → SDK → Sidecar
- 自研 Sidecar → 用现成 Istio / Dapr

💡 **最佳实践**：
- Sidecar 应该是无状态的（容易扩缩）
- Sidecar 失败不应影响主应用（要 try-catch）
- 不要让 Sidecar 持有业务状态（违反职责）
- 用 K8s operator 自动注入 sidecar（避免每个 deployment 手动加）"""),

       ])


def ch05_circuit_breaker() -> None:
    mk("05-architectural-patterns/circuit-breaker.md", "Circuit Breaker 熔断模式",
       "下游故障快速失败 + Resilience4j / Sentinel / Hystrix + 三种状态",
       [
        ("核心问题", """当下游服务出现故障时（响应慢 / 异常率高 / 完全不可用），上游服务如果继续调用会导致：

1. **线程池耗尽**：上游请求 hang 在等待下游
2. **资源耗尽**：CPU / 内存 / 连接池被占满
3. **雪崩效应**：整个系统级联失败
4. **用户体验差**：超时 30 秒后才返回错误"""),

        ("核心思想", """当检测到下游故障率超过阈值时，**熔断器打开**，上游直接快速失败（fallback），不调用下游，给下游恢复时间。

**三种状态**：
```
       失败率 < 阈值        失败率 ≥ 阈值
CLOSED ──────────────→ OPEN
   ↑                      │
   │    经过 sleepWindow   │
   └──── HALF_OPEN ←──────┘
            │
            │ 试探请求成功 → CLOSED
            │ 试探失败 → OPEN
```"""),

        ("Resilience4j 实战", r"""```java
@Service
public class PaymentService {
    @CircuitBreaker(name = "payment", fallbackMethod = "paymentFallback")
    public PaymentResult pay(PaymentRequest req) {
        return paymentClient.charge(req);  // 可能超时 / 抛异常
    }

    // 熔断后的 fallback（必须有相同签名 + Throwable 参数）
    private PaymentResult paymentFallback(PaymentRequest req, Throwable t) {
        log.warn("payment service unavailable: {}", t.getMessage());
        // 1. 排队等待 / 异步重试
        // 2. 返回默认值
        // 3. 抛业务异常
        return PaymentResult.deferred(req.getOrderId());
    }
}

// 配置
resilience4j:
  circuitbreaker:
    instances:
      payment:
        failureRateThreshold: 50        # 失败率 50% 触发熔断
        slowCallRateThreshold: 100      # 慢调用 100% 触发
        slowCallDurationThreshold: 2s   # 2 秒算慢调用
        slidingWindowSize: 100          # 滑动窗口 100 个请求
        minimumNumberOfCalls: 10        # 至少 10 个请求才计算
        waitDurationInOpenState: 10s    # OPEN 状态保持 10 秒
        permittedNumberOfCallsInHalfOpenState: 3  # HALF_OPEN 试 3 次
        recordExceptions:
          - java.io.IOException
          - java.util.concurrent.TimeoutException
        ignoreExceptions:
          - com.example.BusinessException  # 业务异常不计入失败
```

## 编程式使用

```java
CircuitBreaker circuitBreaker = CircuitBreaker.ofDefaults("payment");

CheckedSupplier<PaymentResult> supplier = CircuitBreaker.decorateCheckedSupplier(
    circuitBreaker,
    () -> paymentClient.charge(req)
);

try {
    return Try.of(supplier).getOrElse(this::fallback);
} catch (Throwable e) {
    return fallback(req, e);
}
```"""),

        ("阿里 Sentinel", r"""```java
// Sentinel 是阿里开源的熔断限流组件
@SentinelResource(value = "payment", blockHandler = "paymentBlockHandler", fallback = "paymentFallback")
public PaymentResult pay(PaymentRequest req) {
    return paymentClient.charge(req);
}

public PaymentResult paymentBlockHandler(PaymentRequest req, BlockException e) {
    // 流控熔断
    return PaymentResult.rejected(req.getOrderId());
}

public PaymentResult paymentFallback(PaymentRequest req, Throwable e) {
    // 业务异常
    return PaymentResult.deferred(req.getOrderId());
}
```

## Sentinel 控制台

Sentinel Dashboard 提供：
- 实时监控（QPS / 响应时间 / 异常率）
- 规则配置（流控 / 熔断 / 热点）
- 集群限流
- 链路监控"""),

        ("Hystrix（已停止维护）", r"""```java
// Hystrix 是 Netflix 开源的第一代熔断器，已停止维护
// 但仍有大量遗留代码使用

@HystrixCommand(
    fallbackMethod = "paymentFallback",
    commandProperties = {
        @HystrixProperty(name = "circuitBreaker.errorThresholdPercentage", value = "50"),
        @HystrixProperty(name = "circuitBreaker.requestVolumeThreshold", value = "20"),
        @HystrixProperty(name = "circuitBreaker.sleepWindowInMilliseconds", value = "10000")
    }
)
public PaymentResult pay(PaymentRequest req) {
    return paymentClient.charge(req);
}
```

## Resilience4j vs Sentinel vs Hystrix

| | Resilience4j | Sentinel | Hystrix |
|---|---|---|---|
| 语言 | Java 8+ | Java | Java |
| 设计 | 函数式 | 注解 + 控制台 | 注解 |
| 限流 | ✅ | ✅ | ✅ |
| 熔断 | ✅ | ✅ | ✅ |
| 控制台 | ❌ | ✅（官方 Dashboard）| ✅（Hystrix Dashboard）|
| 维护 | ✅ 活跃 | ✅ 活跃 | ❌ 停止 |

推荐新项目用 **Resilience4j** 或 **Sentinel**。"""),

        ("配置参数详解", """## 关键参数

| 参数 | 含义 | 推荐值 |
|---|---|---|
| **failureRateThreshold** | 失败率阈值 | 50% |
| **slowCallRateThreshold** | 慢调用率阈值 | 100% |
| **slowCallDurationThreshold** | 慢调用时长阈值 | 2s |
| **slidingWindowSize** | 滑动窗口大小 | 100 |
| **minimumNumberOfCalls** | 计算失败率最小请求数 | 10 |
| **waitDurationInOpenState** | OPEN 状态等待时间 | 10s |
| **permittedNumberOfCallsInHalfOpenState** | HALF_OPEN 试探次数 | 3-5 |
| **recordExceptions** | 计入失败的异常 | IOException, TimeoutException |
| **ignoreExceptions** | 忽略的异常 | BusinessException |

## Fallback 策略

1. **返回默认值**：订单标记「待处理」
2. **排队等待**：写入 Kafka 异步重试
3. **走备用路径**：调用备用服务
4. **抛业务异常**：让上层决定（用户友好提示）"""),

        ("适用边界", """✅ **使用场景**：
- 调用下游 HTTP / gRPC 服务
- 调用数据库 / Redis / 外部 API
- 关键路径（不能让慢调用拖垮）
- 高并发场景（防止雪崩）

❌ **避免场景**：
- 单体内部调用（不跨网络）
- 性能极敏感（熔断器有开销）
- 业务简单到不会失败（过度设计）

🔄 **配套模式**：
- **Bulkhead**：舱壁隔离（资源池）
- **Retry**：重试（结合熔断使用）
- **Timeout**：超时控制（熔断的前置条件）
- **Fallback**：降级策略（熔断后的行为）

💡 **最佳实践**：
- 必须配 fallback（不配等于没熔断）
- 超时时间要合理（不能太长）
- 区分业务异常（不计入失败率）
- 监控熔断器状态变化（告警）"""),

       ])


def ch05_bulkhead() -> None:
    mk("05-architectural-patterns/bulkhead.md", "Bulkhead 舱壁隔离模式",
       "资源隔离防雪崩 + Resilience4j 线程池 + K8s resource limit + 连接池隔离",
       [
        ("核心问题", """当多个下游服务共享同一个资源池（线程池 / 连接池）时，一个慢服务会占满所有资源，拖垮所有其他服务调用。

**举例**：
- 共享 100 个线程：90 个被慢 payment 调用占满，剩下 10 个给 inventory / order / 用户请求
- 共享 100 个数据库连接：90 个被慢查询占满，所有其他数据库操作排队
- 共享 1000 个并发：100 个慢请求把所有带宽占满"""),

        ("核心思想", """把资源按业务 / 服务**隔离**成多个独立池，每个池有自己的容量上限。一个池被打满不会影响其他池。

**两种隔离方式**：

| 方式 | 适用 | 案例 |
|---|---|---|
| **线程池隔离** | 不同下游服务 | Resilience4j Bulkhead |
| **信号量隔离** | 同一进程内 | Resilience4j SemaphoreBulkhead |
| **连接池隔离** | 数据库 / HTTP 客户端 | HikariCP / OkHttp |
| **进程隔离** | K8s Pod | K8s resource limit |"""),

        ("Resilience4j 舱壁实战", r"""```java
@Service
public class OrderService {
    // 舱壁 1：支付服务（独立线程池）
    @Bulkhead(name = "payment", type = Bulkhead.Type.THREADPOOL, fallbackMethod = "paymentFallback")
    public PaymentResult pay(PaymentRequest req) {
        return paymentClient.charge(req);
    }

    // 舱壁 2：库存服务（独立线程池）
    @Bulkhead(name = "inventory", type = Bulkhead.Type.THREADPOOL, fallbackMethod = "inventoryFallback")
    public ReserveResult reserve(List<OrderItem> items) {
        return inventoryClient.reserve(items);
    }

    // 舱壁 3：HTTP 客户端（信号量隔离）
    @Bulkhead(name = "http", type = Bulkhead.Type.SEMAPHORE)
    public List<Product> searchProducts(String query) {
        return httpClient.search(query);
    }
}

resilience4j:
  bulkhead:
    instances:
      payment:
        maxThreadPoolSize: 20           # 支付服务最多 20 线程
        maxWaitDuration: 100ms           # 排队最多等 100ms

      inventory:
        maxThreadPoolSize: 15
        maxWaitDuration: 50ms

      http:
        maxConcurrentCalls: 100          # 信号量：最多 100 并发
        maxWaitDuration: 0              # 不等待
```

即使 payment 服务慢导致 20 个线程全占满，inventory 仍有自己的 15 个线程可用。"""),

        ("Spring Cloud Hystrix 舱壁", r"""```java
@HystrixCommand(
    groupKey = "paymentService",
    threadPoolKey = "paymentPool",
    threadPoolProperties = {
        @HystrixProperty(name = "coreSize", value = "20"),
        @HystrixProperty(name = "maxQueueSize", value = "50")
    },
    fallbackMethod = "paymentFallback"
)
public PaymentResult pay(PaymentRequest req) {
    return paymentClient.charge(req);
}

@HystrixCommand(
    groupKey = "inventoryService",
    threadPoolKey = "inventoryPool",
    threadPoolProperties = {
        @HystrixProperty(name = "coreSize", value = "15")
    }
)
public ReserveResult reserve(List<OrderItem> items) {
    return inventoryClient.reserve(items);
}
```"""),

        ("连接池隔离", r"""```typescript
// TypeScript：每个下游服务独立 axios 实例（独立连接池）
const httpClients = {
    payment: axios.create({
        baseURL: 'https://payment.example.com',
        maxSockets: 10,           // 最多 10 个并发连接
        timeout: 5000,
    }),
    inventory: axios.create({
        baseURL: 'https://inventory.example.com',
        maxSockets: 15,
        timeout: 3000,
    }),
    analytics: axios.create({
        baseURL: 'https://analytics.example.com',
        maxSockets: 5,
        timeout: 10000,
    }),
};

// 即使 payment 服务挂掉，inventory 仍有自己的 15 个连接可用
```

## HikariCP 数据库连接池隔离

```yaml
spring:
  datasource:
    primary:
      url: jdbc:mysql://primary-db/mydb
      hikari:
        maximum-pool-size: 20       # 主库连接池
        pool-name: PrimaryPool
    analytics:
      url: jdbc:mysql://analytics-db/mydb
      hikari:
        maximum-pool-size: 5        # 分析库连接池（独立）
        pool-name: AnalyticsPool

// 主库慢查询占满 primary 池，analytics 池不受影响
```"""),

        ("Kubernetes 进程隔离", r"""```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:1.0
          resources:
            requests:
              cpu: 100m      # 至少 0.1 核
              memory: 128Mi  # 至少 128 MB
            limits:
              cpu: 500m      # 最多 0.5 核
              memory: 512Mi  # 最多 512 MB
```

K8s 是终极舱壁：
- 每个 Pod 有自己的 CPU / 内存上限
- 一个 Pod 内存爆掉 → OOM Kill → 不影响其他 Pod
- Namespace 进一步隔离（资源配额 `ResourceQuota`）"""),

        ("实战案例：Hystrix Dashboard", r"""Hystrix Dashboard 可视化各舱壁状态：

```
Thread Pools:
┌────────────┬──────┬───────┬────────┬──────────┐
│ Name       │ Active│ Queue│ PoolSize│ MaxSize  │
├────────────┼──────┼───────┼────────┼──────────┤
│ payment    │   2  │   0   │   18   │   20     │
│ inventory  │   1  │   0   │   14   │   15     │
│ analytics  │   0  │   0   │    3   │    5     │
└────────────┴──────┴───────┴────────┴──────────┘
```

监控每个舱壁的：
- 活跃线程数（接近 maxSize 告警）
- 队列长度（堆积告警）
- 拒绝率（达到上限拒绝）"""),

        ("适用边界", """✅ **使用场景**：
- 调用多个下游服务（避免相互影响）
- 关键路径与非关键路径隔离
- 不同业务有不同 SLA
- K8s 多租户（避免 noisy neighbor）

❌ **避免场景**：
- 调用单一服务（不需要隔离）
- 资源极有限（隔离会浪费）
- 业务极简（直接调即可）

🔄 **与 Circuit Breaker 区别**：
- **Bulkhead**：资源隔离（防雪崩）
- **Circuit Breaker**：快速失败（防拖延）

💼 **组合使用**：
```yaml
# 同时配置 Bulkhead + Circuit Breaker + Timeout + Retry
# 这四个是分布式 resilience 的「四大金刚」
resilience4j:
  bulkhead:
    instances:
      payment: { maxThreadPoolSize: 20 }
  circuitbreaker:
    instances:
      payment: { failureRateThreshold: 50 }
  timelimiter:
    instances:
      payment: { timeoutDuration: 2s }
  retry:
    instances:
      payment: { maxAttempts: 3 }
```

💡 **最佳实践**：
- 线程池大小 = QPS × 平均响应时间 + buffer
- 监控舱壁活跃度（接近 maxSize 告警）
- 与 Circuit Breaker 组合使用
- 优先 K8s 进程隔离（最彻底）"""),

       ])


def ch05_strangler_fig() -> None:
    mk("05-architectural-patterns/strangler-fig.md", "Strangler Fig 绞杀者模式",
       "渐进式迁移 monolith + API Gateway 流量切换 + Netflix / Amazon / 蚂蚁金服",
       [
        ("核心问题", """Monolith 系统（巨石应用）有以下问题：
- 代码复杂（百万行级）
- 部署困难（一次部署影响全局）
- 技术栈僵化（无法引入新语言 / 新框架）
- 团队规模大（沟通成本指数增长）
- 故障影响范围广（一个 bug 可能挂全部）

但**完全重写**风险极高：
- 业务不能中断（在线服务 24/7）
- 重写通常需要 1-2 年（业务早已变化）
- 工程师流失（写新系统的人走了）
- 数据迁移风险（旧数据格式可能丢失）"""),

        ("核心思想", """**逐步**用新服务**包裹**旧系统，逐步把流量从旧系统迁移到新服务。最终旧系统只剩壳子，被「绞杀」。

**类比自然界**：绞杀榕（Strangler Fig）从种子长成树，根系包裹宿主树，最终宿主被绞死。"""),

        ("三阶段迁移", r"""```text
阶段 1：共存（0-3 月）
┌──────────────────────────┐
│      Monolith (旧)        │
│   ┌──────────────────┐   │
│   │  Business Logic  │   │    ┌──────────────────┐
│   │                  │   │    │   新服务 A        │
│   └──────────────────┘   │    │  (新功能独立)    │
│                          │    └──────────────────┘
└──────────────────────────┘
              ▲
              │
         API Gateway
         (分发路由)


阶段 2：迁移（3-18 月）
┌──────────────────────────┐
│      Monolith (旧)        │
│   ┌──────────────────┐   │    ┌──────────────────┐
│   │  部分业务 (迁移中) │   │    │   新服务 A        │
│   └──────────────────┘   │    │  (已迁移)        │
│   ┌──────────────────┐   │    ├──────────────────┤
│   │  剩余业务 (未迁移) │   │    │   新服务 B        │
│   └──────────────────┘   │    │  (迁移中)        │
└──────────────────────────┘    ├──────────────────┤
              ▲                │   新服务 C        │
              │                │  (新功能独立)    │
         API Gateway           └──────────────────┘
         (灰度分流)


阶段 3：绞杀（18-24 月）
┌──────────────────────────┐
│      Monolith (空壳)      │    ┌──────────────────┐
│   ┌──────────────────┐   │    │   新服务 A        │
│   │   几乎无业务     │   │    ├──────────────────┤
│   └──────────────────┘   │    │   新服务 B        │
└──────────────────────────┘    ├──────────────────┤
              ▲                │   新服务 C        │
              │                ├──────────────────┤
         API Gateway           │   新服务 D        │
         (全部新服务)           └──────────────────┘

→ 最终下线 Monolith
```"""),

        ("API Gateway 流量切换", r"""```nginx
# Nginx：10% 流量切到新服务
upstream old_service {
    server old.internal:8080;
}

upstream new_service {
    server new.internal:8080;
}

server {
    location /api/users {
        # 灰度策略：基于 cookie / header / 比例
        set $backend old_service;
        if ($http_x_canary = "true") {        # 1. 内部员工全量
            set $backend new_service;
        }
        if ($cookie_user_group = "beta") {    # 2. Beta 用户
            set $backend new_service;
        }
        # 3. 10% 随机抽样
        set $rand $request_id;
        if ($rand ~ "^.{0}$") {
            set $backend new_service;
        }
        proxy_pass http://$backend;
    }
}
```

## Spring Cloud Gateway

```java
@Bean
public RouteLocator routes(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("user-service", r -> r.path("/api/users/**")
            .uri("lb://user-service-new"))  // 全部走新服务
        .route("order-service", r -> r.path("/api/orders/**")
            .uri("lb://order-service"))  // 还在旧服务
        .build();
}

// 灰度
@Bean
public RouteLocator grayRoutes(RouteLocatorBuilder builder) {
    return builder.routes()
        .route("order-gray", r -> r.path("/api/orders/**")
            .and().header("X-Canary", "true")
            .uri("lb://order-service-new"))
        .route("order-main", r -> r.path("/api/orders/**")
            .uri("lb://order-service-old"))
        .build();
}
```"""),

        ("实战案例", r"""## Netflix

Netflix 是 Strangler Fig 的典范：
- 2008 年：单块 DVD 租赁系统
- 2009-2015：迁移到 AWS 微服务（500+ 服务）
- 迁移用了 7 年，期间业务持续运营

关键经验：
- **不要停机**：每天 1.5 亿次 API 调用不能断
- **逐步迁移**：每次迁移 1-2 个服务，灰度切换
- **数据迁移**：双写 + 后台校验 + 最终一致

## Amazon

- 2002 年开始从 monolith 拆出 SOA
- 2010 年代完成（用了 8+ 年）
- 关键经验：CEO Jeff Bezos 强制要求**所有团队必须通过 API 通信**

## 京东

- 2014 年开始订单系统迁移
- 迁移期间经历多次 618 / 双 11 大促
- 关键经验：**先迁移非核心业务（评论 / 收藏），最后迁移核心（下单 / 支付）**

## 蚂蚁金服

- 2014 年开始从 IOE（IBM / Oracle / EMC）迁移到 SOFA
- 用了 5+ 年完成
- 关键经验：**单元化架构**（按用户 ID 拆分，独立单元独立部署）"""),

        ("迁移策略选择", """## 数据迁移

### 双写 + 后台校验

```java
@Service
public class UserService {
    @Autowired private OldUserRepo oldRepo;
    @Autowired private NewUserRepo newRepo;

    @Transactional
    public void update(User user) {
        oldRepo.save(user);  // 写旧库
        // 异步双写新库
        CompletableFuture.runAsync(() -> newRepo.save(user));

        // 后台校验：定期比对旧库 vs 新库
        // 发现不一致 → 修复 + 告警
    }
}

// 验证脚本（每日跑）
@Scheduled(cron = "0 2 * * *")  // 凌晨 2 点
public void verify() {
    List<User> oldUsers = oldRepo.findAll();
    for (User old : oldUsers) {
        User newUser = newRepo.findById(old.getId()).orElseThrow();
        if (!old.equals(newUser)) {
            alertService.report(old, newUser);
        }
    }
}
```

## 流量切换

| 阶段 | 比例 | 时长 |
|---|---|---|
| 内部员工 | 100% | 1 周 |
| Beta 用户 | 10% | 2 周 |
| 灰度 | 10% → 50% | 2-4 周 |
| 全量 | 100% | — |

每一步都有**回滚预案**（出问题立即切回旧服务）。"""),

        ("适用边界", """✅ **使用场景**：
- 业务不能中断（在线服务）
- 代码历史包袱重（无法重写）
- 团队分批交付（新功能要上线）
- 业务复杂度高（重写风险大）

❌ **避免场景**：
- 业务极简（直接重写）
- 流量太小（不值得拆分）
- 没有 API Gateway 基础设施
- 团队无微服务经验

🔄 **替代方案**：
- **完全重写**：业务简单 / 团队有能力
- **Carving**：直接从 monolith 抽模块
- **Modular Monolith**：不拆分，先模块化

💡 **最佳实践**：
- API Gateway 是关键基础设施
- 数据迁移用双写 + 校验
- 每个迁移步骤都有回滚预案
- 监控新旧两套系统的指标差异
- 优先迁移非核心业务，最后迁移核心"""),

       ])


def ch05_outbox() -> None:
    mk("05-architectural-patterns/outbox.md", "Outbox 事务性发件箱",
       "业务数据 + 消息同事务 + Debezium / Spring Modulith + 防止消息丢失",
       [
        ("核心问题", """业务系统经常需要「写业务数据 + 发消息」（订单创建后发订单事件），但两个操作不在同一个事务中：

```java
// ❌ 双写问题：业务写库成功 + 消息发送失败
@Transactional
public void createOrder(Order o) {
    orderRepo.save(o);
    kafka.send(new OrderCreatedEvent(o));  // 失败 → 消息丢失
}

@Transactional
public void createOrder(Order o) {
    orderRepo.save(o);
    // 事务提交后再发送？可能发送前进程崩溃
    TransactionSynchronizationManager.register(...);
}
```

**问题**：
1. **消息丢失**：业务写库成功 + 消息发送失败 → 状态不一致
2. **消息重复**：业务写库失败 + 消息发送成功 → 重复消息
3. **顺序错乱**：业务库的事务回滚了，消息已经发出"""),

        ("核心思想", """把"业务数据变更 + 发送消息"合并到**同一个本地事务**中：

1. 业务表写入数据
2. 同时把消息写入 **outbox 表**（同事务）
3. 单独的 **relay 进程**轮询 outbox 表，把消息发到 Kafka / RabbitMQ
4. 发送成功后标记 outbox 记录为已发布
5. 定期清理已发布记录（避免表无限增长）"""),

        ("Java 实战", r"""```java
// Outbox 实体
@Entity
@Table(name = "outbox")
public class OutboxEvent {
    @Id private UUID id;
    private String aggregateType;       // 'Order'
    private String aggregateId;         // 'order-123'
    private String eventType;           // 'OrderCreated'
    @Column(columnDefinition = "TEXT") private String payload;  // JSON
    private Instant createdAt;
    private Instant publishedAt;        // null 表示未发布
}

// 业务操作：写订单 + 写 outbox 在同一事务
@Service
@Transactional
public class OrderService {
    @Autowired private OrderRepository orderRepo;
    @Autowired private OutboxRepository outboxRepo;

    public void createOrder(OrderRequest req) {
        Order order = Order.create(req);
        orderRepo.save(order);

        // 同事务：写 outbox 事件
        OutboxEvent event = new OutboxEvent();
        event.setId(UUID.randomUUID());
        event.setAggregateType("Order");
        event.setAggregateId(order.getId());
        event.setEventType("OrderCreated");
        event.setPayload(toJson(order));
        event.setCreatedAt(Instant.now());
        outboxRepo.save(event);
    }
}

// Relay 进程：轮询 outbox 表发送消息
@Component
public class OutboxRelay {
    @Autowired private OutboxRepository outboxRepo;
    @Autowired private KafkaTemplate<String, String> kafka;

    @Scheduled(fixedDelay = 1000)  // 每秒轮询
    public void relay() {
        List<OutboxEvent> unpublished = outboxRepo.findUnpublished(100);
        for (OutboxEvent e : unpublished) {
            try {
                kafka.send("order-events", e.getAggregateId(), e.getPayload()).get(5, TimeUnit.SECONDS);
                e.setPublishedAt(Instant.now());
                outboxRepo.save(e);
            } catch (Exception ex) {
                log.error("Failed to publish outbox event {}", e.getId(), ex);
                // 不标记已发布，下次重试
            }
        }
    }
}

// 定时清理已发布记录（30 天前）
@Scheduled(cron = "0 3 * * *")  // 每天凌晨 3 点
public void cleanup() {
    Instant cutoff = Instant.now().minus(30, ChronoUnit.DAYS);
    outboxRepo.deleteByPublishedAtBefore(cutoff);
}
```"""),

        ("Debezium CDC 模式", r"""更优雅的方案：用 Debezium 监听 binlog 自动生成消息，**不需要写 outbox 代码**：

```yaml
# Debezium 配置：监听 MySQL binlog
name: outbox-connector
config:
  connector.class: io.debezium.connector.mysql.MySqlConnector
  database.hostname: mysql
  database.port: 3306
  database.user: debezium
  database.password: dbz
  database.server.id: 184054
  database.server.name: dbserver1
  database.include.list: mydb
  table.include.list: mydb.outbox
  transforms: outbox
  transforms.outbox.type: io.debezium.transforms.outbox.EventRouter
```

应用代码只需要把事件写到 outbox 表（任意表结构），Debezium 自动：
1. 监听 binlog
2. 把 outbox 表的新行转成 Kafka 消息
3. 自动发布到 Kafka topic

**优势**：
- 应用代码简单（不写 relay 进程）
- 自动 exactly-once（基于 binlog offset）
- 业务侵入小

## Spring Modulith Outbox

```java
@Service
@Transactional
public class OrderService {
    @Autowired private OrderRepository orderRepo;
    @Autowired private ApplicationEventPublisher events;

    public void createOrder(OrderRequest req) {
        Order order = Order.create(req);
        orderRepo.save(order);

        // Spring Modulith 自动把事件写入 outbox 表
        events.publishEvent(new OrderCreatedEvent(order));
    }
}

// application.yml：Spring Modulith 自动启用 outbox
spring:
  modulith:
    events:
      outbox:
        enabled: true
```"""),

        ("outbox 表设计", r"""```sql
CREATE TABLE outbox (
    id              UUID PRIMARY KEY,
    aggregate_type  VARCHAR(255) NOT NULL,
    aggregate_id    VARCHAR(255) NOT NULL,
    event_type      VARCHAR(255) NOT NULL,
    payload         TEXT NOT NULL,
    metadata        JSONB,              -- 额外信息（trace_id / user_id 等）
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    published_at    TIMESTAMP,          -- null = 未发布
    retry_count     INT DEFAULT 0,
    last_error      TEXT
);

CREATE INDEX idx_outbox_unpublished ON outbox (created_at) WHERE published_at IS NULL;
CREATE INDEX idx_outbox_cleanup ON outbox (published_at);
```

## 关键字段

| 字段 | 用途 |
|---|---|
| `aggregate_type` | 聚合根类型（Order / User） |
| `aggregate_id` | 聚合根 ID |
| `event_type` | 事件类型（OrderCreated / OrderPaid） |
| `payload` | JSON 序列化的事件 |
| `published_at` | 已发布时间（null = 未发布）|
| `retry_count` | 重试次数（避免无限重试）|
| `last_error` | 最后一次错误（调试用）|"""),

        ("实战：Debezium + Kafka 完整链路", r"""```text
┌─────────┐     ┌─────────┐     ┌──────────┐     ┌─────────┐
│ Order   │────→│ MySQL   │────→│ Debezium │────→│ Kafka   │
│ Service │     │ outbox  │     │ CDC      │     │ topic   │
└─────────┘     │ table   │     └──────────┘     └────┬────┘
                └─────────┘                            │
                                                       ▼
                                                ┌──────────┐
                                                │ Downstream│
                                                │ Services │
                                                └──────────┘

1. OrderService 写入 orders 表 + outbox 表（同事务）
2. Debezium 监听 outbox 表的 binlog
3. Debezium 把新行转成 Kafka 消息（自动）
4. 下游服务（payment / inventory / notification）消费 Kafka
5. exactly-once 投递（基于 binlog offset）
```

**优势**：
- **不丢失**：outbox 表与业务表同事务
- **不重复**：Kafka exactly-once 语义 + Debezium offset
- **保序**：binlog 顺序保证
- **低耦合**：业务不直接调下游，通过事件驱动"""),

        ("适用边界", """✅ **使用场景**：
- 业务写库 + 发消息必须原子
- 不能容忍消息丢失（订单 / 支付事件）
- 高可靠性要求的金融系统

❌ **避免场景**：
- 消息丢失可接受（日志 / 监控事件）
- 业务能容忍最终一致
- 没有 outbox 表的基础设施

🔄 **演进路径**：
- 直接发消息 → 事务后异步发 → Outbox → Debezium CDC
- Debezium CDC 是当前最佳实践

💡 **最佳实践**：
- outbox 表和业务表同库（避免分布式事务）
- 用 Debezium 而不是手写 relay
- 配置清理策略（30 天前的已发布事件）
- 监控 outbox 表堆积（未发布 > 1 万告警）
- 给下游消费者设置幂等"""),

       ])


# ============================================================================
# Chapter 06: Anti-Patterns (7 stubs)
# ============================================================================

def ch06_god_object() -> None:
    mk("06-anti-patterns/god-object.md", "God Object 上帝对象",
       "症状 + 病因 + 药方 + 检测工具 + 重构案例",
       [
        ("症状", """```java
// 一个类 5000+ 行，承担一切职责
public class UserManager {
    public User createUser(...) { /* 50 行 */ }
    public void sendEmail(...) { /* 100 行 */ }
    public Order processOrder(...) { /* 200 行 */ }
    public Report generateReport(...) { /* 300 行 */ }
    public void exportCSV(...) { /* 150 行 */ }
    public void auditLog(...) { /* 80 行 */ }
    public void validateInput(...) { /* 60 行 */ }
    public void updateCache(...) { /* 90 行 */ }
    // ... 30+ 个职责
}
```

**典型表现**：
1. **类行数 > 1000**（甚至 5000+）
2. **字段 > 30 个**（各种状态）
3. **方法 > 50 个**（什么都能干）
4. **依赖 > 20 个**（所有服务都依赖）
5. **任何改动都会影响这个类**
6. **新人不敢改这个类**（怕踩雷）"""),

        ("病因", """1. **「这个类刚好能装下这些功能」**
   - 早期业务简单，后来塞功能

2. **缺少职责拆分意识（违反 SRP）**
   - 一个类应该有且只有一个变更理由

3. **工期压力下"先这样吧"**
   - 「先把这个功能加到这个类，下次再拆」

4. **错误地把"共享状态"作为聚合理由**
   - 多个功能用同一个字段 → 全塞一个类

5. **代码审查不到位**
   - 没人问"这个方法为什么在这个类"

6. **没有架构守护**
   - 没有 lint / SonarQube 等工具限制类大小"""),

        ("药方", r"""## 1. 按职责拆分（SRP）

```java
// 拆分前
class UserManager { /* 5000 行 */ }

// 拆分后
class UserService {          // 用户 CRUD
    public User create(UserRequest req) { /* ... */ }
    public User findById(long id) { /* ... */ }
}

class EmailService {         // 邮件发送
    public void sendWelcomeEmail(User u) { /* ... */ }
}

class OrderService {         // 订单处理
    public Order createOrder(OrderRequest req) { /* ... */ }
}

class ReportService {        // 报表生成
    public Report generateReport(ReportCriteria c) { /* ... */ }
}

class CsvExporter {          // CSV 导出
    public byte[] export(List<Report> reports) { /* ... */ }
}

class AuditLogger {          // 审计日志
    public void log(String action, Object data) { /* ... */ }
}
```

## 2. 组合优于继承（Facade）

```java
// 用 Facade 模式对外提供统一接口（兼容旧 API）
class UserFacade {
    private final UserService userService;
    private final EmailService emailService;
    private final AuditLogger auditLogger;

    public User createUser(UserRequest req) {
        var user = userService.create(req);
        emailService.sendWelcomeEmail(user);
        auditLogger.log("user.created", user);
        return user;
    }
}
```

## 3. 定期审视

- 每月 review 类行数排行（`cloc` / `SonarQube`）
- 把超长类列入重构清单
- 季度重构 sprint（专门拆上帝类）"""),

        ("检测工具", r"""## SonarQube

```
Rule: Class size (cognitive complexity, lines of code)
Threshold: 
  - Critical: > 1000 lines / cognitive complexity > 50
  - Major: > 500 lines
```

## CodeScene（识别 Hotspot）

```bash
# 找出"高频修改 + 高复杂度"的类
codescene analyze --repo-path . --complexity-threshold 50 --change-frequency-threshold 20
```

## ESLint（JavaScript / TypeScript）

```json
{
  "rules": {
    "max-lines": ["warn", { "max": 500, "skipComments": true }],
    "max-lines-per-function": ["warn", { "max": 100 }],
    "complexity": ["warn", 20]
  }
}
```

## Java 自定义 ArchUnit

```java
@ArchTest
static final ArchRule no_god_classes = classes()
    .that().areNotEnums()
    .and().areNotInterfaces()
    .should(notHaveTooManyMethods(50))
    .because("Classes with > 50 methods violate SRP (Single Responsibility Principle)");

@ArchTest
static final ArchRule no_god_classes_by_lines = classes()
    .should(new ArchCondition<JavaClass>("have less than 1000 lines") {
        public void check(JavaClass clazz, ConditionEvents events) {
            int lines = clazz.getSourceCode().map(s -> s.split("\n").length).orElse(0);
            if (lines > 1000) {
                events.add(SimpleConditionEvent.violated(clazz, clazz.getName() + " has " + lines + " lines"));
            }
        }
    });
```"""),

        ("重构案例：UserService 拆分", r"""假设 UserService 有 30 个方法，拆分为：

```text
UserService (300 行)
├── createUser / updateUser / deleteUser
├── findById / findByEmail
└── (核心 CRUD)

EmailService (200 行)
├── sendWelcomeEmail
├── sendPasswordReset
└── sendNotification

AuthService (200 行)
├── login / logout
├── refreshToken
└── validateToken

UserProfileService (150 行)
├── updateProfile
├── uploadAvatar
└── getProfile

AuditService (100 行)
└── logUserAction
```

**拆分原则**：
1. 按业务职责（CRUD / 邮件 / 认证）
2. 按变更频率（高频 vs 低频分开）
3. 按依赖关系（A 依赖 B，A 不知道 C）

**风险控制**：
1. 拆分前写好测试（覆盖所有方法）
2. 一次只拆一个职责（避免一次大爆炸）
3. 拆分后保持兼容（用 Facade 维持旧 API）
4. 灰度发布（10% → 50% → 100%）"""),

        ("适用边界", """✅ **识别信号**：
- 行数 > 1000 / 方法 > 50 / 依赖 > 20
- 任何改动都要碰这个类
- 新人入职看这个类需要 1 周

❌ **避免拆分**：
- 类行数 < 500（拆得过细反而难维护）
- 业务极简（拆分成本 > 收益）
- 没有足够测试覆盖（拆完容易出 bug）

💡 **预防**：
- **CI 检查**：SonarQube / ArchUnit 拦截超长类
- **code review**：每个 PR 问"这个方法真的属于这个类？"
- **架构守护**：每个 Service / Manager / Util 都有限定职责
- **文档先行**：每个类写明"我是谁，我能做什么"（不要让我猜）"""),

       ])


def ch06_anemic_model() -> None:
    mk("06-anti-patterns/anemic-model.md", "Anemic Model 贫血模型",
       "症状 + 病因 + 药方 + 充血模型 vs 贫血模型",
       [
        ("症状", r"""```java
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
5. 单测要 mock 大量 Service 才能测业务"""),

        ("病因", """1. **把 Entity 当 DTO 用**
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
   - 不懂「充血模型」/「Rich Domain Model」"""),

        ("药方：充血模型", r"""```java
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
```"""),

        ("Domain Events 模式", r"""```java
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
```"""),

        ("充血模型 vs 贫血模型对比", """| | 贫血模型 | 充血模型 |
|---|---|---|
| 实体 | 只有 getter/setter | 有状态 + 行为 |
| 业务逻辑 | 在 Service | 在实体 |
| Service | 编排 + 业务 | 编排（薄） |
| 测试 | 测 Service | 测实体（纯逻辑） |
| 复用 | 难（逻辑在 Service）| 易（实体行为可）） |
| 维护 | 改动要改多处 | 改动集中 |
| 学习 | 简单 | 需 DDD |"""),

        ("重构案例", r"""## 重构前：贫血模型

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
```"""),

        ("适用边界", """✅ **充血模型适用**：
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
- **测试实体**：实体测试是纯单元测试（不需要 mock）"""),

       ])


def ch06_big_ball_of_mud() -> None:
    mk("06-anti-patterns/big-ball-of-mud.md", "Big Ball of Mud 大泥球",
       "症状 + 病因 + 药方 + DDD 限界上下文 + 架构守护",
       [
        ("症状", r"""```java
// Util 类什么都往里塞
public class Util {
    public static String formatDate(Date d) { /* ... */ }
    public static User parseUserJson(String s) { /* ... */ }
    public static BigDecimal calcTax(BigDecimal amount) { /* ... */ }
    public static String generateUUID() { /* ... */ }
    public static void sendEmail(String to, String subject) { /* ... */ }
    public static boolean validatePhone(String phone) { /* ... */ }
    // 200+ 方法，无业务分类
}

// Helper1 / Helper2 / NewHelper / Util2 / Manager1
// 业务逻辑分散在 Controller / Service / Util / Helper 等 5+ 个地方
```

**典型表现**：
1. 没有模块边界（任何文件都能 import 任何文件）
2. 命名混乱（`Util`、`Helper`、`Manager1`、`NewService`）
3. 业务逻辑分散（同一个功能在 5+ 个文件）
4. 改一行代码不知道会破坏什么
5. 测试覆盖率极低（不知道从哪里开始测）
6. 新人入职 3 个月才能上手"""),

        ("病因", """1. **没有架构规范**
   - 谁都能加新模块 / 新文件
   - 没有「包结构」「类命名」规范

2. **缺少 code review**
   - 业务赶进度，无 review
   - 烂代码越积越多

3. **业务变更频繁，代码跟着打补丁**
   - 「修一个 bug 加一个 if-else」

4. **没有架构守护（ArchUnit / Checkstyle）**
   - 工具无法自动拦截违规

5. **团队分批加入，新人风格各异**
   - 没人统一风格

6. **文档缺失 / 过时**
   - 没有「架构图」「包结构说明」"""),

        ("药方", r"""## 1. DDD 限界上下文（按业务拆分）

```text
用户域 (user-context)
├── UserController
├── UserService
├── UserRepository
├── User (领域模型)
└── UserEvents

订单域 (order-context)
├── OrderController
├── OrderService
├── OrderRepository
├── Order (领域模型)
└── OrderEvents

支付域 (payment-context)
├── PaymentController
├── PaymentService
├── PaymentRepository
├── Payment (领域模型)
└── PaymentEvents

公共域 (common)
├── DateUtil          (只做日期格式化)
├── JsonUtil          (只做 JSON 解析)
├── TaxCalculator     (只做税计算)
└── EmailValidator    (只做邮箱校验)
```

**关键**：每个域只暴露 API，通过事件或 RPC 跨域通信。

## 2. 命名规范

```java
// ❌ 混乱命名
public class Util { /* 什么都干 */ }
public class Helper { /* 又一个什么都干 */ }
public class Manager1 { /* 业务 1 */ }
public class NewService { /* 业务 2 */ }

// ✅ 语义化命名
public class DateFormatter { /* 只做日期格式化 */ }
public class UserJsonParser { /* 只做 User JSON 解析 */ }
public class TaxCalculator { /* 只计算税 */ }
public class UserService { /* 只做用户业务 */ }
public class OrderProcessor { /* 只处理订单 */ }
```

每个类名要回答「我是谁」+「我能做什么」。

## 3. 架构守护

```java
// ArchUnit：禁止 Util 类混乱
@ArchTest
static final ArchRule no_util_classes = noClasses()
    .that().haveSimpleName("Util")
    .or().haveSimpleName("Helper")
    .or().haveSimpleName("Manager")
    .because("Util/Helper/Manager often become God classes");

// 禁止跨域依赖（订单域不能直接访问支付域内部类）
@ArchTest
static final ArchRule bounded_contexts = noClasses()
    .that().resideInAPackage("com.example.order..")
    .should().dependOnClassesThat().resideInAPackage("com.example.payment.internal..")
    .because("Order context can only depend on Payment API, not internal");

// Service 类必须有 Service 后缀
@ArchTest
static final ArchRule service_naming = classes()
    .that().areAnnotatedWith(Service.class)
    .should().haveSimpleNameEndingWith("Service");
```"""),

        ("工具与流程", r"""## Checkstyle

```xml
<module name="MethodCount">
    <property name="maxTotal" value="30"/>
</module>

<module name="FileLength">
    <property name="max" value="500"/>
</module>

<module name="ClassFanOutComplexity">
    <property name="max" value="20"/>
</module>
```

## SonarQube

```yaml
sonar:
  qualityGate:
    conditions:
      - metric: cognitive_complexity
        operator: GT
        value: 50
        resource: file
      - metric: file_complexity
        operator: GT
        value: 200
```

## CodeScene

```bash
# 找出"代码复杂度 + 修改频率"高的 Hotspot
codescene analyze --repo-path . --complexity-threshold 50
# 输出：Top 10 Hotspots（这些文件优先重构）
```

## 依赖图

```bash
# dependency-cruiser（JavaScript / TypeScript）
depcruise --validate .dependency-cruiser.json src/

# IntelliJ IDEA：右键 → Diagrams → Show Dependencies
```

## 文档先行

```markdown
# docs/architecture.md

## 模块结构
- user-context: 用户管理
- order-context: 订单管理
- payment-context: 支付管理

## 跨域通信
- order-context 通过 EventBus 发布 OrderCreatedEvent
- payment-context 订阅 OrderCreatedEvent，触发支付

## 命名规范
- *Service: 业务编排
- *Repository: 数据访问
- *Controller: HTTP 接口
- *Factory: 创建逻辑
- *Validator: 校验
- 禁止 Util / Helper / Manager 这种「什么都干」的命名
```"""),

        ("重构案例：拆 Util", r"""## 重构前

```java
public class CommonUtil {
    // 100+ 方法
    public static String formatDate(Date d) { /* ... */ }
    public static User parseUserJson(String s) { /* ... */ }
    public static BigDecimal calcTax(BigDecimal amount, String region) { /* ... */ }
    public static String maskCardNo(String cardNo) { /* ... */ }
    public static boolean isValidEmail(String email) { /* ... */ }
    public static String generateOrderNo() { /* ... */ }
    public static String encryptPassword(String pwd) { /* ... */ }
    // ...
}
```

## 重构后

```text
common/
├── date/
│   └── DateFormatter.java          // 只做日期格式化
├── json/
│   ├── UserJsonParser.java
│   └── OrderJsonParser.java
├── tax/
│   └── TaxCalculator.java          // 只算税
├── crypto/
│   ├── CardMasker.java
│   └── PasswordEncryptor.java
├── validation/
│   ├── EmailValidator.java
│   └── PhoneValidator.java
└── id/
    └── OrderNoGenerator.java
```

每个类职责单一，行数 < 100，新人 5 分钟能看懂。"""),

        ("适用边界", """✅ **大泥球识别**：
- 新人入职 3 个月仍搞不清模块边界
- 任何改动都要碰 5+ 个文件
- 测试覆盖率 < 30%
- 「这代码谁写的」是高频问题

❌ **避免过度拆分**：
- 业务极简（< 10 个类）不需要 DDD
- 团队规模 < 5 人不需要复杂架构
- 性能极敏感（拆分增加网络开销）

💡 **最佳实践**：
- **架构文档**：每个项目维护一份 `ARCHITECTURE.md`
- **code review**：每个 PR 检查「这代码放对地方了吗」
- **架构守护**：ArchUnit / Checkstyle 自动拦截
- **季度重构**：把大泥球列入技术债
- **培训优先**：新人入职讲架构（不是讲语言）"""),

       ])


def ch06_callback_hell() -> None:
    mk("06-anti-patterns/callback-hell.md", "Callback Hell 回调地狱",
       "症状 + 病因 + 药方 + async/await + Promise + RxJS",
       [
        ("症状", r"""```javascript
// 嵌套 8 层回调，可读性为 0
getData(function(a) {
    {
        getMoreData(a, function(b) {
            {
                getMoreData(b, function(c) {
                    {
                        getMoreData(c, function(d) {
                            {
                                getMoreData(d, function(e) {
                                    {
                                        getMoreData(e, function(f) {
                                            // 最终在这里写业务逻辑
                                            console.log(f);
                                        }, errorHandler);
                                    }
                                }, errorHandler);
                            }
                        }, errorHandler);
                    }
                }, errorHandler);
            }
        }, errorHandler);
    }
}, errorHandler);
```

**典型表现**：
1. 嵌套层级 > 5
2. 每个回调都可能失败（errorHandler 重复）
3. 业务逻辑被埋到最深处
4. 错误处理复杂（多层 try-catch）
5. 难以追踪异步流程"""),

        ("病因", """1. **JavaScript 早期没有 Promise / async-await**
   - ES5 之前只能用 callback
   - Node.js 早期 API 都是 callback 风格

2. **不熟悉现代异步原语**
   - 团队仍在用 callback 写新代码

3. **强行用回调解决异步问题**
   - 该用 Promise 的场景用了 callback
   - 该用 async/await 的场景用了 Promise.then

4. **第三方库 callback 嵌套（库设计问题）**
   - 某些库（如早期 fs / mongoose）API 就是 callback
   - 但现在都有 Promise 版本

5. **缺少 Async / Await 培训**
   - 团队没学过现代异步写法"""),

        ("药方", r"""## 1. Promise 链

```javascript
// ✅ Promise 链（ES6+）
getData()
    .then(a => getMoreData(a))
    .then(b => getMoreData(b))
    .then(c => getMoreData(c))
    .then(d => getMoreData(d))
    .then(e => getMoreData(e))
    .then(f => {
        // 业务逻辑
        console.log(f);
    })
    .catch(err => {
        // 统一错误处理
        console.error(err);
    });
```

## 2. async/await（最现代）

```javascript
// ✅ async/await（ES2017+）
async function process() {
    try {
        const a = await getData();
        const b = await getMoreData(a);
        const c = await getMoreData(b);
        const d = await getMoreData(c);
        const e = await getMoreData(d);
        const f = await getMoreData(e);
        // 业务逻辑
        console.log(f);
    } catch (err) {
        // 统一错误处理
        console.error(err);
    }
}
```

## 3. 并行执行

```javascript
// ✅ 并行（如果任务独立）
const [a, b, c] = await Promise.all([
    getData1(),
    getData2(),
    getData3(),
]);
```

## 4. RxJS / Observables

```javascript
// ✅ RxJS（复杂异步流）
import { of, from, forkJoin } from 'rxjs';
import { mergeMap, catchError } from 'rxjs/operators';

from(initialData$).pipe(
    mergeMap(a => from(getMoreData(a))),
    mergeMap(b => from(getMoreData(b))),
    catchError(err => of({ error: err }))
).subscribe(result => console.log(result));
```

## 5. Coroutine（Kotlin / Python）

```kotlin
// Kotlin coroutine
suspend fun process() {
    try {
        val a = getData()
        val b = getMoreData(a)
        // ...
    } catch (e: Exception) {
        // 错误处理
    }
}
```

```python
# Python asyncio
async def process():
    try:
        a = await get_data()
        b = await get_more_data(a)
        # ...
    except Exception as e:
        # 错误处理
        pass
```"""),

        ("实战：Node.js 异步演进", r"""```javascript
// ❌ 早期 Node.js (2010)
fs.readFile('file1.txt', function(err, data1) {
    if (err) throw err;
    fs.readFile('file2.txt', function(err, data2) {
        if (err) throw err;
        fs.readFile('file3.txt', function(err, data3) {
            if (err) throw err;
            console.log(data1 + data2 + data3);
        });
    });
});

// ✅ Node.js 现代（util.promisify）
const fs = require('fs').promises;
const data1 = await fs.readFile('file1.txt', 'utf-8');
const data2 = await fs.readFile('file2.txt', 'utf-8');
const data3 = await fs.readFile('file3.txt', 'utf-8');
console.log(data1 + data2 + data3);

// ✅ Promise.all 并行
const [data1, data2, data3] = await Promise.all([
    fs.readFile('file1.txt', 'utf-8'),
    fs.readFile('file2.txt', 'utf-8'),
    fs.readFile('file3.txt', 'utf-8'),
]);
```

## Go 也曾经有回调地狱

```go
// ❌ Go 早期（callback）
func process(cb func(result string, err error)) {
    go func() {
        // 嵌套回调
        fetch1(func(a string, err error) {
            if err != nil { cb("", err); return }
            fetch2(a, func(b string, err error) {
                if err != nil { cb("", err); return }
                fetch3(b, func(c string, err error) {
                    if err != nil { cb("", err); return }
                    cb(c, nil)
                })
            })
        })
    }()
}

// ✅ Go channel + goroutine
func process(ctx context.Context) (string, error) {
    a, err := fetch1(ctx)
    if err != nil { return "", err }
    b, err := fetch2(ctx, a)
    if err != nil { return "", err }
    c, err := fetch3(ctx, b)
    if err != nil { return "", err }
    return c, nil
}
```"""),

        ("异步错误处理", r"""```javascript
// ❌ 异步 callback 错误处理（每层都要检查）
asyncTask1(function(err, result1) {
    if (err) return callback(err);
    asyncTask2(result1, function(err, result2) {
        if (err) return callback(err);
        asyncTask3(result2, function(err, result3) {
            if (err) return callback(err);
            callback(null, result3);
        });
    });
});

// ✅ async/await：try-catch 一处搞定
async function process() {
    try {
        const r1 = await asyncTask1();
        const r2 = await asyncTask2(r1);
        const r3 = await asyncTask3(r2);
        return r3;
    } catch (err) {
        // 任何一层出错都会被捕获
        console.error('Process failed:', err);
        throw err;
    }
}
```

## Promise 错误处理

```javascript
// .catch() 在链尾
getData()
    .then(a => getMoreData(a))
    .then(b => getMoreData(b))
    .catch(err => console.error(err));  // 任何 .then() 抛错都被捕获
```

## Go error 显式处理

```go
result, err := process(ctx)
if err != nil {
    log.Printf("process failed: %v", err)
    return err
}
```

Go 没有 try-catch，但每个调用都显式 err 判断，避免「忘了检查」。"""),

        ("适用边界", """✅ **使用 async/await**：
- 所有现代 JavaScript / TypeScript 项目
- Node.js 12+ / 浏览器 ES2017+

✅ **使用 Promise**：
- 需要并行多个异步任务（Promise.all）
- 需要链式调用但不一定用 await

✅ **使用 RxJS**：
- 复杂异步流（debounce / throttle / 复杂合并）

✅ **使用 Coroutine**：
- Python（asyncio）
- Kotlin / Swift

❌ **避免 callback**：
- 新写的代码（用 Promise / async）
- ES2017+ 环境（用 async/await）
- 可以用 Promise 化的库（`util.promisify`）

💡 **最佳实践**：
- **优先 async/await**（最现代、可读性最好）
- **并行用 Promise.all**（而不是顺序 await）
- **try-catch 兜底**（一处处理所有错误）
- **超时处理**：`AbortController` / `Promise.race`
- **库选择**：选有 Promise 版本的库（不用 callback 版）"""),

       ])


def ch06_circular_dependency() -> None:
    mk("06-anti-patterns/circular-dependency.md", "Circular Dependency 循环依赖",
       "症状 + 病因 + 药方 + 依赖反转 + 领域事件 + 检测工具",
       [
        ("症状", r"""```
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
5. ORM 双向关联 + JSON 序列化 → StackOverflowError"""),

        ("病因", """1. **模块边界设计错误**
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
   - 试图拆分微服务但公用同一份代码"""),

        ("药方", r"""## 1. 依赖反转（DIP）

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
- **事件解耦**：A 发事件，B 订阅"""),

        ("ORM 双向关联 + 序列化", r"""```java
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
```"""),

        ("检测工具", r"""## Java ArchUnit

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
```"""),

        ("实战案例：拆分用户和订单", r"""## 重构前（循环依赖）

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
- 可以独立部署 / 拆分微服务"""),

        ("适用边界", """✅ **识别循环依赖**：
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
- **重新设计边界**：拆不开就合（拆不开说明本来就是一个）"""),

       ])


def ch06_magic_number() -> None:
    mk("06-anti-patterns/magic-number.md", "Magic Number 魔数",
       "症状 + 病因 + 药方 + 命名常量 + 配置文件 + 单元常量",
       [
        ("症状", r"""```java
// 代码中充斥无解释数字
if (retryCount > 3) { /* 重试 */ }
if (temperature > 100) { /* 过热 */ }
if (cacheSize * 0.95 > maxSize) { /* 触发清理 */ }
Thread.sleep(5000);  // 为什么是 5 秒？
String salt = generateSalt(32);  // 为什么 32？
if (user.getAge() >= 18) { /* 成年人 */ }
BigDecimal taxRate = new BigDecimal("0.06");  // 为什么 6%？
```

**典型表现**：
1. 代码中有 `100`、`0.95`、`5000` 这类数字字面量
2. 数字含义不明（不知道是 KB 还是 MB）
3. 同一数字在多处重复出现
4. 修改一个数字要在多处查找替换
5. 新人看不懂「为什么是这个数字」"""),

        ("病因", """1. **直接 hardcode 数字**（最常见）
   - 「先这样吧」心态
   - 没有常量定义规范

2. **没有常量定义规范**
   - 团队没有常量命名约定
   - 不知道该放在哪个类

3. **"反正能跑"心态**
   - 数字能用就行，不管含义

4. **配置文件未启用**
   - 业务参数应该走配置文件
   - 但开发者偷懒写死在代码里

5. **缺少 code review**
   - 没人问"这个 100 是什么意思"

6. **重构时遗留下未命名的魔数**
   - 原作者知道含义，新人不知道"""),

        ("药方", r"""## 1. 命名常量

```java
public class RetryConfig {
    public static final int MAX_RETRY_COUNT = 3;
    public static final Duration RETRY_INTERVAL = Duration.ofMillis(5000);
    public static final int RETRY_BACKOFF_FACTOR = 2;
}

public class CacheConfig {
    public static final long MAX_CACHE_SIZE = 1_000_000L;  // 100 万
    public static final double HIGH_WATER_RATIO = 0.95;    // 95%
    public static final Duration CACHE_TTL = Duration.ofMinutes(30);
}

public class BusinessConstants {
    public static final int MIN_AGE_FOR_ADULT = 18;
    public static final BigDecimal TAX_RATE = new BigDecimal("0.06");
    public static final int PASSWORD_SALT_LENGTH = 32;
}
```

## 2. 配置文件化（Spring）

```java
@Configuration
@ConfigurationProperties(prefix = "app.retry")
@Data
public class RetryProperties {
    private int maxAttempts = 3;
    private Duration interval = Duration.ofMillis(5000);
    private int backoffFactor = 2;
}

// application.yml
app:
  retry:
    max-attempts: 5          # 可调整，不改代码
    interval: 10s
    backoff-factor: 2
```

## 3. 枚举常量

```java
public enum UserRole {
    GUEST(0),
    USER(1),
    ADMIN(2),
    SUPER_ADMIN(3);

    private final int level;

    UserRole(int level) { this.level = level; }

    public boolean canDeleteUsers() {
        return this.level >= ADMIN.level;
    }
}

// 用法：role.canDeleteUsers() 而不是 role.getLevel() >= 2
```

## 4. 单元常量

```java
// ❌ 单位不明
Thread.sleep(5000);
cache.setMaxSize(1000000);

// ✅ 明确单位
Thread.sleep(Duration.ofSeconds(5).toMillis());
cache.setMaxSize(Size.megabytes(1000));
```"""),

        ("检测工具", r"""## ESLint（TypeScript / JavaScript）

```json
{
    "rules": {
        "no-magic-numbers": ["error", {
            "ignore": [-1, 0, 1, 2],
            "ignoreArrayIndexes": true,
            "enforceConst": true
        }]
    }
}
```

## Checkstyle（Java）

```xml
<module name="MagicNumber">
    <property name="ignoreNumbers" value="0, 1, 2, -1, 100"/>
    <property name="ignoreHashCodeMethod" value="true"/>
    <property name="ignoreAnnotation" value="true"/>
</module>
```

## SonarQube

```
Rule: Magic numbers should not be used
Severity: Major
Description: Magic numbers are numbers that appear in code without explanation.
```

## IntelliJ IDEA

```text
Settings → Editor → Inspections → Java → Code style issues → Magic number
勾选 → 红色高亮魔数
```"""),

        ("实战案例：缓存配置", r"""## 重构前

```java
public class CacheService {
    public void put(String key, Object value) {
        long size = redisTemplate.opsForValue().get("cache:size");
        if (size > 1000000) {                          // 100 万？
            cleanup();
        }
        if (Math.random() < 0.05) {                    // 5%？
            persistToDisk();
        }
        redisTemplate.opsForValue().set(key, value, 30, TimeUnit.MINUTES);  // 30 分钟？
    }
}
```

## 重构后

```java
public class CacheConfig {
    public static final long MAX_CACHE_SIZE = 1_000_000L;
    public static final double PERSIST_PROBABILITY = 0.05;
    public static final Duration DEFAULT_TTL = Duration.ofMinutes(30);
}

public class CacheService {
    @Autowired private RedisTemplate<String, Object> redisTemplate;

    public void put(String key, Object value) {
        long size = redisTemplate.opsForValue().get("cache:size");
        if (size > CacheConfig.MAX_CACHE_SIZE) {
            cleanup();
        }
        if (Math.random() < CacheConfig.PERSIST_PROBABILITY) {
            persistToDisk();
        }
        redisTemplate.opsForValue().set(
            key,
            value,
            CacheConfig.DEFAULT_TTL.toMinutes(),
            TimeUnit.MINUTES
        );
    }
}
```

或者用配置文件：

```yaml
app:
  cache:
    max-size: 1000000
    persist-probability: 0.05
    default-ttl: 30m
```

```java
@ConfigurationProperties(prefix = "app.cache")
@Data
public class CacheProperties {
    private long maxSize = 1_000_000L;
    private double persistProbability = 0.05;
    private Duration defaultTtl = Duration.ofMinutes(30);
}
```"""),

        ("业务常量 vs 魔数", """## 魔数（必须消除）

```java
Thread.sleep(5000);          // ❌
```

```java
private static final Duration RETRY_INTERVAL = Duration.ofSeconds(5);
Thread.sleep(RETRY_INTERVAL.toMillis());  // ✅
```

## 业务常量（保留魔数语义）

```java
private static final BigDecimal TAX_RATE = new BigDecimal("0.06");
private static final int ADULT_AGE = 18;
```

业务常量即使有名字，含义仍可能不清晰，需要**注释**说明。

```java
/**
 * 中国增值税税率（一般纳税人）
 * 国家税务总局 2019 年公告
 */
private static final BigDecimal VAT_RATE = new BigDecimal("0.13");

/**
 * 法定成年年龄（《民法典》17、18 条）
 */
private static final int LEGAL_ADULT_AGE = 18;
```

## 配置文件化（业务可调参数）

```yaml
app:
  pricing:
    tax-rate: 0.06
    discount-rate: 0.10
  age:
    legal-adult: 18
    senior: 60
```

**判断标准**：
- 业务规则相关 → 业务常量（命名 + 注释）
- 技术实现相关 → 配置文件
- 算式中间值 → 命名常量
- -1 / 0 / 1 / 100 这类通用值 → 允许"""),

        ("适用边界", """✅ **必须命名**：
- 业务规则阈值（年龄 / 税率 / 折扣率）
- 算法参数（重试次数 / 超时时间 / 缓存大小）
- 算式中间值（高水位 / 低水位）
- 业务 ID 边界（管理员级别 / 状态码）

❌ **允许魔数**：
- 数组索引（`arr[0]`、`arr[1]`）
- 通用数学值（`-1`、`0`、`1`、`2`、`10`、`100`、`1000`）
- 循环边界（`for (int i = 0; i < 10; i++)`）
- 协议规定的值（HTTP 状态码、`null`、`true`、`false`）
- 单位换算（`1000` 表示 1 KB = 1000 字节）

💡 **最佳实践**：
- **CI 检查**：ESLint no-magic-numbers / Checkstyle
- **code review**：每个数字问"这是魔数吗？"
- **配置文件**：业务可调参数走 yml / properties
- **命名规范**：业务常量放 `*Constants.java`，技术常量放 `*Config.java`
- **注释解释**：业务常量加 Javadoc 引用法规 / 文档"""),

       ])


def ch06_premature_optimization() -> None:
    mk("06-anti-patterns/premature-optimization.md", "Premature Optimization 提前优化",
       "症状 + 病因 + 药方 + 性能分析 + Knuth 法则",
       [
        ("症状", r"""```java
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

**典型表现**：
1. 多层缓存（LRU + Caffeine + Redis）但没测过性能瓶颈
2. 「听说 Redis 很快」就加缓存
3. 复杂索引（联合索引 + 部分索引 + 函数索引）但 QPS 不高
4. 自定义数据结构替代 ArrayList / HashMap（但数据量不大）
5. 异步 / 并发代码（但 QPS 只有 100）"""),

        ("病因", """1. **Donald Knuth 警告过：「过早优化是万恶之源」**
   - 但被很多人「选择性遗忘」

2. **没做 profiling 就开始优化**
   - 不测就猜性能瓶颈
   - 90% 的猜测是错的

3. **「听说 Redis 很快」就加缓存**
   - 没考虑：数据一致性 / 缓存穿透 / 缓存雪崩
   - 没考虑：维护成本 > 性能收益

4. **「听说并行更快」就加并发**
   - 没考虑：线程切换开销 / 锁竞争 / 死锁风险

5. **追求「完美架构」**
   - 复杂架构有学习成本和维护成本
   - 简单架构 80% 够用

6. **老板/PM 压力**
   - 「能不能跑得更快一点」
   - 没数据支撑的优化"""),

        ("药方", r"""## 1. 先测量，后优化

```bash
# Java: JMH (Java Microbenchmark Harness)
jmh -prof gc -wi 5 -i 5 -f 1 .
# 输出：每个方法的吞吐量 / 平均时间 / GC 次数

# Go: pprof + benchmark
go test -bench=. -benchmem -cpuprofile=cpu.p
go tool pprof cpu.p
# 交互：(pprof) top10  // 看 CPU 占用最高的方法

# Python: cProfile
python -m cProfile -s cumtime script.py

# Node.js: 0x / clinic.js
clinic doctor -- node server.js

# 通用：APM 工具
# - Java: Arthas / async-profiler
# - Go: pprof / continuous profiling (Pyroscope)
# - Python: py-spy / Scalene
```

## 2. 80/20 法则

20% 的代码承担 80% 的性能问题：

```bash
# 找出热点（用 pprof）
go tool pprof cpu.p
(pprof) top10
# 80% 的 CPU 时间都在 /usr/local/go/net/http/server.go
# → 优化 HTTP 框架不是优化你的代码

(pprof) list myFunction
# 看自己的函数在做什么
```

## 3. YAGNI（You Aren't Gonna Need It）

```java
// ❌ 提前优化
public class UserService {
    // "未来可能有 100 万用户" → 加分页 + 缓存 + 多级缓存
    public List<User> findAll(int page, int size) {
        // 实际上系统只有 1000 用户
    }
}

// ✅ YAGNI：先实现再说
public class UserService {
    public List<User> findAll() {
        return userRepo.findAll();
    }
    // 真的有性能问题再加分页
}
```

## 4. Knuth 原文

```text
"We should forget about small efficiencies, say about 97% of the time:
premature optimization is the root of all evil.

Yet we should not pass up our opportunities in that critical 3%."
                                    —— Donald Knuth, 1974
```

**翻译**：97% 的情况下忘掉那些小效率（不要为它们优化），提前优化是万恶之源。但在关键的 3% 上不要放弃优化机会。

**关键**：**先测量再优化**，确定那 3% 在哪。"""),

        ("实战案例：缓存降级", r"""## 第一次实现（YAGNI）

```java
@Service
public class ProductService {
    @Autowired private ProductRepository repo;

    public Product findById(long id) {
        return repo.findById(id).orElseThrow();
    }
}
```

**性能**：100 QPS，平均延迟 5ms。**完全够用**。

## 性能问题出现（QPS 10000）

```bash
# pprof 报告显示 ProductService.findById 占 60% CPU
# 原因：DB 查询 + 网络 IO
```

## 添加一级缓存（Redis）

```java
@Service
public class ProductService {
    @Autowired private ProductRepository repo;
    @Autowired private RedisTemplate<String, Product> redis;

    public Product findById(long id) {
        // 1. 先查 Redis
        Product cached = redis.opsForValue().get("product:" + id);
        if (cached != null) return cached;

        // 2. 缓存未命中，查 DB
        Product product = repo.findById(id).orElseThrow();

        // 3. 写入 Redis
        redis.opsForValue().set("product:" + id, product, Duration.ofMinutes(10));
        return product;
    }
}
```

**性能**：5000 QPS，平均延迟 1ms。

## 仍然不够（QPS 50000）

```bash
# 再 profile 发现 Redis IO 占 40%
# 加本地缓存（Caffeine）
```

## 优化到极致（多级缓存）

```java
@Service
public class ProductService {
    @Autowired private ProductRepository repo;
    @Autowired private RedisTemplate<String, Product> redis;
    
    private final Cache<Long, Product> localCache = Caffeine.newBuilder()
        .maximumSize(10_000)
        .expireAfterWrite(Duration.ofMinutes(1))
        .build();

    public Product findById(long id) {
        // 1. 本地缓存（最快）
        Product cached = localCache.getIfPresent(id);
        if (cached != null) return cached;

        // 2. Redis
        cached = redis.opsForValue().get("product:" + id);
        if (cached != null) {
            localCache.put(id, cached);
            return cached;
        }

        // 3. DB
        Product product = repo.findById(id).orElseThrow();

        // 4. 写入两级缓存
        redis.opsForValue().set("product:" + id, product, Duration.ofMinutes(10));
        localCache.put(id, product);
        return product;
    }
}
```

**性能**：50000 QPS，平均延迟 0.1ms。

## 演进路径（关键）

| QPS | 实现 | 复杂度 |
|---|---|---|
| 100 | 直接查 DB | ⭐ |
| 5000 | + Redis 一级缓存 | ⭐⭐ |
| 50000 | + Caffeine 本地缓存 | ⭐⭐⭐ |
| 200000 | + 多级缓存 + 数据预热 | ⭐⭐⭐⭐ |

**关键**：每一步都有数据支撑，**不是提前实现的**。"""),

        ("常见过早优化", """## 1. 多层缓存（无 profiling）

```java
// ❌ 不必要的复杂
LRU + Caffeine + Redis + DB

// ✅ 真有性能问题再加
// 单层 Redis 解决 80% 场景
```

## 2. 自定义数据结构（无业务量）

```java
// ❌ 自定义跳表（数据量 < 1 万）
public class CustomSkipList<K, V> { /* 500 行 */ }

// ✅ Java 标准库够用
ConcurrentSkipListMap<K, V>
```

## 3. 复杂索引（无 QPS）

```sql
-- ❌ 加 5 个联合索引（QPS 只有 100）
CREATE INDEX idx1 ON orders(user_id, status, created_at);
CREATE INDEX idx2 ON orders(status, user_id, created_at);
-- ...

-- ✅ 单索引解决 80% 查询
CREATE INDEX idx_user_status ON orders(user_id, status);
```

## 4. 异步 + 队列（无并发量）

```java
// ❌ 所有操作都异步（QPS < 1000）
@Async public CompletableFuture<Order> create() { /* ... */ }

// ✅ 同步阻塞（QPS < 1000 完全可以）
public Order create() { /* 简单清晰 */ }
```

## 5. 微服务拆分（业务简单）

```java
// ❌ 5 个微服务（业务只有 3 个模块）
order-service / payment-service / inventory-service / shipping-service / notification-service

// ✅ 单体或模块化单体（业务初期）
OrderModule { /* 5 个 Service 放一起 */ }
```"""),

        ("何时优化 / 何时不优化", """## 不优化（97% 场景）

- ✅ 业务代码读起来清晰
- ✅ 性能不构成瓶颈（QPS < 1000）
- ✅ 没有用户投诉
- ✅ 没有 SLA 要求

## 优化（3% 场景）

- ⚠️ 监控告警：接口延迟 P99 > 1s
- ⚠️ 用户反馈：页面卡顿
- ⚠️ 容量预警：CPU / 内存使用率 > 80%
- ⚠️ 业务峰值：双 11 / 618 等大促

## 优化的正确流程

```text
1. 监控发现性能问题（不是猜的）
   ↓
2. profiling 找到瓶颈（不是拍脑袋）
   ↓
3. 优化瓶颈（最小改动）
   ↓
4. 验证优化效果（A/B 测试）
   ↓
5. 监控确认问题解决
   ↓
6. 记录到知识库（避免重复犯）
```

## 优化原则

1. **先测量后优化**（不要猜）
2. **80/20**（优化 20% 代码解决 80% 问题）
3. **简单优先**（单层 Redis 解决 80% 缓存问题）
4. **数据说话**（优化前后对比）
5. **回滚预案**（优化可能引入 bug）"""),

        ("适用边界", """✅ **避免优化**：
- 业务代码读起来清晰
- QPS < 1000
- 没有 SLA 要求
- 没有用户投诉

⚠️ **需要优化**：
- P99 > 1s（接口太慢）
- CPU / 内存 > 80%（资源紧张）
- 业务峰值（大促 / 突发流量）
- SLA 要求（P99 < 100ms）

💡 **最佳实践**：
- **监控先行**：APM 工具（SkyWalking / Datadog / Pyroscope）
- **profiling 工具**：JMH / pprof / async-profiler
- **性能测试**：JMeter / k6 / Gatling
- **A/B 测试**：优化前后对比
- **回滚预案**：优化可能引入 bug
- **文档记录**：每个优化都有 ADR"""),

       ])


# ============================================================================
# Main
# ============================================================================

def main() -> None:
    print(f"Generating design pattern stubs to {DOCS}\n")
    ch01_singleton()
    ch01_factory_method()
    ch01_abstract_factory()
    ch01_builder()
    ch01_prototype()
    ch02_adapter()
    ch02_bridge()
    ch02_composite()
    ch02_decorator()
    ch02_facade()
    ch02_flyweight()
    ch02_proxy()
    ch03_chain_of_responsibility()
    ch03_command()
    ch03_iterator()
    ch03_mediator()
    ch03_memento()
    ch03_observer()
    ch03_state()
    ch03_strategy()
    ch03_template_method()
    ch03_visitor()
    ch03_interpreter()
    ch04_dependency_injection()
    ch04_repository()
    ch04_specification()
    ch04_null_object()
    ch05_cqrs()
    ch05_event_sourcing()
    ch05_saga()
    ch05_sidecar()
    ch05_circuit_breaker()
    ch05_bulkhead()
    ch05_strangler_fig()
    ch05_outbox()
    ch06_god_object()
    ch06_anemic_model()
    ch06_big_ball_of_mud()
    ch06_callback_hell()
    ch06_circular_dependency()
    ch06_magic_number()
    ch06_premature_optimization()
    print(f"\nDone. 42 stubs generated.")


if __name__ == "__main__":
    main()