---
title: 代码评审
---

# 代码评审（Code Review）

代码评审是保证代码质量的最后一道防线，也是团队知识传递的重要途径。

## CR 关注点

### 1. 逻辑正确性

```java
// ❌ 问题：空指针风险
public void process(Order order) {
    String name = order.getUser().getName(); // user 可能为 null
}

// ✅ 修复：判空处理
public void process(Order order) {
    if (order == null || order.getUser() == null) {
        throw new BusinessException("订单信息不完整");
    }
    String name = order.getUser().getName();
}
```

### 2. 性能

```java
// ❌ 问题：循环内查数据库 (N+1 问题)
for (Long id : ids) {
    User user = userMapper.selectById(id);
}

// ✅ 修复：批量查询
List<User> users = userMapper.selectBatchIds(ids);
Map<Long, User> userMap = users.stream()
    .collect(Collectors.toMap(User::getId, Function.identity()));
```

### 3. 安全性

| 检查点 | 说明 |
|---|---|
| SQL 注入 | 是否使用了参数化查询（MyBatis #{} vs ${}） |
| XSS | 用户输入是否做了转义 |
| 敏感信息 | 日志是否打印了密码、token、手机号 |
| 权限 | 接口是否有认证鉴权 |
| 越权 | 是否校验了数据归属（用户只能操作自己的数据） |

### 4. 可维护性

| 检查点 | 说明 |
|---|---|
| 命名 | 类名、方法名、变量名是否表意清晰 |
| 方法长度 | 一个方法是否超过 50 行 |
| 圈复杂度 | if/else 嵌套是否超过 3 层 |
| 魔法值 | 硬编码数字/字符串是否提取为常量/枚举 |
| 注释 | 复杂逻辑是否有注释说明为什么这么写 |

## CR 流程

```
开发者提交 MR/PR → 指定 Reviewer → Reviewer 审查
    ↓                                        ↓
  修改代码 ←────────────── 有问题 ←──────────┘
    ↓
  通过 → 合并到目标分支
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="code-review" :height="400" />
