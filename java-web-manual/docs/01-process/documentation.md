---
title: 文档沉淀
date: 2026-08-15  # date-auto-injected
---

# 文档沉淀

好的文档让团队协作更高效，新人上手更快，自己三个月后还能看懂自己的代码。

## 文档体系

| 文档类型 | 内容 | 放哪里 |
|---|---|---|
| 接口文档 | API 列表、入参出参 | Swagger/Knife4j 自动生成 |
| 设计文档 | 架构设计、技术方案 | Wiki / 语雀 / Notion |
| 操作手册 | 部署步骤、常见问题 | 运维 Wiki |
| 知识库 | 业务知识、踩坑记录 | 团队知识库 |
| 代码注释 | 关键逻辑说明 | 代码中 |

## 接口文档自动化

```java
@Api(tags = "订单管理")
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @ApiOperation("创建订单")
    @PostMapping
    public Result<OrderVO> create(@Valid @RequestBody OrderCreateDTO dto) {
        return Result.success(orderService.create(dto));
    }
}
```

访问 `http://localhost:8080/doc.html` 即可在线查看和调试所有接口。

## 设计文档模板

```markdown
# [功能名称] 技术设计文档

## 1. 背景与目标
## 2. 架构设计
## 3. 数据库设计（ER图 + DDL）
## 4. 接口设计（URL + 入参出参）
## 5. 关键流程图/时序图
## 6. 风险评估
## 7. 上线计划
## 8. 附录（参考链接、会议记录）
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="documentation" :height="400" />
