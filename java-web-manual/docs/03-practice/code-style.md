---
title: 代码规范
date: 2026-08-15  # date-auto-injected
---

# 代码规范

统一的代码风格降低阅读成本，提高团队协作效率。

## 命名规范

| 元素 | 规则 | 示例 |
|---|---|---|
| 类名 | 大驼峰，名词 | UserService, OrderController |
| 方法名 | 小驼峰，动词 | getUserById, createOrder |
| 变量名 | 小驼峰，名词 | orderList, userName |
| 常量 | 全大写+下划线 | MAX_RETRY_COUNT |
| 包名 | 全小写 | com.example.order |
| 枚举 | 大驼峰 | OrderStatus.PENDING |

## 方法规范

```java
// ❌ 方法太长，职责不清
public void processOrder(Order order) {
    // 100+ 行代码...
}

// ✅ 拆分为小方法
public void processOrder(Order order) {
    validateOrder(order);
    calculatePrice(order);
    deductStock(order);
    sendNotification(order);
}
```

<div class="kg-note kg-note-tip">
<strong>单一职责</strong>：一个方法只做一件事。<br/>
<strong>方法长度</strong>：超过 50 行就应考虑拆分。<br/>
<strong>参数个数</strong>：超过 4 个参数应封装为 DTO。
</div>

## 目录结构规范

```
com.example.project
├── controller/         # REST 接口
├── service/            # 业务接口
│   └── impl/           # 业务实现
├── mapper/             # MyBatis Mapper
├── entity/             # 数据库实体
├── dto/                # 请求体（入参）
├── vo/                 # 响应体（出参）
├── config/             # Spring 配置
├── common/             # 公共类
│   ├── exception/      # 异常定义
│   ├── result/         # 统一响应
│   └── util/           # 工具类
└── enums/              # 枚举
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="code-style" :height="400" />
