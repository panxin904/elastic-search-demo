---
title: MVC 模式
date: 2026-08-15  # date-auto-injected
---

# MVC 模式

Spring MVC 是 Spring Web 框架的核心，基于 Model-View-Controller 模式。

## Spring MVC 请求流程

```
Client → DispatcherServlet → HandlerMapping → Controller
                                       ↓
                                  HandlerAdapter
                                       ↓
                                  Controller.method()
                                       ↓
                                  ViewResolver / @ResponseBody
                                       ↓
                                  Response → Client
```

## Controller 写法

```java
@RestController  // = @Controller + @ResponseBody
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/{id}")
    public Result<UserVO> getById(@PathVariable Long id) {
        return Result.success(userService.getById(id));
    }

    @GetMapping
    public Result<PageResult<UserVO>> list(
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        return Result.success(userService.listByPage(page, size));
    }

    @PostMapping
    public Result<UserVO> create(@Valid @RequestBody UserCreateDTO dto) {
        return Result.success(userService.create(dto));
    }
}
```

## 拦截器 vs 过滤器

| | Filter | Interceptor |
|---|---|---|
| 层面 | Servlet 容器 | Spring 框架 |
| 能获取 Bean | 否 | 是 |
| 能获取请求体 | 否（只能 request/response） | 是（HandlerMethod） |
| 使用场景 | 编码、跨域、安全 | 鉴权、日志、性能统计 |

## 🛠️ Spring MVC 关键注解

- `@RestController` = `@Controller` + `@ResponseBody`（返回 JSON）
- `@RequestMapping` 父注解 + `@GetMapping/@PostMapping` 子注解
- `@PathVariable` 路径参数 / `@RequestParam` 查询参数 / `@RequestBody` 请求体
- `@Valid` 触发参数校验（搭配 `@NotNull/@Min/@Max` 等）
- `@ControllerAdvice` + `@ExceptionHandler` 全局异常处理

**性能调优**：异步 MVC（`@Async` + `WebMvcConfigurer` 配置 ThreadPoolTaskExecutor）
可释放 Servlet 线程，适合 IO 密集型接口。

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="mvc-pattern" :height="400" />
