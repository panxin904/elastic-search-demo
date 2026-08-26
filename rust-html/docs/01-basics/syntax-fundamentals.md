---
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
