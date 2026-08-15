---
title: 生命周期 Lifetimes
---

# 生命周期 Lifetimes

生命周期是 Rust 防止悬垂引用的机制：每个引用都有生命周期，标注确保引用不会比它指向的数据活得更久。

## 一句话总结

> **生命周期 = 引用的有效期标注**。**核心规则：引用的生命周期 ≤ 数据的生命周期**。**多数情况自动推断，复杂情况手动标注**。

---

## 悬垂引用问题

```rust
// 反例：返回局部变量的引用
fn dangle() -> &String {
    let s = String::from("hello");
    &s  // s 在函数结束时被 drop，引用无效
}  // 编译错误：missing lifetime specifier

// 正确：返回 owned String
fn no_dangle() -> String {
    String::from("hello")
}
```

## 生命周期标注语法

```rust
// 'a 是生命周期参数
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

// 'a 表示：返回引用的生命周期 = 两个输入引用生命周期的"交集"
```

## 借用检查器自动推断

```rust
// 大多数情况下无需手动标注，编译器自动推断
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    &s[..]
}
```

## 结构体生命周期

```rust
// 持有引用的结构体必须标注生命周期
struct ImportantExcerpt<'a> {
    part: &'a str,
}

impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }

    fn announce_and_return_part(&self, announcement: &str) -> &str {
        println!("Attention: {}", announcement);
        self.part
    }
}
```

## 静态生命周期 'static

```rust
// 'static：整个程序运行期间有效
let s: &'static str = "I have a static lifetime.";

// 字符串字面量都是 'static（存储在二进制中）
let s: &'static str = "hello";

// 何时用？
// - 字符串字面量
// - 全局配置
// - trait object（Box<dyn Trait + 'static>）
// 注意：不要滥用 'static：泄漏内存、阻止 drop
```

## 实战案例：返回较长字符串

```rust
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}

fn main() {
    let string1 = String::from("long string is long");
    let result;
    {
        let string2 = String::from("xyz");
        result = longest(string1.as_str(), string2.as_str());
    }  // string2 drop
    // println!("{}", result);  // 编译错误
}
```

## 关联章节

- **01-basics/ownership**：所有权
- **01-basics/borrowing**：借用
- **02-types-traits/advanced-types**：PhantomData / 高级类型


## 生命周期省略规则（Lifetime Elision）

编译器自动推断的 3 条规则：

1. **每个引用参数都有独立生命周期**：`fn foo(x: &str, y: &str)` → `fn foo<'a, 'b>(x: &'a str, y: &'b str)`
2. **如果只有一个引用输入，所有输出共享同一生命周期**：`fn foo(x: &str) -> &str` → `fn foo<'a>(x: &'a str) -> &'a str`
3. **如果第一个参数是 `&self` / `&mut self`，所有输出共享 self 的生命周期**：方法签名自动推断

```rust
// 规则 2 适用：单输入引用，输出共享
fn first_word(s: &str) -> &str { ... }

// 规则 3 适用：方法签名
impl<'a> Foo<'a> {
    fn get(&self) -> &str { ... }  // 输出共享 self 的生命周期
}
```

## 生命周期子类型（Variance）

```rust
// 协变（covariance）：'long: 'short 时 &'long T 可以当 &'short T 用
fn foo<'a, 'b>(s: &'a str) -> &'b str where 'a: 'b {
    s  // 缩短生命周期，安全
}

// 不变（invariance）：&'a mut T 必须严格匹配
fn mutate<'a>(s: &'a mut String) {
    // 不能传给期望 &'static 或更短生命周期的函数
}

// 逆变（contravariance）：fn(T) 是逆变的（很少直接用）
```

## 高阶 trait bound（HRTB）

```rust
// 任意生命周期都满足
fn longer<'a>(x: &'a str, y: &'a str) -> &'a str { ... }

// 闭包：传入的引用生命周期由调用方决定
fn apply<F>(f: F) where F: for<'a> Fn(&'a str) -> &'a str {
    let s = "hello";
    let r = f(s);
    println!("{}", r);
}
```

## 实战案例：自实现迭代器

```rust
struct StrSplit<'a, 'b> {
    remainder: &'a str,
    delimiter: &'b str,
}

impl<'a, 'b> StrSplit<'a, 'b> {
    fn new(haystack: &'a str, delimiter: &'b str) -> Self {
        Self { remainder: haystack, delimiter }
    }
}

impl<'a, 'b> Iterator for StrSplit<'a, 'b> {
    type Item = &'a str;

    fn next(&mut self) -> Option<Self::Item> {
        let next_delim = self.remainder.find(self.delimiter)?;
        let before = &self.remainder[..next_delim];
        self.remainder = &self.remainder[next_delim + self.delimiter.len()..];
        Some(before)
    }
}
```

## 踩坑：生命周期不够短

```rust
// 错误：返回局部 String 的引用
fn get_default() -> &String {
    let s = String::from("default");
    &s  // 编译错误：s 在函数结束时 drop
}

// 修复 1：返回 owned String
fn get_default() -> String { String::from("default") }

// 修复 2：返回 'static str
fn get_default() -> &'static str { "default" }

// 修复 3：使用 Cow<'_, str>
use std::borrow::Cow;
fn get_default<'a>(input: &'a str) -> Cow<'a, str> {
    if input.is_empty() { Cow::Borrowed("default") }
    else { Cow::Borrowed(input) }
}
```
