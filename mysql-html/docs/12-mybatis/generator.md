---
title: 代码生成器
---

# 🎨 MyBatis-Plus 代码生成器

> 一键生成 **Entity + Mapper + Service + Controller** 全套代码，告别手写 CRUD。

## 🎯 Generator 能做什么？

```
一键生成：
✅ Entity 类（含 @TableName, @TableId, @TableField 等注解）
✅ Mapper 接口（继承 BaseMapper，零 SQL CRUD）
✅ Service 接口（继承 IService）
✅ ServiceImpl（继承 ServiceImpl）
✅ Controller（基础 CRUD 接口 + 分页查询）
✅ XML Mapper（如需复杂 SQL）

可选生成：
✅ DTO / VO（数据传输对象）
✅ Query 类（查询条件封装）
✅ 常量类
✅ 自定义模板（Freemarker）
```

## 🚀 快速使用

### 1. 添加依赖

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-generator</artifactId>
    <version>3.5.5</version>
</dependency>

<dependency>
    <groupId>org.freemarker</groupId>
    <artifactId>freemarker</artifactId>
    <version>2.3.32</version>
</dependency>
```

### 2. 标准生成器代码

```java
import com.baomidou.mybatisplus.generator.FastAutoGenerator;
import com.baomidou.mybatisplus.generator.config.OutputFile;
import com.baomidou.mybatisplus.generator.config.rules.NamingStrategy;
import com.baomidou.mybatisplus.generator.engine.FreemarkerTemplateEngine;

import java.util.Collections;

public class CodeGenerator {
    
    public static void main(String[] args) {
        // ✅ 一行启动（3.x 推荐）
        FastAutoGenerator.create(
                "jdbc:mysql://localhost:3306/mydb",  // 数据源 URL
                "root",                                   // 用户名
                "xxx"                                     // 密码
            )
            .globalConfig(builder -> {
                builder.author("YourName")                  // 作者
                       .enableSwagger()                      // 启用 swagger 注解
                       .outputDir(System.getProperty("user.dir") + "/src/main/java")
                       .commentDate("yyyy-MM-dd")
                       .fileOverride();                      // 覆盖已生成文件
            })
            .packageConfig(builder -> {
                builder.parent("com.example")              // 父包名
                       .moduleName("myapp")                // 模块名
                       .entity("entity")                    // Entity 包名
                       .mapper("mapper")
                       .service("service")
                       .serviceImpl("service.impl")
                       .controller("controller")
                       .pathInfo(Collections.singletonMap(
                           OutputFile.mapperXml, 
                           System.getProperty("user.dir") + "/src/main/resources/mapper"
                       ));
            })
            .strategyConfig(builder -> {
                builder.addInclude("user", "order", "product")    // 要生成的表名
                       .addTablePrefix("t_", "c_")                  // 过滤表前缀
                       
                       // Entity 策略
                       .entityBuilder()
                            .enableLombok()                       // 用 Lombok
                            .enableTableFieldAnnotation()          // 字段注解
                            .naming(NamingStrategy.underline_to_camel)  // 下划线转驼峰
                            .columnNaming(NamingStrategy.underline_to_camel)
                            .idType(IdType.ASSIGN_ID)             // 雪花算法
                            .logicDeleteColumnName("deleted")     // 逻辑删除字段
                            .logicDeletePropertyName("deleted")   // 实体类字段名
                            .versionColumnName("version")         // 乐观锁
                            .addTableFills(new Column("created_at", FieldFill.INSERT))
                            .addTableFills(new Column("updated_at", FieldFill.INSERT_UPDATE))
                            .idType(IdType.ASSIGN_ID)
                            .formatFileName("%sEntity")            // 不加 Entity 后缀
                       .build()
                       
                       // Controller 策略
                       .controllerBuilder()
                            .enableRestStyle()                   // @RestController
                            .enableHyphen()                       // 驼峰转连字符
                       .build()
                       
                       // Service 策略
                       .serviceBuilder()
                            .formatServiceFileName("%sService")
                       .build()
                       
                       // Mapper 策略
                       .mapperBuilder()
                            .formatMapperFileName("%sMapper")
                            .enableMapperAnnotation()              // @Mapper
                       .build();
            })
            .templateEngine(new FreemarkerTemplateEngine())   // 用 Freemarker 模板
            .execute();                                         // 执行
    }
}
```

## 📁 生成的代码结构

```
src/main/
├── java/com/example/myapp/
│   ├── entity/
│   │   ├── User.java              (含 Lombok @Data)
│   │   ├── Order.java
│   │   └── Product.java
│   ├── mapper/
│   │   ├── UserMapper.java        (extends BaseMapper<User>)
│   │   ├── OrderMapper.java
│   │   └── ProductMapper.java
│   ├── service/
│   │   ├── UserService.java       (extends IService<User>)
│   │   ├── OrderService.java
│   │   └── ProductService.java
│   ├── service/impl/
│   │   ├── UserServiceImpl.java   (extends ServiceImpl)
│   │   ├── OrderServiceImpl.java
│   │   └── ProductServiceImpl.java
│   └── controller/
│       ├── UserController.java     (含 @RestController, 基础 CRUD)
│       ├── OrderController.java
│       └── ProductController.java
└── resources/
    └── mapper/
        ├── UserMapper.xml
        ├── OrderMapper.xml
        └── ProductMapper.xml
```

## 📄 生成的代码示例

### Entity

```java
package com.example.myapp.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("user")
public class User {
    
    @TableId(value = "id", type = IdType.ASSIGN_ID)
    private Long id;
    
    private String userName;
    
    private String email;
    
    private Integer age;
    
    private Integer status;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    
    @TableLogic
    private Integer deleted;
    
    @Version
    private Integer version;
}
```

### Mapper

```java
package com.example.myapp.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.myapp.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
    // ✅ 已有 30+ 通用方法
    // 自定义 SQL 写在这里
}
```

### Service

```java
package com.example.myapp.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.myapp.entity.User;

public interface UserService extends IService<User> {
    // 自定义业务方法
}
```

### ServiceImpl

```java
package com.example.myapp.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.myapp.entity.User;
import com.example.myapp.mapper.UserMapper;
import com.example.myapp.service.UserService;
import org.springframework.stereotype.Service;

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
    // 自动拥有所有 CRUD 方法
}
```

### Controller

```java
package com.example.myapp.controller;

import com.example.myapp.entity.User;
import com.example.myapp.service.UserService;
import org.springframework.web.bind.annotation.*;

import javax.annotation.Resource;
import java.util.List;

@RestController
@RequestMapping("/user")
public class UserController {
    
    @Resource
    private UserService userService;
    
    @GetMapping("/list")
    public List<User> list() {
        return userService.list();
    }
    
    @GetMapping("/{id}")
    public User getById(@PathVariable Long id) {
        return userService.getById(id);
    }
    
    @PostMapping
    public boolean save(@RequestBody User user) {
        return userService.save(user);
    }
    
    @PutMapping
    public boolean update(@RequestBody User user) {
        return userService.updateById(user);
    }
    
    @DeleteMapping("/{id}")
    public boolean delete(@PathVariable Long id) {
        return userService.removeById(id);
    }
}
```

## 🔧 高级配置

### 1. 多表生成

```java
.strategyConfig(builder -> {
    builder.addInclude("user", "order", "product", "category")
           .addTablePrefix("t_")  // 自动去掉 t_ 前缀
           .addExclude("sensitive_data")  // 排除敏感表
})
```

### 2. 自定义列名转换

```java
.entityBuilder()
    .naming(NamingStrategy.underline_to_camel)        // 表名下划线转驼峰
    .columnNaming(NamingStrategy.underline_to_camel)   // 列名下划线转驼峰
    .addTableFills(new Column("created_at", FieldFill.INSERT))
```

### 3. 父类继承

```java
.entityBuilder()
    .superClass(BaseEntity.class)  // 继承公共父类
    .addSuperEntityColumns("id", "created_at", "updated_at")
```

```java
@Data
public abstract class BaseEntity {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
}
```

### 4. DTO/VO 生成

```java
.entityBuilder()
    .enableFileOverride()
    .javaTemplate("/templates/entity.java")  // 自定义模板
    .mapperTemplate("/templates/mapper.java")
    .serviceTemplate("/templates/service.java")
    .serviceImplTemplate("/templates/serviceImpl.java")
    .controllerTemplate("/templates/controller.java")
    .build()
```

### 5. 字段过滤

```java
.entityBuilder()
    .addIgnoreColumns("password", "salt")  // 不生成这些字段
    .addIgnoreColumns("create_by", "update_by")  // 不出现在 update SQL 中
```

### 6. Swagger 集成

```java
.globalConfig(builder -> {
    builder.enableSwagger()  // 自动加 @ApiModel 等注解
})
```

```xml
<dependency>
    <groupId>io.swagger</groupId>
    <artifactId>swagger-annotations</artifactId>
    <version>2.2.0</version>
</dependency>
```

## 📚 实战：完整的企业级生成器

```java
public class EnterpriseGenerator {
    
    public static void main(String[] args) {
        FastAutoGenerator.create("jdbc:mysql://192.168.1.10:3306/mydb", "root", "xxx")
            .globalConfig(builder -> {
                builder.author("DBA Team")
                       .enableSwagger()
                       .dateType(DateType.ONLY_DATE)  // 实体类用 java.util.Date
                       .outputDir(getOutputDir())
                       .commentDate("yyyy-MM-dd")
                       .build();
            })
            .packageConfig(builder -> {
                builder.parent("com.company.project")
                       .moduleName("biz")
                       .entity("entity")
                       .mapper("mapper")
                       .service("service")
                       .serviceImpl("service.impl")
                       .controller("controller")
                       .pathInfo(Collections.singletonMap(
                           OutputFile.mapperXml,
                           getResourceDir() + "/mapper"
                       ))
                       .build();
            })
            .strategyConfig(builder -> {
                // 配置策略
                builder.addInclude(getIncludeTables())  // 动态获取表
                       .addTablePrefix("t_", "c_")
                       .enableSkipView()  // 跳过视图
                       
                       .entityBuilder()
                           .enableLombok()
                           .enableTableFieldAnnotation()
                           .naming(NamingStrategy.underline_to_camel)
                           .columnNaming(NamingStrategy.underline_to_camel)
                           .idType(IdType.ASSIGN_ID)
                           .logicDeleteColumnName("deleted")
                           .logicDeletePropertyName("deleted")
                           .versionColumnName("version")
                           .addTableFills(
                               new Column("created_at", FieldFill.INSERT),
                               new Column("updated_at", FieldFill.INSERT_UPDATE)
                           )
                           .build()
                       
                       .controllerBuilder()
                           .enableRestStyle()
                           .enableHyphen()
                           .build()
                       
                       .serviceBuilder()
                           .formatServiceFileName("%sService")
                           .build()
                       
                       .mapperBuilder()
                           .formatMapperFileName("%sMapper")
                           .enableMapperAnnotation()
                           .build();
            })
            .templateEngine(new FreemarkerTemplateEngine())
            .execute();
    }
    
    private static String getIncludeTables() {
        // 动态获取要生成的表（从配置文件或数据库读取）
        return "user,order,product,category,inventory";
    }
    
    private static String getOutputDir() {
        return System.getProperty("user.dir") + "/src/main/java";
    }
    
    private static String getResourceDir() {
        return System.getProperty("user.dir") + "/src/main/resources";
    }
}
```

## 🛠️ IDE 插件（IntelliJ IDEA）

### MyBatisX 插件

```bash
# IntelliJ IDEA → Settings → Plugins → 搜索 MyBatisX
# 功能：
# - 从 Mapper 接口跳转到 XML
# - 自动生成基础 CRUD XML
# - 代码补全
```

### MyBatis Log 插件

```bash
# 插件：MyBatis Log
# 功能：
# - 把 `Preparing: SELECT * FROM users WHERE id = ?` 这种日志
# - 替换为完整的 SQL（带参数值）
# - 方便调试和复制到 Navicat 等工具
```

## ⚠️ 注意事项

### 1. 不要每次启动都重新生成

```java
// ❌ 错误做法：在 Spring Boot 启动时自动执行
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
        // ❌ 不要在这里执行生成器
    }
}

// ✅ 正确：单独运行（mvn exec、IDEA 手动）
// 命令行：java -cp xxx Generator
// 或 IDE 右键运行 main
```

### 2. 生成后检查

```bash
# 生成后检查：
# 1. XML 文件是否生成（如需复杂 SQL）
# 2. Entity 注解是否正确（@TableName 等）
# 3. 主键策略是否合理（雪花 vs 自增）
# 4. 字段映射是否对（snake_case → camelCase）
# 5. 关联表是否需要额外的 VO/DTO
```

### 3. 版本兼容

```xml
<!-- 注意版本对应 -->
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.5</version>  <!-- 必须与 generator 一致 -->
</dependency>
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-generator</artifactId>
    <version>3.5.5</version>  <!-- 保持一致 -->
</dependency>
```

## 🎯 总结

**代码生成器优势：**
- ✅ 提高效率 10 倍（手写 vs 生成）
- ✅ 代码风格统一（团队规范）
- ✅ 减少手写错误（注解自动加）
- ✅ 字段映射自动处理（snake_case）
- ✅ 集成 MP 全功能（逻辑删除、乐观锁、自动填充）

**最佳实践：**
- ✅ Generator 当独立工具运行（不随项目）
- ✅ 配置版本控制（确保团队一致）
- ✅ 生成后 code review
- ✅ 复杂 SQL 用 XML（不被覆盖）
- ✅ 表结构变化时重新生成

**下一步：** [🎯 MyBatis 性能优化](/12-mybatis/performance) — N+1 问题、批量操作、慢 SQL 优化


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
