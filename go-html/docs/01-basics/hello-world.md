---
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
