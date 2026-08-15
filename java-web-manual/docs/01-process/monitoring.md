---
title: 监控运维
---

# 监控运维

系统上线后需要持续监控，及时发现和处理问题。

## 监控四层

```
┌─────────────────────────────────┐
│        业务监控                  │ 订单量、支付成功率、注册转化率
├─────────────────────────────────┤
│        应用监控                  │ QPS、RT、错误率、JVM（堆/GC/线程）
├─────────────────────────────────┤
│        中间件监控                │ MySQL慢查询、Redis命中率、MQ积压
├─────────────────────────────────┤
│        基础设施监控              │ CPU、内存、磁盘、网络
└─────────────────────────────────┘
```

## Spring Boot Actuator

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  metrics:
    export:
      prometheus:
        enabled: true
```

关键端点：
- `/actuator/health` — 健康检查
- `/actuator/metrics` — 指标数据
- `/actuator/env` — 环境信息
- `/actuator/loggers` — 动态修改日志级别

## 告警配置

| 告警项 | 阈值 | 处理 |
|---|---|---|
| 接口错误率 > 1% | 持续 5 分钟 | 立即排查 |
| 接口 RT > 2s | 持续 3 分钟 | 检查慢 SQL / 下游超时 |
| JVM 堆使用率 > 85% | 持续 5 分钟 | 检查内存泄漏 |
| 磁盘使用率 > 85% | 即时 | 清理日志 / 扩容 |

## 日志与链路追踪

```java
// 使用 traceId 串联整个请求链路
@Slf4j
@RestController
public class OrderController {
    @PostMapping("/api/orders")
    public Result create(@RequestBody OrderDTO dto) {
        log.info("创建订单开始, userId={}, productId={}",
            dto.getUserId(), dto.getProductId());
        // traceId 自动注入到日志中
        return Result.success(orderService.create(dto));
    }
}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="monitoring" :height="400" />
