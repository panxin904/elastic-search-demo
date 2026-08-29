---
title: Template Method 模板方法模式
date: 2026-08-15  # date-auto-injected
description: 算法骨架不变 + 部分步骤延迟 + Spring JdbcTemplate / Go http.Handler / Java Servlet
---

# Template Method 模板方法模式

## 核心问题

多个类有相似的算法流程，但部分步骤的具体实现不同。把**通用流程**抽到父类，把**变化部分**留给子类。

**真实场景**：
- Spring JdbcTemplate（流程固定，参数化 SQL 和 RowMapper）
- Java Servlet（service 方法固定，子类实现 doGet / doPost）
- Go http.Handler（HandleFunc 固定，业务实现 HandlerFunc）
- Java AbstractList（增删改固定，子类实现 get）

## 核心思想

定义一个算法的**骨架**，将一些步骤延迟到子类。模板方法使得子类可以不改变算法结构即可重新定义算法的某些步骤。

**关键角色**：
- **AbstractClass**：抽象类，定义模板方法和抽象步骤
- **ConcreteClass**：子类，实现抽象步骤

## Java 实战：Spring JdbcTemplate

```java
// JdbcTemplate 的 query 方法（简化版）
public <T> T query(String sql, RowMapper<T> rowMapper, Object... args) {
    // 1. 获取连接（固定）
    Connection conn = dataSource.getConnection();

    // 2. 创建 PreparedStatement（固定）
    PreparedStatement ps = conn.prepareStatement(sql);

    // 3. 设置参数（固定）
    for (int i = 0; i < args.length; i++) {
        ps.setObject(i + 1, args[i]);
    }

    // 4. 执行 SQL（固定）
    ResultSet rs = ps.executeQuery();

    // 5. 映射结果（变化点，由 RowMapper 提供）
    T result = null;
    if (rs.next()) {
        result = rowMapper.mapRow(rs, 0);
    }

    // 6. 关闭资源（固定）
    rs.close();
    ps.close();
    conn.close();

    return result;
}

// 用法：业务方只提供 SQL + RowMapper
User user = jdbcTemplate.query(
    "SELECT id, name, email FROM users WHERE id = ?",
    (rs, rowNum) -> new User(rs.getLong("id"), rs.getString("name"), rs.getString("email")),
    userId
);
```

JdbcTemplate 帮你写好流程（获取连接 → 创建 statement → 设置参数 → 执行 → 关闭），你只需要提供变化的部分（SQL 和 RowMapper）。

## Java Servlet

```java
// 抽象类 HttpServlet（模板）
public abstract class HttpServlet extends GenericServlet {
    // 模板方法：处理 HTTP 请求
    @Override
    public void service(ServletRequest req, ServletResponse res) {
        HttpServletRequest request = (HttpServletRequest) req;
        HttpServletResponse response = (HttpServletResponse) res;
        service(request, response);  // 调用重载
    }

    protected void service(HttpServletRequest req, HttpServletResponse resp) {
        String method = req.getMethod();
        if (method.equals("GET")) doGet(req, resp);
        else if (method.equals("POST")) doPost(req, resp);
        // ... PUT / DELETE 等
    }

    // 抽象步骤（子类实现）
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) { /* 默认 405 */ }
    protected void doPost(HttpServletRequest req, HttpServletResponse resp) { /* 默认 405 */ }
}

// 具体子类
public class UserServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest req, HttpServletResponse resp) {
        // 业务逻辑
    }
}
```

Servlet 容器（Tomcat / Jetty）调用 `service()`，流程由 HttpServlet 决定，子类只实现 `doGet` / `doPost` 等钩子。

## Go http.Handler

```go
// net/http 包的 Handler 接口
type Handler interface {
    ServeHTTP(ResponseWriter, *Request)
}

// ServeMux 是模板方法模式的实现
func (mux *ServeMux) ServeHTTP(w ResponseWriter, r *Request) {
    // 1. 解析请求路径
    // 2. 查找匹配的 handler
    // 3. 调用 handler.ServeHTTP(w, r)（变化点）
    h, _ := mux.Handler(r)
    h.ServeHTTP(w, r)
}

// 用法：业务方实现 ServeHTTP
type MyHandler struct{}

func (MyHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
}

http.ListenAndServe(":8080", MyHandler{})
```

net/http 是模板方法：ServeMux 处理路由分发，业务方只实现 ServeHTTP。

## TypeScript：Abstract Class

```typescript
abstract class DataExporter {
    // 模板方法：定义导出流程
    async export(data: any[]): Promise<void> {
        const formatted = this.format(data);
        await this.beforeWrite?.(formatted);
        await this.write(formatted);
        await this.afterWrite?.();
    }

    // 抽象步骤：子类必须实现
    protected abstract format(data: any[]): string;

    // 变化点：子类可覆盖
    protected async write(content: string): Promise<void> {
        await fs.writeFile('export.txt', content);
    }

    // 钩子方法：默认空实现，子类可选覆盖
    protected async beforeWrite?(content: string): Promise<void>;
    protected async afterWrite?(): Promise<void>;
}

// CSV 导出
class CSVExporter extends DataExporter {
    protected format(data: any[]) {
        if (data.length === 0) return '';
        const headers = Object.keys(data[0]).join(',');
        const rows = data.map(d => Object.values(d).join(','));
        return [headers, ...rows].join('\n');
    }
}

// JSON 导出
class JSONExporter extends DataExporter {
    protected format(data: any[]) {
        return JSON.stringify(data, null, 2);
    }

    protected async write(content: string) {
        await fs.writeFile('export.json', content);
    }
}

// 用法
const exporter: DataExporter = new CSVExporter();
await exporter.export([{ name: 'Alice', age: 25 }, { name: 'Bob', age: 30 }]);
```

## 与 Strategy 区别

| | Template Method | Strategy |
|---|---|---|
| 抽象层级 | 类继承（编译期） | 对象组合（运行期） |
| 算法骨架 | 不变（基类） | 整个算法都可换 |
| 实现方式 | 抽象方法 | 接口注入 |
| 数量 | 通常一对多（一父多子）| 一对多（一个抽象 N 个实现） |

## 适用边界

✅ **使用场景**：
- 多个类算法流程相同（spring JdbcTemplate / Servlet / Go http.Handler）
- 框架设计（让用户填钩子）
- 代码复用（公共流程抽父类）

❌ **避免场景**：
- 子类完全重写父类（违反模板初衷）
- 继承层级过深（> 3 层）
- 子类与父类耦合过紧（用组合替代）

🔄 **替代方案**：
- **Strategy**：运行期切换算法（更灵活）
- **回调函数**：把步骤作为参数传入
- **Pipeline**：数据流处理

💡 **最佳实践**：
- 模板方法应该在父类中（final 修饰）
- 抽象步骤用 `abstract` 修饰
- 钩子方法（hook）给默认实现（避免子类必须覆盖）
- 优先用组合（Strategy）而非继承
