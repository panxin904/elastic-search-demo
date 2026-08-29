---
title: Abstract Factory 抽象工厂模式
date: 2026-08-15  # date-auto-injected
description: 一族相关对象的创建 + 主题切换 + UI 组件库 / 数据库 driver 族 / Spring ApplicationContext
---

# Abstract Factory 抽象工厂模式

## 核心问题

需要创建「一组相关或相互依赖的对象家族」，而不是单一对象。

**真实场景**：
- UI 组件库（Ant Design / Material UI）：所有组件风格必须统一，不能混搭
- 数据库 driver（MySQL 全家桶 / Oracle 全家桶）：Connection + Statement + ResultSet 必须配套
- 跨平台 GUI（macOS / Windows / Linux）：按钮 + 文本框 + 菜单风格必须统一

## 核心思想

提供一个接口，用于创建**相关对象的家族**，而不需要指定具体类。每个具体工厂负责一个完整产品族。

**与 Factory Method 的区别**：
| | Factory Method | Abstract Factory |
|---|---|---|
| 抽象层级 | 一个产品的创建 | 一族产品的创建 |
| 方法数 | 1 个抽象方法 | 多个抽象方法 |
| 关注点 | 类延迟实例化 | 主题/族切换

## 多语言实现

## Java：UI 组件族

```java
interface UIFactory {
    Button createButton();
    Checkbox createCheckbox();
    TextField createTextField();
}

class MaterialUIFactory implements UIFactory {
    public Button createButton() { return new MaterialButton(); }
    public Checkbox createCheckbox() { return new MaterialCheckbox(); }
    public TextField createTextField() { return new MaterialTextField(); }
}

class AntDesignUIFactory implements UIFactory {
    public Button createButton() { return new AntdButton(); }
    public Checkbox createCheckbox() { return new AntdCheckbox(); }
    public TextField createTextField() { return new AntdTextField(); }
}

// 客户端：只依赖 UIFactory 抽象
class Form {
    private final UIFactory factory;
    Form(UIFactory factory) { this.factory = factory; }

    void render() {
        Button btn = factory.createButton();
        Checkbox cb = factory.createCheckbox();
        // ... 渲染到屏幕
    }
}

// 运行时切换主题
Form materialForm = new Form(new MaterialUIFactory());
Form antdForm = new Form(new AntDesignUIFactory());
```

## TypeScript：跨主题 UI

```typescript
interface UIFactory {
    createButton(): Button;
    createInput(): Input;
    createCard(): Card;
}

class ChakraUIFactory implements UIFactory {
    createButton() { return new ChakraButton(); }
    createInput() { return new ChakraInput(); }
    createCard() { return new ChakraCard(); }
}

class Dashboard {
    constructor(private factory: UIFactory) {}
    render() {
        this.factory.createCard().render();
        this.factory.createButton().render();
    }
}

new Dashboard(new ChakraUIFactory()).render();
```

## 实战：JDBC 全家桶

JDBC 是抽象工厂的经典案例：

```java
// JDBC 抽象产品
public interface Connection {
    Statement createStatement();
    PreparedStatement prepareStatement(String sql);
}

public interface Statement {
    ResultSet executeQuery(String sql) throws SQLException;
}

// MySQL 实现
// com.mysql.cj.jdbc.JdbcConnection implements Connection
// com.mysql.cj.jdbc.JdbcStatement implements Statement

// PG 实现
// org.postgresql.PgConnection implements Connection
// org.postgresql.PgStatement implements Statement

// 客户端只依赖 JDBC API
Connection conn = DriverManager.getConnection(url, user, pwd);
Statement stmt = conn.createStatement();
ResultSet rs = stmt.executeQuery("SELECT ...");
```

DriverManager 内部维护一组 `Driver`，每个 Driver 就是一个具体工厂。

## 与 Spring 的关系

```java
// Spring ApplicationContext 是抽象工厂
public interface ApplicationContext {
    BeanDefinition getBeanDefinition(String name);
    Object getBean(String name);
    // ... 几十个方法
}

// ClassPathXmlApplicationContext / AnnotationConfigApplicationContext
// 是具体工厂（XML 配置 vs 注解配置）
```

每个 ApplicationContext 都能创建一族相关 bean（你的 `@Service` + `@Repository` + `@Configuration`）。

## 适用边界

✅ **使用场景**：
- 多主题 UI（设计系统切换）
- 跨数据库 driver 族
- 跨操作系统 GUI 工具包
- 跨消息中间件适配（Kafka 族 / RabbitMQ 族）

❌ **避免场景**：
- 只有一个产品族（直接用具体类）
- 产品族经常变化（抽象工厂难以演进）
- 业务方不需要切换主题（增加抽象成本）

🔄 **替代方案**：
- **DI 容器**（推荐）：Spring 自动按配置装配一族 bean
- **Strategy + Builder**：每个产品独立选择
- **Prototype**：运行时克隆现有族

💡 **最佳实践**：
- 抽象工厂的接口要稳定（一旦确定不轻易改）
- 产品族之间要强一致（不能出现 Material 按钮 + Antd 卡片）
- 配合 DI 使用：客户端通过配置注入具体工厂
