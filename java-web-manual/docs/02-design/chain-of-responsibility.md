---
title: 责任链模式
---

# 责任链模式

将请求沿着处理链传递，每个处理器决定处理或传递给下一个。

## Java Web 中的应用

- **Servlet Filter 链**：每个 Filter 决定是否放行
- **Spring Interceptor**：preHandle → Controller → postHandle → afterCompletion
- **审批流**：组长 → 经理 → 总监 逐级审批

## 代码示例

```java
// 抽象处理器
public abstract class AbstractHandler {
    protected AbstractHandler next;
    public abstract void handle(Request request);
}

// 参数校验处理器
public class ValidateHandler extends AbstractHandler {
    public void handle(Request request) {
        if (!valid(request)) throw new BusinessException("参数错误");
        if (next != null) next.handle(request);
    }
}

// Spring 自动组装责任链
@Component
public class HandlerChain {
    @Autowired
    private List<AbstractHandler> handlers;
}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="chain-of-responsibility" :height="400" />
