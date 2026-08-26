---
title: 枚举与模式匹配
---

# 枚举与模式匹配

Rust 的 enum 是"和类型"（sum type），能表达"或"语义；模式匹配强制穷尽每个变体。

## 一句话总结

> **enum + match = Rust 消灭 null 与异常的核心**。**核心：Option\<T\> / Result`<T,E>` / 自定义 enum 表达业务状态**。

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
