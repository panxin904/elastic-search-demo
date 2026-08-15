---
title: 测试框架
---

# 测试框架

Java 测试的核心组合：JUnit 5 + Mockito + SpringBootTest。

## JUnit 5

```java
@SpringBootTest  // 加载完整 Spring 上下文
class OrderServiceTest {

    @Autowired
    private OrderService orderService;

    @MockBean  // Mock Spring Bean
    private ProductMapper productMapper;

    @Test
    @DisplayName("创建订单成功")
    void createOrder_success() {
        // Given
        OrderCreateDTO dto = new OrderCreateDTO(1L, 2);
        when(productMapper.selectById(1L))
            .thenReturn(new Product(1L, "商品", 100));

        // When
        OrderVO result = orderService.create(dto);

        // Then
        assertNotNull(result);
        assertEquals(200, result.getTotalAmount());
    }

    @ParameterizedTest
    @ValueSource(ints = {0, -1, 101})
    @DisplayName("数量非法时抛异常")
    void createOrder_invalidQuantity(int quantity) {
        assertThrows(BusinessException.class, () -> {
            orderService.create(new OrderCreateDTO(1L, quantity));
        });
    }
}
```

## Mockito

```java
// Mock 返回值
when(userMapper.selectById(1L)).thenReturn(mockUser);

// Mock 抛异常
when(userMapper.insert(any())).thenThrow(new RuntimeException());

// 验证调用次数
verify(userMapper, times(1)).insert(any());
verify(userMapper, never()).deleteById(any());

// 参数匹配
verify(userMapper).updateById(argThat(user -> "zhangsan".equals(user.getUsername())));
```

## H2 内存数据库

```yaml
# application-test.yml
spring:
  datasource:
    url: jdbc:h2:mem:testdb;MODE=MySQL
    driver-class-name: org.h2.Driver
  sql:
    init:
      mode: always
      schema-locations: classpath:schema.sql
```

```java
@Test
@Sql(scripts = "/data/test-orders.sql")  // 初始化测试数据
void listOrders_shouldReturnPaginatedResults() { ... }
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="testing" :height="400" />
