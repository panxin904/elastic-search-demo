---
title: Big Ball of Mud 大泥球
description: 症状 + 病因 + 药方 + DDD 限界上下文 + 架构守护
---

# Big Ball of Mud 大泥球

## 症状

```java
// Util 类什么都往里塞
public class Util {
    public static String formatDate(Date d) { /* ... */ }
    public static User parseUserJson(String s) { /* ... */ }
    public static BigDecimal calcTax(BigDecimal amount) { /* ... */ }
    public static String generateUUID() { /* ... */ }
    public static void sendEmail(String to, String subject) { /* ... */ }
    public static boolean validatePhone(String phone) { /* ... */ }
    // 200+ 方法，无业务分类
}

// Helper1 / Helper2 / NewHelper / Util2 / Manager1
// 业务逻辑分散在 Controller / Service / Util / Helper 等 5+ 个地方
```

**典型表现**：
1. 没有模块边界（任何文件都能 import 任何文件）
2. 命名混乱（`Util`、`Helper`、`Manager1`、`NewService`）
3. 业务逻辑分散（同一个功能在 5+ 个文件）
4. 改一行代码不知道会破坏什么
5. 测试覆盖率极低（不知道从哪里开始测）
6. 新人入职 3 个月才能上手

## 病因

1. **没有架构规范**
   - 谁都能加新模块 / 新文件
   - 没有「包结构」「类命名」规范

2. **缺少 code review**
   - 业务赶进度，无 review
   - 烂代码越积越多

3. **业务变更频繁，代码跟着打补丁**
   - 「修一个 bug 加一个 if-else」

4. **没有架构守护（ArchUnit / Checkstyle）**
   - 工具无法自动拦截违规

5. **团队分批加入，新人风格各异**
   - 没人统一风格

6. **文档缺失 / 过时**
   - 没有「架构图」「包结构说明」

## 药方

## 1. DDD 限界上下文（按业务拆分）

```text
用户域 (user-context)
├── UserController
├── UserService
├── UserRepository
├── User (领域模型)
└── UserEvents

订单域 (order-context)
├── OrderController
├── OrderService
├── OrderRepository
├── Order (领域模型)
└── OrderEvents

支付域 (payment-context)
├── PaymentController
├── PaymentService
├── PaymentRepository
├── Payment (领域模型)
└── PaymentEvents

公共域 (common)
├── DateUtil          (只做日期格式化)
├── JsonUtil          (只做 JSON 解析)
├── TaxCalculator     (只做税计算)
└── EmailValidator    (只做邮箱校验)
```

**关键**：每个域只暴露 API，通过事件或 RPC 跨域通信。

## 2. 命名规范

```java
// ❌ 混乱命名
public class Util { /* 什么都干 */ }
public class Helper { /* 又一个什么都干 */ }
public class Manager1 { /* 业务 1 */ }
public class NewService { /* 业务 2 */ }

// ✅ 语义化命名
public class DateFormatter { /* 只做日期格式化 */ }
public class UserJsonParser { /* 只做 User JSON 解析 */ }
public class TaxCalculator { /* 只计算税 */ }
public class UserService { /* 只做用户业务 */ }
public class OrderProcessor { /* 只处理订单 */ }
```

每个类名要回答「我是谁」+「我能做什么」。

## 3. 架构守护

```java
// ArchUnit：禁止 Util 类混乱
@ArchTest
static final ArchRule no_util_classes = noClasses()
    .that().haveSimpleName("Util")
    .or().haveSimpleName("Helper")
    .or().haveSimpleName("Manager")
    .because("Util/Helper/Manager often become God classes");

// 禁止跨域依赖（订单域不能直接访问支付域内部类）
@ArchTest
static final ArchRule bounded_contexts = noClasses()
    .that().resideInAPackage("com.example.order..")
    .should().dependOnClassesThat().resideInAPackage("com.example.payment.internal..")
    .because("Order context can only depend on Payment API, not internal");

// Service 类必须有 Service 后缀
@ArchTest
static final ArchRule service_naming = classes()
    .that().areAnnotatedWith(Service.class)
    .should().haveSimpleNameEndingWith("Service");
```

## 工具与流程

## Checkstyle

```xml
<module name="MethodCount">
    <property name="maxTotal" value="30"/>
</module>

<module name="FileLength">
    <property name="max" value="500"/>
</module>

<module name="ClassFanOutComplexity">
    <property name="max" value="20"/>
</module>
```

## SonarQube

```yaml
sonar:
  qualityGate:
    conditions:
      - metric: cognitive_complexity
        operator: GT
        value: 50
        resource: file
      - metric: file_complexity
        operator: GT
        value: 200
```

## CodeScene

```bash
# 找出"代码复杂度 + 修改频率"高的 Hotspot
codescene analyze --repo-path . --complexity-threshold 50
# 输出：Top 10 Hotspots（这些文件优先重构）
```

## 依赖图

```bash
# dependency-cruiser（JavaScript / TypeScript）
depcruise --validate .dependency-cruiser.json src/

# IntelliJ IDEA：右键 → Diagrams → Show Dependencies
```

## 文档先行

```markdown
# docs/architecture.md

## 模块结构
- user-context: 用户管理
- order-context: 订单管理
- payment-context: 支付管理

## 跨域通信
- order-context 通过 EventBus 发布 OrderCreatedEvent
- payment-context 订阅 OrderCreatedEvent，触发支付

## 命名规范
- *Service: 业务编排
- *Repository: 数据访问
- *Controller: HTTP 接口
- *Factory: 创建逻辑
- *Validator: 校验
- 禁止 Util / Helper / Manager 这种「什么都干」的命名
```

## 重构案例：拆 Util

## 重构前

```java
public class CommonUtil {
    // 100+ 方法
    public static String formatDate(Date d) { /* ... */ }
    public static User parseUserJson(String s) { /* ... */ }
    public static BigDecimal calcTax(BigDecimal amount, String region) { /* ... */ }
    public static String maskCardNo(String cardNo) { /* ... */ }
    public static boolean isValidEmail(String email) { /* ... */ }
    public static String generateOrderNo() { /* ... */ }
    public static String encryptPassword(String pwd) { /* ... */ }
    // ...
}
```

## 重构后

```text
common/
├── date/
│   └── DateFormatter.java          // 只做日期格式化
├── json/
│   ├── UserJsonParser.java
│   └── OrderJsonParser.java
├── tax/
│   └── TaxCalculator.java          // 只算税
├── crypto/
│   ├── CardMasker.java
│   └── PasswordEncryptor.java
├── validation/
│   ├── EmailValidator.java
│   └── PhoneValidator.java
└── id/
    └── OrderNoGenerator.java
```

每个类职责单一，行数 < 100，新人 5 分钟能看懂。

## 适用边界

✅ **大泥球识别**：
- 新人入职 3 个月仍搞不清模块边界
- 任何改动都要碰 5+ 个文件
- 测试覆盖率 < 30%
- 「这代码谁写的」是高频问题

❌ **避免过度拆分**：
- 业务极简（< 10 个类）不需要 DDD
- 团队规模 < 5 人不需要复杂架构
- 性能极敏感（拆分增加网络开销）

💡 **最佳实践**：
- **架构文档**：每个项目维护一份 `ARCHITECTURE.md`
- **code review**：每个 PR 检查「这代码放对地方了吗」
- **架构守护**：ArchUnit / Checkstyle 自动拦截
- **季度重构**：把大泥球列入技术债
- **培训优先**：新人入职讲架构（不是讲语言）
