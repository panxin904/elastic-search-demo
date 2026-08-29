---
title: MyBatis / MyBatis-Plus
date: 2026-08-15  # date-auto-injected
---
# MyBatis / MyBatis-Plus
- MyBatis: mapper XML with #{param} (PreparedStatement) vs ${param} (string concat, SQL injection risk)
- MyBatis-Plus: BaseMapper`<T>`, QueryWrapper, LambdaQueryWrapper, auto pagination
```java
@Mapper
public interface UserMapper extends BaseMapper<User> {
  @Select("SELECT * FROM users WHERE age > #{age}")
  List<User> findByAge(@Param("age") int age);
}
// MyBatis-Plus lambda query
List<User> users = userMapper.selectList(
  new LambdaQueryWrapper<User>()
    .gt(User::getAge, 18)
    .eq(User::getStatus, 1)
);
```