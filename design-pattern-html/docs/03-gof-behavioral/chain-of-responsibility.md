---
title: Chain of Responsibility 责任链模式
description: 请求沿链传递 + HTTP 中间件 / Servlet Filter / Spring Interceptor
---

# Chain of Responsibility 责任链模式

## 核心问题

一个请求需要被多个对象处理（鉴权 → 限流 → 业务），但具体由哪个对象处理在运行时才能确定。

**真实场景**：
- HTTP 中间件：CORS → 鉴权 → 限流 → 业务
- Servlet Filter：字符编码 → 鉴权 → 日志
- 工作流引擎：审批链（组长 → 经理 → 总监 → CEO）
- 异常处理：每个 catch 块都是责任链

## 核心思想

把请求的发送者和接收者解耦。让多个对象都有机会处理请求，把这些对象连成一条链，沿链传递请求直到有对象处理它。

**关键点**：
- 每个处理者持有「下一个处理者」的引用
- 请求沿链传递，可在任意节点被处理或终止
- 处理顺序可在运行时配置

## Go HTTP 中间件

```go
package middleware

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
            return  // 中断后续处理
        }
        next(ctx)
    }
}

// 限流中间件
func RateLimit(next Handler) Handler {
    return func(ctx *Context) {
        if !limiter.Allow(ctx.ClientIP()) {
            ctx.Abort(429)
            return
        }
        next(ctx)
    }
}

// 链式组装
func Chain(handler Handler, mws ...Middleware) Handler {
    // 倒序包裹：先执行的最外层
    for i := len(mws) - 1; i >= 0; i-- {
        handler = mws[i](handler)
    }
    return handler
}

// 用法
handler := func(ctx *Context) {
    ctx.JSON(200, map[string]string{"hello": "world"})
}

handler = Chain(handler, Logging, Auth, RateLimit)
// 执行顺序：Logging -> Auth -> RateLimit -> business -> RateLimit -> Auth -> Logging
```

## TypeScript: Express middleware

```typescript
import express, { Request, Response, NextFunction } from 'express';

const app = express();

// 中间件 1：CORS
app.use((req: Request, res: Response, next: NextFunction) => {
    res.header('Access-Control-Allow-Origin', '*');
    next();  // 传给下一个
});

// 中间件 2：JSON 解析
app.use(express.json());

// 中间件 3：日志
app.use((req, res, next) => {
    console.log(`${req.method} ${req.path} at ${new Date().toISOString()}`);
    next();
});

// 中间件 4：鉴权（可以终止）
app.use('/api', (req, res, next) => {
    if (!req.headers.authorization) {
        return res.status(401).send('Unauthorized');  // 不调 next()，链终止
    }
    next();
});

// 业务路由
app.get('/api/users', (req, res) => {
    res.json([{ id: 1, name: 'Alice' }]);
});
```

Express 的中间件就是责任链，`next()` 是传递，`return res.send()` 是终止。

## Java Servlet Filter

```java
@WebFilter("/api/*")
public class AuthFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse resp, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest httpReq = (HttpServletRequest) req;
        String token = httpReq.getHeader("Authorization");

        if (token == null || !validate(token)) {
            ((HttpServletResponse) resp).sendError(401);
            return;  // 不调 chain.doFilter()，链终止
        }

        chain.doFilter(req, resp);  // 传给下一个 filter
    }
}

// web.xml 配置多个 filter 形成链
// <filter-mapping> 按声明顺序执行
```

## Spring Interceptor

```java
public class LoggingInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse resp, Object handler) {
        log.info("preHandle: {}", req.getRequestURI());
        return true;  // true=继续，false=终止
    }

    @Override
    public void postHandle(HttpServletRequest req, HttpServletResponse resp, Object handler, ModelAndView mv) {
        log.info("postHandle: {}", req.getRequestURI());
    }
}

// 注册
@Configuration
public class WebConfig implements WebMvcConfigurer {
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new LoggingInterceptor())
                .addPathPatterns("/api/**")
                .order(1);  // 顺序
    }
}
```

## 与 Decorator 区别

| | Chain of Responsibility | Decorator |
|---|---|---|
| 链长度 | 可变（中途可终止） | 固定（每个都执行）|
| 处理方 | 链上某一节点处理 | 所有装饰器叠加 |
| 适用 | 鉴权 / 限流 / 校验 | 流式处理 / 缓存 / 日志 |
| 终止性 | 处理后可不调 next | 必须完成 |

## 与 Pipeline 模式的关系

责任链与 Pipeline 几乎一样，区别：
- Pipeline 通常是同步数据流（一个阶段的输出是下一个的输入）
- 责任链是请求处理（每个节点可独立决定是否处理 / 终止）

## 适用边界

✅ **使用场景**：
- HTTP 请求处理链
- 工作流审批
- 异常处理链
- 多层校验（数据校验 → 业务规则校验 → 安全校验）

❌ **避免场景**：
- 链过长（> 10 层，debug 困难）
- 处理顺序有强依赖（明确文档）
- 单个处理者承担太多职责（拆成多个）

🔄 **演进路径**：
- 简单 if-else → 责任链（多个对象处理同一请求）
- 责任链 → Pipeline（数据流）
- 责任链 + 装饰器 = 完整拦截机制（Spring AOP）

💡 **最佳实践**：
- 链节点独立可测试（每个 filter / middleware 单独测）
- 显式终止（不调 next 或 return 响应）
- 中间件顺序明确文档化
- Go 用 `next(ctx)` 命名，TypeScript 用 `next()`
