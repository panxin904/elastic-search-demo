---
title: Go 工具链
date: 2026-08-15  # date-auto-injected
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
