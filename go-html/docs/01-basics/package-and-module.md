---
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
