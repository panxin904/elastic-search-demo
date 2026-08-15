---
title: Prototype 原型模式
description: 通过克隆创建对象 + 深拷贝 vs 浅拷贝 + Java Cloneable + JavaScript structuredClone
---

# Prototype 原型模式

## 核心问题

当创建对象的成本很高（DB 连接、大文档、复杂配置），而我们又要创建多个类似的对象时，反复 `new` 不划算。

**真实场景**：
- 加载数据库连接（耗时 100ms）
- 解析 Office 文档（耗时 1s+）
- 游戏地图（10MB 数据，克隆比重新加载快 1000x）
- 模板对象（邮件模板、报表模板）

## 核心思想

通过克隆（`clone()`）而非 `new` 来创建对象。让对象自己负责「复制自己」的逻辑。

**两种拷贝**：
- **浅拷贝**：只复制对象本身 + 引用，不递归复制内部对象
- **深拷贝**：递归复制整个对象图（包括所有嵌套对象）

## Java 实现

## Cloneable 接口（不推荐）

```java
public class MailTemplate implements Cloneable {
    private String subject;
    private String body;
    private List<String> ccList;  // 引用类型

    public MailTemplate(String subject, String body) {
        this.subject = subject;
        this.body = body;
    }

    @Override
    public MailTemplate clone() {
        try {
            return (MailTemplate) super.clone();  // 浅拷贝
        } catch (CloneNotFoundException e) {
            throw new AssertionError();
        }
    }
}
```

**坑**：`Cloneable` 接口没有 `clone()` 方法（只有标记），靠 `Object.clone()`（protected）。深拷贝语义模糊，Effective Java 作者 Josh Bloch **明确不推荐** Cloneable。

## 拷贝构造器（推荐）

```java
public class MailTemplate {
    private final String subject;
    private final String body;
    private final List<String> ccList;

    public MailTemplate(String subject, String body) {
        this.subject = subject;
        this.body = body;
        this.ccList = new ArrayList<>();
    }

    // 拷贝构造器
    public MailTemplate(MailTemplate other) {
        this.subject = other.subject;
        this.body = other.body;
        this.ccList = new ArrayList<>(other.ccList);  // 深拷贝
    }

    public MailTemplate deepClone() {
        return new MailTemplate(this);
    }
}

// 用法
MailTemplate t1 = new MailTemplate("Welcome", "Hi {{name}}");
MailTemplate t2 = t1.deepClone();
t2.setBody("Hello {{name}}");  // 不影响 t1
```

## 多语言实现

## JavaScript：structuredClone（ES2022+）

```javascript
const template = {
    subject: 'Welcome',
    body: 'Hi {{name}}',
    attachments: [{ filename: 'guide.pdf' }, { filename: 'logo.png' }]
};

// 一行完成深拷贝
const copy = structuredClone(template);
copy.attachments[0].filename = 'manual.pdf';

console.log(template.attachments[0].filename);  // 'guide.pdf'（未变）
console.log(copy.attachments[0].filename);       // 'manual.pdf'
```

支持 Date / RegExp / Map / Set / ArrayBuffer 等内置类型，比 `JSON.parse(JSON.stringify(x))` 强大。

## Go：手动 Clone 方法

```go
package mail

type Attachment struct {
    Filename string
    Data     []byte
}

type Template struct {
    Subject     string
    Body        string
    Attachments []*Attachment
}

func (t *Template) Clone() *Template {
    clone := &Template{
        Subject: t.Subject,
        Body:    t.Body,
    }
    for _, a := range t.Attachments {
        clone.Attachments = append(clone.Attachments, &Attachment{
            Filename: a.Filename,
            Data:     append([]byte(nil), a.Data...),  // 深拷贝 slice
        })
    }
    return clone
}
```

## Python：copy.deepcopy

```python
import copy

template = {
    'subject': 'Welcome',
    'body': 'Hi {{name}}',
    'attachments': [{'filename': 'guide.pdf', 'data': b'...'}]
}

cloned = copy.deepcopy(template)
cloned['attachments'][0]['filename'] = 'manual.pdf'

print(template['attachments'][0]['filename'])  # 'guide.pdf'
print(cloned['attachments'][0]['filename'])     # 'manual.pdf'
```

## 适用边界

✅ **使用场景**：
- 对象创建成本高（DB 连接、复杂配置）
- 运行时决定具体类（不知道要克隆什么）
- 模板 / 原型对象（邮件模板、报表模板）
- 历史快照（Game save、撤销栈）

❌ **避免场景**：
- 对象很小（直接 `new` 更快）
- 循环引用（深拷贝会爆栈）
- 不可变对象（共享就好，不需要克隆）

🔄 **替代方案**：
- **拷贝构造器**（Java 推荐）：显式、可控、深浅可选
- **JSON.parse(JSON.stringify(x))**（JS）：简单场景
- **structuredClone()**（JS ES2022+）：浏览器原生
- **copy.deepcopy()**（Python）：标准库
- **Builder**：如果只是想分步创建，用 Builder 更合适

💡 **最佳实践**：
- 优先用拷贝构造器，不用 Cloneable（Effective Java 第 13 条）
- 深浅拷贝要有明确文档（共享可变状态 = bug）
- 不可变对象用「享元」共享，不需要克隆
- 循环引用需要特殊处理（用 id 或 marker）
