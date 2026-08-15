---
title: 模板方法模式
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

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="template-method" :height="400" />
