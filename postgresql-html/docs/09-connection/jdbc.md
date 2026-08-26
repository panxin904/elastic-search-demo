---
title: JDBC 连接
description: PostgreSQL JDBC 驱动实战
---

# JDBC 连接

> **TL;DR**：PG JDBC 驱动 = `org.postgresql.Driver`。**批量插入开 `rewriteBatchedInserts=true` 性能提升 10x**。**连接池用 HikariCP**。

## 一句话定义

```
JDBC 连接 = org.postgresql.Driver
          + HikariCP / DBCP 连接池
          + 批量插入优化
          + COPY 协议
```

## 基本连接

```java
// 1. 注册驱动（PG JDBC 4.0+ 自动注册）
Class.forName("org.postgresql.Driver");

// 2. 基本连接
String url = "jdbc:postgresql://localhost:5432/mydb";
Connection conn = DriverManager.getConnection(url, "user", "password");

// 3. SSL 连接
String url = "jdbc:postgresql://localhost:5432/mydb?sslmode=require&sslcert=client.crt&sslkey=client.key";

// 4. 带 schema
String url = "jdbc:postgresql://localhost:5432/mydb?currentSchema=myschema";
```

## HikariCP 配置（推荐）

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:6432/mydb
    username: appuser
    password: xxx
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: 50
      minimum-idle: 10
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      pool-name: HikariPool-PG
```

## 批量插入优化

### ❌ 错误方式（慢）

```java
PreparedStatement ps = conn.prepareStatement(
  "INSERT INTO users (name, email) VALUES (?, ?)"
);
for (User u : users) {
  ps.setString(1, u.name);
  ps.setString(2, u.email);
  ps.executeUpdate();  // 每次执行
}
```

### ✅ 正确方式（快 10x）

```yaml
# application.yml
spring:
  datasource:
    hikari:
      data-source-properties:
        rewriteBatchedInserts: true    # 关键！
```

```java
// 批量模式
for (User u : users) {
  ps.setString(1, u.name);
  ps.setString(2, u.email);
  ps.addBatch();                       // 加入批
}
ps.executeBatch();                     // 一次性执行
```

**原理**：`rewriteBatchedInserts=true` 把 1000 个 INSERT 合并成 1 条 multi-row INSERT。

## COPY 协议（最快）

```java
CopyManager copyManager = PGConnection.unwrap(PGConnection.class).getCopyAPI();

try (CopyIn copyIn = copyManager.copyIn(
    "COPY users (name, email) FROM STDIN WITH (FORMAT csv)")) {
    for (User u : users) {
        String row = u.name + "," + u.email + "
";
        copyIn.writeToCopy(row.getBytes(), 0, row.length());
    }
}
// 100 万行约 5 秒
```

## PG 特有配置

```yaml
spring:
  datasource:
    hikari:
      data-source-properties:
        # 1. 批量插入优化
        rewriteBatchedInserts: true
        
        # 2. Prepared Statement 缓存
        prepareThreshold: 5              # 5 次后缓存
        
        # 3. 默认 fetch 大小
        defaultRowFetchSize: 100
        
        # 4. 字符集
        charset: UTF-8
        
        # 5. 未知类型兼容性
        stringtype: undefined            # varlena 优化
        
        # 6. 取消长查询
        socketTimeout: 30                # 秒
```

## 常见错误

### 1. 连接超时

```
org.postgresql.net.PGTimeoutException
```

**修复**：
```yaml
spring:
  datasource:
    hikari:
      connection-timeout: 30000
```

### 2. SSL 配置

```
PSQLException: SSL error
```

**修复**：
```yaml
spring:
  datasource:
    url: jdbc:postgresql://host:5432/db?sslmode=require
```

### 3. 字符集

```
编码错误 / 乱码
```

**修复**：
```yaml
spring:
  datasource:
    url: jdbc:postgresql://host:5432/db?charset=UTF8
```

### 4. 时区

```yaml
# JVM 默认时区
user.timezone=Asia/Shanghai

# PG 连接时区
jdbc:postgresql://host:5432/db?TimeZone=Asia/Shanghai
```

## 实战案例

### 案例 1：批量插入 100 万行

```java
// 用 rewriteBatchedInserts=true
int batchSize = 1000;
for (int i = 0; i < users.size(); i += batchSize) {
    PreparedStatement ps = conn.prepareStatement(
      "INSERT INTO users (name, email) VALUES (?, ?)"
    );
    int end = Math.min(i + batchSize, users.size());
    for (int j = i; j < end; j++) {
        ps.setString(1, users.get(j).name);
        ps.setString(2, users.get(j).email);
        ps.addBatch();
    }
    ps.executeBatch();
}
// 100 万行约 30 秒

// 用 COPY（更快）
// 100 万行约 5 秒
```

### 案例 2：分页查询

```java
// OFFSET 性能差（深分页）
PreparedStatement ps = conn.prepareStatement(
  "SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?"
);

// 游标分页（推荐）
PreparedStatement ps = conn.prepareStatement(
  "SELECT * FROM users WHERE id > ? ORDER BY id LIMIT ?"
);
ps.setLong(1, lastId);  // 上次最后 id
ps.setInt(2, 20);
```

## 一句话总结

> **JDBC 连接 = HikariCP + rewriteBatchedInserts=true + 必要的 PG 优化参数**。**批量插入从 30s 降到 5s**。**深分页用游标**。**COPY 协议最快**（百万行 5s）。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


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
