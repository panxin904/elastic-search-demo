---
title: Command 命令模式
description: 请求封装为对象 + 撤销重做 + 任务队列 + CQRS / Saga 命令模式
---

# Command 命令模式

## 核心问题

需要把请求封装为对象，从而支持：
1. 撤销（Undo）
2. 队列化（任务队列）
3. 日志记录（事务）
4. 参数化其他对象（不同请求做参数）
5. 多线程 / 异步执行

## 核心思想

把「请求」的所有信息（URL / 参数 / 执行者）封装成一个**对象**。命令对象持有「接收者」的引用，调用 `execute()` 时让接收者执行动作。

**关键角色**：
- **Command**：抽象命令接口（`execute()` / `undo()`）
- **ConcreteCommand**：具体命令（持有 Receiver）
- **Receiver**：真正执行动作的对象
- **Invoker**：调用命令的对象（按钮 / 任务队列）

## Java 实现

```java
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
```

## TypeScript：任务队列

```typescript
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
```

## 实战：CQRS 命令

CQRS 是 Command 模式的架构升级版：

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

Axon Framework（Java 生态）就基于这种设计。

## 适用边界

✅ **使用场景**：
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
- 撤销栈有大小限制（避免无限增长）


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
