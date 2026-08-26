---
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
