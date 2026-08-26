---
title: Builder 建造者模式
description: 多参数对象构造 + Java Lombok @Builder + Go Functional Options + TypeScript chainable
---

# Builder 建造者模式

## 核心问题

当一个对象的构造需要**很多参数**（≥ 4 个），且部分参数可选时：
1. 用构造器重载会爆炸（`new User(name)`, `new User(name, age)`, ...）
2. 用 setter 会变成「半成品对象」（构造后状态不完整）
3. 用 Map / Json 传参会失去类型安全

## 核心思想

将「对象的构建」与「对象的表示」分离。用一个 Builder 类按步骤设置参数，最后调用 `build()` 一次性生成不可变对象。

**适用信号**：
- 构造参数 ≥ 4 个
- 部分参数可选
- 对象应该是不可变的
- 创建逻辑需要分步

## Java 实现

## 经典 Builder 模式

```java
public final class HttpRequest {
    private final URI uri;
    private final String method;
    private final Map<String, String> headers;
    private final Duration timeout;
    private final byte[] payload;

    private HttpRequest(Builder b) {
        this.uri = b.uri;
        this.method = b.method;
        this.headers = Map.copyOf(b.headers);  // 不可变
        this.timeout = b.timeout;
        this.payload = b.payload;
    }

    public static Builder newBuilder() { return new Builder(); }

    public static class Builder {
        private URI uri;
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();
        private Duration timeout = Duration.ofSeconds(30);
        private byte[] payload;

        public Builder uri(URI uri) { this.uri = uri; return this; }
        public Builder method(String m) { this.method = m; return this; }
        public Builder header(String k, String v) { this.headers.put(k, v); return this; }
        public Builder timeout(Duration d) { this.timeout = d; return this; }
        public Builder POST(byte[] body) { this.method = "POST"; this.payload = body; return this; }

        public HttpRequest build() {
            if (uri == null) throw new IllegalStateException("uri required");
            return new HttpRequest(this);
        }
    }
}

// 用法：链式调用，可读性极好
HttpRequest req = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Content-Type", "application/json")
    .timeout(Duration.ofSeconds(60))
    .POST(payload)
    .build();
```

## Lombok @Builder（推荐）

```java
@Builder
@Getter
public class User {
    private Long id;
    private String name;
    private String email;
    @Builder.Default private int age = 18;
    @Builder.Default private List<String> roles = List.of("user");
}

// 用法：Lombok 自动生成 UserBuilder
User u = User.builder()
    .id(1L)
    .name("Alice")
    .email("alice@example.com")
    .age(25)
    .role("admin")     // @Singular 自动支持
    .role("user")
    .build();
```

## 多语言实现

## Go：Functional Options（最 idiomatic）

```go
package server

import (
    "context"
    "log"
    "time"
)

type Server struct {
    addr    string
    timeout time.Duration
    logger  *log.Logger
    handler http.Handler
}

type Option func(*Server)

func WithTimeout(d time.Duration) Option {
    return func(s *Server) { s.timeout = d }
}

func WithLogger(l *log.Logger) Option {
    return func(s *Server) { s.logger = l }
}

func WithHandler(h http.Handler) Option {
    return func(s *Server) { s.handler = h }
}

func NewServer(addr string, opts ...Option) *Server {
    s := &Server{
        addr:    addr,
        timeout: 30 * time.Second,
        logger:  log.Default(),
    }
    for _, o := range opts {
        o(s)
    }
    return s
}

// 用法：极简，参数顺序无关
srv := NewServer(":8080",
    WithTimeout(60*time.Second),
    WithLogger(customLogger),
    WithHandler(myHandler),
)
```

Functional Options 是 Rob Pike（Go 之父）推荐的 Go 模式，被 grpc-go、k8s 等大型项目广泛使用。

## TypeScript：链式 Builder

```typescript
class QueryBuilder {
    private selects: string[] = [];
    private forms: string[] = [];
    private wheres: string[] = [];
    private orders: string[] = [];
    private limitCount?: number;

    select(...cols: string[]) { this.selects.push(...cols); return this; }
    from(table: string) { this.forms.push(table); return this; }
    where(cond: string) { this.wheres.push(cond); return this; }
    orderBy(col: string, dir: 'ASC' | 'DESC' = 'ASC') { this.orders.push(`${col} ${dir}`); return this; }
    limit(n: number) { this.limitCount = n; return this; }

    toSQL(): string {
        let sql = `SELECT ${this.selects.join(', ')} FROM ${this.forms.join(', ')}`;
        if (this.wheres.length) sql += ` WHERE ${this.wheres.join(' AND ')}`;
        if (this.orders.length) sql += ` ORDER BY ${this.orders.join(', ')}`;
        if (this.limitCount) sql += ` LIMIT ${this.limitCount}`;
        return sql;
    }
}

// 用法
const sql = new QueryBuilder()
    .select('id', 'name', 'email')
    .from('users')
    .where('age > 18')
    .orderBy('created_at', 'DESC')
    .limit(10)
    .toSQL();
// SELECT id, name, email FROM users WHERE age > 18 ORDER BY created_at DESC LIMIT 10
```

## 适用边界

✅ **使用场景**：
- 构造参数 ≥ 4 个（最重要信号）
- 多个参数可选
- 对象应该是不可变的
- 创建逻辑需要分步（如 `withHeader().withBody().build()`）
- 创建过程需要中间校验

❌ **避免场景**：
- 只有 1-2 个参数（直接 `new`）
- 所有参数必填且不多（构造器就够）
- 业务方需要中途修改字段（Builder 是一次性的）

🔄 **替代方案**：
- **构造器重载**：≤ 3 个参数时最简单
- **Setter / Lombok @Data**：可变对象
- **Map / Json**：动态配置（牺牲类型安全）
- **Functional Options (Go)**：Go 社区的 Builder

💡 **最佳实践**：
- Builder 本身应该是静态内部类（`HttpRequest.Builder`）
- `build()` 之前做参数校验
- 不要让 Builder 持有未初始化状态（爆 NullPointerException）
- `@Builder.Default` 给字段默认值


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
