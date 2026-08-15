---
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
