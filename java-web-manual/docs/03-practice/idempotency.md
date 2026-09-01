---
title: 接口幂等
date: 2026-08-15  # date-auto-injected
---

# 接口幂等

幂等：同一个操作执行一次和执行多次，结果相同。

## 为什么需要幂等

- 用户手抖点多次提交按钮
- 网络超时，客户端自动重试
- MQ 消息重复消费
- 定时任务重复执行

## 实现方案

### Token 机制

```java
// 1. 先获取 token
@GetMapping("/token")
public Result<String> getToken() {
    String token = UUID.randomUUID().toString();
    redisTemplate.opsForValue().set("idempotent:" + token, "1",
        5, TimeUnit.MINUTES);
    return Result.success(token);
}

// 2. 提交时校验 token
@PostMapping("/orders")
public Result create(@RequestHeader("Idempotent-Token") String token,
        @RequestBody OrderDTO dto) {
    Boolean deleted = redisTemplate.delete("idempotent:" + token);
    if (Boolean.FALSE.equals(deleted)) {
        return Result.error(2005, "请勿重复提交");
    }
    return Result.success(orderService.create(dto));
}
```

### 数据库唯一索引

```sql
-- 订单号唯一索引，重复插入直接失败
ALTER TABLE t_order ADD UNIQUE KEY uk_order_no (order_no);
```

### 状态机

```java
// 只有"待支付"状态才能改为"已支付"
public void payOrder(Long orderId) {
    int rows = orderMapper.updateStatus(
        orderId, "PENDING", "PAID");  // 乐观锁
    if (rows == 0) {
        throw new BusinessException("订单状态异常");
    }
}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="idempotency" :height="400" />


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
