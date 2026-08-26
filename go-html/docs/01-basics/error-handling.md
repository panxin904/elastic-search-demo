---
title: 错误处理
---

# 错误处理

Go 错误处理哲学：**错误是值，不是异常**。通过显式 error 返回，强制调用者处理错误。

## 一句话总结

> **Go 错误处理 = error 接口 + 显式返回 + errors.Is/As**。**核心：error 是值 / panic 是真异常 / recover 兜底**。

---

## 一、error 接口

### 标准接口

```go
// src/builtin/builtin.go
type error interface {
    Error() string
}
```

### 简单错误

```go
import "errors"
err := errors.New("something went wrong")
err := fmt.Errorf("invalid value: %d", x)

// fmt.Errorf + %w：包装错误
err := fmt.Errorf("query failed: %w", dbErr)
```

### 自定义错误类型

```go
// 1. struct error
type ValidationError struct {
    Field   string
    Message string
}
func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation failed on %s: %s", e.Field, e.Message)
}

// 2. 哨兵错误
var ErrNotFound = errors.New("not found")
var ErrPermissionDenied = errors.New("permission denied")

// 使用
if errors.Is(err, ErrNotFound) {
    return nil
}
```

---

## 二、错误处理模式

### 标准模式：多返回值

```go
func readFile(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err  // 直接返回
    }
    return data, nil
}
```

### 错误判断

```go
// errors.Is：判断特定错误
if errors.Is(err, sql.ErrNoRows) {
    // not found
}

// errors.As：提取特定类型
var pathErr *fs.PathError
if errors.As(err, &pathErr) {
    fmt.Println(pathErr.Path)
}
```

### 错误包装（%w）

```go
func loadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("read config: %w", err)
    }
    var cfg Config
    if err := json.Unmarshal(data, &cfg); err != nil {
        return nil, fmt.Errorf("parse config: %w", err)
    }
    return &cfg, nil
}

// 调用方可以 unwrap
err := loadConfig("config.json")
fmt.Println(err)  // parse config: invalid character 'x' looking for ...
errors.Unwrap(err)  // 拿到 json.Unmarshal 的错误
```

### 错误链（Unwrap）

```go
// 自定义错误支持 Unwrap
type MyError struct {
    Msg string
    Err error
}
func (e *MyError) Error() string {
    return e.Msg + ": " + e.Err.Error()
}
func (e *MyError) Unwrap() error {
    return e.Err
}

// errors.Is/As 自动递归 Unwrap
```

---

## 三、panic 与 recover

### panic：运行时异常

```go
// 显式 panic
panic("something terrible")

// 隐式 panic
var s []int
s[10]  // panic: runtime error: index out of range

var m map[string]int
m["a"] = 1  // panic: assignment to entry in nil map
```

### recover：捕获 panic

```go
func riskyOp() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("recovered:", r)
            // 可以打日志 / 清理 / 重新 panic
        }
    }()

    panic("oops!")
}

riskyOp()  // 输出：recovered: oops!
```

### panic + recover 实战

```go
// HTTP handler panic 安全
func safeHandler(h http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if r := recover(); r != nil {
                log.Printf("panic recovered: %v", r)
                http.Error(w, "Internal Server Error", http.StatusInternalServerError)
            }
        }()
        h(w, r)
    }
}

// 防止 panic 拖垮整个服务
```

---

## 四、错误处理最佳实践

### 1. 不要忽略错误

```go
// ❌ 错
data, _ := os.ReadFile("config.json")

// ✅ 对
data, err := os.ReadFile("config.json")
if err != nil {
    return fmt.Errorf("read config: %w", err)
}
```

### 2. 包装错误而非丢弃

```go
// ❌ 错：丢失上下文
data, err := os.ReadFile(path)
if err != nil {
    return err
}

// ✅ 对：添加上下文
data, err := os.ReadFile(path)
if err != nil {
    return fmt.Errorf("read %s: %w", path, err)
}
```

### 3. 不要 panic 当 error 用

```go
// ❌ 错：业务错误用 panic
func getUser(id int) *User {
    user, err := db.GetUser(id)
    if err != nil {
        panic(err)  // 不要！
    }
    return user
}

// ✅ 对：业务错误用 error
func getUser(id int) (*User, error) {
    user, err := db.GetUser(id)
    if err != nil {
        return nil, err
    }
    return user, nil
}

// ✅ panic 仅用于：
// - 程序无法继续运行（配置缺失、初始化失败）
// - 程序员错误（数组越界、空指针）
// - 通过 recover 捕获并优雅处理
```

### 4. 错误日志 vs 错误返回

```go
// 中间层：记录日志 + 返回错误
func (s *Service) DoSomething() error {
    err := s.doIt()
    if err != nil {
        log.Printf("DoSomething failed: %v", err)  // 记录
        return err                                  // 返回
    }
    return nil
}

// 顶层（main）：打印后退出
func main() {
    if err := run(); err != nil {
        log.Fatal(err)
    }
}
```

---

## 五、错误处理工具

### pkg/errors（社区库）

```go
import "github.com/pkg/errors"

err := errors.Wrap(err, "additional context")
err := errors.Wrapf(err, "format %s", value)

// 打印堆栈
fmt.Printf("%+v\n", err)

// 提取原因
errors.Cause(err)
```

### 第三方增强库

```go
// hashicorp/go-multierror：合并多个错误
import "github.com/hashicorp/go-multierror"

var result error
for _, item := range items {
    if err := process(item); err != nil {
        result = multierror.Append(result, err)
    }
}
if result != nil {
    return result
}
```

---

## 六、错误 vs 异常的取舍

### Go 哲学：error 是值

```go
// Rust：Result<T, E>
fn read_file(path: &str) -> Result<String, io::Error> { ... }

// Go：error
func readFile(path string) (string, error) { ... }
```

### 优点

1. **显式**：错误处理在函数签名中可见
2. **类型安全**：错误是值，可包装、传递、判断
3. **无 try-catch 滥用**：避免 catch 一切

### 缺点

1. **样板代码**：if err != nil 重复
2. **容易被忽略**：可以用 _ 忽略
3. **缺乏语法糖**：Rust 的 ? 操作符更简洁

### Go 1.18+ 改进

```go
// 没有 ? 操作符，但有 named return + defer
func readFile(path string) (data []byte, err error) {
    defer func() {
        if err != nil {
            err = fmt.Errorf("read %s: %w", path, err)
        }
    }()
    return os.ReadFile(path)
}
```

---

## 关联章节

- **01-basics/overview**：Go 总览
- **01-basics/types-and-functions**：类型与函数
- **01-basics/package-and-module**：包与模块

## 一句话总结

> **Go 错误处理 = error 接口 + 显式返回 + errors.Is/As**。**panic 仅用于不可恢复错误**。


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
