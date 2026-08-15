"""Generate rust stub pages via CONTENT dictionary.

Each entry is a multiline string with Frontmatter + 5-7 H2 sections +
code blocks + 实战案例 + 关联章节 + 一句话总结.
"""
import os

DOCS_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "rust-html", "docs",
)

CONTENT = {}


def add(path: str, body: str) -> None:
    CONTENT[path] = body


# ============ 01-basics (5 stubs) ============
add("01-basics/ownership.md", r"""---
title: 所有权 Ownership
---

# 所有权 Ownership

所有权是 Rust 最核心的概念：每个值有且仅有一个所有者，所有者离开作用域时值被自动 drop。

## 一句话总结

> **所有权 = Rust 的"内存安全无 GC"密码**。**三大规则：唯一所有者 / move 转移 / drop 自动释放**。**目标：编译期消灭 use-after-free / double-free**。

---

## 三大规则

```rust
// 规则 1：每个值有且仅有一个所有者
let s = String::from("hello");  // s 是所有者
// take_ownership(s);           // s 已经无效
// println!("{}", s);           // 编译错误

// 规则 2：赋值或传参时所有权转移（move）
let s1 = String::from("hello");
let s2 = s1;  // s1 无效，所有权转移给 s2
// println!("{}", s1);  // 编译错误

// 规则 3：所有者离开作用域，值自动 drop
{
    let s = String::from("hello");
    // 使用 s
}  // s 离开作用域，自动 drop，内存释放
```

## Copy vs Move

```rust
// Copy trait：按位复制（如 i32, bool, f64）
let x = 5;
let y = x;       // 复制（Copy）
println!("{} {}", x, y);  // x 仍然有效

// Move：堆上的值默认 Move
let s1 = String::from("hello");
let s2 = s1;     // Move（堆上的 String）
// println!("{}", s1);  // s1 无效

// 显式 Clone（深拷贝）
let s1 = String::from("hello");
let s2 = s1.clone();  // 深拷贝
println!("{} {}", s1, s2);  // 都有效
```

## 所有权转移实战

```rust
// 函数参数：所有权进入函数
fn take_ownership(s: String) {
    println!("{}", s);
}  // s 在这里 drop

fn main() {
    let s = String::from("hello");
    take_ownership(s);  // s 所有权转移给函数
    // println!("{}", s);  // s 无效
}

// 返回值：所有权返回调用者
fn give_ownership() -> String {
    String::from("hello")
}

fn take_and_give_back(s: String) -> String {
    s
}
```

## Copy 类型清单

```
按位复制（Copy）：
  - 所有整数类型：i8 i16 i32 i64 i128 isize
                    u8 u16 u32 u64 u128 usize
  - 浮点数：f32 f64
  - bool, char
  - 元组（如果所有元素都是 Copy）：(i32, i32)
  - 数组（如果元素是 Copy）：[i32; 3]

堆分配（Move）：
  - String
  - Vec<T>
  - Box<T>
  - 所有自定义 struct / enum（默认）
```

## 实战案例：字符串所有权

```rust
// 反模式：clone 过度
fn process_bad(s: String) -> String {
    let _ = s.trim();
    s.clone()  // 不必要的 clone
}

// 推荐：返回新的 String
fn process_good(s: String) -> String {
    s.trim().to_string()  // 返回新的 owned String
}

// 推荐：借用不修改
fn print_good(s: &String) {
    println!("{}", s);
}
```

## 关联章节

- **01-basics/borrowing**：借用规则
- **01-basics/lifetimes**：生命周期
- **02-types-traits/advanced-types**：Copy/Clone trait

## 一句话总结

> **所有权是 Rust 的"心智负担"，但换来的是"内存安全 + 零运行时开销"**。**过了这一关，Rust 变得自然**。
""")

add("01-basics/borrowing.md", r"""---
title: 借用 Borrowing
---

# 借用 Borrowing

借用允许"使用值而不获取所有权"。通过 `&` 和 `&mut` 两种引用实现，编译期防止数据竞争。

## 一句话总结

> **借用 = 不获取所有权的引用**。**两大规则：不可变借用可多个、可变借用独占、不可变与可变不可共存**。**编译期消灭数据竞争**。

---

## 两大借用规则

```rust
// 规则 1：在同一作用域内：
//   - 不可变借用（&T）可以有任意多个
//   - 可变借用（&mut T）只能有一个

// 规则 2：不可变借用与可变借用不可共存
let mut s = String::from("hello");

let r1 = &s;       // 不可变借用 #1
let r2 = &s;       // 不可变借用 #2（OK）
// let r3 = &mut s;  // 编译错误（不可变 + 可变）
println!("{} {}", r1, r2);

// 不可变借用用完后再可变借用
let r1 = &s;
let r2 = &s;
println!("{} {}", r1, r2);
// r1, r2 不再使用
let r3 = &mut s;  // OK
r3.push_str(" world");
```

## 不可变借用

```rust
fn calculate_length(s: &String) -> usize {
    s.len()
}  // s 离开作用域，但因为是借用，不会 drop

fn main() {
    let s = String::from("hello");
    let len = calculate_length(&s);  // 借用 s
    println!("'{}' length: {}", s, len);  // s 仍然有效
}
```

## 可变借用

```rust
fn append_world(s: &mut String) {
    s.push_str(" world");
}

fn main() {
    let mut s = String::from("hello");
    append_world(&mut s);
    println!("{}", s);  // "hello world"
}
```

## 借用检查器（NLL）

```rust
// Non-Lexical Lifetimes（NLL）：借用生命周期基于"使用"而非"作用域"
fn main() {
    let mut s = String::from("hello");

    let r1 = &s;
    let r2 = &s;
    println!("{} {}", r1, r2);  // r1, r2 最后一次使用

    let r3 = &mut s;
    r3.push_str(" world");
    println!("{}", r3);
}
```

## 实战案例：迭代器借用

```rust
// 经典反模式：可变借用 + 不可变借用
let mut v = vec![1, 2, 3];
let first = &v[0];          // 不可变借用
v.push(4);                  // 编译错误（同时存在）
println!("{}", first);

// 正确：错开生命周期
let mut v = vec![1, 2, 3];
let first = &v[0];          // 不可变借用
println!("{}", first);       // 使用完 first
v.push(4);                  // 此后可以可变借用

// 正确：用 index 而非引用
let first = v[0];           // Copy，自动复制
v.push(4);                  // 不冲突
println!("{}", first);
```

## 4 个借用反模式

```
❌ 反模式 1：可变借用 + 不可变借用
let mut v = vec![1, 2];
let r = &v[0];
v.push(3);  // 借用冲突

❌ 反模式 2：借用跨 await（async 中）
async fn bad() {
    let guard = mutex.lock().unwrap();
    some_async().await;  // 跨 await 持有锁 → 死锁

❌ 反模式 3：返回局部变量的引用
fn bad() -> &String {
    let s = String::from("hi");
    &s  // 悬垂引用 → 编译错误

❌ 反模式 4：借用超过变量生命周期
let r;
{
    let s = String::from("hi");
    r = &s;  // 借用内部变量
}
println!("{}", r);  // s 已 drop → 编译错误
```

## 关联章节

- **01-basics/ownership**：所有权基础
- **01-basics/lifetimes**：生命周期标注
- **04-concurrency/channels**：多线程借用

## 一句话总结

> **借用 = Rust 的"编译期线程安全"基础**。**记住两大规则，编译错误会逼你写出安全的代码**。
""")

add("01-basics/lifetimes.md", r"""---
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

## 一句话总结

> **生命周期 = Rust 防悬垂引用的机制**。**多数情况自动推断，少数复杂情况显式标注 'a**。
""")

add("01-basics/syntax-fundamentals.md", r"""---
title: 语法基础
---

# Rust 语法基础

Rust 语法与其他语言相似但有差异：变量默认不可变、match 强制穷尽、错误处理无异常。

## 一句话总结

> **Rust 语法 = 类 C 系 + 强类型 + 默认不可变 + match 模式匹配**。**关键差异：let/let mut / match / 错误传播 ?**。

---

## 变量与常量

```rust
// 变量（默认不可变）
let x = 5;       // i32
let mut y = 5;   // 可变
y = 10;

// 常量（编译期常量，必须标注类型）
const MAX_POINTS: u32 = 100_000;

// shadowing（遮蔽：新变量覆盖旧变量）
let z = 5;
let z = z + 1;       // 不可变
let z = z * 2;
println!("{}", z);   // 12

// shadowing vs mut
let mut s = "hello";
let s = s.len();      // shadowing 允许（usize）
```

## 数据类型

```rust
// 标量
let a: i32 = -42;            // 整数
let b: f64 = 3.14;           // 浮点
let c: bool = true;
let d: char = '🦀';

// 复合
let tup: (i32, f64, u8) = (500, 6.4, 1);
let (x, y, z) = tup;          // 解构
let arr: [i32; 5] = [1, 2, 3, 4, 5];
```

## 函数

```rust
fn add(x: i32, y: i32) -> i32 {
    x + y      // 表达式返回值（无分号）
}

fn diverging() -> ! {
    panic!("This function never returns!");  // ! = never
}

// 高阶函数
fn apply<F>(f: F, x: i32) -> i32
where F: Fn(i32) -> i32 {
    f(x)
}

let result = apply(|x| x * 2, 5);  // 10
```

## 控制流

```rust
// if 是表达式
let x = if condition { 5 } else { 6 };

// loop 无限循环
let mut counter = 0;
let result = loop {
    counter += 1;
    if counter == 10 {
        break counter * 2;
    }
};

// for 遍历迭代器
for i in 0..5 {           // 0..5 不含 5
    println!("{}", i);
}
```

## match 强制穷尽

```rust
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter(String),
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter(state) => 25,
    }
}

// _ 通配符
match dice_roll {
    3 => add_fancy_hat(),
    7 => remove_fancy_hat(),
    _ => reroll(),
}

// if let 简化
let config_max = Some(3u8);
if let Some(max) = config_max {
    println!("max: {}", max);
}
```

## 错误处理

```rust
// panic!：不可恢复错误
panic!("crash and burn");

// Result：可恢复错误
enum Result<T, E> {
    Ok(T),
    Err(E),
}

// ? 操作符：自动传播错误
fn read_file() -> Result<String, io::Error> {
    let mut s = String::new();
    File::open("file.txt")?.read_to_string(&mut s)?;
    Ok(s)
}
```

## 实战案例：猜数字游戏

```rust
use std::io;
use std::cmp::Ordering;
use rand::Rng;

fn main() {
    println!("猜数字！");
    let secret = rand::thread_rng().gen_range(1..101);

    loop {
        println!("请输入猜测：");
        let mut guess = String::new();
        io::stdin().read_line(&mut guess).expect("读取失败");
        let guess: u32 = match guess.trim().parse() {
            Ok(num) => num,
            Err(_) => continue,
        };

        match guess.cmp(&secret) {
            Ordering::Less => println!("太小了"),
            Ordering::Greater => println!("太大了"),
            Ordering::Equal => {
                println!("猜对了！");
                break;
            }
        }
    }
}
```

## 关联章节

- **01-basics/overview**：基础总览
- **02-types-traits/overview**：类型系统
- **06-advanced/error-handling**：错误处理深度

## 一句话总结

> **Rust 语法基础 = let/let mut / match / ? / Result**。**一周上手，一个月熟练**。
""")

add("01-basics/hello-world.md", r"""---
title: Hello World 实战
---

# Hello World 实战

第一个 Rust 程序：从安装到部署，完整实战。

## 一句话总结

> **Hello World = 安装 Rust → cargo new → cargo run**。**5 分钟跑通，30 分钟熟悉工具链**。

---

## 安装 Rust

```bash
# macOS / Linux：rustup（官方推荐）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 验证
rustc --version
cargo --version
```

## 创建项目

```bash
cargo new hello_rust
cd hello_rust

# 目录结构
hello_rust/
├── .gitignore
├── Cargo.toml        # 项目配置
└── src/
    └── main.rs       # 入口文件
```

```rust
// src/main.rs
fn main() {
    println!("Hello, world!");
}
```

## Cargo.toml

```toml
[package]
name = "hello_rust"
version = "0.1.0"
edition = "2021"     # Rust 版本（2015 / 2018 / 2021 / 2024）
```

## 构建运行

```bash
# 编译
cargo build

# 编译并运行
cargo run

# release 构建（优化，更慢但产物更快）
cargo build --release

# 检查（不生成可执行文件，快速验证代码）
cargo check
```

## 添加依赖

```toml
# Cargo.toml
[dependencies]
ferris-says = "2.2"
```

```rust
// src/main.rs
use ferris_says::say;
use std::io::{stdout, BufWriter};

fn main() {
    let stdout = stdout();
    let message = "Hello fellow Rustaceans!";
    let width = message.chars().count();

    let mut writer = BufWriter::new(stdout.lock());
    say(message, width, &mut writer).unwrap();
}
```

## 第一个测试

```rust
// src/lib.rs
pub fn add(left: usize, right: usize) -> usize {
    left + right
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let result = add(2, 2);
        assert_eq!(result, 4);
    }
}
```

```bash
cargo test
```

## 工具链

```bash
# 格式化
cargo fmt

# 代码检查
cargo clippy

# 文档生成
cargo doc --open
```

## IDE 配置

```bash
# VSCode：安装 rust-analyzer 扩展

# IntelliJ IDEA：安装 IntelliJ Rust 插件

# vim / neovim：配置 coc-rust-analyzer 或 LSP
```

## 调试技巧

```bash
# 1. dbg! 宏快速打印
fn main() {
    let x = 5;
    let y = dbg!(x * 2) + 3;
    println!("y = {}", y);
}

# 2. panic 时的 backtrace
RUST_BACKTRACE=1 cargo run
RUST_BACKTRACE=full cargo run
```

## 关联章节

- **01-basics/overview**：基础总览
- **03-ecosystem/cargo**：Cargo 深度
- **03-ecosystem/tooling**：工具链

## 一句话总结

> **Hello World = Rust 入门第一步**。**cargo new → cargo run → cargo test**，5 分钟完整流程跑通**。
""")

# ============ 02-types-traits (5 stubs) ============
add("02-types-traits/enum-and-pattern.md", r"""---
title: 枚举与模式匹配
---

# 枚举与模式匹配

Rust 的 enum 是"和类型"（sum type），能表达"或"语义；模式匹配强制穷尽每个变体。

## 一句话总结

> **enum + match = Rust 消灭 null 与异常的核心**。**核心：Option<T> / Result<T,E> / 自定义 enum 表达业务状态**。

---

## 基本枚举

```rust
enum IpAddr {
    V4(u8, u8, u8, u8),
    V6(String),
}

let home = IpAddr::V4(127, 0, 0, 1);
let loopback = IpAddr::V6(String::from("::1"));
```

## 模式匹配

```rust
fn route(ip: IpAddr) -> String {
    match ip {
        IpAddr::V4(a, b, c, d) => format!("{}.{}.{}.{}", a, b, c, d),
        IpAddr::V6(s) => s,
    }
}
```

## Option：消灭 null

```rust
enum Option<T> {
    Some(T),
    None,
}

fn find_user(id: u32) -> Option<User> {
    if id == 0 { None } else { Some(User::new(id)) }
}

match find_user(42) {
    Some(user) => println!("Found: {}", user.name),
    None => println!("User not found"),
}

// if let 简化
if let Some(user) = find_user(42) {
    println!("Found: {}", user.name);
}

// 解构 Option
let x: Option<i32> = Some(5);
let y = x.unwrap();          // 5
let z = x.unwrap_or(0);      // 5
let w = x.expect("no value"); // 5

// map / and_then 链式
let result: Option<i32> = Some(5)
    .map(|x| x * 2)
    .and_then(|x| if x > 5 { Some(x) } else { None });
```

## Result：消灭异常

```rust
enum Result<T, E> {
    Ok(T),
    Err(E),
}

fn read_file(path: &str) -> Result<String, io::Error> {
    std::fs::read_to_string(path)
}

// ? 操作符传播错误
fn process() -> Result<String, Box<dyn Error>> {
    let content = std::fs::read_to_string("file.txt")?;
    let trimmed = content.trim().to_string();
    Ok(trimmed)
}
```

## if let / while let

```rust
// if let：单分支匹配
let config_max = Some(3u8);
if let Some(max) = config_max {
    println!("max: {}", max);
}

// while let：循环匹配
let mut stack = vec![1, 2, 3];
while let Some(top) = stack.pop() {
    println!("{}", top);
}
```

## matches! 宏

```rust
// 简化布尔判断
let x = Some(5);
assert!(matches!(x, Some(5)));
assert!(matches!(x, Some(_)));
assert!(!matches!(x, None));

// 配合 if guard
match x {
    Some(n) if n > 0 => println!("positive: {}", n),
    Some(0) => println!("zero"),
    Some(_) => println!("negative"),
    None => println!("none"),
}
```

## 实战案例：状态机

```rust
enum ConnectionState {
    Disconnected,
    Connecting { attempt: u32 },
    Connected { since: SystemTime },
    Failed { error: String, retry_after: Duration },
}

impl Connection {
    fn handle_event(&mut self, event: Event) {
        self.state = match (&self.state, event) {
            (ConnectionState::Disconnected, Event::Connect) =>
                ConnectionState::Connecting { attempt: 1 },
            (ConnectionState::Connecting { attempt }, Event::Timeout) =>
                ConnectionState::Connecting { attempt: attempt + 1 },
            (state, event) => {
                eprintln!("Invalid transition: {:?}", state);
                state.clone()
            }
        };
    }
}
```

## 关联章节

- **02-types-traits/overview**：类型系统
- **02-types-traits/trait**：Trait
- **06-advanced/error-handling**：错误处理

## 一句话总结

> **enum + match = Rust 消灭 null/异常/状态错误的核心武器**。**强制穷尽模式让 bug 在编译期被捕获**。
""")

add("02-types-traits/generics.md", r"""---
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
""")

add("02-types-traits/trait.md", r"""---
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
""")

add("02-types-traits/advanced-types.md", r"""---
title: 高级类型
---

# 高级类型

Newtype / 类型别名 / 永不返回类型 / DST / PhantomData — Rust 类型系统的"瑞士军刀"。

## 一句话总结

> **高级类型 = 表达领域语义 + 类型安全 + 零成本抽象**。**核心：Newtype 模式 / PhantomData / never 类型**。

---

## Newtype 模式

```rust
// 用 tuple struct 包装已有类型，赋予新语义
struct UserId(u64);
struct ProductId(u64);

fn get_user(id: UserId) -> User { todo!() }
fn get_product(id: ProductId) -> Product { todo!() }

let uid = UserId(42);
let pid = ProductId(100);
// get_product(uid);  // 编译错误：类型不匹配
```

## 类型别名

```rust
type Kilometers = i32;
type Thunk = Box<dyn Fn() + Send + 'static>;

let x: Kilometers = 5;
println!("{}", x);  // 5（与 i32 完全等价）

// 类型别名 ≠ Newtype
// 类型别名与原类型完全相同
// Newtype 是新类型，类型检查更严格
```

## never 类型 !

```rust
fn diverging() -> ! {
    panic!("This function never returns!");
}

// never 类型可以强制转换为任何类型
let x: i32 = diverging();
```

## 动态大小类型（DST）

```rust
// str 是 DST：大小编译期未知
let s: str = "hello";  // 错误：DST 不能作为变量
let s: &str = "hello";  // 正确：&str 是胖指针（ptr + len）

// Sized trait：默认所有泛型参数都有 Sized 约束
fn generic<T>(t: T) {}  // 等价于 fn generic<T: Sized>(t: T)

// 放宽约束
fn generic<T: ?Sized>(t: &T) {}
```

## PhantomData

```rust
use std::marker::PhantomData;

struct Iter<'a, T: 'a> {
    ptr: *const T,
    _marker: PhantomData<&'a T>,
}

// 标识拥有所有权但不存储
struct Owned<T> {
    _marker: PhantomData<T>,
}
```

## 关联类型 vs 泛型

```rust
// 关联类型：每个类型只能实现一次
trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}

// 泛型：可以多次实现
trait From<T> {
    fn from(value: T) -> Self;
}
```

## 实战案例：单位类型

```rust
use std::marker::PhantomData;
use std::ops::Add;

struct Meter;
struct Kilometer;

struct Distance<Unit> {
    value: f64,
    _unit: PhantomData<Unit>,
}

impl<Unit> Distance<Unit> {
    fn new(value: f64) -> Self {
        Self { value, _unit: PhantomData }
    }
}

impl Distance<Kilometer> {
    fn to_meters(self) -> Distance<Meter> {
        Distance::new(self.value * 1000.0)
    }
}

impl Add for Distance<Meter> {
    type Output = Distance<Meter>;
    fn add(self, other: Self) -> Self {
        Distance::new(self.value + other.value)
    }
}
```

## 关联章节

- **02-types-traits/overview**：类型系统
- **02-types-traits/trait**：Trait
- **01-basics/lifetimes**：生命周期

## 一句话总结

> **高级类型 = 类型安全的瑞士军刀**：Newtype / 类型别名 / ! / DST / PhantomData 组合出精确的领域语义**。
""")

add("02-types-traits/trait-objects.md", r"""---
title: Trait 对象与动态分发
---

# Trait 对象与动态分发

dyn Trait 是运行时多态：通过虚函数表（vtable）在运行时决定调用的具体实现。

## 一句话总结

> **dyn Trait = 运行时多态**。**核心：堆分配的 Box<dyn Trait> / 引用形式 &dyn Trait**。**对比泛型：性能略低、灵活性高**。

---

## 静态分发 vs 动态分发

```rust
// 静态分发（泛型）
fn print_summary<T: Summary>(item: &T) {
    println!("{}", item.summarize());
}
// 优点：内联优化、性能最优
// 缺点：二进制膨胀

// 动态分发（Trait Object）
fn print_summary(item: &dyn Summary) {
    println!("{}", item.summarize());
}
// 优点：灵活、支持异构集合
// 缺点：间接调用、不能内联
```

## Trait Object 用法

```rust
trait Draw {
    fn draw(&self);
}

struct Circle { radius: f64 }
struct Square { side: f64 }

impl Draw for Circle {
    fn draw(&self) { println!("Circle r={}", self.radius); }
}

impl Draw for Square {
    fn draw(&self) { println!("Square s={}", self.side); }
}

// 异构集合
let shapes: Vec<Box<dyn Draw>> = vec![
    Box::new(Circle { radius: 1.0 }),
    Box::new(Square { side: 2.0 }),
];

for shape in shapes.iter() {
    shape.draw();  // 动态分发
}
```

## Box<dyn Trait>

```rust
let circle: Box<dyn Draw> = Box::new(Circle { radius: 1.0 });

// 用途：
// 1. 异构集合
// 2. 返回实现 Trait 的类型（不知道具体类型）
// 3. 减小栈占用
```

## Object Safety（对象安全）

```rust
// 不是所有 Trait 都能作为 Trait Object
// 要求：
// 1. 方法签名不返回 Self
// 2. 方法没有泛型参数
// 3. 父 Trait 也必须是对象安全的

trait Clone {
    fn clone(&self) -> Self;  // 返回 Self，不是对象安全的
}
```

## dyn Trait Send / Sync

```rust
// 默认 dyn Trait 不是 Send
fn spawn_draw(shape: Box<dyn Draw>) {
    thread::spawn(move || shape.draw());  // 编译错误
}

// 加约束
fn spawn_draw(shape: Box<dyn Draw + Send>) {
    thread::spawn(move || shape.draw());  // OK
}
```

## 实战案例：插件系统

```rust
trait Plugin: Send + Sync {
    fn name(&self) -> &str;
    fn execute(&self, input: &str) -> Result<String, String>;
}

struct UppercasePlugin;
impl Plugin for UppercasePlugin {
    fn name(&self) -> &str { "uppercase" }
    fn execute(&self, input: &str) -> Result<String, String> {
        Ok(input.to_uppercase())
    }
}

struct PluginRegistry {
    plugins: Vec<Box<dyn Plugin>>,
}

impl PluginRegistry {
    fn register<P: Plugin + 'static>(&mut self, plugin: P) {
        self.plugins.push(Box::new(plugin));
    }

    fn run(&self, name: &str, input: &str) -> Result<String, String> {
        for plugin in &self.plugins {
            if plugin.name() == name {
                return plugin.execute(input);
            }
        }
        Err(format!("Plugin not found: {}", name))
    }
}
```

## 关联章节

- **02-types-traits/trait**：Trait 基础
- **02-types-traits/generics**：泛型（静态分发）
- **04-concurrency/channels**：消息传递

## 一句话总结

> **dyn Trait = 运行时多态**。**用于异构集合与插件系统，但有性能开销**。
""")

# ============ 03-ecosystem (4 stubs) ============
add("03-ecosystem/cargo.md", r"""---
title: Cargo
---

# Cargo

Cargo 是 Rust 的官方构建系统与包管理器：一个工具搞定 build / test / bench / doc / publish。

## 一句话总结

> **Cargo = Rust 的 npm + maven + make + 文档生成器**。**核心：项目工作流 + 依赖管理 + 测试 + 发布**。

---

## 项目初始化

```bash
# 新建二进制项目
cargo new my_project
cd my_project

# 目录结构
my_project/
├── .git/
├── .gitignore
├── Cargo.toml
└── src/
    └── main.rs

# 新建库项目
cargo new --lib my_library
```

## Cargo.toml

```toml
[package]
name = "my_project"
version = "0.1.0"
edition = "2021"
authors = ["Alice <alice@example.com>"]
license = "MIT OR Apache-2.0"
description = "A short description"

[dependencies]
serde = "1.0"
tokio = { version = "1", features = ["full"] }

[dev-dependencies]
mockall = "0.11"

[build-dependencies]
cc = "1.0"

[[bin]]
name = "my_project"
path = "src/main.rs"

[lib]
name = "my_library"
path = "src/lib.rs"

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true

[features]
default = ["json"]
json = ["serde_json"]
yaml = ["serde_yaml"]
full = ["json", "yaml"]
```

## 常用命令

```bash
cargo build              # debug 构建
cargo build --release     # release 构建
cargo check              # 快速类型检查

cargo run                # 编译并运行
cargo run --release
cargo run -- arg1 arg2

cargo test               # 运行所有测试
cargo test --release
cargo test test_name
cargo test -- --nocapture

cargo doc                # 生成文档
cargo doc --open

cargo fmt                # 格式化
cargo clippy             # lint
cargo outdated
cargo tree
cargo bench              # nightly

cargo clean              # 删除 target/

cargo add serde
cargo add serde --dev
cargo update
cargo update -p serde
cargo remove serde

cargo publish
cargo login
cargo package
```

## Workspace

```toml
# Cargo.toml（workspace root）
[workspace]
members = [
    "crates/foo",
    "crates/bar",
]

[workspace.dependencies]
serde = "1.0"

[workspace.package]
version = "0.1.0"
edition = "2021"
```

```bash
cargo build --workspace
cargo test --workspace
cargo build -p foo
```

## Feature Flags

```toml
# Cargo.toml
[features]
default = ["json"]
json = ["dep:serde_json"]
yaml = ["dep:serde_yaml"]

[dependencies]
serde_json = { version = "1", optional = true }
```

```rust
#[cfg(feature = "json")]
pub fn parse_json(s: &str) -> Result<Value, serde_json::Error> {
    serde_json::from_str(s)
}
```

```bash
cargo build --features "yaml"
cargo build --features "full"
cargo build --no-default-features
```

## 关联章节

- **03-ecosystem/overview**：生态总览
- **03-ecosystem/crates-io**：crates.io
- **03-ecosystem/tooling**：工具链

## 一句话总结

> **Cargo = Rust 工程的瑞士军刀**：build / test / bench / doc / publish 一站式搞定**。
""")

add("03-ecosystem/crates-io.md", r"""---
title: crates.io
---

# crates.io

crates.io 是 Rust 官方包仓库，与 npm / PyPI 同级，130k+ crates 覆盖几乎所有场景。

## 一句话总结

> **crates.io = Rust 生态的事实标准**。**核心：注册 / 搜索 / 版本管理 / 文档浏览**。

---

## 注册 crates.io 账号

```bash
# 1. 访问 https://crates.io/ 注册账号

# 2. 在 https://crates.io/me 获取 API token

# 3. 登录
cargo login <token>
```

## 搜索 crate

```bash
cargo search serde
```

```
在线搜索：https://crates.io/
- 按下载量排序
- 按最新版本
- 按类别筛选
- 按关键字筛选
- 查看文档：https://docs.rs/<crate-name>
```

## 主流 crates 速查

| 类别 | crate | 用途 |
|------|-------|------|
| **Web 框架** | axum | Tokio 生态 HTTP 框架 |
| **Web 框架** | actix-web | 高性能 HTTP 框架 |
| **异步** | tokio | 异步运行时 |
| **序列化** | serde | 序列化框架 |
| **HTTP Client** | reqwest | 同步 + 异步 |
| **数据库** | sqlx | 异步 SQL |
| **CLI** | clap | 命令行参数 |
| **日志** | tracing | 结构化日志 |
| **错误处理** | anyhow | 应用层错误 |
| **错误处理** | thiserror | 库错误 |
| **加密** | rustls | TLS |
| **性能** | rayon | 数据并行 |
| **并发** | crossbeam | 并发原语 |

## 版本管理

```toml
# Cargo.toml 中的版本约束
[dependencies]
serde = "1.0.215"      # 1.x.y，>= 1.0.215, < 2.0.0
tokio = "^1.40"
reqwest = "0.12"
clap = "~3.2"
```

## 文档站（docs.rs）

```
https://docs.rs/

自动为每个 crate 生成文档：
- API 参考
- 示例代码
- Feature flag 切换
- 版本切换
```

## lib.rs 索引

```
https://lib.rs/

crates.io 的"替代前端"：
- 更现代的 UI
- 更好的搜索
- 统计信息
```

## 实战案例：选型决策

```
场景：HTTP 服务
需求：
  - 高并发（10k+ QPS）
  - 异步
  - 易用
  - 生态成熟

候选：
  - axum（tokio 生态，推荐）
  - actix-web（性能强，学习曲线陡）
  - warp（filter 模式，灵活）

决策：用 axum

依赖：
[dependencies]
axum = "0.7"
tokio = { version = "1", features = ["full"] }
tower = "0.5"
serde = { version = "1", features = ["derive"] }
```

## 关联章节

- **03-ecosystem/overview**：生态总览
- **03-ecosystem/cargo**：Cargo
- **03-ecosystem/std-lib**：标准库

## 一句话总结

> **crates.io = Rust 生态的核心基础设施**：130k+ crates、docs.rs 自动文档、lib.rs 现代 UI**。
""")

add("03-ecosystem/std-lib.md", r"""---
title: 标准库
---

# 标准库

Rust 标准库（std）覆盖了现代软件工程的 90% 需求：集合 / IO / 线程 / 网络 / 时间 / 错误处理。

## 一句话总结

> **std = Rust 标准库**。**核心：核心库 core（无 std）+ alloc + std**。**无 std 模式用于嵌入式**。

---

## 三层结构

```
core（必需）
  - 基础类型：i32, bool, char
  - trait：Iterator, Clone, Copy
  - 切片 &[T]、Option<T>

alloc（堆分配）
  - Vec<T>、String、Box<T>
  - Rc<T>、Arc<T>

std（OS 集成）
  - File、网络、线程
  - 时间、命令行参数
```

## 集合

```rust
use std::collections::{HashMap, HashSet, BTreeMap, VecDeque};

// Vec
let mut v = vec![1, 2, 3];
v.push(4);
v.pop();

// HashMap
let mut map = HashMap::new();
map.insert("alice", 30);
let age = map.get("alice").unwrap_or(&0);

// HashSet
let mut set = HashSet::new();
set.insert(1);
set.contains(&1);

// BTreeMap（按 key 排序）
let mut map = BTreeMap::new();
map.insert(3, "three");
map.insert(1, "one");
```

## IO

```rust
use std::fs::File;
use std::io::{BufRead, BufReader, Read, Write};

// 读文件
let file = File::open("data.txt")?;
let reader = BufReader::new(file);
for line in reader.lines() {
    println!("{}", line?);
}

// 写文件
let mut file = File::create("output.txt")?;
writeln!(file, "Hello")?;

// 读所有内容
let content = std::fs::read_to_string("file.txt")?;
```

## 字符串

```rust
let s: String = String::from("hello");
let s: &str = "hello";

// 切片
let s = "hello world";
let hello = &s[0..5];
let world = &s[6..];

// 字符遍历
for c in "你好".chars() {
    println!("{}", c);
}
```

## 线程

```rust
use std::thread;
use std::time::Duration;

let handle = thread::spawn(|| {
    for i in 1..10 {
        println!("hi number {}", i);
        thread::sleep(Duration::from_millis(1));
    }
});

handle.join().unwrap();

// 闭包捕获变量
let x = 5;
let handle = thread::spawn(move || {
    println!("x = {}", x);
});
```

## 智能指针

```rust
use std::rc::Rc;
use std::sync::Arc;
use std::cell::RefCell;
use std::sync::Mutex;

let b = Box::new(5);
let a = Rc::new(5);
let arc = Arc::new(5);
let x = RefCell::new(5);
let m = Mutex::new(5);
```

## 时间

```rust
use std::time::{Duration, Instant, SystemTime};

let start = Instant::now();
do_work();
let elapsed = start.elapsed();

thread::sleep(Duration::from_secs(1));
```

## 错误处理

```rust
fn find_user(id: u32) -> Option<User> { None }
fn read_file(path: &str) -> Result<String, io::Error> { Err(io::Error::other("")) }

panic!("crash and burn");
assert_eq!(add(1, 2), 3);
```

## no_std 模式

```rust
#![no_std]
#![no_main]

use core::panic::PanicInfo;

#[panic_handler]
fn panic(_info: &PanicInfo) -> ! {
    loop {}
}

#[no_mangle]
pub extern "C" fn _start() -> ! {
    loop {}
}
```

## 实战案例：CLI 工具

```rust
use std::fs::File;
use std::io::{self, BufRead, BufReader};

fn count_lines(path: &str) -> io::Result<usize> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    Ok(reader.lines().count())
}

fn main() -> io::Result<()> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <file>", args[0]);
        std::process::exit(1);
    }

    let count = count_lines(&args[1])?;
    println!("Lines: {}", count);
    Ok(())
}
```

## 关联章节

- **03-ecosystem/overview**：生态总览
- **03-ecosystem/cargo**：Cargo
- **06-advanced/smart-pointer**：智能指针深度

## 一句话总结

> **std = Rust 标准库**：集合 / IO / 线程 / 字符串 / 时间 / 错误处理，覆盖现代工程的 90% 需求**。
""")

add("03-ecosystem/tooling.md", r"""---
title: 测试与工具链
---

# 测试与工具链

Rust 工具链一流：rustfmt / clippy / rust-analyzer / cargo test / cargo bench 全内置。

## 一句话总结

> **Rust 工具链 = 格式化 + lint + IDE + 测试 + 基准**。**核心：cargo test / clippy / rust-analyzer**。

---

## cargo test

```rust
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(1, 2), 3);
    }

    #[test]
    #[should_panic]
    fn test_panic() {
        panic!("test panic");
    }

    #[test]
    #[ignore = "expensive test"]
    fn test_expensive() {
        // 长时间运行的测试
    }
}
```

```bash
# 运行所有测试
cargo test

# 详细输出
cargo test -- --nocapture

# 运行特定测试
cargo test test_add

# 运行被 ignore 的测试
cargo test -- --ignored
```

## 集成测试

```bash
# tests/integration_test.rs
use my_library;

#[test]
fn test_integration() {
    assert_eq!(my_library::add(1, 2), 3);
}
```

```bash
cargo test --test integration_test
```

## 文档测试

```rust
/// 加法函数
///
/// # Examples
///
/// ```
/// let result = my_library::add(1, 2);
/// assert_eq!(result, 3);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

```bash
cargo test --doc
```

## 属性测试（proptest）

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn test_add_commutative(a in 0..1000i32, b in 0..1000i32) {
        assert_eq!(add(a, b), add(b, a));
    }
}
```

## Mock 测试

```rust
use mockall::mock;

#[automock]
trait Database {
    fn get_user(&self, id: u32) -> Option<User>;
}
```

## 基准测试（criterion）

```rust
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_add(c: &mut Criterion) {
    c.bench_function("add", |b| {
        b.iter(|| add(black_box(1), black_box(2)));
    });
}

criterion_group!(benches, bench_add);
criterion_main!(benches);
```

```bash
cargo +nightly bench
```

## rustfmt

```bash
cargo fmt
cargo fmt --check  # CI 用
```

```toml
# rustfmt.toml
edition = "2021"
max_width = 100
tab_spaces = 4
```

## clippy

```bash
cargo clippy
cargo clippy -- -W clippy::pedantic
cargo clippy --fix
```

```rust
// clippy 常见提示
let v: Vec<i32> = Vec::new();  // 反模式
v.push(1);
v.push(2);

let mut v = vec![1, 2];  // 推荐
```

## rust-analyzer

```bash
# VSCode：安装 rust-analyzer 扩展
# IntelliJ IDEA：安装 IntelliJ Rust 插件
# vim / neovim：配置 coc-rust-analyzer 或 LSP
```

## cargo 辅助命令

```bash
cargo install cargo-outdated      # 检查过期依赖
cargo install cargo-tree          # 依赖树
cargo install cargo-bloat         # 二进制大小分析
cargo install cargo-audit         # 安全审计
cargo install cargo-watch         # 文件变化自动重新构建
cargo install cargo-edit          # 命令行编辑 Cargo.toml
cargo install cargo-flamegraph    # 火焰图
```

## 实战案例：完整测试栈

```rust
// src/lib.rs
pub fn parse_positive(s: &str) -> Result<u32, String> {
    let n: u32 = s.parse().map_err(|e: std::num::ParseIntError| e.to_string())?;
    if n == 0 {
        return Err("must be positive".to_string());
    }
    Ok(n)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse() {
        assert_eq!(parse_positive("42").unwrap(), 42);
    }

    #[test]
    fn test_zero() {
        assert!(parse_positive("0").is_err());
    }

    #[test]
    fn test_negative() {
        assert!(parse_positive("-1").is_err());
    }
}
```

## 关联章节

- **03-ecosystem/overview**：生态总览
- **03-ecosystem/cargo**：Cargo
- **03-ecosystem/std-lib**：标准库

## 一句话总结

> **Rust 工具链 = 格式化 + lint + IDE + 测试 + 基准**。**核心：cargo test / clippy / rust-analyzer**。
""")

# ============ 04-concurrency (4 stubs) ============
add("04-concurrency/threads.md", r"""---
title: 线程与 Thread
---

# 线程与 Thread

Rust 标准库的 std::thread 提供原生线程支持，类型系统保证线程安全。

## 一句话总结

> **std::thread = 原生 1:1 OS 线程**。**核心：spawn / join / Send + 'static 闭包**。

---

## 基本用法

```rust
use std::thread;
use std::time::Duration;

fn main() {
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {} from the spawned thread!", i);
            thread::sleep(Duration::from_millis(1));
        }
    });

    for i in 1..5 {
        println!("hi number {} from the main thread!", i);
        thread::sleep(Duration::from_millis(1));
    }

    handle.join().unwrap();
}
```

## move 闭包

```rust
let v = vec![1, 2, 3];

let handle = thread::spawn(move || {
    println!("Vector: {:?}", v);
});

handle.join().unwrap();
```

## 线程返回 Result

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_file(path: String) -> io::Result<String> {
    let mut content = String::new();
    File::open(path)?.read_to_string(&mut content)?;
    Ok(content)
}

fn main() -> io::Result<()> {
    let handle = thread::spawn(|| {
        read_file("data.txt".to_string())
    });

    match handle.join() {
        Ok(Ok(content)) => println!("Read: {}", content),
        Ok(Err(e)) => eprintln!("Error: {}", e),
        Err(_) => eprintln!("Thread panicked"),
    }

    Ok(())
}
```

## 线程局部存储

```rust
use std::cell::RefCell;

thread_local! {
    static COUNTER: RefCell<u32> = RefCell::new(0);
}

fn main() {
    for _ in 0..10 {
        thread::spawn(|| {
            COUNTER.with(|c| {
                *c.borrow_mut() += 1;
                println!("Thread counter: {}", c.borrow());
            });
        });
    }
}
```

## 4 个线程反模式

```rust
// 反模式 1：未等待线程结束
thread::spawn(|| do_work());

// 反模式 2：数据竞争（编译错误）
let mut counter = 0;
thread::spawn(|| counter += 1);

// 反模式 3：线程数无限制
for _ in 0..1_000_000 {
    thread::spawn(|| do_work());
}

// 反模式 4：阻塞主线程
let handle = thread::spawn(|| do_work());
// 没有 handle.join()
```

## 关联章节

- **04-concurrency/overview**：并发总览
- **04-concurrency/channels**：Channel 与共享状态
- **04-concurrency/async-await**：async-await

## 一句话总结

> **std::thread = 原生线程 + 类型安全**。**spawn / join / Send + 'static 闭包是核心 API**。
""")

add("04-concurrency/async-await.md", r"""---
title: async / await
---

# async / await

Rust async-await 是零成本抽象：编译为状态机，运行时由 tokio / async-std 调度。

## 一句话总结

> **async-await = 零成本协程**。**核心：Future trait / 状态机 / 运行时调度**。**与线程对比：内存更省、并发更高**。

---

## 基本语法

```rust
async fn fetch_url(url: &str) -> Result<String, reqwest::Error> {
    let body = reqwest::get(url).await?.text().await?;
    Ok(body)
}

// 调用：返回 Future（不执行）
let future = fetch_url("https://example.com");

// .await 触发 Future 执行
let body = fetch_url("https://example.com").await?;
```

## Future trait

```rust
trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context) -> Poll<Self::Output>;
}

enum Poll<T> {
    Ready(T),
    Pending,
}
```

## tokio runtime

```rust
// tokio 宏（推荐）
#[tokio::main]
async fn main() {
    let body = fetch_url("https://example.com").await.unwrap();
    println!("{}", body);
}
```

## 并发模式

```rust
// tokio::join! 并发执行
async fn parallel() {
    let (a, b, c) = tokio::join!(
        fetch_url("https://a.com"),
        fetch_url("https://b.com"),
        fetch_url("https://c.com"),
    );
}

// tokio::spawn 后台任务
async fn spawn_example() {
    let handle = tokio::spawn(async {
        tokio::time::sleep(Duration::from_secs(10)).await;
        "done"
    });
    do_other_work().await;
    let result = handle.await.unwrap();
}

// tokio::select! 等待多个 Future 任一完成
async fn select_example() {
    tokio::select! {
        result = task_a() => println!("a: {:?}", result),
        result = task_b() => println!("b: {:?}", result),
        _ = tokio::time::sleep(Duration::from_secs(5)) => println!("timeout"),
    }
}
```

## 4 个 async-await 反模式

```rust
// 反模式 1：在 async 中阻塞
async fn read_file_async() -> std::io::Result<String> {
    tokio::fs::read_to_string("file.txt").await  // 用 tokio 而非 std
}

// 反模式 2：持有锁跨 .await
async fn good(mutex: Arc<Mutex<i32>>) {
    {
        let mut guard = mutex.lock().unwrap();
        *guard += 1;
    }
    some_async_op().await;
}

// 反模式 3：spawn_blocking 滥用
async fn heavy_compute() {
    tokio::task::spawn_blocking(|| {
        expensive_calculation()
    }).await.unwrap();
}

// 反模式 4：async fn 递归死循环
async fn recursive() {
    recursive().await;
}
```

## 实战案例：HTTP 服务器

```rust
use axum::{routing::get, Router};
use std::net::SocketAddr;

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(|| async { "Hello, world!" }))
        .route("/users/:id", get(get_user));

    let addr = SocketAddr::from(([0, 0, 0, 0], 3000));
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn get_user(Path(id): Path<u32>) -> String {
    format!("User: {}", id)
}
```

## 关联章节

- **04-concurrency/overview**：并发总览
- **04-concurrency/tokio**：Tokio 运行时
- **06-advanced/async-ecosystem**：异步生态对比

## 一句话总结

> **async-await = Rust 的零成本协程**。**编译为状态机，运行时调度，与线程互补**。
""")

add("04-concurrency/tokio.md", r"""---
title: Tokio 运行时
---

# Tokio 运行时

Tokio 是 Rust 生态最成熟的异步运行时：多线程调度 + IO reactor + 定时器 + 同步原语。

## 一句话总结

> **Tokio = Rust 异步事实标准**。**核心：reactor + 多线程调度 + timer + sync**。**生态完整（axum / hyper / tonic）**。

---

## 添加 Tokio

```toml
# Cargo.toml
[dependencies]
tokio = { version = "1", features = ["full"] }
```

```bash
# 全功能
features = ["full"]

# 按需
features = ["rt-multi-thread", "macros", "net", "sync", "time"]
```

## 启动 Runtime

```rust
#[tokio::main]
async fn main() {
    // 主任务
}
```

## 5 大核心模块

```rust
// 1. tokio::spawn
let handle = tokio::spawn(async {
    do_work().await
});

// 2. tokio::time
use tokio::time::{sleep, timeout, Duration};
sleep(Duration::from_secs(1)).await;
timeout(Duration::from_secs(5), some_async_op()).await?;

// 3. tokio::net
use tokio::net::{TcpListener, TcpStream};
let listener = TcpListener::bind("127.0.0.1:8080").await?;
let (stream, addr) = listener.accept().await?;

// 4. tokio::sync
use tokio::sync::{mpsc, Mutex, RwLock, Semaphore};
let (tx, mut rx) = mpsc::channel(32);

// 5. tokio::fs
let content = tokio::fs::read_to_string("file.txt").await?;
```

## 同步原语

```rust
use tokio::sync::{mpsc, oneshot, broadcast, watch, Mutex, RwLock, Semaphore};

// mpsc：多生产者单消费者
let (tx, mut rx) = mpsc::channel::<String>(100);
tx.send("hello".to_string()).await?;
let msg = rx.recv().await;

// oneshot：单次发送
let (tx, rx) = oneshot::channel::<i32>();
tx.send(42).unwrap();
let value = rx.await.unwrap();

// broadcast：多对多
let (tx, _) = broadcast::channel::<String>(100);
let mut rx1 = tx.subscribe();
tx.send("hello".to_string()).unwrap();
```

## 性能调优

```rust
// 1. 控制并发
use tokio::sync::Semaphore;
let sem = Arc::new(Semaphore::new(100));
for req in reqs {
    let permit = sem.clone().acquire_owned().await.unwrap();
    tokio::spawn(async move {
        handle(req).await;
        drop(permit);
    });
}
```

## 实战案例：并发爬虫

```rust
use reqwest::Client;
use tokio::sync::Semaphore;
use std::sync::Arc;

#[tokio::main]
async fn main() {
    let urls = vec![
        "https://example.com",
        "https://example.org",
    ];

    let client = Client::new();
    let sem = Arc::new(Semaphore::new(10));  // 最多 10 并发

    let mut handles = vec![];
    for url in urls {
        let permit = sem.clone().acquire_owned().await.unwrap();
        let client = client.clone();
        let handle = tokio::spawn(async move {
            let body = client.get(url).send().await.unwrap().text().await.unwrap();
            println!("{}: {} bytes", url, body.len());
            drop(permit);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.await.unwrap();
    }
}
```

## 关联章节

- **04-concurrency/overview**：并发总览
- **04-concurrency/async-await**：async-await
- **04-concurrency/channels**：Channel 与共享状态

## 一句话总结

> **Tokio = Rust 异步生态的事实标准**：完整 runtime + 同步原语 + 网络 / IO / 定时器**。
""")

add("04-concurrency/channels.md", r"""---
title: Channel 与共享状态
---

# Channel 与共享状态

并发原语两大阵营：消息传递（Channel）与共享状态（Arc + Mutex）。Rust 都提供类型安全版本。

## 一句话总结

> **Channel = 消息传递、Arc<Mutex> = 共享状态**。**Rust 哲学："恐惧共享，鼓励消息传递"**。

---

## std::sync::mpsc

```rust
use std::sync::mpsc;
use std::thread;

let (tx, rx) = mpsc::channel();
thread::spawn(move || {
    tx.send(42).unwrap();
});
let value = rx.recv().unwrap();

// 多生产者
let (tx, rx) = mpsc::channel();
for i in 0..3 {
    let tx_clone = tx.clone();
    thread::spawn(move || {
        tx_clone.send(i).unwrap();
    });
}
drop(tx);

for received in rx {
    println!("{}", received);
}
```

## crossbeam-channel

```rust
use crossbeam_channel::{unbounded, bounded, select};

let (tx, rx) = unbounded();
let (tx2, rx2) = unbounded();

tx.send(1).unwrap();

select! {
    recv(rx) -> msg => println!("rx: {:?}", msg),
    recv(rx2) -> msg => println!("rx2: {:?}", msg),
}

// bounded
let (tx, rx) = bounded(100);
```

## Arc + Mutex

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}
```

## RwLock（读写锁）

```rust
use std::sync::{Arc, RwLock};

let data = Arc::new(RwLock::new(vec![1, 2, 3]));

{
    let r1 = data.read().unwrap();
    let r2 = data.read().unwrap();
    println!("{:?}", r1);
}

{
    let mut w = data.write().unwrap();
    w.push(4);
}
```

## 原子类型

```rust
use std::sync::atomic::{AtomicUsize, Ordering};

let counter = AtomicUsize::new(0);
counter.fetch_add(1, Ordering::SeqCst);
let value = counter.load(Ordering::SeqCst);
counter.store(42, Ordering::SeqCst);
```

## tokio 异步 Channel

```rust
use tokio::sync::{mpsc, oneshot, broadcast, watch};

let (tx, mut rx) = mpsc::channel::<String>(100);
tx.send("hello".to_string()).await.unwrap();
let msg = rx.recv().await;

let (tx, rx) = oneshot::channel::<i32>();
let value = rx.await.unwrap();

let (tx, _) = broadcast::channel::<String>(100);
let mut rx1 = tx.subscribe();

let (tx, rx) = watch::channel(0);
let value = rx.borrow().clone();
```

## 死锁 4 大场景

```
场景 1：循环等待
场景 2：持锁等待异步操作
场景 3：回调中重新获取锁
场景 4：信号量泄漏
```

## 实战案例：生产者-消费者

```rust
use crossbeam_channel::bounded;
use std::thread;
use std::time::Duration;

fn main() {
    let (tx, rx) = bounded(10);

    for i in 0..3 {
        let tx = tx.clone();
        thread::spawn(move || {
            for j in 0..100 {
                tx.send(format!("P{}-{}", i, j)).unwrap();
                thread::sleep(Duration::from_millis(10));
            }
        });
    }
    drop(tx);

    let mut handles = vec![];
    for i in 0..2 {
        let rx = rx.clone();
        let handle = thread::spawn(move || {
            while let Ok(msg) = rx.recv() {
                println!("C{} received: {}", i, msg);
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }
}
```

## 关联章节

- **04-concurrency/overview**：并发总览
- **04-concurrency/threads**：线程
- **04-concurrency/tokio**：Tokio 运行时

## 一句话总结

> **Channel 与 Arc<Mutex> 各有适用场景**：Channel 用于消息流、Arc<Mutex> 用于共享可变状态。**Rust 类型系统保证两者都线程安全**。
""")

# ============ 05-systems (5 stubs) ============
add("05-systems/unsafe.md", r"""---
title: unsafe Rust
---

# unsafe Rust

unsafe 块绕过 Rust 编译器的部分检查（4 种操作），允许直接操作内存和硬件。

## 一句话总结

> **unsafe = 关闭 4 种编译期检查**。**核心：解引用裸指针 / 调用 unsafe fn / 访问可变静态 / 实现 unsafe Trait**。**用途：性能优化 + 硬件抽象 + FFI**。

---

## 4 种 unsafe 超能力

```rust
unsafe fn dangerous() {}

// 1. 解引用裸指针
let mut num = 5;
let r1 = &num as *const i32;
let r2 = &mut num as *mut i32;

unsafe {
    println!("r1 is: {}", *r1);
    *r2 = 10;
}

// 2. 调用 unsafe 函数
unsafe {
    dangerous();
}

// 3. 访问或修改可变静态变量
static mut COUNTER: u32 = 0;
unsafe {
    COUNTER += 1;
}

// 4. 实现 unsafe Trait
unsafe trait Send {}
unsafe impl Send for MyType {}
```

## unsafe 块的范围

```rust
fn mixed() {
    let mut num = 5;
    let r = &mut num as *mut i32;

    // unsafe 块限制在最小范围
    unsafe {
        *r = 10;
    }

    println!("{}", num);
}
```

## 何时用 unsafe

```rust
// 1. 调用 C 库（FFI）
extern "C" {
    fn abs(input: i32) -> i32;
}

unsafe {
    println!("{}", abs(-5));
}

// 2. 性能关键路径（绕过边界检查）
let v = vec![1, 2, 3];
unsafe {
    let elem = v.get_unchecked(1);
    println!("{}", elem);
}

// 3. 嵌入式 / OS 开发
unsafe {
    let peripherals = cortex_m::Peripherals::take().unwrap();
    peripherals.GPIOA.bsrr.write(|w| w.bits(1));
}

// 4. 自定义数据结构
pub struct Vec<T> {
    ptr: *mut T,
    len: usize,
    cap: usize,
}

impl<T> Vec<T> {
    pub fn push(&mut self, val: T) {
        unsafe {
            if self.len == self.cap {
                self.grow();
            }
            std::ptr::write(self.ptr.add(self.len), val);
            self.len += 1;
        }
    }
}

// 5. 内联汇编
use std::arch::asm;
unsafe {
    asm!("nop");
}
```

## 5 大安全抽象模式

```rust
// 模式 1：unsafe 封装在 safe API 内
pub struct SafeVec<T> {
    ptr: *mut T,
    len: usize,
    cap: usize,
}

unsafe impl<T: Send> Send for SafeVec<T> {}
unsafe impl<T: Sync> Sync for SafeVec<T> {}

// 模式 2：模块化 unsafe
mod internal {
    pub unsafe fn unchecked_operation() { }
}

pub fn safe_wrapper() {
    unsafe {
        internal::unchecked_operation();
    }
}

// 模式 3：unsafe trait
pub unsafe trait Zeroable {}
unsafe impl Zeroable for i32 {}

// 模式 4：RAII 自动清理
pub struct Guard {
    ptr: *mut T,
}

impl Drop for Guard {
    fn drop(&mut self) {
        unsafe {
            std::ptr::drop_in_place(self.ptr);
        }
    }
}
```

## Miri：检测 unsafe UB

```bash
rustup +nightly component add miri
cargo +nightly miri test
```

## 5 大 unsafe 反模式

```
反模式 1：绕过借用检查 → 越界
反模式 2：双重释放
反模式 3：use-after-free
反模式 4：数据竞争
反模式 5：未初始化内存
```

## 关联章节

- **05-systems/overview**：系统编程
- **05-systems/ffi**：FFI
- **02-types-traits/advanced-types**：PhantomData / MaybeUninit

## 一句话总结

> **unsafe = 性能 + 控制 + 互操作**。**用 unsafe 封装安全抽象，避免散布 unsafe 代码**。
""")

add("05-systems/ffi.md", r"""---
title: FFI 与 C 互操作
---

# FFI 与 C 互操作

Rust 通过 FFI（外部函数接口）与 C 库互操作：调用 C 函数、从 C 调用 Rust、用 bindgen 自动生成绑定。

## 一句话总结

> **FFI = Rust 与 C 的双向桥梁**。**核心：extern "C" / #[no_mangle] / bindgen / cbindgen**。

---

## Rust 调用 C 库

```rust
extern "C" {
    fn abs(input: i32) -> i32;
    fn strlen(s: *const c_char) -> usize;
}

use std::os::raw::c_char;

fn main() {
    unsafe {
        println!("abs(-5) = {}", abs(-5));

        let c_str = b"hello\0";
        let len = strlen(c_str.as_ptr() as *const c_char);
        println!("strlen = {}", len);
    }
}
```

## 链接 C 库

```rust
// build.rs
fn main() {
    cc::Build::new()
        .file("src/native/helper.c")
        .compile("helper");
}
```

## bindgen：自动生成绑定

```rust
// build.rs
use std::env;
use std::path::PathBuf;

fn main() {
    println!("cargo:rerun-if-changed=wrapper.h");

    let bindings = bindgen::Builder::default()
        .header("wrapper.h")
        .parse_callbacks(Box::new(bindgen::CargoCallbacks))
        .generate()
        .expect("Unable to generate bindings");

    let out_path = PathBuf::from(env::var("OUT_DIR").unwrap());
    bindings
        .write_to_file(out_path.join("bindings.rs"))
        .unwrap();
}
```

```c
// wrapper.h
#include <stdio.h>

int add(int a, int b);
char* greet(const char* name);
```

```rust
// src/lib.rs
#![allow(non_snake_case)]
include!(concat!(env!("OUT_DIR"), "/bindings.rs"));

use std::ffi::{CStr, CString};

pub fn safe_add(a: i32, b: i32) -> i32 {
    unsafe { add(a, b) }
}

pub fn safe_greet(name: &str) -> String {
    let c_name = CString::new(name).unwrap();
    unsafe {
        let ptr = greet(c_name.as_ptr());
        let result = CStr::from_ptr(ptr).to_string_lossy().into_owned();
        libc::free(ptr as *mut libc::c_void);
        result
    }
}
```

## Rust 暴露给 C

```rust
#[no_mangle]
pub extern "C" fn rust_function(x: i32) -> i32 {
    x * 2
}

#[no_mangle]
pub extern "C" fn rust_greet(name: *const c_char) -> *mut c_char {
    unsafe {
        let c_str = CStr::from_ptr(name);
        let name_str = c_str.to_str().unwrap_or("unknown");
        let result = format!("Hello, {}!", name_str);
        CString::new(result).unwrap().into_raw()
    }
}

#[no_mangle]
pub extern "C" fn rust_greet_free(s: *mut c_char) {
    unsafe {
        if !s.is_null() {
            drop(CString::from_raw(s));
        }
    };
}
```

## cbindgen：自动生成 C 头文件

```toml
# Cargo.toml
[lib]
crate-type = ["staticlib", "cdylib"]
```

```bash
cargo install cbindgen
cbindgen --config cbindgen.toml --crate my_rust_lib --output my_rust_lib.h
```

## 类型映射

```rust
// Rust → C
i32, i64          → int32_t, int64_t
u8, u32           → uint8_t, uint32_t
f32, f64          → float, double
&str (String)     → const char*
Vec<T>            → T* + len
Option<T>         → T* + null
```

## 实战案例：调用 SQLite

```rust
use rusqlite::{Connection, Result};

fn main() -> Result<()> {
    let conn = Connection::open("test.db")?;

    conn.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)",
        [],
    )?;

    conn.execute("INSERT INTO users (name) VALUES (?1)", ["alice"])?;

    let mut stmt = conn.prepare("SELECT id, name FROM users")?;
    let users = stmt.query_map([], |row| {
        Ok((row.get(0)?, row.get(1)?))
    })?;

    for user in users {
        println!("{:?}", user?);
    }

    Ok(())
}
```

## 实战案例：Python 扩展

```rust
use pyo3::prelude::*;

#[pyfunction]
fn double(x: i64) -> i64 {
    x * 2
}

#[pymodule]
fn my_extension(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(double, m)?)?;
    Ok(())
}
```

```python
import my_extension
print(my_extension.double(21))  # 42
```

## 关联章节

- **05-systems/overview**：系统编程
- **05-systems/unsafe**：unsafe Rust
- **05-systems/embedded**：嵌入式 Rust

## 一句话总结

> **FFI = Rust ↔ C 的双向桥梁**：extern "C" 调入、#[no_mangle] 调出、bindgen/cbindgen 自动生成**。
""")

add("05-systems/embedded.md", r"""---
title: 嵌入式 Rust
---

# 嵌入式 Rust

Rust 嵌入式生态成熟：用 no std 编程微控制器，类型安全 + 零运行时开销 + 强大生态。

## 一句话总结

> **嵌入式 Rust = no_std + 裸机 + 外设访问**。**核心：cortex-m / embedded-hal / RTIC / probe-rs**。

---

## 嵌入式 Rust 工具链

```bash
rustup target add thumbv7em-none-eabihf  # ARM Cortex-M4F
rustup target add riscv32imc-unknown-none-elf  # RISC-V

cargo install probe-rs
cargo install cargo-binutils
```

## Hello LED（STM32）

```rust
#![no_std]
#![no_main]

use panic_halt as _;
use cortex_m_rt::entry;
use stm32f4::stm32f407::{GPIOA, RCC};

#[entry]
fn main() -> ! {
    let peripherals = stm32f407::Peripherals::take().unwrap();
    let rcc = &peripherals.RCC;
    let gpioa = &peripherals.GPIOA;

    rcc.ahb1enr.modify(|_, w| w.gpioaen().set_bit());

    gpioa.moder.modify(|_, w| unsafe { w.bits(0b01 << (5 * 2)) });

    loop {
        gpioa.bsrr.write(|w| unsafe { w.bits(1 << 5) });
        for _ in 0..1_000_000 { cortex_m::asm::nop(); }
        gpioa.bsrr.write(|w| unsafe { w.bits(1 << (5 + 16)) });
        for _ in 0..1_000_000 { cortex_m::asm::nop(); }
    }
}
```

## embedded-hal：硬件抽象

```rust
use embedded_hal::digital::v2::OutputPin;

struct Led<P: OutputPin> {
    pin: P,
}

impl<P: OutputPin> Led<P> {
    fn new(pin: P) -> Self {
        Self { pin }
    }

    fn on(&mut self) -> Result<(), P::Error> {
        self.pin.set_high()
    }

    fn off(&mut self) -> Result<(), P::Error> {
        self.pin.set_low()
    }
}
```

## RTIC：实时中断驱动并发

```toml
[dependencies]
rtic = "1.0"
```

```rust
#![no_std]
#![no_main]

use rtic::app;
use panic_halt as _;

#[app(device = stm32f4::stm32f407, peripherals = true)]
const APP: () = {
    struct Resources {
        led: gpioa::PA5<Output<PushPull>>,
    }

    #[init]
    fn init(cx: init::Context) -> init::LateResources {
        let dp = cx.device;
        let gpioa = dp.GPIOA.split();
        let led = gpioa.pa5.into_push_pull_output();

        init::LateResources { led }
    }

    #[task(binds = TIM2, resources = [led])]
    fn toggle(cx: toggle::Context) {
        cx.resources.led.toggle().unwrap();
    }

    #[idle]
    fn idle(_cx: idle::Context) -> ! {
        loop {
            cortex_m::asm::wfi();
        }
    }
};
```

## Embassy：现代异步嵌入式

```toml
[dependencies]
embassy-stm32 = "0.1"
embassy-executor = "0.3"
```

```rust
#![no_std]
#![no_main]

use embassy_executor::Spawner;
use embassy_time::{Duration, Timer};
use embassy_stm32::gpio::{Output, Level, Speed};
use panic_halt as _;

#[embassy_executor::main]
async fn main(_spawner: Spawner) {
    let p = embassy_stm32::init(Default::default());
    let mut led = Output::new(p.PA5, Level::High, Speed::Low);

    loop {
        led.set_high();
        Timer::after(Duration::from_millis(500)).await;
        led.set_low();
        Timer::after(Duration::from_millis(500)).await;
    }
}
```

## probe-rs：烧录 + 调试

```bash
cargo run --release
probe-rs debug --chip STM32F407VGTx
probe-rs run --chip STM32F407VGTx
```

## 实战案例：传感器数据采集

```rust
use embedded_hal::blocking::i2c::{Write, Read};

struct Bme280<I2C> {
    i2c: I2C,
    address: u8,
}

impl<I2C> Bme280<I2C>
where
    I2C: Write + Read,
{
    fn new(i2c: I2C) -> Self {
        Self { i2c, address: 0x76 }
    }

    fn read_temperature(&mut self) -> Result<f32, I2C::Error> {
        self.i2c.write(self.address, &[0xF4, 0x27])?;

        let mut buf = [0u8; 3];
        self.i2c.write(self.address, &[0xF8])?;
        self.i2c.read(self.address, &mut buf)?;

        let raw = ((buf[0] as u32) << 12) | ((buf[1] as u32) << 4) | ((buf[2] as u32) >> 4);
        Ok((raw as f32) / 5120.0)
    }
}
```

## 关联章节

- **05-systems/overview**：系统编程
- **05-systems/ffi**：FFI
- **05-systems/unsafe**：unsafe Rust

## 一句话总结

> **嵌入式 Rust = no_std + HAL 抽象 + RTIC/Embassy**。**类型安全 + 零开销，让嵌入式更可靠**。
""")

add("05-systems/wasm.md", r"""---
title: WebAssembly
---

# WebAssembly

Rust 是 WebAssembly 编译目标的事实标准：单一语言，浏览器 / Node.js / 边缘计算 / Serverless 全覆盖。

## 一句话总结

> **WASM = 浏览器 + 边缘 + Serverless 的跨平台运行时**。**核心：wasm-bindgen / wasm-pack / wasmtime / WasmEdge**。

---

## 安装 WASM 工具链

```bash
rustup target add wasm32-unknown-unknown
rustup target add wasm32-wasi

cargo install wasm-pack
```

## 第一个 WASM 模块

```rust
// src/lib.rs
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u64 {
    let mut a: u64 = 0;
    let mut b: u64 = 1;
    for _ in 0..n {
        let temp = a + b;
        a = b;
        b = temp;
    }
    a
}
```

```bash
wasm-pack build --target web

# 输出
pkg/
├── my_code.d.ts
├── my_code.js
├── my_code_bg.wasm
└── my_code_bg.wasm.d.ts
```

## 在 JavaScript 中调用

```javascript
import init, { add, fibonacci } from "./pkg/my_code.js";

await init();

console.log(add(2, 3));            // 5
console.log(fibonacci(10));         // 55
```

## JS 互操作

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
extern "C" {
    pub fn alert(s: &str);
}

#[wasm_bindgen]
pub fn greet(name: &str) {
    alert(&("Hello, ".to_string() + name));
}
```

## WASI：服务端 WASM

```rust
use std::io::{self, Read, Write};

fn main() -> io::Result<()> {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    let output = input.to_uppercase();
    io::stdout().write_all(output.as_bytes())?;
    Ok(())
}
```

```bash
cargo build --target wasm32-wasi --release
wasmtime target/wasm32-wasi/release/my_app.wasm < input.txt > output.txt
```

## 边缘计算（Cloudflare Workers）

```rust
use worker::*;

#[event(fetch)]
async fn main(req: Request, env: Env, ctx: Context) -> Result<Response> {
    let path = req.path();

    let response = match path.as_str() {
        "/api/hello" => {
            let name = req.query().get("name").unwrap_or("World");
            Response::ok(format!("Hello, {}!", name))?
        }
        "/" => Response::ok("Rust WASM Worker")?,
        _ => Response::error("Not Found", 404)?,
    };

    Ok(response)
}
```

## 4 大 WASM 优势

```
1. 跨平台：浏览器 / Node.js / Deno / Workers / Wasmtime
2. 性能：接近原生（V8 优化 + AOT 编译）
3. 内存安全：沙箱执行
4. 小体积：gzip 后几十 KB
```

## 实战案例：图像处理

```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn grayscale(input: &[u8], width: u32, height: u32) -> Vec<u8> {
    let mut output = Vec::with_capacity(input.len());
    for chunk in input.chunks(4) {
        let r = chunk[0] as f32;
        let g = chunk[1] as f32;
        let b = chunk[2] as f32;
        let gray = (0.299 * r + 0.587 * g + 0.114 * b) as u8;
        output.extend_from_slice(&[gray, gray, gray, chunk[3]]);
    }
    output
}
```

## 关联章节

- **05-systems/overview**：系统编程
- **05-systems/ffi**：FFI
- **05-systems/performance**：性能优化

## 一句话总结

> **WASM = Rust 的跨平台目标**：浏览器 / Node.js / 边缘 / Serverless / 桌面，唯一语言覆盖所有场景**。
""")

add("05-systems/performance.md", r"""---
title: 性能优化
---

# 性能优化

Rust 的"零成本抽象"已接近最优，但仍有优化空间：剖析 + SIMD + 内存布局 + 并行。

## 一句话总结

> **性能优化 = 剖析先行 + 针对性优化 + 测量验证**。**核心：cargo flamegraph / criterion / SIMD / rayon**。

---

## 性能优化 4 步法

```
1. Measure  -  测量
2. Profile  -  剖析
3. Optimize -  优化
4. Verify   -  验证
```

## 1. 测量 + 剖析

```bash
# 编译优化
cargo build --release

# 火焰图
cargo install flamegraph
cargo flamegraph

# 基准测试
[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "my_bench"
harness = = "false"
```

```rust
// benches/my_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};

fn bench_process(c: &mut Criterion) {
    c.bench_function("process", |b| {
        b.iter(|| process(black_box(100)));
    });
}

criterion_group!(benches, bench_process);
criterion_main!(benches);
```

## 2. 内存布局优化

```rust
// 默认布局
struct Unoptimized {
    a: u8,
    b: u32,
    c: u8,
}

// 手动排序（按大小降序）
struct Optimized {
    b: u32,
    a: u8,
    c: u8,
}

#[repr(C)]
struct CStruct {
    a: u8,
    b: u32,
    c: u8,
}

// 避免 Box 包装小类型
let x = Box::new(42);  // 反模式
let x: i32 = 42;  // 推荐
```

## 3. SIMD

```rust
use std::arch::x86_64::*;

#[target_feature(enable = "avx2")]
unsafe fn simd_add(a: &[f32; 8], b: &[f32; 8]) -> [f32; 8] {
    let va = _mm256_loadu_ps(a.as_ptr());
    let vb = _mm256_loadu_ps(b.as_ptr());
    let result = _mm256_add_ps(va, vb);
    let mut out = [0.0f32; 8];
    _mm256_storeu_ps(out.as_mut_ptr(), result);
    out
}
```

## 4. 并行（rayon）

```rust
use rayon::prelude::*;

let sum: i64 = (1..=1_000_000).into_par_iter().sum();

let mut data = vec![3, 1, 4, 1, 5, 9, 2, 6];
data.par_sort();

let evens: Vec<i32> = data.par_iter().filter(|x| *x % 2 == 0).cloned().collect();
```

## 5. 零拷贝

```rust
use std::borrow::Cow;

fn process_good(input: &str) -> Cow<str> {
    if input.chars().all(|c| c.is_uppercase() || !c.is_alphabetic()) {
        Cow::Borrowed(input)
    } else {
        Cow::Owned(input.to_uppercase())
    }
}

fn first_word(s: &str) -> &str {
    s.split_whitespace().next().unwrap_or("")
}
```

## 6. 避免分配

```rust
const PREFIX: &str = "item-";

fn better(n: usize) -> Vec<String> {
    (0..n).map(|i| format!("{}{}", PREFIX, i)).collect()
}
```

## 7. 异步并行（tokio）

```rust
async fn fetch_all() {
    let (a, b, c) = tokio::join!(
        fetch_url("https://a.com"),
        fetch_url("https://b.com"),
        fetch_url("https://c.com"),
    );
}
```

## 8. 二进制优化

```toml
# Cargo.toml
[profile.release]
opt-level = 3
lto = "fat"
codegen-units = 1
panic = "abort"
strip = true
```

```bash
cargo install cargo-bloat
cargo bloat --release --crates

upx --best target/release/my_app
```

## 实战案例：JSON 解析性能对比

```rust
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct User {
    id: u32,
    name: String,
    email: String,
}

fn parse_users(json: &str) -> Vec<User> {
    serde_json::from_str(json).unwrap()
}

// 性能：
// - from_str: 1.0x baseline
// - borrowed: 1.5-2x 更快（用 &str 替代 String）
// - streaming: 适合 1GB+ 文件
```

## 关联章节

- **05-systems/overview**：系统编程
- **05-systems/unsafe**：unsafe 优化
- **05-systems/wasm**：WASM 性能

## 一句话总结

> **性能优化 = 剖析先行 + 针对性优化 + 测量验证**。**Rust 零成本抽象让大部分代码已经接近最优**。
""")

# ============ 06-advanced (5 stubs) ============
add("06-advanced/macro.md", r"""---
title: 宏 Macro
---

# 宏 Macro

Rust 宏是"编译期代码生成"：声明宏（macro_rules!）和过程宏（proc_macro）两大类。

## 一句话总结

> **宏 = 编译期代码生成**。**核心：macro_rules!（声明宏）+ proc_macro（过程宏）**。**用途：DSL / derive / 代码减少**。

---

## macro_rules! 声明宏

```rust
macro_rules! say_hello {
    () => {
        println!("Hello!");
    };
}

say_hello!();
```

```rust
macro_rules! create_function {
    ($func_name:ident) => {
        fn $func_name() {
            println!("called {:?}", stringify!($func_name));
        }
    };
}

create_function!(foo);
foo();
```

## 宏的捕获类型

```
ident        标识符
expr         表达式
ty           类型
pat          模式
path         路径
literal      字面量
tt           单个 token tree
$($x:tt)*    重复 0+ 次
$($x:tt)+    重复 1+ 次
```

## 重复模式

```rust
macro_rules! my_vec {
    ($($x:expr),* $(,)?) => {
        {
            let mut v = Vec::new();
            $(
                v.push($x);
            )*
            v
        }
    };
}

let v = my_vec![1, 2, 3];
```

## 过程宏（proc_macro）

```toml
# Cargo.toml
[package]
name = "my_macro"

[lib]
proc-macro = true
```

### 派生宏

```rust
use proc_macro::TokenStream;
use quote::quote;
use syn::{parse_macro_input, DeriveInput};

#[proc_macro_derive(Hello)]
pub fn hello_derive(input: TokenStream) -> TokenStream {
    let ast = parse_macro_input!(input as DeriveInput);
    let name = &ast.ident;
    let gen = quote! {
        impl #name {
            pub fn hello(&self) {
                println!("Hello from {}!", stringify!(#name));
            }
        }
    };
    gen.into()
}
```

```rust
use my_macro::Hello;

#[derive(Hello)]
struct MyStruct;

let s = MyStruct;
s.hello();
```

## 调试宏

```bash
cargo install cargo-expand
cargo expand
```

## 实战案例：JSON 查询 DSL

```rust
macro_rules! json {
    (null) => { JsonValue::Null };
    (true) => { JsonValue::Bool(true) };
    ([ $($elem:tt),* $(,)? ]) => {
        JsonValue::Array(vec![$(json!($elem)),*])
    };
    ({ $($key:tt : $value:tt),* $(,)? }) => {
        JsonValue::Object({
            let mut map = HashMap::new();
            $( map.insert($key.to_string(), json!($value)); )*
            map
        })
    };
    ($other:expr) => { JsonValue::from($other) };
}
```

## 关联章节

- **02-types-traits/overview**：类型系统
- **06-advanced/closure-and-iterator**：闭包与迭代器
- **03-ecosystem/cargo**：Cargo 工具链

## 一句话总结

> **宏 = Rust 的元编程**。**macro_rules! 适合简单 DSL、proc_macro 适合复杂 derive 与属性**。
""")

add("06-advanced/closure-and-iterator.md", r"""---
title: 闭包与迭代器
---

# 闭包与迭代器

闭包是匿名函数，迭代器是惰性序列。两者结合是 Rust 函数式编程的核心。

## 一句话总结

> **闭包 + 迭代器 = Rust 函数式编程**。**核心：Fn / FnMut / FnOnce / Iterator trait**。**性能：零成本抽象**。

---

## 闭包基础

```rust
let add = |a, b| a + b;

// 捕获环境
let x = 5;
let print_x = || println!("x = {}", x);

// 移动所有权
let s = String::from("hello");
let consume = move || println!("{}", s);
```

## 3 大闭包 Trait

```rust
fn call_fn<F: Fn()>(f: F) {
    f();
    f();
}

fn call_fn_mut<F: FnMut()>(mut f: F) {
    f();
    f();
}

fn call_fn_once<F: FnOnce()>(f: F) {
    f();
}
```

## 迭代器基础

```rust
let v = vec![1, 2, 3, 4, 5];

let sum: i32 = v.iter().sum();
let v2: Vec<i32> = v.into_iter().map(|x| x * 2).collect();

let mut v = vec![1, 2, 3];
for x in v.iter_mut() {
    *x *= 2;
}
```

## Iterator trait

```rust
trait Iterator {
    type Item;

    fn next(&mut self) -> Option<Self::Item>;

    fn map<B, F>(self, f: F) -> Map<Self, F>
    where F: FnMut(Self::Item) -> B;

    fn filter<P>(self, predicate: P) -> Filter<Self, P>
    where P: FnMut(&Self::Item) -> bool;

    fn collect<B>(self) -> B
    where B: FromIterator<Self::Item>;

    fn fold<B, F>(self, init: B, f: F) -> B
    where F: FnMut(B, Self::Item) -> B;
}
```

## 常用适配器

```rust
let v = vec![1, 2, 3, 4, 5];

let doubled: Vec<i32> = v.iter().map(|x| x * 2).collect();
let evens: Vec<&i32> = v.iter().filter(|x| *x % 2 == 0).collect();
let first3: Vec<&i32> = v.iter().take(3).collect();

let a = vec![1, 2, 3];
let b = vec!["a", "b", "c"];
let pairs: Vec<(i32, &str)> = a.iter().zip(b.iter()).map(|(x, y)| (*x, *y)).collect();
```

## 消费器

```rust
let v = vec![1, 2, 3, 4, 5];

let total: i32 = v.iter().sum();
let sum = v.iter().fold(0, |acc, x| acc + x);

let has_negative = v.iter().any(|x| *x < 0);
let all_positive = v.iter().all(|x| *x > 0);

let first_even = v.iter().find(|x| *x % 2 == 0);

let count = v.iter().filter(|x| *x > 2).count();
```

## 自定义迭代器

```rust
struct Counter {
    count: u32,
}

impl Counter {
    fn new() -> Self { Self { count: 0 } }
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

let counter = Counter::new();
let sum: u32 = counter.sum();
```

## 实战案例：惰性斐波那契

```rust
struct Fib {
    curr: u64,
    next: u64,
}

impl Fib {
    fn new() -> Self { Self { curr: 0, next: 1 } }
}

impl Iterator for Fib {
    type Item = u64;

    fn next(&mut self) -> Option<Self::Item> {
        let curr = self.curr;
        self.curr = self.next;
        self.next = curr + self.next;
        Some(curr)
    }
}

let fib = Fib::new();
let first10: Vec<u64> = fib.take(10).collect();
```

## 关联章节

- **02-types-traits/trait**：Trait
- **06-advanced/macro**：宏
- **06-advanced/smart-pointer**：智能指针

## 一句话总结

> **闭包 + 迭代器 = Rust 函数式核心**。**零成本抽象，性能等同手写循环**。
""")

add("06-advanced/smart-pointer.md", r"""---
title: 智能指针
---

# 智能指针

智能指针是实现了 Deref + Drop 的数据结构，管理堆内存的所有权与生命周期。

## 一句话总结

> **智能指针 = 实现 Deref + Drop 的指针**。**核心：Box / Rc / Arc / RefCell / Mutex**。

---

## Box<T>：堆分配

```rust
let b = Box::new(5);
println!("{}", b);  // 自动 deref

// 递归类型
enum List {
    Cons(i32, Box<List>),
    Nil,
}

let list = Cons(1, Box::new(Cons(2, Box::new(Cons(3, Box::new(Nil))))));

// Trait Object
let shapes: Vec<Box<dyn Draw>> = vec![
    Box::new(Circle { r: 1.0 }),
    Box::new(Square { s: 2.0 }),
];
```

## Rc<T>：单线程引用计数

```rust
use std::rc::Rc;

let a = Rc::new(5);
let b = Rc::clone(&a);
let c = Rc::clone(&a);

println!("Count: {}", Rc::strong_count(&a));  // 3
```

## Arc<T>：多线程引用计数

```rust
use std::sync::Arc;
use std::thread;

let data = Arc::new(vec![1, 2, 3]);
let mut handles = vec![];

for _ in 0..3 {
    let data = Arc::clone(&data);
    let handle = thread::spawn(move || {
        println!("{:?}", data);
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}
```

## RefCell<T>：单线程内部可变性

```rust
use std::cell::RefCell;

let data = RefCell::new(5);

{
    let mut borrowed = data.borrow_mut();
    *borrowed += 1;
}

println!("{}", data.borrow());
```

## Mutex<T>：多线程内部可变性

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let counter = Arc::new(Mutex::new(0));
let mut handles = vec![];

for _ in 0..10 {
    let counter = Arc::clone(&counter);
    let handle = thread::spawn(move || {
        let mut num = counter.lock().unwrap();
        *num += 1;
    });
    handles.push(handle);
}

for handle in handles {
    handle.join().unwrap();
}
```

## 4 大智能指针组合

```rust
use std::rc::Rc;
use std::cell::RefCell;

let shared = Rc::new(RefCell::new(vec![1, 2, 3]));
let a = Rc::clone(&shared);
let b = Rc::clone(&shared);

a.borrow_mut().push(4);
b.borrow_mut().push(5);

// Arc<Mutex<T>>：多线程共享可变
use std::sync::{Arc, Mutex};

let shared = Arc::new(Mutex::new(0));
```

## Deref 与 DerefMut

```rust
use std::ops::{Deref, DerefMut};

struct MyBox<T>(T);

impl<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T {
        &self.0
    }
}

impl<T> DerefMut for MyBox<T> {
    fn deref_mut(&mut self) -> &mut T {
        &mut self.0
    }
}

let x = MyBox(5);
println!("{}", *x);
```

## Weak<T>：弱引用

```rust
use std::rc::{Rc, Weak};

struct Node {
    value: i32,
    parent: Weak<Node>,
    children: Vec<Rc<Node>>,
}

let parent = Rc::new(Node { value: 1, parent: Weak::new(), children: vec![] });
let child = Rc::new(Node { value: 2, parent: Rc::downgrade(&parent), children: vec![] });
parent.children.push(Rc::clone(&child));

if let Some(p) = child.parent.upgrade() {
    println!("Parent value: {}", p.value);
}
```

## Drop Trait

```rust
struct CustomSmartPointer {
    data: String,
}

impl Drop for CustomSmartPointer {
    fn drop(&mut self) {
        println!("Dropping with data: {}", self.data);
    }
}
```

## 实战案例：LRU 缓存

```rust
use std::collections::HashMap;
use std::cell::RefCell;
use std::rc::Rc;

struct Node<K, V> {
    key: K,
    value: V,
    prev: Option<Rc<RefCell<Node<K, V>>>>,
    next: Option<Rc<RefCell<Node<K, V>>>>,
}

pub struct LruCache<K, V> {
    capacity: usize,
    map: HashMap<K, Rc<RefCell<Node<K, V>>>>,
}

impl<K: Clone + Eq + std::hash::Hash, V> LruCache<K, V> {
    pub fn new(capacity: usize) -> Self {
        Self { capacity, map: HashMap::new() }
    }

    pub fn get(&mut self, key: &K) -> Option<V> {
        self.map.get(key).map(|node| node.borrow().value.clone())
    }

    pub fn put(&mut self, key: K, value: V) {
        let node = Rc::new(RefCell::new(Node {
            key: key.clone(),
            value,
            prev: None,
            next: None,
        }));
        self.map.insert(key, node);
    }
}
```

## 关联章节

- **02-types-traits/advanced-types**：高级类型
- **04-concurrency/channels**：Channel 与共享状态
- **05-systems/unsafe**：unsafe

## 一句话总结

> **智能指针 = Rust 内存管理的核心抽象**：Box（堆分配）/ Rc/Arc（共享）/ RefCell/Mutex（内部可变）**。
""")

add("06-advanced/error-handling.md", r"""---
title: 错误处理
---

# 错误处理

Rust 错误处理基于 Result / Option + ? 操作符，无异常，无 panic（除非不可恢复）。

## 一句话总结

> **错误处理 = Result<T, E> + ? + 类型驱动**。**核心：anyhow（应用）/ thiserror（库）+ 自定义 Error**。

---

## 4 大错误处理哲学

```
1. 不可恢复错误用 panic!（程序员的 bug）
2. 可恢复错误用 Result<T, E>（业务错误）
3. 库用自定义 Error enum（精确错误类型）
4. 应用用 anyhow::Result（统一错误包装）
```

## Result + ?

```rust
use std::fs::File;
use std::io::Read;

fn read_file(path: &str) -> Result<String, std::io::Error> {
    let mut file = File::open(path)?;
    let mut content = String::new();
    file.read_to_string(&mut content)?;
    Ok(content)
}
```

## anyhow：应用层错误处理

```toml
[dependencies]
anyhow = "1"
```

```rust
use anyhow::{Context, Result, anyhow, bail};

fn read_config() -> Result<Config> {
    let content = std::fs::read_to_string("config.toml")
        .context("Failed to read config file")?;

    let config: Config = toml::from_str(&content)
        .context("Failed to parse config")?;

    if config.port == 0 {
        bail!("Invalid port: {}", config.port);
    }

    Ok(config)
}

fn main() -> Result<()> {
    let config = read_config()?;
    println!("Port: {}", config.port);
    Ok(())
}
```

## thiserror：库错误处理

```toml
[dependencies]
thiserror = "1"
```

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum DataError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Parse error: {0}")]
    Parse(String),

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Permission denied for {resource}")]
    PermissionDenied { resource: String },
}

fn load_data() -> Result<Data, DataError> {
    let content = std::fs::read_to_string("data.json")?;
    if content.is_empty() {
        return Err(DataError::NotFound("data.json".to_string()));
    }
    Ok(Data {})
}
```

## 自定义 Error

```rust
use std::fmt;
use std::error::Error;

#[derive(Debug)]
struct AppError {
    kind: ErrorKind,
    message: String,
    source: Option<Box<dyn Error + Send + Sync>>,
}

#[derive(Debug)]
enum ErrorKind {
    Io,
    Parse,
    NotFound,
}

impl fmt::Display for AppError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "{:?}: {}", self.kind, self.message)
    }
}

impl Error for AppError {
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        self.source.as_ref().map(|e| e.as_ref() as &(dyn Error + 'static))
    }
}
```

## panic! vs Result

```rust
// panic!：不可恢复错误（程序员的 bug）
panic!("invariant violated");

// Result：可恢复错误（业务错误）
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("division by zero".to_string())
    } else {
        Ok(a / b)
    }
}
```

## 错误传播最佳实践

```rust
// 1. 优先用 ? 操作符（避免 match 嵌套）
fn process() -> Result<()> {
    let data = read_file()?;
    let parsed = parse_data(&data)?;
    save(&parsed)?;
    Ok(())
}

// 2. 上下文信息用 .context()
let content = std::fs::read_to_string(path)
    .context(format!("Failed to read {}", path))?;

// 3. 错误转换用 map_err
let result = operation().map_err(|e| MyError::Operation(e))?;

// 4. 顶层 main 用 anyhow::Result
fn main() -> anyhow::Result<()> {
    // ...
    Ok(())
}
```

## 实战案例：CLI 工具错误处理

```rust
use anyhow::{Context, Result};
use std::fs;
use std::process;

struct Args {
    input: String,
    output: String,
}

fn parse_args() -> Result<Args> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        anyhow::bail!("Usage: {} <input> <output>", args[0]);
    }
    Ok(Args { input: args[1].clone(), output: args[2].clone() })
}

fn run() -> Result<()> {
    let args = parse_args()?;

    let content = fs::read_to_string(&args.input)
        .context(format!("Failed to read input file: {}", args.input))?;

    let processed = content.to_uppercase();

    fs::write(&args.output, processed)
        .context(format!("Failed to write output file: {}", args.output))?;

    Ok(())
}

fn main() {
    if let Err(e) = run() {
        eprintln!("Error: {:?}", e);
        process::exit(1);
    }
}
```

## 关联章节

- **02-types-traits/overview**：类型系统
- **01-basics/syntax-fundamentals**：Result / ? 基础
- **06-advanced/smart-pointer**：智能指针

## 一句话总结

> **错误处理 = Result + ? + 类型驱动**。**anyhow 用于应用、thiserror 用于库**。
""")

add("06-advanced/async-ecosystem.md", r"""---
title: 异步生态对比
---

# 异步生态对比

Rust 异步生态有多个运行时选择：tokio / async-std / smol / embassy，各有侧重。

## 一句话总结

> **tokio = 事实标准 / async-std = 类 std 风格 / smol = 轻量 / embassy = 嵌入式**。**90% 项目选 tokio**。

---

## 4 大运行时横向对比

| 维度 | tokio | async-std | smol | embassy |
|------|-------|-----------|------|---------|
| **生态** | 最完整 | 中等 | 轻量 | 嵌入式 |
| **性能** | 最优 | 中等 | 中等 | 针对 MCU |
| **API 风格** | 自己的 | 类 std | 极简 | 嵌入式 |
| **学习曲线** | 中 | 低 | 低 | 中高 |
| **目标场景** | 服务端 | 服务端 | 工具 / 嵌入式 | 微控制器 |
| **维护状态** | 活跃 | 活跃 | 活跃 | 活跃 |
| **公司背景** | tokio-rs | async-rs | 个人 / tokio-rs | embassy-rs |

## tokio（推荐）

```rust
use tokio::net::TcpListener;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    loop {
        let (mut socket, _) = listener.accept().await?;
        tokio::spawn(async move {
            let mut buf = [0; 1024];
            socket.read(&mut buf).await.unwrap();
            socket.write_all(b"HTTP/1.1 200 OK\r\n\r\nHello").await.unwrap();
        });
    }
}
```

## async-std

```rust
use async_std::net::TcpListener;
use async_std::io::{ReadExt, WriteExt};

#[async_std::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let listener = TcpListener::bind("127.0.0.1:8080").await?;
    let mut incoming = listener.incoming();
    while let Some(stream) = incoming.next().await {
        let mut stream = stream?;
        stream.write_all(b"Hello").await?;
    }
    Ok(())
}
```

## smol（轻量）

```rust
use smol::{net, Executor};

fn main() {
    smol::block_on(async {
        let listener = net::TcpListener::bind("127.0.0.1:8080").await.unwrap();
        loop {
            let (mut stream, _) = listener.accept().await.unwrap();
            smol::spawn(async move {
                use smol::io::{AsyncReadExt, AsyncWriteExt};
                let mut buf = [0; 1024];
                stream.read(&mut buf).await.unwrap();
                stream.write_all(b"Hello").await.unwrap();
            }).detach();
        }
    });
}
```

## embassy（嵌入式）

```rust
#![no_std]
#![no_main]

use embassy_executor::Spawner;
use embassy_time::{Duration, Timer};

#[embassy_executor::main]
async fn main(_spawner: Spawner) {
    loop {
        // 嵌入式主循环
        Timer::after(Duration::from_millis(1000)).await;
        // 闪烁 LED
    }
}
```

## 4 大决策维度

```
1. 生态
   tokio > async-std > smol
   （tokio 有 axum / tonic / sqlx 等完整生态）

2. 学习曲线
   async-std ≈ smol < tokio < embassy
   （async-std API 像 std，tokio 有自己的约定）

3. 性能
   tokio ≈ smol > async-std
   （tokio 多线程 + work-stealing 极致优化）

4. 部署目标
   服务端：tokio / async-std
   嵌入式：embassy
   WASM：smol / 直接用 tokio（在 WASM 中）
   库：抽象掉运行时（用 async-trait）
```

## async 库编写建议

```rust
// 1. 库不绑定特定运行时
use async_trait::async_trait;

#[async_trait]
trait Database {
    async fn get_user(&self, id: u32) -> Option<User>;
}

// 2. 让用户传入 runtime handle
struct MyService {
    runtime: tokio::runtime::Handle,
}

// 3. 用 Send + 'static 约束
async fn process(data: impl Send + 'static) -> Result<(), Error> {
    // ...
}

// 4. 提供 feature flags
[features]
default = ["tokio"]
async-std = ["async-std-runtime"]
smol = ["smol-runtime"]
```

## 4 大生态组件（基于 tokio）

```rust
// 1. Web 框架：axum / actix-web
use axum::{routing::get, Router};

// 2. gRPC：tonic
use tonic::{transport::Server, Request, Response};

// 3. 数据库：sqlx
use sqlx::postgres::PgPool;

// 4. 序列化：serde
use serde::{Serialize, Deserialize};

// 5. 日志：tracing
use tracing::{info, instrument};

// 6. 错误处理：anyhow / thiserror
use anyhow::Result;
```

## 实战案例：tokio 完整 HTTP 服务

```rust
use axum::{
    routing::{get, post},
    Router, Json,
};
use serde::{Deserialize, Serialize};
use tokio::net::TcpListener;

#[derive(Serialize, Deserialize)]
struct User {
    id: u32,
    name: String,
}

#[tokio::main]
async fn main() {
    let app = Router::new()
        .route("/", get(|| async { "Hello, world!" }))
        .route("/users", get(list_users))
        .route("/users/:id", get(get_user));

    let listener = TcpListener::bind("0.0.0.0:3000").await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn list_users() -> Json<Vec<User>> {
    Json(vec![User { id: 1, name: "Alice".to_string() }])
}

async fn get_user(Path(id): Path<u32>) -> Json<User> {
    Json(User { id, name: format!("User {}", id) })
}
```

## 关联章节

- **04-concurrency/async-await**：async-await 基础
- **04-concurrency/tokio**：Tokio 深度
- **05-systems/wasm**：WASM 运行时

## 一句话总结

> **异步生态 = tokio 主导，其他补充**。**90% 服务端项目选 tokio，嵌入式选 embassy，库用 async-trait 抽象**。
""")


def main():
    """Write each CONTENT entry to its corresponding md file."""
    print(f"Total pages to generate: {len(CONTENT)}")
    written = 0
    for rel_path, content in CONTENT.items():
        full_path = os.path.join(DOCS_ROOT, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        written += 1
        print(f"  [{written}/{len(CONTENT)}] {rel_path}")
    print(f"\nGenerated: {written}/{len(CONTENT)} pages")


if __name__ == "__main__":
    main()