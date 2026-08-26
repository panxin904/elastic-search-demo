---
title: Bridge 桥接模式
description: 抽象与实现分离 + JDBC Driver + 跨平台 UI + 多维度独立变化
---

# Bridge 桥接模式

## 核心问题

一个类有**两个独立变化的维度**（如：形状 + 颜色 / 数据库 + 协议 / 平台 + UI 组件），如果用继承会让类层次爆炸。

**举例**：
- 形状（圆形 / 矩形 / 三角形）× 颜色（红 / 蓝 / 绿）= 9 个类
- 数据库（MySQL / PG / Oracle）× 协议（Native / HTTP / gRPC）= 9 个类
- 平台（macOS / Windows / Linux）× 组件（按钮 / 文本框 / 菜单）= 9 个类

## 核心思想

将「抽象」与「实现」分离，使它们都可以独立变化。用「组合」代替「继承」。

**与 Strategy / Adapter 的区别**：
| | Bridge | Strategy | Adapter |
|---|---|---|---|
| 目的 | 抽象与实现解耦 | 算法族切换 | 接口兼容 |
| 数量 | 多个实现 × 多个抽象 | 1 个抽象 × N 个算法 | 单向适配 |
| 设计阶段 | 从一开始 | 运行期替换 | 后期集成 |

## 实战：JDBC Driver

JDBC 是 Bridge 模式的教科书例子：

```java
// 抽象：JDBC API（java.sql.*）
public interface Connection {
    Statement createStatement() throws SQLException;
    PreparedStatement prepareStatement(String sql) throws SQLException;
}

// 实现：各个数据库厂商
// com.mysql.cj.jdbc.JdbcConnection implements Connection
// org.postgresql.PgConnection implements Connection
// oracle.jdbc.OracleConnection implements Connection

// 桥接器：DriverManager
public class DriverManager {
    private static final CopyOnWriteArrayList<DriverInfo> registeredDrivers = new CopyOnWriteArrayList<>();

    public static Connection getConnection(String url, String user, String password) {
        // 遍历注册的 Driver，找到能处理这个 URL 的
        for (DriverInfo di : registeredDrivers) {
            if (di.driver.matchesURL(url)) {
                return di.driver.connect(url, new Properties() {{ put("user", user); put("password", password); }});
            }
        }
        throw new SQLException("No suitable driver");
    }
}

// 客户端：只依赖 JDBC API
Connection conn = DriverManager.getConnection(
    "jdbc:mysql://localhost:3306/mydb", "root", "secret");
```

**抽象**（Connection）和**实现**（MySQL / PG / Oracle）通过 `DriverManager` 桥接，两边都能独立扩展而不互相影响。

## 实战：跨平台 UI

```java
// 实现层级（平台）
public interface WindowImpl {
    void drawText(String text);
    void drawRect(int x, int y, int w, int h);
    void open();
}

public class MacWindowImpl implements WindowImpl {
    @Override public void drawText(String text) { /* 调用 Cocoa */ }
    @Override public void drawRect(int x, int y, int w, int h) { /* NSRect */ }
    @Override public void open() { /* [NSWindow makeKeyAndOrderFront] */ }
}

public class WindowsWindowImpl implements WindowImpl {
    @Override public void drawText(String text) { /* 调用 Win32 GDI */ }
    // ...
}

// 抽象层级（窗口）
public abstract class Window {
    protected WindowImpl impl;  // 桥接
    public Window(WindowImpl impl) { this.impl = impl; }

    public void draw() {
        impl.open();
        impl.drawRect(0, 0, 100, 100);
    }
}

public class Dialog extends Window {
    public Dialog(WindowImpl impl) { super(impl); }

    public void drawDialog() {
        impl.drawText("Are you sure?");
        draw();
    }
}

// 客户端
Window mac = new Dialog(new MacWindowImpl());
Window win = new Dialog(new WindowsWindowImpl());
```

新增平台（Linux X11）只需要新增 `X11WindowImpl`，不需要改任何 Window 类。

## TypeScript 实现

```typescript
// 实现层（渲染后端）
interface Renderer {
    renderCircle(radius: number): string;
    renderSquare(size: number): string;
}

class VectorRenderer implements Renderer {
    renderCircle(radius: number) {
        return `Drawing a circle of radius ${radius} using vectors`;
    }
    renderSquare(size: number) {
        return `Drawing a square of size ${size} using vectors`;
    }
}

class RasterRenderer implements Renderer {
    renderCircle(radius: number) {
        return `Drawing a circle of radius ${radius} using pixels`;
    }
    renderSquare(size: number) {
        return `Drawing a square of size ${size} using pixels`;
    }
}

// 抽象层（形状）
abstract class Shape {
    protected renderer: Renderer;
    constructor(renderer: Renderer) { this.renderer = renderer; }
    abstract draw(): string;
}

class Circle extends Shape {
    constructor(private radius: number, renderer: Renderer) { super(renderer); }
    draw() {
        return this.renderer.renderCircle(this.radius);
    }
}

class Square extends Shape {
    constructor(private size: number, renderer: Renderer) { super(renderer); }
    draw() {
        return this.renderer.renderSquare(this.size);
    }
}

// 用法
const circle = new Circle(5, new VectorRenderer());
console.log(circle.draw());  // "Drawing a circle of radius 5 using vectors"
```

新增形状（Triangle / Pentagon）只需扩展抽象层；新增渲染（SVG / Canvas）只需扩展实现层——**两层独立变化**。

## 适用边界

✅ **使用场景**：
- 两个独立变化的维度（形状×颜色 / 数据库×协议 / 平台×组件）
- 抽象和实现都要独立扩展
- 避免类层次爆炸（继承层级 > 3）

❌ **避免场景**：
- 只有一维变化（用继承就够了）
- 抽象与实现耦合紧密（拆不开）
- 业务规模小（不值得双层抽象）

🔄 **与 Adapter 区别**：
- **Adapter**：已有接口不兼容，后期适配
- **Bridge**：设计时就知道「抽象和实现」会独立变化，主动解耦

💡 **最佳实践**：
- 抽象层持有实现层的引用（组合）
- 实现层接口要稳定（一旦确定不改）
- 抽象层和实现层通过容器（DI / ServiceLoader）装配


<!-- auto-enrich:do-not-edit -->

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
