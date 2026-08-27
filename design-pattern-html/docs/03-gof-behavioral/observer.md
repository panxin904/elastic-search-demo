---
title: Observer 观察者模式
description: 一对多依赖 + 事件总线 + Vue 响应式 / Kafka consumer / Node EventEmitter / Spring Event
---

# Observer 观察者模式

## 核心问题

一个对象的状态改变需要自动通知其他多个对象，且这些对象在编译期不知道具体是谁（运行时绑定）。

**真实场景**：
- GUI 按钮点击 → 更新多个 UI
- 微博关注：博主发文 → 所有粉丝收到通知
- Kafka topic：producer 发消息 → 所有 consumer 收到
- Vue 响应式：data 变化 → 自动更新所有依赖它的视图

## 核心思想

定义对象间的一种一对多依赖关系，当一个对象（Subject）状态改变时，所有依赖它的对象（Observer）都得到通知并自动更新。

**关键点**：
- Subject 持有 Observer 列表
- Subject 提供 `subscribe()` / `unsubscribe()` / `notify()` 接口
- Observer 实现 `update()` 接口
- 通知可以是同步或异步

## TypeScript：事件总线

```typescript
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
```

## Vue 3 响应式原理

Vue 3 的响应式系统就是 Observer 模式：

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
```

## 实战：Kafka Consumer

Kafka topic 是 Observer 模式在分布式系统的实现：

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

OrderService 不直接依赖 NotificationService / AnalyticsService。

## 适用边界

✅ **使用场景**：
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
- 大量订阅考虑 Pub/Sub 中间件


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

<!-- svg-injected:do-not-edit -->

![observer pattern](/observer-pattern.svg)
