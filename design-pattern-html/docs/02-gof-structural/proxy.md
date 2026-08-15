---
title: Proxy 代理模式
description: 控制对象访问 + 远程代理 / 虚拟代理 / 保护代理 / 智能引用 / 缓存代理 + Spring AOP
---

# Proxy 代理模式

## 核心问题

需要控制对某个对象的访问（访问前 / 访问时 / 访问后插入逻辑），但又不能或不方便修改对象本身的代码。

**真实场景**：
- 远程访问：RPC 客户端 stub（gRPC / Dubbo / Thrift）
- 延迟加载：浏览器图片懒加载 / Hibernate 实体代理
- 权限控制：Spring Security 鉴权代理
- 缓存：MyBatis 二级缓存 / Caffeine 缓存代理
- 事务：Spring `@Transactional` 用代理织入事务

## 核心思想

代理对象与真实对象实现**相同接口**，客户端通过代理访问真实对象，代理在调用真实对象前后可以插入额外逻辑。

**5 种代理**：
| 类型 | 用途 | 案例 |
|---|---|---|
| 远程代理 | 隐藏对象在远程地址 | RPC stub |
| 虚拟代理 | 延迟加载大对象 | 浏览器图片懒加载 |
| 保护代理 | 控制访问权限 | Spring Security |
| 智能引用 | 附加额外行为（计数 / 锁） | 缓存代理 |
| 缓存代理 | 缓存昂贵结果 | MyBatis 二级缓存 |

## 实战：Spring AOP 代理

Spring AOP 是动态代理的典范：

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
```

## 实战：gRPC 远程代理

gRPC 客户端 stub 是远程代理：

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

客户端完全感知不到「远程」——这就是远程代理的核心价值。

## 实战：保护代理（鉴权）

```typescript
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
```

## 实战：缓存代理

```typescript
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
```

## 与 Decorator 区别

| | Proxy | Decorator |
|---|---|---|
| 目的 | 控制访问（鉴权 / 缓存 / 远程）| 增加职责 |
| 创建方 | 通常由框架/容器创建 | 客户端主动包裹 |
| 关注点 | 不改变行为 | 行为增强 |
| 数量 | 通常一层（除非链式代理）| 多层叠加 |

代理侧重「替身」，装饰侧重「增强」。

## 适用边界

✅ **使用场景**：
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
- 代理本身应该是无业务逻辑的（薄包装）
