---
title: 单元测试
date: 2026-08-15  # date-auto-injected
---

# 单元测试

单元测试验证代码的最小单元（方法/类）是否正确，是保证代码质量和重构信心的基础。

## 测试框架

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>
```

核心组件：JUnit 5 + Mockito + AssertJ + SpringBootTest

## 测试编写

### Service 层测试

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserMapper userMapper;

    @InjectMocks
    private UserServiceImpl userService;

    @Test
    void createUser_shouldReturnUser_whenValidInput() {
        // Given — 准备数据
        UserCreateDTO dto = new UserCreateDTO("zhangsan", "13800138000");
        when(userMapper.insert(any())).thenReturn(1);

        // When — 执行
        UserVO result = userService.createUser(dto);

        // Then — 断言
        assertThat(result).isNotNull();
        assertThat(result.getUsername()).isEqualTo("zhangsan");
        verify(userMapper, times(1)).insert(any());
    }

    @Test
    void createUser_shouldThrowException_whenUsernameExists() {
        UserCreateDTO dto = new UserCreateDTO("existing", "13800138000");
        when(userMapper.selectByUsername("existing"))
            .thenReturn(new User());

        assertThrows(BusinessException.class,
            () -> userService.createUser(dto));
    }
}
```

### Controller 层测试

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void createUser_shouldReturn200() throws Exception {
        UserCreateDTO dto = new UserCreateDTO("test", "13800138000");
        when(userService.createUser(any())).thenReturn(new UserVO());

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(dto)))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.code").value(0));
    }
}
```

## 测试原则

| 原则 | 说明 |
|---|---|
| FIRST | Fast/Independent/Repeatable/Self-Validating/Timely |
| 一个测试只测一个场景 | 方法名清晰描述测试场景 |
| Given-When-Then | 固定三段式结构 |
| 不依赖外部环境 | Mock 掉数据库、Redis、MQ |
| 覆盖边界条件 | 正常值、null、空集合、超长值 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="unit-test" :height="400" />
