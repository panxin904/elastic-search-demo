---
title: MyBatis 插件机制
---

# 🧩 MyBatis 插件机制

> MyBatis 的插件机制（Interceptor）让你可以**拦截 SQL 执行的四个关键节点**，实现分页、性能监控、读写分离等高级功能。

## 🎯 拦截的四个节点

```
Executor → StatementHandler → ParameterHandler → ResultSetHandler
   ↓             ↓                ↓                  ↓
 执行器       SQL 处理器       参数处理器          结果集处理器
```

```
┌──────────────────────────────────────────┐
│           MyBatis 执行流程                   │
│                                           │
│  ┌──────────┐                              │
│  │ Executor │ ← 可拦截 update/query 等     │
│  └────┬─────┘                              │
│       ↓                                    │
│  ┌─────────────────┐                       │
│  │ StatementHandler │ ← 可拦截 prepare 等   │
│  └────┬────────────┘                       │
│       ↓                                    │
│  ┌──────────────────┐                      │
│  │ ParameterHandler  │ ← 可拦截 setParameter │
│  └────┬─────────────┘                      │
│       ↓                                    │
│  ┌──────────────────┐                      │
│  │ ResultSetHandler  │ ← 可拦截 handleResult │
│  └──────────────────┘                      │
└──────────────────────────────────────────┘
```

## 📝 自定义插件模板

```java
import org.apache.ibatis.executor.statement.StatementHandler;
import org.apache.ibatis.plugin.*;
import org.apache.ibatis.session.ResultHandler;

import java.sql.Statement;
import java.util.Properties;

@Intercepts({
    @Signature(
        type = StatementHandler.class,  // 拦截哪个类
        method = "prepare",              // 拦截哪个方法
        args = {Connection.class}         // 方法参数（用于重载区分）
    )
})
public class SqlPerformancePlugin implements Interceptor {
    
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        // 1. 前置处理：可修改参数、记录开始时间
        long startTime = System.currentTimeMillis();
        
        // 2. 执行原方法
        Object result = invocation.proceed();
        
        // 3. 后置处理：可获取结果、记录耗时
        long endTime = System.currentTimeMillis();
        long cost = endTime - startTime;
        
        // 获取 SQL 信息
        StatementHandler handler = (StatementHandler) invocation.getTarget();
        BoundSql boundSql = handler.getBoundSql();
        String sql = boundSql.getSql();
        
        // 记录慢 SQL（>100ms）
        if (cost > 100) {
            log.warn("Slow SQL [{}ms]: {}", cost, sql);
        }
        
        return result;
    }
    
    @Override
    public Object plugin(Object target) {
        // 创建代理对象（通常用 Plugin.wrap）
        return Plugin.wrap(target, this);
    }
    
    @Override
    public void setProperties(Properties properties) {
        // 从配置文件读取参数
        // 如：properties.getProperty("threshold")
    }
}
```

## 🚀 实战案例

### 案例 1：性能监控插件

```java
@Intercepts({
    @Signature(type = Executor.class, method = "query",
               args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class}),
    @Signature(type = Executor.class, method = "update",
               args = {MappedStatement.class, Object.class})
})
@Component
public class PerformanceMonitorPlugin implements Interceptor {
    
    private static final Logger log = LoggerFactory.getLogger(PerformanceMonitorPlugin.class);
    
    // 慢查询阈值（毫秒）
    private long threshold = 100;
    
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            
            MappedStatement ms = (MappedStatement) invocation.getArgs()[0];
            String sqlId = ms.getId();
            
            // 只记录超过阈值的
            if (cost > threshold) {
                BoundSql boundSql = ms.getBoundSql(invocation.getArgs()[1]);
                String sql = boundSql.getSql()
                    .replaceAll("\\s+", " ")
                    .replaceAll("\\?", "%s");
                
                // 填充参数
                Object paramObj = boundSql.getParameterObject();
                List<Object> params = getParams(boundSql);
                try {
                    sql = String.format(sql, params.toArray());
                } catch (Exception ignored) {}
                
                log.warn("[SLOW SQL] {}ms | {} | params={}", 
                    cost, sql, paramObj);
            }
        }
    }
    
    private List<Object> getParams(BoundSql boundSql) {
        Object paramObj = boundSql.getParameterObject();
        if (paramObj instanceof Map) {
            return new ArrayList<>(((Map<?, ?>) paramObj).values());
        }
        return Collections.singletonList(paramObj);
    }
    
    @Override
    public Object plugin(Object target) {
        return Plugin.wrap(target, this);
    }
    
    @Override
    public void setProperties(Properties properties) {
        String threshold = properties.getProperty("threshold", "100");
        this.threshold = Long.parseLong(threshold);
    }
}
```

**配置：**
```yaml
mybatis:
  plugins:
    - com.example.plugin.PerformanceMonitorPlugin
    - com.example.plugin.PerformanceMonitorPlugin:
        threshold: 200  # 阈值 200ms
```

### 案例 2：SQL 重写插件（数据脱敏）

```java
@Intercepts({
    @Signature(type = StatementHandler.class, method = "prepare",
               args = {Connection.class})
})
public class SqlMaskPlugin implements Interceptor {
    
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        StatementHandler handler = (StatementHandler) invocation.getTarget();
        BoundSql boundSql = handler.getBoundSql();
        String sql = boundSql.getSql();
        
        // 敏感字段脱敏（替换为 ? 防日志泄露）
        sql = sql.replaceAll("\\bphone\\b", "'***PHONE***'");
        sql = sql.replaceAll("\\bid_card\\b", "'***IDCARD***'");
        sql = sql.replaceAll("'(\\d{4})\\d{7}(\\d{4})'", "'$1****$2'");
        
        // 通过反射修改 SQL（MyBatis 的 BoundSql 没有 setter）
        Field sqlField = boundSql.getClass().getDeclaredField("sql");
        sqlField.setAccessible(true);
        sqlField.set(boundSql, sql);
        
        return invocation.proceed();
    }
}
```

### 案例 3：读写分离插件

```java
@Intercepts({
    @Signature(type = Executor.class, method = "query",
               args = {MappedStatement.class, Object.class, RowBounds.class, ResultHandler.class})
})
public class ReadWriteSplitPlugin implements Interceptor {
    
    // 用 ThreadLocal 标记是否走主库
    private static final ThreadLocal<Boolean> FORCE_MASTER = new ThreadLocal<>();
    
    @Autowired
    private DataSourceRouter dataSourceRouter;
    
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        MappedStatement ms = (MappedStatement) invocation.getArgs()[0];
        boolean isQuery = ms.getSqlCommandType() == SqlCommandType.SELECT;
        boolean forceMaster = FORCE_MASTER.get() != null;
        
        // 读操作走从库（除非强制主库）
        if (isQuery && !forceMaster) {
            DataSourceContextHolder.setDataSourceType("slave");
            try {
                return invocation.proceed();
            } finally {
                DataSourceContextHolder.clear();
            }
        }
        
        return invocation.proceed();
    }
    
    // 提供 API 强制走主库
    public static void forceMaster() {
        FORCE_MASTER.set(true);
    }
    
    public static void clearForceMaster() {
        FORCE_MASTER.remove();
    }
}
```

## 🧰 常用第三方插件

### PageHelper（分页插件，最流行）

```xml
<dependency>
    <groupId>com.github.pagehelper</groupId>
    <artifactId>pagehelper-spring-boot-starter</artifactId>
    <version>2.1.0</version>
</dependency>
```

```yaml
# 配置
pagehelper:
  helper-dialect: mysql
  reasonable: true
  support-methods-arguments: true
  params: count=countSql
```

```java
// 使用（极其简单）
@Service
public class UserService {
    public PageInfo<User> listUsers(int pageNum, int pageSize) {
        // 关键：先调用 startPage（用 ThreadLocal）
        PageHelper.startPage(pageNum, pageSize);
        
        // 紧跟的查询会被自动分页
        List<User> users = userMapper.findAll();
        
        // 包装成分页对象
        return new PageInfo<>(users);
    }
}
```

### MyBatis-Plus（功能增强，强烈推荐）

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.5</version>
</dependency>
```

详见 [🚀 MyBatis-Plus 实战](/12-mybatis/mybatis-plus) 章节。

### 数据权限插件（动态加 WHERE 条件）

```java
@Intercepts(@Signature(type = StatementHandler.class, method = "prepare",
                      args = {Connection.class}))
public class DataScopePlugin implements Interceptor {
    
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        // 获取当前用户的数据权限范围
        Set<Long> deptIds = SecurityContext.getCurrentUserDataScope();
        
        StatementHandler handler = (StatementHandler) invocation.getTarget();
        BoundSql boundSql = handler.getBoundSql();
        String originalSql = boundSql.getSql();
        
        // 追加 WHERE 条件（自动加 AND）
        if (originalSql.toUpperCase().contains("WHERE")) {
            boundSql.setSql(originalSql + " AND dept_id IN (" + 
                StringUtils.join(deptIds, ",") + ")");
        } else {
            boundSql.setSql(originalSql + " WHERE dept_id IN (" + 
                StringUtils.join(deptIds, ",") + ")");
        }
        
        return invocation.proceed();
    }
}
```

## ⚙️ 插件配置

### 单个插件

```java
@Configuration
public class MybatisConfig {
    
    @Bean
    public Interceptor performancePlugin() {
        return new PerformanceMonitorPlugin();
    }
    
    @Bean
    public ConfigurationCustomizer configurationCustomizer() {
        return configuration -> {
            // 添加插件
            configuration.addInterceptor(performancePlugin());
        };
    }
}
```

### 多个插件和顺序

```java
@Bean
public ConfigurationCustomizer mybatisPlugins() {
    return configuration -> {
        // 按顺序添加（前面的先执行）
        configuration.addInterceptor(new PerformancePlugin());
        configuration.addInterceptor(new SqlMaskPlugin());
        configuration.addInterceptor(new DataScopePlugin());
        
        // 分页插件必须最后添加（包装 SQL）
        configuration.addInterceptor(new PageInterceptor());
    };
}
```

**插件执行顺序：**
```
Interceptor1.intercept() → 
  Interceptor2.intercept() →
    Interceptor3.intercept() →
      invocation.proceed()  // 执行原 SQL
    返回 → Interceptor3 后续处理
  返回 → Interceptor2 后续处理
返回 → Interceptor1 后续处理
```

## ⚠️ 插件开发陷阱

### 1. 性能影响

```java
// ❌ 在插件中做重操作（如远程调用）
public Object intercept(Invocation invocation) throws Throwable {
    // 每次 SQL 都会执行的代码，必须轻量！
    remoteService.log();  // 远程调用会严重拖慢！
    return invocation.proceed();
}

// ✅ 异步处理（提交到线程池）
private static final ExecutorService POOL = ...;

public Object intercept(Invocation invocation) throws Throwable {
    long start = System.currentTimeMillis();
    try {
        return invocation.proceed();
    } finally {
        long cost = System.currentTimeMillis() - start;
        if (cost > 100) {
            // 异步记录（不阻塞主流程）
            POOL.submit(() -> logSlowSql(cost));
        }
    }
}
```

### 2. 循环引用

```java
// ⚠️ 拦截的类本身不能在插件中被拦截
@Intercepts({@Signature(type = MyPlugin.class, ...)})  // 不要这样做！
```

### 3. 多次注册

```java
// 同一个插件只注册一次
// MyBatis 内部会处理，但插件逻辑会执行多次
```

## 🎯 总结

**MyBatis 四大拦截点：**
- Executor：拦截 update/query/flush/commit
- StatementHandler：拦截 prepare（SQL 准备）
- ParameterHandler：拦截 setParameter
- ResultSetHandler：拦截 handleResult

**实战场景：**
- ✅ 性能监控：记录慢 SQL
- ✅ 数据脱敏：日志屏蔽敏感字段
- ✅ 读写分离：动态选择数据源
- ✅ 分页：PageHelper
- ✅ 数据权限：动态加 WHERE
- ✅ 多租户：动态表名替换

**下一步：** [🚀 MyBatis-Plus 实战](/12-mybatis/mybatis-plus) — 现代项目必备 ORM 增强