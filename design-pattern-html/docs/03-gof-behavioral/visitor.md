---
title: Visitor 访问者模式
description: 不修改元素类增加新操作 + AST 处理 / 编译器 / 文件遍历 + Java ElementVisitor
---

# Visitor 访问者模式

## 核心问题

需要在**不修改元素类**的前提下，对一个复杂对象结构（树 / 集合）中的元素进行**多种不同的操作**。

**真实场景**：
- 编译器：遍历 AST 进行类型检查 / 求值 / 代码生成 / 优化
- 文件系统遍历：遍历所有文件做压缩 / 备份 / 病毒扫描
- Java 编译器 API：ElementVisitor 遍历 Java 元素
- HTML 解析：遍历 DOM 进行各种处理

## 核心思想

把「对元素的操作」从元素类中抽离出来，封装到 Visitor 类中。元素类提供 `accept(visitor)` 方法，让 visitor 来访问自己。

**关键点**：
- 元素类层次稳定（不变）
- 操作经常新增（用 Visitor 扩展）
- 通过**双重分派**实现：accept 调用 visitor 的 visit 方法

## TypeScript：AST 求值与打印

```typescript
interface Expr {
    accept<R>(visitor: ExprVisitor<R>): R;
}

interface ExprVisitor<R> {
    visitNumber(n: NumberExpr): R;
    visitBinary(b: BinaryExpr): R;
}

class NumberExpr implements Expr {
    constructor(public value: number) {}
    accept<R>(v: ExprVisitor<R>): R { return v.visitNumber(this); }
}

class BinaryExpr implements Expr {
    constructor(public op: '+' | '-', public left: Expr, public right: Expr) {}
    accept<R>(v: ExprVisitor<R>): R { return v.visitBinary(this); }
}

// 求值 visitor
class Evaluator implements ExprVisitor<number> {
    visitNumber(n: NumberExpr) { return n.value; }
    visitBinary(b: BinaryExpr) {
        const l = b.left.accept(this);
        const r = b.right.accept(this);
        return b.op === '+' ? l + r : l - r;
    }
}

// 打印 visitor
class Printer implements ExprVisitor<string> {
    visitNumber(n: NumberExpr) { return n.value.toString(); }
    visitBinary(b: BinaryExpr) {
        return `(${b.left.accept(this)} ${b.op} ${b.right.accept(this)})`;
    }
}

// 类型检查 visitor
class TypeChecker implements ExprVisitor<'number' | 'error'> {
    visitNumber(n: NumberExpr) { return 'number'; }
    visitBinary(b: BinaryExpr) {
        const l = b.left.accept(this);
        const r = b.right.accept(this);
        if (l === 'number' && r === 'number') return 'number';
        return 'error';
    }
}

// 用法：1 + 2 - 3
const expr = new BinaryExpr('-',
    new BinaryExpr('+', new NumberExpr(1), new NumberExpr(2)),
    new NumberExpr(3)
);

new Evaluator().visitBinary(expr as any);  // 0
new Printer().visitBinary(expr as any);   // "((1 + 2) - 3)"
new TypeChecker().visitBinary(expr as any); // 'number'
```

新增操作（如代码生成 visitor）只需要新增 Visitor 类，**不修改任何 Expr 类**。

## Java 实战：Java 编译器 API

```java
// Java 编译器 API 用 Visitor 遍历程序元素
public class ElementAnalyzer {
    void analyze(Element element) {
        // Visitor：遍历并收集信息
        element.accept(new ElementVisitor<Void, Void>() {
            @Override
            public Void visitType(TypeElement e, Void p) {
                System.out.println("Type: " + e.getQualifiedName());
                return super.visitType(e, p);
            }

            @Override
            public Void visitMethod(ExecutableElement e, Void p) {
                System.out.println("Method: " + e.getSimpleName());
                return super.visitMethod(e, p);
            }

            @Override
            public Void visitVariable(VariableElement e, Void p) {
                System.out.println("Variable: " + e.getSimpleName());
                return super.visitVariable(e, p);
            }
        }, null);
    }
}
```

## Spring BeanDefinitionVisitor

```java
public class MyBeanVisitor implements BeanDefinitionVisitor {
    @Override
    public void visitBeanDefinition(BeanDefinition beanDefinition) {
        // 自定义处理
    }

    @Override
    public void visitBeanDefinition(String beanName, BeanDefinition beanDefinition) {
        // 自定义处理
    }
}
```

## 实战：文件系统遍历

```typescript
interface FileSystemVisitor<R> {
    visitFile(file: FileNode): R;
    visitDirectory(dir: DirectoryNode): R;
}

class FileNode {
    constructor(public name: string, public size: number) {}
    accept<R>(v: FileSystemVisitor<R>): R { return v.visitFile(this); }
}

class DirectoryNode {
    constructor(public name: string, public children: FileSystemNode[]) {}
    accept<R>(v: FileSystemVisitor<R>): R { return v.visitDirectory(this); }
}

type FileSystemNode = FileNode | DirectoryNode;

// 计算总大小
class SizeCalculator implements FileSystemVisitor<number> {
    visitFile(file: FileNode) { return file.size; }
    visitDirectory(dir: DirectoryNode) {
        return dir.children.reduce((sum, c) => sum + c.accept(this), 0);
    }
}

// 收集所有文件名
class FileCollector implements FileSystemVisitor<string[]> {
    visitFile(file: FileNode) { return [file.name]; }
    visitDirectory(dir: DirectoryNode) {
        return dir.children.flatMap(c => c.accept(this));
    }
}

// 用法
const root = new DirectoryNode('project', [
    new DirectoryNode('src', [new FileNode('index.ts', 1200)]),
    new FileNode('README.md', 2000),
]);

new SizeCalculator().visitDirectory(root);   // 3200
new FileCollector().visitDirectory(root);    // ['src', 'index.ts', 'README.md']
```

## 优缺点

## 优点

- 新增操作容易（新增 Visitor 类，不改元素）
- 操作集中（所有操作在一个 Visitor 中）
- 元素类层次稳定（编译期确定）

## 缺点

- **增加新元素类困难**（必须改所有 Visitor）
- **双重分派**（double dispatch）依赖方法签名
- 违反**封装性**（Visitor 需要访问元素内部状态）

## 适用边界

✅ **使用场景**：
- AST 处理（编译器 / 表达式求值）
- 文件系统遍历（多种操作：压缩 / 备份 / 搜索）
- 对象结构稳定但操作经常新增
- Java ElementVisitor / Spring BeanDefinitionVisitor

❌ **避免场景**：
- 元素类经常新增（Visitor 难以演进）
- 操作只有 1-2 种（直接写在元素类里）
- 不需要遍历整个结构（局部处理）

🔄 **替代方案**：
- **直接方法**：操作简单时直接在元素类加方法
- **pattern matching**：TypeScript / Rust 用 match 替代 Visitor
- **Lambda / 函数式**：操作作为函数传入

💡 **最佳实践**：
- Visitor 接口要尽量稳定（一旦确定不改）
- 用泛型让 Visitor 返回不同类型（`visitX(): R`）
- Go / TS 没有重载，可以用 `accept` 方法避免双重分派
- 警惕 Visitor 膨胀（操作太多 Visitor 难维护）


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [java-language](https://java-px.bot.cd/java-language/):Java 设计模式
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [architecture](https://java-px.bot.cd/architecture/):架构模式
