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

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="factory-pattern" :height="400" />
