---
title: 工厂模式
date: 2026-08-15  # date-auto-injected
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
