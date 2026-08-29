---
title: 动态 SQL
date: 2026-08-15  # date-auto-injected
---

# 🔥 MyBatis 动态 SQL

> 动态 SQL 是 MyBatis 的核心特性，让你**用 XML 拼接条件**，比 Java 字符串拼接优雅得多。

## 🎯 为什么需要动态 SQL？

```java
// ❌ 不使用动态 SQL：在 Java 中拼接
String sql = "SELECT * FROM users WHERE 1=1";
if (status != null) sql += " AND status = " + status;
if (minAge != null) sql += " AND age >= " + minAge;
// 问题：SQL 注入风险、字符串拼接难维护、性能差
```

```xml
<!-- ✅ 使用动态 SQL：在 XML 中拼接条件 -->
<select id="findUsers" resultType="User">
    SELECT * FROM users
    <where>
        <if test="status != null">AND status = #{status}</if>
        <if test="minAge != null">AND age >= #{minAge}</if>
    </where>
</select>
```

## 📚 动态 SQL 标签

### 1️⃣ `<if>` 条件判断

```xml
<!-- 基础：根据参数决定是否拼接条件 -->
<select id="findUsers" resultType="User">
    SELECT * FROM users
    WHERE 1=1
    <if test="name != null and name != ''">
        AND name LIKE CONCAT('%', #{name}, '%')
    </if>
    <if test="status != null">
        AND status = #{status}
    </if>
    <if test="minAge != null">
        AND age >= #{minAge}
    </if>
    <if test="maxAge != null">
        AND <![CDATA[ age <= #{maxAge} ]]>
    </if>
</select>
```

### 2️⃣ `<where>` 智能处理 WHERE

```xml
<!-- 自动去除开头的 AND/OR -->
<select id="findUsers" resultType="User">
    SELECT * FROM users
    <where>
        <if test="name != null">AND name LIKE CONCAT('%', #{name}, '%')</if>
        <if test="status != null">AND status = #{status}</if>
        <if test="minAge != null">AND age >= #{minAge}</if>
    </where>
    ORDER BY created_at DESC
</select>

<!-- 等价于（MyBatis 自动处理）： -->
<!-- WHERE 1=1 AND name LIKE ... AND status = ... -->
```

### 3️⃣ `<choose> / <when> / <otherwise>` 多分支

```xml
<!-- 类似 Java 的 switch-case -->
<select id="findBySortType" resultType="User">
    SELECT * FROM users
    ORDER BY
    <choose>
        <when test="sortType == 'name'">name</when>
        <when test="sortType == 'age'">age</when>
        <when test="sortType == 'created'">created_at</when>
        <otherwise>id</otherwise>
    </choose>
    <choose>
        <when test="order == 'desc'">DESC</when>
        <otherwise>ASC</otherwise>
    </choose>
</select>
```

### 4️⃣ `<foreach>` 遍历集合（最重要）

#### IN 查询

```xml
<!-- 批量查询：WHERE id IN (?, ?, ?) -->
<select id="findByIds" resultType="User">
    SELECT * FROM users
    WHERE id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</select>

<!-- 参数调用：findByIds(Arrays.asList(1, 2, 3)) -->
```

#### 批量插入

```xml
<!-- 批量 INSERT -->
<insert id="batchInsert" parameterType="list">
    INSERT INTO users (user_name, email, age) VALUES
    <foreach collection="list" item="user" separator=",">
        (#{user.userName}, #{user.email}, #{user.age})
    </foreach>
</insert>

<!-- 可选：加上 useGeneratedKeys 获取自增 ID -->
<insert id="batchInsert" parameterType="list" 
        useGeneratedKeys="true" keyProperty="id">
    INSERT INTO users (user_name, email, age) VALUES
    <foreach collection="list" item="user" separator=",">
        (#{user.userName}, #{user.email}, #{user.age})
    </foreach>
</insert>
```

#### 批量更新（foreach + case when）

```xml
<!-- 性能优化：用一条 SQL 批量更新 -->
<update id="batchUpdate" parameterType="list">
    UPDATE users
    <set>
        <foreach collection="list" item="user" separator=",">
            <if test="user.userName != null">
                user_name = CASE id
                <foreach collection="list" item="item" separator=" ">
                    WHEN #{item.id} THEN #{item.userName}
                </foreach>
            </if>
        </foreach>
    </set>
    WHERE id IN
    <foreach collection="list" item="item" open="(" separator="," close=")">
        #{item.id}
    </foreach>
</update>
```

### 5️⃣ `<set>` 动态 SET 子句

```xml
<!-- 更新时只 SET 非空字段 -->
<update id="updateSelective" parameterType="User">
    UPDATE users
    <set>
        <if test="userName != null">user_name = #{userName},</if>
        <if test="email != null">email = #{email},</if>
        <if test="age != null">age = #{age},</if>
        updated_at = NOW(),
    </set>
    WHERE id = #{id}
</update>
```

### 6️⃣ `<bind>` 创建变量

```xml
<!-- 绑定变量，可复用 -->
<select id="searchByName" resultType="User">
    <bind name="pattern" value="'%' + name + '%'"/>
    SELECT * FROM users WHERE name LIKE #{pattern}
</select>
```

### 7️⃣ `<sql>` 片段复用

```xml
<!-- 定义公共 SQL 片段 -->
<sql id="userColumns">
    id, user_name, email, age, status, created_at
</sql>

<sql id="userWhere">
    <where>
        <if test="status != null">status = #{status}</if>
        <if test="minAge != null">AND age >= #{minAge}</if>
    </where>
</sql>

<!-- 引用 -->
<select id="findUsers" resultType="User">
    SELECT <include refid="userColumns"/>
    FROM users
    <include refid="userWhere"/>
</select>
```

### 8️⃣ `<trim>` 自定义前缀后缀

```xml
<!-- trim 是 where/set 的底层实现 -->
<!-- where 标签等价于：trim prefix="WHERE" prefixOverrides="AND |OR " -->
<!-- set 标签等价于：trim prefix="SET" suffixOverrides="," -->

<!-- 自定义：去除前缀 "AND" -->
<select id="findUsers" resultType="User">
    SELECT * FROM users
    <trim prefix="WHERE" prefixOverrides="AND |OR ">
        <if test="name != null">AND name LIKE #{name}</if>
        <if test="status != null">AND status = #{status}</if>
    </trim>
</select>
```

### 9️⃣ `<choose>` 多分支（动态表名）

```xml
<!-- 动态表名（按年份分表） -->
<select id="findByYear" resultType="Order">
    SELECT * FROM
    <choose>
        <when test="year == 2024">orders_2024</when>
        <when test="year == 2025">orders_2025</when>
        <otherwise>orders</otherwise>
    </choose>
    WHERE id = #{id}
</select>
```

## 🎯 实战案例

### 案例 1：多条件搜索

```java
public interface ProductMapper {
    // 多条件搜索（条件可选）
    List<Product> search(ProductQuery query);
}

@Data
public class ProductQuery {
    private String keyword;       // 商品名称（模糊）
    private Long categoryId;       // 类目
    private BigDecimal minPrice;   // 最低价
    private BigDecimal maxPrice;   // 最高价
    private List<Integer> tags;    // 标签 ID 列表
    private String sortBy;        // 排序字段
    private String order;         // 排序方向
}
```

```xml
<select id="search" parameterType="ProductQuery" resultType="Product">
    SELECT <include refid="productColumns"/>
    FROM products
    <where>
        <!-- 关键词模糊搜索 -->
        <if test="keyword != null and keyword != ''">
            AND name LIKE CONCAT('%', #{keyword}, '%')
        </if>
        <!-- 类目精确筛选 -->
        <if test="categoryId != null">
            AND category_id = #{categoryId}
        </if>
        <!-- 价格区间 -->
        <if test="minPrice != null">
            AND price >= #{minPrice}
        </if>
        <if test="maxPrice != null">
            AND <![CDATA[ price <= #{maxPrice} ]]>
        </if>
        <!-- 标签 IN 查询 -->
        <if test="tags != null and tags.size() > 0">
            AND id IN (
                SELECT product_id FROM product_tags
                WHERE tag_id IN
                <foreach collection="tags" item="tagId" open="(" separator="," close=")">
                    #{tagId}
                </foreach>
            )
        </if>
        <!-- 上下架过滤 -->
        <if test="status != null">
            AND status = #{status}
        </if>
    </where>
    <!-- 动态排序 -->
    <choose>
        <when test="sortBy == 'price'">
            ORDER BY price
            <choose>
                <when test="order == 'desc'">DESC</otherwise>
                <otherwise>ASC</otherwise>
            </choose>
        </when>
        <when test="sortBy == 'sales'">
            ORDER BY sales_count DESC
        </when>
        <otherwise>
            ORDER BY created_at DESC
        </otherwise>
    </choose>
</select>
```

### 案例 2：批量更新（性能优化）

```xml
<!-- 一条 SQL 更新多条（效率高） -->
<update id="batchUpdateStatus">
    UPDATE products
    SET status = #{status},
        updated_at = NOW()
    WHERE id IN
    <foreach collection="ids" item="id" open="(" separator="," close=")">
        #{id}
    </foreach>
</update>

<!-- 批量更新不同字段（高级 CASE WHEN） -->
<update id="batchUpdateSelective" parameterType="list">
    UPDATE products
    <trim prefix="SET" suffixOverrides=",">
        <foreach collection="list" item="p" separator=",">
            <if test="p.name != null">name = #{p.name}</if>
            <if test="p.price != null">price = #{p.price}</if>
        </foreach>
    </trim>
    WHERE id IN
    <foreach collection="list" item="p" open="(" separator="," close=")">
        #{p.id}
    </foreach>
</update>
```

### 案例 3：动态排序与分页

```xml
<select id="findByPage" resultType="User">
    SELECT * FROM users
    <where>
        <if test="status != null">status = #{status}</if>
    </where>
    <choose>
        <when test="orderBy == 'name'">ORDER BY name</when>
        <when test="orderBy == 'age'">ORDER BY age</when>
        <when test="orderBy == 'created'">ORDER BY created_at</when>
        <otherwise>ORDER BY id</otherwise>
    </choose>
    <choose>
        <when test="asc == true">ASC</when>
        <otherwise>DESC</otherwise>
    </choose>
    LIMIT #{offset}, #{pageSize}
</select>
```

## ⚠️ 动态 SQL 的陷阱

### 1. 字符串拼接问题

```xml
<!-- ❌ 错误：#{name} 会被自动加引号，但 ${name} 是字符串拼接 -->
<if test="name != null">
    AND name LIKE '%${name}%'  <!-- SQL 注入风险！ -->
</if>

<!-- ✅ 正确：用 CONCAT + #{} -->
<if test="name != null">
    AND name LIKE CONCAT('%', #{name}, '%')
</if>
```

### 2. 特殊字符处理

```xml
<!-- <、>、& 等字符在 XML 中需要转义或用 CDATA -->
<if test="age != null">
    AND <![CDATA[ age >= #{age} ]]>
</if>
```

### 3. 性能陷阱

```xml
<!-- ❌ foreach 太大（IN 10000 个） -->
<foreach collection="list" item="id" open="(" separator="," close=")">
    #{id}
</foreach>
<!-- 数据库 IN 太多性能差 -->

<!-- ✅ 拆分：每批 500，分批查询 -->
<!-- Java 端拆分成多个 List<List<Integer>> -->
```

## 🎯 总结

**动态 SQL 标签速查：**

| 标签 | 用途 |
|---|---|
| `<if>` | 条件判断 |
| `<where>` | 智能 WHERE（去除开头的 AND/OR） |
| `<set>` | 智能 SET（去除末尾的逗号） |
| `<choose>/<when>/<otherwise>` | 多分支 |
| `<foreach>` | 遍历集合（IN/批量） |
| `<bind>` | 创建变量 |
| `<sql>` | 公共 SQL 片段 |
| `<trim>` | 自定义前后缀 |
| `<include>` | 引用 SQL 片段 |

**最佳实践：**
- ✅ 用 `<where>` 代替 WHERE 1=1
- ✅ 用 `<set>` 动态更新
- ✅ 用 `<foreach>` 处理 IN 和批量
- ✅ 用 `<sql>` 片段复用公共列
- ✅ CONCAT + #{} 防 SQL 注入
- ✅ 大批量 IN 拆分查询

**下一步：** [🧩 MyBatis 插件机制](/12-mybatis/plugins) — 自定义插件拦截 SQL 执行