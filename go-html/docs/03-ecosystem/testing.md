---
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
