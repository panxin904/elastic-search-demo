#!/usr/bin/env python3
"""生成 go-html 站点的 stub substantial 页面。"""
from pathlib import Path

ROOT = Path("go-html/docs")

def add(rel_path: str, content: str) -> None:
    """写入一篇 stub。"""
    f = ROOT / rel_path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content.lstrip("\n"), encoding="utf-8")
    print(f"  [done] {rel_path}")


# === 01-basics ===

add("01-basics/syntax-fundamentals.md", r"""---
title: 语法速览
---

# 语法速览

Go 语法极简：25 个关键字，5 分钟上手，1 小时精通。

## 一句话总结

> **Go 语法 = C 风格 + 类型后置 + 错误显式返回**。**核心：变量 := / 切片 slice / map / struct / interface**。

---

## 一、变量与常量

```go
// 变量声明
var name string = "Alice"
var age int = 30              // 完整声明
var address string            // 默认零值

// 短变量声明（仅函数内）
name := "Alice"
age := 30

// 多变量
var (
    name    string = "Alice"
    age     int    = 30
    address string
)

// 常量
const Pi = 3.14
const (
    StatusOK = 200
    StatusNotFound = 404
)

// iota：枚举常量
const (
    Sunday = iota   // 0
    Monday          // 1
    Tuesday         // 2
)
```

### 零值

每个类型都有零值，**变量声明后立即可用**：

```go
var i int      // 0
var s string   // ""
var b bool     // false
var p *int     // nil
var sl []int   // nil
var m map[string]int  // nil（需要 make 才能用）
```

---

## 二、基本类型

```go
// 布尔
var b bool = true

// 整数
var i int = 42              // 默认 int（32 或 64 位，依赖平台）
var i8 int8 = 127           // -128 ~ 127
var i16 int16 = 32767
var i32 int32 = 2147483647
var i64 int64 = 9223372036854775807
var u uint = 42             // 无符号
var u8 uint8 = 255
var by byte = 255           // = uint8

// 浮点
var f32 float32 = 3.14
var f64 float64 = 3.14159265358979

// 复数
var c64 complex64
var c128 complex128

// 字符串（不可变）
var s string = "hello"

// rune（Unicode code point）
var r rune = '中'

// byte（uint8 别名）
var by byte = 'A'
```

### 类型转换

```go
// 必须显式转换（没有隐式）
i := 42
f := float64(i)
s := string(i)  // 错误！应该用 strconv.Itoa(i)
```

---

## 三、控制流

### if

```go
if x > 0 {
    fmt.Println("positive")
} else if x < 0 {
    fmt.Println("negative")
} else {
    fmt.Println("zero")
}

// if with statement
if v := compute(); v > 0 {
    fmt.Println(v)
}
```

### for（唯一循环）

```go
// 标准 for
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// while 风格
for condition {  // 无限循环
    if condition {
        break
    }
}

// range（遍历 slice / map / string / channel）
for i, v := range []int{1, 2, 3} {
    fmt.Println(i, v)
}
for k, v := range map[string]int{"a": 1} {
    fmt.Println(k, v)
}
for i, c := range "hello" {  // 返回 rune
    fmt.Println(i, c)
}
```

### switch

```go
switch x {
case 1:
    fmt.Println("one")
case 2, 3:  // 多值
    fmt.Println("two or three")
default:
    fmt.Println("other")
}

// tagless switch（替代 if-else 链）
switch {
case x > 0:
    fmt.Println("positive")
case x < 0:
    fmt.Println("negative")
default:
    fmt.Println("zero")
}

// type switch
switch v := x.(type) {
case int:
    fmt.Println("int:", v)
case string:
    fmt.Println("string:", v)
}
```

---

## 四、函数

```go
// 基本函数
func add(a, b int) int {
    return a + b
}

// 多返回值（Go 标志特性）
func div(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

// 命名返回值
func split(sum int) (x, y int) {
    x = sum * 4 / 9
    y = sum - x
    return  // naked return
}

// 可变参数
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}
sum(1, 2, 3)        // 6
sum([]int{1, 2}...)  // 展开 slice

// 函数作为值（first-class）
func apply(nums []int, f func(int) int) []int {
    result := make([]int, len(nums))
    for i, v := range nums {
        result[i] = f(v)
    }
    return result
}

// 闭包
func counter() func() int {
    n := 0
    return func() int {
        n++
        return n
    }
}
c := counter()
c()  // 1
c()  // 2
```

---

## 五、数组与切片

### 数组（固定长度）

```go
var a [3]int               // [0, 0, 0]
a := [3]int{1, 2, 3}
a := [...]int{1, 2, 3, 4}  // 自动推断长度

// 二维数组
var grid [3][3]int
```

### 切片（动态数组，**最常用**）

```go
// 创建
s := []int{1, 2, 3}
s := make([]int, 5)       // 长度 5，容量 5
s := make([]int, 0, 10)   // 长度 0，容量 10

// 追加（可能触发扩容）
s = append(s, 1, 2, 3)

// 切片操作（左闭右开）
s := []int{1, 2, 3, 4, 5}
s[1:3]   // [2, 3]
s[:3]    // [1, 2, 3]
s[2:]    // [3, 4, 5]

// 复制
src := []int{1, 2, 3}
dst := make([]int, len(src))
copy(dst, src)

// 删除元素
s := []int{1, 2, 3, 4, 5}
s = append(s[:2], s[3:]...)  // 删除 index 2 → [1, 2, 4, 5]

// 长度 vs 容量
s := make([]int, 3, 10)
len(s)  // 3
cap(s)  // 10
```

---

## 六、Map

```go
// 创建
m := map[string]int{"a": 1, "b": 2}
m := make(map[string]int)

// 增删改查
m["c"] = 3
delete(m, "a")
v := m["b"]
v, ok := m["b"]  // ok 表示是否存在

// 遍历（顺序随机！）
for k, v := range m {
    fmt.Println(k, v)
}

// 坑：nil map 读不 panic，写会 panic
var m map[string]int  // nil
v := m["a"]           // ok，v = 0
m["a"] = 1            // panic: assignment to entry in nil map
```

---

## 七、Struct

```go
type Point struct {
    X, Y int
}

p := Point{X: 1, Y: 2}
p := Point{1, 2}        // 按顺序
p := new(Point)         // 返回 *Point

// 字段访问
p.X = 10

// 嵌套
type Rect struct {
    TopLeft, BottomRight Point
    Color                string
}

// 匿名字段（组合）
type Employee struct {
    Name   string
    int    // 匿名字段（类型名作为字段名）
}

e := Employee{Name: "Alice"}
e.int = 42
```

### 方法

```go
type Circle struct {
    Radius float64
}

// 值接收者
func (c Circle) Area() float64 {
    return 3.14 * c.Radius * c.Radius
}

// 指针接收者（可修改）
func (c *Circle) Scale(factor float64) {
    c.Radius *= factor
}

c := Circle{Radius: 5}
c.Area()             // 78.5
c.Scale(2)           // c.Radius = 10
```

---

## 八、指针

```go
// Go 指针不能运算（不像 C）
var p *int
i := 42
p = &i

fmt.Println(*p)  // 42
*p = 100
fmt.Println(i)   // 100

// new：分配零值内存
p := new(int)   // *int，*p = 0

// make：仅用于 slice / map / channel
s := make([]int, 5)
m := make(map[string]int)
ch := make(chan int)
```

---

## 九、字符串

```go
s := "hello, 世界"
len(s)               // 13（字节数）
utf8.RuneCountInString(s)  // 9（字符数）

// 切片（字节）
s[0]    // 'h'（byte）
s[7]    // 0xE4（"世" 的第一个字节，UTF-8）

// 遍历 rune
for i, r := range s {
    fmt.Printf("%d: %c\n", i, r)
}

// 转换
import "strings"
strings.Contains(s, "hello")
strings.HasPrefix(s, "hello")
strings.Split(s, ",")
strings.Join([]string{"a", "b"}, ",")
strings.ToUpper(s)

import "strconv"
i, err := strconv.Atoi("42")
s := strconv.Itoa(42)
```

---

## 十、错误处理

```go
// error 是内置接口
type error interface {
    Error() string
}

// 标准错误
import "errors"
err := errors.New("something wrong")
err := fmt.Errorf("invalid value: %d", x)

// 自定义错误
type MyError struct {
    Code    int
    Message string
}
func (e *MyError) Error() string {
    return fmt.Sprintf("code=%d, msg=%s", e.Code, e.Message)
}

// 错误判断
if err != nil {
    if errors.Is(err, sql.ErrNoRows) {
        // 处理 not found
    }
    var myErr *MyError
    if errors.As(err, &myErr) {
        fmt.Println(myErr.Code)
    }
    return err
}

// panic + recover（异常处理）
func riskyOp() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("recovered:", r)
        }
    }()
    panic("oops!")
}
```

---

## 关联章节

- **01-basics/overview**：Go 总览
- **01-basics/types-and-functions**：类型与函数
- **01-basics/error-handling**：错误处理
- **01-basics/package-and-module**：包与模块
- **01-basics/hello-world**：Hello World

## 一句话总结

> **Go 语法 = 25 关键字 + C 风格 + 类型后置**。**简洁、显式、一致**。
""")

add("01-basics/types-and-functions.md", r"""---
title: 类型与函数
---

# 类型与函数

深入 Go 类型系统：基础类型 / 复合类型 / 自定义类型 / 函数签名 / 闭包 / 错误处理。

## 一句话总结

> **Go 类型 = 基础类型 + slice/map/chan + struct/interface**。**函数：一等公民，支持多返回值、闭包、defer**。

---

## 一、类型分类

### 基础类型

```go
bool
string
int  int8  int16  int32  int64
uint uint8 uint16 uint32 uint64 uintptr
byte // uint8 别名
rune // int32 别名（Unicode code point）
float32 float64
complex64 complex128
```

### 复合类型

```go
[3]int                    // 数组
[]int                     // 切片
map[string]int            // map
*int                      // 指针
chan int                  // channel
func(int) int             // 函数
struct { X, Y int }       // 结构体
interface { Method() int } // 接口
```

### 类型别名 vs 自定义类型

```go
// 类型别名（完全等价）
type MyInt = int

// 自定义类型（不同类型）
type UserID int
var u UserID = 42
var i int = u  // 错误！必须转换：var i int = int(u)
```

---

## 二、自定义类型

### type 关键字

```go
// 定义新类型
type Celsius float64
type Fahrenheit float64

var c Celsius = 100
var f Fahrenheit = 212

// 类型转换
c = Celsius(100)

// 类型方法
func (c Celsius) ToFahrenheit() Fahrenheit {
    return Fahrenheit(c*9/5 + 32)
}

// 类型不能直接运算（必须转换）
// var sum Celsius = c + 100  // 错误！
```

### struct 类型

```go
type User struct {
    ID       int
    Name     string
    Email    string
    Age      int
    IsActive bool
    Profile  Profile  // 嵌套
}

type Profile struct {
    Bio  string
    Tags []string
}

// 字面量
u := User{
    ID:   1,
    Name: "Alice",
    Profile: Profile{
        Bio: "Go developer",
    },
}

// 零值
var u User  // 所有字段零值

// 比较：struct 是值类型，可比较
if u1 == u2 {  // 所有字段相等
    fmt.Println("equal")
}
```

### 类型嵌入（Embedding）

```go
type Animal struct {
    Name string
}
func (a *Animal) Speak() { fmt.Println("...") }

type Dog struct {
    *Animal  // 嵌入指针（提升字段和方法）
    Breed string
}

d := &Dog{
    Animal: &Animal{Name: "Rex"},
    Breed:  "Labrador",
}
d.Speak()          // 提升方法
d.Name             // 提升字段
```

---

## 三、函数

### 函数签名

```go
// 完整签名
func name(param1 type1, param2 type2) (returnType1, returnType2) {
    // body
}
```

### 多返回值

```go
// 标准模式：最后一个返回值是 error
func readFile(path string) ([]byte, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }
    return data, nil
}

// 调用
data, err := readFile("config.json")
if err != nil {
    log.Fatal(err)
}
```

### 命名返回值

```go
func divide(a, b float64) (quotient, remainder float64, err error) {
    if b == 0 {
        err = errors.New("division by zero")
        return  // 自动返回命名变量（零值）
    }
    quotient = a / b
    remainder = math.Mod(a, b)
    return
}
```

### 可变参数

```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

// 调用
sum(1, 2, 3)            // 直接传
sum(slice...)           // 展开 slice
sum()                   // 0
```

### defer

```go
func readFile(path string) error {
    f, err := os.Open(path)
    if err != nil {
        return err
    }
    defer f.Close()  // 函数返回前执行

    // 读文件
    return nil
}

// defer 执行顺序：LIFO（后进先出）
func demo() {
    defer fmt.Println("first")
    defer fmt.Println("second")
    defer fmt.Println("third")
}
// 输出：third, second, first

// defer 修改返回值
func double(x int) (result int) {
    defer func() { result *= 2 }()
    return x  // result = x * 2
}
```

---

## 四、闭包

### 基本闭包

```go
func adder() func(int) int {
    sum := 0
    return func(x int) int {
        sum += x
        return sum
    }
}

a := adder()
a(1)  // 1
a(2)  // 3
a(3)  // 6

// 闭包捕获变量（引用，不是值）
```

### 闭包陷阱：循环变量

```go
// Go ≤1.21：循环变量共享
funcs := []func(){}
for _, v := range []int{1, 2, 3} {
    funcs = append(funcs, func() { fmt.Println(v) })
}
for _, f := range funcs {
    f()
}
// 输出：3 3 3（所有闭包共享同一个 v）

// 修复 1：传参
for _, v := range []int{1, 2, 3} {
    v := v  // shadow
    funcs = append(funcs, func() { fmt.Println(v) })
}

// 修复 2：Go ≥1.22 自动修复
```

---

## 五、函数作为值

```go
// 函数类型
type Handler func(http.ResponseWriter, *http.Request)

// 函数作为参数
func apply(nums []int, f func(int) int) []int {
    out := make([]int, len(nums))
    for i, v := range nums {
        out[i] = f(v)
    }
    return out
}

// 函数作为返回值（工厂模式）
func getOp(op string) func(int, int) int {
    switch op {
    case "+":
        return func(a, b int) int { return a + b }
    case "-":
        return func(a, b int) int { return a - b }
    default:
        return nil
    }
}
```

### 匿名函数

```go
// IIFE（立即执行）
func() {
    fmt.Println("IIFE")
}()

// goroutine 中
go func() {
    fmt.Println("in goroutine")
}()
```

---

## 六、方法

### 值接收者 vs 指针接收者

```go
type Counter struct {
    n int
}

// 值接收者（不修改）
func (c Counter) Value() int {
    return c.n
}

// 指针接收者（可修改）
func (c *Counter) Increment() {
    c.n++
}

c := Counter{}
c.Increment()  // 实际调用 (&c).Increment()
c.Value()      // 实际调用 (c).Value()
```

### 接收者选择

```go
// 推荐一致性：要么全用值，要么全用指针
type MyStruct struct{}

// ❌ 混用
func (s MyStruct) Method1() {}  // 值
func (s *MyStruct) Method2() {} // 指针

// ✅ 一致
func (s *MyStruct) Method1() {}
func (s *MyStruct) Method2() {}
```

---

## 七、接口

```go
// 接口定义
type Speaker interface {
    Speak() string
}

// 接口实现（隐式）
type Dog struct{}
func (d Dog) Speak() string { return "Woof!" }

type Cat struct{}
func (c Cat) Speak() string { return "Meow!" }

// 多态
func greet(s Speaker) {
    fmt.Println(s.Speak())
}

greet(Dog{})  // Woof!
greet(Cat{})  // Meow!
```

### 空接口（interface{} / any）

```go
// any 是 interface{} 别名（Go 1.18+）
var i any = 42
i = "hello"
i = []int{1, 2, 3}

// 类型断言
v, ok := i.(int)
if ok {
    fmt.Println("int:", v)
}

// type switch
switch v := i.(type) {
case int:
    fmt.Println("int:", v)
case string:
    fmt.Println("string:", v)
}
```

---

## 八、泛型（Go 1.18+）

```go
// 泛型函数
func map[T, U any](slice []T, f func(T) U) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = f(v)
    }
    return result
}

nums := []int{1, 2, 3}
doubled := map(nums, func(n int) int { return n * 2 })
// [2, 4, 6]

// 泛型类型
type Stack[T any] struct {
    items []T
}
func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}
func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}

s := Stack[int]{}
s.Push(1)
s.Push(2)
v, ok := s.Pop()  // 2, true
```

---

## 关联章节

- **01-basics/overview**：Go 总览
- **01-basics/syntax-fundamentals**：语法速览
- **01-basics/error-handling**：错误处理

## 一句话总结

> **Go 类型系统 = 简洁实用**。**struct + interface + 泛型（1.18+）+ 错误显式返回**。
""")

add("01-basics/error-handling.md", r"""---
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
""")

add("01-basics/package-and-module.md", r"""---
title: 包与模块管理
---

# 包与模块管理

Go 包管理从 GOPATH（≤Go 1.10）演进到 Go Modules（≥Go 1.11），现在已成为云原生生态的事实标准。

## 一句话总结

> **Go Modules = go.mod + go.sum + semantic import versioning**。**核心：包是目录 / 模块是版本化单元 / 语义化版本**。

---

## 一、包（Package）

### 包基本概念

```go
// 文件：myapp/handler/user.go
package handler  // 包名

import (
    "fmt"
    "net/http"
    "github.com/gin-gonic/gin"
    "myapp/internal/model"  // 同一模块内的包
)

// 导出（首字母大写）
func GetUser(c *gin.Context) { ... }

// 不导出（首字母小写）
func validateInput(...) { ... }
```

### 包导入

```go
// 标准导入
import "fmt"

// 别名导入
import f "fmt"

// 点导入（直接访问包内导出符号，不推荐）
import . "fmt"

// 下划线导入（仅执行 init 函数）
import _ "github.com/lib/pq"  // 注册 PostgreSQL 驱动
```

### 包初始化

```go
// init 函数：包加载时自动执行（可多个）
func init() {
    // 注册驱动、初始化全局变量等
}

// 使用 init 的场景：
// - 注册数据库驱动（database/sql）
// - 注册 HTTP handler（http.Handle）
// - 验证配置
```

---

## 二、模块（Module）

### go.mod 文件

```go
// go.mod
module github.com/me/myapp

go 1.22

require (
    github.com/gin-gonic/gin v1.10.0
    github.com/spf13/viper v1.18.0
    github.com/lib/pq v1.10.9
)

require (
    // 间接依赖（由直接依赖引入）
    github.com/bytedance/sonic v1.11.6 // indirect
    golang.org/x/sys v0.15.0 // indirect
)

// 替换（用于本地开发 / fork）
replace github.com/old/pkg => github.com/me/pkg v1.0.0
replace github.com/old/pkg => ../local-pkg

// 排除（用于安全漏洞）
exclude github.com/bad/pkg v1.0.0

// 撤回（用于强制升级）
retract [v1.0.0, v1.1.0]
```

### go.sum 文件

```text
// go.sum：依赖校验和（必须 commit）
github.com/gin-gonic/gin v1.10.0 h1:abc...
github.com/gin-gonic/gin v1.10.0/go.mod h1:def...
```

- **h1**：模块内容的哈希（zip 文件）
- **/go.mod h1**：go.mod 文件的哈希
- **作用**：防止依赖被篡改

### 模块路径

```
github.com/me/myapp           // 模块路径（全局唯一）
github.com/me/myapp/cmd/api   // 包路径（模块路径 + 子目录）
github.com/me/myapp/internal  // 内部包（仅本模块可 import）
```

---

## 三、Go Modules 命令

### 初始化

```bash
# 新项目
mkdir myapp && cd myapp
go mod init github.com/me/myapp

# 输出 go.mod 文件
```

### 添加依赖

```bash
# 自动：import 时 go run/build/test 会自动下载
# 手动
go get github.com/gin-gonic/gin          # 最新版
go get github.com/gin-gonic/gin@v1.10.0  # 指定版本
go get github.com/gin-gonic/gin@latest   # 最新
go get -u github.com/gin-gonic/gin       # 升级到最新 minor/patch
go get -u=patch github.com/gin-gonic/gin # 仅升级 patch

# 添加并自动 tidy
go get github.com/gin-gonic/gin && go mod tidy
```

### 清理依赖

```bash
go mod tidy  # 添加缺失依赖 + 移除未使用依赖
```

### 下载依赖

```bash
go mod download           # 下载所有依赖到 $GOPATH/pkg/mod
go mod download -x        # 显示下载细节
```

### Vendor（本地依赖目录）

```bash
go mod vendor  # 创建 vendor/ 目录，复制所有依赖

# 优点：编译不依赖网络
# 缺点：vendor 目录需 commit（增加仓库大小）
# 适用：CI/CD 离线环境 / K8s 镜像构建
```

### 查看依赖

```bash
go list -m all                          # 所有依赖
go list -m -versions github.com/gin-gonic/gin  # 版本列表
go mod graph                            # 依赖图
go mod why github.com/gin-gonic/gin     # 为什么需要这个依赖
```

### 升级 / 降级

```bash
go get github.com/gin-gonic/gin@v1.9.0  # 降级到 1.9.0
go get -u github.com/gin-gonic/gin       # 升级
go mod tidy                              # 同步 go.mod
```

---

## 四、语义化版本（SIV）

### 版本格式

```
vMAJOR.MINOR.PATCH
v1.10.0
v2.0.0
```

- **MAJOR**：不兼容 API 变更
- **MINOR**：向后兼容的功能新增
- **PATCH**：向后兼容的 bug fix

### Go Modules 的特殊规则

```text
v0.x.x  → 每次 MINOR 升级可能不兼容（视为不稳定）
v1.x.x+ → 严格遵循 SIV
v2+     → 模块路径必须带版本后缀
```

### 主版本升级

```go
// v1
import "github.com/gin-gonic/gin"

// v2：模块路径必须变
import "github.com/gin-gonic/gin/v2"
```

**原因**：避免主版本不兼容的依赖被自动升级。

### pseudo-version（伪版本）

```go
// git commit 没有打 tag 时
github.com/me/myapp v0.0.0-20210101000000-abc123def456
```

- 格式：`v0.0.0-yyyymmddhhmmss-commitHash`
- 用途：基于 commit 的版本

---

## 五、依赖冲突解决

### Minimal Version Selection（MVS）

Go 使用 MVS 算法选择依赖版本：
- 选所有依赖中**要求的最小版本**

### 实战冲突

```go
// 模块 A 要求 gin v1.9.0
// 模块 B 要求 gin v1.10.0
// → 最终选 v1.10.0（MVS）
```

### 强制版本

```go
// 在 go.mod 中显式 require
require github.com/gin-gonic/gin v1.10.0

// 使用 replace
replace github.com/gin-gonic/gin => github.com/me/gin v1.10.0-fork
```

---

## 六、Private Module（私有模块）

### 配置 GOPROXY

```bash
# 默认
GOPROXY=https://proxy.golang.org,direct

# 国内
GOPROXY=https://goproxy.cn,direct

# 公司内部
GOPROXY=https://goproxy.mycompany.com,https://proxy.golang.org,direct
```

### 配置 GONOSUMCHECK（跳过校验）

```bash
# 公司内部私有模块
GONOSUMCHECK=github.com/mycompany/*
GONOSUMCHECK="*"  # 全部跳过（不推荐）
```

### 配置 GONOPROXY（不走代理）

```bash
# 公司内部私有模块不走代理（直接从 Git 拉）
GONOPROXY=github.com/mycompany/*
```

### 配置 .netrc

```text
# ~/.netrc
machine github.com
login your-username
password your-token
```

---

## 七、Workspaces（Go 1.18+）

### 多模块并行开发

```bash
# go.work
go work init ./api ./service ./web
```

```go
// go.work
go 1.22

use (
    ./api
    ./service
    ./web
)

// 优势：本地修改多个模块，无需发布即可联动
```

---

## 八、最佳实践

### 1. 提交 go.sum

```bash
git add go.mod go.sum
git commit -m "deps: update gin to v1.10.0"
```

### 2. 定期升级

```bash
# 每周/每月升级一次
go get -u ./...
go mod tidy
```

### 3. 用 tools.go 管理开发工具

```go
// tools.go（不参与编译）
//go:build tools
// +build tools

package tools

import (
    _ "github.com/golangci/golangci-lint/cmd/golangci-lint"
    _ "github.com/swaggo/swag/cmd/swag"
)

// 用法：go run github.com/swaggo/swag/cmd/swag init
```

### 4. CI/CD 缓存

```bash
# GitHub Actions
- uses: actions/setup-go@v5
  with:
    cache: true  # 自动缓存 go 模块
```

---

## 关联章节

- **01-basics/overview**：Go 总览
- **01-basics/types-and-functions**：类型与函数
- **03-ecosystem/go-toolchain**：Go 工具链

## 一句话总结

> **Go Modules = 语义化版本 + go.mod + go.sum + MVS 算法**。**简单、稳定、可重现**。
""")

add("01-basics/hello-world.md", r"""---
title: Hello World 实战
---

# Hello World 实战

从安装到第一个 HTTP 服务：5 分钟跑通，10 分钟理解项目结构。

## 一句话总结

> **Hello World = 安装 Go → go mod init → 写 main.go → go run**。**5 分钟跑通第一个 Go 程序**。

---

## 一、安装 Go

### macOS

```bash
# Homebrew
brew install go

# 官方 pkg（推荐用于开发）
wget https://go.dev/dl/go1.22.5.darwin-amd64.pkg
# 或 ARM64
wget https://go.dev/dl/go1.22.5.darwin-arm64.pkg
# 双击安装

# 验证
go version
```

### Linux

```bash
# 下载
wget https://go.dev/dl/go1.22.5.linux-amd64.tar.gz

# 解压到 /usr/local
sudo tar -C /usr/local -xzf go1.22.5.linux-amd64.tar.gz

# 添加 PATH
echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
source ~/.bashrc

# 验证
go version
```

### Windows

```powershell
# 下载 MSI
# https://go.dev/dl/go1.22.5.windows-amd64.msi
# 双击安装

# 验证
go version
```

### 多版本管理

```bash
# g（gimme / gvm）
curl -sSL https://git.io/g-install | sh -s
g install 1.22.5
g use 1.22.5

# asdf
asdf plugin-add golang
asdf install golang 1.22.5
asdf global golang 1.22.5
```

---

## 二、第一个程序

### 创建项目

```bash
mkdir hello-go && cd hello-go
go mod init github.com/me/hello-go
```

### main.go

```go
// hello-go/main.go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

### 运行

```bash
# 编译并运行
go run main.go

# 输出：Hello, World!

# 只编译（不运行）
go build -o hello

# 编译 + 安装到 $GOPATH/bin
go install
```

### 交叉编译

```bash
# Linux
GOOS=linux GOARCH=amd64 go build -o hello-linux

# macOS
GOOS=darwin GOARCH=arm64 go build -o hello-mac

# Windows
GOOS=windows GOARCH=amd64 go build -o hello.exe

# ARM64 (Raspberry Pi / M1 Mac)
GOOS=linux GOARCH=arm64 go build -o hello-arm
```

---

## 三、第一个 HTTP 服务

### main.go

```go
// hello-go/main.go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
    })

    http.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
        fmt.Fprintln(w, "ok")
    })

    fmt.Println("Server starting on :8080")
    http.ListenAndServe(":8080", nil)
}
```

### 运行

```bash
go run main.go

# 测试
curl http://localhost:8080/world
# 输出：Hello, world!

curl http://localhost:8080/healthz
# 输出：ok
```

---

## 四、第一个 Gin 项目

### 初始化

```bash
mkdir gin-demo && cd gin-demo
go mod init github.com/me/gin-demo

# 添加 Gin 依赖
go get github.com/gin-gonic/gin

# 自动 go mod tidy
go mod tidy
```

### main.go

```go
package main

import (
    "net/http"
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()

    r.GET("/", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{
            "message": "Hello, World!",
        })
    })

    r.GET("/users/:id", func(c *gin.Context) {
        id := c.Param("id")
        c.JSON(http.StatusOK, gin.H{
            "user_id": id,
        })
    })

    r.POST("/users", func(c *gin.Context) {
        var user struct {
            Name  string `json:"name"`
            Email string `json:"email"`
        }
        if err := c.ShouldBindJSON(&user); err != nil {
            c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
            return
        }
        c.JSON(http.StatusCreated, user)
    })

    r.Run(":8080")
}
```

### 运行

```bash
go run main.go

# 测试
curl http://localhost:8080/
curl http://localhost:8080/users/42
curl -X POST http://localhost:8080/users -d '{"name":"Alice","email":"alice@example.com"}'
```

---

## 五、项目结构

### 小型项目

```
hello-go/
├── go.mod
├── go.sum
├── main.go              # 所有代码在一个文件
└── README.md
```

### 中型项目

```
gin-demo/
├── go.mod
├── go.sum
├── main.go              # 入口
├── handler/             # HTTP handler
│   ├── user.go
│   └── order.go
├── service/             # 业务逻辑
│   ├── user.go
│   └── order.go
├── model/               # 数据模型
│   ├── user.go
│   └── order.go
├── middleware/          # 中间件
│   ├── auth.go
│   └── logging.go
└── config/              # 配置
    └── config.go
```

### 大型项目（标准 layout）

```
myapp/
├── cmd/                 # 多个 main 入口
│   ├── api/main.go
│   └── worker/main.go
├── internal/            # 内部包（不可被外部 import）
│   ├── handler/
│   ├── service/
│   ├── repository/
│   └── model/
├── pkg/                 # 公共包（可被外部 import）
│   └── util/
├── api/                 # API 定义（protobuf / openapi）
├── configs/             # 配置文件
├── scripts/             # 构建脚本
├── docs/                # 文档
├── deployments/         # Docker / K8s
├── go.mod
├── go.sum
└── Makefile
```

---

## 六、常用命令

```bash
# 构建
go build                # 当前包
go build ./...          # 全部包
go build -o myapp       # 指定输出名
go build -ldflags="-s -w" -o myapp  # 去除符号表（减小二进制）

# 运行
go run main.go
go run .

# 测试
go test ./...
go test -v
go test -cover
go test -race

# 静态分析
go vet ./...
gofmt -w .
goimports -w .

# 依赖
go mod tidy
go get github.com/foo/bar

# 清理
go clean -cache
go clean -modcache
```

---

## 七、IDE 配置

### VS Code

```json
// .vscode/settings.json
{
    "go.useLanguageServer": true,
    "go.gopath": "/Users/me/go",
    "go.toolsGopath": false,
    "go.lintTool": "golangci-lint",
    "go.formatTool": "goimports",
    "[go]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

### GoLand / IntelliJ

- 安装 **Go 插件**
- File → Settings → Go → GOROOT：选择 Go 安装目录
- File → Settings → Go → GOPATH：配置 GOPATH

### vim / neovim

```vim
" .vimrc
Plug 'fatih/vim-go', { 'do': ':GoUpdateBinaries' }
let g:go_fmt_command = 'goimports'
```

---

## 八、调试技巧

### 1. fmt.Println 调试

```go
// 简单粗暴
fmt.Printf("DEBUG: x=%v, y=%v\n", x, y)

// 结构化
log.Printf("DEBUG: user=%+v", user)
```

### 2. delve 调试器

```bash
# 安装
go install github.com/go-delve/delve/cmd/dlv@latest

# 调试
dlv debug main.go

# 命令
(dlv) break main.go:10    # 断点
(dlv) continue             # 继续
(dlv) next                 # 下一步
(dlv) print x              # 打印变量
```

### 3. pprof 性能分析

```go
import _ "net/http/pprof"

go func() {
    http.ListenAndServe("localhost:6060", nil)
}()
```

```bash
# CPU profile
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Heap profile
go tool pprof http://localhost:6060/debug/pprof/heap
```

### 4. race detector

```bash
go test -race ./...
go run -race main.go
```

---

## 关联章节

- **01-basics/overview**：Go 总览
- **01-basics/syntax-fundamentals**：语法速览
- **03-ecosystem/go-toolchain**：Go 工具链
- **03-ecosystem/standard-library**：标准库

## 一句话总结

> **Hello World = 安装 + go mod + main.go + go run**。**5 分钟跑通第一个 Go 程序**。
""")


add("02-concurrency/goroutine.md", r"""---
title: goroutine
---

# goroutine

goroutine 是 Go 最核心的并发原语：轻量协程，由 Go runtime 调度，单个程序可同时运行数十万个 goroutine。

## 一句话总结

> **goroutine = Go runtime 调度的协程（M:N 模型）**。**核心：go 关键字启动 / 2KB 栈 / GMP 调度 / 协作式+抢占式调度**。

---

## 一、基本用法

```go
// 启动 goroutine
go func() {
    fmt.Println("hello from goroutine")
}()

// 启动带参数的 goroutine
go func(msg string) {
    fmt.Println(msg)
}("hello")

// 启动调用方法的 goroutine
go obj.Method()
```

### 与函数调用的对比

```go
// 同步调用（阻塞）
func() {
    fmt.Println("sync")
}()

// 异步调用（不阻塞）
go func() {
    fmt.Println("async")
}()
fmt.Println("main")
// 输出：main（顺序不固定，async 可能先输出）
```

---

## 二、goroutine 生命周期

### 状态机

```
        ┌──────────┐
        │  Created │ (go 关键字创建)
        └─────┬────┘
              ▼
        ┌──────────┐
        │ Runnable │ (加入队列，等待调度)
        └─────┬────┘
              ▼
        ┌──────────┐
        │ Running  │ (M 上执行)
        └─────┬────┘
              ▼
        ┌──────────┐
        │  Waiting │ (channel / IO / syscall 阻塞)
        └─────┬────┘
              ▼
        ┌──────────┐
        │   Dead   │ (函数返回 / panic)
        └──────────┘
```

### goroutine 退出

```go
// 1. 函数返回：goroutine 正常结束
go func() {
    fmt.Println("done")
}()  // 函数返回后 goroutine 死亡

// 2. 主 goroutine 退出：所有 goroutine 强制结束
func main() {
    go func() {
        time.Sleep(10 * time.Second)
    }()
    // main 直接返回，未等 goroutine 完成
}

// 3. panic 未捕获：goroutine 死亡
go func() {
    panic("oops")  // goroutine crash，不影响 main
}()

// 4. context 取消：goroutine 主动退出
ctx, cancel := context.WithCancel(context.Background())
go func() {
    <-ctx.Done()
    fmt.Println("cancelled")
}()
cancel()
```

---

## 三、GMP 调度模型

### 三个核心组件

```
G (Goroutine) — 用户态协程（初始栈 2KB）
M (Machine)   — OS 线程
P (Processor) — 逻辑处理器（默认 GOMAXPROCS = CPU 核数）
```

### 调度流程

```
1. go func() 创建 G
2. G 加入 P 的 local run queue
3. M（绑定了 P）从 local queue 取 G 执行
4. local queue 满（256）→ 移动到 global queue
5. local queue 空 → work stealing（从其他 P 偷 G）
6. global queue 空 → 从 net poller / syscall 返回的 G 取
```

### M:N 调度优势

| 模型 | 调度方 | 数量级 |
|---|---|---|
| **1:1** (Java Thread) | OS kernel | 千级别 |
| **N:1** (Python asyncio) | 用户态 | 单线程 |
| **M:N** (Go) | Go runtime | 数十万 |

- **轻量**：创建 / 切换成本低
- **透明**：开发者无感
- **可扩展**：单进程轻松支持百万 goroutine

---

## 四、GOMAXPROCS

### 设置并行度

```go
// 默认 = CPU 核数
runtime.GOMAXPROCS(8)

// 通过环境变量
// GOMAXPROCS=4 ./myapp

// 查看当前值
fmt.Println(runtime.GOMAXPROCS(0))
```

### 何时调整

- **CPU 密集任务**：GOMAXPROCS = CPU 核数
- **I/O 密集任务**：可适当调大（让 M 多等待 syscall）
- **容器环境**：GOMAXPROCS 应该 = 容器 CPU limit（可用 `automaxprocs` 自动检测）

### uber-go/automaxprocs

```go
import _ "go.uber.org/automaxprocs"

// 启动时自动检测容器 CPU limit 并设置 GOMAXPROCS
```

---

## 五、goroutine 实战

### 1. 并行计算

```go
func parallelSum(nums []int) int {
    n := len(nums)
    if n == 0 { return 0 }

    mid := n / 2
    sumCh := make(chan int, 2)

    go func() {
        s := 0
        for _, v := range nums[:mid] {
            s += v
        }
        sumCh <- s
    }()

    go func() {
        s := 0
        for _, v := range nums[mid:] {
            s += v
        }
        sumCh <- s
    }()

    return <-sumCh + <-sumCh
}
```

### 2. goroutine 池

```go
type WorkerPool struct {
    jobs    chan Job
    results chan Result
    workers int
}

func NewWorkerPool(workers int) *WorkerPool {
    return &WorkerPool{
        jobs:    make(chan Job, 100),
        results: make(chan Result, 100),
        workers: workers,
    }
}

func (p *WorkerPool) Start() {
    for i := 0; i < p.workers; i++ {
        go func(workerID int) {
            for job := range p.jobs {
                p.results <- processJob(job)
            }
        }(i)
    }
}
```

### 3. goroutine 监控

```go
import "runtime"

// 当前 goroutine 数量
fmt.Println("goroutines:", runtime.NumGoroutine())

// 设置最多 goroutine（软限制）
runtime.GOMAXPROCS(8)

// 强制 GC（一般不需要）
runtime.GC()
```

---

## 六、goroutine 泄漏

### 什么是泄漏

goroutine 启动后**永远无法结束**，占用内存不释放。

### 常见原因

```go
// 1. channel 永远没人接收
func leak1() {
    ch := make(chan int)
    go func() { ch <- 1 }()  // 永久阻塞
}

// 2. 死锁
func leak2() {
    var mu sync.Mutex
    mu.Lock()
    go func() { mu.Lock() }()  // 永久阻塞
}

// 3. 死循环
func leak3() {
    go func() {
        for {
            // 没有退出条件
        }
    }()
}

// 4. select 缺少退出分支
func leak4() {
    ch := make(chan int)
    go func() {
        select {
        case <-ch:
            // 永远不会执行
        }
    }()
}
```

### 检测泄漏

```go
// pprof 检测
import _ "net/http/pprof"

// goroutine profile
curl http://localhost:6060/debug/pprof/goroutine?debug=2

// 输出：所有 goroutine 的堆栈
// 如果某个 goroutine 数量持续增长 → 泄漏
```

### 修复模式

```go
// 用 context 退出
func noLeak(ctx context.Context) {
    ch := make(chan int)
    go func() {
        select {
        case <-ch:
            // work
        case <-ctx.Done():
            return
        }
    }()
}
```

---

## 七、goroutine 调试

### 1. runtime.Stack

```go
buf := make([]byte, 1<<16)
n := runtime.Stack(buf, true)  // true = 所有 goroutine
fmt.Println(string(buf[:n]))
```

### 2. pprof goroutine profile

```go
import _ "net/http/pprof"

go http.ListenAndServe("localhost:6060", nil)
```

```bash
# 浏览器查看
http://localhost:6060/debug/pprof/goroutine?debug=1

# 命令行
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

### 3. goleak 工具

```go
import "go.uber.org/goleak"

func TestNoLeak(t *testing.T) {
    defer goleak.VerifyNone(t)
    // ...
}
```

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/channel**：channel
- **02-concurrency/sync-package**：sync 包
- **02-concurrency/context**：context
- **02-concurrency/patterns**：并发模式
- **06-advanced/runtime**：GMP 调度器

## 一句话总结

> **goroutine = 轻量协程 + M:N 调度 + GMP 模型**。**几十行代码启动数万个并发任务**。
""")


add("02-concurrency/channel.md", r"""---
title: channel
---

# channel

channel 是 goroutine 之间的通信机制：类型安全的消息队列，遵循 CSP（Communicating Sequential Processes）模型。

## 一句话总结

> **channel = goroutine 间的消息队列**。**核心：make 创建 / ch <- 发送 / <-ch 接收 / close 关闭 / select 多路复用**。

---

## 一、基本用法

### 创建

```go
// 无缓冲 channel（同步）
ch := make(chan int)

// 有缓冲 channel（异步）
ch := make(chan int, 10)

// 只发送 / 只接收
sendCh := chan<- int   // 只发送
recvCh := <-chan int   // 只接收
```

### 发送与接收

```go
ch := make(chan int)

// 发送（阻塞直到有接收者）
go func() { ch <- 42 }()

// 接收（阻塞直到有数据）
v := <-ch

// 多返回值接收
v, ok := <-ch  // ok 表示 channel 是否关闭
```

### 关闭

```go
ch := make(chan int)
close(ch)

// 检查是否关闭
v, ok := <-ch
if !ok {
    // channel 已关闭
}

// 关闭后发送会 panic
// ch <- 1  // panic: send on closed channel

// 重复关闭会 panic
// close(ch) // panic: close of closed channel

// 关闭 nil channel 会 panic
var ch chan int
// close(ch) // panic: close of nil channel
```

---

## 二、channel 状态

| 操作 | nil channel | 已关闭 channel | 正常 channel |
|---|---|---|---|
| **发送** | 永久阻塞 | panic | 阻塞 / 发送 |
| **接收** | 永久阻塞 | 返回零值 + false | 阻塞 / 接收 |
| **关闭** | panic | panic | 关闭成功 |
| **len** | 0 | 0 | 缓冲中元素数 |
| **cap** | 0 | 0 | 缓冲容量 |

### 利用 nil channel

```go
// 用 nil channel 禁用某个分支（select 中常用）
func merge(ch1, ch2 <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for ch1 != nil || ch2 != nil {
            select {
            case v, ok := <-ch1:
                if !ok { ch1 = nil; continue }
                out <- v
            case v, ok := <-ch2:
                if !ok { ch2 = nil; continue }
                out <- v
            }
        }
    }()
    return out
}
```

---

## 三、缓冲 vs 无缓冲

### 无缓冲（同步）

```go
ch := make(chan int)  // 容量 0

// 发送阻塞直到有接收者
// 接收阻塞直到有发送者
// 用途：同步信号、握手
```

### 有缓冲（异步）

```go
ch := make(chan int, 10)  // 容量 10

// 发送：缓冲未满时不阻塞，缓冲满时阻塞
// 接收：缓冲非空时不阻塞，缓冲空时阻塞
// 用途：消息队列、限流
```

### 容量选择

```text
小容量（1-10）：同步信号、限流
中容量（100-1000）：任务队列
大容量（10000+）：批处理
无缓冲：必须同步
```

---

## 四、channel 方向

### 双向 vs 单向

```go
// 双向
ch := make(chan int)

// 单向（只发送）
var sendCh chan<- int = ch

// 单向（只接收）
var recvCh <-chan int = ch

// 转换：双向可以隐式转单向，单向不能转双向
```

### 函数签名推荐

```go
// 生产者：参数 chan<- T（只发送）
func produce(ch chan<- int) {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    close(ch)
}

// 消费者：参数 <-chan T（只接收）
func consume(ch <-chan int) {
    for v := range ch {
        fmt.Println(v)
    }
}

// 用户：双向 channel
func main() {
    ch := make(chan int)
    go produce(ch)
    consume(ch)
}
```

**好处**：编译期保证职责单一。

---

## 五、select 多路复用

### 基本 select

```go
select {
case msg := <-ch1:
    fmt.Println("ch1:", msg)
case msg := <-ch2:
    fmt.Println("ch2:", msg)
case ch3 <- 42:
    fmt.Println("sent to ch3")
default:
    fmt.Println("no channel ready")
}
```

### 超时模式

```go
select {
case res := <-ch:
    return res
case <-time.After(1 * time.Second):
    return errors.New("timeout")
}
```

### context 取消

```go
select {
case res := <-ch:
    return res
case <-ctx.Done():
    return ctx.Err()
}
```

### 心跳检测

```go
heartbeat := time.NewTicker(1 * time.Second)
defer heartbeat.Stop()

for {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-heartbeat.C:
        // 健康检查 / 续约
    case msg := <-ch:
        // 处理消息
    }
}
```

### 非阻塞接收

```go
select {
case msg := <-ch:
    fmt.Println(msg)
default:
    fmt.Println("no message")
}
```

---

## 六、关闭 channel 的规则

### 谁创建谁关闭

```go
// ✅ 推荐：发送方关闭
func producer(ch chan<- int) {
    for i := 0; i < 10; i++ {
        ch <- i
    }
    close(ch)  // 发送方关闭
}

func consumer(ch <-chan int) {
    for v := range ch {  // 自动检测关闭
        fmt.Println(v)
    }
}
```

### 多个发送方

```go
// 用 sync.Once 确保只关闭一次
var once sync.Once
func closeCh(ch chan int) {
    once.Do(func() {
        close(ch)
    })
}
```

### 通知式 channel

```go
// 不发送数据，只用作通知（关闭即可）
done := make(chan struct{})
go func() {
    // do work
    close(done)  // 通知完成
}()
<-done  // 等待完成
```

---

## 七、channel 实战模式

### 1. 信号量（限流）

```go
sem := make(chan struct{}, 10)  // 最多 10 个并发
for _, item := range items {
    sem <- struct{}{}  // 获取信号量
    go func(item Item) {
        defer func() { <-sem }()  // 释放信号量
        process(item)
    }(item)
}
```

### 2. Pipeline

```go
// 阶段 1
gen := func(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

// 阶段 2
sq := func(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

// 使用
for v := range sq(gen(1, 2, 3)) {
    fmt.Println(v)  // 1, 4, 9
}
```

### 3. Fan-out / Fan-in

```go
// Fan-out：多个 goroutine 读同一个 channel
// Fan-in：多个 channel 合并到一个

func fanIn(cs ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup
    for _, c := range cs {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(c)
    }
    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}
```

### 4. Context 取消传播

```go
func worker(ctx context.Context, ch <-chan int) {
    for {
        select {
        case <-ctx.Done():
            return
        case v, ok := <-ch:
            if !ok {
                return
            }
            // 处理 v
        }
    }
}
```

---

## 八、channel 性能

### 性能开销

- **无缓冲**：~100ns（每次 send/receive）
- **有缓冲**：~50ns（非阻塞时）
- **比 Mutex**：快 2-10x

### 性能陷阱

```go
// 1. 频繁的发送/接收（高频场景考虑 sync.Pool）
// 2. 大 channel 缓冲（占用内存）
// 3. 阻塞 channel 导致 goroutine 堆积
```

### channel vs Mutex 选择

| 场景 | 推荐 |
|---|---|
| **数据流 / 消息队列** | channel |
| **共享状态 / 计数器** | Mutex / atomic |
| **复杂状态同步** | Mutex + channel |
| **通知信号** | channel（close 即通知） |

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/goroutine**：goroutine
- **02-concurrency/sync-package**：sync 包
- **02-concurrency/context**：context
- **02-concurrency/patterns**：并发模式

## 一句话总结

> **channel = goroutine 间的消息队列**。**CSP 模型：通信代替共享内存**。
""")


add("02-concurrency/sync-package.md", r"""---
title: sync 包
---

# sync 包

Go 标准库 sync 包提供传统并发原语：Mutex、WaitGroup、Once、Pool 等。channel 是 Go 的"高级抽象"，sync 包则是"底层原语"。

## 一句话总结

> **sync 包 = Mutex + WaitGroup + Once + Pool + atomic**。**核心：锁保护共享内存 + 信号量同步 + 对象池复用**。

---

## 一、Mutex（互斥锁）

### 基本用法

```go
var (
    mu sync.Mutex
    counter int
)

func increment() {
    mu.Lock()
    defer mu.Unlock()
    counter++
}
```

### RWMutex（读写锁）

```go
var (
    rwmu sync.RWMutex
    config map[string]string
)

// 读（多个 goroutine 可同时读）
func get(key string) string {
    rwmu.RLock()
    defer rwmu.RUnlock()
    return config[key]
}

// 写（独占）
func set(key, value string) {
    rwmu.Lock()
    defer rwmu.Unlock()
    config[key] = value
}
```

### Mutex vs RWMutex 选择

| 场景 | 推荐 |
|---|---|
| 读多写少（>10:1） | RWMutex |
| 写多读少 | Mutex |
| 简单计数 / 状态 | Mutex 或 atomic |

---

## 二、WaitGroup（等待组）

### 基本用法

```go
var wg sync.WaitGroup

for i := 0; i < 10; i++ {
    wg.Add(1)  // 计数器 +1
    go func(i int) {
        defer wg.Done()  // 计数器 -1
        fmt.Println(i)
    }(i)
}

wg.Wait()  // 阻塞直到计数器 = 0
```

### 注意事项

```go
// ❌ 错：Add 在 goroutine 内（可能 Wait 已经返回）
for i := 0; i < 10; i++ {
    go func() {
        wg.Add(1)  // 危险！
        defer wg.Done()
    }()
}
wg.Wait()

// ✅ 对：Add 在 goroutine 外
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
    }()
}
wg.Wait()
```

### WaitGroup vs errgroup

```go
// WaitGroup：等待完成，不收集错误
var wg sync.WaitGroup
wg.Add(2)
go func() { defer wg.Done() }()
go func() { defer wg.Done() }()
wg.Wait()

// errgroup：等待完成 + 收集错误
import "golang.org/x/sync/errgroup"

var g errgroup.Group
g.Go(func() error { return nil })
g.Go(func() error { return errors.New("failed") })
if err := g.Wait(); err != nil {
    log.Fatal(err)  // 第一个错误
}
```

---

## 三、Once（只执行一次）

### 基本用法

```go
var (
    instance *Singleton
    once     sync.Once
)

func GetInstance() *Singleton {
    once.Do(func() {
        instance = &Singleton{
            conn: openDB(),
        }
    })
    return instance
}
```

### 内部实现

```go
// 标准库实现
func (o *Once) Do(f func()) {
    if o.done.Load() == 0 {  // fast path
        o.doSlow(f)
    }
}

func (o *Once) doSlow(f func()) {
    o.m.Lock()
    defer o.m.Unlock()
    if o.done.Load() == 0 {
        defer o.done.Store(1)
        f()
    }
}
```

### OnceValue / OnceFunc（Go 1.21+）

```go
// 返回值的 Once
config := sync.OnceValue(func() *Config {
    return loadConfig("config.yaml")
})
cfg := config()  // 首次调用加载，后续直接返回

// 函数形式的 Once
init := sync.OnceFunc(func() {
    fmt.Println("initialized")
})
init()  // 第一次执行
init()  // 不执行
```

---

## 四、Pool（对象池）

### 基本用法

```go
var bufPool = sync.Pool{
    New: func() interface{} {
        return new(bytes.Buffer)
    },
}

func process(data []byte) string {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()  // 重要：清空
        bufPool.Put(buf)
    }()

    buf.Write(data)
    return buf.String()
}
```

### 适用场景

1. **频繁分配/释放的对象**：bytes.Buffer / 连接 / 大对象
2. **GC 压力优化**：减少堆分配
3. **临时对象复用**：避免重复初始化

### 注意事项

```go
// ❌ 错：不清空
defer bufPool.Put(buf)

// ✅ 对：先 Reset 再 Put
defer func() {
    buf.Reset()
    bufPool.Put(buf)
}()
```

### Pool vs sync.Pool vs typed pool

```go
// 标准 sync.Pool（interface{}）
var pool = sync.Pool{New: func() interface{} { return new(Buffer) }}
buf := pool.Get().(*Buffer)  // 需要类型断言

// 泛型版本（社区库）
import "github.com/samber/go-sync"
pool := go_sync.NewPool(func() *Buffer { return new(Buffer) })
buf := pool.Get()  // 无需类型断言
```

---

## 五、Cond（条件变量）

### 基本用法

```go
var (
    mu    sync.Mutex
    cond  = sync.NewCond(&mu)
    ready bool
)

// 等待方
cond.L.Lock()
for !ready {
    cond.Wait()  // 释放锁并等待，唤醒后重新获取锁
}
cond.L.Unlock()

// 通知方
cond.L.Lock()
ready = true
cond.Broadcast()  // 唤醒所有等待者
// cond.Signal()  // 唤醒一个等待者
cond.L.Unlock()
```

### 适用场景

- **生产者-消费者**：buffer 满/空时等待
- **资源就绪**：等待初始化完成

### 实战：限制并发数

```go
type Semaphore struct {
    mu    sync.Mutex
    cond  *sync.Cond
    n     int
    limit int
}

func NewSemaphore(limit int) *Semaphore {
    s := &Semaphore{limit: limit}
    s.cond = sync.NewCond(&s.mu)
    return s
}

func (s *Semaphore) Acquire() {
    s.mu.Lock()
    for s.n >= s.limit {
        s.cond.Wait()
    }
    s.n++
    s.mu.Unlock()
}

func (s *Semaphore) Release() {
    s.mu.Lock()
    s.n--
    s.cond.Broadcast()
    s.mu.Unlock()
}
```

---

## 六、Map（并发安全 Map）

### 基本用法

```go
var m sync.Map

// 写
m.Store("key", "value")

// 读
v, ok := m.Load("key")

// 遍历
m.Range(func(k, v interface{}) bool {
    fmt.Println(k, v)
    return true  // 继续
})
```

### 适用场景

```go
// ✅ 适合：key 集合稳定、读多写少
// ❌ 不适合：高频写入（用 RWMutex + map 性能更好）
```

### sync.Map vs map + Mutex

| 维度 | sync.Map | map + RWMutex |
|---|---|---|
| 读性能 | ⭐⭐⭐⭐⭐（无锁） | ⭐⭐⭐⭐（RLock） |
| 写性能 | ⭐⭐（全局锁） | ⭐⭐⭐⭐（Lock） |
| 类型 | interface{} | 任意 |
| 适用 | 只读多、写少 | 读写均衡 |

### 实战：缓存

```go
type Cache struct {
    m sync.Map
}

func (c *Cache) Get(key string) (interface{}, bool) {
    return c.m.Load(key)
}

func (c *Cache) Set(key string, value interface{}) {
    c.m.Store(key, value)
}

func (c *Cache) GetOrCompute(key string, compute func() interface{}) interface{} {
    if v, ok := c.m.Load(key); ok {
        return v
    }
    v := compute()
    c.m.Store(key, v)
    return v
}
```

---

## 七、atomic（原子操作）

### 基本用法

```go
import "sync/atomic"

var counter int64

// 原子加
atomic.AddInt64(&counter, 1)

// 原子读
v := atomic.LoadInt64(&counter)

// 原子存
atomic.StoreInt64(&counter, 100)

// CAS
old := atomic.LoadInt64(&counter)
new := old + 1
swapped := atomic.CompareAndSwapInt64(&counter, old, new)
```

### atomic.Int64（Go 1.19+）

```go
var counter atomic.Int64

counter.Add(1)
v := counter.Load()
counter.Store(100)

// CAS
old := counter.Load()
new := old + 1
swapped := counter.CompareAndSwap(old, new)
```

### atomic.Value（任意类型）

```go
var config atomic.Value

config.Store(&Config{...})
cfg := config.Load().(*Config)

// 热更新配置
go func() {
    for {
        time.Sleep(1 * time.Minute)
        newCfg := loadConfig()
        config.Store(newCfg)
    }
}()
```

---

## 八、sync vs channel 选择

### 通用原则

| 场景 | 推荐 | 理由 |
|---|---|---|
| 通信 / 数据流 | channel | CSP 哲学 |
| 共享状态 | sync.Mutex | 简单直接 |
| 计数器 | atomic | 性能最佳 |
| 等待一组任务 | sync.WaitGroup | 简洁 |
| 单次初始化 | sync.Once | 线程安全 |
| 对象池 | sync.Pool | 减少 GC |
| 并发安全 map | sync.Map | 避免锁 |
| 复杂状态同步 | Mutex + channel | 组合 |

### 实战对比

```go
// channel 版：worker pool
jobs := make(chan Job, 100)
for w := 0; w < 10; w++ {
    go func() {
        for job := range jobs {
            process(job)
        }
    }()
}

// sync 版：worker pool（用 semaphore）
var wg sync.WaitGroup
sem := make(chan struct{}, 10)
for _, job := range jobs {
    wg.Add(1)
    sem <- struct{}{}
    go func(j Job) {
        defer wg.Done()
        defer func() { <-sem }()
        process(j)
    }(job)
}
wg.Wait()
```

---

## 九、最佳实践

### 1. 减少锁粒度

```go
// ❌ 一个全局锁
var mu sync.Mutex
var data map[string]int

// ✅ 分片锁
type ShardedMap struct {
    shards [16]struct {
        mu sync.RWMutex
        m  map[string]int
    }
}
```

### 2. 用 defer Unlock

```go
// ❌ 容易忘记 Unlock
mu.Lock()
if err := doSomething(); err != nil {
    mu.Unlock()  // 重复代码
    return err
}
mu.Unlock()

// ✅ defer 兜底
mu.Lock()
defer mu.Unlock()
if err := doSomething(); err != nil {
    return err  // defer 会执行
}
```

### 3. 用 atomic 代替 Mutex（简单计数）

```go
// ❌ Mutex 开销大
var (
    mu sync.Mutex
    counter int
)
mu.Lock()
counter++
mu.Unlock()

// ✅ atomic 快 5-10x
var counter atomic.Int64
counter.Add(1)
```

### 4. 避免锁嵌套

```go
// ❌ 死锁风险
func A() {
    mu1.Lock()
    defer mu1.Unlock()
    B()  // B 也加锁 mu2，可能死锁
}

func B() {
    mu2.Lock()
    defer mu2.Unlock()
}

// ✅ 用 channel 或避免嵌套
```

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/goroutine**：goroutine
- **02-concurrency/channel**：channel
- **02-concurrency/context**：context
- **06-advanced/runtime**：GMP 调度器

## 一句话总结

> **sync 包 = 锁 + 信号量 + 池 + 原子**。**channel 处理通信，sync 处理状态**。
""")


add("02-concurrency/context.md", r"""---
title: context 上下文
---

# context 上下文

context 是 Go 并发编程的"瑞士军刀"：取消传播、超时控制、request-scoped 数据传递。

## 一句话总结

> **context = 请求级别的全局状态 + 取消信号传播**。**核心：WithCancel / WithTimeout / WithValue / Done() channel**。

---

## 一、为什么需要 context

### 典型场景

```go
// HTTP 请求 → RPC → DB 查询 → 第三方 API
// 任何一层超时都应该取消后续所有调用
```

```go
// ❌ 没有 context：超时无法传播
func handleRequest(w http.ResponseWriter, r *http.Request) {
    data := rpcCall()                    // 1s
    dbCall(data)                          // 5s
    thirdPartyCall(data)                  // 10s
    // 总耗时 16s，无法中途取消
}

// ✅ 有 context：整链路可取消
func handleRequest(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
    defer cancel()

    data := rpcCallContext(ctx)           // 接收 ctx.Done()
    dbCallContext(ctx, data)              // 接收 ctx.Done()
    thirdPartyCallContext(ctx, data)      // 接收 ctx.Done()
    // 总耗时 ≤ 5s
}
```

---

## 二、context 接口

### 4 个方法

```go
type Context interface {
    Deadline() (deadline time.Time, ok bool)  // 返回截止时间
    Done() <-chan struct{}                     // 返回取消信号 channel
    Err() error                                // 返回取消原因
    Value(key any) any                         // 获取 request-scoped 值
}
```

### 两个实现

```go
// 1. Background：根 context
ctx := context.Background()

// 2. TODO：占位 context（不确定用什么时）
ctx := context.TODO()
```

---

## 三、4 个派生函数

### 1. WithCancel：手动取消

```go
ctx, cancel := context.WithCancel(parent)

// 取消
cancel()

// 在 goroutine 中监听
go func() {
    select {
    case <-ctx.Done():
        fmt.Println("cancelled:", ctx.Err())
        // cleanup
    case <-time.After(5 * time.Second):
        fmt.Println("done")
    }
}()
```

### 2. WithTimeout：超时取消

```go
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()  // 释放资源

// 等价于
deadline := time.Now().Add(5 * time.Second)
ctx, cancel := context.WithDeadline(parent, deadline)
```

### 3. WithDeadline：截止时间

```go
deadline := time.Date(2025, 1, 1, 0, 0, 0, 0, time.UTC)
ctx, cancel := context.WithDeadline(parent, deadline)
defer cancel()
```

### 4. WithValue：传值

```go
type traceIDKey struct{}

ctx := context.WithValue(parent, traceIDKey{}, "abc-123")

// 取值
traceID := ctx.Value(traceIDKey{}).(string)
```

### 取消传播

```
Background (根)
   │
   ├── WithCancel  → cancel1
   │      │
   │      ├── WithTimeout → cancel2 (timeout 触发的 cancel)
   │      │
   │      └── WithValue
   │
   └── WithValue
```

**取消规则**：父 context 取消 → 所有子 context 都取消。

---

## 四、实战模式

### 1. HTTP Server

```go
func handler(w http.ResponseWriter, r *http.Request) {
    // r.Context() 是 server 自动管理的
    ctx := r.Context()

    data, err := fetchDataContext(ctx)
    if err != nil {
        if errors.Is(err, context.DeadlineExceeded) {
            http.Error(w, "timeout", http.StatusGatewayTimeout)
            return
        }
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    fmt.Fprint(w, data)
}

func fetchDataContext(ctx context.Context) (string, error) {
    req, _ := http.NewRequestWithContext(ctx, "GET", "https://api.example.com", nil)
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    // 读 body 也监听 ctx.Done()
    done := make(chan error, 1)
    var data string
    go func() {
        b, _ := io.ReadAll(resp.Body)
        data = string(b)
        done <- nil
    }()

    select {
    case err := <-done:
        return data, err
    case <-ctx.Done():
        return "", ctx.Err()
    }
}
```

### 2. gRPC

```go
// gRPC 自动支持 context
ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()

resp, err := client.GetUser(ctx, &pb.GetUserRequest{Id: "123"})
if err != nil {
    if status.Code(err) == codes.DeadlineExceeded {
        // timeout
    }
    return err
}
```

### 3. Database

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

var users []User
err := db.QueryContext(ctx, "SELECT * FROM users WHERE active = true", &users)
```

### 4. 跨服务链路追踪

```go
// 传递 trace ID
ctx := context.WithValue(parent, traceIDKey{}, "trace-abc-123")

// 在日志中打印
log.Printf("[trace=%s] processing request", ctx.Value(traceIDKey{}))
```

---

## 五、context 规则

### 1. 作为函数第一个参数

```go
// ✅ 标准
func DoSomething(ctx context.Context, arg1 string) error

// ❌ 不标准
func DoSomething(arg1 string, ctx context.Context) error
```

### 2. 不要把 context 放在 struct 字段

```go
// ❌ 错
type Service struct {
    ctx context.Context  // 不要
}

func (s *Service) Do() {}

// ✅ 对：context 作为参数
type Service struct{}

func (s *Service) Do(ctx context.Context) {}
```

**理由**：context 是 request-scoped，不是 service-scoped。

### 3. 不要传 nil context

```go
// ❌ 错：传 nil
DoSomething(nil, "arg")

// ✅ 对：用 Background 或 TODO
DoSomething(context.Background(), "arg")
```

### 4. WithValue 只能传递 request-scoped 数据

```go
// ✅ 对：trace ID / auth token / request ID
ctx := context.WithValue(parent, "traceID", "abc-123")

// ❌ 错：业务参数
ctx := context.WithValue(parent, "userID", "u-123")  // 不应该
```

**应该用参数传递**：
```go
func DoSomething(ctx context.Context, userID string) {}  // 对
```

### 5. defer cancel()

```go
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()  // 必须！避免 context 泄漏
```

---

## 六、context.Value 的最佳实践

### 自定义 key 类型

```go
// 用 struct 类型作为 key（避免冲突）
type traceIDKey struct{}
type userIDKey struct{}

ctx := context.WithValue(parent, traceIDKey{}, "abc-123")
ctx = context.WithValue(ctx, userIDKey{}, "user-456")

// 取值
traceID := ctx.Value(traceIDKey{}).(string)
```

### 不要用 string 类型

```go
// ❌ 错：string key 容易冲突
ctx := context.WithValue(parent, "traceID", "abc")

// ✅ 对：自定义类型
type traceIDKey struct{}
ctx := context.WithValue(parent, traceIDKey{}, "abc")
```

### 封装访问方法

```go
type traceIDKey struct{}

func WithTraceID(ctx context.Context, id string) context.Context {
    return context.WithValue(ctx, traceIDKey{}, id)
}

func TraceID(ctx context.Context) string {
    if id, ok := ctx.Value(traceIDKey{}).(string); ok {
        return id
    }
    return ""
}
```

---

## 七、常见陷阱

### 陷阱 1：忘记 cancel

```go
func leak() {
    ctx, cancel := context.WithCancel(context.Background())
    // 忘记 cancel()，ctx 不会被 GC
}

// 修复
func noLeak() {
    ctx, cancel := context.WithCancel(context.Background())
    defer cancel()  // 必须 defer
}
```

### 陷阱 2：覆盖 ctx 参数

```go
// ❌ 错：覆盖入参
func DoSomething(ctx context.Context) error {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    // ...
}

// ✅ 对：命名区分
func DoSomething(ctx context.Context) error {
    c, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    // 使用 c
}
```

### 陷阱 3：context.Value 类型断言失败

```go
// 不存在
v := ctx.Value("missing").(string)  // panic: interface conversion

// ✅ 修复：用 comma ok
v, ok := ctx.Value("missing").(string)
if !ok {
    return ""
}
```

---

## 八、性能开销

- **传递**：几乎无开销（interface 引用）
- **Done() channel**：每个 ctx 一个 channel（用完后要 cancel 释放）
- **WithValue**：每次都创建新 ctx（链式）

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/goroutine**：goroutine
- **02-concurrency/channel**：channel
- **02-concurrency/patterns**：并发模式

## 一句话总结

> **context = 取消传播 + 超时控制 + request-scoped 值**。**Go 并发的标配**。
""")


add("02-concurrency/patterns.md", r"""---
title: 并发模式实战
---

# 并发模式实战

Go 并发的 7 大实战模式：Worker Pool、Pipeline、Fan-out/Fan-in、Pub-Sub、限流、熔断、分布式协调。

## 一句话总结

> **Go 并发模式 = Worker Pool + Pipeline + Fan-out/Fan-in + errgroup**。**核心：用 channel 通信、用 errgroup 错误传播、用 context 取消**。

---

## 一、Worker Pool（线程池）

### 基础版本

```go
func workerPool(jobs <-chan int, results chan<- int) {
    for j := range jobs {
        results <- processJob(j)
    }
}

func main() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    // 启动 3 个 worker
    for w := 1; w <= 3; w++ {
        go workerPool(jobs, results)
    }

    // 发送 5 个任务
    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)

    // 接收 5 个结果
    for a := 1; a <= 5; a++ {
        <-results
    }
}

func processJob(j int) int {
    time.Sleep(100 * time.Millisecond)
    return j * 2
}
```

### 增强版（errgroup + ctx）

```go
func workerPoolCtx(ctx context.Context, jobs <-chan int) error {
    for j := range jobs {
        select {
        case <-ctx.Done():
            return ctx.Err()
        default:
            if err := processJobCtx(ctx, j); err != nil {
                return err
            }
        }
    }
    return nil
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()

    jobs := make(chan int, 100)
    var g errgroup.Group

    // 启动 5 个 worker
    for w := 1; w <= 5; w++ {
        g.Go(func() error {
            return workerPoolCtx(ctx, jobs)
        })
    }

    // 发送任务
    g.Go(func() error {
        defer close(jobs)
        for j := 1; j <= 100; j++ {
            select {
            case jobs <- j:
            case <-ctx.Done():
                return ctx.Err()
            }
        }
        return nil
    })

    if err := g.Wait(); err != nil {
        log.Fatal(err)
    }
}
```

---

## 二、Pipeline（管道）

### 三阶段管道

```go
// 阶段 1：生成数据
func gen(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// 阶段 2：平方
func sq(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// 阶段 3：求和
func sum(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        total := 0
        for n := range in {
            total += n
        }
        out <- total
    }()
    return out
}

// 组合
func main() {
    // gen(2, 3) → sq → sq → sum
    result := <-sum(sq(sq(gen(2, 3))))
    fmt.Println(result)  // ((2^2)^2 + (3^2)^2) = 16 + 81 = 97
}
```

### 带 ctx 的管道

```go
func genCtx(ctx context.Context, nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            select {
            case out <- n:
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}
```

---

## 三、Fan-out / Fan-in

### Fan-out：分发任务到多个 worker

```go
func distribute(in <-chan Job, workers int) []<-chan Job {
    outs := make([]<-chan Job, workers)
    for i := 0; i < workers; i++ {
        outs[i] = worker(in)
    }
    return outs
}

func worker(in <-chan Job) <-chan Job {
    out := make(chan Job)
    go func() {
        defer close(out)
        for j := range in {
            out <- process(j)
        }
    }()
    return out
}
```

### Fan-in：合并多个 channel

```go
func merge(cs ...<-chan Job) <-chan Job {
    out := make(chan Job)
    var wg sync.WaitGroup

    for _, c := range cs {
        wg.Add(1)
        go func(c <-chan Job) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(c)
    }

    go func() {
        wg.Wait()
        close(out)
    }()

    return out
}
```

### 完整 Fan-out + Fan-in

```go
func main() {
    in := genJobs(100)

    // Fan-out：3 个 worker
    workers := distribute(in, 3)

    // Fan-in：合并结果
    out := merge(workers...)

    for result := range out {
        fmt.Println(result)
    }
}
```

---

## 四、限流模式

### 信号量限流

```go
type Semaphore chan struct{}

func NewSemaphore(n int) Semaphore {
    return make(chan struct{}, n)
}

func (s Semaphore) Acquire() {
    s <- struct{}{}
}

func (s Semaphore) Release() {
    <-s
}

// 使用
sem := NewSemaphore(10)  // 最多 10 并发
for _, item := range items {
    sem.Acquire()
    go func(item Item) {
        defer sem.Release()
        process(item)
    }(item)
}
```

### 令牌桶限流（基于 time/rate）

```go
import "golang.org/x/time/rate"

limiter := rate.NewLimiter(100, 50)  // 100 QPS，桶容量 50

func handler(w http.ResponseWriter, r *http.Request) {
    if !limiter.Allow() {
        http.Error(w, "Too Many Requests", http.StatusTooManyRequests)
        return
    }
    // 处理请求
}
```

### 漏桶限流

```go
import "github.com/uber-go/ratelimit"

rl := ratelimit.New(100)  // 100 QPS

func handler(w http.ResponseWriter, r *http.Request) {
    rl.Take()  // 阻塞直到令牌可用
    // 处理请求
}
```

---

## 五、熔断模式

### sony/gobreaker

```go
import "github.com/sony/gobreaker"

cb := gobreaker.NewCircuitBreaker(gobreaker.Settings{
    Name:        "downstream-service",
    MaxRequests: 3,                // 半开状态最大请求数
    Interval:    60 * time.Second, // 统计周期
    Timeout:     30 * time.Second, // 熔断后恢复时间
    ReadyToTrip: func(counts gobreaker.Counts) bool {
        return counts.ConsecutiveFailures > 5
    },
})

result, err := cb.Execute(func() (interface{}, error) {
    return callDownstream()
})
```

### 手动熔断

```go
type CircuitBreaker struct {
    mu             sync.Mutex
    state          string  // closed / open / half-open
    failureCount   int
    successCount   int
    lastFailureTime time.Time
}

func (cb *CircuitBreaker) Call(fn func() error) error {
    cb.mu.Lock()
    if cb.state == "open" {
        if time.Since(cb.lastFailureTime) > 30*time.Second {
            cb.state = "half-open"
        } else {
            cb.mu.Unlock()
            return errors.New("circuit open")
        }
    }
    cb.mu.Unlock()

    err := fn()
    cb.mu.Lock()
    defer cb.mu.Unlock()

    if err != nil {
        cb.failureCount++
        cb.lastFailureTime = time.Now()
        if cb.failureCount >= 5 {
            cb.state = "open"
        }
        return err
    }

    cb.successCount++
    if cb.state == "half-open" {
        cb.state = "closed"
        cb.failureCount = 0
    }
    return nil
}
```

---

## 六、Pub-Sub（发布订阅）

### 基础实现

```go
type PubSub struct {
    mu       sync.RWMutex
    subs     map[string][]chan Message
}

type Message struct {
    Topic   string
    Payload interface{}
}

func NewPubSub() *PubSub {
    return &PubSub{subs: make(map[string][]chan Message)}
}

func (ps *PubSub) Subscribe(topic string) <-chan Message {
    ch := make(chan Message, 10)
    ps.mu.Lock()
    ps.subs[topic] = append(ps.subs[topic], ch)
    ps.mu.Unlock()
    return ch
}

func (ps *PubSub) Publish(topic string, payload interface{}) {
    ps.mu.RLock()
    defer ps.mu.RUnlock()
    for _, ch := range ps.subs[topic] {
        ch <- Message{Topic: topic, Payload: payload}
    }
}

func (ps *PubSub) Unsubscribe(topic string, ch <-chan Message) {
    ps.mu.Lock()
    defer ps.mu.Unlock()
    subs := ps.subs[topic]
    for i, c := range subs {
        if c == ch {
            ps.subs[topic] = append(subs[:i], subs[i+1:]...)
            close(c)
            return
        }
    }
}
```

### 使用

```go
ps := NewPubSub()

sub := ps.Subscribe("user.created")
go func() {
    for msg := range sub {
        fmt.Println("received:", msg.Payload)
    }
}()

ps.Publish("user.created", "alice")
```

---

## 七、errgroup 模式

### 并行 + 错误聚合

```go
import "golang.org/x/sync/errgroup"

func main() {
    var g errgroup.Group

    urls := []string{
        "https://api1.example.com",
        "https://api2.example.com",
        "https://api3.example.com",
    }

    for _, url := range urls {
        url := url
        g.Go(func() error {
            resp, err := http.Get(url)
            if err != nil {
                return fmt.Errorf("get %s: %w", url, err)
            }
            defer resp.Body.Close()
            // 处理响应
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        log.Fatal(err)  // 第一个错误
    }
}
```

### errgroup.WithContext：第一个错误取消其他

```go
g, ctx := errgroup.WithContext(context.Background())

for _, url := range urls {
    g.Go(func() error {
        req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
        resp, err := http.DefaultClient.Do(req)
        if err != nil {
            return err
        }
        defer resp.Body.Close()
        // 处理响应
        return nil
    })
}

if err := g.Wait(); err != nil {
    log.Fatal(err)
}
```

### errgroup.SetLimit：限制并发数

```go
g := errgroup.Group{}
g.SetLimit(10)  // 最多 10 个并发

for _, url := range urls {
    url := url
    g.Go(func() error {
        // 自动等待直到 < 10 并发
        resp, err := http.Get(url)
        // ...
        return nil
    })
}
```

---

## 八、Map-Reduce 模式

### 经典 MapReduce

```go
// Map：每个 goroutine 处理一个分片
func mapShards[T, U any](items []T, mapper func(T) U, workers int) []U {
    shardSize := (len(items) + workers - 1) / workers
    results := make([][]U, workers)
    var wg sync.WaitGroup

    for w := 0; w < workers; w++ {
        wg.Add(1)
        start, end := w*shardSize, (w+1)*shardSize
        if end > len(items) {
            end = len(items)
        }
        go func(shard []T, idx int) {
            defer wg.Done()
            for _, item := range shard {
                results[idx] = append(results[idx], mapper(item))
            }
        }(items[start:end], w)
    }

    wg.Wait()

    // Flatten
    var out []U
    for _, r := range results {
        out = append(out, r...)
    }
    return out
}

// Reduce
func reduce[T any](items []T, initial T, reducer func(T, T) T) T {
    result := initial
    for _, item := range items {
        result = reducer(result, item)
    }
    return result
}

// 使用
sum := reduce(mapShards(nums, func(n int) int { return n * n }, 4), 0, func(a, b int) int { return a + b })
```

---

## 九、超时模式

### 单层超时

```go
ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()

result, err := rpcCall(ctx)
if errors.Is(err, context.DeadlineExceeded) {
    // timeout
}
```

### 多层超时（递增）

```go
// 顶层 HTTP handler：30s
ctx1, cancel1 := context.WithTimeout(r.Context(), 30*time.Second)
defer cancel1()

// RPC 调用：10s
ctx2, cancel2 := context.WithTimeout(ctx1, 10*time.Second)
defer cancel2()

// DB 查询：3s
ctx3, cancel3 := context.WithTimeout(ctx2, 3*time.Second)
defer cancel3()

db.QueryContext(ctx3, ...)
```

### 整体超时 + 阶段超时

```go
ctx, cancel := context.WithTimeout(r.Context(), 30*time.Second)
defer cancel()

// 阶段 1：5s
ctx1, cancel1 := context.WithTimeout(ctx, 5*time.Second)
defer cancel1()
stage1(ctx1)

// 阶段 2：剩余 25s
ctx2, cancel2 := context.WithTimeout(ctx, time.Until(deadline)-5*time.Second)
defer cancel2()
stage2(ctx2)
```

---

## 十、Graceful Shutdown 模式

```go
func main() {
    ctx, cancel := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer cancel()

    srv := &http.Server{Addr: ":8080"}

    // 启动服务
    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            log.Fatal(err)
        }
    }()

    // 等待信号
    <-ctx.Done()
    log.Println("Shutting down...")

    // 30s 内优雅退出
    shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
    defer cancel()

    if err := srv.Shutdown(shutdownCtx); err != nil {
        log.Printf("Server forced to shutdown: %v", err)
    }

    log.Println("Server exited")
}
```

---

## 关联章节

- **02-concurrency/overview**：CSP 总览
- **02-concurrency/goroutine**：goroutine
- **02-concurrency/channel**：channel
- **02-concurrency/sync-package**：sync 包
- **02-concurrency/context**：context

## 一句话总结

> **Go 并发模式 = Worker Pool + Pipeline + Fan-out + errgroup + 限流熔断**。**实战模板可直接复用**。
""")


# === 03-ecosystem ===

add("03-ecosystem/go-toolchain.md", r"""---
title: Go 工具链
---

# Go 工具链

Go 的杀手锏：**官方工具链**——格式化、依赖管理、测试、构建一条龙。

## 一句话总结

> **Go 工具链 = gofmt + go vet + go mod + go test + go build + 交叉编译**。**没有第三方包管理器战争，go mod 一统天下**。

---

## 一、gofmt — 官方格式化

```bash
# 格式化单个文件
gofmt main.go

# 整个项目格式化
gofmt -w .

# 检查但不改（CI 用）
gofmt -l .

# 简化代码
gofmt -s -w .
```

**理念**：代码风格不应有争议，gofmt 让所有 Go 代码看起来一样。所有 IDE 集成 gofmt on save。

## 二、go vet — 静态检查

```bash
# 检查代码
go vet ./...

# 常见捕获错误
# - Printf format string 不匹配
# - 锁拷贝
# - range 循环变量地址
# - 错误的 mutex 用法
```

集成到 CI：`go vet ./... && echo "ok"`

## 三、go mod — 依赖管理

```bash
# 初始化模块
go mod init github.com/user/repo

# 添加依赖
go get github.com/gin-gonic/gin@latest
go get github.com/gin-gonic/gin@v1.9.0  # 指定版本

# 整理依赖（删除未使用 + 补全缺失）
go mod tidy

# 验证依赖完整性
go mod verify

# 下载到本地
go mod download

# 替换依赖（monorepo 调试用）
# go.mod
replace github.com/old/pkg => ../local-pkg
```

**go.mod 结构**：
```
module github.com/user/repo

go 1.22

require (
    github.com/gin-gonic/gin v1.9.0
    github.com/spf13/viper v1.16.0
)

require (
    // indirect dependencies
    github.com/xxx v1.0.0 // indirect
)
```

**go.sum**：所有依赖的 hash，确保不可篡改。

## 四、go test — 测试

```bash
# 运行所有测试
go test ./...

# 详细输出
go test -v ./...

# 跑特定测试
go test -run TestAdd ./...

# 覆盖率
go test -cover ./...
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out  # 浏览器看

# race detector（数据竞争）
go test -race ./...

# 基准测试
go test -bench=. -benchmem
```

## 五、go build — 构建

```bash
# 当前平台
go build -o myapp .

# 交叉编译（Go 杀手特性）
GOOS=linux GOARCH=amd64 go build -o myapp-linux .
GOOS=darwin GOARCH=arm64 go build -o myapp-mac-m1 .
GOOS=windows GOARCH=amd64 go build -o myapp.exe .

# 减少二进制大小
go build -ldflags="-s -w" -o myapp .
# -s 去掉符号表
# -w 去掉调试信息
# 通常可减 30%
```

**支持的目标平台**（`go tool dist list`）：
- linux/amd64, linux/arm64
- darwin/amd64, darwin/arm64
- windows/amd64, windows/arm64
- freebsd/amd64
- 等等 30+ 平台

## 六、go run — 运行

```bash
# 运行 main 包
go run main.go

# 整个目录
go run .

# 带参数
go run main.go --port 8080
```

## 七、go install — 安装

```bash
# 安装二进制到 $GOPATH/bin
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest

# 安装当前项目
go install .
```

## 八、go env — 环境变量

```bash
go env GOROOT          # Go 安装路径
go env GOPATH          # 工作目录（~/go）
go env GOMODCACHE      # 模块缓存（~/go/pkg/mod）
go env GOOS GOARCH     # 当前平台
go env GOPROXY         # 模块代理（默认 proxy.golang.org）
go env GOSUMDB         # 校验和数据库

# 关键环境变量
GOPROXY=https://goproxy.cn,direct  # 中国镜像
GO111MODULE=on
CGO_ENABLED=0                       # 禁用 CGO（静态二进制）
GOPRIVATE=github.com/myorg/*        # 私有仓库不走代理
```

## 九、其他实用命令

```bash
go doc fmt.Println          # 查文档
go doc -all net/http        # 包所有文档
godoc -http=:6060           # 启本地文档服务器

go version
go env
go clean -cache             # 清理构建缓存
go clean -modcache          # 清理模块缓存

# pprof 命令行
go tool pprof cpu.prof
go tool pprof mem.prof
go tool pprof http://localhost:6060/debug/pprof/heap
```

## 十、Makefile / Taskfile

**Go 项目标配 Makefile**：

```makefile
.PHONY: build test lint run

build:
	go build -o bin/myapp .

test:
	go test -race -coverprofile=coverage.out ./...

lint:
	golangci-lint run ./...

run:
	go run .

clean:
	rm -rf bin/ coverage.out

deps:
	go mod tidy
	go mod verify
```

**Taskfile.yml**（更现代的替代）：
```yaml
version: '3'
tasks:
  build:
    cmds: [go build -o bin/myapp .]
  test:
    cmds: [go test -race -coverprofile=coverage.out ./...]
  lint:
    cmds: [golangci-lint run]
```

## 关联章节

- **03-ecosystem/standard-library**：标准库
- **03-ecosystem/testing**：测试与覆盖率
- **03-ecosystem/benchmark**：性能基准

## 一句话总结

> **Go 工具链 = 一站式开发体验**。**无需 Maven/Gradle/npm/yarn 的选择焦虑，go 命令全包**。
""")


add("03-ecosystem/standard-library.md", r"""---
title: 标准库
---

# Go 标准库

**Go 标准库是 Go 最大的优势**——`net/http` `encoding/json` `sync` `context` `database/sql` 全部开箱即用，无需 Spring/Hibernate/Express 这样的重量级框架。

## 一句话总结

> **Go 标准库 ≈ Java 17 + Spring Boot 核心 + Jackson + Guava 一半**。**`net/http` 起步就能写生产级 Web 服务**。

---

## 一、必学标准包 TOP 20

| 包 | 作用 | 关键 API |
|---|---|---|
| `fmt` | 格式化 I/O | `Printf`, `Sprintf`, `Errorf` |
| `errors` | 错误处理 | `New`, `Is`, `As`, `Join` (Go 1.20+) |
| `context` | 上下文/超时/取消 | `Background`, `WithCancel`, `WithTimeout` |
| `sync` | 同步原语 | `Mutex`, `WaitGroup`, `Once`, `Pool` |
| `sync/atomic` | 原子操作 | `AddInt64`, `LoadPointer`, `CAS` |
| `time` | 时间/定时器 | `Now`, `After`, `Ticker`, `Tick` |
| `io` | I/O 抽象 | `Reader`, `Writer`, `Copy`, `MultiWriter` |
| `os` | 操作系统 | `Open`, `Create`, `Getenv`, `Args` |
| `path/filepath` | 路径 | `Join`, `Base`, `Dir`, `Walk` |
| `encoding/json` | JSON | `Marshal`, `Unmarshal`, `Decoder` |
| `net/http` | HTTP 客户端/服务端 | `Get`, `Post`, `ListenAndServe`, `Handler` |
| `net/url` | URL 解析 | `Parse`, `Values`, `QueryEscape` |
| `strings` | 字符串 | `Split`, `Join`, `Contains`, `Builder` |
| `strconv` | 类型转换 | `Itoa`, `Atoi`, `FormatFloat`, `ParseBool` |
| `sort` | 排序 | `Slice`, `SliceStable`, `Strings` |
| `container/list` | 双向链表 | `PushBack`, `Remove` |
| `container/heap` | 堆 | `Push`, `Pop`, `Init` |
| `bufio` | 缓冲 I/O | `NewReader`, `NewWriter`, `Scanner` |
| `log` / `log/slog` | 日志 | `Println`, `Default`, `slog.Info` (Go 1.21+) |
| `reflect` | 反射 | `TypeOf`, `ValueOf`, `DeepEqual` |
| `database/sql` | SQL 抽象 | `Open`, `Query`, `Exec`, `Scan` |
| `crypto/*` | 加密 | `sha256`, `hmac`, `rsa`, `tls` |
| `encoding/*` | 编码 | `gob`, `base64`, `hex`, `csv`, `xml` |
| `runtime` | runtime 控制 | `GOMAXPROCS`, `NumGoroutine`, `GC` |
| `testing` | 测试 | `T`, `B`, `M`, `Run` |

## 二、`net/http` — Web 服务核心

**Hello World Web 服务**：

```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
    })
    http.ListenAndServe(":8080", nil)
}
```

**生产级 server**（自定义 mux + 中间件）：

```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        next.ServeHTTP(w, r)
        log.Printf("%s %s %v", r.Method, r.URL.Path, time.Since(start))
    })
}

func main() {
    mux := http.NewServeMux()
    mux.HandleFunc("GET /users/{id}", getUser)
    mux.HandleFunc("POST /users", createUser)

    srv := &http.Server{
        Addr:         ":8080",
        Handler:      loggingMiddleware(mux),
        ReadTimeout:  5 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  120 * time.Second,
    }
    log.Fatal(srv.ListenAndServe())
}
```

**Go 1.22+ 路由增强**：
- `GET /users/{id}`：方法+路径模式
- `{id}` 占位符
- `r.PathValue("id")` 拿值

**HTTP 客户端**：

```go
resp, err := http.Get("https://api.github.com/users/octocat")
if err != nil { return err }
defer resp.Body.Close()

body, _ := io.ReadAll(resp.Body)
fmt.Println(string(body))

// POST JSON
data, _ := json.Marshal(payload)
resp, err := http.Post(url, "application/json", bytes.NewReader(data))

// 自定义 Client（推荐）
client := &http.Client{Timeout: 10 * time.Second}
req, _ := http.NewRequest("GET", url, nil)
req.Header.Set("Authorization", "Bearer "+token)
resp, err := client.Do(req)
```

## 三、`encoding/json` — 序列化

```go
type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email,omitempty"`  // 零值跳过
}

// 编码
u := User{ID: 1, Name: "Alice", Email: "alice@example.com"}
data, _ := json.Marshal(u)
// {"id":1,"name":"Alice","email":"alice@example.com"}

// 美化输出
data, _ := json.MarshalIndent(u, "", "  ")

// 解码
var u2 User
json.Unmarshal(data, &u2)

// 流式编码（适合大对象）
enc := json.NewEncoder(w)
enc.Encode(u)

// 流式解码（HTTP 处理器里常用）
dec := json.NewDecoder(r.Body)
var u User
dec.Decode(&u)
```

**性能技巧**：
- `jsoniter` / `easyjson` 比标准库快 2-5 倍
- `[]byte` 而非 `string` 减少拷贝
- `json.Decoder` 流式避免整段加载

## 四、`context` — 上下文/取消

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

// 传给下游
result, err := db.QueryContext(ctx, "SELECT ...")

// goroutine 监听
go func() {
    select {
    case <-ctx.Done():
        return  // 取消
    case <-time.After(3 * time.Second):
        fmt.Println("done")
    }
}()

// 传值
ctx = context.WithValue(ctx, userIDKey, 42)
uid := ctx.Value(userIDKey).(int)
```

**规则**：ctx 是请求作用域的第一个参数，跨 API 边界传递。

## 五、`sync` — 并发原语

```go
// Mutex
var mu sync.Mutex
mu.Lock()
defer mu.Unlock()

// RWMutex（读多写少）
var rwmu sync.RWMutex
rwmu.RLock()  // 多个读
rwmu.Lock()   // 排他写

// WaitGroup
var wg sync.WaitGroup
for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(i int) {
        defer wg.Done()
        // work
    }(i)
}
wg.Wait()

// Once（单例）
var once sync.Once
var instance *Singleton
once.Do(func() { instance = &Singleton{} })

// Pool（对象池）
var bufPool = sync.Pool{
    New: func() any { return new(bytes.Buffer) },
}
buf := bufPool.Get().(*bytes.Buffer)
defer bufPool.Put(buf)
```

## 六、`log/slog` — 结构化日志（Go 1.21+）

```go
import "log/slog"

logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
slog.SetDefault(logger)

slog.Info("user login", "user_id", 42, "ip", r.RemoteAddr)
slog.Error("db error", "err", err, "query", query)
slog.Warn("rate limit", "limit", 100, "user", uid)

// 输出
// {"time":"2026-08-09T22:00:00Z","level":"INFO","msg":"user login","user_id":42}
```

**vs logrus/zap**：slog 是官方标准，无第三方依赖。

## 七、database/sql — 数据库抽象

```go
import "database/sql"
import _ "github.com/go-sql-driver/mysql"  // 注册驱动

db, err := sql.Open("mysql", "user:pass@tcp(localhost:3306)/dbname")
defer db.Close()

// 连接池配置
db.SetMaxOpenConns(25)
db.SetMaxIdleConns(5)
db.SetConnMaxLifetime(5 * time.Minute)

// 查询
rows, err := db.Query("SELECT id, name FROM users WHERE age > ?", 18)
defer rows.Close()
for rows.Next() {
    var id int
    var name string
    rows.Scan(&id, &name)
}

// 单行
var name string
db.QueryRow("SELECT name FROM users WHERE id = ?", 1).Scan(&name)

// 事务
tx, _ := db.Begin()
tx.Exec("UPDATE ...")
tx.Commit()  // 或 tx.Rollback()
```

**注意**：`database/sql` 偏底层，常用 `sqlx` / `gorm` 增强。

## 八、crypto — 加密

```go
import (
    "crypto/sha256"
    "crypto/hmac"
    "crypto/rand"
    "crypto/rsa"
    "crypto/tls"
)

h := sha256.Sum256([]byte("hello"))
fmt.Printf("%x", h)

// HMAC
mac := hmac.New(sha256.New, []byte("secret"))
mac.Write([]byte("message"))
expectedMAC := mac.Sum(nil)

// RSA
priv, _ := rsa.GenerateKey(rand.Reader, 2048)
ciphertext, _ := rsa.EncryptOAEP(sha256.New(), rand.Reader, &priv.PublicKey, []byte("secret"), nil)
```

## 九、`testing` — 测试

见 03-ecosystem/testing 章节。

## 十、`runtime` — runtime 控制

```go
import "runtime"

runtime.GOMAXPROCS(8)  // P 数量（默认 = CPU 核数）
runtime.GC()            // 强制 GC
runtime.Gosched()       // 让出 CPU

var m runtime.MemStats
runtime.ReadMemStats(&m)
fmt.Printf("Alloc=%d MB\n", m.Alloc/1024/1024)
fmt.Printf("NumGoroutine=%d\n", runtime.NumGoroutine())
```

## 关联章节

- **03-ecosystem/go-toolchain**：工具链
- **03-ecosystem/testing**：测试
- **06-advanced/runtime**：GMP 调度
- **06-advanced/reflection**：反射

## 一句话总结

> **Go 标准库 = Production-Ready 工具集**。**`net/http` + `database/sql` + `encoding/json` 三件套能写出 90% 的服务**。
""")


add("03-ecosystem/testing.md", r"""---
title: 测试与覆盖率
---

# Go 测试与覆盖率

**Go 测试哲学**：简单、明确、无需第三方库。

## 一句话总结

> **Go 测试 = table-driven + testify 断言 + mockgen + race detector + go-carries**。**核心：测试金字塔 + race 必跑 + 覆盖率 80%+**。

---

## 一、testing 包基础

**测试文件命名**：`xxx_test.go`，同包或 `_test` 包（黑盒测试）。

**基本结构**：

```go
// user.go
package user

func Add(a, b int) int { return a + b }

// user_test.go
package user

import "testing"

func TestAdd(t *testing.T) {
    got := Add(1, 2)
    if got != 3 {
        t.Errorf("Add(1, 2) = %d, want 3", got)
    }
}
```

**运行**：
```bash
go test ./...               # 跑全部
go test -v ./...            # 详细
go test -run TestAdd ./...  # 跑指定
go test -short ./...        # 跳过长测试
```

## 二、Table-Driven Test（Go 惯用法）

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        name string
        a, b int
        want int
    }{
        {"positive", 1, 2, 3},
        {"negative", -1, -2, -3},
        {"zero", 0, 0, 0},
        {"mixed", -1, 1, 0},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := Add(tt.a, tt.b); got != tt.want {
                t.Errorf("Add(%d, %d) = %d, want %d", tt.a, tt.b, got, tt.want)
            }
        })
    }
}
```

**优势**：新增 case 加一行，结构清晰。

## 三、子测试与子基准

```go
func TestUser(t *testing.T) {
    t.Run("Create", func(t *testing.T) { /* ... */ })
    t.Run("Update", func(t *testing.T) { /* ... */ })
    t.Run("Delete", func(t *testing.T) { /* ... */ })
}

// go test -v -run TestUser/Create
```

## 四、Testify — 第三方断言库

**安装**：`go get github.com/stretchr/testify`

```go
import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestUser(t *testing.T) {
    u := &User{ID: 1, Name: "Alice"}
    
    // assert：失败继续
    assert.Equal(t, 1, u.ID)
    assert.NotNil(t, u)
    assert.Contains(t, u.Name, "Ali")
    
    // require：失败终止
    require.NoError(t, err)
    require.NotEmpty(t, u.Name)
    
    // mock
    mockObj := new(MockDB)
    mockObj.On("Get", 1).Return(u, nil)
    
    // suite
    suite.Run(t, new(UserSuite))
}
```

**为什么用 testify**：比 `t.Errorf` 写更少，错误信息更好。

## 五、Mock — 接口模拟

**手写 mock**：

```go
type DB interface {
    Get(id int) (*User, error)
}

type MockDB struct {
    users map[int]*User
}

func (m *MockDB) Get(id int) (*User, error) {
    u, ok := m.users[id]
    if !ok {
        return nil, errors.New("not found")
    }
    return u, nil
}
```

**go:generate + mockgen**（推荐）：

```go
//go:generate mockgen -source=user.go -destination=mock_user.go -package=user

// user.go
type DB interface {
    Get(id int) (*User, error)
}
```

```bash
go generate ./...
```

生成 `mock_user.go`：
```go
func (m *MockDB) Get(id int) (*User, error) {
    ret := m.Called(id)
    return ret.Get(0).(*User), ret.Error(1)
}

// 用
mockDB := new(MockDB)
mockDB.On("Get", 1).Return(&User{ID: 1}, nil)
```

## 六、覆盖率

```bash
# 函数覆盖率
go test -cover ./...

# 详细覆盖率
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out   # 每函数覆盖率
go tool cover -html=coverage.out   # 浏览器看（红/绿色）

# 集成到 CI
go test -coverprofile=coverage.out -covermode=atomic ./...
# 设定最低门槛
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | awk '/total:/ {print $3}' | sed 's/%//' | \
  awk '{if ($1 < 80) exit 1}'
```

**指标**：
- 行覆盖（默认）
- 分支覆盖（`-covermode=count`）
- 推荐 80% 起步，关键路径 100%

## 七、Race Detector

**必跑**：

```bash
go test -race ./...
```

检测数据竞争（同一变量被多 goroutine 无同步读写）。**生产代码提交前必跑**。

**示例**：
```go
func TestRace(t *testing.T) {
    var counter int
    var wg sync.WaitGroup
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter++  // race!
        }()
    }
    wg.Wait()
}
// go test -race 会报警
```

## 八、Fuzzing（Go 1.18+）

```go
func FuzzReverse(f *testing.F) {
    testcases := []string{"Hello", "世界", " "}
    for _, tc := range testcases {
        f.Add(tc)
    }
    f.Fuzz(func(t *testing.T, s string) {
        rev := Reverse(s)
        if Reverse(rev) != s {
            t.Errorf("Reverse(Reverse(%q)) = %q, want %q", s, rev, s)
        }
    })
}

// go test -fuzz=FuzzReverse
```

自动找崩溃输入，是 Go 测试的杀手特性之一。

## 九、HTTP Handler 测试

```go
func TestUserHandler(t *testing.T) {
    req := httptest.NewRequest("GET", "/users/1", nil)
    w := httptest.NewRecorder()
    
    handler := UserHandler{db: &MockDB{}}
    handler.ServeHTTP(w, req)
    
    assert.Equal(t, 200, w.Code)
    assert.Contains(t, w.Body.String(), "Alice")
}

// 启动测试 server
ts := httptest.NewServer(handler)
defer ts.Close()
resp, _ := http.Get(ts.URL + "/users/1")
```

## 十、Test Main — 全局 setup/teardown

```go
func TestMain(m *testing.M) {
    setup()      // 全局初始化
    code := m.Run()  // 跑测试
    teardown()   // 清理
    os.Exit(code)
}
```

## 十一、Example Test — 文档化测试

```go
func ExampleAdd() {
    fmt.Println(Add(1, 2))
    // Output: 3
}
```

**作用**：example 同时是文档和测试，`go test` 验证输出。

## 十二、CI 集成

**GitHub Actions**：

```yaml
name: test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: go test -race -coverprofile=coverage.out ./...
      - run: go vet ./...
      - run: go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
      - run: golangci-lint run
      - uses: codecov/codecov-action@v3
```

## 关联章节

- **03-ecosystem/standard-library**：testing 是标准库
- **03-ecosystem/benchmark**：基准测试
- **03-ecosystem/go-toolchain**：go test / go vet

## 一句话总结

> **Go 测试 = table-driven + testify + mock + race + 80% 覆盖率**。**无第三方框架，go test 够用**。
""")


add("03-ecosystem/benchmark.md", r"""---
title: 性能基准与 pprof
---

# Go 性能基准与 pprof

**Go 的性能分析是其他语言望尘莫及的**——`pprof` + `trace` + `benchstat` 三大武器。

## 一句话总结

> **Go 性能 = benchmark + pprof CPU/Heap/Goroutine + trace 时序图 + benchstat 对比**。**10 行代码接入，定位慢在哪儿**。

---

## 一、Benchmark 基础

**测试函数命名**：`BenchmarkXxx(b *testing.B)`

```go
// 简单基准
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}

// table-driven
func BenchmarkAdd_TableDriven(b *testing.B) {
    cases := []struct{ name string; a, b int }{
        {"small", 1, 2},
        {"large", 1 << 30, 1 << 30},
    }
    for _, c := range cases {
        b.Run(c.name, func(b *testing.B) {
            for i := 0; i < b.N; i++ {
                Add(c.a, c.b)
            }
        })
    }
}
```

**运行**：
```bash
go test -bench=.                              # 全部
go test -bench=BenchmarkAdd -benchmem         # 内存分配
go test -bench=. -benchtime=10s               # 跑 10 秒
go test -bench=. -count=5                     # 跑 5 次（统计）
go test -bench=. -cpu=1,2,4,8                 # 不同 GOMAXPROCS
```

**输出**：
```
BenchmarkAdd-8    1000000000    0.254 ns/op    0 B/op    0 allocs/op
```
- `-8`：8 核
- `1000000000`：b.N
- `0.254 ns/op`：每次耗时
- `0 B/op`：每次分配字节
- `0 allocs/op`：每次分配次数

## 二、benchstat — 对比基准

```bash
go install golang.org/x/perf/cmd/benchstat@latest

# 跑两次保存结果
go test -bench=. -count=10 > old.txt
# 改代码...
go test -bench=. -count=10 > new.txt

# 对比
benchstat old.txt new.txt
```

**输出**：
```
name      old time/op  new time/op  delta
Add-8     0.30ns ± 2%  0.25ns ± 1%  -16.67%  (p=0.000 n=10+10)
```

带置信区间，p-value，**科学对比**。

## 三、Reset / Stop / RunParallel

```go
func BenchmarkComplex(b *testing.B) {
    // 一次性 setup（不算入 b.N）
    expensiveSetup()
    b.ResetTimer()
    
    for i := 0; i < b.N; i++ {
        Complex()
    }
}

// 并行基准
func BenchmarkParallel(b *testing.B) {
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            Complex()
        }
    })
}
```

## 四、pprof 五大类型

```go
import "runtime/pprof"

// 1. CPU profile
f, _ := os.Create("cpu.prof")
pprof.StartCPUProfile(f)
defer pprof.StopCPUProfile()
// 跑被测代码

// 2. Heap profile（内存）
f, _ := os.Create("heap.prof")
pprof.WriteHeapProfile(f)

// 3. Goroutine profile
pprof.Lookup("goroutine").WriteTo(f, 0)

// 4. Block profile（阻塞）
runtime.SetBlockProfileRate(1)
pprof.Lookup("block").WriteTo(f, 0)

// 5. Mutex profile
runtime.SetMutexProfileFraction(1)
pprof.Lookup("mutex").WriteTo(f, 0)
```

**生产级 pprof — 暴露 HTTP 端点**：

```go
import "net/http/pprof"

func main() {
    go func() {
        http.ListenAndServe("localhost:6060", nil)  // pprof 端点
    }()
    // 业务代码...
}
```

**访问**：
- `http://localhost:6060/debug/pprof/` — 浏览器看索引
- `http://localhost:6060/debug/pprof/profile?seconds=30` — 30s CPU profile
- `http://localhost:6060/debug/pprof/heap` — 堆 profile
- `http://localhost:6060/debug/pprof/goroutine` — goroutine profile
- `http://localhost:6060/debug/pprof/trace?seconds=5` — execution trace

**生产环境**注意加鉴权！

## 五、go tool pprof 分析

```bash
# 交互式
go tool pprof cpu.prof
(pprof) top 10          # CPU 占用 top 10
(pprof) list Add        # 看 Add 函数源码级火焰
(pprof) web             # 生成 .svg 浏览器看
(pprof) peek Add        # 看调用链
(pprof) traces          # 看调用 trace

# 直接给 URL（实时采样）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30
```

**火焰图**：
```bash
# 安装 FlameGraph
go install github.com/uber/go-torch@latest
go-torch -seconds 30 http://localhost:6060/debug/pprof/profile

# 或用 pprof 自带
go tool pprof -http=:8080 cpu.prof
# 浏览器打开 http://localhost:8080 看交互式火焰图
```

## 六、Execution Trace

**最强大工具**，看 goroutine 调度、GC、系统调用、阻塞：

```go
import "runtime/trace"

f, _ := os.Create("trace.out")
trace.Start(f)
defer trace.Stop()
// 跑被测代码
```

```bash
go tool trace trace.out
# 浏览器打开，5 个 tab：
# - View trace：时序图
# - Goroutine analysis
# - Network blocking profile
# - Synchronization blocking profile
# - Syscall blocking profile
```

**解决**：goroutine 阻塞、调度延迟、GC 停顿。

## 七、逃逸分析

**关键问题**：变量分配在栈还是堆？

```bash
go build -gcflags='-m' main.go
# 输出：moved to heap: x
```

**判定**：
- 返回局部变量指针 → 逃逸到堆
- 闭包引用 → 逃逸
- 切片/map 大小未知 → 逃逸
- interface{} 装箱 → 逃逸

**优化**：
- 避免大结构体传值（用指针）
- sync.Pool 重用对象
- 预分配 slice/map：`make([]T, 0, 100)`

## 八、内存优化技巧

```go
// ❌ 低效：每次 append 可能重新分配
var s []int
for i := 0; i < 1000; i++ {
    s = append(s, i)
}

// ✅ 高效：预分配
s := make([]int, 0, 1000)
for i := 0; i < 1000; i++ {
    s = append(s, i)
}

// ❌ strings.Builder 低效
var s string
for _, v := range values {
    s += strconv.Itoa(v)  // 每次新建 string
}

// ✅ strings.Builder 高效
var b strings.Builder
b.Grow(1000)  // 预分配
for _, v := range values {
    b.WriteString(strconv.Itoa(v))
}
s := b.String()
```

## 九、常见性能陷阱

1. **defer 性能**：在热循环里 defer 有开销（虽然已经优化到 ~35ns）
2. **interface{} 装箱**：用泛型（Go 1.18+）替代
3. **map[string]X 取不到值**：两次 hash + 内存分配，用 sync.Map / map[uint64]X
4. **string/[]byte 转换**：用 unsafe 避免拷贝（`*(*string)(unsafe.Pointer(&b))`）
5. **GC 压力**：高频对象用 sync.Pool
6. **过多 goroutine**：worker pool 控制并发数
7. **同步锁竞争**：用 atomic 或 channel 替代

## 十、真实案例

**案例：JSON 序列化慢**：
```go
// 优化前：json.Marshal 5ms/op
// 优化方案：
// 1. jsoniter：2ms/op
// 2. easyjson：0.5ms/op（代码生成）
// 3. protobuf：0.1ms/op（跨服务推荐）
```

**案例：字符串拼接慢**：
```go
// 优化前：+= 50ms/op
// 优化后：strings.Builder 5ms/op（10x）
```

## 关联章节

- **03-ecosystem/testing**：单元测试
- **06-advanced/pprof**：runtime pprof 详解
- **06-advanced/runtime**：GMP 调度
- **06-advanced/gc**：GC 调优

## 一句话总结

> **Go 性能 = benchmark + pprof + trace + 逃逸分析**。**内置工具链够用，无需 async-profiler / YourKit**。
""")


# === 04-cloud-native ===

add("04-cloud-native/docker-internals.md", r"""---
title: Docker 源码导读
---

# Docker 源码导读

**Docker 80% Go 写**——理解 Docker = 理解 Go 在系统编程中的应用。

## 一句话总结

> **Docker = containerd + runc + daemon + CLI**。**Go 优势：静态二进制 + goroutine 高并发 + 跨平台编译**。

---

## 一、Docker 架构全景

```
┌─────────────────┐
│  docker CLI     │  ← 用户输入
└────────┬────────┘
         │ REST API
         ▼
┌─────────────────┐
│  dockerd daemon │  ← 后台进程
└────────┬────────┘
         │ gRPC
         ▼
┌─────────────────┐
│  containerd     │  ← 容器 runtime 抽象
└────────┬────────┘
         │ OCI spec
         ▼
┌─────────────────┐
│  runc           │  ← 实际 namespace/cgroup 操作
└─────────────────┘
```

**Docker 现在是上层**，底层是 containerd + runc，都是 Go 写。

## 二、源码结构

```bash
git clone https://github.com/moby/moby
cd moby
ls cmd/          # CLI / daemon 入口
ls daemon/       # 后台逻辑
ls api/          # REST API
ls container/    # 容器管理
ls image/        # 镜像
ls libcontainer/ # 早期 cgroup/namespace（已抽到 runc）
```

**关键 Go 包**：
- `daemon/graphdriver/`：镜像层存储（aufs/overlay2）
- `daemon/execdriver/`：执行驱动
- `daemon/network/`：网络（bridge/overlay）
- `pkg/archive/`：tar 压缩/解压

## 三、镜像分层

```go
// layer 注册
type layer struct {
    cacheID  string
    diffID   digest.Digest
    size     int64
    parent   *layer
    children map[*layer]struct{}
}

// roLayer 不可变，chainID = 所有 diffID 拼接的 sha256
type roLayer struct {
    *layer
    chainID digest.Digest
}

// graph driver：实际存储
type Driver interface {
    Create(id, parent string) error
    Get(id, mountLabel string) (containerfs.ContainerFS, error)
    Put(id string) error
    Remove(id string) error
    Diff(id string) (io.ReadCloser, error)
    ApplyDiff(id string, diff io.Reader) (int64, error)
}
```

**overlay2 驱动**：
- `/var/lib/docker/overlay2/<id>/diff`：可读可写层
- `/var/lib/docker/overlay2/<id>/merged`：联合挂载点
- `/var/lib/docker/overlay2/<id>/work`：OverlayFS 内部

## 四、Namespace + Cgroup 隔离

```go
import "github.com/opencontainers/runc/libcontainer"

// 创建 namespace
ns := []syscall.Cloneflag{
    syscall.CLONE_NEWNS,    // mount
    syscall.CLONE_NEWPID,   // PID
    syscall.CLONE_NEWNET,   // network
    syscall.CLONE_NEWUTS,   // hostname
    syscall.CLONE_NEWIPC,   // IPC
    syscall.CLONE_NEWUSER,  // UID/GID
}

// Cgroup 限制
cgroup := &configs.Cgroup{
    Name: "docker-abc",
    Resources: &configs.Resources{
        MemorySwappiness: nil,
        MemoryLimit:      func() int64 { return 512 * 1024 * 1024 },  // 512MB
        CpuShares:        func() uint64 { return 1024 },
        CpuQuota:         func() int64 { return 100000 },  // 100ms per 100ms
    },
}
```

**Cgroup v2 vs v1**：v2 是 unified hierarchy，K8s 1.25+ 全面支持。

## 五、Go 的协程在 Docker 中的应用

```go
// dockerd 用 goroutine 管理 container lifecycle
func (daemon *Daemon) containerStart(...) {
    go func() {
        if err := daemon.containerd.Start(context, ...); err != nil {
            errs <- err
        }
    }()
    select {
    case err := <-errs:
        return err
    case <-time.After(10 * time.Second):
        return errors.New("container start timeout")
    }
}

// 一个 dockerd 跑 10000+ 容器，10w+ goroutine
```

**Go 优势**：相比 C，goroutine 让 dockerd 能同时管海量容器。

## 六、containerd 源码导读

```bash
git clone https://github.com/containerd/containerd
ls cmd/ctr/       # containerd CLI
ls cmd/containerd/  # daemon 入口
ls services/      # 内部服务
ls core/          # 核心抽象
```

**关键概念**：
- **Content**：OCI blob 存储
- **Image**：不可变镜像
- **Snapshot**：文件系统快照（overlayfs/native/btrfs）
- **Task**：运行中的容器
- **Lease**：资源租约

## 七、OCI Spec

```json
{
  "ociVersion": "1.0.2",
  "process": {
    "user": { "uid": 0, "gid": 0 },
    "args": ["/bin/sh"],
    "env": ["PATH=/usr/local/bin"],
    "cwd": "/",
    "rlimits": [{ "type": "RLIMIT_NOFILE", "hard": 1024, "soft": 1024 }]
  },
  "root": { "path": "rootfs" },
  "hostname": "mycontainer",
  "mounts": [
    { "destination": "/proc", "type": "proc", "source": "proc" }
  ],
  "linux": {
    "namespaces": [
      { "type": "pid" }, { "type": "network" }, { "type": "ipc" }
    ],
    "resources": {
      "memory": { "limit": 536870912 },
      "cpu": { "shares": 1024 }
    }
  }
}
```

runc 接受 OCI spec JSON，启动容器。

## 八、Docker BuildKit

**新一代构建器**：

```go
// BuildKit 用 LLB (Low-Level Builder) 表示构建图
llb.Image("golang:1.22").
    Run(llb.Shlex("go build -o /out/myapp .")).
    Run(llb.Shlex("cp /out/myapp /output/"))

// 并行执行 + 缓存复用
```

**优势**：
- 并行执行步骤
- 精确缓存（按文件内容 hash）
- 不需要 dockerd（docker buildx 远程构建）
- 支持 rootless

## 九、Go 1.11+ Modules + Vendor

Docker 早期用 vendor，2020 年后转 Go modules：

```bash
go mod init github.com/moby/moby
go mod tidy
go mod vendor
```

## 关联章节

- **04-cloud-native/kubernetes-internals**：K8s 调度
- **04-cloud-native/cncf-ecosystem**：CNCF 全景
- **04-cloud-native/etcd-internals**：etcd Raft

## 一句话总结

> **Docker 源码 = containerd + runc + daemon**。**Go 的 namespace/cgroup 抽象让容器化变简单**。
""")


add("04-cloud-native/kubernetes-internals.md", r"""---
title: Kubernetes 源码导读
---

# Kubernetes 源码导读

**Kubernetes（K8s）= Go 写的事实标准**——100+ 个组件，全是 Go。

## 一句话总结

> **K8s = kube-apiserver + kube-scheduler + kube-controller-manager + kubelet + kube-proxy + etcd**。**所有组件用 client-go 通信**。

---

## 一、K8s 架构全景

```
                    ┌──────────────┐
                    │ kubectl/UI   │
                    └──────┬───────┘
                           │ HTTPS
                    ┌──────▼───────┐
                    │ kube-apiserver │ ← 唯一入口
                    └──────┬───────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼─────┐      ┌────▼─────┐      ┌────▼─────┐
   │scheduler │      │controller│      │  etcd    │
   │          │      │ manager  │      │ (存储)   │
   └──────────┘      └──────────┘      └──────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐         ┌───▼───┐         ┌───▼───┐
   │ kubelet │         │kubelet│         │kubelet│
   │ (Node1) │         │(Node2)│         │(Node3)│
   └─────────┘         └───────┘         └───────┘
```

## 二、源码结构

```bash
git clone https://github.com/kubernetes/kubernetes
cd kubernetes

ls cmd/                  # 组件入口
  kube-apiserver/
  kube-scheduler/
  kube-controller-manager/
  kubelet/

ls pkg/                  # 核心库
  api/                   # API types
  apis/                  # API 组
  client/                # 客户端
  registry/              # 注册表
  controller/            # controller 框架
  scheduler/             # 调度器
  kubelet/               # kubelet
  kube-proxy/            # 网络代理

ls staging/              # 独立模块
  src/k8s.io/api/
  src/k8s.io/client-go/
  src/k8s.io/apimachinery/
```

**Go monorepo 模式**：`staging/src/k8s.io/*` 是 vendored 子模块。

## 三、API Server 核心

```go
// cmd/kube-apiserver/apiserver.go
func Run(completeOptions completedServerRunOptions, stopCh <-chan struct{}) error {
    server, err := CreateServerChain(completeOptions, stopCh)
    if err != nil { return err }
    
    return server.PrepareRun().Run(stopCh)
}

// 三大核心：
// 1. GenericAPIServer：HTTP + 认证 + 鉴权
// 2. Aggregator：CRD 聚合
// 3. APIExtensions：CRD 注册
```

**请求处理链**：
1. Authentication（认证）
2. Authorization（RBAC）
3. Admission（mutating/validating webhook）
4. Validation
5. Etcd 读写
6. 返回

## 四、Scheduler 调度器

```go
// pkg/scheduler/scheduler.go
type Scheduler struct {
    Algorithm    ScheduleAlgorithm
    Extenders    []SchedulerExtender
    Error       func(*Pod, error)
    Recorder     events.EventRecorder
    NextPod      func() *Pod
    WaitForCacheSync func() bool
}

func (sched *Scheduler) scheduleOne() {
    pod := sched.NextPod()
    suggestedHost, err := sched.Algorithm.Schedule(pod)
    if err != nil {
        // 抢占
        sched.preempt(pod)
        return
    }
    // 假定 (assume) 缓存
    sched.assume(assumedPod)
    // 异步 bind
    go sched.bind(assumedPod, suggestedHost)
}
```

**调度框架**（Scheduling Framework）：
- **PreFilter**：前置过滤
- **Filter**：节点过滤（资源/亲和性/污点）
- **Score**：打分
- **Reserve**：预留
- **Permit**：批准
- **PreBind**：绑定前
- **Bind**：执行绑定
- **PostBind**：绑定后

## 五、Controller Manager

```go
// pkg/controller/
type ReplicaSetController struct {
    rsControl  rsControlInterface
    podControl controller.PodControlInterface
    expectations *expectations
}

func (rsc *ReplicaSetController) processNextWorkItem() bool {
    key, _ := rsc.queue.Get()
    rsc.syncReplicaSet(key.(string))
    return true
}

func (rsc *ReplicaSetController) syncReplicaSet(key string) error {
    namespace, name := cache.SplitMetaNamespaceKey(key)
    rs, _ := rsc.rsLister.ReplicaSets(namespace).Get(name)
    // 计算当前 vs 期望
    // 调 rsc.podControl 创建/删除 pod
    // 更新 status
}
```

**workqueue 模式**：
- Informer 监听 watch 事件
- 加入 workqueue
- worker goroutine 消费
- 失败 requeue（指数退避）

## 六、client-go — 编程接口

```go
import "k8s.io/client-go/kubernetes"
import "k8s.io/client-go/tools/clientcmd"

config, _ := clientcmd.BuildConfigFromFlags("", "/path/to/kubeconfig")
clientset, _ := kubernetes.NewForConfig(config)

// List pods
pods, _ := clientset.CoreV1().Pods("default").List(ctx, metav1.ListOptions{})

// Create deployment
deployment := &appsv1.Deployment{
    ObjectMeta: metav1.ObjectMeta{Name: "nginx"},
    Spec: appsv1.DeploymentSpec{
        Replicas: int32Ptr(3),
        Selector: &metav1.LabelSelector{MatchLabels: map[string]string{"app": "nginx"}},
        Template: corev1.PodTemplateSpec{
            ObjectMeta: metav1.ObjectMeta{Labels: map[string]string{"app": "nginx"}},
            Spec: corev1.PodSpec{Containers: []corev1.Container{{Name: "nginx", Image: "nginx:1.25"}}},
        },
    },
}
clientset.AppsV1().Deployments("default").Create(ctx, deployment, metav1.CreateOptions{})
```

## 七、Informer / Watch 机制

```go
factory := informers.NewSharedInformerFactory(clientset, 30*time.Second)
podInformer := factory.Core().V1().Pods().Informer()

podInformer.AddEventHandler(cache.ResourceEventHandlerFuncs{
    AddFunc: func(obj interface{}) { /* 新 pod 加入 */ },
    UpdateFunc: func(old, new interface{}) { /* pod 更新 */ },
    DeleteFunc: func(obj interface{}) { /* pod 删除 */ },
})

factory.Start(stopCh)
factory.WaitForCacheSync(stopCh)
```

**Informer 三件套**：
1. **Reflector**：list+watch apiserver
2. **DeltaFIFO**：事件队列
3. **Indexer**：本地缓存（thread-safe）

## 八、CRD + Controller Runtime

**自定义资源**：

```go
// 定义 CRD
type MyApp struct {
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`
    Spec   MyAppSpec   `json:"spec,omitempty"`
    Status MyAppStatus `json:"status,omitempty"`
}

type MyAppSpec struct {
    Replicas int    `json:"replicas"`
    Image    string `json:"image"`
}

// 实现 DeepCopyObject
func (m *MyApp) DeepCopyObject() runtime.Object { /* ... */ }

// 注册到 Scheme
scheme.AddKnownTypes(MyAppGroupVersion, &MyApp{}, &MyAppList{})
```

**controller-runtime**（Kubebuilder）：

```go
func (r *MyAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
    var myapp myappv1.MyApp
    if err := r.Get(ctx, req.NamespacedName, &myapp); err != nil {
        return ctrl.Result{}, client.IgnoreNotFound(err)
    }
    
    // 调谐逻辑：保证 Spec.Status == Spec.Replicas
    if myapp.Status.Replicas != myapp.Spec.Replicas {
        // 创建/删除 pod
    }
    return ctrl.Result{RequeueAfter: 30 * time.Second}, nil
}
```

## 九、kubelet 核心

```go
// pkg/kubelet/kubelet.go
type Kubelet struct {
    hostname      string
    nodeName      string
    containerRuntime  kubecontainer.Runtime
    imageManager  kubeimage.Manager
    cadvisor      cadvisor.Interface
    oomWatcher    oomwatcher.Watcher
}

func (kl *Kubelet) syncPod(o syncPodOptions) error {
    // 1. 创建 sandbox（gVisor / runc）
    // 2. 启动 containers
    // 3. 设置网络
    // 4. health check (probe)
    // 5. 报告 status 给 apiserver
}
```

**CRI（Container Runtime Interface）**：
- gRPC 接口
- kubelet 调 cri，cri 调 runc / containerd

## 十、Go 的优势在 K8s

| 优势 | 体现 |
|---|---|
| 静态二进制 | kubelet / kube-proxy 几 MB，无需 runtime |
| goroutine | controller 并发处理上千对象 |
| channel | Informer 事件流 |
| interface | storage provider 抽象（etcd / 未来 sqlite） |
| gofmt | K8s 100+ 仓库风格统一 |
| go mod | 统一依赖管理 |

## 关联章节

- **04-cloud-native/docker-internals**：容器基础
- **04-cloud-native/etcd-internals**：K8s 后端存储
- **04-cloud-native/cncf-ecosystem**：CNCF 全景

## 一句话总结

> **K8s 源码 = 100+ 组件 + client-go + controller-runtime**。**Go 让大规模集群管理代码保持简洁**。
""")


add("04-cloud-native/prometheus-internals.md", r"""---
title: Prometheus 源码导读
---

# Prometheus 源码导读

**Prometheus = Cloud Native 监控的事实标准**——Go 写，80+ 组件，10 年迭代。

## 一句话总结

> **Prometheus = pull-based TSDB + PromQL + alerting + service discovery**。**Go 让单机/集群部署都简单**。

---

## 一、Prometheus 架构

```
┌──────────────┐
│  targets     │  ← 应用 / exporter
└──────┬───────┘
       │ HTTP GET /metrics
       ▼
┌──────────────┐
│  Prometheus  │  ← 采集 + TSDB + 规则
│   Server     │
└──────┬───────┘
       │ remote_write
       ▼
┌──────────────┐
│  Alertmanager│  ← 告警聚合 / 去重 / 路由
└──────┬───────┘
       │ Webhook / Email / Slack
       ▼
┌──────────────┐
│  Grafana     │  ← 可视化
└──────────────┘
```

## 二、源码结构

```bash
git clone https://github.com/prometheus/prometheus
ls cmd/prometheus/      # 主服务
ls cmd/promtool/        # 工具
ls discovery/           # 服务发现（k8s / consul / file）
ls rules/               # 告警规则
ls storage/             # TSDB 存储
ls scrape/              # 抓取逻辑
ls web/                 # Web UI
```

**关键包**：
- `prometheus/tsdb/`：自研 TSDB
- `prometheus/promql/`：查询引擎
- `prometheus/discovery/`：服务发现
- `prometheus/rules/`：告警/记录规则

## 三、TSDB 存储

```go
// storage/tsdb/db.go
type DB struct {
    dir   string
    opts  *Options
    chunkPool chunkenc.Pool
    blocks []*Block
    head   *Head
    
    // 时间序列索引
    series *seriesIndex
    postings *index.Postings
}

// 时间序列由 labels hash 索引
type labels.Labels []Label  // 键值对

// Append 一个样本
func (a *headAppender) Add(lset labels.Labels, t int64, v float64) (uint64, error) {
    s, _, err := a.head.getOrCreate(lset.Hash(), lset)
    if err != nil { return 0, err }
    a.samples = append(a.samples, record.RefSample{Ref: s, T: t, V: v})
    return s, nil
}
```

**TSDB 关键概念**：
- **Block**：2 小时数据，压缩成 mmap 块
- **WAL**：Write-Ahead Log，崩溃恢复
- **Compaction**：小 block 合并成大 block
- **Retention**：超过保留期 block 删
- **Out-of-order**：乱序样本支持（Prometheus 2.4+）

## 四、PromQL 引擎

```go
// promql/engine.go
type Engine struct {
    opts           EngineOptions
    ng             *numberLoader
    storage        storage.Storage
}

// 编译 PromQL → AST → 逻辑计划 → 物理计划
func (ng *engine) NewInstantQuery(queryable storage.Queryable, qs string, ts time.Time) (Query, error) {
    expr, err := parser.ParseExpr(qs)
    if err != nil { return nil, err }
    q, err := ng.newQuery(queryable, expr, ts, ts, 0)
    return q, err
}
```

**核心算子**：
- `rate()`：每秒增长率
- `irate()`：瞬时增长率
- `sum/rate`：聚合
- `histogram_quantile()`：直方图分位数
- `predict_linear()`：线性预测

**查询优化**：向量匹配、索引查找、并发执行。

## 五、Scrape 抓取

```go
// scrape/scrape.go
type scrapePool struct {
    config    *config.ScrapeConfig
    client    *http.Client
    targets   map[uint64]*Target
    // ...
}

func (sp *scrapePool) sync(targets []*Target) {
    // 1. 标记 active
    for _, t := range targets {
        if t.Disabled(GlobalState.Labels) { continue }
        t.setActive(GlobalState.ScrapePools.OC())
    }
    
    // 2. 拉取 metrics
    for _, t := range active {
        go t.scrapeAndReport()
    }
}
```

**Target 抓取**：
1. HTTP GET `<target>/metrics`
2. 解析文本格式
3. 写到 TSDB
4. 失败标记

## 六、Service Discovery

```go
// discovery/kubernetes/kubernetes.go
type Discovery struct {
    client kubernetes.Interface
    role   string  // endpoints/pod/service
}

func (d *Discovery) Run(ctx context.Context, ch chan<- []*targetgroup.Group) {
    // 1. 列出资源
    endpoints, _ := d.client.CoreV1().Endpoints("default").List(ctx, metav1.ListOptions{})
    // 2. 转成 targets
    for _, ep := range endpoints.Items {
        tg := &targetgroup.Group{Source: ep.Name}
        for _, ss := range ep.Subsets {
            for _, addr := range ss.Addresses {
                tg.Targets = append(tg.Targets, model.LabelSet{
                    "__address__":                  model.LabelValue(dn + ":" + port),
                    "__meta_kubernetes_pod_label_app":  model.LabelValue("myapp"),
                })
            }
        }
        ch <- []*targetgroup.Group{tg}
    }
}
```

**支持 30+ SD**：
- k8s / endpoints / pod / service / ingress
- consul / eureka
- file / http / dns / aws / gce / azure

## 七、Alerting

```yaml
# rule.yaml
groups:
  - name: example
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status="500"}[5m]))
            /
          sum(rate(http_requests_total[5m]))
            > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate"
          description: "{{ $value | humanizePercentage }} errors"
```

**告警生命周期**：
1. Prometheus 评估规则
2. ALERT 状态推送 Alertmanager
3. Alertmanager 路由 / 去重 / 抑制 / 静默
4. 发送 Webhook / Email / Slack

## 八、Remote Write

```go
// storage/remote/write.go
func (w *WriteStorage) Write(req *remote.WriteRequest) error {
    // 1. 编码（snappy + protobuf）
    // 2. 发送到 remote（Thanos / Cortex / Mimir / VictoriaMetrics）
    // 3. 队列 + 重试
}
```

**为何需要 remote write**：
- Prometheus 单机容量有限（百万级时间序列）
- Remote write 到对象存储（S3/GCS）实现长期
- 多 Prometheus 联邦查询

## 九、Go 的优势在 Prometheus

| 优势 | 体现 |
|---|---|
| 静态二进制 | 单文件部署，无需 Python/Ruby runtime |
| goroutine | 10000+ target 并发抓取 |
| mmap | TSDB block 用 mmap 提升 IO |
| Prometheus client_golang | Go 应用无缝埋点 |
| go mod | 各组件独立发布 |

## 十、Prometheus 2.x vs VictoriaMetrics

| 指标 | Prometheus | VictoriaMetrics |
|---|---|---|
| 单机容量 | 千万级 | 亿级 |
| 存储压缩 | ~2 bytes/sample | ~0.5 bytes/sample |
| Remote write | 支持 | 支持（更快） |
| Go 写 | 是 | 是 |
| 集群方案 | Agent + 联邦 / Cortex | Enterprise Cluster |

## 关联章节

- **04-cloud-native/kubernetes-internals**：K8s SD
- **04-cloud-native/etcd-internals**：另一种分布式存储
- **04-cloud-native/cncf-ecosystem**：CNCF 全景

## 一句话总结

> **Prometheus 源码 = TSDB + PromQL + scrape + SD + alert**。**Go 的并发 + mmap + 静态部署让监控变简单**。
""")


add("04-cloud-native/etcd-internals.md", r"""---
title: etcd 源码导读
---

# etcd 源码导读

**etcd = 分布式 KV + Raft + watch**——K8s / 微服务的事实配置/协调中心。

## 一句话总结

> **etcd = Raft 共识 + BoltDB + gRPC + watch + lease**。**Go 让分布式系统代码保持可读**。

---

## 一、etcd 是什么

- **名字**：/`ˈɛtsiːdiː/`，Linux `/etc` 配置目录 + distributed `d`
- **作者**：李响（CoreOS，后 Red Hat / IBM）
- **用途**：K8s 后端存储 / 服务发现 / 配置中心 / 分布式锁
- **CAP**：CP（强一致）

## 二、架构

```
┌──────────────────────────┐
│ Client (curl / etcdctl)  │
└────────────┬─────────────┘
             │ gRPC
             ▼
┌──────────────────────────┐
│   etcd server (v3 API)   │
│  ┌──────────────────┐    │
│  │ Raft consensus   │    │
│  └────────┬─────────┘    │
│  ┌────────▼─────────┐    │
│  │ MVCC tree (BoltDB)│    │
│  └────────┬─────────┘    │
│  ┌────────▼─────────┐    │
│  │ gRPC + watch +   │    │
│  │ lease + auth     │    │
│  └──────────────────┘    │
└──────────────────────────┘
```

## 三、源码结构

```bash
git clone https://github.com/etcd-io/etcd
ls server/        # 核心服务
  etcdserver/    # etcd 主循环
  auth/          # 鉴权
  lease/         # 租约
  mvcc/          # 多版本并发控制
  watcher/       # 监听
ls raft/         # Raft 实现
ls wal/          # Write-Ahead Log
ls store/        # 旧版 v2 store
ls client/       # 客户端 SDK
ls etcdctl/      # CLI
```

## 四、Raft 一致性算法

```go
// raft/raft.go
type raft struct {
    id uint64
    Term uint64
    Vote uint64
    state StateType  // Follower / Candidate / Leader
    
    log          *raftLog
    nextEnts()   []pb.Entry
    // ...
}

// 心跳 + 日志复制
func (r *raft) tickElection() {
    r.electionElapsed++
    if r.promotable() && r.pastElectionTimeout() {
        r.campaign()  // 转 Candidate
    }
}

// 投票
func (r *raft) campaign(t CampaignType) {
    r.becomeCandidate()
    if r.quorum() == r.votes {
        r.becomeLeader()  // 半数以上当选
    }
}
```

**Raft 三种角色**：
- **Follower**：被动接收
- **Candidate**：竞选 Leader
- **Leader**：处理写操作

**Raft 关键概念**：
- **Term**：逻辑时钟
- **Election timeout**：150-300ms 随机
- **Heartbeat**：50ms
- **Log replication**：复制到多数
- **Snapshot**：压缩日志

**Raft vs Paxos**：Raft = 易懂的 Paxos，etcd 用 Raft。

## 五、MVCC 多版本并发控制

```go
// server/mvcc/kvstore.go
type store struct {
    mu    sync.RWMutex
    revMu sync.RWMutex
    
    tree  *btree.BTree   // 内存索引
    
    // 持久化
    ss       *bolt.Session
    bucket   *bolt.Bucket  // "key"
    metaBucket *bolt.Bucket  // "meta"
    
    // 压缩
    compactMainRev int64
}

func (s *store) Put(key, val []byte, leaseID lease.LeaseID) int64 {
    rev := s.currentRev + 1
    s.saveKey(key, val, rev)  // 写到 BoltDB
    s.tree.ReplaceOrInsert(newKey)  // 更新内存索引
    s.currentRev = rev
    return rev
}
```

**核心概念**：
- **revision**：每次写递增的版本号
- **mod_revision**：key 最后修改的 revision
- **create_revision**：key 创建的 revision
- **version**：key 修改次数

**Range 查询支持历史**：给定 revision，可查该时刻的 value。

## 六、BoltDB — 嵌入式 KV

```go
// bolt.Open
db, _ := bolt.Open("etcd.db", 0600, nil)
defer db.Close()

db.Update(func(tx *bolt.Tx) error {
    bucket, _ := tx.CreateBucketIfNotExists([]byte("key"))
    return bucket.Put([]byte("hello"), []byte("world"))
})

db.View(func(tx *bolt.Tx) error {
    bucket := tx.Bucket([]byte("key"))
    val := bucket.Get([]byte("hello"))
    fmt.Println(string(val))  // "world"
    return nil
})
```

**BoltDB 特点**：
- 嵌入式（无 server）
- B+ 树实现
- ACID 事务
- mmap 读写
- 纯 Go（无 CGO）

## 七、gRPC API

```protobuf
service KV {
  rpc Range(RangeRequest) returns (RangeResponse) {}
  rpc Put(PutRequest) returns (PutResponse) {}
  rpc DeleteRange(DeleteRangeRequest) returns (DeleteRangeResponse) {}
  rpc Txn(TxnRequest) returns (TxnResponse) {}
  rpc Compact(CompactionRequest) returns (CompactionResponse) {}
}

service Watch {
  rpc Watch(WatchRequest) returns (stream WatchResponse) {}
}

service Lease {
  rpc LeaseGrant(LeaseGrantRequest) returns (LeaseGrantResponse) {}
  rpc LeaseKeepAlive(stream LeaseKeepAliveRequest) returns (stream LeaseKeepAliveResponse) {}
}
```

**V3 全部用 gRPC**，V2 REST API 仍兼容。

## 八、Watch 监听

```go
// server/mvcc/watcher.go
type watcher struct {
    id     WatchID
    unsynced watcherSet  // 未同步的
    synced  watcherSet  // 已同步的
    ch     chan WatchResponse
}

func (w *watcher) notify(e mvccpb.Event) {
    select {
    case w.ch <- WatchResponse{...}:
    case <-time.After(3*time.Second):
        // 慢消费者
    }
}
```

**Watch 机制**：
- 客户端订阅 key 前缀
- server 推送变更事件
- 支持 progress_notify（防止事件丢失）
- 支持 compact_revision 过滤

**真实使用**：K8s 内部 list+watch 通过 etcd watch 实现。

## 九、Lease 租约

```go
// server/lease/lessor.go
type lessor struct {
    mu     sync.Mutex
    leases map[LeaseID]*Lease
    
    // 过期检查
    leaseExpiredNotifier *Notifier
}

type Lease struct {
    ID      LeaseID
    ttl     int64
    itemSet map[WatchID]struct{}  // 关联的 key
    expiry  time.Time
}

// KeepAlive（10s 一次）
lease, _ := client.Grant(ctx, 10)  // 10s TTL
client.Put(ctx, "key", "val", clientv3.WithLease(lease.ID))
ch, _ := client.KeepAlive(ctx, lease.ID)  // 持续 keepalive
```

**Lease vs TTL**：
- **TTL**：key 单独过期
- **Lease**：key 绑定租约，租约过期 key 全删

## 十、客户端使用

```go
import "go.etcd.io/etcd/client/v3"

cli, _ := clientv3.New(clientv3.Config{
    Endpoints:   []string{"localhost:2379"},
    DialTimeout: 5 * time.Second,
})
defer cli.Close()

// Put
cli.Put(ctx, "key", "value")

// Get
resp, _ := cli.Get(ctx, "key", clientv3.WithPrefix())
for _, kv := range resp.Kvs {
    fmt.Printf("%s = %s\n", kv.Key, kv.Value)
}

// Watch
rch := cli.Watch(ctx, "key", clientv3.WithPrefix())
for wresp := range rch {
    for _, ev := range wresp.Events {
        fmt.Printf("Type: %s Key: %s Value: %s\n", ev.Type, ev.Kv.Key, ev.Kv.Value)
    }
}

// Txn
cli.Txn(ctx).
    If(clientv3.Compare(clientv3.Value("lock"), "=", "owner1")).
    Then(clientv3.OpPut("lock", "owner2")).
    Else(clientv3.OpGet("lock")).
    Commit()
```

## 十一、性能调优

```bash
# etcd 启动参数
--data-dir=/var/lib/etcd
--listen-client-urls=http://0.0.0.0:2379
--advertise-client-urls=http://node1:2379
--listen-peer-urls=http://0.0.0.0:2380
--initial-advertise-peer-urls=http://node1:2380
--initial-cluster=node1=http://node1:2380,node2=http://node2:2380,node3=http://node3:2380
--initial-cluster-token=etcd-cluster-1
--initial-cluster-state=new

# 调优
--quota-backend-bytes=8589934592  # 8GB 存储上限
--max-request-bytes=10485760       # 10MB 请求
--election-timeout=1000
--heartbeat-interval=100
```

**K8s 性能建议**：
- 3-5 节点，奇数
- SSD 存储
- CPU 4-8 核
- 内存 8-16GB
- 网络 1Gbps+

## 关联章节

- **04-cloud-native/kubernetes-internals**：K8s 用 etcd
- **04-cloud-native/prometheus-internals**：另一种存储
- **04-cloud-native/cncf-ecosystem**：CNCF 全景

## 一句话总结

> **etcd = Raft + MVCC + BoltDB + gRPC**。**Go + BoltDB 让 etcd 成为分布式协调的瑞士军刀**。
""")


add("04-cloud-native/cncf-ecosystem.md", r"""---
title: CNCF 项目全景
---

# CNCF 项目全景

**CNCF（Cloud Native Computing Foundation）= 云原生生态**——80% 项目是 Go 写。

## 一句话总结

> **CNCF Landscape = 130+ 毕业项目 + 200+ 沙盒项目**。**Go 是云原生时代的 C 语言**。

---

## 一、CNCF 是什么

- 2015 年成立，Linux Foundation 旗下
- 总部：旧金山
- 会员：红帽 / 谷歌 / AWS / Azure / 阿里 / 华为 / 腾讯 / 字节...
- 目标：推广云原生技术（容器 / 服务网格 / 监控 / GitOps）

## 二、毕业项目 TOP 30

| 阶段 | 项目 | 用途 | Go 占比 |
|---|---|---|---|
| 🎓 | **Kubernetes** | 容器编排 | 100% |
| 🎓 | **Prometheus** | 监控 | 100% |
| 🎓 | **etcd** | KV 存储 | 100% |
| 🎓 | **containerd** | 容器 runtime | 100% |
| 🎓 | **CoreDNS** | DNS 服务 | 100% |
| 🎓 | **Fluentd** | 日志收集 | 30% (CRuby) |
| 🎓 | **Envoy** | 服务代理 | 60% (C++) |
| 🎓 | **Helm** | K8s 包管理 | 100% |
| 🎓 | **TiKV** | 分布式 KV | 100% (Rust 10%) |
| 🎓 | **Jaeger** | 分布式追踪 | 100% |
| 🎓 | **Vitess** | MySQL 集群 | 100% |
| 🎓 | **TUF** | 安全更新 | 100% |
| 🎓 | **Argo** | 工作流 | 100% |
| 🎓 | **Cilium** | CNI + Service Mesh | 70% (C 30%) |
| 🎓 | **Crossplane** | K8s 控制平面 | 100% |
| 🎓 | **Backstage** | 开发者门户 | 80% (TS 20%) |
| 🎓 | **Cortex** | Prometheus 集群 | 100% |
| 🎓 | **Thanos** | Prometheus 长期存储 | 100% |
| 🎓 | **OpenTelemetry** | 可观测性 | 70% |
| 🎓 | **KubeVirt** | 虚拟机 K8s | 100% |
| 🎓 | **Karmada** | 多云 K8s | 100% |
| 🎓 | **Keda** | 事件驱动 K8s | 100% |
| 🎓 | **cert-manager** | TLS 证书 | 100% |
| 🎓 | **Dapr** | 应用运行时 | 100% |
| 🎓 | **Istio** | Service Mesh | 100% (Envoy 60%) |
| 🎓 | **rook** | 存储编排 | 100% |
| 🎓 | **Linkerd** | Service Mesh | 90% (Rust 10%) |
| 🎓 | **SPIFFE/SPIRE** | 身份认证 | 100% |
| 🎓 | **Dragonfly** | 镜像分发 | 100% |
| 🎓 | **WasmEdge** | WebAssembly runtime | 70% (C++) |

**Go 比例**：约 80% 的 CNCF 项目主要用 Go 写。

## 三、沙盒项目精选

| 项目 | 用途 |
|---|---|
| **Kubewarden** | K8s admission policy（用 Rust 沙箱） |
| **KubeArmor** | K8s 运行时安全 |
| **Parsec** | 云原生 PKI |
| **Tinkerbell** | bare-metal 编排 |
| **Curiefense** | API 安全网关 |
| **PipeCD** | GitOps（CD） |
| **OpenFeature** | Feature flag 标准 |
| **KCL** | 配置语言 |
| **KubeVela** | 应用抽象层 |
| **Sealer** | K8s 集群镜像 |

## 四、CNCF Landscape 分层

```
┌─────────────────────────────────────────┐
│  App Definition & Development           │
│  Helm / Skaffold / Tilt / Backstage     │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Orchestration & Management             │
│  Kubernetes / Argo / Crossplane / Karmada│
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Runtime                                │
│  containerd / runc / gVisor / Kata      │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Provisioning                           │
│  Terraform / Crossplane / Pulumi        │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Platform                               │
│  Rancher / OpenShift / TKE              │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Observability & Analysis               │
│  Prometheus / Loki / Tempo / Jaeger     │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Service Mesh / RPC / API Gateway       │
│  Istio / Linkerd / Envoy / Dapr         │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Storage                                │
│  Rook / MinIO / TiKV / Vitess           │
└──────────────┬──────────────────────────┘
               ▼
┌─────────────────────────────────────────┐
│  Security & Compliance                  │
│  cert-manager / TUF / SPIFFE / Falco    │
└─────────────────────────────────────────┘
```

## 五、Go 在 CNCF 中的技术垄断

**原因 1：Go 的语言特性契合云原生**

| 需求 | Go 的方案 |
|---|---|
| 静态二进制（容器友好） | `CGO_ENABLED=0` 单文件几 MB |
| 跨平台编译 | `GOOS=linux GOARCH=arm64 go build` |
| 高并发 | goroutine + channel |
| 网络协议 | gRPC 官方支持 |
| 标准库 | net/http / crypto/tls / encoding/json |
| 部署简单 | 单二进制 + 配置文件 |

**原因 2：Google 的示范效应**

- K8s（Google）= Go
- gRPC（Google）= Go
- Borg → K8s → 全行业跟进

**原因 3：Docker / K8s 时代红利**

- 2014 年 Docker 爆发，Go 工程师需求暴增
- K8s 1.0（2015）需要 Go 开发者

**原因 4：库生态正循环**

- client-go、controller-runtime → K8s operator
- gRPC-Go / protobuf → 微服务
- prometheus/client_golang → 监控

## 六、Go 写的明星项目

### 容器 & 编排
- Kubernetes（10w+ stars）
- Docker（68k+）
- containerd（15k+）
- Helm（25k+）
- Argo（15k+）
- k3s / k0s（轻量 K8s）

### 服务网格 & API
- Istio（35k+）
- Linkerd（10k+）
- Dapr（23k+）
- Traefik（47k+）
- Caddy（54k+）

### 可观测性
- Prometheus（53k+）
- Thanos（12k+）
- Cortex（5k+）
- Loki（22k+）
- Tempo（4k+）
- OpenTelemetry（Go SDK 1.5k+）

### 数据库 & 存储
- etcd（46k+）
- TiKV（14k+）
- Vitess（17k+）
- MinIO（44k+）
- CockroachDB（28k+）
- InfluxDB（28k+）
- ClickHouse（C++ 但有 Go client）
- Dragonfly（13k+）
- NATS（15k+）

### DevOps
- Terraform（41k+）
- Vault（29k+）
- Packer（14k+）
- Consul（27k+）
- Nomad（14k+）

## 七、非 Go 但同生态

- **Rust**：Linkerd 2-proxy / TiKV 部分 / Kubewarden / Deno runtime
- **C++**：Envoy / Istio data plane / ClickHouse
- **TypeScript**：Backstage / Deno（少数）
- **Java**：Elasticsearch / Solr / Cassandra
- **Python**：Pyroscope / Apache Airflow

## 八、Go 在 CNCF 贡献者生态

**贡献数据**（2024）：
- 70%+ 的 CNCF 项目核心维护者用 Go
- CNCF 维护者中 Go 开发者占 60%
- K8s 1.30 release 有 400+ 贡献者

## 九、学习路径

**入门路径**：
1. **Go 基础**：语法 / goroutine / interface
2. **net/http**：写 REST API
3. **gRPC**：服务间通信
4. **Docker**：容器化
5. **K8s**：deploy 到集群
6. **Prometheus**：埋点 + 抓取
7. **Operator / CRD**：K8s 扩展
8. **Service Mesh**：Istio / Linkerd

**项目参与路径**：
- 入门：good first issue
- 进阶：fix bug / improve docs
- 高级：feature / design proposal

## 关联章节

- **04-cloud-native/docker-internals**：容器
- **04-cloud-native/kubernetes-internals**：编排
- **04-cloud-native/prometheus-internals**：监控
- **04-cloud-native/etcd-internals**：存储

## 一句话总结

> **CNCF Landscape = 云原生生态地图**。**Go 是云原生时代的 C 语言，统治 80% 项目**。
""")


# === 05-microservices ===

add("05-microservices/gin-framework.md", r"""---
title: Gin 框架
---

# Gin Web 框架

**Gin = Go 生态最流行的 Web 框架**——80k+ stars，性能接近 net/http + httprouter。

## 一句话总结

> **Gin = httprouter 路由 + 中间件链 + JSON 绑定 + 错误处理**。**替代品：Echo / Fiber / Chi**。

---

## 一、为什么选 Gin

- 性能：50k+ QPS
- API 友好：JSON / XML / YAML
- 中间件：日志 / 认证 / 限流 / 跨域
- 错误恢复：`recover()` 防 panic 进程挂
- 生态：JWT / CORS / GORM / Redis / K8s client

## 二、Hello World

```go
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()  // 包含 Logger + Recovery 中间件
    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "pong"})
    })
    r.Run()  // 监听 0.0.0.0:8080
}
```

## 三、路由

```go
// 静态
r.GET("/users", listUsers)
r.POST("/users", createUser)
r.PUT("/users/:id", updateUser)
r.DELETE("/users/:id", deleteUser)
r.PATCH("/users/:id", patchUser)

// 参数
c.Param("id")  // /users/123 → "123"

// 查询参数
c.Query("page")   // /users?page=2
c.DefaultQuery("page", "1")

// 通配
r.GET("/static/*filepath", serveStatic)

// 路由组（中间件 + 公共前缀）
v1 := r.Group("/v1")
{
    auth := v1.Group("/", authMiddleware())
    {
        auth.GET("/users", listUsers)
        auth.POST("/users", createUser)
    }
}
```

## 四、Handler

```go
func listUsers(c *gin.Context) {
    // 1. 拿参数
    page := c.DefaultQuery("page", "1")
    
    // 2. 调 service
    users, err := userService.List(page)
    if err != nil {
        c.JSON(500, gin.H{"error": err.Error()})
        return
    }
    
    // 3. 返回
    c.JSON(200, users)
    // 或：c.JSON(200, gin.H{"data": users, "code": 0})
}
```

## 五、绑定

```go
type CreateUserReq struct {
    Name  string `json:"name" binding:"required,min=2,max=20"`
    Email string `json:"email" binding:"required,email"`
    Age   int    `json:"age" binding:"gte=0,lte=150"`
}

func createUser(c *gin.Context) {
    var req CreateUserReq
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    // req 已验证通过
}

// 四种绑定
c.ShouldBindJSON(&req)      // JSON body
c.ShouldBind(&req)          // 自动识别（JSON / form / query）
c.ShouldBindUri(&req)       // URI 参数
c.ShouldBindQuery(&req)     // Query 字符串
```

**Validation**：Gin 用 go-playground/validator，支持 required / email / min / max / gte / lte / oneof / uuid / alphanum 等。

## 六、中间件

```go
// 自定义中间件
func LoggerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        c.Next()  // 执行 handler
        log.Printf("%s %s %v", c.Request.Method, c.Request.URL.Path, time.Since(start))
    }
}

// 全局中间件
r.Use(LoggerMiddleware(), gin.Recovery())

// 路由组中间件
authGroup := r.Group("/admin", authMiddleware())

// 单路由中间件
r.GET("/users", authMiddleware(), listUsers)
```

**常用中间件**：
- `gin.Recovery()`：panic 恢复
- `gin.Logger()`：访问日志
- `cors.New(...)`：CORS
- `jwt.New(...)`：JWT 验证
- `ratelimit.New(...)`：限流

## 七、完整 CRUD 例子

```go
package main

import (
    "net/http"
    "strconv"
    "github.com/gin-gonic/gin"
)

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}

var users = make(map[int]*User)
var nextID = 1

func main() {
    r := gin.Default()
    
    r.GET("/users", func(c *gin.Context) {
        list := make([]*User, 0, len(users))
        for _, u := range users { list = append(list, u) }
        c.JSON(200, list)
    })
    
    r.GET("/users/:id", func(c *gin.Context) {
        id, _ := strconv.Atoi(c.Param("id"))
        u, ok := users[id]
        if !ok {
            c.JSON(404, gin.H{"error": "not found"})
            return
        }
        c.JSON(200, u)
    })
    
    r.POST("/users", func(c *gin.Context) {
        var u User
        if err := c.ShouldBindJSON(&u); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }
        u.ID = nextID
        nextID++
        users[u.ID] = &u
        c.JSON(201, u)
    })
    
    r.PUT("/users/:id", func(c *gin.Context) {
        id, _ := strconv.Atoi(c.Param("id"))
        var u User
        c.ShouldBindJSON(&u)
        u.ID = id
        users[id] = &u
        c.JSON(200, u)
    })
    
    r.DELETE("/users/:id", func(c *gin.Context) {
        id, _ := strconv.Atoi(c.Param("id"))
        delete(users, id)
        c.Status(204)
    })
    
    r.Run(":8080")
}
```

## 八、与其他框架对比

| 框架 | 路由算法 | 性能 | 特色 |
|---|---|---|---|
| **Gin** | httprouter（基数树） | 50k QPS | 生态最丰富 |
| **Echo** | 基数树 | 60k QPS | API 略胜 Gin |
| **Fiber** | fasthttp | 100k+ QPS | Express-like |
| **Chi** | 基数树 | 50k QPS | 标准库风格 |
| **net/http** | 无 | 30k QPS | 标准库 |
| **Iris** | 基数树 | 50k QPS | 较老，功能多 |

**建议**：Gin 适合 90% 场景；极致性能选 Fiber（但 fasthttp 不兼容 net/http）。

## 九、生产实践

**项目结构**：

```
myapp/
├── cmd/
│   └── server/main.go
├── internal/
│   ├── handler/    # HTTP handler
│   ├── service/    # 业务逻辑
│   ├── repo/       # 数据访问
│   └── model/      # 数据模型
├── pkg/
│   ├── middleware/
│   └── util/
├── configs/
│   └── config.yaml
├── go.mod
└── go.sum
```

**优雅关闭**：

```go
srv := &http.Server{Addr: ":8080", Handler: r}
go srv.ListenAndServe()

quit := make(chan os.Signal, 1)
signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
<-quit

ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
if err := srv.Shutdown(ctx); err != nil {
    log.Fatal("Server forced to shutdown:", err)
}
```

## 关联章节

- **05-microservices/grpc**：gRPC
- **05-microservices/kratos**：微服务框架
- **03-ecosystem/standard-library**：net/http

## 一句话总结

> **Gin = httprouter + 中间件 + 验证**。**90% Go Web 项目首选**。
""")


add("05-microservices/grpc.md", r"""---
title: gRPC + Protobuf
---

# gRPC + Protobuf

**gRPC = 跨语言高性能 RPC 框架**——基于 HTTP/2 + Protobuf，由 Google 开发。

## 一句话总结

> **gRPC = HTTP/2 + Protobuf + 多语言 + 流式 RPC**。**微服务内部通信的事实标准**。

---

## 一、为什么选 gRPC

| 优势 | 体现 |
|---|---|
| 性能 | Protobuf 二进制编码，比 JSON 小 3-10 倍 |
| 类型安全 | .proto 生成客户端/服务端代码 |
| 多语言 | Go/Java/Python/Node/Rust/C++/PHP 全部支持 |
| 流式 | 服务端 / 客户端 / 双向流 |
| HTTP/2 | 多路复用 + Header 压缩 |
| 自动生成 | protoc 自动生成 stub |

**vs REST**：
- 性能：gRPC 5-10x
- 类型：gRPC 强类型 vs REST 弱类型
- 工具：gRPC 需 protoc vs REST 只需 curl
- 浏览器：gRPC 需要 grpc-web 代理

## 二、Protobuf 定义

**user.proto**：

```protobuf
syntax = "proto3";

package user.v1;

option go_package = "github.com/myorg/myapp/api/user/v1;userv1";

service UserService {
    rpc GetUser(GetUserRequest) returns (GetUserResponse);
    rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
    rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
    rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);
    rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);
    
    // 服务端流
    rpc WatchUsers(WatchUsersRequest) returns (stream UserEvent);
    // 客户端流
    rpc BatchCreateUsers(stream CreateUserRequest) returns (BatchResponse);
    // 双向流
    rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message User {
    int64 id = 1;
    string name = 2;
    string email = 3;
    int32 age = 4;
    repeated string tags = 5;
    map<string, string> metadata = 6;
}

message GetUserRequest { int64 id = 1; }
message GetUserResponse { User user = 1; }

message ListUsersRequest {
    int32 page = 1;
    int32 page_size = 2;
    string filter = 3;
}
message ListUsersResponse {
    repeated User users = 1;
    int32 total = 2;
}
```

## 三、生成 Go 代码

```bash
# 安装工具
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# 生成
protoc --go_out=. --go_opt=paths=source_relative \
       --go-grpc_out=. --go-grpc_opt=paths=source_relative \
       proto/user.proto

# 产物
api/user/v1/user.pb.go        # 消息类型
api/user/v1/user_grpc.pb.go   # 服务端/客户端接口
```

## 四、服务端实现

```go
package main

import (
    "context"
    "net"
    "google.golang.org/grpc"
    pb "github.com/myorg/myapp/api/user/v1"
)

type server struct {
    pb.UnimplementedUserServiceServer
    db *sql.DB
}

func (s *server) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
    var u pb.User
    err := s.db.QueryRowContext(ctx, "SELECT id, name, email, age FROM users WHERE id = ?", req.Id).
        Scan(&u.Id, &u.Name, &u.Email, &u.Age)
    if err != nil {
        return nil, status.Errorf(codes.NotFound, "user not found: %v", err)
    }
    return &pb.GetUserResponse{User: &u}, nil
}

func (s *server) ListUsers(ctx context.Context, req *pb.ListUsersRequest) (*pb.ListUsersResponse, error) {
    rows, _ := s.db.QueryContext(ctx, "SELECT id, name, email, age FROM users LIMIT ? OFFSET ?",
        req.PageSize, (req.Page-1)*req.PageSize)
    defer rows.Close()
    
    var users []*pb.User
    for rows.Next() {
        var u pb.User
        rows.Scan(&u.Id, &u.Name, &u.Email, &u.Age)
        users = append(users, &u)
    }
    return &pb.ListUsersResponse{Users: users, Total: int32(len(users))}, nil
}

func (s *server) WatchUsers(req *pb.WatchUsersRequest, stream pb.UserService_WatchUsersServer) error {
    ch := subscribe(req.Filter)
    for ev := range ch {
        if err := stream.Send(&pb.UserEvent{User: ev.User, Type: pb.UserEventType_USER_UPDATED}); err != nil {
            return err
        }
    }
    return nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    s := grpc.NewServer()
    pb.RegisterUserServiceServer(s, &server{db: openDB()})
    s.Serve(lis)
}
```

## 五、客户端实现

```go
package main

import (
    "context"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    pb "github.com/myorg/myapp/api/user/v1"
)

func main() {
    conn, _ := grpc.Dial("localhost:50051", grpc.WithTransportCredentials(insecure.NewCredentials()))
    defer conn.Close()
    
    client := pb.NewUserServiceClient(conn)
    
    // Unary call
    resp, err := client.GetUser(context.Background(), &pb.GetUserRequest{Id: 42})
    
    // Server streaming
    stream, _ := client.WatchUsers(context.Background(), &pb.WatchUsersRequest{})
    for {
        event, err := stream.Recv()
        if err == io.EOF { break }
        fmt.Println(event)
    }
}
```

## 六、拦截器（Middleware）

```go
// 服务端
func loggingInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    start := time.Now()
    resp, err := handler(ctx, req)
    log.Printf("method=%s duration=%v err=%v", info.FullMethod, time.Since(start), err)
    return resp, err
}

s := grpc.NewServer(grpc.UnaryInterceptor(loggingInterceptor))

// 客户端
client := pb.NewUserServiceClient(conn, grpc.WithUnaryInterceptor(authInterceptor))
```

## 七、TLS + 认证

```go
// 服务端 TLS
creds, _ := credentials.NewServerTLSFromFile("server.crt", "server.key")
s := grpc.NewServer(grpc.Creds(creds))

// mTLS
cert, _ := tls.LoadX509KeyPair("client.crt", "client.key")
caPool := x509.NewCertPool()
caPool.AddCert(caCert)
creds := credentials.NewTLS(&tls.Config{Certificates: []tls.Certificate{cert}, RootCAs: caPool})

// 客户端
conn, _ := grpc.Dial("server:50051", grpc.WithTransportCredentials(creds))

// Token 认证
md := metadata.New(map[string]string{"authorization": "Bearer " + token})
ctx := metadata.NewOutgoingContext(context.Background(), md)
```

## 八、gRPC 错误处理

```go
import "google.golang.org/grpc/status"
import "google.golang.org/grpc/codes"

// 服务端
if err != nil {
    return nil, status.Errorf(codes.NotFound, "user %d not found", id)
}

// 客户端
resp, err := client.GetUser(ctx, req)
if err != nil {
    st, ok := status.FromError(err)
    if ok {
        switch st.Code() {
        case codes.NotFound:
            // 处理 404
        case codes.DeadlineExceeded:
            // 超时
        case codes.Unauthenticated:
            // 重新登录
        }
    }
}
```

**标准 gRPC 错误码**：
- OK / Canceled / Unknown / InvalidArgument / DeadlineExceeded
- NotFound / AlreadyExists / PermissionDenied / ResourceExhausted
- FailedPrecondition / Aborted / OutOfRange / Unimplemented
- Internal / Unavailable / DataLoss / Unauthenticated

## 九、grpc-gateway — RESTful 网关

**用 gRPC 同时支持 REST**：

```bash
protoc -I . --grpc-gateway_out . --grpc-gateway_opt paths=source_relative proto/user.proto
```

自动生成 REST 端点，转发到 gRPC。

## 十、gRPC 服务发现

```go
import "google.golang.org/grpc/resolver"

conn, _ := grpc.Dial("kubernetes:///myservice:50051",
    grpc.WithDefaultServiceConfig(`{"loadBalancingPolicy":"round_robin"}`))
```

支持：
- DNS：`consul:///service`
- k8s：`kubernetes:///service-name`
- 自定义 resolver

## 十一、性能优化

```go
// 1. 连接复用：多 goroutine 共享一个 *grpc.ClientConn
// 2. 流式代替频繁 unary
// 3. 启用压缩
s := grpc.NewServer(grpc.RPCCompressor(grpc.NewGZIPCompressor()))

// 4. 限制消息大小
s := grpc.NewServer(grpc.MaxRecvMsgSize(10 * 1024 * 1024))

// 5. keepalive
s := grpc.NewServer(grpc.KeepaliveParams(keepalive.ServerParameters{
    Time:    30 * time.Second,
    Timeout: 5 * time.Second,
}))
```

## 关联章节

- **05-microservices/gin-framework**：REST 替代
- **05-microservices/kratos**：微服务框架（用 gRPC）
- **05-microservices/case-study**：真实案例

## 一句话总结

> **gRPC = HTTP/2 + Protobuf + 流式 + 多语言**。**微服务内部通信首选**。
""")


add("05-microservices/kratos.md", r"""---
title: Kratos / go-zero / go-micro
---

# Go 微服务框架

**三个主流 Go 微服务框架对比**——Kratos、go-zero、go-micro。

## 一句话总结

> **Kratos（字节/B 站）= 完整套件；go-zero（好未来）= 工程化；go-micro = 早期标杆**。**国内推荐 Kratos 或 go-zero**。

---

## 一、为什么需要微服务框架

**Gin 写单体服务够用，但微服务需要**：
- 服务注册 / 发现
- 负载均衡
- 限流 / 熔断
- 链路追踪
- 配置中心
- 监控埋点
- 错误处理
- 重试 / 超时

**这些是 Go 微服务框架提供的**。

## 二、Kratos（推荐）

**Bilibili 开源**（2019，2020 字节收购后并入），定位"Go 微服务全栈框架"。

```bash
go install github.com/go-kratos/kratos/cmd/kratos/v2@latest
kratos new helloworld
cd helloworld
kratos run
```

**目录结构**：

```
helloworld/
├── api/                 # proto 定义
│   └── helloworld/v1/
├── cmd/                 # 入口
│   └── helloworld/
│       └── main.go
├── configs/             # 配置
├── internal/
│   ├── biz/             # 业务逻辑
│   ├── data/            # 数据访问
│   ├── service/         # service 层（proto 实现）
│   └── server/          # HTTP/gRPC server
└── third_party/         # proto 依赖
```

**核心组件**：

```go
// cmd/helloword/main.go
func main() {
    flag.Parse()
    logger := log.With(log.NewStdLogger(os.Stdout),
        "ts", log.DefaultTimestamp,
        "caller", log.DefaultCaller,
    )
    
    c := config.New(config.WithSource(file.NewSource(flagconf)))
    bc := newBootstrapConfig()
    if err := c.Load(); err != nil { panic(err) }
    
    app, cleanup, err := wireApp(bc.Server, bc.Data, logger)
    if err != nil { panic(err) }
    defer cleanup()
    
    if err := app.Run(); err != nil { panic(err) }
}
```

**Kratos 优点**：
- 完整套件：HTTP + gRPC + 服务发现 + 配置 + 限流
- Wire 依赖注入
- 中间件丰富（recovery / logging / tracing / ratelimit / circuit breaker）
- 与 K8s 集成好
- 字节 / B 站生产验证

**Kratos 缺点**：
- 学习曲线陡
- 文档偏少（相对 Java Spring Cloud）
- 较新，社区生态中等

## 三、go-zero

**好未来开源**（2020），定位"极简工程化"，中国 Go 微服务首选。

```bash
goctl api new greet
goctl rpc new greet
goctl docker -go greet.api
```

**API 定义（DSL）**：

```go
// greet.api
syntax = "v1"

type HelloReq {
    Name string `form:"name"`
}
type HelloResp {
    Msg  string `json:"msg"`
}

service greet-api {
    @handler GreetHandler
    get /greet/hello (HelloReq) returns (HelloResp)
}
```

**生成的代码**：

```go
// internal/handler/greethandler.go
func (h *GreetHandler) Greet(ctx *rest.Context) {
    var req types.HelloReq
    if err := ctx.Bind(&req); err != nil { /* ... */ }
    
    resp, err := h.svc.Greet(ctx, &req)
    if err != nil { /* ... */ }
    
    httpx.OkJson(ctx, resp)
}
```

**goctl 一键生成**：API + RPC + Model + DDL + K8s YAML + Dockerfile + Helm。

**go-zero 优点**：
- goctl 代码生成（DSL 驱动）
- 内置 ETCD / K8s 注册中心
- 内置 JWT 鉴权
- 内置限流熔断
- 中国社区最大
- 文档中文友好

**go-zero 缺点**：
- 高度依赖 goctl，黑盒生成
- 框架侵入性强
- 升级时偶有 breaking change

## 四、go-micro

**早期 Go 微服务标杆**（2015，社区驱动），但 2020 年后维护放缓。

```go
import "go-micro.dev/v4"

service := micro.NewService(
    micro.Name("greeter"),
    micro.Version("latest"),
)
service.Init()

proto.RegisterGreeterHandler(service.Server(), &Greeter{})

if err := service.Run(); err != nil { log.Fatal(err) }
```

**go-micro 优点**：
- 插件化设计（broker / registry / transport / selector）
- 多语言支持（Java / Python sidecar）

**go-micro 缺点**：
- v3/v4 转向商业化
- 社区分裂（microhq vs go-micro/v4）
- 中文文档少

## 五、对比表

| 维度 | Kratos | go-zero | go-micro |
|---|---|---|---|
| 厂商 | 字节 / B 站 | 好未来 | 个人 |
| Stars | 22k+ | 28k+ | 12k+ |
| 上手难度 | 中 | 中（goctl 驱动） | 中 |
| 代码生成 | protoc + wire | goctl | protoc |
| 依赖注入 | Wire | 手写 | 手写 |
| 注册中心 | consul/etcd/k8s/nacos | etcd/k8s | consul/etcd/k8s/mdns |
| 限流 | 内置 | 内置 | 插件 |
| 熔断 | 内置 | 内置 | 插件 |
| 链路追踪 | OpenTelemetry | 内置 | OpenTracing |
| 文档 | 中文好 | 中文好 | 英文 |
| 社区 | 中（活跃） | 大（活跃） | 小（不活跃） |
| 生产验证 | 字节 / B 站 / 哔哩哔哩 | 好未来 / 腾讯 | 较老项目 |

## 六、如何选型

**选 Kratos 如果**：
- 项目需要完整套件
- 已经在 K8s 环境
- 需要灵活的依赖注入
- 团队愿意学习

**选 go-zero 如果**：
- 想用 goctl 提高效率
- 团队是 Java 转 Go（DSL 风格类似 Spring）
- 需要中文文档
- 业务规模中等（10-100 个服务）

**选 go-micro 如果**：
- 维护老项目
- 需要多语言 sidecar

**不用框架如果**：
- 5 个服务以下
- 业务简单（CRUD）
- 想用 K8s Service 替代服务发现

## 七、自建微服务栈

**用 K8s 替代服务发现**：

```go
// 直接调 K8s Service
conn, _ := grpc.Dial("myservice.default.svc.cluster.local:50051", ...)

// K8s Service 自带负载均衡 + 服务发现
// 用 Istio 加限流 / 熔断 / 链路追踪
```

**优势**：
- 简单：Gin + gRPC + K8s 足够
- K8s 资源管控一体化
- 减少框架绑定

**适合**：10-30 个服务，K8s 原生团队。

## 八、实战：Kratos 完整示例

**1. proto**：

```protobuf
syntax = "proto3";
package user.v1;
option go_package = "github.com/myorg/myapp/api/user/v1;userv1";

service User {
    rpc CreateUser(CreateUserRequest) returns (CreateUserReply);
}

message CreateUserRequest {
    string name = 1;
    string email = 2;
}

message CreateUserReply {
    int64 id = 1;
}
```

**2. biz**（业务逻辑）：

```go
// internal/biz/user.go
type User struct {
    ID    int64
    Name  string
    Email string
}

type UserRepo interface {
    Save(ctx context.Context, u *User) (*User, error)
}

type UserUsecase struct {
    repo UserRepo
    log  *log.Helper
}

func NewUserUsecase(repo UserRepo, logger log.Logger) *UserUsecase {
    return &UserUsecase{repo: repo, log: log.NewHelper(logger)}
}

func (uc *UserUsecase) Create(ctx context.Context, name, email string) (*User, error) {
    if name == "" {
        return nil, errors.BadRequest("INVALID_NAME", "name cannot be empty")
    }
    return uc.repo.Save(ctx, &User{Name: name, Email: email})
}
```

**3. data**（数据访问）：

```go
// internal/data/user.go
type userRepo struct {
    data *Data
    log  *log.Helper
}

func NewUserRepo(data *Data, logger log.Logger) biz.UserRepo {
    return &userRepo{data: data, log: log.NewHelper(logger)}
}

func (r *userRepo) Save(ctx context.Context, u *biz.User) (*biz.User, error) {
    res, err := r.data.db.ExecContext(ctx, "INSERT INTO users (name, email) VALUES (?, ?)", u.Name, u.Email)
    if err != nil { return nil, err }
    id, _ := res.LastInsertId()
    return &biz.User{ID: id, Name: u.Name, Email: u.Email}, nil
}
```

**4. service**（proto 实现）：

```go
// internal/service/user.go
type UserService struct {
    usecase *biz.UserUsecase
}

func NewUserService(usecase *biz.UserUsecase) *UserService {
    return &UserService{usecase: usecase}
}

func (s *UserService) CreateUser(ctx context.Context, req *userv1.CreateUserRequest) (*userv1.CreateUserReply, error) {
    u, err := s.usecase.Create(ctx, req.Name, req.Email)
    if err != nil { return nil, err }
    return &userv1.CreateUserReply{Id: u.ID}, nil
}
```

**5. main**（wire 注入）：

```go
// cmd/user/main.go
func main() {
    // wire 生成的 main
    app, cleanup, err := wireApp(bc.Server, bc.Data, logger)
    defer cleanup()
    app.Run()
}
```

## 关联章节

- **05-microservices/grpc**：底层 RPC
- **05-microservices/gin-framework**：单体框架
- **05-microservices/service-governance**：服务治理
- **05-microservices/case-study**：真实案例

## 一句话总结

> **Kratos = 字节系，go-zero = 工程化，go-micro = 老牌**。**国内首选 Kratos 或 go-zero**。
""")


add("05-microservices/service-governance.md", r"""---
title: 服务治理
---

# 微服务治理

**服务治理 = 让多个服务稳定运行**：限流 / 熔断 / 降级 / 链路追踪 / 配置中心 / 服务发现。

## 一句话总结

> **服务治理 = 高可用 + 可观测 + 可配置 + 可扩展**。**核心：限流 + 熔断 + 链路追踪 + 配置中心**。

---

## 一、服务治理全景

```
┌─────────────────────────────────────────────┐
│ 服务治理                                       │
├──────────────┬──────────────┬────────────────┤
│  服务稳定性   │  可观测性     │  服务协作        │
│  限流        │  链路追踪     │  服务发现        │
│  熔断        │  日志        │  配置中心        │
│  降级        │  指标        │  消息队列        │
│  超时        │  健康检查     │  分布式锁        │
│  重试        │  告警        │  全链路灰度      │
└──────────────┴──────────────┴────────────────┘
```

## 二、限流

**目的**：防止流量过载，保护后端。

### 算法

| 算法 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| 固定窗口 | 1s 计数 | 简单 | 边界突刺 |
| 滑动窗口 | 多个窗口 | 平滑 | 内存大 |
| 漏桶 | 固定速率出水 | 恒定 | 突发浪费 |
| 令牌桶 | 攒令牌 | 允许突发 | 略复杂 |

### Go 实现

```go
import "golang.org/x/time/rate"

// 令牌桶：每秒 100 个，桶容量 200
limiter := rate.NewLimiter(rate.Limit(100), 200)

if !limiter.Allow() {
    http.Error(w, "Too Many Requests", 429)
    return
}
```

### 分布式限流

**Redis + Lua 原子计数**：

```lua
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local cur = redis.call("INCR", key)
if cur > limit then
    return 0
end
redis.call("EXPIRE", key, 1)
return 1
```

**Sentinel / Sentinel-Go**（阿里开源）：

```go
import "github.com/alibaba/sentinel-golang/core/flow"

flow.LoadRules([]*flow.Rule{
    {Resource: "order", TokenCalculateStrategy: flow.WarmUp, WarmUpColdFactor: 3, Threshold: 100},
})

entry, _ := flow.LoadGlobalTrace(context.Background(), "order")
if entry != nil { defer entry.Exit() }
```

## 三、熔断

**目的**：下游服务故障时快速失败，避免雪崩。

### 状态机

```
Closed ──故障率超阈值──> Open ──(sleep window)──> Half-Open
   ▲                                                  │
   └────────────────成功──────────────────────────────┘
                          └──失败──> Open
```

### Go 实现（gobreaker）

```go
import "github.com/sony/gobreaker"

cb := gobreaker.NewCircuitBreaker(gobreaker.Settings{
    Name:        "user-service",
    MaxRequests: 3,
    Interval:    1 * time.Minute,    // 统计周期
    Timeout:     30 * time.Second,   // Open 持续时间
    ReadyToTrip: func(counts gobreaker.Counts) bool {
        return counts.ConsecutiveFailures > 5
    },
})

result, err := cb.Execute(func() (interface{}, error) {
    return httpClient.Get("http://user-service/api/users")
})
```

**sentinel-golang**：

```go
import "github.com/alibaba/sentinel-golang/core/circuitbreaker"

circuitbreaker.LoadRules([]*circuitbreaker.Rule{
    {Resource: "user-service", Strategy: circuitbreaker.SlowRequestRatio,
        Threshold: 0.5, StatIntervalMs: 10000, MinRequestAmount: 10,
        SlowRatioThreshold: 0.6, MaxAllowedRtMs: 100},
})
```

## 四、超时与重试

```go
ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
defer cancel()

// 一层调用：3s 超时
resp, err := client.GetUser(ctx, req)

// 多层传递：每层 1s
ctx, cancel = context.WithTimeout(parentCtx, 1*time.Second)
```

**重试**：

```go
import "github.com/avast/retry-go"

err := retry.Do(
    func() error {
        return doRequest()
    },
    retry.Attempts(3),
    retry.Delay(100*time.Millisecond),
    retry.DelayType(retry.BackOffDelay),
    retry.MaxDelay(2*time.Second),
    retry.OnRetry(func(n uint, err error) {
        log.Printf("retry %d: %v", n, err)
    }),
)
```

**重试策略**：
- 指数退避：`100ms → 200ms → 400ms → ...`
- 抖动：避免雷鸣群
- 仅 idempotent 操作可重试

## 五、服务发现

**目标**：客户端无需硬编码服务地址。

### 模式

| 模式 | 特点 | 代表 |
|---|---|---|
| 客户端发现 | 客户端查注册中心 + LB | Eureka / Consul |
| 服务端发现 | LB 查询注册中心 | K8s Service / AWS ALB |

### Go 客户端发现

```go
import "github.com/hashicorp/consul/api"

client, _ := api.NewClient(api.DefaultConfig())
services, _, _ := client.Catalog().Service("user-service", "", nil)
for _, s := range services {
    fmt.Println(s.ServiceAddress, s.ServicePort)
}

// resolver 自动
conn, _ := grpc.Dial("consul:///user-service",
    grpc.WithDefaultServiceConfig(`{"loadBalancingPolicy":"round_robin"}`))
```

### K8s 模式（服务端发现）

```go
// K8s Service 自带负载均衡
conn, _ := grpc.Dial("user-service.default.svc.cluster.local:50051")
// K8s DNS + Service VIP → kube-proxy → pod
```

## 六、配置中心

**Apollo**（携程开源）：

```go
import "github.com/apolloconfig/agollo/v4"

client, _ := agollo.StartWithConfig(func() (*config.AppConfig, error) {
    return &config.AppConfig{
        AppID:          "myapp",
        Cluster:        "default",
        IP:             "http://apollo.config:8080",
        NamespaceName:  "application",
    }, nil
})

timeout := client.GetStringValue("request.timeout", "3s")
```

**Nacos**（阿里开源）：

```go
import "github.com/nacos-group/nacos-sdk-go/clients"

client, _ := clients.NewConfigClient(vo.NacosClientParam{
    ServerConfigs: []vo.ServerConfig{{IpAddr: "127.0.0.1", Port: 8848}},
})
dataId, _ := client.GetConfig(vo.ConfigParam{DataId: "user-service.yaml", Group: "DEFAULT_GROUP"})
```

**Viper + K8s ConfigMap**：

```go
viper.SetConfigFile("/etc/config/user-service.yaml")
viper.WatchConfig()
viper.OnConfigChange(func(e fsnotify.Event) {
    reloadConfig()
})
```

## 七、链路追踪

**OpenTelemetry（推荐）**：

```go
import "go.opentelemetry.io/otel"

func main() {
    tp := otelinit.NewTracerProvider()  // 初始化
    otel.SetTracerProvider(tp)
    
    r := gin.Default()
    r.Use(otelgin.Middleware("user-service"))
    
    r.GET("/users/:id", func(c *gin.Context) {
        ctx := c.Request.Context()
        tracer := otel.Tracer("user-service")
        ctx, span := tracer.Start(ctx, "GetUser")
        defer span.End()
        
        // 业务代码
        u, _ := userService.GetUser(ctx, c.Param("id"))
        c.JSON(200, u)
    })
}
```

**Jaeger / Tempo / Zipkin**：trace 后端。

## 八、健康检查

```go
import "github.com/heptiolabs/healthcheck"

health := healthcheck.NewHandler()
health.AddLivenessCheck("goroutine-threshold", healthcheck.GoroutineCountCheck(100))
health.AddReadinessCheck("mysql", healthcheck.DatabasePingCheck(db, 1*time.Second))
health.AddReadinessCheck("redis", healthcheck.RedisPingCheck(redisClient, "localhost:6379", 1*time.Second))

http.Handle("/live", health)
http.Handle("/ready", health)
```

**K8s 集成**：
- Liveness probe：`/live` 失败 → 重启 pod
- Readiness probe：`/ready` 失败 → 不接流量

## 九、降级

```go
// Hystrix 风格
type DegradeFunc func(ctx context.Context) (interface{}, error)

func WithFallback(primary, fallback func(ctx context.Context) (interface{}, error)) func(ctx context.Context) (interface{}, error) {
    return func(ctx context.Context) (interface{}, error) {
        result, err := primary(ctx)
        if err != nil {
            log.Printf("primary failed: %v, fallback", err)
            return fallback(ctx)
        }
        return result, nil
    }
}

// 用
getProduct := WithFallback(
    func(ctx context.Context) (interface{}, error) { return productService.Get(ctx, id) },
    func(ctx context.Context) (interface{}, error) { return defaultProduct, nil },  // 降级
)
```

## 十、灰度发布

**K8s + Istio**：

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: user-service
spec:
  http:
  - match:
    - headers:
        x-user-group:
          exact: beta
    route:
    - destination:
        host: user-service
        subset: v2
  - route:
    - destination:
        host: user-service
        subset: v1
```

**按比例**：

```yaml
spec:
  http:
  - route:
    - destination:
        host: user-service
        subset: v2
      weight: 10
    - destination:
        host: user-service
        subset: v1
      weight: 90
```

## 关联章节

- **05-microservices/grpc**：RPC
- **05-microservices/kratos**：框架
- **05-microservices/case-study**：真实案例
- **04-cloud-native/kubernetes-internals**：K8s

## 一句话总结

> **服务治理 = 限流 + 熔断 + 追踪 + 配置 + 发现**。**K8s 简化部分，框架简化全部**。
""")


# === 06-advanced ===

add("06-advanced/runtime.md", r"""---
title: runtime 调度器 GMP
---

# Go runtime 与 GMP 调度

**Go runtime = GMP 调度器 + GC + goroutine + channel**——理解它 = 写出高性能 Go。

## 一句话总结

> **GMP = G (goroutine) + M (machine/OS thread) + P (processor/逻辑 CPU)**。**work-stealing + hand-off 调度算法**。

---

## 一、GMP 模型

```
┌─────┐         ┌─────┐
│  M1 │ ── P1 ──┤ LRQ │ Local Run Queue (256 slots)
└─────┘    │    └─────┘
           │
           │    ┌────────────┐
           │    │   GRQ      │ Global Run Queue
           │    │ (unlimited)│
           │    └────────────┘
┌─────┐    │    ┌─────┐
│  M2 │ ── P2 ──┤ LRQ │
└─────┘         └─────┘
   ▲                ▲
   │                │
   └──syscall───────┘
```

- **G（Goroutine）**：用户态协程，初始栈 2KB
- **M（Machine）**：OS 线程，由 runtime 管理
- **P（Processor）**：逻辑 CPU，持有 LRQ；M 必须绑定 P 才能执行 G
- **LRQ**：每个 P 的本地队列，256 槽位
- **GRQ**：全局队列，无 M 偷取时新 G 放这里

## 二、调度算法

```go
// runtime/proc.go
func schedule() *g {
    top:
        gp, inheritTime, _ := runqget(_p_)  // 1. 优先从 LRQ 取
        if gp == nil {
            gp, inheritTime = globrunqget(_, _p_)  // 2. LRQ 空，从 GRQ 取
        }
        if gp == nil {
            gp, inheritTime = runqsteal(_p_, sched)  // 3. 偷其他 P 的一半 LRQ
        }
        if gp == nil {
            gp, _ = findrunnable()  // 4. 偷 + GC + polling
        }
        return gp
}
```

**调度时机**：
1. goroutine 阻塞（syscall / channel / IO）
2. goroutine 主动让出（runtime.Gosched()）
3. goroutine 运行时间过长（10ms 强制调度）
4. 启动新 goroutine

## 三、goroutine 创建

```go
go func() {  // go func
    // 1. newproc → g
    // 2. 优先放当前 P 的 LRQ
    // 3. LRQ 满（256）放 GRQ
}()

// runtime 内部
func newproc(siz int32, fn *funcval) {
    _p_ := getg().m.p.ptr()
    newg := gfget(_p_)  // 优先复用空闲 g
    if newg == nil {
        newg = malg(_StackMin)  // 分配新的 g
    }
    runqput(_p_, newg, true)  // 放 LRQ
}
```

## 四、M 数量控制

```go
// GOMAXPROCS = P 数量 = 可同时执行的 M 数量
// 默认 = CPU 核数
runtime.GOMAXPROCS(8)

// M 数量无上限（最大 10000）
// 但实际 M >> P 会导致线程切换开销
// M 阻塞在 syscall 时，P 会解绑给其他 M
```

**Syscall 处理**：
```
G 调 syscall → M 阻塞 → P 解绑 → GRQ 或其他 M 接管 → syscall 返回后 P 再绑定
```

**netpoller（Go 核心黑科技）**：
- Linux epoll / macOS kqueue
- goroutine 网络 IO 不阻塞 M
- epoll_wait 后唤醒 G

## 五、栈管理

```go
// goroutine 栈：动态伸缩
// 初始 2KB，最大 1GB（默认）
// 每次函数调用检查栈是否够
// 不够就 grow

// runtime/stack.go
func newstack() {
    // 分配 2 倍新栈
    // 拷贝旧栈内容
    // 调整指针
    // 用 copystack
}
```

**栈拷贝**：
- 1.x 之前是 split stack（hot split 性能问题）
- 1.x 之后是 contiguous stack（一次 grow，2x）

## 六、抢占式调度（Go 1.14+）

**问题**：goroutine 里死循环，runtime 没法调度其他 G。

**Go 1.14 引入基于信号的抢占**：
- sysmon 线程发送 SIGURG
- 目标 G 的 signal handler 检查是否需要让出
- 强制调度点

```go
// runtime/proc.go
func retake(now int64) uint32 {
    // 1. M 在 syscall 超 10ms：解绑 P
    // 2. G 运行超过 10ms：发 SIGURG 抢占
}
```

**Go 1.14 之前**：只能依靠函数调用作为调度点，纯 for 循环无法抢占。

## 七、调度可视化

**GODEBUG**：

```bash
GODEBUG=schedtrace=1000 ./myapp
# 输出每秒调度器状态：
# SCHED 0ms: gomaxprocs=8 idleprocs=8 threads=4 spinningthreads=0 idlethreads=2 runqueue=0 [0 0 0 0 0 0 0 0]

GODEBUG=scheddetail=1,schedtrace=1000 ./myapp
# 详细：每个 P 的状态
```

**trace**（更强大）：

```go
import "runtime/trace"
f, _ := os.Create("trace.out")
trace.Start(f)
defer trace.Stop()
```

```bash
go tool trace trace.out
# 浏览器看时序图
```

## 八、runtime 调优

```go
// 1. GOMAXPROCS
runtime.GOMAXPROCS(runtime.NumCPU())  // 容器环境按 CPU limit 设置

// 2. 调试
import _ "net/http/pprof"
go func() { http.ListenAndServe(":6060", nil) }()

// 3. 内存分配
debug.SetGCPercent(100)        // GC 触发比例
debug.SetMemoryLimit(8 << 30)  // 8GB 内存上限（Go 1.19+）
debug.SetMaxStack(1 << 20)     // 单 goroutine 栈最大

// 4. goroutine 数量
runtime.NumGoroutine()
```

## 九、runtime 关键函数

```go
// goroutine
runtime.Goexit()       // 退出当前 goroutine
runtime.Gosched()      // 让出 CPU
runtime.NumGoroutine() // goroutine 数量

// 内存
runtime.ReadMemStats(&m)
runtime.MemStats{Alloc, HeapAlloc, NumGC, PauseNs, ...}

// GC
runtime.GC()           // 强制 GC
debug.SetGCPercent(n)  // GC 触发比例
debug.FreeOSMemory()   // 强制返回 OS 内存

// 锁
runtime.LockOSThread() // 锁线程
runtime.UnlockOSThread()
```

## 十、真实问题排查

**问题 1：goroutine 泄漏**
```go
// ❌ 死循环
go func() {
    for {
        // 不退出
    }
}()

// ✅ context 退出
ctx, cancel := context.WithCancel(ctx)
go func() {
    for {
        select {
        case <-ctx.Done(): return
        default:
            // work
        }
    }
}()
```

**问题 2：调度延迟**
```bash
# 看 GODEBUG=schedtrace 中 stw（Stop The World）时间
SCHED 1000ms: ... stw=2.0ms
# stw > 10ms 需要调优
```

**问题 3：M 太多**
```go
// 看 runtime.Stack 是否有大量 M 在 syscall
buf := make([]byte, 1<<20)
runtime.Stack(buf, true)
fmt.Println(string(buf))
```

## 关联章节

- **02-concurrency/goroutine**：goroutine 基础
- **06-advanced/gc**：GC
- **06-advanced/pprof**：性能分析

## 一句话总结

> **GMP = G (goroutine) + M (machine) + P (processor) + work-stealing**。**Go 调度的灵魂**。
""")


add("06-advanced/gc.md", r"""---
title: GC 三色标记
---

# Go GC 三色标记

**Go GC = 并发三色标记 + 写屏障**——STW < 1ms（Go 1.8+），vs Java G1 几 ms 到几十 ms。

## 一句话总结

> **Go GC = Concurrent Tri-color Mark + Write Barrier + Pacemaker**。**STW 阶段仅 ms 级，业务无感知**。

---

## 一、Go GC 演进

| 版本 | 算法 | STW |
|---|---|---|
| Go 1.0 | STW 全暂停 | 几秒 |
| Go 1.3 | mark-sweep | 几百 ms |
| Go 1.5 | 三色标记 + 写屏障 | < 100ms |
| Go 1.8 | hybrid write barrier | < 1ms |
| Go 1.19 | memory limit | < 1ms |

## 二、三色标记原理

**三种颜色**：
- **White**：未访问（待回收）
- **Grey**：已发现，子节点未扫描
- **Black**：已扫描，子节点已处理

**流程**：
```
初始：所有对象 White
GC 根（栈/全局变量）置 Grey
循环：
  1. 从 Grey 集合取对象
  2. 标 Black
  3. 它引用的子对象标 Grey
直到 Grey 集合空
剩余 White = 垃圾
```

**问题**：用户程序（mutator）并发修改对象，可能导致：
- **漏标**：本应存活的对象被回收 → **严重错误**
- **多标**：本应回收的对象没回收 → **下次回收**

## 三、写屏障（Write Barrier）

**Go 1.8+ hybrid write barrier**：

```go
// 写屏障伪代码
func writePointer(slot, ptr) {
    shade(ptr)  // 将 ptr 染 Grey
    *slot = ptr
}
```

**作用**：mutator 修改引用时，确保被引用对象不漏标。

**两种屏障**：
- **Dijkstra 插入屏障**：写时标灰新引用
- **Yuasa 删除屏障**：写时标灰旧引用

**Go 1.8+ 混合**：
- 启动时 STW 打开插入屏障
- 关闭插入屏障 → 打开删除屏障
- 用 stack rescan 弥补
- 关闭删除屏障

## 四、GC 阶段

```
GC 周期：
  1. STW: GC start (几十微秒)
     - 开 hybrid write barrier
     - 扫描栈 → Grey
  2. Concurrent Mark (并发标记)
     - GC 协程后台跑
     - mutator 继续运行
  3. STW: Mark termination (几十微秒)
     - 关 write barrier
     - 处理剩余工作
  4. Concurrent Sweep (并发清扫)
     - 释放 White 对象
     - mutator 同时分配
```

**Pacemaker**：GC 触发比例（`GOGC=100`）控制 GC 频率。

## 五、GC 调优

```go
import "runtime/debug"

// 1. 调整 GC 触发比例
debug.SetGCPercent(200)  // heap 翻倍才 GC（吞吐优先）
debug.SetGCPercent(50)   // heap 50% 增长就 GC（延迟优先）

// 2. 内存上限（Go 1.19+）
debug.SetMemoryLimit(8 << 30)  // 8GB 硬上限

// 3. 强制 GC
runtime.GC()           // 立刻 GC（生产慎用）
debug.FreeOSMemory()   // GC + 把内存还给 OS

// 4. 监控
import _ "net/http/pprof"
http.ListenAndServe(":6060", nil)
// 访问 http://localhost:6060/debug/pprof/heap
```

## 六、pacer 调优

**Pacer = GC 节奏控制**：

```go
// 目标：堆增长 1 倍时启动下一次 GC
// 计算：trigger = live + live * GOGC / 100
// live = 上次 GC 后存活堆
// GOGC=100 → trigger = 2 * live

// 调整策略
// - 延迟敏感（Web 服务）：GOGC=50，减少 GC 间隔
// - 吞吐敏感（批处理）：GOGC=200，减少 GC 次数
```

**Go 1.19 memory limit**：
- 超过 limit → 强制 GC
- limit 0 = 关闭

## 七、内存分配

```go
// 1. 栈分配
//   - 编译器逃逸分析决定
//   - 不需要 GC
//   - 函数返回自动释放

// 2. 堆分配
//   - runtime.newobject
//   - mcache（线程本地）→ mcentral（全局）→ mheap（OS）
//   - 多种 size class

// 3. 分配优化
//   - 预分配 make([]T, 0, n)
//   - sync.Pool 复用
//   - 避免大对象（>32KB）
//   - 减少指针（减少 GC 扫描）
```

**Go 内存布局**：
```
┌─────────────┐
│   mcache    │  // 线程本地，size class
└─────┬───────┘
      │ 不足
┌─────▼───────┐
│  mcentral   │  // 全局，按 size class 分组
└─────┬───────┘
      │ 不足
┌─────▼───────┐
│   mheap     │  // 调 OS 申请
└─────┬───────┘
      │ 不足
      OS mmap
```

## 八、GC 监控指标

```go
var stats runtime.MemStats
runtime.ReadMemStats(&stats)

stats.Alloc        // 当前使用
stats.HeapAlloc    // 堆使用
stats.HeapObjects  // 对象数
stats.NumGC        // GC 次数
stats.PauseNs      // 最近 GC 暂停时间
stats.PauseTotalNs // 总 GC 暂停
stats.NextGC       // 下次 GC 触发阈值
```

**Prometheus 指标**：
```go
import "github.com/prometheus/client_golang/prometheus"

var goGcDuration = prometheus.NewHistogram(prometheus.HistogramOpts{
    Name:    "go_gc_duration_seconds",
    Help:    "A summary of the GC invocation durations.",
})

// 或者直接用 promhttp.DefaultCollect
http.Handle("/metrics", promhttp.Handler())
```

## 九、GC 触发时机

```go
// 1. 堆增长到 trigger
// 2. 距离上次 GC 超过 forcegcperiod（2 分钟）
// 3. runtime.GC() 强制
// 4. SetMemoryLimit 超限
// 5. 分配大对象（>32KB）绕过 size class
```

## 十、逃逸分析

**决定变量分配在栈还是堆**：

```bash
go build -gcflags='-m' main.go
# 输出
# ./main.go:5:2: moved to heap: x
```

**逃逸场景**：
- 返回局部变量指针
- 闭包引用
- 切片/map 大小未知
- interface{} 装箱
- 大对象（>64KB）

**避免逃逸**：
- 局部变量不取地址
- 用值类型而非指针（结构体小）
- 预分配 slice/map 容量

## 十一、Go GC vs JVM GC

| 维度 | Go GC | Java G1/ZGC |
|---|---|---|
| 算法 | 三色标记 + 写屏障 | 分代 + 并发标记 |
| STW | < 1ms | G1: 几十 ms, ZGC: < 1ms |
| 分代 | 无 | 有（年轻代/老年代） |
| 调优 | 简单 | 复杂（10+ 参数） |
| 分配 | 栈优先 | 堆优先 |
| 适合 | I/O bound / 微服务 | 计算密集 / 大堆 |

**Go GC 优势**：
- 简单：少参数（GOGC / memory limit）
- 延迟：< 1ms STW
- 协作：mutator 友好

**Go GC 劣势**：
- 无分代：长生命周期对象反复扫描
- 大堆效率低（建议 4GB 以下）

## 关联章节

- **06-advanced/runtime**：GMP 调度
- **06-advanced/pprof**：性能分析
- **03-ecosystem/benchmark**：pprof 用法

## 一句话总结

> **Go GC = Concurrent Tri-color + Write Barrier**。**STW < 1ms，延迟友好**。
""")


add("06-advanced/pprof.md", r"""---
title: pprof 与 trace
---

# Go pprof 与 trace

**pprof = Go 内置性能分析**——CPU / heap / goroutine / block / mutex / trace 全覆盖。

## 一句话总结

> **pprof = 5 种 profile（CPU/heap/goroutine/block/mutex）+ trace 时序图**。**生产 10 行接入，定位慢在哪儿**。

---

## 一、五大 profile 类型

| Profile | 抓什么 | 何时用 |
|---|---|---|
| **CPU** | 函数执行时间 | CPU 100% |
| **Heap** | 内存分配 / 堆对象 | 内存泄漏 / OOM |
| **Goroutine** | goroutine 栈 | goroutine 泄漏 |
| **Block** | 阻塞（channel / IO / syscall） | 卡顿 |
| **Mutex** | 锁竞争 | 锁争抢 |

## 二、HTTP 端点（推荐生产方式）

```go
import (
    "net/http"
    "net/http/pprof"
    "runtime"
)

func main() {
    runtime.SetMutexProfileFraction(5)  // 开启 mutex profile
    runtime.SetBlockProfileRate(1)       // 开启 block profile
    
    mux := http.NewServeMux()
    mux.HandleFunc("/debug/pprof/", pprof.Index)
    mux.HandleFunc("/debug/pprof/cmdline", pprof.Cmdline)
    mux.HandleFunc("/debug/pprof/profile", pprof.Profile)
    mux.HandleFunc("/debug/pprof/symbol", pprof.Symbol)
    mux.HandleFunc("/debug/pprof/trace", pprof.Trace)
    
    // 单独端点（auth）
    go func() {
        http.ListenAndServe("localhost:6060", mux)  // ⚠️ 加 auth
    }()
}
```

**访问**：
- `http://localhost:6060/debug/pprof/` — 索引
- `http://localhost:6060/debug/pprof/profile?seconds=30` — 30s CPU
- `http://localhost:6060/debug/pprof/heap` — heap
- `http://localhost:6060/debug/pprof/goroutine` — goroutine
- `http://localhost:6060/debug/pprof/trace?seconds=5` — trace

**生产**：
- 防火墙限制访问 IP
- 或加 basic auth
- 或走 sidecar

## 三、CPU profile

```bash
# 远程抓 30s CPU
curl http://localhost:6060/debug/pprof/profile?seconds=30 -o cpu.prof

# 交互分析
go tool pprof cpu.prof
(pprof) top 10
      flat  flat%   sum%        cum   cum%
         0     0%   50.0%     8.50s 50.0%  runtime.scanobject
     1.50s 8.33%  58.3%     3.00s 16.7%  compress/flate.(*compressor).deflate
# flat：函数本身耗时
# cum：函数 + 调用链总耗时

(pprof) list myFunction
# 看 myFunction 每行耗时

(pprof) web
# 生成 callgraph.svg，浏览器看调用图
```

**火焰图**：
```bash
# pprof 自带 -http
go tool pprof -http=:8080 cpu.prof
# 浏览器打开 http://localhost:8080 → View → Flame Graph
```

## 四、Heap profile

```bash
# 远程抓 heap
curl http://localhost:6060/debug/pprof/heap -o heap.prof

# 分析
go tool pprof heap.prof
(pprof) top 10 -cum
(pprof) list myAllocFunc
(pprof) alloc_space  # 按分配字节
(pprof) inuse_space  # 按当前使用字节
(pprof) alloc_objects
(pprof) inuse_objects
```

**关键指标**：
- **alloc_space**：从启动累计分配字节（含已 GC）
- **inuse_space**：当前使用字节
- **alloc_objects**：累计分配对象数
- **inuse_objects**：当前存活对象数

**代码中**：
```go
import "runtime/pprof"

pprof.Lookup("heap").WriteTo(f, 0)
```

## 五、Goroutine profile

```bash
# 抓当前所有 goroutine
curl http://localhost:6060/debug/pprof/goroutine?debug=2
# 详细文本输出

# profile 格式
curl http://localhost:6060/debug/pprof/goroutine -o goroutine.prof
go tool pprof goroutine.prof
(pprof) top
(pprof) trace  # 看调用链
```

**代码**：
```go
import "runtime/pprof"

pprof.Lookup("goroutine").WriteTo(f, 0)
```

**泄漏排查**：
```go
// 1. 启动时基线
buf1 := make([]byte, 1<<20)
runtime.Stack(buf1, true)
os.WriteFile("goroutines.before.txt", buf1, 0644)

// 2. 运行一段时间后再抓
buf2 := make([]byte, 1<<20)
runtime.Stack(buf2, true)
os.WriteFile("goroutines.after.txt", buf2, 0644)

// 3. diff 找新增的 goroutine
diff goroutines.before.txt goroutines.after.txt
```

## 六、Block profile（阻塞）

```go
// 必须先开
runtime.SetBlockProfileRate(1)  // 1ns 以上的阻塞都记录
```

```bash
curl http://localhost:6060/debug/pprof/block -o block.prof
go tool pprof block.prof
(pprof) top
# 看哪些函数阻塞最久（channel / mutex / select / IO）
```

## 七、Mutex profile（锁竞争）

```go
runtime.SetMutexProfileFraction(5)  // 5 次竞争采样 1 次
```

```bash
curl http://localhost:6060/debug/pprof/mutex -o mutex.prof
go tool pprof mutex.prof
```

**降低锁竞争**：
- 减小临界区
- sync.RWMutex 替代 Mutex
- 用 atomic 操作
- sharded map

## 八、Execution Trace

**最强大工具**，看 goroutine 调度、GC、syscall、阻塞全时序。

```go
import "runtime/trace"

f, _ := os.Create("trace.out")
trace.Start(f)
defer trace.Stop()
// 跑被测代码
```

```bash
go tool trace trace.out
# 浏览器打开，5 个 tab：
# 1. View trace：时序图（goroutine 状态、GC、syscall、运行、阻塞）
# 2. Goroutine analysis：按 goroutine 状态统计
# 3. Network blocking profile
# 4. Synchronization blocking profile
# 5. Syscall blocking profile
```

**生产**：远程抓
```bash
curl http://localhost:6060/debug/pprof/trace?seconds=5 -o trace.out
go tool trace trace.out
```

## 九、火焰图

**Uber go-torch**（已弃用，推荐 pprof 自带）：

```bash
go install github.com/uber/go-torch@latest
go-torch -seconds 30 http://localhost:6060/debug/pprof/profile
# 生成 flamegraph.svg
```

**pprof 自带**：
```bash
go tool pprof -http=:8080 cpu.prof
# 浏览器 http://localhost:8080
# 菜单 View → Flame Graph
```

## 十、连续 profile（持续监控）

**pyroscope**（推荐开源）：

```go
import "github.com/pyroscope-io/client/pyroscope"

pyroscope.Start(pyroscope.Config{
    ApplicationName: "myapp",
    ServerAddress:   "http://pyroscope:4040",
    Tags:            map[string]string{"env": "prod"},
})
```

**parca**（CNCF）：eBPF 抓取，无需代码侵入。

## 十一、Profile-guided Optimization (PGO)

**Go 1.20+ PGO**：

```bash
# 1. 抓 default profile
go test -bench=. -cpuprofile=default.pgo

# 2. 用 PGO 编译（自动检测 default.pgo）
go build -pgo=default.pgo -o myapp .

# 3. 性能提升 2-7%（来自标准库）
```

**生产建议**：
- 关键服务持续抓取 CPU profile
- 定期重新编译启用 PGO

## 十二、真实排查案例

**案例 1：CPU 100%**

```bash
# 1. 抓 CPU profile
curl http://localhost:6060/debug/pprof/profile?seconds=30 -o cpu.prof
# 2. 看 top
go tool pprof -top -cum cpu.prof
# 3. 找到热点函数，list 看具体行
go tool pprof -list hotFunc cpu.prof
```

**案例 2：内存增长**

```bash
# 1. 抓 heap
curl http://localhost:6060/debug/pprof/heap -o heap.prof
# 2. 看 alloc_space（累计分配）
go tool pprof -top -cum -sample_index=alloc_space heap.prof
# 3. 找到分配最多的函数
```

**案例 3：goroutine 泄漏**

```bash
# 1. 抓 goroutine
curl http://localhost:6060/debug/pprof/goroutine?debug=2 | head -100
# 2. 看哪些 goroutine 数量异常
curl http://localhost:6060/debug/pprof/goroutine?debug=2 | grep "^goroutine" | awk '{print $2}' | sort | uniq -c | sort -rn | head
```

**案例 4：调度延迟**

```bash
# 1. 抓 trace
curl http://localhost:6060/debug/pprof/trace?seconds=10 -o trace.out
# 2. 看 trace 里 GC、syscall、阻塞占比
go tool trace trace.out
```

## 关联章节

- **06-advanced/runtime**：GMP 调度
- **06-advanced/gc**：GC
- **03-ecosystem/benchmark**：benchmark

## 一句话总结

> **pprof + trace = Go 性能调优的瑞士军刀**。**10 行代码接入，无三方依赖**。
""")


add("06-advanced/cgo.md", r"""---
title: cgo 与 FFI
---

# cgo 与 FFI

**cgo = Go 调用 C 代码的桥**——双刃剑，能用但要谨慎。

## 一句话总结

> **cgo = C 库的 Go 绑定**。**性能收益大但破坏 Go 部署模型（必须 glibc / libxxx），能避免就避免**。

---

## 一、cgo 基础

```go
package main

/*
#include <stdio.h>
#include <stdlib.h>

void hello() {
    printf("Hello from C!\n");
}
*/
import "C"

func main() {
    C.hello()
}
```

**原理**：
- `import "C"` 启用 cgo
- 注释里写 C 代码
- 通过 `C.xxx` 调 C 函数
- Go 编译器调用 gcc/clang 编译 C 代码

## 二、调用 C 标准库

```go
package main

/*
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
*/
import "C"
import "unsafe"

func main() {
    // C 字符串
    cs := C.CString("Hello, C!")
    defer C.free(unsafe.Pointer(cs))  // 必须 free
    
    C.puts(cs)
    
    // C 内存
    buf := (*C.char)(C.malloc(1024))
    defer C.free(unsafe.Pointer(buf))
    C.memset(unsafe.Pointer(buf), 0, 1024)
    
    // C.strlen
    n := C.strlen(cs)
    println("len:", int(n))  // 9
}
```

## 三、调用 C 库

**libcurl 示例**：

```go
package main

/*
#cgo CFLAGS: -I/usr/include
#cgo LDFLAGS: -lcurl
#include <curl/curl.h>
#include <stdlib.h>

size_t WriteCallback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    char **response = (char**)userp;
    *response = realloc(*response, realsize + 1);
    memcpy(*response, contents, realsize);
    (*response)[realsize] = 0;
    return realsize;
}
*/
import "C"
import (
    "fmt"
    "unsafe"
)

func FetchURL(url string) (string, error) {
    curl := C.curl_easy_init()
    defer C.curl_easy_cleanup(curl)
    
    var response *C.char
    defer C.free(unsafe.Pointer(response))
    
    C.curl_easy_setopt(curl, C.CURLOPT_URL, C.CString(url))
    defer C.free(unsafe.Pointer(C.CString(url)))
    C.curl_easy_setopt(curl, C.CURLOPT_WRITEFUNCTION, C.WriteCallback)
    C.curl_easy_setopt(curl, C.CURLOPT_WRITEDATA, unsafe.Pointer(&response))
    
    res := C.curl_easy_perform(curl)
    if res != C.CURLE_OK {
        return "", fmt.Errorf("curl error: %d", int(res))
    }
    
    return C.GoString(response), nil
}
```

## 四、cgo 性能开销

```go
// ❌ 每次调用都有开销
for i := 0; i < 1e6; i++ {
    C.sqrt(C.double(i))  // 100ns/op（含 cgo bridge）
}

// ✅ 批量调用减少开销
data := make([]C.double, 1e6)
for i := range data {
    data[i] = C.double(i)
}
C.process_array(&data[0], C.int(len(data)))
// 一次 cgo 调 C 批量处理
```

**cgo 调用开销**：~100ns / 次（vs Go 函数 ~1ns）
- 参数/返回值跨语言转换
- goroutine 锁（M 不能同时跑多个 cgo）
- 调度开销

## 五、CGO_ENABLED 与静态链接

```bash
# 默认：CGO 启用，依赖 glibc
CGO_ENABLED=1 go build -o myapp .

# 静态二进制（无 glibc 依赖）
CGO_ENABLED=0 go build -o myapp .

# alpine 容器
FROM alpine:3.18
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/myapp /
CMD ["/myapp"]
# 镜像 ~15MB
```

**CGO 启用 = 必须 glibc**：
- 镜像变大（libc6-compat / glibc）
- 跨平台部署复杂
- K8s 多架构镜像麻烦

**建议**：
- 99% 场景用纯 Go
- 必须用 C 库时考虑纯 Go 替代

## 六、常见 C 库替代

| C 库 | 纯 Go 替代 |
|---|---|
| libcurl | net/http |
| sqlite3 | modernc.org/sqlite（纯 Go 移植） |
| libyaml | gopkg.in/yaml.v3 |
| OpenSSL | crypto/tls + crypto/...（部分） |
| libxml2 | encoding/xml + goquery |
| libpng | png（标准库） |
| zlib | compress/flate |

## 七、cgo 高级用法

### 回调（Go 函数给 C 调）

```go
package main

/*
#include <stdio.h>

typedef void (*callback_t)(int);

void register_callback(callback_t cb) {
    cb(42);
}
*/
import "C"
import "unsafe"

//export GoCallback
func GoCallback(x C.int) {
    println("Go got:", int(x))
}

func main() {
    cb := C.callback_t(C.GoCallback)  // Go 函数转 C 回调
    // ❌ 不能直接传 Go 函数指针给 C（go 1.21+ 用 //export）
    // 用 go-pointer 库
}
```

**Go 1.21+ 改进**：`//export GoCallback` 让 C 调用 Go 函数（实验）。

### C 调用 Go

```go
// cgo_callback.go
package main

//export GoAdd
func GoAdd(a, b C.int) C.int {
    return a + b
}
```

```bash
go build -buildmode=c-shared -o libmygo.so .
# 产动态库，C 程序 link
```

## 八、避免 cgo 的策略

1. **c-shared 模式**：用 Go 写 C 库（linkname / buildmode）
2. **gRPC wrapper**：Go 调 C，C 写服务
3. **WASM**：C 编译为 WASM，Go 调 WASM
4. **Sidecar**：C 程序独立部署，Go 调 HTTP

## 九、cgo 最佳实践

```go
// 1. 缓存 C 字符串（避免每次 C.CString）
var staticStr = C.CString("static")
defer C.free(unsafe.Pointer(staticStr))

// 2. 减少 cgo 调用次数
// 用 batch + 一次调用

// 3. 重要 cgo 函数独立包
// internal/clib/wrapper.go

// 4. 测试
//go:build cgo
// +build cgo

// 5. 错误处理
result, err := C.myfunc(...)
if err != nil { /* ... */ }
```

## 十、build tags 与 cgo

```go
//go:build linux && cgo
// +build linux cgo

package mypackage

// 只在 linux + cgo 启用时编译
```

**好处**：跨平台代码用纯 Go 替代，C 代码用 cgo 加速。

## 十一、真实案例

**场景 1**：图像处理用 C 库（libvips）

```go
// 性能 vs Go image
// libvips + cgo: 50ms
// pure Go imaging: 800ms (16x 慢)
```

**场景 2**：高性能密码学（BoringSSL）

```go
// CGO_ENABLED=1 go build -tags boringcrypto
// 用 BoringSSL 替代 Go crypto
// 性能 + 安全 + FIPS 兼容
```

**场景 3**：SQLite 内嵌（替代 CGO SQLite）

```go
import _ "modernc.org/sqlite"
// 纯 Go SQLite，无 CGO
// 比 mattn/go-sqlite3 慢 10%，但无需 CGO
```

## 十二、Go 1.21+ CGO 改进

- **`//export`** 实验性支持（Go 调 C 函数）
- **更好的编译器优化**（C 代码 LTO）
- **改进的 cgo 文档**

## 关联章节

- **06-advanced/runtime**：底层 runtime
- **06-advanced/gc**：GC 与 cgo
- **03-ecosystem/go-toolchain**：编译

## 一句话总结

> **cgo = C 库 Go 桥，性能高但破坏纯 Go 部署**。**优先找纯 Go 替代，必要时用 cgo**。
""")


add("06-advanced/reflection.md", r"""---
title: 反射 reflect
---

# Go 反射 reflect

**反射 = 运行时检查类型和值**——强大但慢，谨慎使用。

## 一句话总结

> **反射 = TypeOf + ValueOf + 动态调用**。**99% 场景不需要，仅 JSON / ORM / 配置 / DI 用**。

---

## 一、反射基础

```go
import "reflect"

type User struct {
    ID    int    `json:"id" validate:"required"`
    Name  string `json:"name" validate:"required,min=2"`
    Email string `json:"email,omitempty"`
}

func main() {
    u := User{ID: 1, Name: "Alice", Email: "alice@example.com"}
    
    // 1. TypeOf 拿类型
    t := reflect.TypeOf(u)
    fmt.Println(t.Name(), t.Kind())  // User struct
    
    // 2. ValueOf 拿值
    v := reflect.ValueOf(u)
    
    // 3. 字段数量
    for i := 0; i < t.NumField(); i++ {
        field := t.Field(i)
        value := v.Field(i)
        fmt.Printf("%s: %v = %v (tag: %s)\n",
            field.Name, field.Type, value, field.Tag.Get("json"))
    }
    
    // 4. 调用方法
    m := reflect.ValueOf(&u).MethodByName("Greet")
    if m.IsValid() {
        m.Call([]reflect.Value{reflect.ValueOf("Hello")})
    }
}
```

## 二、Type vs Value

```go
// TypeOf：类型元信息
t := reflect.TypeOf(u)
t.Name()          // "User"
t.Kind()          // reflect.Struct
t.NumField()      // 3
t.Field(0).Name   // "ID"
t.Field(0).Type   // int
t.Field(0).Tag    // StructTag
t.Implements(...) // 是否实现某接口
t.Method(0)       // 方法

// ValueOf：值
v := reflect.ValueOf(u)
v.Kind()          // reflect.Struct
v.NumField()      // 3
v.Field(0)        // 1（int 值）
v.Field(0).Int()  // 1
v.Field(1).String()  // "Alice"
v.Method(0).Call(...)  // 调方法
```

**Type 和 Value 互转**：
```go
v := reflect.ValueOf(u)
t := v.Type()
```

## 三、修改值

```go
u := User{ID: 1, Name: "Alice"}

// ❌ 错误：传值无法修改
v := reflect.ValueOf(u)
v.FieldByName("Name").SetString("Bob")  // panic

// ✅ 传指针
v := reflect.ValueOf(&u).Elem()  // Elem() 解引用
v.FieldByName("Name").SetString("Bob")
fmt.Println(u.Name)  // "Bob"

// CanSet 检查
if v.FieldByName("Name").CanSet() {
    v.FieldByName("Name").SetString("Bob")
}
```

**注意**：private 字段（首字母小写）不可 Set（CanSet() == false）。

## 四、动态创建

```go
// 动态创建 struct
t := reflect.StructOf([]reflect.StructField{
    {Name: "ID", Type: reflect.TypeOf(int(0)), Tag: `json:"id"`},
    {Name: "Name", Type: reflect.TypeOf("")},
})
v := reflect.New(t).Elem()
v.Field(0).SetInt(1)
v.Field(1).SetString("Alice")

// 动态创建 slice
sliceType := reflect.SliceOf(reflect.TypeOf(int(0)))
slice := reflect.MakeSlice(sliceType, 0, 10)
slice = reflect.Append(slice, reflect.ValueOf(42))
```

## 五、动态调用

```go
type User struct{}
func (u *User) Greet(name string) string { return "Hello, " + name }

u := &User{}
v := reflect.ValueOf(u)

// 调 Greet("Alice")
result := v.MethodByName("Greet").Call([]reflect.Value{
    reflect.ValueOf("Alice"),
})
fmt.Println(result[0].String())  // "Hello, Alice"
```

**无参数方法**：
```go
result := v.MethodByName("Init").Call(nil)
```

**构造并调用**：
```go
v := reflect.New(reflect.TypeOf(User{})).Elem()
// 设置字段
v.MethodByName("Greet").Call([]reflect.Value{reflect.ValueOf("Bob")})
```

## 六、接口与反射

```go
// 任意值 → interface{} → reflect.Value
var x interface{} = 42
v := reflect.ValueOf(x)

// interface{} 还原
y := v.Interface()
fmt.Println(y)

// 类型断言 vs 反射
if str, ok := x.(string); ok { /* 编译时类型安全 */ }
if v.Kind() == reflect.String { /* 运行时 */ }
```

**重要规则**：
- `reflect.TypeOf(nil)` 返回 nil（nil 没有类型）
- `reflect.ValueOf(nil)` 返回 zero Value
- 区分 nil interface{} 和 typed nil

## 七、StructTag

```go
type User struct {
    ID    int    `json:"id" db:"user_id" validate:"required"`
    Name  string `json:"name,omitempty" validate:"min=2,max=20"`
    Email string `json:"email" validate:"email"`
}

// 拿 tag
t := reflect.TypeOf(User{})
field, _ := t.FieldByName("ID")
jsonTag := field.Tag.Get("json")  // "id"
dbTag := field.Tag.Get("db")      // "user_id"
validateTag := field.Tag.Get("validate")  // "required"

// 解析 tag 字符串
tag := reflect.StructTag(`json:"name,omitempty" validate:"required"`)
opts := strings.Split(tag.Get("json"), ",")
// ["name", "omitempty"]
```

**自定义 tag 格式**：
```go
type Config struct {
    Host string `env:"HOST" default:"localhost" desc:"database host"`
}
```

## 八、反射性能

```go
// Benchmark:
BenchmarkNormalCall-8     1 ns/op
BenchmarkReflectCall-8    200 ns/op   // 200x 慢
```

**为什么慢**：
- 类型信息查询
- 内存拷贝
- 接口装箱
- 编译器无法内联

**优化**：
- 缓存 reflect.Type
- 缓存 reflect.Value
- 用 `go generate` 提前生成代码
- 减少反射层数

## 九、反射 vs 泛型（Go 1.18+）

```go
// 反射
func PrintSlice(s interface{}) {
    v := reflect.ValueOf(s)
    for i := 0; i < v.Len(); i++ {
        fmt.Println(v.Index(i))
    }
}

// 泛型
func PrintSlice[T any](s []T) {
    for _, v := range s {
        fmt.Println(v)
    }
}
```

**何时用哪个**：
| 场景 | 选 |
|---|---|
| 编译时类型确定 | 泛型 |
| 任意类型（JSON / map[any]） | 反射 |
| 高性能热路径 | 泛型 |
| 框架 / 库代码 | 反射 |
| 业务代码 | 泛型 |

**Go 1.18+ 泛型**：

```go
// Map 函数
func Map[T, U any](s []T, f func(T) U) []U {
    r := make([]U, len(s))
    for i, v := range s {
        r[i] = f(v)
    }
    return r
}

// Filter
func Filter[T any](s []T, pred func(T) bool) []T {
    r := make([]T, 0)
    for _, v := range s {
        if pred(v) {
            r = append(r, v)
        }
    }
    return r
}
```

## 十、真实场景

### 1. JSON 序列化（标准库内部用反射）

```go
import "encoding/json"

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
}

u := User{ID: 1, Name: "Alice"}
data, _ := json.Marshal(u)
// {"id":1,"name":"Alice"}
```

**替代**：jsoniter / easyjson（代码生成，比反射快 2-5 倍）。

### 2. ORM（GORM / ent）

```go
import "gorm.io/gorm"

type User struct {
    gorm.Model
    Name  string
    Email string `gorm:"uniqueIndex"`
}

db.AutoMigrate(&User{})
db.Create(&User{Name: "Alice"})

// GORM 内部用反射读 struct tag
```

### 3. 配置加载（viper）

```go
type Config struct {
    Server   ServerConfig   `mapstructure:"server"`
    Database DatabaseConfig `mapstructure:"database"`
}

viper.Unmarshal(&config)
// viper 反射读 tag
```

### 4. 依赖注入（wire）

```go
// wire_gen.go 是代码生成
// 但 dig / fx 用反射
container := dig.New()
container.Provide(NewUserService)
container.Invoke(func(s *UserService) { /* ... */ })
```

## 十一、unsafe — 反射的极端

```go
import "unsafe"

// 字符串 ↔ []byte 无拷贝
s := "hello"
b := unsafe.Slice(unsafe.StringData(s), len(s))
// b 是 []byte 视图（不分配）

// 任意指针
p := unsafe.Pointer(&u)
v := reflect.NewAt(t, p).Elem()
```

**unsafe 使用场景**：
- 性能极致优化（避免拷贝）
- 底层系统编程
- C 互操作

**不要用**：常规业务代码。

## 十二、最佳实践

1. **避免业务代码用反射**——用泛型
2. **缓存 reflect.Type / Value**
3. **用代码生成替代反射**（go generate）
4. **第三方库用反射**——自己不用
5. **测试反射代码**——`reflect.DeepEqual`
6. **性能敏感路径不用反射**

## 关联章节

- **06-advanced/runtime**：runtime 与反射
- **03-ecosystem/standard-library**：encoding/json
- **05-microservices/kratos**：wire 依赖注入

## 一句话总结

> **反射 = TypeOf + ValueOf + 动态调用**。**框架用，业务用泛型**。
""")
