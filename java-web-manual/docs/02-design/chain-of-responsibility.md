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

## 🛠️ 何时用责任链

**使用场景**：请求需要**多个处理者**依次处理（每个处理者可决定是否处理 + 传给下一个）。

**典型应用**：
- Servlet Filter / Spring Interceptor
- Netty ChannelPipeline
- Spring Security Filter Chain
- 日志 / 鉴权 / 限流 / 监控 多层串联

**与装饰器模式区别**：责任链**单向传递**（每个处理者可中断），装饰器**层层包裹**
（外层调用内层）。

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="chain-of-responsibility" :height="400" />


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
