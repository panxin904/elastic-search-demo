---
title: Memento 备忘录模式
description: 保存恢复对象状态 + 撤销操作 / 数据库快照 / Redux undo / Git 内部原理
---

# Memento 备忘录模式

## 核心问题

需要在不破坏封装性的前提下，捕获对象的内部状态，并在该对象之外保存这个状态，以便以后恢复。

**真实场景**：
- 撤销操作（编辑器 / IDE / Photoshop）
- 数据库快照（Redis RDB / PostgreSQL PITR）
- 游戏存档（保存当前进度）
- Git 内部（每次 commit 是对象状态的 memento）

## 核心思想

用三个角色协作：
1. **Originator（原发器）**：要保存状态的对象
2. **Memento（备忘录）**：存储 Originator 的内部状态
3. **Caretaker（管理者）**：管理 Memento（保存栈 / 队列）

关键点：Memento 只暴露「窄接口」给 Caretaker（`getState()`），暴露「宽接口」给 Originator（`setState()`）。

## TypeScript 实战：编辑器

```typescript
// Memento：不可变快照
class EditorMemento {
    constructor(public readonly content: string) {}
}

// Originator：编辑器
class Editor {
    private content = '';

    type(text: string) { this.content += text; }
    save(): EditorMemento {
        return new EditorMemento(this.content);  // 创建快照
    }
    restore(m: EditorMemento) {
        this.content = m.content;  // 恢复
    }
    getContent() { return this.content; }
}

// Caretaker：撤销栈
class History {
    private stack: EditorMemento[] = [];

    push(m: EditorMemento) { this.stack.push(m); }
    pop(): EditorMemento | undefined { return this.stack.pop(); }
}

// 用法
const editor = new Editor();
const history = new History();

editor.type('Hello');
history.push(editor.save());
editor.type(' World');
history.push(editor.save());
editor.type('!');

console.log(editor.getContent());  // "Hello World!"

editor.restore(history.pop()!);    // 撤销 !
console.log(editor.getContent());  // "Hello World"

editor.restore(history.pop()!);    // 撤销 World
console.log(editor.getContent());  // "Hello"
```

## Java 实战

```java
// Memento（不可变快照）
public final class EditorMemento {
    private final String content;
    public EditorMemento(String content) { this.content = content; }
    public String getContent() { return content; }  // 窄接口给 Caretaker
}

// Originator
public class Editor {
    private StringBuilder content = new StringBuilder();

    public void type(String text) { content.append(text); }
    public EditorMemento save() { return new EditorMemento(content.toString()); }
    public void restore(EditorMemento m) { this.content = new StringBuilder(m.getContent()); }
    public String getContent() { return content.toString(); }
}

// Caretaker
public class History {
    private final Deque<EditorMemento> stack = new ArrayDeque<>();
    public void push(EditorMemento m) { stack.push(m); }
    public EditorMemento pop() { return stack.pop(); }
}
```

## 实战：数据库快照

数据库的快照（snapshot）本质是 Memento：

```bash
# Redis RDB 快照（fork + copy-on-write）
> SAVE  # 阻塞式保存（生产禁用）
> BGSAVE  # 后台 fork 子进程，父进程继续服务

# 生成的 dump.rdb 是 Redis 数据集的 memento
```

PostgreSQL PITR（Point-in-Time Recovery）：

```sql
-- 基准备份（memento 1）
pg_basebackup -D /backup/base

-- WAL 日志（后续变更记录）
-- recovery 时把 base + WAL replay 到指定时间点
```

## Git 内部

每次 `git commit` 是工作区 + 暂存区的 memento：

```bash
git commit -m "feat: add login"
# 创建 commit 对象，包含：
# - tree（暂存区快照）
# - parent（前一个 commit）
# - author / message

git reset HEAD~1  # 撤销最后一次 commit（memento.pop()）
```

Git 的 reflog 是撤销栈的实现。

## 适用边界

✅ **使用场景**：
- 撤销/重做（编辑器 / IDE）
- 数据库快照 / 事务回滚
- 游戏存档
- 长流程表单（保存草稿）
- 命令模式 + Memento = 可撤销命令

❌ **避免场景**：
- 对象状态很简单（直接保存就行）
- 快照成本很高（大数据对象序列化慢）
- 撤销栈无大小限制（内存泄漏）
- 业务不需要回退

🔄 **与 Command 区别**：
- **Memento**：保存状态快照（被动）
- **Command**：保存操作（主动）

🔄 **与 Prototype 区别**：
- **Prototype**：克隆对象（深拷贝）
- **Memento**：只快照部分状态（窄接口）

💡 **最佳实践**：
- Memento 应该不可变（避免 Caretaker 篡改）
- 撤销栈有大小限制（默认 50 ~ 100）
- 大对象 Memento 考虑增量快照
- Memento 序列化要考虑兼容性（不同版本的对象结构）


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
