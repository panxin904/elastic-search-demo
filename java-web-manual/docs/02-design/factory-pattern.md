---
title: 工厂模式
---

# 工厂模式

定义创建对象的接口，让子类决定实例化哪个类。

## Java Web 中的应用

- **Spring BeanFactory**：IoC 容器本身就是巨型工厂
- **SqlSessionFactory**：MyBatis 创建 SqlSession
- **ThreadPoolExecutor 工厂**：统一创建线程池

## 代码示例

```java
// 简单工厂
public class NotificationFactory {
    public static NotificationService create(String type) {
        return switch (type) {
            case "SMS" -> new SmsService();
            case "EMAIL" -> new EmailService();
            default -> throw new IllegalArgumentException();
        };
    }
}
```

## 🛠️ 何时用工厂模式

**使用场景**：创建逻辑较复杂（参数多 / 多种类型 / 需要缓存 / 需要单例管理），
或者**调用方不想关心具体类名**（依赖倒置 + 解耦）。

**不要用**：只有 1-2 个实现类，且创建逻辑简单（直接 `new`）。

**Spring 替代**：直接用 `@Component` + `@Autowired`，IoC 容器本身就是工厂，
业务代码不需要再写工厂类。

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="factory-pattern" :height="400" />
