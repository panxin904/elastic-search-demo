---
title: 类型与函数
date: 2026-08-15  # date-auto-injected
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


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [rust](https://java-px.bot.cd/rust/):Rust 对比
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s / Docker
- [devops](https://java-px.bot.cd/devops/):DevOps 工具
