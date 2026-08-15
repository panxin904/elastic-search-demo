---
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
