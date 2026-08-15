---
title: 泛型 Generics
---

# 泛型 Generics

Rust 泛型实现"零成本抽象"：编译期单态化（每个具体类型生成独立代码），运行时性能等同手写。

## 一句话总结

> **泛型 = 类型参数化 + 零成本**。**核心：编译期单态化、Trait 约束、where 子句**。

---

## 函数泛型

```rust
fn largest<T: PartialOrd + Copy>(list: &[T]) -> T {
    let mut largest = list[0];
    for &item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}

let nums = vec![34, 50, 25, 100, 65];
let result = largest(&nums);  // i32

let chars = vec!['y', 'm', 'a', 'q'];
let result = largest(&chars);  // char
```

## 结构体泛型

```rust
struct Point<T> {
    x: T,
    y: T,
}

let integer = Point { x: 5, y: 10 };
let float = Point { x: 1.0, y: 4.0 };

// 多泛型参数
struct Point2<T, U> {
    x: T,
    y: U,
}

let mixed = Point2 { x: 5, y: 4.0 };
```

## 枚举泛型

```rust
enum Option<T> {
    Some(T),
    None,
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

## 方法泛型

```rust
struct Point<T> {
    x: T,
    y: T,
}

impl<T> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}

// 仅对特定类型实现
impl Point<f32> {
    fn distance_from_origin(&self) -> f32 {
        (self.x.powi(2) + self.y.powi(2)).sqrt()
    }
}
```

## Trait 约束

```rust
// 单个约束
fn notify<T: Summary>(item: &T) {
    println!("{}", item.summarize());
}

// 多个约束（+）
fn notify<T: Summary + Display>(item: &T) {
    println!("{} {}", item.summarize(), item);
}

// where 子句（复杂约束更清晰）
fn some_function<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Debug + Send + Sync,
{ 0 }

// 返回实现了 Trait 的类型（impl Trait）
fn returns_summarizable() -> impl Summary {
    NewsArticle { /* ... */ }
}
```

## 单态化（Monomorphization）

```rust
// 泛型在编译期生成具体类型的代码
let integer = Some(5);
let float = Some(5.0);

// 编译为：
// enum Option_i32 { Some(i32), None }
// enum Option_f64 { Some(f64), None }

// 优点：性能等同手写
// 缺点：二进制体积增大
```

## 关联类型

```rust
trait Iterator {
    type Item;

    fn next(&mut self) -> Option<Self::Item>;
}

struct Counter {
    count: u32,
}

impl Iterator for Counter {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        self.count += 1;
        if self.count < 6 {
            Some(self.count)
        } else {
            None
        }
    }
}
```

## 实战案例：通用 HashMap 包装

```rust
use std::collections::HashMap;
use std::hash::Hash;

struct Cache<K, V>
where
    K: Hash + Eq + Clone,
    V: Clone,
{
    data: HashMap<K, V>,
}

impl<K, V> Cache<K, V>
where
    K: Hash + Eq + Clone,
    V: Clone,
{
    fn new() -> Self {
        Self { data: HashMap::new() }
    }

    fn get_or_insert<F>(&mut self, key: K, default: F) -> V
    where
        F: FnOnce() -> V,
    {
        self.data.entry(key).or_insert_with(default).clone()
    }
}
```

## 关联章节

- **02-types-traits/overview**：类型系统
- **02-types-traits/trait**：Trait
- **02-types-traits/advanced-types**：高级类型

## 一句话总结

> **泛型 = Rust 抽象能力 + 零运行时开销**。**编译期单态化，性能等同手写，但二进制会变大**。
