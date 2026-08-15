---
title: 依赖注入
---

# 依赖注入（IoC/DI）

Spring 通过 IoC 容器管理对象的创建和依赖关系，开发者只需声明需要什么。

## 三种注入方式

```java
// 1. 字段注入（不推荐，难以测试）
@Autowired
private UserService userService;

// 2. Setter 注入
private UserService userService;
@Autowired
public void setUserService(UserService userService) {
    this.userService = userService;
}

// 3. 构造器注入（推荐！）
private final UserService userService;
public UserController(UserService userService) {
    this.userService = userService;
}

// Lombok 简化
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;
}
```

## Bean 生命周期

```
实例化 → 属性赋值 → Aware接口回调 → @PostConstruct
→ InitializingBean → 自定义init → Bean就绪
→ @PreDestroy → DisposableBean → 自定义destroy
```

## @Autowired vs @Resource

| | @Autowired | @Resource |
|---|---|---|
| 来源 | Spring | JDK (JSR-250) |
| 默认装配 | byType | byName |
| 指定方式 | @Qualifier | name 属性 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="dependency-injection" :height="400" />
