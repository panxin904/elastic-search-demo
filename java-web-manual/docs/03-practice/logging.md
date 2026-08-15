---
title: 日志规范
---

# 日志规范

日志是排查问题的核心手段，规范的日志让问题定位效率提升 10 倍。

## 日志级别与使用场景

| 级别 | 使用场景 |
|---|---|
| ERROR | 系统错误，需要人工介入（数据库挂了、第三方不可用） |
| WARN | 潜在问题（参数异常但有兜底、降级触发、接近阈值） |
| INFO | 关键业务流程节点（请求入参、调用外部接口、重要状态变更） |
| DEBUG | 调试信息（方法入参出参、中间变量，生产环境不开） |

## 日志配置

```yaml
logging:
  level:
    root: INFO
    com.example: DEBUG              # 自己的包开 DEBUG
    com.example.mapper: INFO        # SQL 太吵，压到 INFO
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] [%X{traceId}] %-5level %logger{36} - %msg%n"
```

## 正确 vs 错误写法

```java
// ❌ 错误：吞异常不记录
try { doSomething(); } catch (Exception e) {}

// ❌ 错误：打印敏感信息
log.info("用户登录: username={}, password={}", username, password);

// ❌ 错误：使用字符串拼接
log.info("用户" + username + "创建了订单" + orderId);

// ✅ 正确：使用占位符
log.info("用户创建订单: userId={}, orderId={}, amount={}",
    userId, orderId, amount);

// ✅ 正确：异常必须记录堆栈
try { doSomething(); }
catch (Exception e) {
    log.error("处理失败: orderId={}", orderId, e);  // 第二个参数传异常对象
}
```

## 链路追踪 traceId

```java
// 拦截器中设置 traceId
@Component
public class TraceInterceptor implements HandlerInterceptor {
    @Override
    public boolean preHandle(HttpServletRequest request,
            HttpServletResponse response, Object handler) {
        String traceId = request.getHeader("X-Trace-Id");
        if (traceId == null) traceId = UUID.randomUUID().toString();
        MDC.put("traceId", traceId);
        return true;
    }

    @Override
    public void afterCompletion(...) {
        MDC.clear();  // 防止内存泄漏
    }
}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="logging" :height="400" />
