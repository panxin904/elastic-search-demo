---
title: Magic Number 魔数
description: 症状 + 病因 + 药方 + 命名常量 + 配置文件 + 单元常量
---

# Magic Number 魔数

## 症状

```java
// 代码中充斥无解释数字
if (retryCount > 3) { /* 重试 */ }
if (temperature > 100) { /* 过热 */ }
if (cacheSize * 0.95 > maxSize) { /* 触发清理 */ }
Thread.sleep(5000);  // 为什么是 5 秒？
String salt = generateSalt(32);  // 为什么 32？
if (user.getAge() >= 18) { /* 成年人 */ }
BigDecimal taxRate = new BigDecimal("0.06");  // 为什么 6%？
```

**典型表现**：
1. 代码中有 `100`、`0.95`、`5000` 这类数字字面量
2. 数字含义不明（不知道是 KB 还是 MB）
3. 同一数字在多处重复出现
4. 修改一个数字要在多处查找替换
5. 新人看不懂「为什么是这个数字」

## 病因

1. **直接 hardcode 数字**（最常见）
   - 「先这样吧」心态
   - 没有常量定义规范

2. **没有常量定义规范**
   - 团队没有常量命名约定
   - 不知道该放在哪个类

3. **"反正能跑"心态**
   - 数字能用就行，不管含义

4. **配置文件未启用**
   - 业务参数应该走配置文件
   - 但开发者偷懒写死在代码里

5. **缺少 code review**
   - 没人问"这个 100 是什么意思"

6. **重构时遗留下未命名的魔数**
   - 原作者知道含义，新人不知道

## 药方

## 1. 命名常量

```java
public class RetryConfig {
    public static final int MAX_RETRY_COUNT = 3;
    public static final Duration RETRY_INTERVAL = Duration.ofMillis(5000);
    public static final int RETRY_BACKOFF_FACTOR = 2;
}

public class CacheConfig {
    public static final long MAX_CACHE_SIZE = 1_000_000L;  // 100 万
    public static final double HIGH_WATER_RATIO = 0.95;    // 95%
    public static final Duration CACHE_TTL = Duration.ofMinutes(30);
}

public class BusinessConstants {
    public static final int MIN_AGE_FOR_ADULT = 18;
    public static final BigDecimal TAX_RATE = new BigDecimal("0.06");
    public static final int PASSWORD_SALT_LENGTH = 32;
}
```

## 2. 配置文件化（Spring）

```java
@Configuration
@ConfigurationProperties(prefix = "app.retry")
@Data
public class RetryProperties {
    private int maxAttempts = 3;
    private Duration interval = Duration.ofMillis(5000);
    private int backoffFactor = 2;
}

// application.yml
app:
  retry:
    max-attempts: 5          # 可调整，不改代码
    interval: 10s
    backoff-factor: 2
```

## 3. 枚举常量

```java
public enum UserRole {
    GUEST(0),
    USER(1),
    ADMIN(2),
    SUPER_ADMIN(3);

    private final int level;

    UserRole(int level) { this.level = level; }

    public boolean canDeleteUsers() {
        return this.level >= ADMIN.level;
    }
}

// 用法：role.canDeleteUsers() 而不是 role.getLevel() >= 2
```

## 4. 单元常量

```java
// ❌ 单位不明
Thread.sleep(5000);
cache.setMaxSize(1000000);

// ✅ 明确单位
Thread.sleep(Duration.ofSeconds(5).toMillis());
cache.setMaxSize(Size.megabytes(1000));
```

## 检测工具

## ESLint（TypeScript / JavaScript）

```json
{
    "rules": {
        "no-magic-numbers": ["error", {
            "ignore": [-1, 0, 1, 2],
            "ignoreArrayIndexes": true,
            "enforceConst": true
        }]
    }
}
```

## Checkstyle（Java）

```xml
<module name="MagicNumber">
    <property name="ignoreNumbers" value="0, 1, 2, -1, 100"/>
    <property name="ignoreHashCodeMethod" value="true"/>
    <property name="ignoreAnnotation" value="true"/>
</module>
```

## SonarQube

```
Rule: Magic numbers should not be used
Severity: Major
Description: Magic numbers are numbers that appear in code without explanation.
```

## IntelliJ IDEA

```text
Settings → Editor → Inspections → Java → Code style issues → Magic number
勾选 → 红色高亮魔数
```

## 实战案例：缓存配置

## 重构前

```java
public class CacheService {
    public void put(String key, Object value) {
        long size = redisTemplate.opsForValue().get("cache:size");
        if (size > 1000000) {                          // 100 万？
            cleanup();
        }
        if (Math.random() < 0.05) {                    // 5%？
            persistToDisk();
        }
        redisTemplate.opsForValue().set(key, value, 30, TimeUnit.MINUTES);  // 30 分钟？
    }
}
```

## 重构后

```java
public class CacheConfig {
    public static final long MAX_CACHE_SIZE = 1_000_000L;
    public static final double PERSIST_PROBABILITY = 0.05;
    public static final Duration DEFAULT_TTL = Duration.ofMinutes(30);
}

public class CacheService {
    @Autowired private RedisTemplate<String, Object> redisTemplate;

    public void put(String key, Object value) {
        long size = redisTemplate.opsForValue().get("cache:size");
        if (size > CacheConfig.MAX_CACHE_SIZE) {
            cleanup();
        }
        if (Math.random() < CacheConfig.PERSIST_PROBABILITY) {
            persistToDisk();
        }
        redisTemplate.opsForValue().set(
            key,
            value,
            CacheConfig.DEFAULT_TTL.toMinutes(),
            TimeUnit.MINUTES
        );
    }
}
```

或者用配置文件：

```yaml
app:
  cache:
    max-size: 1000000
    persist-probability: 0.05
    default-ttl: 30m
```

```java
@ConfigurationProperties(prefix = "app.cache")
@Data
public class CacheProperties {
    private long maxSize = 1_000_000L;
    private double persistProbability = 0.05;
    private Duration defaultTtl = Duration.ofMinutes(30);
}
```

## 业务常量 vs 魔数

## 魔数（必须消除）

```java
Thread.sleep(5000);          // ❌
```

```java
private static final Duration RETRY_INTERVAL = Duration.ofSeconds(5);
Thread.sleep(RETRY_INTERVAL.toMillis());  // ✅
```

## 业务常量（保留魔数语义）

```java
private static final BigDecimal TAX_RATE = new BigDecimal("0.06");
private static final int ADULT_AGE = 18;
```

业务常量即使有名字，含义仍可能不清晰，需要**注释**说明。

```java
/**
 * 中国增值税税率（一般纳税人）
 * 国家税务总局 2019 年公告
 */
private static final BigDecimal VAT_RATE = new BigDecimal("0.13");

/**
 * 法定成年年龄（《民法典》17、18 条）
 */
private static final int LEGAL_ADULT_AGE = 18;
```

## 配置文件化（业务可调参数）

```yaml
app:
  pricing:
    tax-rate: 0.06
    discount-rate: 0.10
  age:
    legal-adult: 18
    senior: 60
```

**判断标准**：
- 业务规则相关 → 业务常量（命名 + 注释）
- 技术实现相关 → 配置文件
- 算式中间值 → 命名常量
- -1 / 0 / 1 / 100 这类通用值 → 允许

## 适用边界

✅ **必须命名**：
- 业务规则阈值（年龄 / 税率 / 折扣率）
- 算法参数（重试次数 / 超时时间 / 缓存大小）
- 算式中间值（高水位 / 低水位）
- 业务 ID 边界（管理员级别 / 状态码）

❌ **允许魔数**：
- 数组索引（`arr[0]`、`arr[1]`）
- 通用数学值（`-1`、`0`、`1`、`2`、`10`、`100`、`1000`）
- 循环边界（`for (int i = 0; i < 10; i++)`）
- 协议规定的值（HTTP 状态码、`null`、`true`、`false`）
- 单位换算（`1000` 表示 1 KB = 1000 字节）

💡 **最佳实践**：
- **CI 检查**：ESLint no-magic-numbers / Checkstyle
- **code review**：每个数字问"这是魔数吗？"
- **配置文件**：业务可调参数走 yml / properties
- **命名规范**：业务常量放 `*Constants.java`，技术常量放 `*Config.java`
- **注释解释**：业务常量加 Javadoc 引用法规 / 文档
