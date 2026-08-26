---
title: Saga 分布式事务
description: 跨服务事务编排 + Orchestration vs Choreography + Temporal / Camunda
---

# Saga 分布式事务

## 核心问题

分布式系统中，多个服务需要协同完成一个业务事务（如：下单 + 扣款 + 扣库存 + 发货），但无法用传统的 ACID 本地事务。

**矛盾**：
- 业务要求原子性（全成功或全失败）
- 分布式没有全局事务（CAP 定理）
- 2PC / 3PC 太重（性能差、不可用）

## 核心思想

把分布式长事务拆成多个**本地事务 + 补偿操作**，实现最终一致性。

**两种 Saga**：

| 类型 | 实现 | 适用 |
|---|---|---|
| **Orchestration（编排）** | 中央协调器逐步调用 | 流程清晰 / 适合复杂业务 |
| **Choreography（编排）** | 各服务通过事件相互触发 | 简单流程 / 服务解耦 |

## Orchestration Saga 实战

```typescript
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
```

## Choreography Saga 实战

```typescript
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
```

## 实战工具

## Temporal（最流行的 Saga 框架）

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

Camunda 用 BPMN 图定义 Saga 流程，业务分析师可以直接修改。

## 适用边界

✅ **使用场景**：
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
- 优先 Orchestration（更易调试）


<!-- auto-enrich:do-not-edit -->

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
