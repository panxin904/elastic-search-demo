---
title: Strategy 策略模式
description: 算法族互相替换 + 支付方式 / 排序算法 / 压缩算法 / Spring @Conditional
---

# Strategy 策略模式

## 核心问题

需要在运行时选择算法的具体实现（多种算法实现同一接口），且算法经常变化或新增。

**真实场景**：
- 支付方式（支付宝 / 微信 / PayPal / Stripe）
- 排序算法（冒泡 / 快速 / 归并 / 堆排序）
- 压缩算法（gzip / zstd / lz4 / snappy）
- 路线规划（最短距离 / 最少时间 / 避开收费）
- 推荐算法（协同过滤 / 内容相似 / 深度学习）

## 核心思想

定义一系列算法，把它们**一个个封装起来**，并且使它们可以**互相替换**。

**关键角色**：
- **Strategy**：策略接口（所有算法实现同一接口）
- **ConcreteStrategy**：具体策略
- **Context**：持有策略引用，按需调用

## TypeScript：支付方式

```typescript
interface PaymentStrategy {
    pay(amount: number): Promise<PaymentResult>;
}

class AlipayStrategy implements PaymentStrategy {
    async pay(amount: number): Promise<PaymentResult> {
        // 调用支付宝 SDK
        return { success: true, transactionId: 'alipay_' + Date.now() };
    }
}

class WechatPayStrategy implements PaymentStrategy {
    async pay(amount: number): Promise<PaymentResult> {
        // 调用微信支付 SDK
        return { success: true, transactionId: 'wxpay_' + Date.now() };
    }
}

class PayPalStrategy implements PaymentStrategy {
    async pay(amount: number): Promise<PaymentResult> {
        // 调用 PayPal SDK
        return { success: true, transactionId: 'pp_' + Date.now() };
    }
}

// Context
class PaymentContext {
    constructor(private strategy: PaymentStrategy) {}

    setStrategy(s: PaymentStrategy) { this.strategy = s; }

    async execute(amount: number) {
        return this.strategy.pay(amount);
    }
}

// 用法
const ctx = new PaymentContext(new AlipayStrategy());
await ctx.execute(100);

ctx.setStrategy(new WechatPayStrategy());
await ctx.execute(200);

ctx.setStrategy(new PayPalStrategy());
await ctx.execute(300);

// 新增支付方式：只需要新增一个 Strategy 类，不改其他代码
```

## 与 if-else 对比

```typescript
// ❌ if-else 地狱
function pay(method: string, amount: number) {
    if (method === 'alipay') {
        // 20 行支付宝逻辑
    } else if (method === 'wechat') {
        // 20 行微信逻辑
    } else if (method === 'paypal') {
        // 20 行 PayPal 逻辑
    }
    // 新增支付方式必须改这里（违反开闭原则）
}

// ✅ 策略模式
function pay(strategy: PaymentStrategy, amount: number) {
    return strategy.pay(amount);  // 新增策略只需新增类
}

// 类型安全
// 不会传错 method（编译期检查）
```

## Java 实战：压缩算法

```java
public interface CompressionStrategy {
    byte[] compress(byte[] data);
    byte[] decompress(byte[] data);
}

public class GzipStrategy implements CompressionStrategy {
    @Override public byte[] compress(byte[] data) {
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream();
             GZIPOutputStream gzos = new GZIPOutputStream(baos)) {
            gzos.write(data);
            return baos.toByteArray();
        } catch (IOException e) { throw new RuntimeException(e); }
    }
    @Override public byte[] decompress(byte[] data) {
        try (GZIPInputStream gzis = new GZIPInputStream(new ByteArrayInputStream(data));
             ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            gzis.transferTo(baos);
            return baos.toByteArray();
        } catch (IOException e) { throw new RuntimeException(e); }
    }
}

public class Lz4Strategy implements CompressionStrategy { /* LZ4 实现 */ }
public class ZstdStrategy implements CompressionStrategy { /* Zstandard 实现 */ }

@Service
public class CompressionService {
    private CompressionStrategy strategy = new GzipStrategy();  // 默认

    @Autowired private Environment env;

    public void init() {
        String algo = env.getProperty("compression.algo", "gzip");
        switch (algo) {
            case "lz4": strategy = new Lz4Strategy(); break;
            case "zstd": strategy = new ZstdStrategy(); break;
            default: strategy = new GzipStrategy();
        }
    }

    public byte[] compress(byte[] data) { return strategy.compress(data); }
}
```

## Spring 中的策略

```java
// Spring 的 @Conditional 是策略模式的容器化
@Configuration
public class DataSourceConfig {

    @Bean
    @ConditionalOnProperty(name = "db.type", havingValue = "mysql")
    public DataSource mysqlDataSource() {
        return new MySQLDataSource();
    }

    @Bean
    @ConditionalOnProperty(name = "db.type", havingValue = "postgres")
    public DataSource postgresDataSource() {
        return new PostgreSQLDataSource();
    }

    @Bean
    @ConditionalOnProperty(name = "db.type", havingValue = "oracle")
    public DataSource oracleDataSource() {
        return new OracleDataSource();
    }
}

// application.yml
// db.type: postgres  ← 启动时 Spring 自动选 PostgreSQLDataSource
```

不同数据库驱动就是不同策略，Spring 根据配置自动选择。

## 适用边界

✅ **使用场景**：
- 多种算法实现同一接口（支付 / 排序 / 压缩）
- 算法经常新增或变化
- 运行时选择算法（按配置 / 按业务条件）

❌ **避免场景**：
- 只有 1-2 个算法（直接调用即可）
- 业务方不需要切换（增加抽象成本）
- 算法差异不大（用参数化而非策略）

🔄 **与 State 区别**：
- **Strategy**：客户端主动选择
- **State**：状态间自动转换

🔄 **与 Template Method 区别**：
- **Strategy**：对象组合（运行期切换）
- **Template Method**：类继承（编译期决定）

💡 **最佳实践**：
- 策略接口要稳定（一旦确定不轻易改）
- 用工厂管理策略创建（避免到处 new）
- 配合 DI 容器使用（Spring 自动注入）
- 策略类应该是无状态的（方便复用）
