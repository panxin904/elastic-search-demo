---
title: 数据库连接池
---

# 💧 数据库连接池

> 连接池是数据库访问的**基础设施**。选错连接池或配置不当，**性能可差 10 倍**。本章深入对比主流连接池，详解 HikariCP 的正确配置。

## 🎯 为什么需要连接池？

```
没有连接池：
- 每次请求：建立 TCP 连接 → 鉴权 → 执行 SQL → 关闭连接
- 单次耗时：30-100ms
- 1 万次请求：1000 秒（数据库连接数爆炸）

有连接池：
- 启动时预创建 N 个连接
- 复用连接，省去建立/销毁开销
- 单次耗时：1-5ms（提升 10-50 倍）
```

## 📊 主流连接池对比

| 连接池 | 性能 | 特性 | 适用场景 |
|---|---|---|---|
| **HikariCP** | ⭐⭐⭐⭐⭐ | 极快，零依赖 | **默认推荐** |
| Druid (Alibaba) | ⭐⭐⭐⭐ | 监控完善，WAF 过滤 | 需要详细监控 |
| Tomcat JDBC | ⭐⭐⭐⭐ | Tomcat 内置 | Tomcat 项目 |
| DBCP | ⭐⭐ | 老牌，稳定 | 老项目 |
| C3P0 | ⭐ | 太古老 | 不推荐 |

**HikariCP 性能对比**（来自官方 benchmark）：

```
HikariCP:  ~50,000 ops/sec
Tomcat JDBC: ~45,000 ops/sec
Druid:     ~40,000 ops/sec
DBCP:      ~10,000 ops/sec
```

## 🚀 HikariCP 实战（推荐）

### 添加依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-jdbc</artifactId>
</dependency>
<!-- HikariCP 已包含在 spring-boot-starter-jdbc 中 -->
```

### application.yml 完整配置

```yaml
spring:
  datasource:
    type: com.zaxxer.hikari.HikariDataSource
    driver-class-name: com.mysql.cj.jdbc.Driver
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=Asia/Shanghai&characterEncoding=utf8&rewriteBatchedStatements=true
    username: root
    password: xxx
    
    hikari:
      # === 核心配置（必调） ===
      # 最大连接数
      maximum-pool-size: 20
      # 最小空闲连接
      minimum-idle: 5
      # 获取连接超时（毫秒）
      connection-timeout: 30000
      # 空闲连接超时（毫秒）
      idle-timeout: 600000
      # 连接最大存活时间（毫秒）
      max-lifetime: 1800000
      # 连接测试查询
      connection-test-query: SELECT 1
      
      # === 性能优化（推荐） ===
      # 数据源名称
      pool-name: MyHikariPool
      # 预热连接数（启动时立即创建）
      # minimum-idle=5 表示预热 5 个
      # 批量大小
      # data-source-properties.rewriteBatchedStatements=true  # 必须加！MySQL 驱动优化
      # MySQL 驱动专属优化
      data-source-properties:
        cachePrepStmts: true
        prepStmtCacheSize: 250
        prepStmtCacheSqlLimit: 2048
        useServerPrepStmts: true
        rewriteBatchedStatements: true
        cacheResultSetMetadata: true
        cacheServerConfiguration: true
        elideSetAutoCommits: true
        maintainTimeStats: false
      
      # === 监控（可选） ===
      register-mbeans: true
      # 泄露检测（超时未关闭连接会被记录）
      leak-detection-threshold: 60000
      
      # === 验证（可选） ===
      validation-timeout: 5000
      # 自动提交
      auto-commit: true
```

### 关键参数详解

| 参数 | 默认 | 推荐 | 说明 |
|---|---|---|---|
| `maximum-pool-size` | 10 | 20-30 | 最多多少个连接 |
| `minimum-idle` | 等同 max | 5-10 | 保持空闲连接数 |
| `connection-timeout` | 30s | 30s | 获取连接超时 |
| `idle-timeout` | 10min | 10-15min | 空闲多久被回收 |
| `max-lifetime` | 30min | 30min | 连接最大存活时间 |
| `leak-detection-threshold` | 0 | 60s | 连接泄露检测 |

### 如何计算 maximum-pool-size？

```
公式（来自 HikariCP wiki）：
connections = ((core_count × 2) + effective_spindle_count)

其中：
- core_count: CPU 核心数
- effective_spindle_count: 存储盘数（SSD=1，HDD=多盘取 1）

示例：
- 4 核 + 1 SSD = (4×2)+1 = 9（建议 10-20）
- 8 核 + 1 SSD = (8×2)+1 = 17（建议 20-30）

⚠️ MySQL 默认 max_connections = 151
⚠️ 所有应用实例的连接数总和不应超过这个值
```

## 🔥 Druid 实战（需要详细监控时）

### 添加依赖

```xml
<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>druid-spring-boot-starter</artifactId>
    <version>1.2.20</version>
</dependency>
```

### 配置

```yaml
spring:
  datasource:
    type: com.alibaba.druid.pool.DruidDataSource
    url: jdbc:mysql://localhost:3306/mydb
    username: root
    password: xxx
    driver-class-name: com.mysql.cj.jdbc.Driver
    
    druid:
      # 基础配置
      initial-size: 5
      min-idle: 5
      max-active: 20
      max-wait: 60000
      
      # 检测
      test-while-idle: true
      test-on-borrow: false
      test-on-return: false
      
      # 性能
      pool-prepared-statements: true
      max-pool-prepared-statement-per-connection-size: 20
      
      # 监控（特色）
      filters: stat,wall,slf4j
      filter:
        stat:
          enabled: true
          log-slow-sql: true
          slow-sql-millis: 1000
        wall:
          enabled: true  # 防 SQL 注入
          config:
            multi-statement-allow: true
      
      # 监控页面
      stat-view-servlet:
        enabled: true
        login-username: admin
        login-password: admin
        url-pattern: /druid/*
```

**Druid 监控页面：** 访问 `http://localhost:8080/druid/`

可以看到：
- 实时 SQL 执行统计
- 慢 SQL 列表
- 连接池使用情况
- 各种维度的统计

## 📊 多数据源下的连接池配置

```yaml
# application.yml
spring:
  datasource:
    master:
      url: jdbc:mysql://master:3306/mydb
      username: root
      password: xxx
      hikari:
        maximum-pool-size: 10
        pool-name: MasterPool
    slave:
      url: jdbc:mysql://slave:3306/mydb
      username: readonly
      password: xxx
      hikari:
        maximum-pool-size: 30  # 从库承担读流量，连接可以更多
        pool-name: SlavePool
        read-only: true  # HikariCP 标记为只读连接
```

**关键原则：**
- **主库连接少**（10）：处理写操作，连接不能太多
- **从库连接多**（30）：处理读流量，连接可适当增加
- **总和 ≤ MySQL max_connections**

## 🔧 实战：监控连接池

### 启用 HikariCP 指标（Spring Boot Actuator）

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
        include: health, metrics, prometheus
  metrics:
    enable:
      hikaricp: true  # 开启 HikariCP 指标
```

**访问指标：** `http://localhost:8080/actuator/metrics/hikaricp.connections.active`

**关键指标：**
- `hikaricp.connections.active`：活跃连接数
- `hikaricp.connections.idle`：空闲连接数
- `hikaricp.connections.pending`：等待连接的线程数
- `hikaricp.connections.timeout`：获取连接超时次数
- `hikaricp.connections.acquire`：获取连接总次数

### Prometheus + Grafana 监控

```yaml
management:
  endpoints:
    web:
      exposure:
        include: prometheus
  prometheus:
    metrics:
      export:
        enabled: true
```

Prometheus 抓取 `http://localhost:8080/actuator/prometheus`，Grafana 导入官方 Dashboard 模板。

**告警规则：**
```promql
# 连接池使用率 > 80%
hikaricp_connections_active / hikaricp_connections_max > 0.8

# 获取连接超时
rate(hikaricp_connections_timeout_total[5m]) > 0

# 等待连接线程 > 10
hikaricp_connections_pending > 10
```

## 🛠️ 常见问题与解决

### 问题 1：连接泄露

```java
// ❌ 没有正确关闭连接
public void leak() {
    Connection conn = dataSource.getConnection();
    // 业务逻辑...
    // 忘记 close()
}

// ✅ 用 try-with-resources
public void good() {
    try (Connection conn = dataSource.getConnection()) {
        // 业务逻辑
    }  // 自动 close()
}
```

**检测泄露：**
```yaml
hikari:
  leak-detection-threshold: 60000  # 60 秒未关闭的连接会被记录
```

### 问题 2：连接池耗尽

```
报错：HikariPool-1 - Connection is not available, request timed out
```

**原因与解决：**
```java
// 1. 长事务（连接占用太久）
@Transactional  // 事务持续 5 分钟
public void longRunning() {
    // 慢查询 + 远程调用 + 大数据处理
}

// ✅ 拆分
public void shortRunning() {
    // 快速操作
}
```

```yaml
# 2. 连接池配置过小
hikari:
  maximum-pool-size: 10  # 如果应用用 20 个连接就太小
# ✅ 调到 30
```

```java
// 3. 连接未释放
Connection conn = dataSource.getConnection();
// 忘记 close
// ✅ 用 try-with-resources
```

### 问题 3：连接空闲超时

```
报错：Connection marked as broken
```

**原因：** 防火墙 / 路由器的空闲连接超时  
**解决：**
```yaml
hikari:
  # 比防火墙超时短
  max-lifetime: 1800000  # 30 分钟
  idle-timeout: 600000   # 10 分钟
  
  # 或用 keepalive（MySQL 驱动）
  data-source-properties:
    socketTimeout: 300000
    connectTimeout: 30000
```

## 🎯 性能优化清单

| 优化项 | 性能提升 | 说明 |
|---|---|---|
| `maximum-pool-size` 合理 | 20-50% | 太小/太大都慢 |
| `minimum-idle` 预热 | 启动时更快 | 避免冷启动 |
| `rewriteBatchedStatements=true` | **5-10x** | 批量 INSERT 必备 |
| `cachePrepStmts=true` | 1.5-3x | PreparedStatement 缓存 |
| `useServerPrepStmts=true` | 1.5-3x | 用服务器端预编译 |
| `prepStmtCacheSize=250` | 1.5-2x | 缓存 250 个 SQL |
| `leak-detection-threshold` | 调试 | 找连接泄露 |
| Prometheus 监控 | 主动 | 提前发现问题 |

## 🎯 总结

**连接池选型建议：**
- ✅ **默认选 HikariCP**（Spring Boot 默认，性能最好）
- ✅ 需要详细监控选 **Druid**（阿里生态，WAF 过滤）
- ✅ 老项目用 DBCP/C3P0（升级 HikariCP）

**配置黄金法则：**
- `maximum-pool-size` = 核心数 × 2 + 磁盘数
- `minimum-idle` = `maximum-pool-size` 的 1/4
- `max-lifetime` ≤ 数据库 `wait_timeout`
- `connection-timeout` 30 秒
- 必加 `rewriteBatchedStatements=true`

**生产环境必备：**
- ✅ 启用 Prometheus 监控
- ✅ 启用 leak detection
- ✅ 配置告警（连接池使用率 > 80%）
- ✅ 定期 review 慢 SQL

**下一步：** [🔀 多数据源配置](/13-multids/multi-datasource) — 多库场景的实战