---
title: Trait
date: 2026-08-15  # date-auto-injected
---

# Trait

Trait 是 Rust 行为抽象的核心：定义共享行为，支持默认方法、关联类型、Trait bound。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Rust 生命周期省略规则</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Lifetime Elision · 3 条规则让编译器自动推导</text>

  <!-- 规则 1 -->
  <rect class="at-hover-card" x="30" y="90" width="540" height="90" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="50" y="115" font-size="13" font-weight="700" fill="#1e40af">规则 ① 输入生命周期：每个引用参数各得一个</text>
  <text x="50" y="140" font-size="11" font-family="monospace" fill="#1e293b">fn foo(x: &amp;str, y: &amp;str)  →  fn foo&lt;'a, 'b&gt;(x: &amp;'a str, y: &amp;'b str)</text>
  <text x="50" y="162" font-size="10" fill="#475569" font-style="italic">编译器为每个引用参数分配独立生命周期参数 'a, 'b</text>

  <!-- 规则 2 -->
  <rect class="at-hover-card" x="30" y="195" width="540" height="100" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="50" y="220" font-size="13" font-weight="700" fill="#047857">规则 ② 单输入生命周期：输出与该输入一致</text>
  <text x="50" y="245" font-size="11" font-family="monospace" fill="#1e293b">fn foo(x: &amp;str) -&gt; &amp;str  →  fn foo&lt;'a&gt;(x: &amp;'a str) -&gt; &amp;'a str</text>
  <text x="50" y="268" font-size="10" fill="#475569" font-style="italic">仅 1 个引用参数 → 输出生命周期默认为它</text>

  <!-- 规则 3 -->
  <rect class="at-hover-card" x="30" y="310" width="540" height="100" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="50" y="335" font-size="13" font-weight="700" fill="#991b1b">规则 ③ 方法中 &amp;self / &amp;mut self：输出与 self 一致</text>
  <text x="50" y="360" font-size="11" font-family="monospace" fill="#1e293b">impl Foo { fn name(&amp;self) -&gt; &amp;str }</text>
  <text x="50" y="378" font-size="11" font-family="monospace" fill="#1e293b">          → fn name&lt;'a&gt;(&amp;'a self) -&gt; &amp;'a str</text>

  <!-- 多输出失败示例 -->
  <rect x="30" y="425" width="540" height="50" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="50" y="448" font-size="12" font-weight="700" fill="#92400e">多输入 + 输出引用：编译器无法推导 → 必须显式标注</text>
  <text x="50" y="465" font-size="11" font-family="monospace" fill="#1e293b">fn longest&lt;'a&gt;(x: &amp;'a str, y: &amp;'a str) -&gt; &amp;'a str  // 手动声明</text>
</svg>

## 一句话总结

> **Trait = 行为接口 + 默认实现 + 关联类型**。**类比 Java interface 但更强（默认方法 + 默认泛型 + 关联类型）**。

---

## 定义 Trait

```rust
pub trait Summary {
    fn summarize(&self) -> String;

    // 默认实现
    fn default_summarize(&self) -> String {
        String::from("(Read more...)")
    }
}
```

## 实现 Trait

```rust
pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

pub struct Tweet {
    pub username: String,
    pub content: String,
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}
```

## 默认实现

```rust
trait Summary {
    fn summarize_author(&self) -> String;

    fn summarize(&self) -> String {
        format!("(Read more from {}...)", self.summarize_author())
    }
}

impl Summary for Tweet {
    fn summarize_author(&self) -> String {
        format!("@{}", self.username)
    }
}
```

## Trait 作为参数

```rust
// 单个 Trait bound
pub fn notify(item: &impl Summary) {
    println!("Breaking news! {}", item.summarize());
}

// Trait bound 语法
pub fn notify<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize());
}

// 多个 bound
pub fn notify<T: Summary + Display>(item: &T) { }

// where 子句
pub fn notify<T, U>(item1: &T, item2: &U)
where
    T: Summary + Display,
    U: Summary + Debug,
{ }
```

## Trait 作为返回值

```rust
fn returns_summarizable() -> impl Summary {
    NewsArticle { /* ... */ }
}

// 注意：impl Trait 限制：必须返回单一具体类型
```

## Trait Object（动态分发）

```rust
fn make_summary(items: Vec<Box<dyn Summary>>) -> Vec<String> {
    items.iter().map(|i| i.summarize()).collect()
}

let articles: Vec<Box<dyn Summary>> = vec![
    Box::new(NewsArticle { /* ... */ }),
    Box::new(Tweet { /* ... */ }),
];

// 引用形式
fn print_summary(item: &dyn Summary) {
    println!("{}", item.summarize());
}
```

## 关联类型

```rust
trait Iterator {
    type Item;

    fn next(&mut self) -> Option<Self::Item>;
}

impl Iterator for Counter {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        Some(self.count)
    }
}
```

## 常用标准 Trait

```rust
// Debug / Clone / Copy / PartialEq / Eq / Hash / Default
// 都可以 derive

#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Point {
    x: i32,
    y: i32,
}
```

## 关联章节

- **02-types-traits/overview**：类型系统
- **02-types-traits/generics**：泛型
- **02-types-traits/trait-objects**：Trait 对象与动态分发

## 一句话总结

> **Trait = Rust 抽象的核心**：定义行为契约、支持默认实现、支持关联类型、静态分发（泛型）与动态分发（dyn Trait）两种模式**。


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
