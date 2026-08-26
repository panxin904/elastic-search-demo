---
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
