---
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


<!-- auto-enrich:do-not-edit -->

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [rust](https://java-px.bot.cd/rust/):Rust 对比
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s / Docker
- [devops](https://java-px.bot.cd/devops/):DevOps 工具
