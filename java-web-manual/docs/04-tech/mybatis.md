---
title: MyBatis / MyBatis-Plus
date: 2026-08-15  # date-auto-injected
---

# MyBatis / MyBatis-Plus

MyBatis 是 Java 最流行的 ORM 框架之一，MyBatis-Plus 在其基础上提供了更多便捷功能。

## MyBatis vs MyBatis-Plus

| | MyBatis | MyBatis-Plus |
|---|---|---|
| 基础 CRUD | 手写 SQL | 内置 BaseMapper |
| 分页 | 手动实现 | Page 类型 + 插件 |
| 条件构造 | Example / 手写 | LambdaQueryWrapper |
| 代码生成 | 无 | 内置 Generator |

## 基本用法

```java
// Mapper 接口
@Mapper
public interface UserMapper extends BaseMapper<User> {

    User selectByPhone(@Param("phone") String phone);

    List<User> selectByCondition(@Param("name") String name,
                                  @Param("status") Integer status);
}
```

## MyBatis-Plus 核心功能

```java
// 内置 CRUD
userMapper.selectById(1L);
userMapper.selectList(new LambdaQueryWrapper<User>()
    .eq(User::getStatus, 1)
    .like(User::getUsername, "张"));

// 分页
Page<User> page = new Page<>(1, 20);
userMapper.selectPage(page, wrapper);

// 逻辑删除（@TableLogic）
// 自动将 DELETE 转为 UPDATE deleted = 1
```

## #{} vs ${}

| | #{} | ${} |
|---|---|---|
| 方式 | 预编译占位符 | 字符串替换 |
| 防注入 | 是 | 否 |
| 用途 | WHERE 条件值 | 表名、列名（动态 SQL）|
| 安全 | ✅ 安全 | ⚠️ 有注入风险 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="mybatis" :height="400" />
