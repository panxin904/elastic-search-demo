---
title: 策略模式
date: 2026-08-15  # date-auto-injected
---

# 策略模式

定义一组算法，分别封装，使其可以互相替换。

## Java Web 中的应用

- **多种支付方式**：微信支付、支付宝、银行卡
- **多种通知渠道**：短信、邮件、App推送
- **多种计费规则**：普通用户、VIP、企业

## 代码示例

```java
// 策略接口
public interface PayStrategy {
    void pay(Order order);
}

@Component("WECHAT")
public class WechatPay implements PayStrategy {
    public void pay(Order order) { /* 微信支付 */ }
}

// 工厂自动注入
@Service
public class PayService {
    @Autowired
    private Map<String, PayStrategy> strategyMap;

    public void pay(Order order, String type) {
        PayStrategy strategy = strategyMap.get(type);
        strategy.pay(order);  // 替代 if-else
    }
}
```

## 🛠️ 何时用策略模式

**使用场景**：多种算法可以**互换**，且算法选择**在运行时决定**（如支付方式
选择、排序算法选择、压缩算法选择）。

**优势**：消除 if-else 链，新增算法只需新增 Strategy 实现类（OCP）。

**Spring 替代**：用 `Map<String, Strategy>` + `@Component` 自动注入多种实现，
比手写 if-else 优雅。

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="strategy-pattern" :height="400" />


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
