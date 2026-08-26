---
title: 错误处理
---

# 错误处理

Rust 错误处理基于 Result / Option + ? 操作符，无异常，无 panic（除非不可恢复）。

## 一句话总结

> **错误处理 = Result`<T, E>` + ? + 类型驱动**。**核心：anyhow（应用）/ thiserror（库）+ 自定义 Error**。

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
