---
title: 类型系统总览
---

# 类型系统总览

Rust 的类型系统是其"零成本抽象"的基石。理解 enum / 泛型 / Trait 三件套，等于掌握了 Rust 抽象能力的 80%。

## 一句话总结

> **Rust 类型系统 = 枚举 + 模式匹配 + 泛型 + Trait**。**核心：类型即文档、编译期多态、零运行时开销**。

---

## 4 大类型基石

```
1. struct    - 命名字段聚合
2. enum      - 和类型（sum type），可表达"或"语义
3. 泛型      - 类型参数化
4. Trait     - 行为抽象（类似 interface 但更强大）
```

## 枚举：Rust 的杀手锏

```rust
// enum 表达"或"语义，比 null 更安全
enum IpAddr {
    V4(u8, u8, u8, u8),
    V6(String),
}

let home = ip: V4(127, 0, 0, 1);
let loopback = ip: V6(String::from("::1"));

// 模式匹配强制穷尽
fn route(ip: addr) -> String {
    match ip {
        ip: V4(a, b, c, d) => format!("{}.{}.{}.{}", a, b, c, d),
        ip: V6(s) => s,
    }
}
```

## Option & Result：消灭 null 和异常

```rust
// Option<T> = Some(T) | None
// 没有 null，没有 NPE（NullPointerException）

fn find_user(id: u32) -> Option<User> {
    if id == 0 { return None; }
    Some(User { id, name: "alice".to_string() })
}

// 使用时必须处理 None
match find_user(42) {
    Some(user) => println!("Found: {}", user.name),
    None => println!("User not found"),
}

// Result<T, E> = Ok(T) | Err(E)
// 强制处理错误，无 checked exception
fn read_file(path: &str) -> Result<String, io::Error> {
    std::fs::read_to_string(path)
}
```

## Trait：行为抽象

```rust
// 定义 Trait
trait Summary {
    fn summarize(&self) -> String;

    // 默认实现
    fn default_summary(&self) -> String {
        String::from("(Read more...)")
    }
}

// 实现 Trait
struct NewsArticle {
    headline: String,
    location: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, {}", self.headline, self.location)
    }
}

// 静态分发（编译期单态化，性能等同手写）
fn print_summary<T: Summary>(item: &T) {
    println!("{}", item.summarize());
}
```

## 泛型 + Trait 约束

```rust
// 泛型函数 + Trait 约束
fn largest<T: PartialOrd + Copy>(list: &[T]) -> T {
    let mut largest = list[0];
    for &item in list {
        if item > largest {
            largest = item;
        }
    }
    largest
}

// where 子句（复杂约束更清晰）
fn complex<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Debug + Send,
{ ... }

// 默认类型参数
struct MyStruct<T = String> {
    value: T,
}
```

## 零成本抽象的原理

```rust
// 泛型编译为单态化（每个具体类型生成独立代码）
fn generic<T: Add>(a: T, b: T) -> T {
    a + b
}

// 编译为
fn generic_i32(a: i32, b: i32) -> i32 { a + b }
fn generic_f64(a: f64, b: f64) -> f64 { a + b }
// 没有虚函数表、没有装箱、性能等同手写
```

## 4 大 Trait 派生的便利

```rust
// 自动 derive 常用 Trait
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct Point {
    x: i32,
    y: i32,
}

// Debug       - {:?} 格式化
// Clone       - .clone() 深拷贝
// Copy        - 按位复制（隐式）
// PartialEq   - == 比较
// Eq          - 完全等价（自反）
// Hash        - 放入 HashMap
// Default     - Default::default()
// Send/Sync   - 线程安全（标记）
```

## 实战案例：写一个 Result 链

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username_from_file() -> Result<String, io::Error> {
    // ? 操作符：自动传播错误
    let mut file = File::open("username.txt")?;
    let mut username = String::new();
    file.read_to_string(&mut username)?;
    Ok(username)
}

// 链式调用
fn process() -> Result<String, Box<dyn std::error::Error>> {
    let s = std::fs::read_to_string("username.txt")?;
    let trimmed = s.trim().to_string();
    Ok(trimmed)
}
```

## 关联章节

- **02-types-traits/enum-and-pattern**：枚举与模式匹配深度
- **02-types-traits/trait**：Trait 完整指南
- **02-types-traits/generics**：泛型系统
- **06-advanced/error-handling**：错误处理

## 一句话总结

> **类型系统是 Rust 抽象的核心**：enum 表达"或"、Trait 表达"行为"、泛型表达"参数化"，三者零成本。