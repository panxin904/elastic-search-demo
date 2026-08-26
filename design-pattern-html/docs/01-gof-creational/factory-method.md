---
title: Factory Method 工厂方法模式
description: 创建逻辑延迟到子类 + 框架扩展点 + Java Spring BeanFactory / Go Wire 源码解读
---

# Factory Method 工厂方法模式

## 核心问题

创建对象时不知道将来会创建哪些具体类，或者希望把「创建逻辑」推迟到子类决定。

**经典场景**：
- 日志库（Log4j / SLF4j）：业务方只调 `LoggerFactory.getLogger()`，不知道底层是 Log4j 还是 Logback
- 数据库驱动（JDBC）：业务方只调 `DriverManager.getConnection()`，不知道是 MySQL 还是 PG
- HTTP 服务器（Go `http.Handler`）：业务方实现 Handler 接口，框架决定何时调用

## 核心思想

定义一个创建对象的抽象方法（`factoryMethod()`），让子类决定具体实例化哪个类。

**对比简单工厂**：简单工厂用 if-else 硬编码；工厂方法把 if-else 推迟到子类覆写。

## UML 结构

```text
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
```

## 多语言实现

## Java：经典实现

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
```

## 实战：框架中的应用

## Spring BeanFactory

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
```

## 适用边界

✅ **使用场景**：
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
- 配合模板方法使用（父类定义流程，子类实现步骤）


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

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
