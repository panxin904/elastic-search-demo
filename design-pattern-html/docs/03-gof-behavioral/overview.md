---
title: 行为型模式总览
date: 2026-08-15  # date-auto-injected
---

# 行为型模式总览

> GoF 23 模式中专门解决「对象间职责分配与通信」问题的 11 个模式。行为型模式既关注类之间的算法/职责流转（Template Method / Strategy / State），也关注对象间的消息传递（Observer / Mediator / Command）和状态管理（Memento）。

## 为什么需要行为型模式

结构型模式回答「**用什么**」和行为型模式回答「**怎么做**」。当业务复杂度提升后，最难的不是对象怎么组合，而是：

1. **算法族切换**：支付有支付宝/微信/PayPal，怎么避免一堆 if-else？→ Strategy
2. **请求处理链**：HTTP 中间件、责任链、Pipeline 怎么组织？→ Chain of Responsibility
3. **状态机**：订单从「待支付→已支付→已发货→已完成」怎么表达？→ State
4. **事件订阅**：Kafka / RabbitMQ 主题订阅模式对应什么 OO 抽象？→ Observer

## 11 种行为型模式速览

| 模式 | 核心问题 | 典型场景 |
|---|---|---|
| **Chain of Responsibility 责任链** | 多个对象依次尝试处理请求 | Servlet Filter / Spring Interceptor / Express middleware |
| **Command 命令** | 把请求封装为对象（可撤销/队列）| 任务队列 / 撤销重做 / 数据库事务 |
| **Iterator 迭代器** | 顺序访问聚合对象元素 | Java Collection / JS for-of / Rust IntoIterator |
| **Mediator 中介者** | 集中控制对象间交互 | GUI 对话框组件协作 / 航空管制塔台 |
| **Memento 备忘录** | 保存/恢复对象内部状态 | 撤销操作 / 游戏存档 / 数据库快照 |
| **Observer 观察者** | 一对多依赖，自动通知 | 事件总线 / Vue/React 响应式 / Kafka consumer |
| **State 状态** | 行为随状态变化 | TCP 连接状态机 / 订单状态机 / 工作流引擎 |
| **Strategy 策略** | 算法族互相替换 | 支付方式 / 排序算法 / 压缩算法 |
| **Template Method 模板方法** | 算法骨架不变，部分步骤延迟到子类 | Spring JdbcTemplate / Java Servlet / Go http.Handler |
| **Visitor 访问者** | 在不修改元素类的前提下增加新操作 | AST 处理 / 编译器 / 文件树遍历 |
| **Interpreter 解释器** | 实现自定义语言/表达式求值 | SQL 解析器 / 正则表达式 / 数学表达式 |

## Chain of Responsibility 责任链模式

### 核心思想

把请求的发送者和接收者解耦，让多个对象都有机会处理请求。把这些对象连成一条链，沿链传递请求直到有对象处理为止。

### 实战：HTTP 中间件

```go
// Go: 中间件链
type Handler func(ctx *Context)

type Middleware func(Handler) Handler

func Chain(h Handler, mws ...Middleware) Handler {
    for i := len(mws) - 1; i >= 0; i-- {
        h = mws[i](h)
    }
    return h
}

// 用法
auth := func(next Handler) Handler {
    return func(ctx *Context) {
        if !ctx.IsAuthenticated() {
            ctx.Abort(401)
            return
        }
        next(ctx)
    }
}

logging := func(next Handler) Handler {
    return func(ctx *Context) {
        log.Printf("%s %s", ctx.Method, ctx.Path)
        next(ctx)
    }
}

h := Chain(handler, logging, auth, rateLimit)
```

### 实战：Servlet Filter / Express middleware

```typescript
// Express 中间件链
app.use(corsMiddleware);          // 1. CORS
app.use(express.json());         // 2. 解析 body
app.use(authMiddleware);         // 3. 鉴权
app.use('/api/users', userRouter); // 4. 路由
```

### 与 Decorator 的区别

| | Chain of Responsibility | Decorator |
|---|---|---|
| 链长度 | 可变（中途可以停止） | 固定（每个都执行） |
| 处理方 | 链上某一节点处理 | 所有装饰器叠加 |
| 适用 | 鉴权 / 限流 / 校验 | 流式处理 / 缓存 / 日志 |

## Command 命令模式

### 核心思想

把请求封装为对象，从而允许用不同的请求、队列、日志来参数化其他对象。也支持可撤销操作。

### 实战：任务队列

```typescript
interface Command {
    execute(): void;
    undo(): void;
}

class AddItemCommand implements Command {
    constructor(private cart: Cart, private item: Item) {}
    execute() { this.cart.add(this.item); }
    undo() { this.cart.remove(this.item); }
}

class CommandQueue {
    private history: Command[] = [];

    execute(cmd: Command) {
        cmd.execute();
        this.history.push(cmd);
    }

    undoLast() {
        const cmd = this.history.pop();
        cmd?.undo();
    }
}
```

### 实战：数据库事务

Command 模式天然契合事务模型：

```sql
-- 每个 SQL 都是一个 Command，事务统一 commit/rollback
BEGIN;
INSERT INTO orders ...;
UPDATE inventory ...;
COMMIT;  -- 或 ROLLBACK;
```

## Iterator 迭代器模式

### 核心思想

提供一种方法顺序访问聚合对象中的各个元素，而不暴露其内部表示。

### Java / Go / TS 对比

```java
// Java: 显式 Iterator 接口
List<String> list = Arrays.asList("a", "b", "c");
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    System.out.println(it.next());
}

// Java 8+: forEach + lambda
list.forEach(System.out::println);
```

```go
// Go: range 关键字
for i, v := range []string{"a", "b", "c"} {
    fmt.Println(i, v)
}

// 自定义迭代器（Go 1.23+ range over func）
func (c *Counter) Yield() func() (int, bool) {
    i := 0
    return func() (int, bool) {
        if i < c.max { i++; return i, true }
        return 0, false
    }
}
```

```typescript
// TypeScript: Iterable / Iterator 协议
class Range implements Iterable<number> {
    constructor(private from: number, private to: number) {}
    *[Symbol.iterator]() {
        for (let i = this.from; i <= this.to; i++) yield i;
    }
}

for (const n of new Range(1, 5)) {
    console.log(n);  // 1,2,3,4,5
}
```

## Mediator 中介者模式

### 核心思想

用一个中介对象来封装一系列对象的交互。中介者使各对象不需要显式相互引用，从而使其耦合松散。

### 实战：聊天室

```typescript
class ChatRoom implements Mediator {
    private users: User[] = [];
    register(user: User) {
        this.users.push(user);
        user.setMediator(this);
    }
    send(message: string, from: User, to?: User) {
        if (to) {
            to.receive(message, from);
        } else {
            this.users.forEach(u => {
                if (u !== from) u.receive(message, from);
            });
        }
    }
}

class User {
    constructor(private name: string, private mediator?: Mediator) {}
    send(msg: string, to?: User) { this.mediator?.send(msg, this, to); }
    receive(msg: string, from: User) { console.log(`${this.name} <- ${from.name}: ${msg}`); }
}
```

## Memento 备忘录模式

### 核心思想

在不破坏封装性的前提下，捕获对象的内部状态，并在该对象之外保存这个状态，以便以后恢复。

### 实战：撤销操作

```typescript
class EditorMemento {
    constructor(public readonly content: string) {}
}

class Editor {
    private content = '';
    type(text: string) { this.content += text; }
    save(): EditorMemento { return new EditorMemento(this.content); }
    restore(m: EditorMemento) { this.content = m.content; }
    getContent() { return this.content; }
}

class History {
    private stack: EditorMemento[] = [];
    push(m: EditorMemento) { this.stack.push(m); }
    pop() { return this.stack.pop(); }
}

const editor = new Editor();
const history = new History();

editor.type('Hello');
history.push(editor.save());
editor.type(' World');
console.log(editor.getContent());  // "Hello World"

editor.restore(history.pop()!);
console.log(editor.getContent());  // "Hello"
```

## Observer 观察者模式

### 核心思想

定义对象间的一种一对多依赖关系，当一个对象状态改变时，所有依赖它的对象都得到通知并自动更新。

### 实战：Vue 响应式

```typescript
// Vue 3 响应式就是 Observer 模式
import { ref, watchEffect } from 'vue';

const count = ref(0);

// count 被读取时收集依赖（订阅）
// count 被赋值时通知所有订阅者（通知）
watchEffect(() => {
    console.log(`count = ${count.value}`);
});

count.value++;  // 触发 watchEffect
```

### 实战：Kafka Consumer

Kafka topic 的所有 consumer 都是 observer，自动接收 producer 发布的消息。

## State 状态模式

### 核心思想

允许对象在内部状态改变时改变它的行为，对象看起来好像修改了它的类。

### 实战：订单状态机

```java
interface OrderState {
    OrderState pay(Order order);
    OrderState ship(Order order);
    OrderState complete(Order order);
    OrderState cancel(Order order);
}

class PendingState implements OrderState {
    @Override public OrderState pay(Order o) {
        o.setState(new PaidState());
        o.notify("支付成功");
        return o.getState();
    }
    @Override public OrderState ship(Order o) {
        throw new IllegalStateException("未支付不能发货");
    }
}

class PaidState implements OrderState {
    @Override public OrderState ship(Order o) {
        o.setState(new ShippedState());
        return o.getState();
    }
    @Override public OrderState cancel(Order o) {
        // 退款逻辑
        o.setState(new CancelledState());
        return o.getState();
    }
}
```

### 与 Strategy 的区别

| | State | Strategy |
|---|---|---|
| 状态转换 | 状态间互相切换 | 互相独立，客户端选择 |
| 数量 | 通常有限状态机 | 多个等价的算法 |
| 触发 | 内部事件驱动 | 客户端主动选择 |

## Strategy 策略模式

### 核心思想

定义一系列算法，把它们一个个封装起来，并且使它们可以互相替换。

### 实战：支付方式

```typescript
interface PaymentStrategy {
    pay(amount: number): Promise<PaymentResult>;
}

class AlipayStrategy implements PaymentStrategy {
    async pay(amount: number) { /* 调用支付宝 SDK */ }
}

class WechatPayStrategy implements PaymentStrategy {
    async pay(amount: number) { /* 调用微信支付 SDK */ }
}

class PaymentContext {
    constructor(private strategy: PaymentStrategy) {}
    setStrategy(s: PaymentStrategy) { this.strategy = s; }
    async execute(amount: number) { return this.strategy.pay(amount); }
}

// 客户端
const ctx = new PaymentContext(new AlipayStrategy());
await ctx.execute(100);
ctx.setStrategy(new WechatPayStrategy());
await ctx.execute(200);
```

### 与 if-else 的对比

```typescript
// ❌ if-else 地狱
function pay(method: string, amount: number) {
    if (method === 'alipay') { /* 20 行 */ }
    else if (method === 'wechat') { /* 20 行 */ }
    else if (method === 'paypal') { /* 20 行 */ }
    // 新增支付方式必须改这里
}

// ✅ 策略模式
function pay(strategy: PaymentStrategy, amount: number) {
    return strategy.pay(amount);  // 新增策略只需新增类
}
```

## Template Method 模板方法模式

### 核心思想

定义一个算法的骨架，而将一些步骤延迟到子类。模板方法使得子类可以在不改变算法结构的情况下重新定义算法的某些步骤。

### 实战：Spring JdbcTemplate

```java
// Spring 帮你写好流程：获取连接 → 创建 statement → 设置参数 → 执行 → 映射结果 → 关闭
// 你只需要提供：SQL + 参数 + RowMapper
jdbcTemplate.query(
    "SELECT id, name, email FROM users WHERE id = ?",
    new Object[]{userId},
    (rs, rowNum) -> new User(rs.getLong("id"), rs.getString("name"), rs.getString("email"))
);
```

### 与 Strategy 的区别

| | Template Method | Strategy |
|---|---|---|
| 抽象层级 | 类继承（编译期决定） | 对象组合（运行期切换） |
| 算法骨架 | 不变（基类） | 整个算法都可换 |
| 实现 | 抽象方法 | 接口注入 |

## Visitor 访问者模式

### 核心思想

封装一些施加于某种数据结构元素之上的操作。一旦这些操作需要修改，接受这个操作的数据结构可以保持不变。

### 实战：AST 处理

```typescript
interface ExprVisitor<R> {
    visitNumber(n: NumberExpr): R;
    visitBinary(b: BinaryExpr): R;
}

interface Expr {
    accept<R>(v: ExprVisitor<R>): R;
}

class NumberExpr implements Expr {
    constructor(public value: number) {}
    accept<R>(v: ExprVisitor<R>): R { return v.visitNumber(this); }
}

class BinaryExpr implements Expr {
    constructor(public op: string, public left: Expr, public right: Expr) {}
    accept<R>(v: ExprVisitor<R>): R { return v.visitBinary(this); }
}

// 不同的 visitor：求值 / 打印 / 类型检查
class Evaluator implements ExprVisitor<number> {
    visitNumber(n: NumberExpr) { return n.value; }
    visitBinary(b: BinaryExpr) {
        const l = b.left.accept(this);
        const r = b.right.accept(this);
        return b.op === '+' ? l + r : l - r;
    }
}

class Printer implements ExprVisitor<string> {
    visitNumber(n: NumberExpr) { return n.value.toString(); }
    visitBinary(b: BinaryExpr) {
        return `(${b.left.accept(this)} ${b.op} ${b.right.accept(this)})`;
    }
}
```

### Java 经典案例

- `java.lang.model.element.Element` + `ElementVisitor`：编译器 API
- `java.nio.file.FileVisitor`：遍历文件树
- Spring `BeanDefinitionVisitor`：解析 Bean 配置

## Interpreter 解释器模式

### 核心思想

给定一个语言，定义它的文法的一种表示，并定义一个解释器，这个解释器使用该表示来解释语言中的句子。

### 实战：表达式求值

```typescript
interface Expr { interpret(): number; }
class Number implements Expr {
    constructor(public value: number) {}
    interpret() { return this.value; }
}
class Plus implements Expr {
    constructor(public left: Expr, public right: Expr) {}
    interpret() { return this.left.interpret() + this.right.interpret(); }
}

const expr = new Plus(new Number(1), new Plus(new Number(2), new Number(3)));
console.log(expr.interpret());  // 6
```

### 实战：正则表达式

正则表达式本身就是一种语言，`/^(\d+)\.(\d+)$/` 就是一个 Interpreter。

### 何时使用 / 避免

✅ **使用**：DSL / SQL 解析 / 简单表达式
❌ **避免**：复杂语法（用 ANTLR / Yacc / 表达式树库）

## 11 模式决策树

```
需要处理多个对象的协作通信？
├── 请求沿链传递，每个节点可选处理 → Chain of Responsibility
├── 一对多通知 → Observer
├── 通过第三方集中调度 → Mediator
└── 请求需要撤销/队列化 → Command

需要在多个算法/状态间切换？
├── 有限状态机 → State
├── 互相独立的算法族 → Strategy
└── 算法骨架不变，部分步骤可变 → Template Method

需要遍历复杂结构？
├── 顺序访问元素 → Iterator
└── 在不修改结构前提下增加操作 → Visitor

需要保存/恢复状态？
└── → Memento

需要解析自定义语言？
└── → Interpreter
```

## 与现代框架的关系

| 模式 | 现代对应 |
|---|---|
| Observer | EventEmitter / Vue reactivity / Kafka |
| Iterator | for-of / range / Stream |
| Command | Task Queue / Saga / CQRS |
| State | Spring StateMachine / XState |
| Chain | Express middleware / Spring Filter |
| Mediator | MediatR (C#) / NestJS EventBus |
| Memento | Redux undo / Git snapshots |
| Strategy | Spring `@Conditional` / DI |
| Template | Spring Template / Go `http.Handler` |
| Visitor | Java ElementVisitor / AST traversal |
| Interpreter | ANTLR / RegExp / SQL parser |

## 实战建议

1. **State 替代 if-else**：订单状态机写成 switch-case 后期会爆炸
2. **Strategy 替代条件分支**：支付 / 排序 / 压缩都该用策略
3. **Observer 是事件驱动的基础**：理解 Observer 才能理解 Kafka / Vue
4. **Chain 包装流水线**：每个 HTTP 请求都过 5-10 个 middleware
5. **Visitor 慎用**：双分派在 TS / Go 里写起来繁琐，多用 pattern matching 替代
6. **Interpreter 不要手写**：直接用 ANTLR / Parser combinator 库

## 下一步

- 阅读每篇单独的 GoF 11 行为型模式细节：[Chain of Responsibility](./chain-of-responsibility) / [Command](./command) / [Iterator](./iterator) / [Mediator](./mediator) / [Memento](./memento) / [Observer](./observer) / [State](./state) / [Strategy](./strategy) / [Template Method](./template-method) / [Visitor](./visitor) / [Interpreter](./interpreter)
- 进阶：[架构模式 · CQRS](../05-architectural-patterns/cqrs)（Command 的架构升级版）
- 反向自查：[反模式 · 回调地狱](../06-anti-patterns/callback-hell)（Observer / Callback 滥用）

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
