# 结构型模式总览

> GoF 23 模式中专门解决「类与对象如何组合」问题的 7 个模式。结构型模式通过**继承或组合**，让接口/实现分离、对象组合灵活、性能开销可控。

## 为什么需要结构型模式

继承是 OOP 的核心武器，但「过度继承」会让类层次爆炸、接口污染。结构型模式回答三个问题：

1. **如何适配不兼容的接口？** → Adapter / Bridge
2. **如何让对象组合替代继承？** → Composite / Decorator / Facade
3. **如何控制资源消耗？** → Flyweight / Proxy

## 7 种结构型模式速览

| 模式 | 核心问题 | 典型场景 |
|---|---|---|
| **Adapter 适配器** | 让原本接口不兼容的类可以合作 | 旧系统接入新 SDK / 包装第三方库 |
| **Bridge 桥接** | 抽象与实现分离，各自独立变化 | JDBC Driver / 跨平台 UI |
| **Composite 组合** | 树形结构，客户端一致对待单个对象和组合 | 文件系统 / DOM 树 / 组织架构 |
| **Decorator 装饰器** | 动态给对象添加职责，不改原类 | Java IO 流 / Go middleware / NestJS 拦截器 |
| **Facade 外观** | 为子系统提供统一高层接口 | Spring 的 JdbcTemplate / 第三方支付封装 |
| **Flyweight 享元** | 共享细粒度对象，减少内存 | 文本编辑器字符 / 游戏地图格子 / Java Integer 缓存 |
| **Proxy 代理** | 为对象提供占位符控制访问 | RPC 框架 / Spring AOP / 缓存代理 / 权限校验 |

## Adapter 适配器模式

### 核心思想

把一个类的接口转换成客户端期望的另一种接口，让原本接口不兼容的类可以合作。

### 两种适配器

| 类型 | 实现方式 | 适用场景 |
|---|---|---|
| **对象适配器**（组合） | 持有被适配者实例 | Java / Go 推荐 |
| **类适配器**（继承） | 继承被适配者 | C++ / 不推荐（多重继承歧义） |

### 实战：统一日志接口

```java
// 旧项目用的是 log4j，业务方想统一用 SLF4J 接口
public class Log4jToSlf4jAdapter implements org.slf4j.Logger {
    private final org.apache.log4j.Logger log4j;

    public Log4jToSlf4jAdapter(org.apache.log4j.Logger log4j) {
        this.log4j = log4j;
    }

    @Override
    public void info(String msg) {
        log4j.info(msg);
    }
    // ... 其他方法同样适配
}
```

### Java 生态经典案例

- `java.util.Arrays#asList()`：把数组适配成 List
- `java.io.InputStreamReader`：把字节流适配成字符流
- Spring `HandlerAdapter`：把各种 Controller 适配成统一的 Handler 接口

## Bridge 桥接模式

### 核心思想

将抽象部分与实现部分分离，使它们都可以独立变化。

### 与 Strategy / Adapter 的区别

| | Bridge | Strategy | Adapter |
|---|---|---|---|
| 目的 | 抽象与实现解耦 | 算法族切换 | 接口兼容 |
| 数量关系 | 多个实现 × 多个抽象 | 1 个抽象 × N 个算法 | 单向适配 |
| 关系 | 组合（聚合） | 组合 | 组合或继承 |

### 实战：JDBC Driver

```java
// JDBC 抽象层（java.sql.DriverManager）
// 各个数据库厂商实现 Driver 接口
// MySQL: com.mysql.cj.jdbc.Driver
// Oracle: oracle.jdbc.driver.OracleDriver
// PostgreSQL: org.postgresql.Driver

// 客户端只依赖 java.sql.Connection，与具体数据库无关
Connection conn = DriverManager.getConnection(url, user, pwd);
```

这就是 Bridge：抽象（JDBC API）和实现（各厂商 Driver）通过 DriverManager 这个桥接器连接。

## Composite 组合模式

### 核心思想

将对象组合成树形结构以表示「部分-整体」的层次结构。客户端对单个对象和组合对象使用**一致**的接口。

### 实战：文件系统

```typescript
// 目录和文件用同一个接口
interface FileSystemNode {
    getName(): string;
    getSize(): number;
    print(indent: string): void;
}

class File implements FileSystemNode {
    constructor(private name: string, private size: number) {}
    getSize() { return this.size; }
    print(indent: string) {
        console.log(`${indent}📄 ${this.name} (${this.size}B)`);
    }
}

class Directory implements FileSystemNode {
    private children: FileSystemNode[] = [];
    constructor(private name: string) {}

    add(node: FileSystemNode) {
        this.children.push(node);
    }

    getSize(): number {
        return this.children.reduce((sum, c) => sum + c.getSize(), 0);
    }

    print(indent: string) {
        console.log(`${indent}📁 ${this.name}/`);
        this.children.forEach(c => c.print(indent + '  '));
    }
}

// 客户端一致对待 file 和 directory
const root = new Directory('project');
const src = new Directory('src');
src.add(new File('index.ts', 1200));
src.add(new File('utils.ts', 800));
root.add(src);
root.add(new File('README.md', 2000));

root.print('');
// 📁 project/
//   📁 src/
//     📄 index.ts (1200B)
//     📄 utils.ts (800B)
//   📄 README.md (2000B)
```

### 经典案例

- Java AWT/Swing 组件树（Container + Component）
- HTML DOM（Node 子树）
- Kubernetes 资源树（Pod → Container）
- 组织架构树

## Decorator 装饰器模式

### 核心思想

动态地给对象添加职责，而不改变原类结构。装饰器模式是继承的替代方案，比继承更灵活（运行时添加/撤销）。

### 与 Proxy 的区别

| | Decorator | Proxy |
|---|---|---|
| 目的 | 增加新职责 | 控制访问 |
| 创建方 | 客户端主动包裹 | 通常由框架/容器创建 |
| 关注点 | 行为增强 | 访问控制 |

### 实战：Java IO 流

```java
// FileInputStream → BufferedInputStream → DataInputStream
// 每一层都是装饰器
DataInputStream dis = new DataInputStream(
    new BufferedInputStream(
        new FileInputStream("data.bin")));

int magic = dis.readInt();
long timestamp = dis.readLong();
```

### Go 中间件链（装饰器）

```go
// HTTP 中间件是经典的 Decorator
func LoggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        log.Printf("started %s %s", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
        log.Printf("completed in %v", time.Since(start))
    })
}

// 链式包裹
handler := LoggingMiddleware(AuthMiddleware(rateLimit.Handler))
```

### TypeScript 装饰器（语言级支持）

```typescript
// NestJS / Angular 大量使用
@Controller('/users')
class UserController {
    @Get('/:id')
    @UseGuards(AuthGuard)
    getUser(@Param('id') id: string) {
        return this.userService.findById(id);
    }
}
```

## Facade 外观模式

### 核心思想

为子系统中的一组接口提供一个统一的高层接口，使子系统更易使用。

### 实战：Spring JdbcTemplate

```java
// 不直接用 Connection/Statement/ResultSet，而是用 JdbcTemplate
jdbcTemplate.queryForObject("SELECT name FROM users WHERE id = ?",
    String.class, userId);

// 背后 JdbcTemplate 帮你处理：
// 1. 获取连接
// 2. 创建 PreparedStatement
// 3. 设置参数
// 4. 执行 SQL
// 5. 映射结果集
// 6. 关闭资源
```

### 何时使用 / 避免

✅ **使用**：第三方 SDK 封装（支付 / OAuth / 短信网关）
✅ **使用**：遗留系统的现代化接口
❌ **避免**：把 Facade 写成「上帝服务」，又把所有业务逻辑塞回来

## Flyweight 享元模式

### 核心思想

通过共享技术实现大量细粒度对象的复用，减少内存占用。

### 经典案例：Java Integer 缓存

```java
// Java 在 -128 ~ 127 范围内共享 Integer 对象
Integer a = 127;
Integer b = 127;
System.out.println(a == b);  // true（同一个对象）

Integer c = 128;
Integer d = 128;
System.out.println(c == d);  // false（不同对象）
```

### 实战：文本编辑器字符渲染

```java
class CharacterFlyweight {
    private final char ch;  // 内部状态（共享）
    // private int x, y;   // 外部状态（不共享）
    public CharacterFlyweight(char ch) { this.ch = ch; }
    public void render(int x, int y, Font font) {
        // 渲染时把外部状态传进来
    }
}
```

26 个字母 × 6 种字体 = 156 个对象（不是 1000 篇文章 × 1000 字）

## Proxy 代理模式

### 核心思想

为其他对象提供一种代理以控制对这个对象的访问。

### 5 种代理类型

| 类型 | 用途 | 案例 |
|---|---|---|
| **远程代理** | 隐藏对象在远程地址 | RPC stub（gRPC / Dubbo）|
| **虚拟代理** | 延迟加载大对象 | 浏览器图片懒加载 |
| **保护代理** | 控制访问权限 | Spring Security 鉴权 |
| **智能引用** | 附加额外行为（计数/锁）| CDN 缓存代理 |
| **缓存代理** | 缓存昂贵结果 | MyBatis 二级缓存 |

### 实战：Spring AOP

```java
// Spring AOP 用 JDK 动态代理 / CGLIB 字节码增强
@Service
public class OrderService {
    @Transactional
    public void createOrder(Order o) { /* ... */ }
}

// Spring 在运行时生成 OrderService 的代理：
// - 方法调用前开启事务
// - 方法调用后提交 / 异常时回滚
// - 客户端完全无感知
```

### gRPC 客户端 stub（远程代理）

```go
// .pb.go 自动生成
type OrderServiceClient interface {
    CreateOrder(ctx context.Context, in *CreateOrderRequest, opts ...grpc.CallOption) (*CreateOrderResponse, error)
}

// 客户端调用 stub，stub 帮你处理：
// 1. 序列化（protobuf）
// 2. 网络传输（HTTP/2）
// 3. 反序列化
// 4. 错误处理
resp, err := orderClient.CreateOrder(ctx, req)
```

## 7 模式对比速查表

| 模式 | 关系 | 复用粒度 | 是否改变接口 |
|---|---|---|---|
| Adapter | 适配 | 类级别 | ✅ 转换接口 |
| Bridge | 解耦 | 抽象/实现两维 | ✅ 抽象接口 |
| Composite | 树形 | 递归结构 | ❌ 一致接口 |
| Decorator | 增强 | 单对象 | ❌ 同接口 |
| Facade | 简化 | 子系统 | ✅ 简化接口 |
| Flyweight | 共享 | 细粒度对象 | ❌ 不变 |
| Proxy | 控制 | 单对象 | ❌ 不变（或转 RPC）|

## 实战建议

1. **优先 Decorator 而非继承**：要扩展行为，先想装饰器
2. **Facade 是 API 设计的核心**：每个对外服务都该有一层 Facade
3. **Proxy 是 AOP / RPC 的基础**：理解 Proxy 才能理解 Spring / gRPC
4. **Composite 注意类型安全**：Java 用 `instanceof` + 强制转换会很难维护，考虑 visitor
5. **Flyweight 慎用**：现代 JVM GC 已经很快，不必要的享元会增加复杂度
6. **Bridge 容易过度设计**：只有「两个独立变化维度」时才用

## 下一步

- 阅读每篇单独的 GoF 7 结构型模式细节：[Adapter](./adapter) / [Bridge](./bridge) / [Composite](./composite) / [Decorator](./decorator) / [Facade](./facade) / [Flyweight](./flyweight) / [Proxy](./proxy)
- 进阶：[现代模式 · Null Object](../04-modern-patterns/null-object)
- 反向自查：[反模式 · 大泥球](../06-anti-patterns/big-ball-of-mud)（结构混乱的常见病）