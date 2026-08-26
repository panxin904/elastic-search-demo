---
title: MyBatis 快速入门
---

# ⚙️ MyBatis 快速入门

> MyBatis 是 Java 生态最流行的 ORM 框架之一，**SQL 与 Java 代码分离**，既保留 SQL 灵活性，又提供对象映射能力。

## 🎯 MyBatis 是什么？

MyBatis（前身 iBatis）是 Apache 顶级项目，通过 **XML 或注解** 配置 SQL，将 Java 方法映射到 SQL 语句。

```
┌────────────────────────────────┐
│        Application              │
│   ┌────────────────────────┐   │
│   │  UserMapper（接口）    │   │
│   │   findById(int id)     │   │
│   │   insert(User user)    │   │
│   └────────────────────────┘   │
│            │                    │
│            ▼ MyBatis 解析        │
│   ┌────────────────────────┐   │
│   │  UserMapper.xml        │   │
│   │  （SQL 映射）          │   │
│   └────────────────────────┘   │
│            │                    │
│            ▼ JDBC               │
│   ┌────────────────────────┐   │
│   │       MySQL            │   │
│   └────────────────────────┘   │
└────────────────────────────────┘
```

## 🚀 Spring Boot 集成 MyBatis

### 1. 添加依赖

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>3.0.3</version>
</dependency>

<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
</dependency>
```

### 2. application.yml 配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: xxx
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5

mybatis:
  # Mapper XML 文件位置
  mapper-locations: classpath:mapper/**/*.xml
  # 实体类别名包
  type-aliases-package: com.example.entity
  # 下划线转驼峰
  configuration:
    map-underscore-to-camel-case: true
    # 打印 SQL（生产环境关闭）
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
    # 缓存配置
    cache-enabled: true
    # 延迟加载
    lazy-loading-enabled: true
    aggressive-lazy-loading: false
    # 二级缓存
    second-level-cache-enabled: true

  # 配置插件（PageHelper, MyBatis-Plus 等）
  plugins:
    - com.github.pagehelper.PageInterceptor
```

### 3. 启动类扫描 Mapper

```java
@SpringBootApplication
@MapperScan("com.example.mapper")
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

## 📝 Mapper 接口

```java
package com.example.mapper;

import com.example.entity.User;
import org.apache.ibatis.annotations.Param;

public interface UserMapper {
    // 简单查询
    User findById(Integer id);
    
    // 列表查询
    List<User> findAll();
    
    // 条件查询（多个参数用 @Param 命名）
    List<User> findByStatus(@Param("status") Integer status,
                            @Param("minAge") Integer minAge);
    
    // 插入（返回影响行数）
    int insert(User user);
    
    // 插入（返回自增 ID）
    int insertReturnId(User user);
    
    // 更新
    int update(User user);
    
    // 删除（按 ID）
    int deleteById(Integer id);
    
    // 统计
    long countByStatus(Integer status);
    
    // 分页查询
    List<User> findByPage(@Param("offset") int offset,
                          @Param("limit") int limit);
}
```

## 📄 Mapper XML（最常用的方式）

### 基础 CRUD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.UserMapper">

    <!-- 结果映射：列名 → 实体字段 -->
    <resultMap id="userResultMap" type="User">
        <id column="id" property="id"/>
        <result column="user_name" property="userName"/>
        <result column="created_at" property="createdAt"/>
    </resultMap>

    <!-- 公共 SQL 片段 -->
    <sql id="userColumns">
        id, user_name, email, age, status, created_at
    </sql>

    <!-- 查询所有 -->
    <select id="findAll" resultMap="userResultMap">
        SELECT <include refid="userColumns"/>
        FROM users
    </select>

    <!-- 按 ID 查询 -->
    <select id="findById" parameterType="int" resultMap="userResultMap">
        SELECT <include refid="userColumns"/>
        FROM users
        WHERE id = #{id}
    </select>

    <!-- 多条件查询（注意参数命名 #{status} 对应 @Param） -->
    <select id="findByStatus" resultMap="userResultMap">
        SELECT <include refid="userColumns"/>
        FROM users
        WHERE status = #{status}
          AND age >= #{minAge}
        ORDER BY created_at DESC
    </select>

    <!-- 插入 -->
    <insert id="insert" parameterType="User" useGeneratedKeys="true" keyProperty="id">
        INSERT INTO users (user_name, email, age, status, created_at)
        VALUES (#{userName}, #{email}, #{age}, #{status}, NOW())
    </insert>

    <!-- 更新 -->
    <update id="update" parameterType="User">
        UPDATE users
        SET user_name = #{userName},
            email = #{email},
            age = #{age},
            updated_at = NOW()
        WHERE id = #{id}
    </update>

    <!-- 删除 -->
    <delete id="deleteById" parameterType="int">
        DELETE FROM users WHERE id = #{id}
    </delete>

    <!-- 统计 -->
    <select id="countByStatus" parameterType="int" resultType="long">
        SELECT COUNT(*) FROM users WHERE status = #{status}
    </select>

</mapper>
```

## 🎨 实体类

```java
package com.example.entity;

import lombok.Data;

@Data
public class User {
    private Integer id;
    private String userName;     // 对应 user_name 列
    private String email;
    private Integer age;
    private Integer status;
    private LocalDateTime createdAt;
}
```

## 🎯 调用示例

```java
@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    // 注入 SqlSession（高级用法，可手动控制）
    @Autowired
    private SqlSession sqlSession;
    
    public User getUser(Integer id) {
        // 简单调用
        return userMapper.findById(id);
    }
    
    public List<User> listActiveUsers(Integer minAge) {
        return userMapper.findByStatus(1, minAge);
    }
    
    @Transactional
    public User createUser(User user) {
        userMapper.insertReturnId(user);  // 返回自增 ID
        return user;
    }
    
    // 使用 SqlSession 的高级查询
    public User findByEmailCustom(String email) {
        return sqlSession.selectOne(
            "com.example.mapper.UserMapper.findByEmail",
            email
        );
    }
}
```

## 🔧 注解方式（不需要 XML）

简单的 CRUD 可以用注解替代 XML：

```java
public interface UserMapper {
    
    @Select("SELECT * FROM users WHERE id = #{id}")
    User findById(Integer id);
    
    @Select("SELECT * FROM users WHERE status = #{status} ORDER BY created_at DESC")
    List<User> findByStatus(@Param("status") Integer status);
    
    @Insert("INSERT INTO users (user_name, email) VALUES (#{userName}, #{email})")
    @Options(useGeneratedKeys = true, keyProperty = "id")
    int insert(User user);
    
    @Update("UPDATE users SET user_name = #{userName} WHERE id = #{id}")
    int update(User user);
    
    @Delete("DELETE FROM users WHERE id = #{id}")
    int deleteById(Integer id);
}
```

**XML vs 注解：**
- ✅ XML：适合复杂 SQL（动态 SQL、复用片段）
- ✅ 注解：适合简单 SQL（开发快）
- 💡 项目规范：推荐 XML（统一管理）

## 🧪 单元测试（用 H2 或真实 MySQL）

```java
@SpringBootTest
class UserMapperTest {
    
    @Autowired
    private UserMapper userMapper;
    
    @Test
    void testFindById() {
        User user = userMapper.findById(1);
        assertThat(user).isNotNull();
        assertThat(user.getId()).isEqualTo(1);
    }
    
    @Test
    void testInsert() {
        User user = new User();
        user.setUserName("张三");
        user.setEmail("zhangsan@x.com");
        userMapper.insert(user);
        assertThat(user.getId()).isNotNull();
    }
}
```

## 🎯 总结

**MyBatis 核心概念：**
- ✅ Mapper 接口（Java 方法定义）
- ✅ Mapper XML（SQL 实现）或注解
- ✅ ResultMap（结果映射）
- ✅ 参数映射（#{paramName}）
- ✅ 动态 SQL（if/where/foreach）

**最佳实践：**
- ✅ 使用 XML 统一管理 SQL
- ✅ XML 和 Mapper 接口放同包
- ✅ 用 @Param 命名参数
- ✅ 用 resultMap 而不是 resultType（字段多时）
- ✅ 复杂查询用 PageHelper 分页

**下一步：** [🔥 MyBatis 动态 SQL](/12-mybatis/dynamic-sql) — if/where/foreach/choose 的妙用


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
