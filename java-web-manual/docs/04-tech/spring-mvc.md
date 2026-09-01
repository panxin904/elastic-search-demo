---
title: Spring MVC
date: 2026-08-15  # date-auto-injected
---

# Spring MVC

Spring MVC 处理 Web 层的请求分发、参数绑定、响应返回。

## 请求处理流程

```
DispatcherServlet
    → HandlerMapping (找到哪个 Controller)
    → HandlerAdapter (调用 Controller 方法)
    → Controller.method() (执行业务逻辑)
    → ViewResolver / @ResponseBody (返回结果)
    → Response
```

## 参数绑定

```java
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    // 路径参数
    @GetMapping("/{id}")
    public Result<OrderVO> getById(@PathVariable Long id) {}

    // 查询参数 ?page=1&size=20
    @GetMapping
    public Result<PageResult<OrderVO>> list(
        @RequestParam(defaultValue = "1") int page,
        @RequestParam(defaultValue = "20") int size) {}

    // 请求体 JSON
    @PostMapping
    public Result<OrderVO> create(@Valid @RequestBody OrderCreateDTO dto) {}

    // 请求头
    @GetMapping("/profile")
    public Result<UserVO> profile(@RequestHeader("Authorization") String token) {}
}
```

## 拦截器

```java
@Component
public class AuthInterceptor implements HandlerInterceptor {

    @Override
    public boolean preHandle(HttpServletRequest request,
            HttpServletResponse response, Object handler) {
        String token = request.getHeader("Authorization");
        if (token == null) {
            throw new BusinessException(3001, "未登录");
        }
        // 解析 token，设置用户上下文
        return true;
    }
}

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Autowired
    private AuthInterceptor authInterceptor;

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(authInterceptor)
            .addPathPatterns("/api/**")
            .excludePathPatterns("/api/login", "/api/register");
    }
}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="spring-mvc" :height="400" />


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
