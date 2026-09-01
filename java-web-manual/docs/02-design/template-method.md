---
title: 模板方法模式
date: 2026-08-15  # date-auto-injected
---

# 模板方法模式

在父类中定义算法骨架，子类实现具体步骤。

## Java Web 中的应用

- **BaseService**：通用 CRUD 模板
- **JdbcTemplate / RestTemplate**：连接管理、异常处理已封装
- **数据导出**：查询数据 → 格式化 → 写入文件（子类实现格式化）

## 代码示例

```java
public abstract class AbstractExportService<T> {
    // 模板方法（final 防止子类修改骨架）
    public final void export(HttpServletResponse response) {
        List<T> data = queryData();    // 子类实现
        formatAndWrite(data, response); // 子类实现
        logExport();                    // 公共逻辑
    }
    protected abstract List<T> queryData();
    protected abstract void formatAndWrite(List<T> data, HttpServletResponse response);
}
```

## 🛠️ 何时用模板方法

**使用场景**：业务流程**整体固定**，但某些步骤需要子类定制（如 Spring
`AbstractView.render()`、`JdbcTemplate`、`AbstractHandlerMethodMapping`）。

**与策略模式区别**：
- 模板方法：**继承**关系，子类覆写钩子方法（流程由父类控制）
- 策略模式：**组合**关系，运行时切换算法（流程由调用方控制）

**钩子方法（hook）vs 抽象方法：钩子有默认实现（子类可选择性覆写），抽象方法必须覆写。

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="template-method" :height="400" />


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
