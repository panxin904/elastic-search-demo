---
title: Mediator 中介者模式
description: 集中对象间交互 + 聊天室 / GUI 组件协作 / MediatR / NestJS EventBus
---

# Mediator 中介者模式

## 核心问题

多个对象之间相互依赖，形成「网状」通信。如果新加一个对象，需要知道所有其他对象的接口，扩展困难。

**举例**：
- GUI 对话框：5 个组件（按钮 / 文本框 / 下拉框 / 复选框 / 列表）互相联动（按钮启用取决于文本框非空，复选框切换禁用下拉框...）
- 聊天室：N 个用户两两通信，N² 个关系
- 航空管制：N 架飞机由一个塔台协调

## 核心思想

用一个中介对象来封装一系列对象的交互。中介者使各对象不需要显式相互引用，从而使其耦合松散，而且可以独立地改变它们之间的交互。

**关键点**：
- 各同事（Colleague）只与中介者通信
- 中介者知道所有同事的接口
- 中介者承担协调逻辑（复杂的同事间关系）

## TypeScript：聊天室

```typescript
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

各 User 只依赖 Mediator 接口，不需要知道其他 User 的存在。

## 实战：GUI 组件

```java
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

不引入中介者的话：TextField 需要知道 Button 和 Checkbox 的存在，组件间形成网状依赖。

## 实战：MediatR (C# / .NET)

MediatR 是 Mediator 模式在 .NET 的事实标准：

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

Controller 不直接依赖 Handler，所有请求通过 `_mediator.Send()` 分发，天然解耦。

## NestJS EventBus

```typescript
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

OrderService 不直接调 NotificationService，通过 EventBus 解耦。

## 适用边界

✅ **使用场景**：
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
- 警惕中介者膨胀（必要时拆为多个）


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
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
