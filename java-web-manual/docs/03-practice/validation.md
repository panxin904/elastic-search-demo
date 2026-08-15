---
title: 参数校验
---

# 参数校验

永远不要信任前端传来的数据，必须在服务端做严格校验。

## 注解校验

```java
@Data
public class UserCreateDTO {

    @NotBlank(message = "用户名不能为空")
    @Size(min = 2, max = 20, message = "用户名长度2-20位")
    private String username;

    @NotBlank(message = "手机号不能为空")
    @Pattern(regexp = "^1[3-9]\\d{9}$", message = "手机号格式不正确")
    private String phone;

    @NotNull(message = "年龄不能为空")
    @Min(value = 1, message = "年龄不能小于1")
    @Max(value = 150, message = "年龄不能大于150")
    private Integer age;

    @Email(message = "邮箱格式不正确")
    private String email;
}

@RestController
public class UserController {
    @PostMapping
    public Result<UserVO> create(@Valid @RequestBody UserCreateDTO dto) {
        // dto 已经过校验，放心使用
        return Result.success(userService.create(dto));
    }
}
```

## 常用校验注解

| 注解 | 说明 |
|---|---|
| @NotNull | 不能为 null |
| @NotBlank | 不能为 null 且 trim 后长度 > 0 |
| @NotEmpty | 不能为 null 且 size > 0（集合/字符串） |
| @Size(min, max) | 长度范围 |
| @Min / @Max | 数值范围 |
| @Pattern | 正则匹配 |
| @Email | 邮箱格式 |

## 分组校验

```java
// 创建时校验
public interface Create {}
// 更新时校验
public interface Update {}

public class UserDTO {
    @NotNull(groups = Update.class, message = "ID不能为空")
    private Long id;
    @NotBlank(groups = {Create.class, Update.class})
    private String username;
}

// Controller 中指定校验分组
@PostMapping
public Result create(@Validated(Create.class) @RequestBody UserDTO dto) {}

@PutMapping
public Result update(@Validated(Update.class) @RequestBody UserDTO dto) {}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="validation" :height="400" />
