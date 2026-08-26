---
title: God Object 上帝对象
description: 症状 + 病因 + 药方 + 检测工具 + 重构案例
---

# God Object 上帝对象

## 症状

```java
// 一个类 5000+ 行，承担一切职责
public class UserManager {
    public User createUser(...) { /* 50 行 */ }
    public void sendEmail(...) { /* 100 行 */ }
    public Order processOrder(...) { /* 200 行 */ }
    public Report generateReport(...) { /* 300 行 */ }
    public void exportCSV(...) { /* 150 行 */ }
    public void auditLog(...) { /* 80 行 */ }
    public void validateInput(...) { /* 60 行 */ }
    public void updateCache(...) { /* 90 行 */ }
    // ... 30+ 个职责
}
```

**典型表现**：
1. **类行数 > 1000**（甚至 5000+）
2. **字段 > 30 个**（各种状态）
3. **方法 > 50 个**（什么都能干）
4. **依赖 > 20 个**（所有服务都依赖）
5. **任何改动都会影响这个类**
6. **新人不敢改这个类**（怕踩雷）

## 病因

1. **「这个类刚好能装下这些功能」**
   - 早期业务简单，后来塞功能

2. **缺少职责拆分意识（违反 SRP）**
   - 一个类应该有且只有一个变更理由

3. **工期压力下"先这样吧"**
   - 「先把这个功能加到这个类，下次再拆」

4. **错误地把"共享状态"作为聚合理由**
   - 多个功能用同一个字段 → 全塞一个类

5. **代码审查不到位**
   - 没人问"这个方法为什么在这个类"

6. **没有架构守护**
   - 没有 lint / SonarQube 等工具限制类大小

## 药方

## 1. 按职责拆分（SRP）

```java
// 拆分前
class UserManager { /* 5000 行 */ }

// 拆分后
class UserService {          // 用户 CRUD
    public User create(UserRequest req) { /* ... */ }
    public User findById(long id) { /* ... */ }
}

class EmailService {         // 邮件发送
    public void sendWelcomeEmail(User u) { /* ... */ }
}

class OrderService {         // 订单处理
    public Order createOrder(OrderRequest req) { /* ... */ }
}

class ReportService {        // 报表生成
    public Report generateReport(ReportCriteria c) { /* ... */ }
}

class CsvExporter {          // CSV 导出
    public byte[] export(List<Report> reports) { /* ... */ }
}

class AuditLogger {          // 审计日志
    public void log(String action, Object data) { /* ... */ }
}
```

## 2. 组合优于继承（Facade）

```java
// 用 Facade 模式对外提供统一接口（兼容旧 API）
class UserFacade {
    private final UserService userService;
    private final EmailService emailService;
    private final AuditLogger auditLogger;

    public User createUser(UserRequest req) {
        var user = userService.create(req);
        emailService.sendWelcomeEmail(user);
        auditLogger.log("user.created", user);
        return user;
    }
}
```

## 3. 定期审视

- 每月 review 类行数排行（`cloc` / `SonarQube`）
- 把超长类列入重构清单
- 季度重构 sprint（专门拆上帝类）

## 检测工具

## SonarQube

```
Rule: Class size (cognitive complexity, lines of code)
Threshold: 
  - Critical: > 1000 lines / cognitive complexity > 50
  - Major: > 500 lines
```

## CodeScene（识别 Hotspot）

```bash
# 找出"高频修改 + 高复杂度"的类
codescene analyze --repo-path . --complexity-threshold 50 --change-frequency-threshold 20
```

## ESLint（JavaScript / TypeScript）

```json
{
  "rules": {
    "max-lines": ["warn", { "max": 500, "skipComments": true }],
    "max-lines-per-function": ["warn", { "max": 100 }],
    "complexity": ["warn", 20]
  }
}
```

## Java 自定义 ArchUnit

```java
@ArchTest
static final ArchRule no_god_classes = classes()
    .that().areNotEnums()
    .and().areNotInterfaces()
    .should(notHaveTooManyMethods(50))
    .because("Classes with > 50 methods violate SRP (Single Responsibility Principle)");

@ArchTest
static final ArchRule no_god_classes_by_lines = classes()
    .should(new ArchCondition<JavaClass>("have less than 1000 lines") {
        public void check(JavaClass clazz, ConditionEvents events) {
            int lines = clazz.getSourceCode().map(s -> s.split("\n").length).orElse(0);
            if (lines > 1000) {
                events.add(SimpleConditionEvent.violated(clazz, clazz.getName() + " has " + lines + " lines"));
            }
        }
    });
```

## 重构案例：UserService 拆分

假设 UserService 有 30 个方法，拆分为：

```text
UserService (300 行)
├── createUser / updateUser / deleteUser
├── findById / findByEmail
└── (核心 CRUD)

EmailService (200 行)
├── sendWelcomeEmail
├── sendPasswordReset
└── sendNotification

AuthService (200 行)
├── login / logout
├── refreshToken
└── validateToken

UserProfileService (150 行)
├── updateProfile
├── uploadAvatar
└── getProfile

AuditService (100 行)
└── logUserAction
```

**拆分原则**：
1. 按业务职责（CRUD / 邮件 / 认证）
2. 按变更频率（高频 vs 低频分开）
3. 按依赖关系（A 依赖 B，A 不知道 C）

**风险控制**：
1. 拆分前写好测试（覆盖所有方法）
2. 一次只拆一个职责（避免一次大爆炸）
3. 拆分后保持兼容（用 Facade 维持旧 API）
4. 灰度发布（10% → 50% → 100%）

## 适用边界

✅ **识别信号**：
- 行数 > 1000 / 方法 > 50 / 依赖 > 20
- 任何改动都要碰这个类
- 新人入职看这个类需要 1 周

❌ **避免拆分**：
- 类行数 < 500（拆得过细反而难维护）
- 业务极简（拆分成本 > 收益）
- 没有足够测试覆盖（拆完容易出 bug）

💡 **预防**：
- **CI 检查**：SonarQube / ArchUnit 拦截超长类
- **code review**：每个 PR 问"这个方法真的属于这个类？"
- **架构守护**：每个 Service / Manager / Util 都有限定职责
- **文档先行**：每个类写明"我是谁，我能做什么"（不要让我猜）


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
<!-- auto-enrich:do-not-edit -->
