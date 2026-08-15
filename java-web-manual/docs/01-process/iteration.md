---
title: 迭代优化
---

# 迭代优化

系统上线不是终点，根据监控数据和用户反馈持续优化。

## 优化来源

| 来源 | 示例 |
|---|---|
| 监控数据 | 接口 RT 持续上升 → 优化慢 SQL |
| 用户反馈 | 页面加载慢 → 加缓存、CDN |
| 代码评审 | 代码耦合严重 → 重构拆分 |
| 技术调研 | 新技术更高效 → 评估替换 |
| 线上事故 | 复盘根因 → 加强防护 |

## 常见优化方向

### 性能优化
```
慢 SQL → 加索引 / 优化 SQL / 读写分离
接口慢 → 加缓存 / 异步化 / 并行调用
JVM 频繁 GC → 调大堆内存 / 优化对象创建
```

### 架构优化
```
单体 → 微服务拆分
同步 → 异步消息解耦
单点 → 集群 + 负载均衡
单库 → 分库分表
```

### 代码优化
```java
// ❌ Before: 多重 if-else
if ("WECHAT".equals(type)) { payByWechat(); }
else if ("ALIPAY".equals(type)) { payByAlipay(); }
else if ("BANK".equals(type)) { payByBank(); }

// ✅ After: 策略模式
@Autowired
private Map<String, PayStrategy> payStrategyMap;

public void pay(String type, Order order) {
    PayStrategy strategy = payStrategyMap.get(type);
    if (strategy == null) throw new BusinessException("不支持");
    strategy.pay(order);
}
```

## 技术债务管理

| 债务类型 | 处理策略 |
|---|---|
| 架构债务（单体→微服务） | 按模块逐步拆分，列入季度规划 |
| 代码债务（烂代码） | 童子军原则：每次提交比之前干净一点 |
| 依赖债务（过时版本） | 定期升级，关注安全漏洞 |
| 测试债务（覆盖率低） | 新代码必须写测试，老代码逐步补 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="iteration" :height="400" />
