---
title: Decorator 装饰器模式
description: 动态添加职责 + Java IO 流 + Go middleware + TypeScript 装饰器 + Spring AOP
---

# Decorator 装饰器模式

## 核心问题

需要给对象动态添加职责，但又不能修改原类。继承的方案是「静态」的（编译期决定），且容易产生子类爆炸。

**真实场景**：
- Java IO 流：FileInputStream → BufferedInputStream → DataInputStream，每层都是一个装饰器
- HTTP 中间件：Logging → Auth → RateLimit，每层都是一个装饰器
- 咖啡价格：美式 + 糖 + 奶 + 巧克力，每加一份都是装饰
- React 高阶组件（HOC）：withRouter / withAuth / withTheme

## 核心思想

装饰器持有「被装饰对象」的引用，并实现与被装饰对象**相同的接口**。装饰器在调用被装饰对象的方法前后，添加额外行为。

**关键点**：
- 装饰器与被装饰者实现**相同接口**
- 装饰器持有被装饰者的引用（组合）
- 可以**多层嵌套**装饰
- 运行时决定装饰链

## Java IO 经典案例

```java
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

装饰链顺序无关（可以 GZIPInputStream(BufferedInputStream(FileInputStream))）。

## Go 中间件

Go 的 HTTP 中间件是装饰器的典范：

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

每个中间件都是装饰器，包装了下一个 handler 并添加额外逻辑。

## TypeScript 装饰器

TypeScript / ES 装饰器是语言级支持：

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
```

## 与 Proxy 区别

| | Decorator | Proxy |
|---|---|---|
| 目的 | 增加新职责 | 控制访问 |
| 创建方 | 客户端主动包裹 | 通常由框架/容器创建 |
| 关注点 | 行为增强 | 访问控制（鉴权 / 延迟加载 / 缓存）|
| 数量关系 | 多个叠加 | 通常一层 |

## 适用边界

✅ **使用场景**：
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
- Go 的 Middleware 是社区标准模式
