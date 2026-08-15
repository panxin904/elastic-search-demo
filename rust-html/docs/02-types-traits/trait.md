---
title: Trait
---

# Trait

Trait 是 Rust 行为抽象的核心：定义共享行为，支持默认方法、关联类型、Trait bound。

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
