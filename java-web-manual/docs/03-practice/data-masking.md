---
title: 数据脱敏
date: 2026-08-15  # date-auto-injected
---

# 数据脱敏

对手机号、身份证、银行卡等敏感信息进行部分遮蔽处理。

## 🛠️ 数据脱敏方案

**静态脱敏**：DB 导出前就脱敏（备份、日志、BI 报表场景）。优点：调用方无感知。

**动态脱敏**：查询时按用户权限脱敏（金融 / 医疗合规场景）。常用 `@JsonSerialize` + 自定义 Serializer 屏蔽敏感字段。

**常见脱敏规则**：
- 手机号 `138****1234`
- 身份证 `110101********1234`
- 银行卡 `**** **** **** 1234`
- 邮箱 `abc***@gmail.com`

**合规要求**：GDPR / 个人信息保护法（PIPL）要求"最小必要原则"+ 加密存储 + 审计日志。

## 脱敏规则

| 类型 | 规则 | 示例 |
|---|---|---|
| 手机号 | 保留前3后4 | 138****1234 |
| 身份证 | 保留前4后4 | 3301**********1234 |
| 银行卡 | 保留后4 | ****1234 |
| 姓名 | 保留姓，名用* | 张** |
| 邮箱 | 用户名部分打* | t***@qq.com |

## Jackson 序列化脱敏

```java
@Target(ElementType.FIELD)
@Retention(RetentionPolicy.RUNTIME)
@JacksonAnnotationsInside
@JsonSerialize(using = DesensitizeSerializer.class)
public @interface Desensitize {
    DesensitizeType type();
}

public enum DesensitizeType {
    PHONE,      // 手机号
    ID_CARD,    // 身份证
    BANK_CARD,  // 银行卡
    NAME,       // 姓名
    EMAIL       // 邮箱
}

public class DesensitizeSerializer extends JsonSerializer<String> {
    @Override
    public void serialize(String value, JsonGenerator gen, ...) {
        Desensitize annotation = ...;
        String result = switch (annotation.type()) {
            case PHONE -> value.replaceAll("(\\d{3})\\d{4}(\\d{4})", "$1****$2");
            case ID_CARD -> value.replaceAll("(\\d{4})\\d{10}(\\d{4})", "$1****$2");
            default -> "****";
        };
        gen.writeString(result);
    }
}
```

## 使用

```java
@Data
public class UserVO {
    private Long id;
    private String username;

    @Desensitize(type = DesensitizeType.PHONE)
    private String phone;  // 自动脱敏：138****1234
}
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="data-masking" :height="400" />
