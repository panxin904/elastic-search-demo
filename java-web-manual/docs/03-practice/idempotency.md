---
title: 接口幂等
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
