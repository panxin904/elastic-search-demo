---
title: 安全实践
date: 2026-08-15  # date-auto-injected
---

# 安全实践

安全是底线。一个漏洞可能导致数据泄露、资金损失、法律风险。

## 常见攻击与防御

### SQL 注入

```java
// ❌ 危险：字符串拼接
@Select("SELECT * FROM t_user WHERE username = '${username}'")

// ✅ 安全：参数化查询
@Select("SELECT * FROM t_user WHERE username = #{username}")
```

### XSS（跨站脚本）

```java
// 后端对用户输入做 HTML 转义
String safe = HtmlUtils.htmlEscape(userInput);

// 或使用 JSON 序列化时全局配置
@JsonComponent
public class XssStringSerializer extends JsonSerializer<String> {
    @Override
    public void serialize(String value, JsonGenerator gen, ...) {
        gen.writeString(HtmlUtils.htmlEscape(value));
    }
}
```

### CSRF（跨站请求伪造）

- 前后端分离架构中，使用 Token 认证天然防 CSRF
- Cookie 设置 SameSite=Strict

### 敏感信息保护

```java
// ❌ 绝不在日志打印
log.info("用户登录: password={}", password);

// ✅ 日志脱敏
log.info("用户登录: username={}, password=******", username);

// 配置文件加密
spring.datasource.password=${JASYPT_ENCRYPTED_PASSWORD}

// 接口响应脱敏
@JsonSerialize(using = PhoneDesensitizeSerializer.class)
private String phone;  // 138****1234
```

## 认证与授权

| 组件 | 用途 |
|---|---|
| Spring Security | 认证授权框架 |
| JWT | 无状态 Token |
| OAuth2 | 第三方登录 |
| RBAC | 基于角色的权限控制 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="security" :height="400" />
