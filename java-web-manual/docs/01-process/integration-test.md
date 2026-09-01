---
title: 集成测试
date: 2026-08-15  # date-auto-injected
---

# 集成测试

集成测试验证多个模块之间的协作是否正常，包括数据库、缓存、消息队列等中间件的真实交互。

## 集成测试 vs 单元测试

| | 单元测试 | 集成测试 |
|---|---|---|
| 范围 | 单个方法/类 | 多个模块协作 |
| 外部依赖 | 全部 Mock | 使用真实/内存中间件 |
| 速度 | 毫秒级 | 秒级 |
| 目的 | 逻辑正确性 | 交互正确性 |

## Spring Boot 集成测试

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc
@Transactional  // 测试结束自动回滚
class OrderIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void createOrder_shouldPersistToDatabase() {
        // 发起真实 HTTP 请求
        ResponseEntity<Result> response = restTemplate.postForEntity(
            "/api/orders", orderDTO, Result.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody().getCode()).isEqualTo(0);

        // 验证数据库
        Order order = orderMapper.selectById(
            response.getBody().getData().getOrderId());
        assertThat(order).isNotNull();
    }
}
```

## 集成测试要点

| 要点 | 实践 |
|---|---|
| 使用 H2 内存库 | 测试环境用 H2 替代 MySQL，快速且隔离 |
| 数据隔离 | 每个测试独立数据，用 @Sql 初始化 / @Transactional 回滚 |
| 关键链路必测 | 核心业务流程的端到端测试不能少 |
| CI 自动执行 | 集成到 CI 流水线，每次提交自动跑 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="integration-test" :height="400" />
