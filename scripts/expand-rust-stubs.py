#!/usr/bin/env python3
"""
扩展 7 篇 <3KB 的 rust stub 到 ≥3KB。
每个文件追加：实战案例 / 踩坑教训 / 选型决策 等扩展小节。
"""
from pathlib import Path

ROOT = Path("rust-html/docs")

EXPANSIONS = {

    "01-basics/hello-world.md": """

## 完整工程结构（生产级 Hello World）

```bash
hello_rust/
├── .gitignore
├── Cargo.toml
├── Cargo.lock           # 锁定依赖版本（commit 到 git）
├── src/
│   ├── main.rs          # 二进制入口
│   ├── lib.rs           # 库入口（推荐拆分）
│   └── bin/
│       └── alt.rs       # 多个二进制
├── tests/               # 集成测试
│   └── integration.rs
├── examples/            # 可执行示例
│   └── basic.rs
├── benches/             # 基准测试（nightly）
│   └── bench.rs
└── target/              # 编译产物（git ignore）
```

## 实战案例：发布到 crates.io

```bash
# 1. 完善 Cargo.toml 元信息
# description / license / repository / keywords / categories

# 2. cargo login <api-token>

# 3. cargo publish --dry-run    # 预检
cargo publish                   # 真正发布

# 4. 撤回（24h 内只能一次）
cargo yank --vers 0.1.0

# 5. 文档自动部署到 docs.rs
#    cargo publish 后自动触发
#    访问 https://docs.rs/hello_rust
```

## 踩坑：rustup 版本管理

```bash
# 安装多个 toolchain
rustup toolchain install stable
rustup toolchain install nightly
rustup toolchain install 1.75.0      # 特定版本

# 项目级锁定
rustup override set nightly

# 全局默认
rustup default stable

# 跨平台编译
rustup target add aarch64-apple-darwin
rustup target add x86_64-unknown-linux-gnu

# 组件
rustup component add clippy rustfmt rust-src
```

## IDE 选择矩阵

| IDE / Editor | 插件 | 适合 |
|---|---|---|
| **VS Code** | rust-analyzer | 通用首选 |
| **IntelliJ IDEA** | IntelliJ Rust | 重度 Java 转 Rust |
| **Neovim** | nvim-lspconfig + rust-analyzer | vim 用户 |
| **Helix** | 内置 LSP | 现代编辑器 |
| **Zed** | 内置 | 极致性能 |
| **CLion** | IntelliJ Rust | C/C++ 转 Rust |
""",

    "01-basics/lifetimes.md": """

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
""",

    "02-types-traits/advanced-types.md": """

## 类型转换：`From` / `Into` / `TryFrom` / `TryInto`

```rust
// From：标准转换（消费输入）
struct Meters(f64);
impl From<f64> for Meters {
    fn from(v: f64) -> Self { Meters(v) }
}

// Into：From 的反向（自动实现）
let m: Meters = 3.14.into();

// TryFrom：可能失败的转换
struct EvenNumber(i32);
impl TryFrom<i32> for EvenNumber {
    type Error = &'static str;
    fn try_from(v: i32) -> Result<Self, Self::Error> {
        if v % 2 == 0 { Ok(EvenNumber(v)) }
        else { Err("not even") }
    }
}
```

## `Sized` 与 `?Sized`

```rust
// T: Sized 默认所有泛型参数都有 Sized 约束
fn print<T: std::fmt::Debug>(t: T) { println!("{:?}", t); }

// ?Sized 放宽约束（接收 DST）
fn print_dyn<T: std::fmt::Debug + ?Sized>(t: &T) { println!("{:?}", t); }

print_dyn(&"hello");  // &str 是 DST
print_dyn(&[1, 2, 3]);  // &[T] 是 DST
```

## 内部可变性：`Cell` / `RefCell` / `Mutex`

```rust
use std::cell::Cell;

// Cell<T>：Copy 类型（无需 mut）
struct Counter { count: Cell<u32> }
impl Counter {
    fn increment(&self) { self.count.set(self.count.get() + 1); }
}

// RefCell<T>：运行时借用检查（用于单线程）
use std::cell::RefCell;
let data = RefCell::new(vec![1, 2, 3]);
data.borrow_mut().push(4);  // 运行时检查，可能 panic
```

## 实战案例：Builder 模式 + PhantomData

```rust
use std::marker::PhantomData;

// 类型状态（type state）模式
struct Uninitialized;
struct Initialized;

struct Connection<State> {
    handle: i32,
    _state: PhantomData<State>,
}

impl Connection<Uninitialized> {
    fn new() -> Self {
        Self { handle: 0, _state: PhantomData }
    }
    fn connect(self) -> Connection<Initialized> {
        Connection { handle: 1, _state: PhantomData }
    }
}

impl Connection<Initialized> {
    fn query(&self, sql: &str) -> String {
        format!("Result for {}", sql)
    }
}

let conn = Connection::new().connect();
conn.query("SELECT 1");  // 未初始化的连接无法 query
```

## 选型决策：何时用 Newtype vs 类型别名

| 场景 | 推荐 | 原因 |
|---|---|---|
| 防止单位混淆（米/千米） | **Newtype** | 编译期阻止错误 |
| 用户 ID vs 产品 ID | **Newtype** | 类型严格 |
| 简化复杂签名 `Box<dyn Fn() + Send + 'static>` | **类型别名** | 不增加类型严格度 |
| 字符串别名 | **类型别名** | String 还是 String |
""",

    "03-ecosystem/cargo.md": """

## Cargo.lock 策略

```bash
# 二进制项目（应用）：commit lock
git add Cargo.lock
# 保证所有开发者 + CI 用同一版本

# 库项目（crate）：不 commit lock
# cargo publish 时强制 .gitignore

# 强制重新解析
rm Cargo.lock
cargo update
```

## 私有 crate 源（私有 registry）

```toml
# ~/.cargo/config.toml
[source.crates-io]
replace-with = "tuna"

[source.tuna]
registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index"

# 或企业私有源
[source.my-company]
registry = "https://cargo.mycompany.com/git/index"
```

## 离线构建

```bash
# 预下载所有依赖到 vendor/
cargo vendor

# 项目内 vendor 目录
mkdir .cargo
cat > .cargo/config.toml <<EOF
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

# 离线构建
cargo build --offline
```

## 条件编译（target / feature）

```rust
// src/lib.rs
#[cfg(target_os = "linux")]
pub fn linux_only() { /* ... */ }

#[cfg(target_os = "windows")]
pub fn windows_only() { /* ... */ }

#[cfg(feature = "serde")]
pub use serde::{Serialize, Deserialize};
```

## Cargo 常用环境变量

```bash
CARGO_TARGET_DIR=/tmp/target cargo build     # 自定义产物目录
CARGO_BUILD_JOBS=4 cargo build               # 并行度
RUSTC_WRAPPER=sccache cargo build            # 编译缓存
RUSTFLAGS="-C target-cpu=native" cargo build # CPU 优化
RUST_BACKTRACE=full cargo run                # panic backtrace
```

## 实战案例：跨平台编译

```bash
# 安装目标
rustup target add aarch64-apple-darwin
rustup target add x86_64-unknown-linux-gnu
rustup target add wasm32-unknown-unknown

# 静态二进制（Linux）
RUSTFLAGS="-C target-feature=+crt-static" \
  cargo build --release --target x86_64-unknown-linux-gnu

# 最小镜像（约 5MB）
docker run --rm -v $(pwd):/app -w /app rust:slim \
  cargo build --release
```
""",

    "03-ecosystem/crates-io.md": """

## crate 选型黄金法则

1. **下载量**：> 100 万 = 主流；> 10 万 = 可用；< 1 万 = 慎用
2. **活跃度**：最近 3 个月有 commit = 维护中；1 年没动 = 死亡
3. **issue/PR 响应**：核心维护者响应 < 7 天 = 健康
4. **文档完整度**：docs.rs 自动生成，看 example + 覆盖率
5. **MSRV（Minimum Supported Rust Version）**：决定可移植性

## 实战：选型 HTTP 客户端

| crate | 同步 | 异步 | TLS | 特点 |
|---|---|---|---|---|
| **reqwest** | ✅ | ✅ | rustls/native | 上手最快 |
| **hyper** | ❌ | ✅ | 需自配 | Tokio 底层 |
| **ureq** | ✅ | ❌ | rustls/native | 轻量 |
| **awc** (actix) | ✅ | ✅ | native | actix 生态 |
| **surf** | ✅ | ✅ | 多种 | 中间件系统 |

**决策树**：
- Tokio 生态 + 易用 → **reqwest**
- 极致控制 + 性能 → **hyper**
- 轻量 CLI 工具 → **ureq**
- actix-web 服务 → **awc**

## 实战：选型序列化框架

```toml
# serde：基础 trait
serde = { version = "1", features = ["derive"] }

# JSON
serde_json = "1"

# YAML
serde_yaml = "0.9"  # 注意：已弃用，推荐 serde_yml

# TOML
toml = "0.8"

# MessagePack（高性能二进制）
rmp-serde = "1"

# BSON（MongoDB）
serde = { version = "1", features = ["derive"] }
bson = "2"
```

## 实战：依赖审计（cargo-deny / cargo-audit）

```bash
# 安装
cargo install cargo-deny --locked
cargo install cargo-audit --locked

# 检查安全漏洞
cargo audit

# 检查许可证合规
cargo deny check license

# 重复依赖检测
cargo tree -d

# 检查过时依赖
cargo install cargo-outdated
cargo outdated
```

## 创建自己的 crate

```bash
# 1. cargo new --lib my_crate

# 2. 完善 Cargo.toml
[package]
name = "my_crate"
description = "A short description (< 200 chars)"
license = "MIT OR Apache-2.0"
repository = "https://github.com/me/my_crate"
keywords = ["async", "tokio"]
categories = ["network-programming"]
edition = "2021"
rust-version = "1.70"  # MSRV

# 3. README.md（crates.io 显示）

# 4. cargo publish --dry-run  # 检查
cargo publish                 # 发布
```

## 私有 registry（企业内部）

```toml
# 企业私有 registry（使用 GitLab / Gitea）
[registries.company]
index = "https://gitlab.mycompany.com/api/v4/packages/rust/cargo-index"

[net]
git-fetch-with-cli = true
```
""",

    "04-concurrency/threads.md": """

## `Send` / `Sync` 标记 trait

```rust
// Send：可在线程间转移所有权
// Sync：可在线程间共享引用（&T 是 Send）

// 标准库自动实现
// - i32, String, Vec<T>: Send + Sync（如果 T: Send）
// - Rc<T>: !Send !Sync（引用计数非原子）
// - Mutex<T>: Send + Sync（如果 T: Send）
// - RefCell<T>: Send 但 !Sync（运行时借用检查）

// 自定义类型
struct MyType { /* ... */ }
// 编译器自动派生 Send/Sync（字段全 Send/Sync 时）

// 手动 opt-out
struct NotSend {
    _marker: PhantomData<*const ()>,  // raw pointer !Send !Sync
}
```

## 线程池（rayon）

```rust
use rayon::prelude::*;

// 数据并行（CPU-bound）
let sum: i64 = (0..1_000_000).into_par_iter().sum();

// 并行 map
let squares: Vec<i64> = vec![1, 2, 3, 4].into_par_iter().map(|x| x * x).collect();

// 并行排序
let mut data = vec![5, 3, 1, 4, 2];
data.par_sort();

// 线程池配置
rayon::ThreadPoolBuilder::new()
    .num_threads(8)
    .build_global()
    .unwrap();
```

## scoped threads（借用闭包）

```rust
use std::thread;

let mut data = vec![1, 2, 3, 4];

// 普通 spawn 必须 move（无法借用）
// thread::spawn(|| data.push(5));  // 错误

// scoped：线程保证在作用域内 join，可借用
thread::scope(|s| {
    s.spawn(|| {
        println!("len = {}", data.len());  // 借用合法
    });
    s.spawn(|| {
        data[0] += 1;  // 借用合法
    });
});  // 自动 join 所有线程
```

## 实战案例：并行下载

```rust
use std::sync::{Arc, Mutex};
use std::thread;

let urls = vec![
    "https://example.com/a",
    "https://example.com/b",
    "https://example.com/c",
];
let results = Arc::new(Mutex::new(Vec::new()));

let handles: Vec<_> = urls.into_iter().enumerate().map(|(i, url)| {
    let results = Arc::clone(&results);
    thread::spawn(move || {
        // reqwest::blocking::get(url)...
        let content = format!("content of {}", url);
        results.lock().unwrap().push((i, content));
    })
}).collect();

for h in handles { h.join().unwrap(); }

println!("{:?}", results.lock().unwrap());
```

## 选型：原生 thread vs rayon vs tokio

| 场景 | 推荐 | 原因 |
|---|---|---|
| CPU-bound 数据并行 | **rayon** | 自动 work-stealing |
| 偶尔后台任务 | **std::thread** | 简单直接 |
| I/O-bound 高并发 | **tokio** | 异步 + 轻量 |
| 阻塞 syscall | **std::thread** + thread pool | 避免阻塞 runtime |
| 长期守护进程 | **tokio::task::spawn** | 优雅关闭 |
""",

    "06-advanced/macro.md": """

## 函数式宏（function-like proc_macro）

```rust
use proc_macro::TokenStream;

#[proc_macro]
pub fn sql(input: TokenStream) -> TokenStream {
    let sql = input.to_string();
    // 解析 SQL，构建 query
    quote! { /* 生成的代码 */ }.into()
}

// 使用
let users = sql!(SELECT * FROM users WHERE age > 18);
```

## 属性宏（attribute proc_macro）

```rust
#[proc_macro_attribute]
pub fn trace_fn(_attr: TokenStream, item: TokenStream) -> TokenStream {
    let fn_ast = parse_macro_input!(item as ItemFn);
    let name = &fn_ast.sig.ident;
    let body = &fn_ast.block;
    let vis = &fn_ast.vis;
    let sig = &fn_ast.sig;

    quote! {
        #vis #sig {
            let __start = std::time::Instant::now();
            let __result = (|| #body)();
            println!("{} took {:?}", stringify!(#name), __start.elapsed());
            __result
        }
    }.into()
}

// 使用
#[trace_fn]
fn expensive() -> u64 {
    (0..1_000_000).sum()
}
```

## 宏卫生（hygiene）

```rust
// 宏内部变量名不会污染调用方作用域
macro_rules! make_var {
    () => {
        let x = 42;  // 这个 x 与外部 x 隔离
    };
}

let x = 10;
make_var!();
println!("{}", x);  // 10（外部 x 不受影响）
```

## 实战案例：`derive_more` crate

```toml
# Cargo.toml
[dependencies]
derive_more = { version = "1", features = ["full"] }
```

```rust
use derive_more::{Add, Sub, Display, From, Into, Debug};

#[derive(Debug, Clone, Copy, Add, Sub, PartialEq, Eq)]
struct Point { x: i32, y: i32 }

#[derive(Display, From, Into)]
struct UserId(u64);

#[derive(Debug)]
#[debug("Custom format: {} {}", field1, field2)]
struct MyStruct { field1: i32, field2: String }
```

## 宏设计原则

1. **优先用函数/泛型**：只有真正需要编译期生成时才用宏
2. **输入验证**：在宏内做语法/语义检查，给清晰错误
3. **卫生性**：避免变量名冲突
4. **文档完整**：每个宏参数都要解释
5. **提供 example**：让用户复制即可用

## 选型：何时用什么宏方案

| 场景 | 推荐 |
|---|---|
| 简单重复代码（5-20 行） | **macro_rules!** |
| 自动 derive trait（Serialize/Display） | **proc_macro_derive** |
| 自定义属性（如 `#[trace]`、`#[test]`） | **proc_macro_attribute** |
| DSL（sql!, html!, json!） | **macro_rules!** 或 **function-like proc_macro** |
| 需要访问类型信息（如字段名） | **proc_macro_derive** + `syn`/`quote` |
""",

}


def expand():
    root = Path("rust-html/docs")
    for rel_path, addition in EXPANSIONS.items():
        f = root / rel_path
        if not f.exists():
            print(f"  MISSING: {rel_path}")
            continue
        original = f.read_text(encoding="utf-8")
        # 移除文件末尾重复的"一句话总结"
        content = original.rstrip()
        # 找到最后一个"## 一句话总结"前的所有内容
        idx = content.rfind("\n## 一句话总结\n")
        if idx > 0:
            # 检查这个总结是否和前面的总结重复
            first_summary = content.find("## 一句话总结\n")
            if first_summary != idx:
                # 删掉末尾的总结
                content = content[:idx]
        new_content = content.rstrip() + "\n" + addition
        f.write_text(new_content, encoding="utf-8")
        size = f.stat().st_size
        status = "OK" if size >= 3000 else "TOO SHORT"
        print(f"  {status:>9} {rel_path} -> {size} bytes")


if __name__ == "__main__":
    expand()
