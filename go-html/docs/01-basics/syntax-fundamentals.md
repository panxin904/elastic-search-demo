---
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
