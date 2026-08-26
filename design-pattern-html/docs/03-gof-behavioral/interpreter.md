---
title: Interpreter 解释器模式
description: 自定义语言求值 + 表达式解析 + SQL parser / 正则表达式 / DSL
---

# Interpreter 解释器模式

## 核心问题

需要实现一个**自定义语言**或**表达式**的求值。例如：
- 数学表达式：`(1 + 2) * 3`
- 布尔表达式：`(age > 18) AND (country = 'CN')`
- SQL 解析：`SELECT * FROM users WHERE age > 18`
- DSL（领域特定语言）：`order.create().item().pay()`

## 核心思想

给定一个语言，定义它的**文法**（grammar）的一种表示，并定义一个**解释器**，使用该表示来解释语言中的句子。

**关键角色**：
- **AbstractExpression**：抽象表达式（`interpret()`）
- **TerminalExpression**：终结符表达式（数字 / 变量）
- **NonTerminalExpression**：非终结符表达式（+ / - / *）
- **Context**：上下文（存储变量值等）

## TypeScript：数学表达式

```typescript
// 抽象表达式
interface Expr {
    interpret(): number;
}

// 终结符：数字
class NumberExpr implements Expr {
    constructor(public value: number) {}
    interpret() { return this.value; }
}

// 终结符：变量
class VariableExpr implements Expr {
    constructor(public name: string, public context: Context) {}
    interpret() { return this.context.get(this.name); }
}

// 非终结符：加法
class PlusExpr implements Expression {
    constructor(public left: Expr, public right: Expr) {}
    interpret() { return this.left.interpret() + this.right.interpret(); }
}

class MinusExpr implements Expression {
    constructor(public left: Expr, public right: Expr) {}
    interpret() { return this.left.interpret() - this.right.interpret(); }
}

// 上下文
class Context {
    private vars = new Map<string, number>();
    set(name: string, value: number) { this.vars.set(name, value); }
    get(name: string) { return this.vars.get(name) ?? 0; }
}

// 用法：(x + 2) - 3，x = 5
const ctx = new Context();
ctx.set('x', 5);

const expr = new MinusExpr(
    new PlusExpr(new VariableExpr('x', ctx), new NumberExpr(2)),
    new NumberExpr(3)
);

console.log(expr.interpret());  // (5 + 2) - 3 = 4
```

## 实战：正则表达式

正则表达式本身就是一种语言，Regexp 引擎是解释器：

```javascript
// JavaScript 正则表达式
const pattern = /^(\\d+)\\.(\\d+)\\.(\\d+)\\.(\\d+)$/;

const matcher = pattern.exec('192.168.1.1');
console.log(matcher);
// ['192.168.1.1', '192', '168', '1', '1']

// 实际场景：解析 IP 地址
function parseIP(ip: string) {
    const m = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/.exec(ip);
    if (!m) return null;
    return {
        a: parseInt(m[1]),
        b: parseInt(m[2]),
        c: parseInt(m[3]),
        d: parseInt(m[4]),
    };
}
```

正则表达式引擎内部用 NFA / DFA 解释正则语法。

## 实战：SQL 解析器

```java
// ANTLR 生成的 SQL 解析器（简化）
public class SqlParser {
    public static void parse(String sql) {
        // ANTLR 自动生成的 Lexer / Parser
        CharStream input = CharStreams.fromString(sql);
        SqlLexer lexer = new SqlLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        SqlParser parser = new SqlParser(tokens);

        ParseTree tree = parser.selectStatement();
        System.out.println(tree.toStringTree(parser));

        // 用 Visitor 遍历 AST
        SqlBaseVisitor<Void> visitor = new SqlBaseVisitor<Void>() {
            @Override
            public Void visitSelectStatement(SqlParser.SelectStatementContext ctx) {
                System.out.println("Select columns:");
                ctx.columnList().column().forEach(c -> System.out.println(" - " + c.getText()));
                System.out.println("From table: " + ctx.tableName().getText());
                if (ctx.WHERE() != null) {
                    System.out.println("Where: " + ctx.expression().getText());
                }
                return null;
            }
        };
        visitor.visit(tree);
    }
}

// 用法
SqlParser.parse("SELECT id, name FROM users WHERE age > 18");
// 输出：
// Select columns:
//  - id
//  - name
// From table: users
// Where: age > 18
```

SQL 解析器 = Lexer（词法分析）+ Parser（语法分析）+ Visitor（语义分析）。

## 实战：DSL（领域特定语言）

```typescript
// SQL DSL（TypeORM）
const users = await connection
    .createQueryBuilder()
    .select('user')
    .from(User, 'user')
    .where('user.age > :age', { age: 18 })
    .andWhere('user.country = :country', { country: 'CN' })
    .orderBy('user.createdAt', 'DESC')
    .limit(10)
    .getMany();

// 流式 API 是 DSL，每个方法是 Expression 节点
```

```typescript
// Cron 表达式解析
class CronExpression {
    constructor(
        public minute: string,
        public hour: string,
        public dayOfMonth: string,
        public month: string,
        public dayOfWeek: string
    ) {}

    static parse(expr: string): CronExpression {
        const parts = expr.split(' ');
        if (parts.length !== 5) throw new Error('Invalid cron');
        return new CronExpression(...parts);
    }

    matches(date: Date): boolean {
        return (
            this.matchesField(date.getMinutes(), this.minute) &&
            this.matchesField(date.getHours(), this.hour) &&
            this.matchesField(date.getDate(), this.dayOfMonth) &&
            this.matchesField(date.getMonth() + 1, this.month) &&
            this.matchesField(date.getDay(), this.dayOfWeek)
        );
    }

    private matchesField(value: number, pattern: string): boolean {
        if (pattern === '*') return true;
        if (pattern.includes(',')) return pattern.split(',').map(Number).includes(value);
        if (pattern.includes('/')) {
            const [, step] = pattern.split('/');
            return value % parseInt(step) === 0;
        }
        return parseInt(pattern) === value;
    }
}

// 用法
const cron = CronExpression.parse('0 0 * * *');  // 每天 0 点
cron.matches(new Date('2024-01-01 00:00:00'));  // true
```

## 何时使用 / 避免

✅ **使用场景**：
- 简单 DSL / 表达式求值
- SQL / 数学公式 / 业务规则引擎
- 自定义配置格式（YAML / HCL / TOML）

❌ **避免场景**：
- 复杂语法（用 ANTLR / Yacc / Lex）
- 性能敏感（解释执行比编译慢 10-100x）
- 一次性脚本（直接写 if-else）

🔄 **替代方案**：
- **ANTLR / Yacc**：复杂语法解析
- **正则表达式**：文本匹配
- **JEXL / SpEL**：Java 表达式
- **Lambda / 闭包**：参数化行为

💡 **最佳实践**：
- 文法要简单（否则维护成本指数增长）
- 用 Visitor 遍历语法树（不直接递归）
- 错误处理要友好（明确语法错误位置）
- 考虑用现成库（ANTLR / PEG.js）而非手写


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
