---
title: State 状态模式
description: 行为随状态变化 + 订单状态机 / TCP 连接状态 / Spring StateMachine
---

# State 状态模式

## 核心问题

对象的行为随着其**内部状态**的改变而改变，看起来好像修改了它的类。

**真实场景**：
- 订单状态机：待支付 → 已支付 → 已发货 → 已完成 / 已取消
- TCP 连接：CLOSED → LISTEN → SYN_SENT → ESTABLISHED → ...
- 电梯状态：停止 / 运行 / 维修 / 故障
- 文档状态：草稿 / 审核中 / 已发布 / 已归档
- 工作流引擎节点状态

## 核心思想

将「状态」封装成独立的类，把「状态相关的行为」从原对象移到状态类中。对象（Context）持有当前状态对象引用，把行为委托给状态对象。

**关键角色**：
- **Context**：持有当前状态，处理客户端请求
- **State**：状态接口（每个状态对应一个行为）
- **ConcreteState**：具体状态实现

## Java 实战：订单状态机

```java
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
```

## TypeScript：TCP 简化版

```typescript
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
```

## 实战：Spring StateMachine

Spring 有官方的 StateMachine 框架：

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
```

## 与 Strategy 区别

| | State | Strategy |
|---|---|---|
| 状态转换 | 状态间互相切换 | 互相独立，客户端选择 |
| 数量 | 通常有限状态机 | 多个等价的算法 |
| 触发 | 内部事件驱动 | 客户端主动选择 |
| 封装性 | 通常是 Context 内部的状态 | 通常是注入到 Context 的策略 |

## 适用边界

✅ **使用场景**：
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
- 持久化状态（重启可恢复）
