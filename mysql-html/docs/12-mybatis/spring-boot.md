---
title: MyBatis 与 Spring Boot 集成
---

# 🔧 MyBatis 与 Spring Boot 集成实战

> 完整的 **Spring Boot + MyBatis-Plus + MySQL** 项目实战，从零搭建到生产部署。

## 🚀 项目初始化

### 1. 创建 Spring Boot 项目（推荐用 Spring Initializr）

```
访问 https://start.spring.io/ 或用 IDE
依赖：
- Spring Web
- MySQL Driver
- MyBatis Framework（选 Spring Boot 3 + MyBatis）
- Lombok（可选）
```

### 2. 添加 MyBatis-Plus 依赖

```xml
<dependencies>
    <!-- Spring Boot Starter -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <!-- MyBatis-Plus（核心） -->
    <dependency>
        <groupId>com.baomidou</groupId>
        <artifactId>mybatis-plus-boot-starter</artifactId>
        <version>3.5.5</version>
    </dependency>
    
    <!-- MySQL 驱动 -->
    <dependency>
        <groupId>com.mysql</groupId>
        <artifactId>mysql-connector-j</artifactId>
        <scope>runtime</scope>
    </dependency>
    
    <!-- Lombok -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <optional>true</optional>
    </dependency>
    
    <!-- 校验 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
</dependencies>
```

## 📁 完整项目结构

```
src/main/java/com/example/myapp/
├── Application.java                    # 启动类
├── config/
│   ├── MybatisPlusConfig.java          # MP 配置
│   ├── WebMvcConfig.java               # Web 配置
│   └── MetaObjectHandler.java           # 自动填充
├── entity/
│   ├── BaseEntity.java                 # 公共父类
│   └── User.java                        # 用户实体
├── mapper/
│   └── UserMapper.java                  # Mapper 接口
├── service/
│   ├── UserService.java                 # Service 接口
│   └── impl/
│       └── UserServiceImpl.java          # Service 实现
├── controller/
│   └── UserController.java              # 控制器
├── dto/
│   ├── UserDTO.java                     # 数据传输
│   └── UserQuery.java                   # 查询条件
└── common/
    ├── Result.java                      # 统一返回
    └── PageResult.java                  # 分页返回

src/main/resources/
├── application.yml                      # 配置
├── mapper/                               # XML 映射
│   └── UserMapper.xml
└── db/                                   # SQL 脚本
    └── init.sql
```

## ⚙️ application.yml 完整配置

```yaml
server:
  port: 8080
  servlet:
    context-path: /api

spring:
  application:
    name: myapp
  datasource:
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/myapp?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8
    username: root
    password: xxx
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      idle-timeout: 600000
      max-lifetime: 1800000
      connection-timeout: 30000

  # Jackson 配置
  jackson:
    date-format: yyyy-MM-dd HH:mm:ss
    time-zone: GMT+8

# MyBatis-Plus 配置
mybatis-plus:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.example.myapp.entity
  configuration:
    map-underscore-to-camel-case: true
    cache-enabled: false
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
    default-statement-timeout: 30
  global-config:
    banner: false
    db-config:
      id-type: assign_id
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0
  plugins:
    - com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor

# 日志
logging:
  level:
    com.example.myapp.mapper: debug
    com.baomidou.mybatisplus: warn
```

## 🚀 启动类

```java
package com.example.myapp;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.transaction.annotation.EnableTransactionManagement;

@SpringBootApplication
@EnableTransactionManagement
@MapperScan("com.example.myapp.mapper")
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

## 📦 Entity 层

### BaseEntity（公共父类）

```java
package com.example.myapp.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public abstract class BaseEntity {
    
    @TableId(value = "id", type = IdType.ASSIGN_ID)
    private Long id;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    
    @TableLogic
    @TableField(select = false)
    private Integer deleted;
    
    @Version
    private Integer version;
}
```

### User（用户实体）

```java
package com.example.myapp.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.Version;
import lombok.Data;
import lombok.EqualsAndHashCode;

@Data
@EqualsAndHashCode(callSuper = true)
@TableName("users")
public class User extends BaseEntity {
    
    private String userName;
    private String email;
    private Integer age;
    private Integer status;
    
    // 密码字段（查询时不返回）
    @com.baomidou.mybatisplus.annotation.TableField(select = false)
    private String password;
}
```

## 📋 Service 层（完整业务实现）

### UserService 接口

```java
package com.example.myapp.service;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.service.IService;
import com.example.myapp.dto.UserDTO;
import com.example.myapp.dto.UserQuery;
import com.example.myapp.entity.User;

public interface UserService extends IService<User> {
    
    /**
     * 创建用户（含校验）
     */
    boolean createUser(UserDTO dto);
    
    /**
     * 分页查询
     */
    IPage<User> pageQuery(UserQuery query);
    
    /**
     * 复杂查询（自定义 SQL）
     */
    java.util.List<UserDTO> getUsersWithOrders(Long userId);
}
```

### UserServiceImpl 实现

```java
package com.example.myapp.service.impl;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.myapp.dto.UserDTO;
import com.example.myapp.dto.UserQuery;
import com.example.myapp.entity.User;
import com.example.myapp.mapper.UserMapper;
import com.example.myapp.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor  // Lombok：自动 final 字段注入构造器
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
    
    private final UserMapper userMapper;
    
    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean createUser(UserDTO dto) {
        // 1. 校验（业务层）
        if (userMapper.selectCount(
            Wrappers.<User>lambdaQuery().eq(User::getEmail, dto.getEmail())
        ) > 0) {
            throw new RuntimeException("邮箱已存在");
        }
        
        // 2. DTO 转 Entity
        User user = new User();
        BeanUtils.copyProperties(dto, user);  // Spring 工具类
        
        // 3. 加密密码（实际项目用 BCrypt）
        user.setPassword("{noop}" + dto.getPassword());
        
        // 4. 保存（自动填 createdAt / updatedAt）
        return save(user);
    }
    
    @Override
    public IPage<User> pageQuery(UserQuery query) {
        // 构造分页对象
        Page<User> page = new Page<>(query.getPageNum(), query.getPageSize());
        
        // 构造查询条件
        return userMapper.selectPage(page, query.toWrapper());
    }
    
    @Override
    public List<UserDTO> getUsersWithOrders(Long userId) {
        // 一条 SQL 解决 N+1（JOIN）
        return userMapper.getUsersWithOrders(userId);
    }
}
```

## 📄 Mapper 层

### Mapper 接口

```java
package com.example.myapp.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.myapp.dto.UserDTO;
import com.example.myapp.entity.User;
import org.apache.ibatis.annotations.Param;

import java.util.List;

public interface UserMapper extends BaseMapper<User> {
    
    // ✅ 自动获得 30+ CRUD 方法
    
    /**
     * 自定义复杂查询（JOIN 解决 N+1）
     */
    List<UserDTO> getUsersWithOrders(@Param("userId") Long userId);
}
```

### Mapper XML（复杂查询）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.myapp.mapper.UserMapper">

    <!-- 用户 + 订单 关联查询 -->
    <resultMap id="userWithOrdersMap" type="UserDTO">
        <id column="u_id" property="id"/>
        <result column="user_name" property="userName"/>
        <result column="email" property="email"/>
        <!-- 一对多：订单列表 -->
        <collection property="orders" ofType="com.example.myapp.entity.Order">
            <id column="o_id" property="id"/>
            <result column="amount" property="amount"/>
            <result column="created_at" property="createdAt"/>
        </collection>
    </resultMap>

    <select id="getUsersWithOrders" resultMap="userWithOrdersMap">
        SELECT 
            u.id AS u_id, u.user_name, u.email,
            o.id AS o_id, o.amount, o.created_at
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.id = #{userId}
        ORDER BY o.created_at DESC
    </select>

</mapper>
```

## 🌐 Controller 层

### UserController

```java
package com.example.myapp.controller;

import com.baomidou.mybatisplus.core.metadata.IPage;
import com.example.myapp.common.Result;
import com.example.myapp.dto.UserDTO;
import com.example.myapp.dto.UserQuery;
import com.example.myapp.entity.User;
import com.example.myapp.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/user")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    /**
     * 分页查询
     * GET /api/user/page?pageNum=1&pageSize=10
     */
    @GetMapping("/page")
    public Result<IPage<User>> page(
        @RequestParam(defaultValue = "1") Integer pageNum,
        @RequestParam(defaultValue = "10") Integer pageSize,
        @RequestParam(required = false) String keyword
    ) {
        UserQuery query = new UserQuery();
        query.setPageNum(pageNum);
        query.setPageSize(pageSize);
        if (keyword != null) query.setKeyword(keyword);
        
        return Result.success(userService.pageQuery(query));
    }
    
    /**
     * 详情（含订单）
     * GET /api/user/{id}/detail
     */
    @GetMapping("/{id}/detail")
    public Result<UserDTO> detail(@PathVariable Long id) {
        List<UserDTO> list = userService.getUsersWithOrders(id);
        return Result.success(list.isEmpty() ? null : list.get(0));
    }
    
    /**
     * 创建
     * POST /api/user
     */
    @PostMapping
    public Result<User> create(@RequestBody @Valid UserDTO dto) {
        userService.createUser(dto);
        return Result.success();
    }
    
    /**
     * 更新
     * PUT /api/user
     */
    @PutMapping
    public Result<Boolean> update(@RequestBody @Valid UserDTO dto) {
        User user = new User();
        org.springframework.beans.BeanUtils.copyProperties(dto, user);
        return Result.success(userService.updateById(user));
    }
    
    /**
     * 删除（逻辑删除）
     * DELETE /api/user/{id}
     */
    @DeleteMapping("/{id}")
    public Result<Boolean> delete(@PathVariable Long id) {
        return Result.success(userService.removeById(id));
    }
}
```

## 📋 DTO & Common 类

### 统一返回 Result

```java
package com.example.myapp.common;

import lombok.Data;
import java.io.Serializable;

@Data
public class Result<T> implements Serializable {
    
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
    
    public static <T> Result<T> success() {
        return success(null);
    }
    
    public static <T> Result<T> error(int code, String message) {
        Result<T> r = new Result<>();
        r.setCode(code);
        r.setMessage(message);
        return r;
    }
}
```

### UserDTO

```java
package com.example.myapp.dto;

import com.example.myapp.entity.User;
import com.example.myapp.entity.Order;
import lombok.Data;

import javax.validation.constraints.Email;
import javax.validation.constraints.NotBlank;
import java.util.List;

@Data
public class UserDTO {
    private Long id;
    
    @NotBlank(message = "用户名不能为空")
    private String userName;
    
    @Email(message = "邮箱格式不正确")
    private String email;
    
    private Integer age;
    private String password;  // 创建时必填
    
    private List<Order> orders;  // 一对多
}
```

### UserQuery（查询条件）

```java
package com.example.myapp.dto;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.example.myapp.entity.User;
import lombok.Data;

@Data
public class UserQuery {
    private Integer pageNum = 1;
    private Integer pageSize = 10;
    private String keyword;  // 模糊匹配用户名
    
    public LambdaQueryWrapper<User> toWrapper() {
        LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
        if (keyword != null && !keyword.isEmpty()) {
            wrapper.like(User::getUserName, keyword);
        }
        wrapper.orderByDesc(User::getCreatedAt);
        return wrapper;
    }
}
```

## 🧪 测试

### Service 测试

```java
@SpringBootTest
@Transactional  // 测试后自动回滚
class UserServiceTest {
    
    @Autowired
    private UserService userService;
    
    @Test
    void testCreate() {
        UserDTO dto = new UserDTO();
        dto.setUserName("张三");
        dto.setEmail("zhangsan@example.com");
        dto.setPassword("xxx");
        
        assertTrue(userService.createUser(dto));
        
        // 验证自动填充
        User created = userService.getOne(
            Wrappers.<User>lambdaQuery().eq(User::getUserName, "张三")
        );
        assertNotNull(created.getCreatedAt());
        assertEquals(0, created.getVersion());
    }
    
    @Test
    void testDuplicateEmail() {
        UserDTO dto = new UserDTO();
        dto.setUserName("张三");
        dto.setEmail("duplicate@example.com");
        dto.setPassword("xxx");
        userService.createUser(dto);
        
        // 再次创建相同邮箱应抛异常
        UserDTO dto2 = new UserDTO();
        dto2.setUserName("李四");
        dto2.setEmail("duplicate@example.com");  // 相同邮箱
        dto2.setPassword("xxx");
        
        assertThrows(RuntimeException.class, () -> userService.createUser(dto2));
    }
    
    @Test
    void testPageQuery() {
        UserQuery query = new UserQuery();
        query.setPageNum(1);
        query.setPageSize(10);
        query.setKeyword("张");
        
        IPage<User> page = userService.pageQuery(query);
        assertTrue(page.getTotal() >= 0);
        assertNotNull(page.getRecords());
    }
}
```

### Controller 测试（用 MockMvc）

```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @Autowired
    private ObjectMapper objectMapper;
    
    @Test
    void testPage() throws Exception {
        mockMvc.perform(get("/api/user/page")
                .param("pageNum", "1")
                .param("pageSize", "10"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }
    
    @Test
    void testCreate() throws Exception {
        UserDTO dto = new UserDTO();
        dto.setUserName("测试用户");
        dto.setEmail("test@example.com");
        dto.setPassword("xxx");
        
        mockMvc.perform(post("/api/user")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200));
    }
}
```

## 📊 性能监控（Actuator）

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics, prometheus
  metrics:
    tags:
      application: myapp
```

访问 `http://localhost:8080/actuator/health` 查看应用健康状况。

## 🚀 部署

### 打 JAR 包

```bash
# Maven
mvn clean package

# Gradle
gradle bootJar
```

### 运行

```bash
# 直接运行
java -jar target/myapp-1.0.0.jar

# 后台运行（nohup）
nohup java -jar target/myapp-1.0.0.jar > app.log 2>&1 &
```

### Docker 部署

```dockerfile
FROM openjdk:17-jdk-slim
WORKDIR /app
COPY target/myapp-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

```bash
docker build -t myapp:1.0.0 .
docker run -d -p 8080:8080 --name myapp myapp:1.0.0
```

## 📋 实战检查清单

- ✅ Entity 用 `@TableName`, `@TableId` 等注解
- ✅ DTO 单独定义（与 Entity 解耦）
- ✅ Controller 只负责接收参数和返回结果（薄）
- ✅ Service 负责业务逻辑（厚）
- ✅ 复杂查询放 XML，简单查询用 MP
- ✅ 事务注解 `@Transactional`
- ✅ 校验用 Bean Validation
- ✅ 统一返回 Result
- ✅ 全局异常处理
- ✅ 日志规范

**下一步：** [🚀 MyBatis-Plus 实战](/12-mybatis/mybatis-plus) — 现代项目必学的 ORM 增强


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
