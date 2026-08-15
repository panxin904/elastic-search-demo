---
title: Web 开发
---

# 🌐 Spring Boot Web 开发

> 掌握 REST API 开发、参数校验、统一异常处理，是每个 Java 开发者必备技能。

## 🚀 第一个 REST API

```java
@RestController  // = @Controller + @ResponseBody
@RequestMapping("/api/users")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping
    public List<User> list() {
        return userService.findAll();
    }
    
    @GetMapping("/{id}")
    public User getById(@PathVariable Long id) {
        return userService.findById(id);
    }
    
    @PostMapping
    public User create(@RequestBody @Valid UserDTO dto) {
        return userService.create(dto);
    }
    
    @PutMapping("/{id}")
    public User update(@PathVariable Long id, @RequestBody @Valid UserDTO dto) {
        return userService.update(id, dto);
    }
    
    @DeleteMapping("/{id}")
    public void delete(@PathVariable Long id) {
        userService.delete(id);
    }
}
```

## 📍 请求映射

| 注解 | 说明 | 示例 |
|---|---|---|
| `@GetMapping` | GET 请求 | 查询 |
| `@PostMapping` | POST 请求 | 创建 |
| `@PutMapping` | PUT 请求 | 全量更新 |
| `@PatchMapping` | PATCH 请求 | 部分更新 |
| `@DeleteMapping` | DELETE 请求 | 删除 |
| `@RequestMapping` | 通用映射 | 兼容所有 |

```java
// 简写形式
@GetMapping("/users")              // = @RequestMapping(value = "/users", method = GET)
@PostMapping(value = "/users", consumes = "application/json")
```

## 📦 参数绑定

### @PathVariable（路径变量）

```java
@GetMapping("/users/{id}/orders/{orderId}")
public Order getOrder(
    @PathVariable Long id,
    @PathVariable("orderId") String oid  // 自定义绑定名
) {
    return orderService.getById(oid);
}

// 正则约束
@GetMapping("/users/{id:[0-9]+}")
public User getById(@PathVariable Long id) {
    return userService.findById(id);
}
```

### @RequestParam（查询参数）

```java
@GetMapping("/users")
public List<User> list(
    @RequestParam(defaultValue = "1") int pageNum,
    @RequestParam(defaultValue = "10") int pageSize,
    @RequestParam(required = false) String keyword
) {
    return userService.list(pageNum, pageSize, keyword);
}

// Map 接收所有参数
@GetMapping("/search")
public List<User> search(@RequestParam Map<String, String> params) {
    return userService.search(params);
}
```

### @RequestBody（请求体 JSON）

```java
@PostMapping("/users")
public User create(@RequestBody UserDTO dto) {
    return userService.create(dto);
}

// 必填 + 校验
@PostMapping("/users")
public User create(@RequestBody @Valid UserDTO dto) {
    return userService.create(dto);
}
```

### @RequestHeader / @CookieValue

```java
@GetMapping("/me")
public User me(@RequestHeader("Authorization") String token,
              @CookieValue("sessionId") String sessionId) {
    return userService.currentUser(token, sessionId);
}
```

## ✅ 参数校验

### 注解

```java
@Data
public class UserDTO {
    
    @NotNull(message = "ID不能为空")
    private Long id;
    
    @NotBlank(message = "用户名不能为空")
    @Size(min = 3, max = 20, message = "用户名长度3-20")
    private String username;
    
    @Email(message = "邮箱格式不正确")
    private String email;
    
    @Min(value = 0, message = "年龄不能小于0")
    @Max(value = 150, message = "年龄不能大于150")
    private Integer age;
    
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式错误")
    private String phone;
    
    @Past(message = "生日必须是过去时间")
    private LocalDate birthday;
    
    @Future(message = "过期时间必须是未来")
    private LocalDateTime expireAt;
}
```

### 启用校验

```java
@PostMapping("/users")
public User create(@RequestBody @Valid UserDTO dto) {
    // 校验失败自动抛 MethodArgumentNotValidException
    return userService.create(dto);
}
```

### 分组校验

```java
public interface Create {}
public interface Update {}

@Data
public class UserDTO {
    @Null(groups = Create.class)
    @NotNull(groups = Update.class)
    private Long id;
    
    @NotBlank(groups = {Create.class, Update.class})
    private String username;
}

@PostMapping
public User create(@RequestBody @Validated(Create.class) UserDTO dto) {
    return userService.create(dto);
}
```

## 🚨 统一异常处理

### @ControllerAdvice / @ExceptionHandler

```java
@RestControllerAdvice  // = @ControllerAdvice + @ResponseBody
public class GlobalExceptionHandler {
    
    // 1. 业务异常
    @ExceptionHandler(BusinessException.class)
    public Result<Void> handleBusiness(BusinessException e) {
        log.warn("业务异常: {}", e.getMessage());
        return Result.error(400, e.getMessage());
    }
    
    // 2. 参数校验异常
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public Result<Void> handleValidation(MethodArgumentNotValidException e) {
        String msg = e.getBindingResult().getFieldErrors().stream()
            .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
            .collect(Collectors.joining("; "));
        return Result.error(400, "参数校验失败: " + msg);
    }
    
    // 3. 404
    @ExceptionHandler(NoHandlerFoundException.class)
    public Result<Void> handle404(NoHandlerFoundException e) {
        return Result.error(404, "接口不存在");
    }
    
    // 4. 全局兜底
    @ExceptionHandler(Exception.class)
    public Result<Void> handleAll(Exception e) {
        log.error("系统异常", e);
        return Result.error(500, "系统繁忙，请稍后重试");
    }
}
```

### 自定义业务异常

```java
@Getter
public class BusinessException extends RuntimeException {
    private final int code;
    
    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
    }
    
    public BusinessException(String message) {
        this(500, message);
    }
}

// 使用
throw new BusinessException(404, "用户不存在");
```

### 统一返回格式

```java
@Data
public class Result<T> {
    private int code;
    private String message;
    private T data;
    
    public static <T> Result<T> success(T data) {
        Result<T> r = new Result<>();
        r.setCode(200);
        r.setMessage("success");
        r.setData(data);
        return r;
    }
    
    public static <T> Result<T> error(int code, String message) {
        Result<T> r = new Result<>();
        r.setCode(code);
        r.setMessage(message);
        return r;
    }
}
```

## 🔧 拦截器与过滤器

### HandlerInterceptor

```java
public class AuthInterceptor implements HandlerInterceptor {
    
    @Override
    public boolean preHandle(HttpServletRequest request, 
                           HttpServletResponse response, 
                           Object handler) throws Exception {
        String token = request.getHeader("Authorization");
        if (token == null) {
            response.setStatus(401);
            return false;
        }
        // 验证 token
        return true;
    }
}

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new AuthInterceptor())
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/auth/login");
    }
}
```

### Filter（更底层）

```java
@Component
@Order(1)
public class LogFilter implements Filter {
    
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain) 
            throws IOException, ServletException {
        long start = System.currentTimeMillis();
        chain.doFilter(req, res);
        long cost = System.currentTimeMillis() - start;
        log.info("Request cost: {}ms", cost);
    }
}
```

## 📄 文件上传

```java
@PostMapping("/upload")
public String upload(@RequestParam("file") MultipartFile file) throws IOException {
    if (file.isEmpty()) {
        throw new BusinessException("文件为空");
    }
    
    // 限制大小
    if (file.getSize() > 10 * 1024 * 1024) {
        throw new BusinessException("文件超过 10MB");
    }
    
    // 保存到本地
    String filename = UUID.randomUUID() + "-" + file.getOriginalFilename();
    File dest = new File("/tmp/upload/" + filename);
    file.transferTo(dest);
    
    return "上传成功: " + filename;
}
```

```yaml
# application.yml
spring:
  servlet:
    multipart:
      max-file-size: 10MB
      max-request-size: 50MB
```

## 🌐 CORS 跨域

```java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOriginPatterns("*")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true)
                .maxAge(3600);
    }
}

// 或注解方式
@CrossOrigin(origins = "*", maxAge = 3600)
@RestController
public class UserController { ... }
```

## 📊 实战：统一 API 响应

```java
@RestController
@RequestMapping("/api/products")
public class ProductController {
    
    @Autowired
    private ProductService productService;
    
    @GetMapping
    public Result<Page<Product>> list(
        @RequestParam(defaultValue = "1") int pageNum,
        @RequestParam(defaultValue = "10") int pageSize
    ) {
        Page<Product> page = productService.list(pageNum, pageSize);
        return Result.success(page);
    }
    
    @GetMapping("/{id}")
    public Result<Product> detail(@PathVariable Long id) {
        Product p = productService.getById(id);
        if (p == null) {
            throw new BusinessException(404, "商品不存在");
        }
        return Result.success(p);
    }
    
    @PostMapping
    public Result<Product> create(@RequestBody @Valid ProductDTO dto) {
        return Result.success(productService.create(dto));
    }
    
    @DeleteMapping("/{id}")
    public Result<Void> delete(@PathVariable Long id) {
        productService.delete(id);
        return Result.success();
    }
}
```

## 🎯 总结

**Web 开发核心：**
- ✅ `@RestController` + 请求映射注解
- ✅ 参数绑定：`@PathVariable` / `@RequestParam` / `@RequestBody`
- ✅ 参数校验：`@Valid` + `@NotNull` / `@NotBlank` 等
- ✅ 统一异常：`@RestControllerAdvice` + `@ExceptionHandler`
- ✅ 拦截器 / 过滤器：AOP 思想

**最佳实践：**
- ✅ Controller 只做参数接收和返回
- ✅ 业务逻辑放 Service 层
- ✅ 用 `@Valid` 做参数校验
- ✅ 用 `@RestControllerAdvice` 统一异常
- ✅ 返回统一 `Result<T>` 格式

**下一步：** [💾 数据访问](/01-springboot/data) — Spring Data JPA、MyBatis-Plus 集成