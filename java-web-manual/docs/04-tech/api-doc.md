---
title: 接口文档
date: 2026-08-15  # date-auto-injected
---

# 接口文档（Swagger / Knife4j）

自动生成在线 API 文档，支持在线调试，前端不用再对着静态文档开发。

## Knife4j（推荐）

Knife4j 是 Swagger 的增强版，UI 更好看，功能更丰富。

```xml
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-openapi3-jakarta-spring-boot-starter</artifactId>
    <version>4.4.0</version>
</dependency>
```

## 使用

```java
@Configuration
public class Knife4jConfig {
    @Bean
    public OpenAPI openAPI() {
        return new OpenAPI()
            .info(new Info()
                .title("订单系统 API")
                .version("v1.0")
                .description("订单管理系统接口文档"));
    }
}

@Tag(name = "订单管理")
@RestController
@RequestMapping("/api/orders")
public class OrderController {

    @Operation(summary = "创建订单")
    @PostMapping
    public Result<OrderVO> create(@Valid @RequestBody OrderCreateDTO dto) {
        return Result.success(orderService.create(dto));
    }

    @Operation(summary = "查询订单详情")
    @Parameter(name = "id", description = "订单ID", required = true)
    @GetMapping("/{id}")
    public Result<OrderVO> getById(@PathVariable Long id) {
        return Result.success(orderService.getById(id));
    }
}

@Data
@Schema(description = "订单创建请求")
public class OrderCreateDTO {
    @Schema(description = "商品ID", required = true, example = "1")
    @NotNull
    private Long productId;

    @Schema(description = "购买数量", required = true, example = "2")
    @Min(1) @Max(100)
    private Integer quantity;

    @Schema(description = "备注", example = "尽快发货")
    private String remark;
}
```

访问 `http://localhost:8080/doc.html` 即可看到在线文档。

## Swagger 常用注解

| 注解 | 作用 |
|---|---|
| @Tag | Controller 分类标签 |
| @Operation | 接口说明 |
| @Parameter | 参数说明 |
| @Schema | DTO 字段说明 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="api-doc" :height="400" />
