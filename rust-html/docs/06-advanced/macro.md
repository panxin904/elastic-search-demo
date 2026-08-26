---
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


<!-- auto-enrich:do-not-edit -->

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
