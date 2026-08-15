---
title: 策略模式
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

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="strategy-pattern" :height="400" />
